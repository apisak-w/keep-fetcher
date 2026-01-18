import requests
import os
import sys
from config.env import ENV

class TelegramClient:
    """
    Client for sending notifications via Telegram Bot API.
    """
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.environ.get(ENV.get('TELEGRAM_BOT_TOKEN'))
        self.chat_id = chat_id or os.environ.get(ENV.get('TELEGRAM_CHAT_ID'))
        
        missing_envs = []
        if not self.bot_token:
            missing_envs.append(ENV.get('TELEGRAM_BOT_TOKEN'))
        if not self.chat_id:
            missing_envs.append(ENV.get('TELEGRAM_CHAT_ID'))
            
        if missing_envs:
            print(f"Error: Telegram environment variables not defined: {', '.join(missing_envs)}")
            sys.exit(1)
            
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, text):
        """
        Send a text message to the configured Telegram chat.
        
        Args:
            text (str): The message text to send.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.bot_token or not self.chat_id:
            print("Telegram notification skipped: Bot token or chat ID not configured.")
            return False

        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
