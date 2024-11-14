import requests
from bs4 import BeautifulSoup
import os
import re

os.makedirs('html', exist_ok=True)
os.makedirs('text', exist_ok=True)

urls = {
    "phenomena": 'https://www.phenomena-experience.com/programacion-peliculas/todas.html',
    "malda": "https://www.cinemamalda.com/cartelera-dia-dia/",
    # "verdi": "https://barcelona.cines-verdi.com/cartelera", # not very accessible
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
    # parse html and remove useless tags
    response = requests.get(urls[cine], headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in ["head", "footer", "nav", "script"]:
        for element in soup.find_all(tag):
            element.decompose()
    
    plain_text = soup.get_text(separator='\n', strip=True).lower()
    
    # replace abbreviations with full names
    for abbr, full in days_abbr.items():
        plain_text = re.sub(r'\b' + re.escape(abbr) + r'\b', full.lower(), plain_text)

    # save plain text to file
    with open(f'text/{cine}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(plain_text)
    
    print(f"Scraped {cine}.")


