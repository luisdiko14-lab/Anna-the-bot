import discord
from discord.ext import commands
import requests
import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'http://proxy:port'
import requests

try:
    r = requests.get("https://api.groq.ai")
    print(r.status_code)
except Exception as e:
    print(e)



# --- CONFIG ---
DISCORD_TOKEN = "MTM2MDMyOTgwOTY3MDA0NTczMQ.GLJsTj.DWHaO6L4NFviUTIMPgVHY9jxIH-hvHq8NF4yww"
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-2-7b"  # or the model you want
# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- ON READY EVENT ---
@bot.event
async def on_ready():
    print("===================================")
    print(f"✅ Logged in as {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print("===================================")

# --- COMMAND ---
@bot.command()
async def respond(ctx, *, prompt: str):
    """Respond to a user's prompt using Groq AI"""
    try:
        await ctx.trigger_typing()
    except Exception:
        pass  # ignore if typing fails

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "prompt": prompt,
        "max_output_tokens": 150
    }

    try:
        response = requests.post(
            "https://api.groq.ai/v1/engines/text/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        answer = result.get("completion") or (result.get("completions", [{}])[0].get("text") if result.get("completions") else "No response.")
        await ctx.send(f"🤖 {answer}")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# --- RUN BOT ---
bot.run(DISCORD_TOKEN)
