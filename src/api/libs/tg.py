import requests
import os

class TelegramBot:
    """
    Simple Telegram Bot client using the official Bot API.

    Example:
        bot = TelegramBot(bot_token="123456:ABCDEF...")
        bot.send_message(chat_id="987654321", text="Hello world!")
    """

    def __init__(self, bot_token: str) -> None:
        """
        Initialize the bot client.

        Args:
            bot_token: Telegram bot token obtained from @BotFather.
        """
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, chat_id: str, text: str, parse_mode: str | None = None) -> bool:
        """
        Send a plain-text message to a specific chat.

        Args:
            chat_id: Numeric chat ID or username (e.g. '@channelname').
            text: Message content.
            parse_mode: Optional. 'Markdown' or 'HTML' for rich text.

        Returns:
            True if message was sent successfully, False otherwise.
        """
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode

        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            return bool(data.get("ok"))
        except requests.RequestException as e:
            print(f"Error sending message: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = "194219638"
    bot = TelegramBot(BOT_TOKEN)
    ok = bot.send_message(CHAT_ID, "Hello from Python class example")
    print("Sent:", ok)
