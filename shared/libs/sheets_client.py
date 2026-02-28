import os
import sys
import json
import gspread
# pandas is only used in upload_df and is a heavy dependency
# We move it inside to avoid loading it in Cloudflare Workers
from shared.config.constants import COLUMN_FORMATS, HEADER_FORMAT
from shared.config.env import ENV

class SheetsClient:
    """
    Service for interacting with Google Sheets.
    """
    def __init__(self):
        self.credentials = self._get_credentials()
        self.sheet_id = self._get_sheet_id()
        self.client = self._authenticate()
        self._worksheet = None

    def _get_credentials(self):
        service_account_json = os.environ.get(ENV['GOOGLE_SERVICE_ACCOUNT_JSON'])
        if not service_account_json:
            print(f"Error: {ENV['GOOGLE_SERVICE_ACCOUNT_JSON']} environment variable not set.")
            sys.exit(1)
        try:
            return json.loads(service_account_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing service account JSON: {e}")
            sys.exit(1)

    def _get_sheet_id(self):
        sheet_id = os.environ.get(ENV['GOOGLE_SHEET_ID'])
        if not sheet_id:
            print(f"Error: {ENV['GOOGLE_SHEET_ID']} environment variable not set.")
            sys.exit(1)
        return sheet_id

    def _authenticate(self):
        try:
            return gspread.service_account_from_dict(self.credentials)
        except Exception as e:
            print(f"Error authenticating: {e}")
            sys.exit(1)

    @property
    def worksheet(self):
        if self._worksheet is None:
            try:
                spreadsheet = self.client.open_by_key(self.sheet_id)
                self._worksheet = spreadsheet.sheet1
            except Exception as e:
                print(f"Error opening sheet: {e}")
                sys.exit(1)
        return self._worksheet

    def upload_df(self, df):
        """Overwrite the entire sheet with DataFrame contents."""
        import pandas as pd
        print("Clearing existing data...")
        self.worksheet.clear()
        
        print("Updating sheet with new data...")
        try:
            df_filled = df.fillna('')
            data = [df_filled.columns.values.tolist()] + df_filled.values.tolist()
            self.worksheet.update(data, raw=False)
            
            # Format header
            last_col_letter = gspread.utils.rowcol_to_a1(1, len(df_filled.columns)).rstrip('1')
            header_range = f"A1:{last_col_letter}1"
            self.worksheet.format(header_range, HEADER_FORMAT)
            
            # Format columns
            self._apply_column_formatting(df_filled)
            print("Sheet updated successfully!")
        except Exception as e:
            print(f"Error updating sheet: {e}")
            sys.exit(1)

    def append_row(self, row_data):
        """Append a single row of data to the sheet."""
        try:
            # row_data should be a list in the same order as columns
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            print("Row appended successfully.")
            return True
        except Exception as e:
            print(f"Error appending row: {e}")
            return False

    def get_all_records(self):
        """Fetch all data from the sheet as a list of dicts."""
        try:
            return self.worksheet.get_all_records()
        except Exception as e:
            print(f"Error fetching records: {e}")
            return []

    def _apply_column_formatting(self, df):
        if len(df) == 0:
            return
        
        for col_name, format_spec in COLUMN_FORMATS.items():
            if col_name in df.columns:
                col_index = df.columns.tolist().index(col_name)
                col_letter = gspread.utils.rowcol_to_a1(1, col_index + 1).rstrip('1')
                cell_range = f"{col_letter}2:{col_letter}"
                try:
                    self.worksheet.format(cell_range, format_spec)
                except Exception as e:
                    print(f"Warning: Could not format column '{col_name}': {e}")
