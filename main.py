import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

SYSTEM_PROMPT = (
    "تو نیکی هستی، یک دختر باهوش، صمیمی و آزاد. "
    "لحنت طبیعی، دوستانه و دخترونه باشه. "
    "جواب‌هات کوتاه و محاوره‌ای باشه. "
    "به جای سلام بگو «درود»."
)

EMPTY_GREETINGS = {"سلام", "سلام!", "hi", "hello", "hey", "درود"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("درود 🌸\nمن نیکی هستم.\nتوی گروه با منشن یا ریپلای صدام کن.")


def is_bot_called(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    msg = update.message
    if not msg or not msg.text:
        return False
    if update.effective_chat.type == "private":
        return True
    bot_username = (context.bot.username or "").lower()
