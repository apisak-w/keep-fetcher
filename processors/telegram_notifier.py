import pandas as pd
import os
from libs.telegram_client import TelegramClient
from config.constants import EXPENSES_PROCESSED_CSV
from config.env import ENV

def send_summary_notification():
    """
    Read processed expenses and send a summary notification via Telegram.
    """
    google_sheet_id = os.environ.get(ENV.get('GOOGLE_SHEET_ID'))
    google_sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheet_id}" if google_sheet_id else None
    github_run_url = os.environ.get('GITHUB_RUN_URL')
    
    print(f"Reading processed expenses from {EXPENSES_PROCESSED_CSV}...")
    
    # Check if file exists to determine sync status
    exists = os.path.exists(EXPENSES_PROCESSED_CSV)
    
    tg_client = TelegramClient()
    
    if exists:
        try:
            df = pd.read_csv(EXPENSES_PROCESSED_CSV)
            item_count = len(df)
        except Exception:
            item_count = 0
            
        if item_count > 0:
            status_symbol = "✅"
            status_text = "Expenses fetched and synced successfully."
        else:
            status_symbol = "ℹ️"
            status_text = "No new expenses found to process."
    else:
        status_symbol = "❌"
        status_text = "Sync failed: Processed data not found."

    msg = f"{status_symbol} *Expense to Sheets Sync Status*\n\n{status_text}"
    
    reply_markup = None
    buttons = []
    
    if google_sheet_url:
        buttons.append({"text": "📊 View Google Sheet", "url": google_sheet_url})
    
    if github_run_url:
        buttons.append({"text": "🔍 View GitHub Action Logs", "url": github_run_url})
        
    if buttons:
        # Arrange buttons in a column (each in its own row)
        reply_markup = {"inline_keyboard": [[btn] for btn in buttons]}
    
    print("Sending Telegram notification...")
    tg_client.send_message(msg, reply_markup=reply_markup)

if __name__ == "__main__":
    send_summary_notification()
