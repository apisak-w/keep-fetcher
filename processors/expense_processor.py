import os
import re
from datetime import datetime
import pandas as pd


# ============================================================================
# Configuration
# ============================================================================

EXPENSE_CATEGORIES = {
    'Shopping': [
        'book', 'gift', 'clothes', 'shoes', 'bag', 'amazon', 'lazada', 
        'shopee', 'sofa', 'tuya', 'adapter', 'phone', 'belt', 'coffee table', 
        'battery', 'key', 'ladle', 'lamp', 'perfume', 'rug', 'stairs', 
        'home appliance', 'housewares', 'shirt', 'shorts', 'toothpaste'
    ],
    'Food': [
        'food', 'lunch', 'dinner', 'breakfast', 'snack', 'meal', 'drink'
    ],
    'Transport': [
        'mrt', 'bts', 'taxi', 'motorcycle', 'bus', 'rabbit', 'grab', 'uber', 
        'train', 'flight', 'tsubaru', 'airport', 'express', 'two row car', 
        'arl', 'srt'
    ],
    'Utilities': [
        'mobile', 'top-up', 'mobile top up', 'icloud', 'internet', 'bill', 
        'subscription', 'netflix', 'spotify'
    ],
    'Entertainment': [
        'movie', 'cinema', 'game', 'concert', 'ticket', 'show', 'party', 
        'bar', 'club', 'youtube', 'disney', 'badminton'
    ],
    'Personal': [
        'haircut', 'gym', 'sport', 'massage', 'spa', 'doctor', 'medicine', 
        'driving', 'medical', 'personal care'
    ],
    'Housing/Car': [
        'car', 'rent', 'condo', 'electricity', 'water', 'home', 'house'
    ],
}

INPUT_FILE = 'outputs/keep_notes.csv'
OUTPUT_FILE = 'outputs/expenses_processed.csv'


# ============================================================================
# Parsing Functions
# ============================================================================

def parse_date(date_str):
    """Parse date string like 'November 22th, 2025' into a date object."""
    try:
        # Remove ordinal suffixes (st, nd, rd, th)
        clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        return datetime.strptime(clean_date_str, "%B %d, %Y").date()
    except ValueError:
        return None


def parse_expense_line(line):
    """
    Extract description and amount from an expense line.
    
    Expected format: "☐ Description Amount [UNCLEARED]"
    Only processes unchecked items (☐). Ignores checked items (☑).
    
    Returns:
        dict or None: {'description': str, 'amount': float, 'uncleared': bool}
    """
    stripped_line = line.strip()
    
    # Only process unchecked items
    if not stripped_line.startswith("☐"):
        return None

    # Remove checkbox and clean
    clean_line = stripped_line.replace("☐", "", 1).strip()
    if not clean_line:
        return None

    # Extract description and amount
    # Pattern: Description + Amount + Optional UNCLEARED
    match = re.search(
        r'^(.*)\\s+(\\d+(?:\\.\\d+)?)(?:\\s+UNCLEARED)?.*$', 
        clean_line, 
        re.IGNORECASE
    )
    
    if not match:
        return None
        
    return {
        'description': match.group(1).strip(),
        'amount': float(match.group(2)),
        'uncleared': "UNCLEARED" in clean_line.upper()
    }


def categorize_expense(description):
    """Categorize expense based on keywords in description."""
    desc_lower = description.lower()
    
    for category, keywords in EXPENSE_CATEGORIES.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
            
    return 'Other'


# ============================================================================
# Main Processing
# ============================================================================

def process_expenses(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """
    Process expense notes from Keep and export to CSV.
    
    Args:
        input_file: Path to keep_notes.csv
        output_file: Path to save processed expenses
    """
    print(f"Reading {input_file}...")
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # Filter for expense notes
    expense_notes = df[df['labels'].str.contains('expense', case=False, na=False)]
    print(f"Found {len(expense_notes)} expense notes.")
    
    # Process each expense note
    processed_data = []
    for _, row in expense_notes.iterrows():
        note_date = parse_date(row['title'])
        if not note_date:
            continue
            
        # Parse each line in the note
        for line in str(row['text']).split('\\n'):
            item = parse_expense_line(line)
            if item:
                processed_data.append({
                    'date': note_date,
                    'category': categorize_expense(item['description']),
                    'description': item['description'],
                    'amount': item['amount'],
                    'uncleared': item['uncleared']
                })

    if not processed_data:
        print("No expense items extracted.")
        return

    # Create DataFrame and sort
    result_df = pd.DataFrame(processed_data)
    result_df = result_df.sort_values(by='date', ascending=False)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    result_df.to_csv(output_file, index=False)
    
    print(f"Extracted {len(result_df)} expense items.")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    process_expenses()
