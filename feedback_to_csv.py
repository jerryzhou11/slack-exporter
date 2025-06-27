#!/usr/bin/env python3
import json
import csv
import sys
import os
import re
from datetime import datetime

def extract_feedback(json_file, csv_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Only keep messages with a 'text' field
    feedbacks = [msg for msg in data if isinstance(msg, dict) and 'text' in msg]

    # Regex to match everything from 'image _' to the end of the string
    metadata_pattern = re.compile(r' image _.*$', re.UNICODE)

    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['feedback_text'])
        for msg in feedbacks:
            text = msg['text'].replace('\n', ' ').replace('\r', ' ').strip()
            # Remove the metadata pattern at the end
            text = metadata_pattern.sub('', text)
            writer.writerow([text])
    print(f"Extracted {len(feedbacks)} feedback messages to {csv_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 feedback_to_csv.py <input_json_file> <output_csv_file>")
        sys.exit(1)
    json_file = sys.argv[1]
    csv_file = sys.argv[2]
    if not os.path.exists(json_file):
        print(f"Error: {json_file} does not exist")
        sys.exit(1)
    extract_feedback(json_file, csv_file) 