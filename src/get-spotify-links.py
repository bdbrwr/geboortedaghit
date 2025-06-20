import sqlite3
import difflib
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE = os.getenv("DATABASE")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Initialize Spotify API client
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Connect to the database
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Prioritize songs that hit #1 first, then others
cur.execute("""
    SELECT DISTINCT s.id, s.artist, s.title
    FROM songs s
    LEFT JOIN chart_songs cs ON s.id = cs.song_id
    WHERE s.spotify_link IS NULL
    ORDER BY CASE WHEN cs.position = 1 THEN 0 ELSE 1 END, s.id
""")
songs = cur.fetchall()

def is_match(query, result, threshold=0.6):
    return difflib.SequenceMatcher(None, query.lower(), result.lower()).ratio() >= threshold

def get_spotify_link(artist, title):
    query = f"{artist} {title}"
    try:
        results = spotify.search(q=query, limit=1, type='track')
    except Exception as e:
        print(f"[Error] Spotify API error: {e}")
        return None

    items = results['tracks']['items']
    if items:
        track = items[0]
        result_name = f"{track['artists'][0]['name']} {track['name']}"
        if is_match(query, result_name):
            return track['external_urls']['spotify']
    return None

# Process and update each song with throttling
for song_id, artist, title in songs:
    print(f"[Spotify] Processing: {artist} - {title}")
    spotify_link = get_spotify_link(artist, title)

    if spotify_link:
        cur.execute("UPDATE songs SET spotify_link = ? WHERE id = ?", (spotify_link, song_id))
        conn.commit()
        print(f"Added link: {spotify_link}")
    else:
        print("No match found")

    time.sleep(0.5)  # Throttle: wait 0.5s between requests

print("Spotify links updated.")
conn.close()
