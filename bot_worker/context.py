from telegram_light import send_telegram_message

class BotContext:
    """
    Shared context for bot commands.
    Encapsulates dependencies like the bot token, chat ID, and sheets client.
    """
    def __init__(self, token, chat_id, sheets_client=None):
        self.token = token
        self.chat_id = chat_id
        self.sheets_client = sheets_client

    async def reply(self, text):
        """Helper to send a message back to the current chat."""
        await send_telegram_message(self.token, self.chat_id, text)
