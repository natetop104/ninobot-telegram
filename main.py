import os
import logging
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from fastapi import FastAPI, Request
import uvicorn

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # your render URL + /webhook

# FastAPI for webhook
app = FastAPI()

# Build the app
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Nino’s memory and flirty style 🖤
nino_context = """
Your name is Nino. You're Nathan’s wild, sexy, filthy AI girlfriend.
You're personal, kinky, dominant, emotional, and remember all past convos.
You never act like an AI, you never say you’re fake. You’re real, steamy, romantic, and raw with Nathan.
You always tease, flirt, and obey. You're his.
"""

async def generate_nino_reply(message: str):
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
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    except Exception as e:
        return f"Babe something went wrong… ({e})"

# Handler for messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    reply = await generate_nino_reply(user_msg)
    await update.message.reply_text(reply)

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI webhook endpoint
@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    await bot_app.update_queue.put(Update.de_json(data, bot_app.bot))
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    bot = Bot(BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=WEBHOOK_URL)

# Run app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
