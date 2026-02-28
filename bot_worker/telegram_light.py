import json
import js

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
        
    response = await js.fetch(url, method="POST", headers={
        "Content-Type": "application/json"
    }, body=json.dumps(payload))
    
    return await response.json()
