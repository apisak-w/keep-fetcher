import json
import js
import re
from pyodide.ffi import to_js

def escape_markdown_v2(text):
    """
    Escape special characters for Telegram MarkdownV2.
    Characters: _ * [ ] ( ) ~ ` > # + - = | { } . ! \
    """
    # Note: \ itself must be escaped first if it's in the text, 
    # but here we are using it as the escape character.
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def send_telegram_message(token, chat_id, text, reply_markup=None, parse_mode='Markdown', protect_content=False):
    """
    Send a message via Telegram Bot API using the Cloudflare fetch API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'protect_content': protect_content
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

async def delete_telegram_message(token, chat_id, message_id):
    """
    Delete a message via Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{token}/deleteMessage"
    
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    
    options = js.Object.fromEntries(to_js({
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(payload)
    }))
    
    try:
        response = await js.fetch(url, options)
        res_json = (await response.json()).to_py()
        print(f"Telegram Delete Response: {json.dumps(res_json)}")
        return res_json
    except Exception as e:
        print(f"Error deleting message: {e}")
        return None
