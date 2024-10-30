import requests
from bs4 import BeautifulSoup
import os
import re

os.makedirs('html', exist_ok=True)
os.makedirs('text', exist_ok=True)

urls = {
    "phenomena": 'https://www.phenomena-experience.com/programacion-peliculas/todas.html',
    "malda": "https://www.cinemamalda.com/",
    "verdi": "https://barcelona.cines-verdi.com/cartelera",
    "filmoteca": "https://www.filmoteca.cat/web/ca/view-agenda-setmanal",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
}
days_abbr = {
    "lu": "Lunes",
    "ma": "Martes",
    "mi": "Miércoles",
    "ju": "Jueves",
    "vi": "Viernes",
    "sa": "Sábado",
    "do": "Domingo"
}


for cine in urls.keys():
    response = requests.get(urls[cine], headers=headers)

    with open(f'html/{cine}.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    plain_text = soup.get_text(separator='\n', strip=True).lower() # convert to lowercase

    for abbr, full in days_abbr.items(): # replace abbreviated days of the week with full names 
        plain_text = re.sub(r'\b' + re.escape(abbr) + r'\b', full.lower(), plain_text)

    with open(f'text/{cine}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(plain_text)
    
    print(f"Scraped {cine} page.")

