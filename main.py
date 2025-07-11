import discord
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Discord client setup with message intent
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

# Groq API setup
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

def ask_groq(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        data = response.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"Groq API error: {data['error'].get('message', 'Unknown error')}"
        else:
            return f"Unexpected response: {data}"
    except Exception as e:
        return f"Request failed: {e}"

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await tree.sync()
    print("Slash commands synced.")

@tree.command(name="ask", description="Ask Groq a question")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    answer = ask_groq(prompt, GROQ_API_KEY)
    await interaction.followup.send(answer)

bot.run(DISCORD_TOKEN)
