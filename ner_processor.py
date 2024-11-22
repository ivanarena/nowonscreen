import os
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key="")

context = """
    You are a linguist specialized in named entity recognition, with knowledge
    about films and cinemas. Your role is to detect information about film
    screenings and showtimes and organize it into a structured output for the 
    user.
"""

def process_scraped_data(cinemas, target_date, input_dir="text/"):
    """
    Process scraped text data using GenAI to extract screenings for a target date.
    """
    target_date = (datetime.now() + timedelta(days=target_date)).strftime("%d %B %Y")
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=context,    
    )
    
    screenings = []
    for cinema in cinemas:
        file_path = os.path.join(input_dir, f"{cinema}.txt")
        if not os.path.exists(file_path):
            print(f"No data found for {cinema}. Run the scraper first.")
            continue
        
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        
        prompt = f"""
        Extract all screenings occurring on {target_date} from the following text for cinema '{cinema}'.
        Each screening must be represented as a **separate JSON object**, even if the same film is shown multiple times.
        The output must be a JSON list, and each object must include:
        - "cinema": The name of the cinema (always '{cinema}').
        - "title": The title of the film.
        - "original_title": The original title of the film (if different, otherwise use the title).
        - "director": The director of the film (if available).
        - "year_of_release": The year the film was released (if available).
        - "screening_date": The date of the screening (must be {target_date}).
        - "screening_time": The exact time of the screening (one time per object).
        - "language": The language of the film (if available).
        - "price": The price of the ticket (if available).
        - "cast": A list of main cast members (if available).

        ### Example Output
        ```json
        [
            {{
                "cinema": "phenomena",
                "title": "Film Title",
                "original_title": "Original Title",
                "director": "Director Name",
                "year_of_release": 1999,
                "screening_date": "20 November 2024",
                "screening_time": "18:00",
                "language": "English",
                "price": "€12",
                "cast": ["Actor A", "Actor B"]
            }},
            {{
                "cinema": "phenomena",
                "title": "Film Title",
                "original_title": "Original Title",
                "director": "Director Name",
                "year_of_release": 1999,
                "screening_date": "20 November 2024",
                "screening_time": "20:00",
                "language": "English",
                "price": "€12",
                "cast": ["Actor A", "Actor B"]
            }}
        ]
        """
        
        prompt += f"\n{text}"
        
        result = model.generate_content(prompt)
        print(f"Result for cinema {cinema}:\n{result}")
        #print(f"Result obtained: {result}")
        #screenings.extend(json.loads(result.text.replace("```", "").strip()))
        screenings.extend(json.loads(result.text.replace("json", "").replace("```", "")))
        #try:
        #    if raw_text.startswith("```json"):
        #        raw_text = raw_text[7:]  # Remove the initial ```json
        #    if raw_text.endswith("```"):
        #        raw_text = raw_text[:-3]  # Remove the ending ```
        #    screenings.extend(json.loads(raw_text))
        #except json.JSONDecodeError as e:
        #    print(f"Error decoding JSON for cinema {cinema}: {e}")
        #    continue
            
    return screenings
