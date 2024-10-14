import requests
from bs4 import BeautifulSoup
import os

os.makedirs('html', exist_ok=True)
os.makedirs('text', exist_ok=True)

urls = {
    "phenomena": 'https://www.phenomena-experience.com/programacion-peliculas/todas.html',
    "malda": "https://www.cinemamalda.com/"
}


for cine in urls.keys():
    response = requests.get(urls[cine])
    
    with open(f'html/{cine}.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    plain_text = soup.get_text(separator='\n', strip=True)
    
    with open(f'text/{cine}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(plain_text)
    
    print(f"Scraped {cine} page.")

