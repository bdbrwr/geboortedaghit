import sqlite3
import difflib
import time
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE = os.getenv("DATABASE")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Connect to the database
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Fetch songs without a YouTube link, prioritize #1 hits
cur.execute("""
    SELECT DISTINCT s.id, s.artist, s.title
    FROM songs s
    LEFT JOIN chart_songs cs ON s.id = cs.song_id
    WHERE s.youtube_link IS NULL
    ORDER BY CASE WHEN cs.position = 1 THEN 0 ELSE 1 END, s.id
""")
songs = cur.fetchall()

def is_match(query, result, threshold=0.6):
    return difflib.SequenceMatcher(None, query.lower(), result.lower()).ratio() >= threshold

def get_youtube_link(artist, title):
    query = f"{artist} {title}"
    try:
        response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=1,
            type='video'
        ).execute()
    except Exception as e:
        print(f"[Error] YouTube API error: {e}")
        return None

    items = response.get('items', [])
    if items:
        item = items[0]
        result_title = item['snippet']['title']
        if is_match(query, result_title):
            return f"https://www.youtube.com/watch?v={item['id']['videoId']}"
    return None

# Process and update each song with throttling
for song_id, artist, title in songs:
    print(f"[YouTube] Processing: {artist} - {title}")
    youtube_link = get_youtube_link(artist, title)

    if youtube_link:
        cur.execute("UPDATE songs SET youtube_link = ? WHERE id = ?", (youtube_link, song_id))
        conn.commit()
        print(f"Added link: {youtube_link}")
    else:
        print("No match found")

    time.sleep(0.5)  # Throttle: wait 0.5s between requests

print("YouTube links updated.")
conn.close()
