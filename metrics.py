def compute_metrics(extracted_df, test_df):
    """
    Compare the extracted data with the ground truth and compute metrics for each field.
    """
    # Create a unique identifier for matching (a tuple of selected fields)
    extracted_df["key"] = extracted_df[["cinema", "title", "screening_date", "screening_time"]].apply(tuple, axis=1)
    test_df["key"] = test_df[["cinema", "title", "screening_date", "screening_time"]].apply(tuple, axis=1)

    # Match keys
    extracted_keys = set(extracted_df["key"])
    test_keys = set(test_df["key"])
    
    print("Extracted keys:", len(extracted_keys), len(extracted_df))
    print("Test keys:", len(test_keys), len(test_df))

    # Compute true positives, false positives, and false negatives
    # For every test key, look for the respective in extracted
    matched_keys = []
    for key in test_keys:
        if key in extracted_keys:
            matched_keys.append(key)
    print(f"Matched {len(matched_keys)} keys out of {len(test_keys)}.")
    
    # Precision measures how many of the extracted screenings are correct (i.e., match the ground truth). 
    true_positives = 0
    total_fields = 0
    for key in matched_keys:
        extracted_row = extracted_df[extracted_df["key"] == key].iloc[0]
        test_row = test_df[test_df["key"] == key].iloc[0]
        for field in extracted_df.columns:
            if extracted_row[field] == test_row[field]:
                true_positives += 1
            else:
                print(f"Comparing {field} {extracted_row[field]} with {test_row[field]} for key {key}.")
            total_fields += 1
    precision = true_positives / total_fields if total_fields > 0 else 0
    print(f"True Positives: {true_positives}, Total Fields: {total_fields}")

    # Recall measures how many of the actual screenings in the ground truth were successfully extracted.
    recall = len(matched_keys) / len(test_keys)
    f1_score = 2 * (precision * recall) / (precision + recall)
    
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score
    }

    return metrics