import json
import os
import pandas as pd
from config import CINEMAS, MODEL
from datetime import datetime, timedelta
import time
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import numpy as np

from llm import generate_prompt

def fetch_examples(training_dataset_path, input_text, similarity_based=True):
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

def ner(file_path: str, cinema: str, training_dataset_path: str, mode="static", target_dates=None):
    """
    Process scraped text data using GenAI to extract screenings for specified target dates.

    Args:
        file_path (str): Path to the file containing the scraped text data.
        cinema (str): The name of the cinema.
        training_dataset_path (str): Path to the training dataset.
        mode (str): Mode of generating the prompt - "static", "random", "similarity".
        target_dates (list, optional): List of target dates to extract screenings for. Defaults to calculating next week's dates.

    Returns:
        list: List of extracted screenings.
    """
    if target_dates is None:
        today = datetime.now()
        target_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((6 - today.weekday()) % 7 + 1)]
    else:
        # Ensure target dates are formatted as strings in 'YYYY-MM-DD'
        target_dates = [datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d") for date in target_dates]

    screenings = []
    start = time.time()
    
    for date in target_dates:
        if not os.path.exists(file_path):
            print(f"No data found for {cinema}. Run the scraper first.")
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        
        if mode == "static":
            prompt = generate_prompt(cinema, date, text, mode=mode)
        else:
            if mode == "random":
                example_input, example_output = fetch_examples(training_dataset_path, text, False)
            elif mode == "similarity":
                example_input, example_output = fetch_examples(training_dataset_path, text, True)
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
        print(f"Extracted {len(screenings) - count} screenings for {date} at {cinema}.")
    
    end = time.time()
    print(f"Extracted {len(screenings)} screenings in {end-start:.2f} seconds.")
    return screenings

def compute_metrics(extracted, ground_truth, labels):
    """
    Compare the extracted data with the ground truth and compute metrics for each label.
    """
    results = {label: {"precision": 0, "recall": 0, "f1_score": 0} for label in labels}

    extracted_indexed = {
        f"{s['screening_date']}-{s.get('screening_time', '')}": s
        for s in extracted
    }
    ground_truth_indexed = {
        f"{g['screening_date']}-{g.get('screening_time', '')}": g
        for _, g in ground_truth.iterrows()
    }

    print(f"Extracted indexed:\n {extracted_indexed}\n length: {len(extracted_indexed)}")
    print(f"Ground truth indexed:\n {ground_truth_indexed}\n length: {len(ground_truth_indexed)}")
          
    keys = ground_truth_indexed.keys()
    for i, key in enumerate(keys):
        gt = ground_truth_indexed.get(key, {})
        et = extracted_indexed.get(key, {})
        print(f"Ground truth {i}: {gt}")
        print(f"Extracted on {i}: {et}")

    for label in labels:
        y_true = []
        y_pred = []
        for key in keys:
            ground_truth_value = (
                str(ground_truth_indexed.get(key, {}).get(label, "")).lower()
            )
            extracted_value = (
                str(extracted_indexed.get(key, {}).get(label, "")).lower()
            )
            
            ground_truth_value = ground_truth_value if ground_truth_value not in ["nan", "none"] else "nan"
            extracted_value = extracted_value if extracted_value not in ["nan", "none"] else "nan"

            y_true.append(ground_truth_value)
            y_pred.append(extracted_value)

        print(f"y_true: {y_true}")
        print(f"y_pred: {y_pred}")

        # Compute precision, recall, and F1
        results[label]["precision"] = precision_score(y_true, y_pred, average='micro', zero_division=1)
        results[label]["recall"] = recall_score(y_true, y_pred, average='micro', zero_division=1)
        results[label]["f1_score"] = f1_score(y_true, y_pred, average='micro', zero_division=1)

    return results

def evaluation(train_dataset_path: str, test_dataset_path: str, web_dir_path: str, web_filename: str, web_name: str, target_dates=None):
    """
    Evaluate the model by comparing extracted data with ground truth and computing metrics.

    Args:
        train_dataset_path (str): Path to the training dataset.
        test_dataset_path (str): Path to the testing dataset.
        web_dir_path (str): Directory path where the scraped text files are located.
        web_filename (str): Filename of the scraped text file.
        web_name (str): Name of the cinema for evaluation.
        target_dates (list, optional): List of target dates in 'DD-MM-YYYY' format.
    
    Returns:
        None
    """
    # Load the testing dataset
    with open(test_dataset_path, mode='r') as file:
        test_ds = pd.read_csv(test_dataset_path)

    # Construct the path to the scraped text file
    web_path = os.path.join(web_dir_path, web_filename)

    # Perform Named Entity Recognition (NER) to extract screenings
    screenings = ner(web_path, web_name, train_dataset_path, target_dates=target_dates)

    print("---SCREENINGS---")
    print(screenings)

    # Define the labels to evaluate
    labels = [
        "cinema", "title", "original_title", "director", "year_of_release",
        "screening_date", "screening_time", "language", "price", "cast"
    ]

    # Compute the performance metrics
    metrics = compute_metrics(screenings, test_ds, labels)

    # Display the performance metrics
    print("\n--- PERFORMANCE METRICS ---")
    for label, scores in metrics.items():
        print(f"Label: {label}")
        print(f"  Precision: {scores['precision']:.2f}")
        print(f"  Recall: {scores['recall']:.2f}")
        print(f"  F1 Score: {scores['f1_score']:.2f}\n")

custom_dates = ["25-12-2024", "26-12-2024", "27-12-2024", "28-12-2024", "29-12-2024", "30-12-2024", "31-12-2024"]
evaluation('datasets/training_dataset.csv', 'datasets/testing_dataset_phenomena_24.csv', "text", "phenomena_24.txt", "phenomena", target_dates=custom_dates)
