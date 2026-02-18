import discord
from discord.ext import commands
import time
import platform

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        text = str(timedelta(seconds=difference))
        await ctx.send(f"Uptime: {text}")

async def setup(bot):
    await bot.add_cog(Utilities(bot))
