import json
import logging
import js
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from shared.libs.sheets_client import SheetsClient
from bot.handlers import start, record_expense, record_income, report

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def on_fetch(request, env, ctx):
    """
    Cloudflare Worker entry point.
    """
    # Initialize the app with the token from environment variables
    # Cloudflare secrets are available on the 'env' object
    token = env.TELEGRAM_BOT_TOKEN
    if not token:
        return js.Response.new("TELEGRAM_BOT_TOKEN not set", status=500)

    application = ApplicationBuilder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("expense", record_expense))
    application.add_handler(CommandHandler("income", record_income))
    application.add_handler(CommandHandler("report", report))

    # Handle the request
    if request.method == "POST":
        try:
            # Parse the update from the request body
            data = await request.json()
            # Convert to dict if it's already parsed or handle raw
            if isinstance(data, str):
                data = json.loads(data)
                
            update = Update.de_json(data, application.bot)
            
            await application.initialize()
            await application.process_update(update)
            await application.shutdown()

            return js.Response.new("OK", status=200)
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            return js.Response.new(f"Error: {e}", status=500)
            
    return js.Response.new("Method Not Allowed", status=405)
