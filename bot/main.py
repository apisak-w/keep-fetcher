import os
import sys
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from shared.config.env import ENV
from bot.handlers import start, record_expense, record_income, report

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Start the bot."""
    token = os.environ.get(ENV['TELEGRAM_BOT_TOKEN'])
    if not token:
        print(f"Error: {ENV['TELEGRAM_BOT_TOKEN']} environment variable not set.")
        sys.exit(1)

    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("expense", record_expense))
    application.add_handler(CommandHandler("income", record_income))
    application.add_handler(CommandHandler("report", report))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
