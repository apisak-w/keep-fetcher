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
    Only processes lines starting with ☐ (unchecked). Ignores ☑ (checked).
    """
    stripped_line = line.strip()
    
    # Strict filter: Must start with ☐
    if not stripped_line.startswith("☐"):
        return None

    # Remove check box and leading/trailing whitespace
    clean_line = stripped_line.replace("☐", "", 1).strip()
    
    if not clean_line:
        return None

    # Regex to find the last number in the string which is likely the amount
    # We use greedy match (.*) for description to ensure we capture everything 
    # up to the LAST number in the line.
    
    # Pattern: 
    # ^(.*)         -> Group 1: Description (greedy match)
    # \s+           -> Separator space
    # (\d+(?:\.\d+)?) -> Group 2: Amount (integer or float)
    # (?:\s+UNCLEARED)? -> Optional UNCLEARED tag
    # .*$           -> Any remaining characters
    
    match = re.search(r'^(.*)\s+(\d+(?:\.\d+)?)(?:\s+UNCLEARED)?.*$', clean_line, re.IGNORECASE)
    
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

def get_category(description):
    """Categorizes expense based on description keywords."""
    desc_lower = description.lower()
    
    categories = {
        'Shopping': ['book', 'gift', 'clothes', 'shoes', 'bag', 'amazon', 'lazada', 'shopee', 'sofa', 'tuya', 'adapter', 'phone', 'belt', 'coffee table', 'battery', 'key', 'ladle', 'lamp', 'perfume', 'rug', 'stairs', 'home appliance', 'housewares', 'shirt', 'shorts', 'toothpaste'],
        'Food': ['food', 'lunch', 'dinner', 'breakfast', 'snack', 'meal', 'drink'],
        'Transport': ['mrt', 'bts', 'taxi', 'motorcycle', 'bus', 'rabbit', 'grab', 'uber', 'train', 'flight', 'mrt', 'tsubaru', 'airport', 'express', 'two row car', 'arl', 'srt'],
        'Utilities': ['mobile', 'top-up', 'mobile top up', 'icloud', 'internet', 'bill', 'subscription', 'netflix', 'spotify'],
        'Entertainment': ['movie', 'cinema', 'game', 'concert', 'ticket', 'show', 'party', 'bar', 'club', 'youtube', 'disney', 'badminton'],
        'Personal': ['haircut', 'gym', 'sport', 'massage', 'spa', 'doctor', 'medicine', 'driving', 'medical', 'personal care'],
        'Housing/Car': ['car', 'rent', 'condo', 'electricity', 'water', 'home', 'house'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
            
    return 'Other'

def process_expenses(input_file='outputs/keep_notes.csv', output_file='outputs/expenses_processed.csv'):
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
                    'category': get_category(item['description']),
                    'description': item['description'],
                    'amount': item['amount'],
                    'uncleared': item['uncleared']
                })

    if not processed_data:
        print("No expense items extracted.")
        return

    result_df = pd.DataFrame(processed_data)
    
    # Sort by date descending
    result_df = result_df.sort_values(by='date', ascending=False)
    
    print(f"Extracted {len(result_df)} expense items.")
    # Save to CSV
    output_file = 'outputs/expenses_processed.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Processed {len(df)} expense items.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    process_expenses()
