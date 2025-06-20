from flask import Blueprint, render_template, request
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

main = Blueprint('main', __name__)
DB_PATH = os.getenv('DATABASE', 'fallback.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_date_dutch(date_obj):
    months = [
        "januari", "februari", "maart", "april", "mei", "juni",
        "juli", "augustus", "september", "oktober", "november", "december"
    ]
    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    return f"{day} {month} {year}"

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date_str = request.form['birthdate']
        try:
            birthdate = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return render_template('index.html', error="Ongeldige datum, probeer opnieuw.")

        conn = get_db_connection()
        chart = conn.execute("""
            SELECT * FROM charts
            WHERE from_date <= ? AND to_date >= ?
            LIMIT 1
        """, (birthdate, birthdate)).fetchone()

        if chart is None:
            conn.close()
            return render_template('index.html', error="Geen hitlijst gevonden voor deze datum.")

        top_song_row = conn.execute("""
            SELECT s.title, s.artist FROM chart_songs cs
            JOIN songs s ON s.id = cs.song_id
            WHERE cs.chart = ? AND cs.position = 1
            LIMIT 1
        """, (chart['id'],)).fetchone()
        conn.close()

        if top_song_row is None:
            return render_template('index.html', error="Geen nummer 1 gevonden voor deze datum.")

        formatted_date = format_date_dutch(birthdate)
        return render_template('result.html', song=top_song_row, birthdate=formatted_date)

    return render_template('index.html')
