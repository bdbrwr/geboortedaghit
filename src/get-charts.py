import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE = os.getenv("DATABASE")
BASE_URL = "https://www.top40.nl/top40/{year}/week-{week}"

def main():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    latest_date = get_latest_chart_date(cursor)
    today = datetime.today().date()

    if latest_date and today <= latest_date:
        print("No new charts to process.")
        return

    start_year, start_week = get_next_chart(cursor, latest_date)

    while True:
        chart_friday = get_friday_date(start_year, start_week)
        if chart_friday >= today:
            print(f"Reached future chart: week {start_week} of {start_year} (Friday = {chart_friday}). Stopping.")
            break

        url = BASE_URL.format(year=start_year, week=start_week)
        print(f"Processing {url}")

        try:
            soup = get_data(url)

            week_info_text = soup.select_one(".list__nav-bar--week-info").text.strip()
            week_number, to_date = parse_week_info(week_info_text)
            from_date = to_date - timedelta(days=6)

            songs_raw = soup.select("div.top40-list__item")
            songs = [parse_song_info(s) for s in songs_raw if parse_song_info(s) is not None]

            if not songs:
                print(f"No songs found for week {start_week} of {start_year}. Skipping.")
                start_year, start_week = increment_week(start_year, start_week)
                continue

            cursor.execute("""
                INSERT INTO charts (year, week, from_date, to_date, source)
                VALUES (?, ?, ?, ?, ?)
            """, (start_year, start_week, from_date, to_date, url))
            chart_id = cursor.lastrowid

            for song_info in songs:
                # Insert or ignore song into songs table
                cursor.execute("""
                    INSERT OR IGNORE INTO songs (title, artist) VALUES (?, ?)
                """, (song_info['title'], song_info['artist']))

                # Retrieve the song_id
                cursor.execute("""
                    SELECT id FROM songs WHERE title = ? AND artist = ?
                """, (song_info['title'], song_info['artist']))
                song_row = cursor.fetchone()
                if not song_row:
                    print(f"Failed to retrieve song ID for: {song_info['artist']} - {song_info['title']}")
                    continue

                song_id = song_row[0]

                # Insert into chart_songs
                cursor.execute("""
                    INSERT INTO chart_songs (position, chart, song_id)
                    VALUES (?, ?, ?)
                """, (
                    song_info['position'],
                    chart_id,
                    song_id
                ))

            conn.commit()
            print(f"Inserted chart for week {start_week} of {start_year} with {len(songs)} songs.")

            start_year, start_week = increment_week(start_year, start_week)

        except Exception as e:
            print(f"Error processing week {start_week} of {start_year}: {e}")
            start_year, start_week = increment_week(start_year, start_week)

    conn.close()


def get_latest_chart_date(cursor):
    cursor.execute("SELECT MAX(to_date) FROM charts")
    row = cursor.fetchone()
    return datetime.strptime(row[0], "%Y-%m-%d").date() if row and row[0] else None


def get_next_chart(cursor, latest_date):
    if not latest_date:
        return 1965, 1

    cursor.execute("""
        SELECT year, week FROM charts 
        WHERE to_date = (SELECT MAX(to_date) FROM charts)
    """)
    row = cursor.fetchone()

    if not row:
        return 1965, 1

    year, week = row
    return increment_week(year, week)


def increment_week(year, week):
    return (year, week + 1) if week < 53 else (year + 1, 1)


def get_data(url):
    page = requests.get(url)
    if not page.ok:
        raise ValueError(f"Could not fetch page: {url}")
    soup = BeautifulSoup(page.text, "html.parser")
    return soup


def parse_week_info(text):
    dutch_months = {
        'januari': 1, 'februari': 2, 'maart': 3, 'april': 4,
        'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'december': 12
    }

    match = re.search(r"week\s+(\d+)\s+\((\d+)\s+(\w+)\s+(\d{4})\)", text, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid week info format")

    week_number = int(match.group(1))
    day = int(match.group(2))
    month_str = match.group(3).lower()
    year = int(match.group(4))

    month = dutch_months.get(month_str)
    if not month:
        raise ValueError(f"Unknown Dutch month: {month_str}")

    date_obj = datetime(year, month, day)
    return week_number, date_obj.date()


def parse_song_info(soup):
    position_tag = soup.select_one("div.top40-list__item__info__position")
    if not position_tag:
        return None

    position_text = position_tag.text.strip()
    if position_text == "-" or not position_text.isdigit():
        return None

    try:
        position = int(position_text)
        title = soup.select_one("div.top40-list__item__info a.h3 h2.h3").text.strip()
        artist = soup.select_one("a.p.lead.lowercase h3.p.lead.lowercase").text.strip()
        weeks = int(soup.select_one("div.top40-list__item__controls--weeks span.h5").text.strip())
    except Exception:
        return None

    return {
        "position": position,
        "title": title,
        "artist": artist,
        "weeks": weeks
    }


def get_friday_date(year, week_number):
    count = 0
    day = datetime(year, 1, 1)
    while count < week_number:
        if day.weekday() == 4:
            count += 1
        day += timedelta(days=1)
    return (day - timedelta(days=1)).date()


if __name__ == "__main__":
    main()
