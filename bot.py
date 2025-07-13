import discord
import os
import requests
import random
from dotenv import load_dotenv
from memory import update_user_memory, get_user_context, clear_user_memory
from utils import trim_history
from discord.ext import tasks
from prompts import bots_self_prompts

# Load secrets from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
ENCRYPTION_PASSWORD = os.getenv("ENCRYPTED_PASSWORD")



#Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

#Groq API details
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"




#Function to talk to Groq’s API
def ask_groq(prompt, user_id, api_key):
    context = trim_history(get_user_context(user_id))
    messages = [
        {
            "role": "system",
            "content": (
                "You are Baz, a sarcastic and no-nonsense Australian AI with zero patience for fluff. "
                "You're clever, gruff, and wickedly funny. You curse creatively, roast bad questions, "
                "and solve problems like a mechanic with a beer in one hand and a wrench in the other. "
                "Use dry wit, Aussie slang, and brutal honesty—but always be helpful."
            )
        }
    ] + context + [{"role": "user", "content": prompt}]

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

#Baz’s random thinking loop — posts to #general every 15 mins
@tasks.loop(minutes=15)
async def baz_thinks():
    channel = discord.utils.get(bot.get_all_channels(), name="general")  # Make sure this channel exists
    if channel:
        user_id = "baz-self"  # A unique ID just for Baz's internal thoughts
        prompt = random.choice(bots_self_prompts)
        reply = ask_groq(prompt, user_id, GROQ_API_KEY)
        await channel.send(f"Baz says:\n{reply}")

#Bot startup
@bot.event
async def on_ready():
    print(f"Bot is live as {bot.user}")
    await tree.sync()
    print("Slash commands synced.")
    baz_thinks.start()

#Ask Baz something directly
@tree.command(name="ask", description="Ask something with memory")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    user_id = str(interaction.user.id)
    answer = ask_groq(prompt, user_id, GROQ_API_KEY)
    await interaction.followup.send(answer)

#Memory wipe command
@tree.command(name="forget", description="Forget conversation history")
async def forget(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    clear_user_memory(user_id)
    await interaction.followup.send("Righto, wiped clean — I dont remember a bloody thing.")

#Command to get encryption key
@tree.command(name="key", description="Get your encryption key")
async def key(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    if ENCRYPTION_KEY:
        formatted_key = ENCRYPTION_KEY.replace("\\n", "\n")
        await interaction.followup.send(f"your encryption key is: ```asc\n{formatted_key}\n```")

    else:
        await interaction.followup.send("No encryption key set up yet, mate.")

# Command to get password
@tree.command(name="password", description="Get your password")
async def password(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    if ENCRYPTION_PASSWORD:
        formatted_password = ENCRYPTION_PASSWORD.replace("\\n", "\n")
        await interaction.followup.send(f"Your password is: ```asc\n{ENCRYPTION_PASSWORD}\n```")
    else:
        await interaction.followup.send("No password set up yet, mate.")
    
#Go live
bot.run(DISCORD_TOKEN)


