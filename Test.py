import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def set_bot_avatar():
    """Set the bot's avatar from file."""
    try:
        with open("avatar_with_drawn_emojis.gif", "rb") as f:
            await bot.user.edit(avatar=f.read())
        print("✅ Bot avatar set successfully on startup!")
    except FileNotFoundError:
        print("❌ File `avatar_with_drawn_emojis.gif` not found.")
    except discord.HTTPException as e:
        print(f"❌ Failed to set bot avatar: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await set_bot_avatar()

@bot.command()
@commands.has_permissions(administrator=True)
async def changepfp(ctx):
    """Change the bot's profile picture (admin only)."""
    await set_bot_avatar()
    await ctx.send("✅ Bot profile picture updated!")

bot.run("process.env.DISCORD_TOKEN")
