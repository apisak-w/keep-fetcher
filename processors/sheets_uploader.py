import gspread
import pandas as pd
import os
import sys

def upload_to_sheets(csv_file='outputs/expenses_processed.csv'):
    # 1. Get credentials from environment variable
    # The JSON key should be stored in GOOGLE_SERVICE_ACCOUNT_JSON env var
    service_account_info = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')

    if not service_account_info:
        print("Error: GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set.")
        return

    if not sheet_id:
        print("Error: GOOGLE_SHEET_ID environment variable not set.")
        return

    print("Authenticating with Google Sheets...")
    try:
        # Save the JSON content to a temporary file because gspread expects a filename or dict
        # We can pass the dict directly if we parse it, but let's try to parse it as dict first
        import json
        creds_dict = json.loads(service_account_info)
        gc = gspread.service_account_from_dict(creds_dict)
    except Exception as e:
        print(f"Error authenticating: {e}")
        return

    print(f"Opening sheet with ID: {sheet_id}")
    try:
        sh = gc.open_by_key(sheet_id)
        # Assuming we want to update the first worksheet
        worksheet = sh.sheet1 
    except Exception as e:
        print(f"Error opening sheet: {e}")
        return

    print(f"Reading data from {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
        return

    # Replace NaN with empty string for Sheets compatibility
    df = df.fillna('')

    print("Clearing existing data...")
    worksheet.clear()

    print("Updating sheet with new data...")
    # update([dataframe]) is available in recent gspread versions, 
    # but let's use a more standard list of lists approach for compatibility
    try:
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("Sheet updated successfully!")
    except Exception as e:
        print(f"Error updating sheet: {e}")

if __name__ == "__main__":
    upload_to_sheets()
