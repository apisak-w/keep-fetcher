# Keep Expense Manager

A Python tool to manage your expenses via Google Keep and Telegram, synced to Google Sheets.

## Project Structure

- `fetcher/`: Logic to fetch and sync notes from Google Keep.
- `bot/`: Telegram bot to record income/expenses and view reports.
- `shared/`: Shared configuration and reusable libraries (Keep, Sheets, etc.).

## Features

- **Google Keep Sync**: Fetches expense notes from Google Keep and uploads them to Google Sheets.
- **Telegram Bot**:
  - Record expenses: `/expense <amount> <description> [category]`
  - Record income: `/income <amount> <description>`
  - View reports: `/report` (Monthly summary by category)
- **Shared Google Sheets Backend**: Both fetcher and bot update the same Google Sheet.

## Installation

1. **Clone the repository** and navigate to the project directory.
2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Google Keep Fetcher

Sync your Google Keep notes to Google Sheets:

```bash
python3 -m fetcher.main
```

Then process and upload:

```bash
python3 -m fetcher.expense_processor
python3 -m fetcher.sheets_uploader
```

### Telegram Bot

Start the bot:

```bash
python3 -m bot.main
```

## Configuration

Set the following environment variables:

- `GOOGLE_ACCOUNT_EMAIL`: Your Google account email.
- `GOOGLE_OAUTH_TOKEN`: OAuth token for Google Keep (see fetcher docs).
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Service account JSON for Google Sheets.
- `GOOGLE_SHEET_ID`: Target Google Sheet ID.
- `TELEGRAM_BOT_TOKEN`: Token from @BotFather.

## GitHub Actions

Automated sync is supported via GitHub Actions. See `.github/workflows/` for details.
