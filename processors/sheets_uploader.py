import os
import sys
import json
import gspread
import pandas as pd
from config.constants import EXPENSES_PROCESSED_CSV, COLUMN_FORMATS
from config.env import ENV


# ============================================================================
# Authentication Functions
# ============================================================================

def get_credentials():
    """
    Get Google Service Account credentials from environment.
    
    Returns:
        dict: Service account credentials
        
    Raises:
        SystemExit: If credentials are not found
    """
    service_account_json = os.environ.get(ENV['GOOGLE_SERVICE_ACCOUNT_JSON'])
    
    if not service_account_json:
        print(f"Error: {ENV['GOOGLE_SERVICE_ACCOUNT_JSON']} environment variable not set.")
        sys.exit(1)
    
    try:
        return json.loads(service_account_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing service account JSON: {e}")
        sys.exit(1)


def get_sheet_id():
    """
    Get Google Sheet ID from environment.
    
    Returns:
        str: Google Sheet ID
        
    Raises:
        SystemExit: If sheet ID is not found
    """
    sheet_id = os.environ.get(ENV['GOOGLE_SHEET_ID'])
    
    if not sheet_id:
        print(f"Error: {ENV['GOOGLE_SHEET_ID']} environment variable not set.")
        sys.exit(1)
    
    return sheet_id


def authenticate_gspread(credentials):
    """
    Authenticate with Google Sheets API.
    
    Args:
        credentials: Service account credentials dict
        
    Returns:
        gspread.Client: Authenticated gspread client
        
    Raises:
        SystemExit: If authentication fails
    """
    print("Authenticating with Google Sheets...")
    try:
        return gspread.service_account_from_dict(credentials)
    except Exception as e:
        print(f"Error authenticating: {e}")
        sys.exit(1)


# ============================================================================
# Sheet Operations
# ============================================================================

def open_worksheet(client, sheet_id):
    """
    Open the first worksheet of a Google Sheet.
    
    Args:
        client: Authenticated gspread client
        sheet_id: Google Sheet ID
        
    Returns:
        gspread.Worksheet: The first worksheet
        
    Raises:
        SystemExit: If sheet cannot be opened
    """
    print(f"Opening sheet with ID: {sheet_id}")
    try:
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.sheet1
    except Exception as e:
        print(f"Error opening sheet: {e}")
        sys.exit(1)


def load_csv_data(csv_file):
    """
    Load data from CSV file.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        pd.DataFrame: Loaded data
        
    Raises:
        SystemExit: If file cannot be read
    """
    print(f"Reading data from {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
        # Replace NaN with empty string for Sheets compatibility
        return df.fillna('')
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
        sys.exit(1)


def apply_column_formatting(worksheet, df):
    """
    Apply formatting to specific columns in the worksheet.
    
    Args:
        worksheet: gspread worksheet to format
        df: DataFrame with the data (used to determine column positions and row count)
    """
    if len(df) == 0:
        return
    
    for col_name, format_spec in COLUMN_FORMATS.items():
        if col_name in df.columns:
            print(f"Formatting '{col_name}' column...")
            col_index = df.columns.tolist().index(col_name)
            col_letter = chr(65 + col_index)  # A=65 in ASCII
            cell_range = f"{col_letter}2:{col_letter}{len(df) + 1}"
            
            try:
                worksheet.format(cell_range, format_spec)
            except Exception as e:
                print(f"Warning: Could not format column '{col_name}': {e}")


def update_worksheet(worksheet, df):
    """
    Update worksheet with DataFrame contents.
    
    Args:
        worksheet: gspread worksheet to update
        df: DataFrame with data to upload
        
    Raises:
        SystemExit: If update fails
    """
    print("Clearing existing data...")
    worksheet.clear()
    
    print("Updating sheet with new data...")
    try:
        # Convert DataFrame to list of lists (header + rows)
        data = [df.columns.values.tolist()] + df.values.tolist()
        worksheet.update(data)
        
        # Apply column formatting
        apply_column_formatting(worksheet, df)
        
        print("Sheet updated successfully!")
    except Exception as e:
        print(f"Error updating sheet: {e}")
        sys.exit(1)


# ============================================================================
# Main Function
# ============================================================================

def upload_to_sheets(csv_file=EXPENSES_PROCESSED_CSV):
    """
    Upload CSV data to Google Sheets.
    
    Args:
        csv_file: Path to CSV file to upload
    """
    # Get credentials and sheet ID
    credentials = get_credentials()
    sheet_id = get_sheet_id()
    
    # Authenticate and open worksheet
    client = authenticate_gspread(credentials)
    worksheet = open_worksheet(client, sheet_id)
    
    # Load and upload data
    df = load_csv_data(csv_file)
    update_worksheet(worksheet, df)


if __name__ == "__main__":
    upload_to_sheets()
