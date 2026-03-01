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

# Import DDD components
from infrastructure.kv_user_repository import KVUserRepository
from services.auth_service import AuthService

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
        user_id = message.get("from", {}).get("id")
        
        # print(f"Message text: {text}, Chat ID: {chat_id}, User ID: {user_id}")
        
        if not chat_id or not user_id:
            return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

        token = getattr(env, "TELEGRAM_BOT_TOKEN", None)
        sheets_json = getattr(env, "GOOGLE_SERVICE_ACCOUNT_JSON", None)
        default_sheet_id = getattr(env, "GOOGLE_SHEET_ID", None)
        users_kv = getattr(env, "BOT_USERS_KV", None)

        if not all([token, sheets_json, default_sheet_id]):
            print("Missing core environment variables!")
            return js.Response.new("Internal Config Error", js.Object.fromEntries(to_js({"status": 500})))

        # Access Control via AuthService (DDD)
        user_repo = KVUserRepository(users_kv)
        auth_service = AuthService(user_repo)
        user = await auth_service.authenticate(user_id)

        # Log user attempt and their authorization status
        print(f"User Attempt - ID: {user_id}, Authorized: {user.is_authorized}")

        if not user.is_authorized:
            error_msg = "🚫 You are not registered to use this bot." if not users_kv or not await users_kv.get(f"user:{user_id}") else "🚫 You are not authorized to use this bot."
            await send_telegram_message(token, chat_id, error_msg)
            return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

        # Use default sheet_id (overrides are no longer supported as per simplification)
        sheet_id = default_sheet_id

        sheets_client = SheetsLightClient(sheets_json, sheet_id)
        bot_ctx = BotContext(token, chat_id, sheets_client)

        # Basic Router
        if text.startswith("/start"):
            await handle_start(bot_ctx)

        elif text.startswith("/report"):
            await handle_report(bot_ctx, text)

        return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

    except Exception as e:
        # Important: Return 200 OK to Telegram even on error to stop retries.
        # Errors should be debugged via Cloudflare Workers logs.
        print(f"Error handling request: {e}")
        return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))
