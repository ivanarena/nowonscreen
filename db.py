import sqlite3
from datetime import datetime, timedelta


def create():
    """
    Initialize the database and create the necessary table for storing film screenings.
    """
    connection = sqlite3.connect("screenings.db")
    cursor = connection.cursor()

    # Create table for screenings
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cinema TEXT NOT NULL,
            title TEXT NOT NULL,
            original_title TEXT,
            director TEXT,
            year_of_release INTEGER,
            screening_date DATE NOT NULL,
            screening_time TIME NOT NULL,
            language TEXT,
            price REAL,
            cast TEXT,
            UNIQUE(cinema, title, screening_date, screening_time)
        )
        """
    )

    connection.commit()
    connection.close()


def insert(screenings):
    """
    Save a list of screenings to the database.

    Parameters:
        screenings (list): A list of dictionaries where each dictionary contains screening details.
    """
    connection = sqlite3.connect("screenings.db")
    cursor = connection.cursor()

    for screening in screenings:
        try:
            cursor.execute(
                """
                INSERT INTO screenings (
                    cinema, title, original_title, director, year_of_release, screening_date, 
                    screening_time, language, price, cast
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    screening["cinema"].title() if screening["cinema"] else None,
                    screening["title"].title() if screening["title"] else None,
                    screening.get("original_title").title() if screening.get("original_title") else None,
                    screening.get("director").title() if screening.get("director") else None,
                    screening.get("year_of_release"),
                    datetime.strptime(screening["screening_date"], "%Y-%m-%d"),
                    screening["screening_time"].replace("h", ""), # sometimes the LLM would output "HH:MMh" instead of "HH:MM"
                    screening.get("language"),
                    f"€{screening.get('price').replace('€', '')}" if screening.get("price") else None,
                    ", ".join(
                        screening.get("cast", [])
                        if isinstance(screening.get("cast"), list)
                        else []
                    ),
                ),
            )
        except sqlite3.IntegrityError:
            print(f'''
                Screening {screening["title"]} at {screening["cinema"]} at
                {screening["screening_time"]}on {screening["screening_date"]} already present.
            ''')
            continue
    connection.commit()
    connection.close()


def query(date=None, cinema=None, full=False):
    """
    Query screenings for a specific date.

    Parameters:
        target_date (str): The target date in the format "DD Month YYYY" (e.g., "22 November 2024").

    Returns:
        list: A list of tuples where each tuple represents a screening.
    """
    connection = sqlite3.connect("screenings.db")
    cursor = connection.cursor()
    
    params = []
    conditions = []
    today = datetime.now()
    if date == "today":
        conditions.append("strftime('%Y-%m-%d', screening_date) = ?")
        params.append(today.strftime("%Y-%m-%d"))
    elif date == "tomorrow":
        conditions.append("strftime('%Y-%m-%d', screening_date) = ?")
        params.append((today + timedelta(days=1)).strftime("%Y-%m-%d"))
    elif date == "week":
        sunday = today + timedelta(days=(6 - today.weekday()))
        conditions.append("screening_date BETWEEN ? AND ?")
        params.append(today.strftime("%Y-%m-%d"))
        params.append((sunday + timedelta(days=1)).strftime("%Y-%m-%d"))
    if cinema:
        conditions.append("cinema = ?")
        params.append(cinema.title())

    sql = """
        SELECT screening_date, screening_time, title, cinema
        FROM screenings
    """
    if full:
        sql = """
            SELECT *
            FROM screenings
        """
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY screening_date, screening_time"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    connection.close()

    return results