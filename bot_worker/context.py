from telegram_light import send_telegram_message, delete_telegram_message

class BotContext:
    """
    Shared context for bot commands.
    Encapsulates dependencies like the bot token, chat ID, and sheets client.
    """
    def __init__(self, token, chat_id, sheets_client=None):
        self.token = token
        self.chat_id = chat_id
        self.sheets_client = sheets_client

    async def reply(self, text, parse_mode='Markdown', protect_content=False):
        """Helper to send a message back to the current chat."""
        return await send_telegram_message(self.token, self.chat_id, text, parse_mode=parse_mode, protect_content=protect_content)

    async def delete_message(self, message_id):
        """Helper to delete a message in the current chat."""
        return await delete_telegram_message(self.token, self.chat_id, message_id)
