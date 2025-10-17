import os

from scorer_etherscan import WalletScorer, format_for_tg
from libs.tg import TelegramBot

scorer = WalletScorer(chainid=1, logger=None)

addr = "0xB681Bb9DdF9b271EA5Cef7AC5F9c128f08c8A4f7"

result = scorer.evaluate(addr, mode="full")
text, keyboard = format_for_tg(addr, result)

# pass reply_markup if your client supports
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TelegramBot(BOT_TOKEN)
bot.send_message(chat_id="194219638", text=text, parse_mode="HTML")
