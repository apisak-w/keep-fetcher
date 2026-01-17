"""
Configuration constants for Google Keep Fetcher.

This module contains all configuration values used across the application.
"""


# ============================================================================
# File Paths
# ============================================================================

# Output directory
OUTPUT_DIR = "outputs"

# Output files
KEEP_NOTES_CSV = f"{OUTPUT_DIR}/keep_notes.csv"
EXPENSES_PROCESSED_CSV = f"{OUTPUT_DIR}/expenses_processed.csv"


# ============================================================================
# Expense Categories
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


# ============================================================================
# Google Sheets Formatting
# ============================================================================

COLUMN_FORMATS = {
    'date': {
        'numberFormat': {
            'type': 'DATE',
            'pattern': 'yyyy-mm-dd'
        },
        'horizontalAlignment': 'CENTER'
    },
    'amount': {
        'numberFormat': {
            'type': 'NUMBER',
            'pattern': '#,##0.00'
        }
    },
    'uncleared': {
        'horizontalAlignment': 'CENTER'
    }
}

HEADER_FORMAT = {
    "textFormat": {"bold": True},
    "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
    "horizontalAlignment": "CENTER"
}


# ============================================================================
# Keyring Configuration
# ============================================================================

KEYRING_SERVICE_NAME = "google-keep-fetcher"
