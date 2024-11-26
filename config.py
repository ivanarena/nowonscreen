import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# llm 
CONTEXT = """
    You are a linguist specialized in named entity recognition, with knowledge
    about films and cinemas. Your role is to detect information about film
    screenings and showtimes and organize it into a structured output for the 
    user.
"""
MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=CONTEXT,
)

# scraper etc.
CINEMA_URLS = {
    "phenomena": "https://www.phenomena-experience.com/programacion-peliculas/todas.html",
    "malda": "https://www.cinemamalda.com/cartelera-dia-dia/",
    "filmoteca": "https://www.filmoteca.cat/web/ca/view-agenda-setmanal",
}
CINEMAS = list(CINEMA_URLS.keys())
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
    "do": "Domingo",
}

