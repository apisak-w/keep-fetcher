# Google Keep Fetcher

A Python CLI tool to fetch your Google Keep notes and export them to a Pandas DataFrame and CSV file. This tool uses the unofficial `gkeepapi` library.

## Features

-   Fetches all notes from Google Keep.
-   Supports multiple authentication methods to bypass "BadAuthentication" errors.
-   Exports data to a Pandas DataFrame.
-   Saves notes to `keep_notes.csv`.
-   Extracts note metadata: Title, Text, Created/Updated timestamps, Labels, Archived/Trashed status, and URL.

## Prerequisites

-   Python 3.7+
-   A Google Account

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main script:

```bash
./venv/bin/python3 main.py
```

### Authentication

When you run the script, you will be prompted to enter your Google email. Then, you will be presented with three authentication options:

1.  **App Password**: Try this first if you have an App Password generated. Note that this often fails with `BadAuthentication` due to Google's security checks.
2.  **Master Token**: If you already have a master token (starting with `aas_et/`), you can enter it here.
3.  **OAuth Token (Recommended)**: Use this "Alternative Flow" if option #1 fails.
    -   Open `https://accounts.google.com/EmbeddedSetup` in your browser (Incognito mode recommended).
    -   Log in to your Google Account.
    -   Open Developer Tools (F12 or Right-click -> Inspect).
    -   Go to the **Application** tab (or **Storage** tab in Firefox) -> **Cookies**.
    -   Find the cookie named `oauth_token`.
    -   Copy its value and paste it into the terminal when prompted.

**Note**: After a successful login, the master token is securely stored in your system's keyring, so you won't need to re-authenticate every time.

## Output

The script will:
1.  Print the first 5 notes to the console.
2.  Save all notes to `outputs/keep_notes.csv`.

## Expense Processor

If you use Google Keep to track expenses (e.g., notes titled "November 22th, 2025" with items like "☐ Food 150"), you can use the expense processor to extract this data.

```bash
./venv/bin/python3 processors/expense_processor.py
```

This will:
1.  Read `outputs/keep_notes.csv`.
2.  Filter for notes with the "expense" label.
3.  Parse the date from the note title.
4.  Extract unchecked items (starting with `☐`) from the text. Checked items (`☑`) are ignored.
5.  Automatically categorize expenses (Food, Transport, Utilities, etc.) based on keywords.
6.  Save the structured data to `outputs/expenses_processed.csv` with columns: `date`, `category`, `description`, `amount`, `uncleared`.

## GitHub Actions & Google Sheets

You can automate the fetching and processing using the included GitHub Action workflow.

### Prerequisites
1.  **Google Service Account**:
    -   Create a Service Account in Google Cloud Console.
    -   Enable the **Google Sheets API**.
    -   Download the JSON key file.
    -   Share your target Google Sheet with the Service Account's email address.
2.  **GitHub Secrets**:
    -   Go to your repository Settings -> Secrets and variables -> Actions.
    -   Add `GOOGLE_ACCOUNT_EMAIL`: Your Google Account email address.
    -   Add `GOOGLE_OAUTH_TOKEN`: Your Google OAuth Token (from the `oauth_token` cookie).
        -   To get this:
            1.  Open `https://accounts.google.com/EmbeddedSetup` in Incognito.
            2.  Log in.
            3.  Open DevTools -> Application -> Cookies.
            4.  Copy the value of `oauth_token`.
    -   Add `GOOGLE_SERVICE_ACCOUNT_JSON`: The content of your Service Account JSON key file.
    -   Add `GOOGLE_SHEET_ID`: The ID of your target Google Sheet (found in the URL).

### Triggering the Workflow
1.  Go to the **Actions** tab in your repository.
2.  Select **Manual Keep Fetcher**.
3.  Click **Run workflow**.
4.  The workflow will fetch notes, process expenses, and update your Google Sheet.

## Disclaimer

This project uses `gkeepapi`, which is an unofficial client for the Google Keep API. It is not supported by Google and may break if Google changes their internal API. Use at your own risk.
