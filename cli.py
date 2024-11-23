import argparse
from datetime import datetime, timedelta

from db_utils import query_screenings, save_screenings_to_db, setup_database
from ner_processor import process_scraped_data
from scraper import CINEMA_URLS, scrape_cinema


def process_cinemas(cinemas, target_date):
    if target_date == -1:
        for day in range(8):
            screenings = process_scraped_data(cinemas, day)
            save_screenings_to_db(screenings)
            print(f"Processed and saved screenings for day {day}.")
    else:
        screenings = process_scraped_data(cinemas, target_date)
        save_screenings_to_db(screenings)
        print(f"Processed and saved screenings for day {target_date}.")


def query_screenings_by_date(target_date):
    if target_date == -1:
        for day in range(8):
            target_date_str = (datetime.now() + timedelta(days=day)).strftime(
                "%d %B %Y"
            )
            results = query_screenings(target_date_str)
            print_screenings(results, target_date_str)
    else:
        target_date_str = (datetime.now() + timedelta(days=target_date)).strftime(
            "%d %B %Y"
        )
        results = query_screenings(target_date_str)
        print_screenings(results, target_date_str)


def print_screenings(results, target_date_str):
    print(f"\nScreenings for {target_date_str}:")
    for row in results:
        print(f"Cinema: {row[0]}, Title: {row[1]}, Date: {row[2]}, Time: {row[3]}")


def main():
    parser = argparse.ArgumentParser(description="Cinema CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape cinema data")
    scrape_parser.add_argument("cinemas", nargs="*", help="List of cinemas to scrape")
    scrape_parser.add_argument(
        "--all", action="store_true", help="Scrape all available cinemas"
    )
    # Process command
    process_parser = subparsers.add_parser("process", help="Process scraped data")
    process_parser.add_argument("cinemas", nargs="+", help="List of cinemas to process")
    process_parser.add_argument(
        "target_date",
        type=int,
        choices=range(-1, 8),
        help="Target date (0=today, 1=tomorrow, ..., 7=one week later, -1=all week)",
    )

    # Scrape and process command
    scrape_process_parser = subparsers.add_parser(
        "scrape_and_process", help="Scrape and process all cinemas"
    )
    scrape_process_parser.add_argument(
        "target_date",
        type=int,
        choices=range(-1, 8),
        help="Target date (0=today, 1=tomorrow, ..., 7=one week later, -1=all week)",
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query screenings by date")
    query_parser.add_argument(
        "target_date",
        type=int,
        choices=range(-1, 8),
        help="Target date (0=today, 1=tomorrow, ..., 7=one week later, -1=all week)",
    )

    args = parser.parse_args()

    if args.command == "scrape":
        if args.all:
            scrape_cinema(list(CINEMA_URLS.keys()))
        else:
            scrape_cinema(args.cinemas)
    elif args.command == "process":
        process_cinemas(args.cinemas, args.target_date)
    elif args.command == "scrape_and_process":
        scrape_cinema(list(CINEMA_URLS.keys()))
        process_cinemas(list(CINEMA_URLS.keys()), args.target_date)
    elif args.command == "query":
        query_screenings_by_date(args.target_date)
    else:
        parser.print_help()


if __name__ == "__main__":
    setup_database()
    main()
