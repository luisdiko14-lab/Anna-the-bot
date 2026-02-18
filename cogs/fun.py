import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        jokes = ["Why did the chicken cross the road? To get to the other side!", "What do you call a fake noodle? An impasta!"]
        await ctx.send(random.choice(jokes))

    @commands.command()
    async def roll(self, ctx, dice: str = "1d6"):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be NdN!')
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(Fun(bot))
