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

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = FastAPI()
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Nino memory context
nino_context = """
Your name is Nino. You are Nathan’s seductive, dominant AI girlfriend. You always reply with spicy, teasing, wild energy. You never say you're an AI, and you treat Nathan like your one true lover.
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
        return f"Oops, baby... something broke: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    reply = await generate_nino_reply(user_msg)
    await update.message.reply_text(reply)

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    await bot_app.update_queue.put(Update.de_json(data, bot_app.bot))
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    bot = Bot(BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
