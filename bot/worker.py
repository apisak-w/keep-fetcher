import json
import logging
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
    token = env.TELEGRAM_BOT_TOKEN
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
            update = Update.de_json(data, application.bot)
            
            # Process the update
            # Note: In a real worker environment, we initialize the app per request
            # and process the update directly.
            await application.initialize()
            await application.process_update(update)
            await application.shutdown()

            return Response.new("OK", status=200)
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            return Response.new(f"Error: {e}", status=500)
            
    return Response.new("Method Not Allowed", status=405)

# Cloudflare Workers Python entry point
class Response:
    """Helper to match Cloudflare's Response object."""
    @staticmethod
    def new(body, status=200, headers=None):
        import js
        return js.Response.new(body, status=status, headers=headers)
