import os
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

context = """
    You are a linguist specialized in named entity recognition, with knowledge
    about films and cinemas. Your role is to detect information about film
    screenings and showtimes and organize it into a structured output for the 
    user.
"""
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=context
)

# read scraped files
data_path = "text/"
data = {}
for filename in os.listdir(data_path):
    if filename.endswith(".txt"):
        with open(os.path.join(data_path, filename), 'r', encoding='utf-8') as file:
            data[filename[:-4]] = file.read()

tomorrow = f"{datetime.now() + timedelta(days=1):%d %B %Y}"
for venue in data.keys():
    prompt = f"""
        extract all the screenings occuring tomorrow {tomorrow} from this text from cinema {venue}. The output
        must be a json list of films, including the following information if available:
            - title
            - original_title
            - director
            - year_of_release
            - screening times 
            - screening date
            - language
            - cinema (as above)
            - price
            - cast
    If a screening is at multiple times on the same day, only include it once in your answer but point all the times.\n
    """  + data[venue],

    result = model.generate_content(
        prompt,
    )
    screenings = json.loads(result.text.replace("json", "").replace("```", ""))
    for screening in screenings:
        print(json.dumps(screening, indent=4))     