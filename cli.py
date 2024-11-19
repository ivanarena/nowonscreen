import argparse
from datetime import datetime, timedelta
from scraper import scrape_cinema
from ner_processor import process_scraped_data
from db_utils import setup_database, save_screenings_to_db, query_screenings

def main():
    parser = argparse.ArgumentParser(description="Cinema CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape cinema data")
    scrape_parser.add_argument("cinemas", nargs="+", help="List of cinemas to scrape")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process scraped data")
    process_parser.add_argument("cinemas", nargs="+", help="List of cinemas to process")
    process_parser.add_argument("target_date", type=int, choices=range(-1, 8),
                                help="Target date (0=today, 1=tomorrow, ..., 7=one week later, -1=all week)")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query screenings by date")
    query_parser.add_argument("target_date", type=int, choices=range(-1, 8),
                               help="Target date (0=today, 1=tomorrow, ..., 7=one week later, -1=all week)")

    args = parser.parse_args()

    if args.command == "scrape":
        scrape_cinema(args.cinemas)
    elif args.command == "process":
        if args.target_date == -1:
            for day in range(8):  # Process for all 7 days (0 to 7 inclusive)
                screenings = process_scraped_data(args.cinemas, day)
                save_screenings_to_db(screenings)
            print("Processed and saved screenings for the entire week.")
        else:
            screenings = process_scraped_data(args.cinemas, args.target_date)
            save_screenings_to_db(screenings)
            print(f"Processed and saved screenings for day {args.target_date}.")
    elif args.command == "query":
        if args.target_date == -1:
            for day in range(8):  # Query for all 7 days (0 to 7 inclusive)
                target_date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
                results = query_screenings(target_date)
                print(f"\nScreenings for {target_date}:")
                for row in results:
                    print(f"Cinema: {row[0]}, Title: {row[1]}, Date: {row[2]}, Times: {row[3]}")
        else:
            target_date = (datetime.now() + timedelta(days=args.target_date)).strftime("%Y-%m-%d")
            results = query_screenings(target_date)
            print(f"\nScreenings for {target_date}:")
            for row in results:
                print(f"Cinema: {row[0]}, Title: {row[1]}, Date: {row[2]}, Times: {row[3]}")
    else:
        parser.print_help()

if __name__ == "__main__":
    setup_database()
    main()
