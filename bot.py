import discord
from discord.ext import commands, tasks
import random
import asyncio
import os
import sys
from dotenv import load_dotenv

# ==================================================
# --- CONFIGURATION & SECURITY ---
# ==================================================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_USERS = ["luisthegoat7301", "zelda_life", "blackopsmode"]

if not TOKEN:
    print("❌ ERROR: Token not found! Put DISCORD_TOKEN in .env file.")
    exit()

PREFIX = ("anna", "!")

# ==================================================
# --- SETUP ---
# ==================================================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ==================================================
# --- NATURE STATUS LOOP ---
# ==================================================

nature_scenes = [
    "Pokemon! 🌲",
    "MEW! 🌅",
    "Flowing Rivers 🌊",
    "Pikachu 🏔️",
    "Starry Nights 🌌",
    "Blooming Pokemons 🌸",
    "Falling Rain 🌧️",
    "Mew is cool! i like it",
    "Just Got verified! ✅"
]

@tasks.loop(seconds=67)
async def change_status():
    activity_name = random.choice(nature_scenes)
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name=activity_name
    )
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    print(f"🔄 Status changed to: {activity_name}")

@change_status.before_loop
async def before_status():
    await bot.wait_until_ready()

# ==================================================
# --- EVENTS ---
# ==================================================

@bot.event
async def on_ready():
    print("===================================")
    print(f"✅ Logged in as {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print("===================================")

    if not change_status.is_running():
        change_status.start()

    print("🌐 Syncing slash commands...")
    await bot.tree.sync()
    print("✅ Global slash commands synced!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.lower().startswith(('anna', '!')):
        # Process the command
        await bot.process_commands(message)

# ==================================================
# --- COMMANDS ---
# ==================================================

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🌿 Anna Help",
                          description="Nature-themed guardian bot.",
                          color=discord.Color.green())
    embed.add_field(name="Commands", value="`ping`, `help`", inline=False)
    await ctx.send(embed=embed)

# ==================================================
# --- RUN BOT ---
# ==================================================

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Critical Error: {e}")
