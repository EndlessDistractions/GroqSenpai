import discord
import os
import requests
from dotenv import load_dotenv
from memory import update_user_memory, get_user_context, clear_user_memory
from utils import trim_history

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

def ask_groq(prompt, user_id, api_key):
    context = trim_history(get_user_context(user_id))
    messages = context + [{"role": "user", "content": prompt}]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        data = response.json()
        if "choices" in data and data["choices"]:
            reply = data["choices"][0]["message"]["content"]
            update_user_memory(user_id, {"role": "user", "content": prompt})
            update_user_memory(user_id, {"role": "assistant", "content": reply})
            return reply
        elif "error" in data:
            return f"Groq API error: {data['error'].get('message', 'Unknown error')}"
        else:
            return "Unexpected Groq response."
    except Exception as e:
        return f"Request failed: {e}"

@bot.event
async def on_ready():
    print(f"Bot is live as {bot.user}")
    await tree.sync()
    print("Slash commands synced.")

@tree.command(name="ask", description="Ask Groq something with memory")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    user_id = str(interaction.user.id)
    answer = ask_groq(prompt, user_id, GROQ_API_KEY)
    await interaction.followup.send(answer)

@tree.command(name="forget", description="Forget conversation history")
async def forget(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    clear_user_memory(user_id)
    await interaction.followup.send("Your memory has been cleared")

bot.run(DISCORD_TOKEN)
