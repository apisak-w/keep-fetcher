import json
import js
import logging
from pyodide.ffi import to_js
from telegram_light import send_telegram_message
from sheets_light import SheetsLightClient
from utils import parse_record_message, format_report

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
        
        print(f"Incoming Webhook Data: {json.dumps(data)}")
            
        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        
        print(f"Message text: {text}, Chat ID: {chat_id}")
        
        if not chat_id:
            return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

        token = getattr(env, "TELEGRAM_BOT_TOKEN", None)
        sheets_json = getattr(env, "GOOGLE_SERVICE_ACCOUNT_JSON", None)
        sheet_id = getattr(env, "GOOGLE_SHEET_ID", None)

        if not all([token, sheets_json, sheet_id]):
            print("Missing environment variables!")
            return js.Response.new("Internal Config Error", js.Object.fromEntries(to_js({"status": 500})))

        sheets_client = SheetsLightClient(sheets_json, sheet_id)

        # Basic Router
        if text.startswith("/start"):
            print("Handling /start command")
            welcome = (
                "Hi! I'm your Expense Manager Bot (Lightweight Worker Edition).\n\n"
                "Commands:\n"
                "/expense <amount> <description> [category]\n"
                "/income <amount> <description>\n"
                "/report - Get current month summary"
            )
            await send_telegram_message(token, chat_id, welcome)

        elif text.startswith("/expense") or text.startswith("/income"):
            is_expense = text.startswith("/expense")
            print(f"Handling {'/expense' if is_expense else '/income'} command")
            record = parse_record_message(text, is_expense=is_expense)
            
            if not record:
                error = "Invalid format. Use: /expense <amount> <description> [category]" if is_expense else "Invalid format. Use: /income <amount> <description>"
                await send_telegram_message(token, chat_id, error)
            else:
                row = [record['date'], record['category'], record['description'], record['amount'], record['uncleared']]
                await sheets_client.append_row(row)
                status = "expense" if is_expense else "income"
                await send_telegram_message(token, chat_id, f"✅ Recorded {status}: ฿{record['amount']} for {record['description']}")

        elif text.startswith("/report"):
            print("Handling /report command")
            await send_telegram_message(token, chat_id, "Fetching report... please wait.")
            records = await sheets_client.get_all_records()
            report_text = format_report(records)
            await send_telegram_message(token, chat_id, report_text)

        return js.Response.new("OK", js.Object.fromEntries(to_js({"status": 200})))

    except Exception as e:
        # In a real worker, we might want to log this to Cloudflare Logs
        print(f"Error handling request: {e}")
        return js.Response.new(f"Internal Error: {e}", js.Object.fromEntries(to_js({"status": 500})))
