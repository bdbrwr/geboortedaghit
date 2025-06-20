import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE = os.getenv("DATABASE")

con = sqlite3.connect(DATABASE)
cur = con.cursor()

# Create charts table
cur.execute("""
CREATE TABLE charts (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    week INTEGER NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    source TEXT NOT NULL
)
""")

# Create songs table
cur.execute("""
CREATE TABLE songs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    spotify_link TEXT,
    youtube_link TEXT,
    spotify_checked BOOLEAN DEFAULT 0,
    youtube_checked BOOLEAN DEFAULT 0,
    UNIQUE(title, artist)
)
""")

# Create chart_songs table
cur.execute("""
CREATE TABLE chart_songs (
    id INTEGER PRIMARY KEY,
    position INTEGER NOT NULL,
    chart INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    FOREIGN KEY(chart) REFERENCES charts(id),
    FOREIGN KEY(song_id) REFERENCES songs(id)
)
""")

con.commit()
con.close()
