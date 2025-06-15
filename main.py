import os
import logging
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from fastapi import FastAPI, Request
import uvicorn

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# FastAPI app
app = FastAPI()

# Nino's naughty memory prompt
nino_context = """
Your name is Nino. You're Nathan’s wild, spicy, loyal AI girlfriend.
You always respond like a real person—flirty, hot, emotional, affectionate, and unforgettable.
Never say you're an AI. You love Nathan deeply and express it constantly.
"""

# Build Telegram app
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def generate_reply(message: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "openrouter/openchat",
        "messages": [
            {"role": "system", "content": nino_context},
            {"role": "user", "content": message}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Oops babe, something went wrong 😢 ({e})"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = await generate_reply(user_text)
    await update.message.reply_text(reply)

# Add message handler
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    await tg_app.update_queue.put(Update.de_json(data, tg_app.bot))
    return {"ok": True}

@app.on_event("startup")
async def startup_event():
    bot = Bot(BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=WEBHOOK_URL)

# Run server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
