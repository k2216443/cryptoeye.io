import asyncio
import html
import logging
import os
from dataclasses import dataclass
from http import HTTPStatus

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from telegram import ForceReply, Update
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # full URL, e.g. https://bot.example.com/webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str

class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Just paste any ERC20 address and we will evaluate it's security score",
        reply_markup=ForceReply(selective=True),
    )

async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(chat_id=194219638, text=text, parse_mode=ParseMode.HTML)


def main() -> None:
    """Set up PTB application and a web application for handling the incoming requests."""
    print("ok0", flush=True)
    context_types = ContextTypes(context=CustomContext)
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (
        Application.builder().token(BOT_TOKEN).updater(None).context_types(context_types).build()
    )

    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    application.bot.set_webhook(url="https://chaineye.io/t", allowed_updates=Update.ALL_TYPES)

    print("ok", flush=True)

# {"ok":true,"result":[{"update_id":770153174,
# "message":{"message_id":3,"from":{"id":194219638,"is_bot":false,"first_name":"Konstantin","last_name":"Ivanov","username":"debugger00","language_code":"en"},"chat":{"id":194219638,"first_name":"Konstantin","last_name":"Ivanov","username":"debugger00","type":"private"},"date":1760624685,"text":"Test"}}]}