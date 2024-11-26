import argparse
from datetime import datetime
import db
import llm
from config import CINEMAS
from scraper import scrape


def get_screenings(date=None, cinema=None):
    if date is None:
        date = "week"
    title = "This week" if date == "week" else date.capitalize()
    title += "'s screenings at "
    title += "all cinemas" if cinema is None else cinema.title()
    title += ".\n"
    results = db.query(date, cinema)
    print(title)
    for row in results:
        date_str = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y")
        print(f"{date_str:<15}, {row[1]:<10} {row[2]:<60} at {row[3]:<20}")
    

def main():
    parser = argparse.ArgumentParser(description="NowOnScreen")
    parser.add_argument("-d", "--date", type=str, nargs="?", choices=["today", "tomorrow"], help="Target date (today, tomorrow)")
    parser.add_argument("-c", "--cinema", type=str, nargs="?", choices=CINEMAS, help="Cinema name")

    args = parser.parse_args()
    date = args.date if "date" in args else None
    cinema = args.cinema if "cinema" in args else None
    get_screenings(date, cinema)


if __name__ == "__main__":
    db.create()
    scrape()
    screenings = llm.ner()
    db.insert(screenings)
    main()
