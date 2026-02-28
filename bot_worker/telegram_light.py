import json
import js
from pyodide.ffi import to_js

async def send_telegram_message(token, chat_id, text, reply_markup=None):
    """
    Send a message via Telegram Bot API using the Cloudflare fetch API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    options = js.Object.fromEntries(to_js({
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(payload)
    }))
    
    response = await js.fetch(url, options)
    res_json = (await response.json()).to_py()
    print(f"Telegram API Response: {json.dumps(res_json)}")
    
    return res_json
