import discord
from discord.ext import commands
import asyncio
import os

# ==========================================
# 🔧 CONFIGURATION SECTION (Edit this!)
# ==========================================

# Format: "Category Name": { "text": ["emoji-name"], "voice": ["Emoji | Name"] }
SERVER_STRUCTURE = {
    "📌 | Server Information": {
        "text": [
            "📢-announcements",
            "📜-rules",
            "👋-welcome",
            "ℹ️-info"
        ],
        "voice": [] # No voice channels in info
    },
    "💬 | Community Hub": {
        "text": [
            "💬-general",
            "🐸-memes",
            "🤖-bot-commands",
            "📸-media"
        ],
        "voice": [
            "☕ | Lounge",
            "🔊 | Hangout",
            "🎵 | Music",
            "💤 | AFK"
        ]
    },
    "🎮 | Gaming Center": {
        "text": [
            "🎮-gaming-chat",
            "🤝-lfg",         # Looking For Group
            "🎬-clips"
        ],
        "voice": [
            "🎮 | Main Lobby",
            "🔫 | FPS Squad",
            "⚔️ | MOBA Team",
            "⛏️ | Minecraft",
            "🎲 | Among Us",
            "🏆 | Ranked"
        ]
    }
}

# Roles: (Name, Color, Permissions)
ROLES_CONFIG = [
    ("👑 Owner", discord.Color.from_rgb(255, 0, 0), discord.Permissions(administrator=True)),
    ("🛡️ Admin", discord.Color.from_rgb(200, 50, 50), discord.Permissions(administrator=True)),
    ("🔨 Moderator", discord.Color.from_rgb(255, 165, 0), discord.Permissions(manage_messages=True, kick_members=True)),
    ("🎮 Gamer", discord.Color.purple(), discord.Permissions(send_messages=True)),
    ("💎 VIP", discord.Color.gold(), discord.Permissions(send_messages=True)),
    ("👤 Member", discord.Color.blue(), discord.Permissions(send_messages=True)),
    ("🤖 Bots", discord.Color.dark_grey(), discord.Permissions(send_messages=True)),
]

# ==========================================
# 🤖 BOT CODE
# ==========================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

class ConfirmSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Build Server", style=discord.ButtonStyle.success, emoji="🏗️")
    async def build_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Permission & Safety Checks
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        me = guild.me

        if not me.guild_permissions.manage_channels or not me.guild_permissions.manage_roles:
            await interaction.followup.send("❌ **Error:** I need `Manage Channels` and `Manage Roles` permissions!", ephemeral=True)
            return

        report_lines = []

        try:
            # 2. Create Roles
            report_lines.append("**__Roles Created__**")
            for name, color, perms in ROLES_CONFIG:
                existing = discord.utils.get(guild.roles, name=name)
                if not existing:
                    await guild.create_role(name=name, permissions=perms, color=color, reason="Server Setup")
                    report_lines.append(f"✅ {name}")
                else:
                    report_lines.append(f"☑️ {name} (Exists)")
                await asyncio.sleep(0.2) # Avoid rate limits

            # 3. Create Categories and Channels
            report_lines.append("\n**__Channels Created__**")

            for category_name, content in SERVER_STRUCTURE.items():
                # Find or Create Category
                category = discord.utils.get(guild.categories, name=category_name)
                if not category:
                    category = await guild.create_category(category_name)
                    report_lines.append(f"\n📂 **{category_name}**")

                # Create Text Channels
                for text_name in content["text"]:
                    # Note: Discord forces text channels to be lowercase/hyphenated
                    if not discord.utils.get(guild.text_channels, name=text_name, category=category):
                        await guild.create_text_channel(text_name, category=category)
                        report_lines.append(f"  📝 {text_name}")
                        await asyncio.sleep(0.2)

                # Create Voice Channels
                for voice_name in content["voice"]:
                    if not discord.utils.get(guild.voice_channels, name=voice_name, category=category):
                        await guild.create_voice_channel(voice_name, category=category)
                        report_lines.append(f"  🔊 {voice_name}")
                        await asyncio.sleep(0.2)

            # 4. Final Success Embed
            embed = discord.Embed(
                title="✅ Server Setup Complete!",
                description="I have successfully organized your server with the Gaming, Community, and Info layout.",
                color=discord.Color.green()
            )
            # Truncate report if too long
            report_str = "\n".join(report_lines)
            if len(report_str) > 1000:
                report_str = report_str[:1000] + "\n... (list truncated)"

            embed.add_field(name="Log", value=report_str)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: `{str(e)}`", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Setup cancelled. No changes made.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Displays the interactive setup menu."""
    embed = discord.Embed(
        title="🛠️ Server Setup Assistant",
        description=(
            "Click **Build Server** to automatically create:\n"
            "• **Gaming Zone** (Lobbies, Ranked, LFG)\n"
            "• **Community Hub** (General, Music, Memes)\n"
            "• **Info Section** (Rules, Announcements)\n"
            "• **Roles** (Owner, Admin, Gamer, VIP, etc)\n\n"
            "**Note:** I will check for existing channels to avoid duplicates."
        ),
        color=discord.Color.blurple()
    )
    view = ConfirmSetupView()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready! Type !setup in your server.")

if __name__ == "__main__":
    # Get token from environment or input
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        TOKEN = input("Enter your Bot Token: ")
    bot.run(TOKEN)