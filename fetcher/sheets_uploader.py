import os
import sys
import pandas as pd
from shared.libs.sheets_client import SheetsClient
from shared.config.constants import EXPENSES_PROCESSED_CSV

def upload_to_sheets(csv_file=EXPENSES_PROCESSED_CSV):
    """
    Upload CSV data to Google Sheets using the shared SheetsClient.
    
    Args:
        csv_file: Path to CSV file to upload
    """
    print(f"Reading data from {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
        sys.exit(1)

    client = SheetsClient()
    client.upload_df(df)

if __name__ == "__main__":
    upload_to_sheets()
