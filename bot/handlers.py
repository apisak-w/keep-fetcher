import os
from telegram import Update
from telegram.ext import ContextTypes
from shared.libs.sheets_client import SheetsClient
from bot.utils import parse_record_message, format_report

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your Expense Manager Bot. "
        f"You can record expenses/income and get reports.\n\n"
        f"Commands:\n"
        f"/expense <amount> <description> [category]\n"
        f"/income <amount> <description>\n"
        f"/report - Get current month summary"
    )

async def record_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record an expense to Google Sheets."""
    text = update.message.text
    record = parse_record_message(text, is_expense=True)
    
    if not record:
        await update.message.reply_text("Invalid format. Use: /expense <amount> <description> [category]")
        return

    client = SheetsClient()
    # Assuming columns: Date, Category, Description, Amount, Uncleared
    row = [record['date'], record['category'], record['description'], record['amount'], record['uncleared']]
    
    if client.append_row(row):
        await update.message.reply_text(f"Recorded expense: ฿{record['amount']} for {record['description']} ({record['category']})")
    else:
        await update.message.reply_text("Failed to record expense. Please try again.")

async def record_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record income to Google Sheets."""
    text = update.message.text
    record = parse_record_message(text, is_expense=False)
    
    if not record:
        await update.message.reply_text("Invalid format. Use: /income <amount> <description>")
        return

    client = SheetsClient()
    row = [record['date'], record['category'], record['description'], record['amount'], record['uncleared']]
    
    if client.append_row(row):
        await update.message.reply_text(f"Recorded income: ฿{record['amount']} for {record['description']}")
    else:
        await update.message.reply_text("Failed to record income. Please try again.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a report from Google Sheets."""
    await update.message.reply_text("Fetching report... please wait.")
    
    client = SheetsClient()
    records = client.get_all_records()
    
    report_text = format_report(records)
    await update.message.reply_markdown(report_text)
