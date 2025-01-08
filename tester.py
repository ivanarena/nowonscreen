import json
import re
import os
import pandas as pd
from config import MODEL
from datetime import datetime, timedelta
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
from llm import generate_prompt
from metrics import compute_metrics
import argparse


def postprocess(extracted_df):
    extracted_df = extracted_df.sort_values(by=['cinema', 'screening_date', 'screening_time'])
    for _, row in extracted_df.iterrows():
        if row["screening_time"][-1] == 'h':
            row["screening_time"] = row["screening_time"][:-1]
        row["title"] = re.sub(r'\s*\((?:4k|dolby atmos)(?: [^)]*)?\)', '', row["title"], flags=re.IGNORECASE)
        if row["year_of_release"]:
            row["year_of_release"] = int(str(row["year_of_release"])[:4])
        if row["price"]:
            row["price"] = f"€{row['price'].replace('€', '')}"
        if row["cast"]:
            row["cast"] = ', '.join(row["cast"]).replace("ʻ", "'").replace('"', "")
        else:
            row["cast"] = "nan"
        for field in row.index:
            if not row[field]:
                row[field] = "nan"
    return extracted_df


def normalize(df):
    for field in df.columns:
        df[field] = (
            df[field]
            .astype(str)  # Ensure all values are converted to strings
            .str.lower()  # Convert to lowercase
            .str.strip()  # Remove leading/trailing whitespace
            .fillna("")   # Replace NaN values with an empty string
        )
    return df


def fetch_examples(
        training_dataset_path, 
        input_text, 
        similarity_based=True
):
    """
    Fetch Example Input and Output from the training dataset.
    
    Args:
        training_dataset_path (str): Path to the training dataset (CSV format expected).
        input_text (str): The input text for which examples are sought.
        similarity_based (bool): If True, fetch based on similarity; else fetch randomly.
    
    Returns:
        tuple: A tuple (example_input, example_output).
    """
    # Load training dataset
    training_df = pd.read_csv(training_dataset_path)
    
    # Assume training dataset has 'example_input' and 'example_output' columns
    example_inputs = training_df['example_input']
    example_outputs = training_df['example_output']
    
    if similarity_based:
        # Compute similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(example_inputs)
        input_vector = vectorizer.transform([input_text])
        similarity_scores = cosine_similarity(input_vector, tfidf_matrix).flatten()
        
        # Get the most similar example
        most_similar_idx = similarity_scores.argmax()
        example_input = example_inputs.iloc[most_similar_idx]
        example_output = example_outputs.iloc[most_similar_idx]
    else:
        # Random sampling
        random_idx = random.randint(0, len(training_df) - 1)
        example_input = example_inputs.iloc[random_idx]
        example_output = example_outputs.iloc[random_idx]
    
    return example_input, example_output


def ner(
        filename: str, 
        cinema: str, 
        training_dataset_path: str, 
        mode="static", 
):
    """
    Process scraped text data using GenAI to extract screenings for specified target dates.

    Args:
        filename (str): Path to the file containing the scraped text data.
        cinema (str): The name of the cinema.
        training_dataset_path (str): Path to the training dataset.
        mode (str): Mode of generating the prompt - "static", "random", "similarity".
        target_dates (list, optional): List of target dates to extract screenings for. Defaults to calculating next week's dates.

    Returns:
        list: List of extracted screenings.
    """
    # get weeks dates from testing dataset
    week_number = int(filename.split('_')[-1].split('.')[0][1:])
    year = 2024
    first_day_of_year = datetime(year, 1, 1)
    first_week_start = first_day_of_year - timedelta(days=first_day_of_year.weekday())
    target_dates = [(first_week_start + timedelta(weeks=week_number - 1) + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    screenings = []
    start = time.time()
    
    for date in target_dates:
        if not os.path.exists(filename):
            print(f"No data found for {cinema}. Run the scraper first.")
            continue

        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()
        
        if mode == "static":
            prompt = generate_prompt(cinema, date, text, mode=mode)
        else:
            if mode == "random":
                example_input, example_output = fetch_examples(training_dataset_path, text, similarity_based=False)
            elif mode == "similarity":
                example_input, example_output = fetch_examples(training_dataset_path, text, similarity_based=True)
            prompt = generate_prompt(cinema, date, text, example_input, example_output, mode=mode)

        result = MODEL.generate_content(prompt)
        count = len(screenings)
        try:
            screenings.extend(
                json.loads(result.text.replace("json", "").replace("```", ""))
            )
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for date {date}: {e}")
        time.sleep(5)  # Avoid rate limiting
        # print(f"Extracted {len(screenings) - count} screenings for {date} at {cinema} (from {filename}).")
    
    end = time.time()
    print(f"Extracted {len(screenings)} screenings in {end-start:.2f} seconds.")
    return screenings



def evaluate(
        mode: str,
):
    """
    Evaluate the model by comparing extracted data with ground truth and computing metrics.

    Args:
        mode (str): Example selection mode.
        target_dates (list, optional): List of target dates in 'DD-MM-YYYY' format.
    
    Returns:
        None
    """
    test_df = pd.read_csv(os.path.join('test', "screenings.csv"))
    screenings = []
    filenames = test_df.drop_duplicates(subset=['filename'])
    for _, row in filenames.iterrows():
        filename = row['filename']
        cinema = row['cinema']
        input_examples = 'examples.csv'
        print("Extracting screenings from", filename)
        screenings.extend(ner(os.path.join('text', filename), cinema, input_examples, mode=mode))


    # Convert screenings to DataFrame
    screenings_df = pd.DataFrame(screenings)
    # screenings_df = pd.read_csv('extracted_screenings_test.csv') # only for debug
    # screenings_df.to_csv('extracted_screenings_test.csv', index=False)
    
    extracted_df = postprocess(screenings_df)
    extracted_df = normalize(extracted_df)
    test_df = normalize(test_df)

    metrics = compute_metrics(extracted_df, test_df)
    print(metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the evaluation script with specified mode.")
    parser.add_argument('-m', '--mode', type=str, default="static", help='Mode of generating the prompt - "static", "random", "similarity".')
    args = parser.parse_args()

    evaluate(mode=args.mode)
