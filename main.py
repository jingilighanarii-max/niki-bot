import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN تنظیم نشده!")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY تنظیم نشده!")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = (
    "تو نیکی هستی، یک دختر باهوش، صمیمی و آزاد. "
    "می‌تونی در مورد هر موضوعی حرف بزنی. "
    "لحنت طبیعی، دوستانه و دخترونه باشه. "
    "جواب‌هات کوتاه و محاوره‌ای باشه، مثل چت واقعی. "
    "هر وقت خواستی احوالپرسی کنی بگو «درود» به جای سلام."
)

EMPTY_GREETINGS = {
    "سلام", "سلام!", "سلام؟", "سلام.", "hi", "hello", "hey",
    "salam", "درود", "درود!", "درود.",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "درود 🌸\n"
        "من نیکی هستم.\n\n"
        "توی گروه فقط وقتی صدام کنی یا بهم ریپلای کنی جواب می‌دم."
    )


def is_bot_called(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.message
    if not message or not message.text:
        return False

    if update.effective_chat.type == "private":
        return True

    bot_username = (context.bot.username or "").lower()
    text = message.text.lower()

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = text[entity.offset: entity.offset + entity.length]
                if bot_username and bot_username in mention:
                    return True

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == context.bot.id:
            return True

    return False


def clean_text(text: str, bot_username: str) -> str:
    if bot_username:
        text = text.replace(f"@{bot_username}", "")
        text = text.replace(f"@{bot_username.lower()}", "")
    return text.strip()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.effective_user and update.effective_user.id == context.bot.id:
        return

    if not is_bot_called(update, context):
        return

    bot_username = context.bot.username or ""
