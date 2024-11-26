import os
import re
import requests
from bs4 import BeautifulSoup
from config import CINEMA_URLS, HEADERS, DAYS_ABBR
from datetime import datetime

def scrape(output_dir="text/"):
    """
    Scrape selected cinemas and save their plain text output.
    """
    current_week = datetime.now().isocalendar()[1]
    do_scrape = False
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            file_week = datetime.fromtimestamp(os.path.getmtime(file_path)).isocalendar()[1]
            if file_week != current_week:
                do_scrape = True
                break
        break

    if not do_scrape:
        return
    
    os.makedirs(output_dir, exist_ok=True)
    for cinema in CINEMA_URLS:
        print(f"Scraping {cinema}...")
        response = None
        soup = None
        for _ in range(3):
            try:
                response = requests.get(CINEMA_URLS[cinema], headers=HEADERS, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                print(f"Attempt failed: {e}")
        
        if response is None or soup is None:
            print(f"Failed to scrape {cinema} after 3 attempts.")
            continue

        for tag in ["head", "footer", "nav", "script"]:
            for element in soup.find_all(tag):
                element.decompose()

        plain_text = soup.get_text(separator="\n", strip=True).lower()

        for abbr, full in DAYS_ABBR.items():
            plain_text = re.sub(
                r"\b" + re.escape(abbr) + r"\b", full.lower(), plain_text
            )

        with open(
            os.path.join(output_dir, f"{cinema}.txt"), "w", encoding="utf-8"
        ) as file:
            file.write(plain_text)
        print(f"Scraped {cinema} successfully!")
