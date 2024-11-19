import os
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key="AIzaSyAC1jdMgX-vFz6Ox1MxbO11PQbKLV_FYRw")

def process_scraped_data(cinemas, target_date, input_dir="text/"):
    """
    Process scraped text data using GenAI to extract screenings for a target date.
    """
    target_date = (datetime.now() + timedelta(days=target_date)).strftime("%d %B %Y")
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
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
        The output should be a JSON list of films with these fields:
        - title
        - original_title
        - director
        - year_of_release
        - screening_times
        - screening_date
        - language
        - cinema
        - price
        - cast
        """
        
        prompt += f"\n{text}"
        
        result = model.generate_content(prompt)
        #print(f"Result obtained: {result}")
        #screenings.extend(json.loads(result.text.replace("```", "").strip()))
        #screenings.extend(json.loads(result.text.replace("json", "").replace("```", "")))
        try:
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]  # Remove the initial ```json
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]  # Remove the ending ```
            screenings.extend(json.loads(raw_text))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for cinema {cinema}: {e}")
            continue
            
    return screenings
