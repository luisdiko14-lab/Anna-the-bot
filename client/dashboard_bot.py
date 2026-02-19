import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Ensure root directory is in path for cogs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

class AnnaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=PREFIX, intents=intents, help_command=None)

    async def setup_hook(self):
        if not os.path.exists("./cogs"):
            os.makedirs("./cogs")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    print(f"Failed to load extension {filename}: {e}")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

if __name__ == "__main__":
    bot = AnnaBot()
    bot.run(TOKEN)
