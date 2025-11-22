import pandas as pd
import re
from datetime import datetime

def parse_date(date_str):
    """
    Parses date string like "November 22th, 2025" into a datetime object.
    Handles ordinal suffixes (st, nd, rd, th).
    """
    try:
        # Remove ordinal suffixes (st, nd, rd, th) from the day
        # Regex looks for a digit followed by st, nd, rd, or th, and removes the suffix
        clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        return datetime.strptime(clean_date_str, "%B %d, %Y").date()
    except ValueError:
        return None

def parse_expense_line(line):
    """
    Extracts description and amount from a line.
    Expected format: "☐ Description Amount [UNCLEARED]"
    """
    # Remove check box and leading/trailing whitespace
    clean_line = line.replace("☐", "").replace("☑", "").strip()
    
    if not clean_line:
        return None

    # Regex to find the last number in the string which is likely the amount
    # This handles cases like "Food 159" or "Monthly car payment 18975"
    # It assumes the amount is at the end or near the end (before optional UNCLEARED)
    
    # Pattern: 
    # ^(.*?)        -> Group 1: Description (lazy match from start)
    # \s+           -> Separator space
    # (\d+(?:\.\d+)?) -> Group 2: Amount (integer or float)
    # (?:\s+UNCLEARED)? -> Optional UNCLEARED tag
    # .*$           -> Any remaining characters
    
    match = re.search(r'^(.*?)\s+(\d+(?:\.\d+)?)(?:\s+UNCLEARED)?.*$', clean_line, re.IGNORECASE)
    
    if match:
        description = match.group(1).strip()
        amount = float(match.group(2))
        is_uncleared = "UNCLEARED" in clean_line.upper()
        return {
            'description': description,
            'amount': amount,
            'uncleared': is_uncleared
        }
    
    return None

def process_expenses(input_file='keep_notes.csv', output_file='expenses_processed.csv'):
    print(f"Reading {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # Filter for expense notes
    # Assuming 'labels' column contains string representation of list like "['💸 expense']"
    expense_notes = df[df['labels'].str.contains('expense', case=False, na=False)]
    
    print(f"Found {len(expense_notes)} expense notes.")
    
    processed_data = []

    for index, row in expense_notes.iterrows():
        note_date = parse_date(row['title'])
        
        if not note_date:
            # print(f"Skipping note with invalid date title: {row['title']}")
            continue
            
        lines = str(row['text']).split('\n')
        
        for line in lines:
            item = parse_expense_line(line)
            if item:
                processed_data.append({
                    'date': note_date,
                    'description': item['description'],
                    'amount': item['amount'],
                    'uncleared': item['uncleared'],
                    'original_note_title': row['title'],
                    'note_id': row['id']
                })

    if not processed_data:
        print("No expense items extracted.")
        return

    result_df = pd.DataFrame(processed_data)
    
    # Sort by date descending
    result_df = result_df.sort_values(by='date', ascending=False)
    
    print(f"Extracted {len(result_df)} expense items.")
    print(f"Saving to {output_file}...")
    result_df.to_csv(output_file, index=False)
    print("Done.")
    
    print("\nSample Data:")
    print(result_df.head())

if __name__ == "__main__":
    process_expenses()
