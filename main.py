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

# ---------- لاگ‌گیری ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

# ---------- متغیرهای محیطی ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN تنظیم نشده!")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY تنظیم نشده!")

# ---------- کلاینت Groq ----------
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


# ---------- دستور /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "درود 🌸\n"
        "من نیکی هستم.\n\n"
        "توی گروه فقط وقتی صدام کنی یا بهم ریپلای کنی جواب می‌دم."
    )


# ---------- تشخیص اینکه بات صدا زده شده یا نه ----------
def is_bot_called(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.message
    if not message or not message.text:
        return False

    # در چت خصوصی همیشه جواب بده
    if update.effective_chat.type == "private":
        return True

    bot_username = (context.bot.username or "").lower()
    text = message.text.lower()

    # منشن با @
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = text[entity.offset: entity.offset + entity.length]
                if bot_username and bot_username in mention:
                    return True

    # ریپلای روی پیام بات
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == context.bot.id:
            return True

    return False


# ---------- پاک کردن منشن از متن ----------
def clean_text(text: str, bot_username: str) -> str:
    if bot_username:
        text = text.replace(f"@{bot_username}", "")
        text = text.replace(f"@{bot_username.lower()}", "")
    return text.strip()


# ---------- پاسخ به پیام‌ها ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    # از پیام‌های خود بات صرف‌نظر کن
    if update.effective_user and update.effective_user.id == context.bot.id:
        return

    if not is_bot_called(update, context):
        return

    bot_username = context.bot.username or ""
    text = clean_text(update.message.text.strip(), bot_username)

    # پیام خالی بعد از پاک کردن منشن
    if not text:
        return

    # توی گروه، سلام خشک و خالی رو نادیده بگیر
    if update.effective_chat.type != "private" and text.lower() in EMPTY_GREETINGS:
        return

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
