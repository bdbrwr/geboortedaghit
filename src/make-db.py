import sqlite3

con = sqlite3.connect("geboortedaghit.db")
cur = con.cursor()

#create Charts table
cur.execute("CREATE TABLE charts(id INTEGER PRIMARY KEY, year INTEGER NOT NULL, week INTEGER NOT NULL, from_date DATE NOT NULL, to_date DATE NOT NULL, source TEXT NOT NULL)")

#create Charts songs table
cur.execute("CREATE TABLE chart_songs(id INTEGER PRIMARY KEY, position INTEGER NOT NULL, artist TEXT NOT NULL, title TEXT NOT NULL, chart INTEGER, spotify_link TEXT, youtube_link TEXT, FOREIGN KEY(chart) REFERENCES charts(id))")

con.close()