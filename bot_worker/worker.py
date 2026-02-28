import json
import js
import logging
from pyodide.ffi import to_js
from telegram_light import send_telegram_message
from sheets_light import SheetsLightClient
from context import BotContext

# Import command handlers
from commands.start import handle_start
from commands.expense import handle_expense
from commands.income import handle_income
from commands.report import handle_report

# Setup logging
logging.basicConfig(level=logging.INFO)

async def on_fetch(request, env, ctx):
    """
    Cloudflare Worker entry point - Lightweight Webhook Version.
    """
    if request.method != "POST":
        return js.Response.new("Method Not Allowed", js.Object.fromEntries(to_js({"status": 405})))

    try:
        # Use .to_py() to convert the JavaScript proxy object to a Python dict
        data = (await request.json()).to_py()
        
        # print(f"Incoming Webhook Data: {json.dumps(data)}")
            
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        # print(f"Message text: {text}, Chat ID: {chat_id}")
        
        if not chat_id:
            return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

        token = getattr(env, "TELEGRAM_BOT_TOKEN", None)
        sheets_json = getattr(env, "GOOGLE_SERVICE_ACCOUNT_JSON", None)
        sheet_id = getattr(env, "GOOGLE_SHEET_ID", None)

        if not all([token, sheets_json, sheet_id]):
            print("Missing environment variables!")
            return js.Response.new("Internal Config Error", js.Object.fromEntries(to_js({"status": 500})))

        sheets_client = SheetsLightClient(sheets_json, sheet_id)
        bot_ctx = BotContext(token, chat_id, sheets_client)

        # Basic Router
        if text.startswith("/start"):
            await handle_start(bot_ctx)

        # elif text.startswith("/expense"):
        #     await handle_expense(bot_ctx, text)
        # 
        # elif text.startswith("/income"):
        #     await handle_income(bot_ctx, text)

        elif text.startswith("/report"):
            await handle_report(bot_ctx, text)

        return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

    except Exception as e:
        # Important: Return 200 OK to Telegram even on error to stop retries.
        # Errors should be debugged via Cloudflare Workers logs.
        print(f"Error handling request: {e}")
        return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))
