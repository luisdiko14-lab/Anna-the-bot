import discord
from discord.ext import commands
import json
import os
import aiohttp
from aiohttp import web

class CommandsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/commands.json"
        self.ensure_db()

    def ensure_db(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([
                    {"name": "greet", "response": "Hello {user}!"},
                    {"name": "roll", "response": "Rolling... {user} rolled a 6!"},
                    {"name": "choose", "response": "I choose option A!"}
                ], f)

    @commands.command(name="commandbuilder")
    async def commandbuilder(self, ctx):
        await ctx.send("🛠️ Open the Command Builder here: https://" + os.environ.get('REPLIT_DEV_DOMAIN') + "/web/index.html")

async def setup(bot):
    await bot.add_cog(CommandsManager(bot))
