import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE = os.getenv("DATABASE")

def migrate_to_normalized_schema():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # 1. Create the new songs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            spotify_link TEXT,
            youtube_link TEXT,
            UNIQUE(title, artist)
        )
    """)

    conn.commit()

    # 2. Insert unique songs into songs table
    cur.execute("""
        SELECT DISTINCT title, artist FROM chart_songs
    """)
    unique_songs = cur.fetchall()

    for title, artist in unique_songs:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO songs (title, artist) VALUES (?, ?)
            """, (title, artist))
        except Exception as e:
            print(f"Error inserting song: {title} - {artist}: {e}")

    conn.commit()

    # 3. Add song_id column to chart_songs
    cur.execute("ALTER TABLE chart_songs ADD COLUMN song_id INTEGER")

    # 4. Populate song_id by joining on title+artist
    cur.execute("""
        SELECT id, title, artist FROM chart_songs
    """)
    chart_songs = cur.fetchall()

    for row_id, title, artist in chart_songs:
        cur.execute("""
            SELECT id FROM songs WHERE title = ? AND artist = ?
        """, (title, artist))
        song_row = cur.fetchone()

        if song_row:
            song_id = song_row[0]
            cur.execute("""
                UPDATE chart_songs SET song_id = ? WHERE id = ?
            """, (song_id, row_id))

    conn.commit()

    # 5. Clean up chart_songs: remove artist/title, add FK
    cur.execute("PRAGMA foreign_keys=off")  # Needed for SQLite table redefinition

    # Rename old table
    cur.execute("ALTER TABLE chart_songs RENAME TO old_chart_songs")

    # Recreate chart_songs without artist/title, and with FK
    cur.execute("""
        CREATE TABLE chart_songs (
            id INTEGER PRIMARY KEY,
            position INTEGER NOT NULL,
            chart INTEGER,
            song_id INTEGER,
            FOREIGN KEY(chart) REFERENCES charts(id),
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    """)

    # Copy data over
    cur.execute("""
        INSERT INTO chart_songs (id, position, chart, song_id)
        SELECT id, position, chart, song_id FROM old_chart_songs
    """)

    # Drop old table
    cur.execute("DROP TABLE old_chart_songs")
    cur.execute("PRAGMA foreign_keys=on")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_to_normalized_schema()
