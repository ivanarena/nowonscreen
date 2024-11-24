import sqlite3


def setup_database():
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
            screening_date TEXT NOT NULL,
            screening_time TEXT NOT NULL,
            language TEXT,
            price TEXT,
            cast TEXT,
            UNIQUE(cinema, title, screening_date, screening_time)
        )
        """
    )

    connection.commit()
    connection.close()


def save_screenings_to_db(screenings):
    """
    Save a list of screenings to the database.

    Parameters:
        screenings (list): A list of dictionaries where each dictionary contains screening details.
    """
    connection = sqlite3.connect("screenings.db")
    cursor = connection.cursor()

    # Insert screenings into the database
    for screening in screenings:
        cursor.execute(
            """
            INSERT INTO screenings (
                cinema, title, original_title, director, year_of_release, screening_date, 
                screening_time, language, price, cast
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                screening["cinema"],
                screening["title"],
                screening.get("original_title"),
                screening.get("director"),
                screening.get("year_of_release"),
                screening["screening_date"],
                screening["screening_time"],
                screening.get("language"),
                screening.get("price"),
                ", ".join(
                    screening.get("cast", [])
                    if isinstance(screening.get("cast"), list)
                    else []
                ),
            ),
        )
    connection.commit()
    connection.close()


def query_screenings(target_date):
    """
    Query screenings for a specific date.

    Parameters:
        target_date (str): The target date in the format "DD Month YYYY" (e.g., "22 November 2024").

    Returns:
        list: A list of tuples where each tuple represents a screening.
    """
    connection = sqlite3.connect("screenings.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT screening_date, screening_time, title, cinema
        FROM screenings
        WHERE screening_date = ?
        ORDER BY screening_date, screening_time
        """,
        (target_date,),
    )

    results = cursor.fetchall()
    connection.close()

    return results
