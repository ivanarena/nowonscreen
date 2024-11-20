import sqlite3
from datetime import datetime, timedelta

DB_PATH = "cinema_screenings.db"

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cinema TEXT NOT NULL,
        title TEXT NOT NULL,
        screening_date TEXT NOT NULL,
        screening_time TEXT NOT NULL,
        original_title TEXT,
        director TEXT,
        year_of_release INTEGER,
        language TEXT,
        price TEXT,
        cast TEXT,
        UNIQUE(cinema, title, screening_date, screening_time)
    );
    """)
    conn.commit()
    conn.close()


def save_screenings_to_db(screenings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for screening in screenings:
        cursor.execute("""
        INSERT INTO screenings (
            cinema, title, screening_date, screening_time, original_title,
            director, year_of_release, language, price, cast
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cinema, title, screening_date, screening_time) DO UPDATE SET
            original_title=excluded.original_title,
            director=excluded.director,
            year_of_release=excluded.year_of_release,
            language=excluded.language,
            price=excluded.price,
            cast=excluded.cast;
        """, (
            screening["cinema"],
            screening["title"],
            screening["screening_date"],
            screening["screening_time"],
            screening.get("original_title"),
            screening.get("director"),
            screening.get("year_of_release"),
            screening.get("language"),
            screening.get("price"),
            ", ".join(screening.get("cast", []) if isinstance(screening.get("cast"), list) else [])
        ))
        print(f"Saved screening: {screening}")


def query_screenings(target_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT cinema, title, screening_date, screening_time
    FROM screenings
    WHERE screening_date = ?;
    """, (target_date,))
    results = cursor.fetchall()
    conn.close()
    return results
