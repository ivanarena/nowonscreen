import json
import os
from datetime import datetime, timedelta
from config import CINEMAS, MODEL
import time


def generate_prompt(cinema, date, text, example_input=None, example_output=None, mode="static"):
    """
    Generate the prompt dynamically based on the mode.

    Args:
        cinema (str): Name of the cinema.
        date (str): Date for the screenings.
        text (str): Input text to process.
        example_input (str, optional): Example input from the training dataset.
        example_output (str, optional): Example output from the training dataset.
        mode (str): Mode of generating the prompt - "static", "random", "similarity".

    Returns:
        str: The complete prompt.
    """
    if mode == "static":
        # Fixed static example
        example_prompt = """
        ### Example Output
        ```json
        [
            {{
                "cinema": "{cinema}",
                "title": "Film Title (in spanish or catalan). Just include the film title, not (4K), (VOE)...",
                "original_title": "Original Title",
                "director": "Director Name",
                "year_of_release": YYYY,
                "screening_date": "{date}",
                "screening_time": "HH:MM" (without 'h'),
                "language": "Language",
                "price": "€XX",
                "cast": ["Actor A", "Actor B"]
            }},
            ...
        ]
        ```
        """
    elif mode == "random" or mode == "similarity" and example_input and example_output:
        # Randomly sampled example
        example_prompt = f"""
        ### Example Input
        {example_input}

        ### Example Output
        {example_output}
        """
    else:
        raise ValueError("Invalid mode or missing example input/output for selected mode.")
    
    prompt = f"""
    Extract all screenings occurring on {date} from the following text for cinema '{cinema}'.
    Each screening must be represented as a **separate JSON object**, even if the same film is shown multiple times.
    The output must be a JSON list, and each object must include:
    - "cinema": The name of the cinema (always '{cinema}').
    - "title": The title of the film (might be a spanish or catalan translation).
    - "original_title": The original title of the film (if different, otherwise use the title).
    - "director": The director of the film (if available).
    - "year_of_release": The year the film was released (if available).
    - "screening_date": The date of the screening (must be {date}).
    - "screening_time": The exact time of the screening (one time per object).
    - "language": The language of the film (if available).
    - "price": The price of the ticket (if available).
    - "cast": A list of main cast members (if available).

    {example_prompt}

    {text}
    """
    return prompt

def ner(input_dir="text/"):
    """
    Process scraped text data using GenAI to extract screenings for a target date.
    """
    today = datetime.now()
    current_week = today.isocalendar()[1]
    target_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((6 - today.weekday()) % 7 + 1)]
    screenings = []
    start = time.time()
    for date in target_dates:
        for cinema in CINEMAS:
            file_path = os.path.join(input_dir, f"{cinema}_w{current_week}.txt")
            if not os.path.exists(file_path):
                print(f"No data found for {cinema}. Run the scraper first.")
                continue

            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            prompt = generate_prompt(cinema, date, text, mode="static")
            
            result = MODEL.generate_content(prompt)
            count = len(screenings)
            screenings.extend(
                json.loads(result.text.replace("json", "").replace("```", ""))
            )
            time.sleep(5) # Avoid rate limiting
            print(f"Extracted {len(screenings)-count} screenings for {date} at {cinema}.")
        time.sleep(30) # Avoid rate limiting
    end = time.time()
    print(f"Extracted {len(screenings)} screenings in {end-start:.2f} seconds.")
    return screenings
