import requests
import os

url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/setWebhook"

payload = {
    "url": "https://chaineye.io/api/tg",
}
headers = {
    "accept": "application/json",
    "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(url)
print(response.text)
