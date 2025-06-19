import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

url = "https://www.top40.nl/top40/1965/week-1"
url = "https://www.top40.nl/top40/2023/week-19"

def main():
    full_page = get_data(url)

    week_date = full_page.select_one(".list__nav-bar--week-info").text.strip()
    print(parse_week_info(week_date))

    songs = full_page.select("div.top40-list__item")
    for song in songs:
        song_info = parse_song_info(song)
        if song_info:
            print(
                f"position={song_info['position']}\n"
                f"artist={song_info['artist']}\n"
                f"title={song_info['title']}\n"
                f"weeks={song_info['weeks']}\n"
                )

def get_data(url):
    page = requests.get(url)
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
        raise ValueError("Invalid format")

    week_number = int(match.group(1))
    day = int(match.group(2))
    month_str = match.group(3).lower()
    year = int(match.group(4))

    month = dutch_months.get(month_str)
    if not month:
        raise ValueError(f"Unknown month: {month_str}")

    date_obj = datetime(year, month, day)
    return (week_number, date_obj)

def parse_song_info(soup):
    position_tag = soup.select_one("div.top40-list__item__info__position")
    if not position_tag:
        return None 

    position_text = position_tag.text.strip()
    if position_text == "-":
        return None 

    try:
        position = int(position_text)
    except ValueError:
        return

    song_info = {
        "position": position,
        "title": soup.select_one("div.top40-list__item__info a.h3 h2.h3").text.strip(),
        "artist": soup.select_one("a.p.lead.lowercase h3.p.lead.lowercase").text.strip(),
        "weeks": int(soup.select_one("div.top40-list__item__controls--weeks span.h5").text.strip())
    }

    return song_info


if __name__ == "__main__":
    main()