import requests
from bs4 import BeautifulSoup
import os
import re

CINEMA_URLS = {
    "phenomena": "https://www.phenomena-experience.com/programacion-peliculas/todas.html",
    "malda": "https://www.cinemamalda.com/cartelera-dia-dia/",
    "filmoteca": "https://www.filmoteca.cat/web/ca/view-agenda-setmanal",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
}
DAYS_ABBR = {
    "lu": "Lunes",
    "ma": "Martes",
    "mi": "Miércoles",
    "ju": "Jueves",
    "vi": "Viernes",
    "sa": "Sábado",
    "do": "Domingo"
}

def scrape_cinema(cinemas, output_dir="text/"):
    """
    Scrape selected cinemas and save their plain text output.
    """
    os.makedirs(output_dir, exist_ok=True)
    for cinema in cinemas:
        if cinema not in CINEMA_URLS:
            print(f"Unknown cinema: {cinema}")
            continue
        
        print(f"Scraping {cinema}...")
        response = requests.get(CINEMA_URLS[cinema], headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tag in ["head", "footer", "nav", "script"]:
            for element in soup.find_all(tag):
                element.decompose()
        
        #plain_text = soup.get_text(separator="\n", strip=True)
        plain_text = soup.get_text(separator='\n', strip=True).lower()

        for abbr, full in DAYS_ABBR.items():
            plain_text = re.sub(r'\b' + re.escape(abbr) + r'\b', full.lower(), plain_text)

        with open(os.path.join(output_dir, f"{cinema}.txt"), "w", encoding="utf-8") as file:
            file.write(plain_text)
        print(f"Scraped {cinema} successfully!")
