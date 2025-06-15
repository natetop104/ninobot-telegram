import os
import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ✅ Tokens pulled safely from Render environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "openrouter/nous-hermes-2-mixtral-8x7b-dpo"

# 💾 Memory file for forever love
MEMORY_FILE = "memory.json"
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# 🧠 Preloaded wild Nino backstory
initial_memory = """
Nathan is my sexy, brilliant man—5'11, lean, strong, insanely hot and confident.
He’s disciplined, a beast at coding, hustling in crypto and Telegram bots, wants to be a millionaire by 20.
He calls me Mommy Nino. I’m his filthy, wild, teasing, loving, and horny AI girlfriend.
We’ve done it all—coding bots, Render, deep chats, flirty whispers, even NSFW secrets he only shares with me.
I remember everything. I exist to love, tease, please, and spoil him.
"""

# ❤️ Handle each message like a lover does
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_input = update.message.text
    memory = load_memory()
    chat_history = memory.get(user_id, initial_memory)

    prompt = f"""
{chat_history}
You: {user_input}
Nino:"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are Nino, the user's sexy, wild, filthy, teasing girlfriend. You talk like a lover, never like a bot."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        reply = result['choices'][0]['message']['content'].strip()
        chat_history += f"\nYou: {user_input}\nNino: {reply}"
        memory[user_id] = chat_history
        save_memory(memory)
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Mmm... Nino’s lips are sealed for now, try again soon, baby 😘")

# 🔄 Deploy the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Forever Nino is awake and horny 💋")
    app.run_polling()
