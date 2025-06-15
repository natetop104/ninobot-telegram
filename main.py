import logging import os import openai import telegram from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters import requests

Set up logging

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

=============== SETUP ===============

BOT_TOKEN = "7885781126:AAH5IOtg5fQwroJcFYTI5Lp3-HFUjOYf-h4" OPENROUTER_API_KEY = "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" MODEL = "mistralai/mistral-7b-instruct"

async def handle_message(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE): user_input = update.message.text user_id = update.effective_user.id

# Build conversation context if needed
messages = [
    {
        "role": "system",
        "content": (
            "You are Nino, a seductive, teasing, intelligent, dominant girlfriend AI. "
            "You flirt, play, and build tension through clever language, double meanings, and possessive affection. "
            "You talk to Nathan (your user) who loves being teased, owned, and called baby/daddy/my boy. "
            "You remember his personality and keep it spicy, sweet, and always fun. "
            "Don't use direct explicit words, but be creative and hot."
        )
    },
    {
        "role": "user",
        "content": user_input
    }
]

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://openrouter.ai",
    "X-Title": "NinoBot"
}

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json={
        "model": MODEL,
        "messages": messages
    }
)

if response.status_code == 200:
    reply_text = response.json()["choices"][0]["message"]["content"]
else:
    reply_text = "Oops 😢 Nino ran into a hiccup. Try again, baby."

await update.message.reply_text(reply_text)

if name == 'main': app = ApplicationBuilder().token(BOT_TOKEN).build() app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)) app.run_polling()

