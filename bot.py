import discord
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional
import random
import asyncio
import os
import sys
import platform
import psutil
import time
from datetime import timedelta, datetime
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

@tasks.loop(seconds=2)
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
    # Prevent duplicate execution on reconnect
    if hasattr(bot, "ready_ran") and bot.ready_ran:
        return
    bot.ready_ran = True

    print("===================================")
    print(f"✅ Logged in as {bot.user} ")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print("===================================")

    # Start status loop safely
    if not change_status.is_running():
        change_status.start()
        print("🔄 Status task started!")

    print("🌐 Syncing slash commands...")

    try:
        # Global sync (can take up to 1 hour to appear everywhere)
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} global slash commands!")

        # Instant per-guild sync
        for guild in bot.guilds:
            guild_synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(guild_synced)} commands to {guild.name} ({guild.id})")

    except Exception as e:
        print(f"❌ Slash sync error: {e}")

@bot.event
async def on_message(message):
    # 1. Ignore bots (including yourself)
    if message.author.bot:
        return

    # 2. Check if the message starts with "anna" or "!"
    # Using .lower() ensures "Anna" or "ANNA" also work
    if message.content.lower().startswith(('anna', '!')):
        async with message.channel.typing():
            await asyncio.sleep(5)
            # You can add a response here if you want!
  
    # 3. Important: This allows your other @bot.commands to still run
    await bot.process_commands(message)

      
# ==================================================
        # --- ERROR HANDLING ---
        # ==================================================

@bot.event
async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("⛔ **Access Denied:** Missing permissions.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("⚠️ **Missing Argument:** Check command usage.")
            else:
                print(f"❌ Unexpected Error: {error}")

        # ==================================================
        # --- COMMAND LOGGING ---
        # ==================================================
@bot.event
async def on_command(ctx):
    from datetime import datetime
    import os

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    guild = ctx.guild
    author = ctx.author
    channel = ctx.channel

    guild_name = guild.name if guild else "Direct Message"
    guild_id = guild.id if guild else "N/A"

    channel_name = getattr(channel, "name", "DM")
    channel_id = getattr(channel, "id", "N/A")

    command_name = ctx.command.name if ctx.command else "Unknown"
    command_content = ctx.message.content if ctx.message else "N/A"

    # Roles (ONLY if in guild)
    if guild:
        roles = [role.name for role in author.roles if role.name != "@everyone"]
        roles_text = ", ".join(roles) if roles else "No Roles"
        is_admin = author.guild_permissions.administrator
    else:
        roles_text = "No Roles (DM)"
        is_admin = False

    avatar_url = author.display_avatar.url

    log_message = (
        "\n"
        "================ COMMAND LOG =================\n"
        f"Time       : {timestamp}\n"
        f"User       : {author} ({author.id})\n"
        f"Admin      : {is_admin}\n"
        f"Roles      : {roles_text}\n"
        f"Avatar CDN : {avatar_url}\n"
        "\n"
        f"Command    : {command_name}\n"
        f"Message    : {command_content}\n"
        f"Channel    : {channel_name} ({channel_id})\n"
        f"Server     : {guild_name} ({guild_id})\n"
        "==============================================\n"
    )

    # ---- PRINT ----
    print(log_message)

    # ---- WRITE FILE SAFELY ----
    try:
        with open("logger.c", "a", encoding="utf-8") as f:
            f.write(log_message)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[LOGGER ERROR] {e}")

    # ---- DM USER ----
    try:
        await author.send(
            f"📜 Logged `{command_name}` at {timestamp}\n"
            f"Server: {guild_name}\n"
            f"Channel: {channel_name}"
        )
    except Exception:
        pass




        # ==================================================
        # --- BOT CONTROL COMMANDS ---
        # ==============================================================
@bot.tree.command(name="start", description="Signals bot is active")
async def start(interaction: discord.Interaction):
                    await interaction.response.send_message("🌲 **AnnaBot is online and guarding the forest!**")
                    message = (
                        "*Turning on @Anna-the-Guardian*\n"
                        "Connecting to Discord API services...\n"
                        f"Gateway ID: {bot.user.id}\n"
                        "System Boot Successful ✅\n"
                        "RAM: 86GB\n"
                        "CPU: AMD Ryzen Threadripper 96-Core\n"
                        "SYSTEM: Windows 11 Server 2025\n"
                        "All packages loaded.\n"
                        "🟢 Bot is ONLINE."
                    )
                    await interaction.followup.send(message)

@bot.tree.command(name="shutdown", description="Shuts down the bot (dev only)")
async def shutdown(interaction: discord.Interaction):

        # ✅ Authorized usernames
        AUTHORIZED_USERS = ["luisthegoat7301", "zelda_life"]  # Put exact usernames here (case-sensitive)

        if interaction.user.name not in AUTHORIZED_USERS:
            return await interaction.response.send_message(
                "⛔ Only authorized developers can shut me down.",
                ephemeral=True
            )

        await interaction.response.send_message("💤 Powering down... Goodbye.")

        print(f"Shutdown initiated by {interaction.user}")

        # Gracefully close Discord connection
        await bot.close()

        # Force stop Python process
        import sys
        sys.exit()

                      


@bot.tree.command(name="restart", description="Restarts the bot systems (dev only)")
async def restart(interaction: discord.Interaction):
                    if (str(interaction.user) not in AUTHORIZED_USERS) and (interaction.user.name not in AUTHORIZED_USERS):
                        return await interaction.response.send_message("⛔ Unauthorized.", ephemeral=True)

                    try:
                        change_status.stop()
                    except Exception:
                        pass

                    try:
                        await bot.change_presence(status=discord.Status.invisible)
                    except Exception:
                        pass

                    await interaction.response.send_message("🔄 Restarting systems...")
                    try:
                        await asyncio.sleep(5)
                    except Exception:
                        pass

                    await interaction.followup.send("✅ Systems rebooted successfully.")
                    try:
                        change_status.start()
                    except Exception:
                        pass



             
# UI CLASSES (Must be defined globally)
# ------------------------------------------------------------------

class TypeModal(discord.ui.Modal, title="Set Activity Type"):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    activity = discord.ui.TextInput(
        label="Activity Type",
        placeholder="playing / watching / listening / streaming",
        required=True,
        max_length=64,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Map string to Discord ActivityType
        type_map = {
            "playing": discord.ActivityType.playing, "play": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching, "watch": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening, "listen": discord.ActivityType.listening,
            "streaming": discord.ActivityType.streaming, "stream": discord.ActivityType.streaming
        }

        chosen = type_map.get(self.activity.value.lower())
        if not chosen:
            return await interaction.response.send_message("❌ Invalid type. Use: playing, watching, listening, or streaming.", ephemeral=True)

        self.parent_view.activity_type = chosen
        self.parent_view.activity_type_raw = self.activity.value
        await interaction.response.edit_message(content=self.parent_view.build_preview(), view=self.parent_view)

class MessageModal(discord.ui.Modal, title="Set Presence Message"):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    message = discord.ui.TextInput(
        label="Message (Stream: Title | URL)",
        placeholder="Chess  OR  My Stream | https://twitch.tv/...",
        required=True,
        style=discord.TextStyle.long,
        max_length=200,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.presence_text = self.message.value
        await interaction.response.edit_message(content=self.parent_view.build_preview(), view=self.parent_view)

class PresenceView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.invoker = ctx.author
        # State
        self.activity_type = None
        self.activity_type_raw = None
        self.presence_text = None
        self.status = discord.Status.online
        self.status_raw = "online"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.invoker:
            await interaction.response.send_message("❌ This is not your menu.", ephemeral=True)
            return False
        return True

    def build_preview(self, confirmed=False):
        t = self.activity_type_raw or "—"
        m = self.presence_text or "—"
        s = self.status_raw
        if confirmed:
            return f"✅ **Applied:**\nType: **{t}**\nMsg: {m}\nStatus: **{s}**"
        return f"**Preview**\nType: `{t}`\nMessage: `{m}`\nStatus: `{s}`\n\n(Only {self.invoker.display_name} can interact)"

    @discord.ui.button(label="Set Type", style=discord.ButtonStyle.secondary)
    async def set_type(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TypeModal(parent_view=self))

    @discord.ui.button(label="Set Message", style=discord.ButtonStyle.secondary)
    async def set_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MessageModal(parent_view=self))

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.activity_type:
            return await interaction.response.send_message("❌ Set Activity Type first.", ephemeral=True)
        if not self.presence_text:
            return await interaction.response.send_message("❌ Set Message first.", ephemeral=True)

        try:
            act = None
            if self.activity_type == discord.ActivityType.streaming:
                if "|" in self.presence_text:
                    title, url = map(str.strip, self.presence_text.split("|", 1))
                    act = discord.Streaming(name=title, url=url)
                else:
                    return await interaction.response.send_message("❌ Streaming needs `Title | URL`", ephemeral=True)
            else:
                act = discord.Activity(type=self.activity_type, name=self.presence_text)

            await self.ctx.bot.change_presence(status=self.status, activity=act)

            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content=self.build_preview(confirmed=True), view=self)
            self.stop()
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

class StatusView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.invoker = ctx.author
        self.chosen = discord.Status.online
        self.chosen_raw = "online"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.invoker:
            await interaction.response.send_message("❌ Not your menu.", ephemeral=True)
            return False
        return True

    def build_preview(self, confirmed=False):
        if confirmed:
            return f"✅ Status updated to **{self.chosen_raw}**"
        return f"**Preview Status**: `{self.chosen_raw}`"

    async def update(self, interaction):
        await interaction.response.edit_message(content=self.build_preview(), view=self)

    @discord.ui.button(label="Online", style=discord.ButtonStyle.primary)
    async def online(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen, self.chosen_raw = discord.Status.online, "online"
        await self.update(interaction)

    @discord.ui.button(label="Idle", style=discord.ButtonStyle.secondary)
    async def idle(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen, self.chosen_raw = discord.Status.idle, "idle"
        await self.update(interaction)

    @discord.ui.button(label="DND", style=discord.ButtonStyle.danger)
    async def dnd(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen, self.chosen_raw = discord.Status.dnd, "dnd"
        await self.update(interaction)

    @discord.ui.button(label="Invisible", style=discord.ButtonStyle.secondary)
    async def invisible(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.chosen, self.chosen_raw = discord.Status.invisible, "invisible"
        await self.update(interaction)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.ctx.bot.change_presence(status=self.chosen)
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content=self.build_preview(confirmed=True), view=self)
            self.stop()
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# ------------------------------------------------------------------
# COMMANDS
# ------------------------------------------------------------------
@bot.command(name="changePresence")
async def changePresence(ctx):
    # Checks the username (e.g., 'johndoe') against your list
    if ctx.author.name not in AUTHORIZED_USERS:
        return await ctx.send("❌ Unauthorized.", delete_after=5)

    view = PresenceView(ctx)
    await ctx.send(view.build_preview(), view=view)

@bot.command(name="changeStatus")
async def changeStatus(ctx):
    # Checks the username (e.g., 'johndoe') against your list
    if ctx.author.name not in AUTHORIZED_USERS:
        return await ctx.send("❌ Unauthorized.", delete_after=5)

    view = StatusView(ctx)
    await ctx.send(view.build_preview(), view=view)




@bot.tree.command(name="makerole", description="Create a role with permissions (dev only)")
async def makerole(interaction: discord.Interaction, perm: str, name: str):
                    if (str(interaction.user) not in AUTHORIZED_USERS) and (interaction.user.name not in AUTHORIZED_USERS):
                        return await interaction.response.send_message("⛔ Developer access only.", ephemeral=True)

                    perms = discord.Permissions.none()
                    p = perm.lower()

                    if p == "admin":
                        perms = discord.Permissions(administrator=True)
                    elif p == "ban":
                        perms = discord.Permissions(ban_members=True)
                    elif p == "kick":
                        perms = discord.Permissions(kick_members=True)
                    elif p == "mod":
                        perms = discord.Permissions(manage_messages=True, kick_members=True, ban_members=True)

                    try:
                        role = await interaction.guild.create_role(name=name, permissions=perms, color=discord.Color.random(), hoist=True)
                        await interaction.response.send_message(f"✅ Created role **{role.name}** with **{p}** permissions!")
                    except Exception as e:
                        await interaction.response.send_message(f"❌ Error creating role: {e}", ephemeral=True)


        # ==================================================
        # --- RUN BOT ---
        # 


# ==============================================================================
# SECTION 1: GENERAL COMMANDS
# ==============================================================================




@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🌿 NatureBot Help",
                          description="Watching nature and moderating.",
                          color=discord.Color.green())
    embed.add_field(
        name="Control",
        value="`start`, `restart`, `shutdown`, `changeStatus`, `changePresence`",
        inline=False)
    embed.add_field(
        name="General",
        value=
        "`ping`, `serverinfo`, `userinfo`, `avatar`, `uptime`, `invite`, `poll`, `8ball`, `roll`, `coinflip`, `slap`, `hug`, `pat`,  `rps` "
    )
    embed.add_field(
        name="Moderation",
        value=
        "`kick`, `ban`, `unban`, `softban`, `timeout`, `untimeout`, `purge`,  `lock`, `unlock`, `slowmode`, `nick`, `addrole`, `removerole`, `warn`, `warnings`, `clearwarns`, `announce`, `dm`, `say`"
    )
    embed.add_field(
        name="Cool/Custom",
        value=
        "`mewmew`, `emojify`, `spoiler`, `reverse`, `mock`, `vaporwave`, `binary`, `morse`, `piglatin`, `advice`, `truth`, `dare`, `joke`, `iq`, `remindme`"
    )
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')
    

@bot.command()
async def react(ctx, message_id: int, emoji: str):
    try:
        # Fetch the message from the current channel
        message = await ctx.channel.fetch_message(message_id)

        # Add the reaction
        await message.add_reaction(emoji)

        # Delete the user's command message
        await ctx.message.delete()

    except discord.NotFound:
        await ctx.send("❌ Message not found.", delete_after=5)
    except discord.HTTPException:
        await ctx.send("❌ Invalid emoji or I can't use that emoji.", delete_after=5)
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}", delete_after=5)

    
import discord
from discord.ext import commands
from discord import ui



        # ---------- Buttons UI ----------
class ServerInfoView(ui.View):
            def __init__(self, guild: discord.Guild, author: discord.Member):
                super().__init__(timeout=120)
                self.guild = guild
                self.author = author

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message("❌ Only the command user can use these buttons.", ephemeral=True)
                    return False
                return True

            @ui.button(label="📋Show Admins📋", style=discord.ButtonStyle.green)
            async def show_admins(self, interaction: discord.Interaction, button: ui.Button):
                admins = [m.mention for m in self.guild.members if m.guild_permissions.administrator]
                if not admins:
                    await interaction.response.send_message("No admins found.", ephemeral=True)
                    return
                await interaction.response.send_message("\n".join(admins[:25]), ephemeral=True)

            @ui.button(label="🎭Show Roles🎭", style=discord.ButtonStyle.blurple)
            async def show_roles(self, interaction: discord.Interaction, button: ui.Button):
                roles = [r.mention for r in self.guild.roles if r.name != "@everyone"]
                if not roles:
                    await interaction.response.send_message("No roles found.", ephemeral=True)
                    return
                await interaction.response.send_message("\n".join(roles[:25]), ephemeral=True)

            @ui.button(label="📸Server Icon📸", style=discord.ButtonStyle.green)
            async def show_icon(self, interaction: discord.Interaction, button: ui.Button):
                if self.guild.icon:
                    await interaction.response.send_message(f"[Click here to view the icon]({self.guild.icon.url})", ephemeral=True)
                else:
                    await interaction.response.send_message("No server icon.", ephemeral=True)

            @ui.button(label="🖼️Server Banner🖼️", style=discord.ButtonStyle.green)
            async def show_banner(self, interaction: discord.Interaction, button: ui.Button):
                if self.guild.banner:
                    await interaction.response.send_message(f"[Click here to view the banner]({self.guild.banner.url})", ephemeral=True)
                else:
                    await interaction.response.send_message("No banner found.", ephemeral=True)

        # ---------- Server Info Command ----------
@bot.command(name="serverinfo")
@commands.guild_only()
async def serverinfo(ctx):
            guild = ctx.guild
            owner = guild.owner or await guild.fetch_owner()
            total = guild.member_count
            humans = len([m for m in guild.members if not m.bot])
            bots = len([m for m in guild.members if m.bot])
            boosts = getattr(guild, "premium_subscription_count", 0)
            boost_level = getattr(guild, "premium_tier", 0)
            created_at = f"<t:{int(guild.created_at.timestamp())}:F>"

            embed = discord.Embed(
                title=f"📊 {guild.name} — Server Info",
                description=f"**Server ID:** `{guild.id}`",
                color=discord.Color.blue()
            )
            embed.add_field(name="👑 Owner", value=owner.mention, inline=True)
            embed.add_field(name="📅 Created", value=created_at, inline=True)
            embed.add_field(name="👥 Members", value=f"Total: {total}\nHumans: {humans}\nBots: {bots}", inline=True)
            embed.add_field(name="🚀 Boost Level", value=f"Level {boost_level}\n{boosts} Boosts", inline=True)
            embed.add_field(name="🎭 Roles", value=f"{len(guild.roles)-1}", inline=True)
            embed.add_field(name="💬 Channels", value=f"{len(guild.channels)}", inline=True)

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            if guild.banner:
                embed.set_image(url=guild.banner.url)

            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            view = ServerInfoView(guild, ctx.author)
            await ctx.send(embed=embed, view=view)





import discord
from discord.ext import commands
from discord import ui


# ==============================
# USER INFO VIEW (BUTTONS)
# ==============================

class UserInfoView(ui.View):
    def __init__(self, member: discord.Member, author: discord.Member):
        super().__init__(timeout=60)
        self.member = member
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the person who typed the command can click the buttons
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This menu isn't for you.", ephemeral=True)
            return False
        return True

    @ui.button(label="Show Roles", emoji="📜", style=discord.ButtonStyle.green)
    async def show_roles(self, interaction: discord.Interaction, button: ui.Button):
        roles = [role.mention for role in self.member.roles if role.name != "@everyone"]
        text = ", ".join(roles) if roles else "No roles."
        await interaction.response.send_message(f"📜 **Roles for {self.member.name}:**\n{text}", ephemeral=True)

    @ui.button(label="Show Permissions", emoji="🔐", style=discord.ButtonStyle.success)
    async def show_perms(self, interaction: discord.Interaction, button: ui.Button):
        perms = [perm.replace("_", " ").title() for perm, value in self.member.guild_permissions if value]
        text = ", ".join(perms) if perms else "No special permissions."
        await interaction.response.send_message(f"🔐 **Permissions for {self.member.name}:**\n{text}", ephemeral=True)

    @ui.button(label="Show Admins", emoji="🛡️", style=discord.ButtonStyle.secondary)
    async def show_admins(self, interaction: discord.Interaction, button: ui.Button):
        # Finds all non-bot members with Administrator permission
        admins = [m.mention for m in interaction.guild.members if m.guild_permissions.administrator and not m.bot]
        text = ", ".join(admins) if admins else "No admins found."
        await interaction.response.send_message(f"🛡️ **Server Admins:**\n{text}", ephemeral=True)

# ==============================
# USER INFO COMMAND
# ==============================

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    # Format timestamps
    joined = f"<t:{int(member.joined_at.timestamp())}:F>" if member.joined_at else "Unknown"
    created = f"<t:{int(member.created_at.timestamp())}:F>"

    # Create Permission Summary
    perms = [perm.replace("_", " ").title() for perm, value in member.guild_permissions if value]
    perms_summary = ", ".join(perms[:8]) + ("..." if len(perms) > 8 else "")

    # Badge logic
    badges = []
    if member.bot: badges.append("🤖 Bot")
    if member.guild_permissions.administrator: badges.append("🛡️ Admin")
    if member.id == ctx.guild.owner_id: badges.append("👑 Owner")
    badge_text = " | ".join(badges) if badges else "Member"

    # Build the Embed
    embed = discord.Embed(
        title=f"User Info - {member.name}",
        color=member.color if member.color != discord.Color.default() else discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=False)
    embed.add_field(name="🏷️ Status", value=badge_text, inline=True)
    embed.add_field(name="🎭 Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="📅 Account Created", value=created, inline=False)
    embed.add_field(name="🚪 Joined Server", value=joined, inline=False)
    embed.add_field(name="🔐 Key Permissions", value=perms_summary or "None", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    # Send message with View
    view = UserInfoView(member, ctx.author)
    await ctx.send(embed=embed, view=view)

# bot.run("YOUR_TOKEN_HERE")
@bot.command()
async def uptime(ctx):
    await ctx.send("I have been watching nature since I woke up!")





@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Poll",
                          description=question,
                          color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=1360329809670045731&permissions=8&response_type=code&redirect_uri=https%3A%2F%2Fsites.google.com%2Fview%2Finfo-about-anna%2Fhome&integration_type=0&scope=identify+email+connections+bot"

@bot.command()
async def invite(ctx):
    """Sends the bot's invite link"""
    await ctx.send(f"🌟 Invite me to your server using this link:\n{INVITE_LINK}")


@bot.command(aliases=['8ball'])
async def eightball(ctx, *, question):
    responses = [
        "It is certain.", "Without a doubt.", "Ask again later.",
        "My sources say no."
    ]
    await ctx.send(f"🎱 **Q:** {question}\n**A:** {random.choice(responses)}")


@bot.command()
async def roll(ctx, sides: int = 6):
    await ctx.send(f"🎲 Rolled a **{random.randint(1, sides)}**!")


@bot.command()
async def coinflip(ctx):
    await ctx.send(f"🪙 It's **{random.choice(['Heads', 'Tails'])}**!")




@bot.command()
async def slap(ctx, member: discord.Member):
    embed = discord.Embed(
        description=f"**{ctx.author.name}** slapped **{member.name}**!",
        color=discord.Color.red())
    embed.set_image(
        url="https://media.giphy.com/media/Gf3AUz3eBNb8q28W84/giphy.gif")
    await ctx.send(embed=embed)





@bot.tree.command(name="giveviewacessandmsg", description="Give a user access to a channel and send a message")
@app_commands.describe(user="Select user", channel="Select channel")
async def giveviewacessandmsg(
    interaction: discord.Interaction,
    user: discord.Member,
    channel: discord.TextChannel
):

    await interaction.response.defer(ephemeral=True)

    # Check if bot has permission
    if not interaction.guild.me.guild_permissions.manage_channels:
        return await interaction.followup.send(
            "❌ I need Manage Channels permission.",
            ephemeral=True
        )

    try:
        await channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True
        )

        await channel.send(f"👋 {user.mention}, you now have access to this channel!")

        await interaction.followup.send(
            "✅ Done successfully.",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "❌ Permission error. My role must be above the user and channel.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ Unexpected error: {e}",
            ephemeral=True
        )





@bot.command()
async def pat(ctx, member: discord.Member):
    await ctx.send(f"**{ctx.author.name}** pats **{member.name}** on the head."
                   )

@bot.tree.command(name="showchannels", description="Show channels from a server")
@app_commands.describe(
    server="Server name (must share with bot)",
    amount="How many channels to show (0-250)"
)
async def showchannels(
    interaction: discord.Interaction,
    server: str,
    amount: app_commands.Range[int, 0, 250]
):

    await interaction.response.defer(ephemeral=True)

    # Find the guild
    guild = discord.utils.get(bot.guilds, name=server)

    if not guild:
        return await interaction.followup.send(
            "❌ Server not found or I am not in that server.",
            ephemeral=True
        )

    # Get channels (sorted by position)
    channels = sorted(guild.channels, key=lambda c: c.position)

    # Apply limit
    if amount == 0:
        amount = len(channels)

    channels = channels[:amount]

    if not channels:
        return await interaction.followup.send(
            "⚠️ No channels found.",
            ephemeral=True
        )

    # Format output
    output = "\n".join(
        f"{i+1}. #{channel.name} ({channel.__class__.__name__})"
        for i, channel in enumerate(channels)
    )

    # Discord message limit protection
    if len(output) > 1900:
        output = output[:1900] + "\n... truncated"

    await interaction.followup.send(
        f"📂 **Channels in {guild.name}**\n\n{output}",
        ephemeral=True
    )





# ==============================================================================
# SECTION 2: MODERATION COMMANDS
# ==============================================================================


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="None"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked {member}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="None"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned {member}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"🕊️ Unbanned {user}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member):
    await member.ban(reason="Softban", delete_message_days=1)
    await member.unban()
    await ctx.send(f"🧹 Softbanned {member}")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int):
    await member.timeout(timedelta(minutes=minutes))
    await ctx.send(f"⏰ {member} timed out for {minutes}m.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 Removed timeout for {member}")


@bot.command(name="specs")
async def specs(ctx):
    embed = discord.Embed(
        title="🚀 Mega Ultra Server Specs",
        description="DESKTOP-LUIS-VITRUAL-MACCHINE",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🧠 RAM",
        value="999 TB DDR5 Ultra-Speed Memory",
        inline=False
    )

    embed.add_field(
        name="💾 Storage",
        value="350 PB NVMe Gen5 SSD Storage",
        inline=False
    )

    embed.add_field(
        name="⚙️ CPU",
        value="11500 Cores • 7750 Threads • 1000.0GHz Boost * AMD Ryzen 9 9950X3D/9950X",
        inline=False
    )

    embed.add_field(
        name="📂 File Capacity",
        value="100,000 Files Supported",
        inline=True
    )

    embed.add_field(
        name="📜 Code Capacity",
        value="1000,000,000 Lines of Code",
        inline=True
    )

    embed.add_field(
        name="🌐 Network",
        value="975 Gbps Dedicated Uplink",
        inline=False
    )

    embed.set_footer(text="Powered by Omega Ultra Plan 999  643,10,100,100,000$ cost.🔥")

    await ctx.send(embed=embed)

    
@bot.command()
async def giveacess(ctx, *, user_input: str):
        await ctx.send(f"It does successfully got access for {user_input}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ Deleted {amount} messages.", delete_after=3)





@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=False)
    await ctx.send("🔒 Locked.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,
                                      send_messages=True)
    await ctx.send("🔓 Unlocked.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐢 Slowmode: {seconds}s.")


@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, name=None):
    await member.edit(nick=name)
    await ctx.send(f"🏷️ Changed nick for {member.name}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx,
                  member: discord.Member,
                  role: discord.Role,
                  *,
                  reason="Runned command by a staff member"):
    await member.add_roles(role, reason=reason)
    await ctx.send(f"✅ Added {role.name} to {member.name}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx,
                     member: discord.Member,
                     role: discord.Role,
                     *,
                     reason="Runned command by a staff member"):
    await member.remove_roles(role, reason=reason)
    await ctx.send(f"❌ Removed {role.name} from {member.name}")


warnings = {}


@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, r="No reason"):
    if member.id not in warnings: warnings[member.id] = []
    warnings[member.id].append(r)
    await ctx.send(f"⚠️ Warned {member.name}")


@bot.command()
async def warnings_list(ctx, member: discord.Member):
    w = warnings.get(member.id, [])
    await ctx.send(
        f"📋 {member.name} has {len(w)} warnings: {', '.join(w) if w else 'None'}"
    )


@bot.command()
@commands.has_permissions(kick_members=True)
async def clearwarns(ctx, member: discord.Member):
    warnings[member.id] = []
    await ctx.send(f"🧼 Cleared {member.name}")

@bot.command()
async def joinvc(ctx):
    if ctx.author.voice is None:
        await ctx.send("You must be in a voice channel first!")
        return

    channel = ctx.author.voice.channel

    # Connect to the voice channel (or move if already connected)
    if ctx.voice_client is None:
        vc = await channel.connect()
    else:
        vc = ctx.voice_client
        await vc.move_to(channel)

    # Ensure bot is unmuted and undeafened
    await vc.guild.me.edit(mute=False, deafen=False)

    await ctx.send(f"Joined **{channel.name}** and I'm unmuted & undeafened!")


@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, channel: discord.TextChannel, *, msg):
    await channel.send(embed=discord.Embed(
        title="📢 Announcement", description=msg, color=discord.Color.red()))


@bot.command()
@commands.has_permissions(administrator=True)
async def dm(ctx, member: discord.Member, *, msg):
    try:
        await member.send(f"📩 Staff: {msg}")
        await ctx.send("Sent.")
    except:
        await ctx.send("DMs closed.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)


# ==============================================================================
# SECTION 3: CUSTOM COOL COMMANDS
# =====================================================================


@bot.command()
async def emojify(ctx, *, text):
    res = "".join(f":regional_indicator_{c}: " if c.isalpha() else c
                  for c in text.lower())
    await ctx.send(res)


@bot.command()
async def spoiler(ctx, *, text):
    await ctx.send("".join(f"||{c}||" for c in text))


@bot.command()
async def reverse(ctx, *, text):
    await ctx.send(text[::-1])


@bot.command()
async def mock(ctx, *, text):
    await ctx.send("".join(
        random.choice([c.upper(), c.lower()]) for c in text))


@bot.command()
async def vaporwave(ctx, *, text):
    await ctx.send(" ".join(text))


@bot.command()
async def hello(ctx):
        await ctx.send(f"Hello {ctx.author.name}!, how are you? ")


@bot.command()
async def binary(ctx, *, text):
    await ctx.send(f"```{' '.join(format(ord(c), '08b') for c in text)}```")


@bot.command()
async def morse(ctx, *, text):
    m_dict = {
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        ' ': '/'
    }
    await ctx.send(" ".join(m_dict.get(c.upper(), c) for c in text))





@bot.command()
async def advice(ctx):
    await ctx.send(f"💡 {random.choice(['Drink water.', 'Sleep more.'])}")


@bot.command()
async def truth(ctx):
    await ctx.send(f"🤥 {random.choice(['Biggest fear?', 'Crush name?'])}")


@bot.command()
async def dare(ctx):
    await ctx.send(f"🔥 {random.choice(['Send last DM.', 'Meow in VC.'])}")


@bot.command()
async def joke(ctx):
    await ctx.send(
        "🤣 Why did the bot cross the road? To get to the nature side!")


@bot.command()
async def iq(ctx):
    await ctx.send(f"🧠 IQ: **{random.randint(50, 200)}**")


@bot.command()
async def remindme(ctx, time: int, *, task):
    await ctx.send("⏰ Noted.")
    await asyncio.sleep(time)
    await ctx.send(f"🔔 {ctx.author.mention}: {task}")


@bot.command()
async def wouldyourather(ctx):
    choices = [
        ("Fly or Invisibility?", "🦅", "👻"),
        ("Coffee or Tea?", "☕", "🍵"),
        ("Pizza or Burger?", "🍕", "🍔"),
        ("Summer or Winter?", "☀️", "❄️"),
        ("Beach or Mountains?", "🏖️", "🏔️"),
    ]
    question, emoji1, emoji2 = random.choice(choices)
    embed = discord.Embed(title="🤔 Would You Rather...",
                          description=question,
                          color=discord.Color.purple())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji1)
    await msg.add_reaction(emoji2)


@bot.command()
async def weather(ctx):
    conditions = [
        "☀️ Sunny", "🌧️ Rainy", "⛅ Cloudy", "🌩️ Stormy", "❄️ Snowy", "🌬️ Windy"
    ]
    await ctx.send(f"🌍 Weather in nature: **{random.choice(conditions)}**")


@bot.command()
async def fact(ctx):
    facts = [
        "🌳 Forests produce 28% of the world's oxygen.",
        "🐝 Honey never spoils and can last for thousands of years.",
        "🦁 A group of flamingos is called a 'flamboyance'.",
        "🌊 Octopuses have three hearts.",
        "🦗 Grasshoppers have been on Earth for 300 million years.",
        "🌺 Sunflowers can track the sun across the sky.",
    ]
    await ctx.send(random.choice(facts))


@bot.command()
async def pickagain(ctx):
    colors = [
        "Red", "Blue", "Green", "Purple", "Yellow", "Orange", "Pink", "Black"
    ]
    await ctx.send(f"🎨 Your random color is: **{random.choice(colors)}**")

@bot.command()
async def a(ctx):
    # Get the member by name#discriminator
    member = discord.utils.get(ctx.guild.members, name="elian01676")
    if not member:
        await ctx.send("User not found.")
        return

    # Get the channel by ID
    channel = ctx.guild.get_channel(1400193275498987560)
    if not channel:
        await ctx.send("Channel not found.")
        return

    # Set permissions for the user
    overwrite = channel.overwrites_for(member)
    overwrite.view_channel = True
    overwrite.send_messages = True
    await channel.set_permissions(member, overwrite=overwrite)

    await ctx.send(f"✅ {member.mention} now has access to send messages and view the channel.")


@bot.command()
async def quote(ctx):
    quotes = [
        "In every walk with nature, one receives far more than he seeks. - John Muir",
        "The clearest way into the Universe is through a forest wilderness. - John Muir",
        "Nature is not a place to visit. It is home. - Gary Snyder",
        "We do not inherit the earth from our ancestors; we borrow it from our children. - Native American Proverb",
    ]
    embed = discord.Embed(description=random.choice(quotes),
                          color=discord.Color.green())
    embed.set_footer(text="🌿 Nature Quote")
    await ctx.send(embed=embed)


@bot.command()
async def rng(ctx, min_val: int, max_val: int):
    result = random.randint(min_val, max_val)
    await ctx.send(
        f"🎲 Random number between {min_val} and {max_val}: **{result}**")


@bot.command()
async def choose(ctx, *, options):
    choices = [c.strip() for c in options.split("|")]
    if len(choices) < 2:
        await ctx.send("❌ Provide at least 2 options separated by |")
        return
    await ctx.send(f"✨ I choose: **{random.choice(choices)}**")


@bot.command()
async def prefix(ctx):
    await ctx.send(f"🔤 My command prefix is: `{PREFIX}`")


@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title="🤖 NatureBot Info",
                          color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=False)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=False)
    embed.add_field(name="Prefix", value=PREFIX, inline=False)
    embed.add_field(name="Latency",
                    value=f"{round(bot.latency * 1000)}ms",
                    inline=False)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else "")
    await ctx.send(embed=embed)


@bot.command()
async def rps(ctx, choice: str):
    """Play Rock, Paper, Scissors. Example: !rps rock"""
    valid = ["rock", "paper", "scissors"]
    if choice.lower() not in valid:
        await ctx.send("❌ Choose: rock, paper, or scissors")
        return
    bot_choice = random.choice(valid)
    result = "Tie!" if choice.lower() == bot_choice else ("You win! 🎉" if (
        choice.lower() == "rock" and bot_choice == "scissors"
        or choice.lower() == "paper" and bot_choice == "rock"
        or choice.lower() == "scissors" and bot_choice == "paper") else
                                                          "I win! 🏆")
    await ctx.send(
        f"You chose **{choice}**, I chose **{bot_choice}**. {result}")


@bot.command()
async def flip(ctx):
    """Flip a coin with a dramatic animation"""
    msg = await ctx.send("🪙 Flipping...")
    await asyncio.sleep(1)
    result = random.choice(["Heads", "Tails"])
    await msg.edit(content=f"🪙 It landed on... **{result}**!")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def sync(ctx):
    """
    Syncs the slash commands to the server instantly.
    """
    fmt = await ctx.bot.tree.sync()
    await ctx.send(f"✅ Synced {len(fmt)} slash commands!")


# --- 1. TEXT COMMAND VERSION (FIXED) ---
@bot.command()
@commands.has_permissions(manage_emojis=True)
async def copyEmoji(ctx,
                    emoji: str):  # changed to str to prevent conversion errors
    """
    Copies a custom emoji.
    Usage: !copyEmoji <emoji>
    """
    try:
        # Manually convert the string to a PartialEmoji
        partial_emoji = discord.PartialEmoji.from_str(emoji)

        if not partial_emoji.is_custom_emoji():
            return await ctx.send(
                "❌ You can only copy **Custom Emojis**, not standard ones like 😀."
            )

        # Download and Upload
        image_data = await partial_emoji.read()
        new_emoji = await ctx.guild.create_custom_emoji(
            name=partial_emoji.name, image=image_data)

        await ctx.send(f"✅ Copied! New emoji: {new_emoji}")

    except discord.HTTPException:
        await ctx.send("❌ Failed: Do you have empty emoji slots?")
    except ValueError:
        await ctx.send("❌ Error: That doesn't look like a valid custom emoji.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# --- 2. SLASH COMMAND VERSION ---
@bot.tree.command(name="copy_emoji",
                  description="Steal a custom emoji from another server")
@app_commands.describe(emoji="Paste the emoji here")
@app_commands.checks.has_permissions(manage_emojis=True)
async def copy_emoji_slash(interaction: discord.Interaction, emoji: str):
    await interaction.response.defer()

    try:
        # Convert string to emoji object
        partial_emoji = discord.PartialEmoji.from_str(emoji)

        image_data = await partial_emoji.read()

        new_emoji = await interaction.guild.create_custom_emoji(
            name=partial_emoji.name, image=image_data)

        await interaction.followup.send(
            f"✅ Steal successful! Added {new_emoji}")

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, target: str, role: discord.Role):
    """
    Gives a role to a specific member or EVERYONE in the server.
    Usage: !give_role @User 123456789
    Usage: !give_role all 123456789
    """
    # 1. Check if the bot's role is high enough to give this role
    if ctx.guild.me.top_role <= role:
        return await ctx.send(
            "❌ My role is not high enough to assign this role!")

    # --- MODE: ALL ---
    if target.lower() == "all":
        status_msg = await ctx.send(
            "⏳ Starting mass-role for **all** members. This may take a while..."
        )
        count = 0

        for member in ctx.guild.members:
            # Skip if they already have it or if it's a bot (optional)
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                    # Small sleep to prevent Discord rate limits (Very Important!)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    continue
                except Exception as e:
                    print(f"Error giving role to {member}: {e}")

        await status_msg.edit(
            content=f"✅ Finished! Added {role.name} to **{count}** members.")

    # --- MODE: SINGLE MEMBER ---
    else:
        try:
            # Try to find the member by ID or Mention
            member = await commands.MemberConverter().convert(ctx, target)
            await member.add_roles(role)
            await ctx.send(f"✅ Added {role.name} to **{member.display_name}**."
                           )
        except commands.MemberNotFound:
            await ctx.send(
                f"❌ Could not find a member named `{target}`. Use a mention, ID, or type `all`."
            )


@bot.tree.command(name="ping", description="Check latency and system specs")
async def ping_slash(interaction: discord.Interaction):

    # --- CPU ---
    cpu_name = platform.processor() or "Unknown CPU"
    physical = psutil.cpu_count(logical=False) or 0
    logical = psutil.cpu_count(logical=True) or 0

    # --- RAM (GB) ---
    total_ram = psutil.virtual_memory().total / (1024 ** 3)
    ram_gb = f"{total_ram:.2f} GB"

    # --- GPU (Windows VM expected) ---
    gpu_name = "Windows VM Graphics Driver 2"

    # --- Device Name ---
    device_name = "Desktop-LUIS-Anna-VITRUAL-MACCHINE"

    # --- Real Uptime ---
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    now = datetime.now()
    delta = timedelta(seconds=uptime_seconds)
    # Using a simple calculation if psutil boot_time is too far back or just format the delta
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # --- Latency ---
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🖥️ System Specs",
        color=0x2f3136
    )

    embed.add_field(
        name="Device",
        value=f"`{device_name}`",
        inline=False
    )

    embed.add_field(
        name="CPU",
        value=f"{cpu_name}\n{physical}C / {logical}T",
        inline=False
    )

    embed.add_field(
        name="RAM",
        value=ram_gb,
        inline=True
    )

    embed.add_field(
        name="Graphics",
        value=gpu_name,
        inline=True
    )

    embed.add_field(
        name="Real Uptime",
        value=uptime_str,
        inline=False
    )

    embed.add_field(
        name="Latency",
        value=f"🏓 {latency}ms",
        inline=True
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="echo", description="Make the bot repeat your message")
@app_commands.describe(message="The message to repeat")
async def echo_slash(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="user_info", description="Get information about a user")
@app_commands.describe(member="The member to get info about")
async def user_info_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    perms = [perm.replace("_", " ").title() for perm, value in member.guild_permissions if value]
    perms_text = ", ".join(perms[:10]) + ("..." if len(perms) > 10 else "")
    
    embed = discord.Embed(title=f"User Info - {member}", color=member.color)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=True)
    embed.add_field(name="Created", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=True)
    embed.add_field(name="Permissions", value=perms_text or "None", inline=False)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    await interaction.response.send_message(embed=embed)

# --- ADDITIONAL SLASH COMMANDS (fixed) ---

# 1. Moderation
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if interaction.guild is None:
        return await interaction.response.send_message("⛔ This command can only be used in a server.", ephemeral=True)

    bot_member = interaction.guild.me or await interaction.guild.fetch_member(bot.user.id)
    if not bot_member.guild_permissions.ban_members:
        return await interaction.response.send_message("⛔ I don't have permission to ban members.", ephemeral=True)

    # Prevent banning the guild owner or the bot itself
    if member.id == interaction.guild.owner_id:
        return await interaction.response.send_message("⛔ I cannot ban the server owner.", ephemeral=True)
    if member.id == bot.user.id:
        return await interaction.response.send_message("⛔ I cannot ban myself.", ephemeral=True)

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ Banned **{member}** for: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("⛔ I do not have permission to ban that user.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❗ Failed to ban the user. Please try again later.", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if interaction.guild is None:
        return await interaction.response.send_message("⛔ This command can only be used in a server.", ephemeral=True)

    bot_member = interaction.guild.me or await interaction.guild.fetch_member(bot.user.id)
    if not bot_member.guild_permissions.kick_members:
        return await interaction.response.send_message("⛔ I don't have permission to kick members.", ephemeral=True)

    # Safety checks
    if member.id == interaction.guild.owner_id:
        return await interaction.response.send_message("⛔ I cannot kick the server owner.", ephemeral=True)
    if member.id == bot.user.id:
        return await interaction.response.send_message("⛔ I cannot kick myself.", ephemeral=True)

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ Kicked **{member}** for: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("⛔ I do not have permission to kick that user.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❗ Failed to kick the user. Please try again later.", ephemeral=True)

@bot.tree.command(name="clear", description="Clear a number of messages (1-100)")
@app_commands.describe(amount="Number of messages to clear (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_slash(interaction: discord.Interaction, amount: int):
    if interaction.guild is None:
        return await interaction.response.send_message("⛔ This command can only be used in a server.", ephemeral=True)

    if amount < 1 or amount > 100:
        return await interaction.response.send_message("⛔ Amount must be between 1 and 100.", ephemeral=True)

    channel = interaction.channel
    # Ensure channel supports purge
    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
        return await interaction.response.send_message("⛔ I can only clear messages in text channels or threads.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    try:
        # note: purge will skip messages older than 14 days automatically
        deleted = await channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Cleared **{len(deleted)}** messages.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("⛔ I don't have permission to manage messages in this channel.", ephemeral=True)
    except discord.HTTPException:
        await interaction.followup.send("❗ Failed to clear messages. Please try again later.", ephemeral=True)

# 2. General
@bot.tree.command(name="server_info", description="Get information about the server")
async def server_info_slash(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        return await interaction.response.send_message("⛔ This command can only be used in a server.", ephemeral=True)

    owner = guild.owner or (await guild.fetch_member(guild.owner_id) if guild.owner_id else "Unknown")
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=str(owner), inline=True)
    embed.add_field(name="Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Created At", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=False)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

# 3. Fun
@bot.tree.command(name="roll_dice", description="Roll a dice")
@app_commands.describe(sides="Number of sides (default 6)")
async def roll_slash(interaction: discord.Interaction, sides: int = 6):
    if sides < 2:
        return await interaction.response.send_message("⛔ Sides must be at least 2.", ephemeral=True)
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 Rolled a **{result}** (1-{sides})!")

@bot.tree.command(name="random_joke", description="Get a funny joke by me.")
async def joke_slash(interaction: discord.Interaction):
    jokes = [
        "Why did the bot cross the road? To get to the nature side!",
        "What do you call a fake noodle? An Impasta!",
        "Why don't scientists trust atoms? Because they make up everything!"
    ]
    await interaction.response.send_message(f"🤣 {random.choice(jokes)}")


# 11 Slash (Tree) Commands — NO imports, NO setup
# Assumes: bot, discord, app_commands, random already exist

POLL_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"]

@bot.tree.command(name="echo2", description="Echo back your text")
async def echo(interaction, text: str):
    await interaction.response.send_message(text)

@bot.tree.command(name="8ball", description="Ask the magic 8ball")
async def eight_ball(interaction, question: str):
    answers = ["Yes.","No.","Maybe.","Definitely!","Absolutely not.","Ask again."]
    await interaction.response.send_message(f"🎱 {random.choice(answers)}")

@bot.tree.command(name="roll", description="Roll dice like 2d6")
async def roll(interaction, notation: str):
    try:
        n, m = notation.lower().split("d")
        n = int(n) if n else 1
        m = int(m)
        rolls = [random.randint(1, m) for _ in range(n)]
        await interaction.response.send_message(f"🎲 {rolls} → **{sum(rolls)}**")
    except:
        await interaction.response.send_message("Invalid format.", ephemeral=True)

@bot.tree.command(name="coin", description="Flip a coin")
async def coin(interaction):
    await interaction.response.send_message(f"🪙 {random.choice(['Heads','Tails'])}")

@bot.tree.command(name="rps", description="Rock Paper Scissors")
@app_commands.choices(choice=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors"),
])
async def rps(interaction, choice: app_commands.Choice[str]):
    bot_choice = random.choice(["rock","paper","scissors"])
    await interaction.response.send_message(f"You: {choice.value} | Bot: {bot_choice}")

@bot.tree.command(name="avatar", description="Show avatar")
async def avatar(interaction, user: discord.User = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user}'s Avatar")
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="Create a poll (2-10 options)")
async def poll(interaction, question: str, options: str):
    opts = [o.strip() for o in options.split(',') if o.strip()]
    if not 2 <= len(opts) <= 10:
        await interaction.response.send_message("2-5 options required.", ephemeral=True)
        return
    desc = "\n".join(f"{POLL_EMOJIS[i]} {opts[i]}" for i in range(len(opts)))
    embed = discord.Embed(title=question, description=desc)
    msg = await interaction.channel.send(embed=embed)
    for i in range(len(opts)):
        await msg.add_reaction(POLL_EMOJIS[i])
    await interaction.response.send_message("Poll created!", ephemeral=True)

@bot.tree.command(name="shuffle", description="Shuffle items")
async def shuffle(interaction, items: str):
    arr = [x.strip() for x in items.split(',') if x.strip()]
    random.shuffle(arr)
    await interaction.response.send_message("🔀 " + ", ".join(arr))

@bot.tree.command(name="color", description="Random hex color")
async def color(interaction):
    hexcol = ''.join(random.choice('0123456789ABCDEF') for _ in range(6))
    embed = discord.Embed(title=f"#{hexcol}", color=int(hexcol,16))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ascii", description="Stylized text")
async def ascii_text(interaction, text: str):
    await interaction.response.send_message(f"```\n{' '.join(text.upper())}\n```")

@bot.tree.command(name="stats", description="Show latency")
async def stats(interaction):
    await interaction.response.send_message(f"🏓 {round(bot.latency*1000)}ms")


# 4. Restart
@bot.tree.command(name="restart2", description="Restarts the bot (Authorized users only)")
async def restart_slash(interaction: discord.Interaction):
    # Support either AUTHORIZED_USER (single str/id) or AUTHORIZED_USERS (iterable)
    user_ok = False
    if globals().get("AUTHORIZED_USER") is not None:
        user_ok = str(interaction.user) == str(globals().get("AUTHORIZED_USER")) or str(interaction.user.id) == str(globals().get("AUTHORIZED_USER"))
    else:
        auth_list = globals().get("AUTHORIZED_USERS", [])
        try:
            user_ok = (str(interaction.user) in auth_list) or (str(interaction.user.id) in [str(x) for x in auth_list])
        except Exception:
            user_ok = False

    if not user_ok:
        return await interaction.response.send_message("⛔ You are not authorized to restart me!", ephemeral=True)

    await interaction.response.send_message("🔄 Restarting... See you in a bit!", ephemeral=True)
    # Subprocess or execv in your main file will handle the actual restart; using sys.executable is more portable
    os.execv(sys.executable, [sys.executable] + sys.argv)
    
# Paste this into your bot file (where `discord`, `app_commands` and `tree` already exist).
# No imports or token/login code here — only command registration.
# Call: setup(tree, start_time=your_bot_start_datetime) after you create the tree.

def setup(tree, *, start_time=None):
    # in-memory warnings store: {guild_id: {user_id: [reason, ...]}}
    warnings_store = {}

    # helper
    def _get_guild_warns(guild_id):
        return warnings_store.setdefault(guild_id, {})

    ####################
    # Utility commands
    ####################

@bot.tree.command(name="pings", description="Check bot latency")
async def ping(interaction):
        latency_ms = round(interaction.client.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency_ms}ms")


        # ---------------------------
        # Utility: consistent decorator usage: use bot.tree.command
        # ---------------------------

        # ---------- Server / User ----------
        @bot.tree.command(name="serverinfo", description="Show server info")
        async def serverinfo(interaction: discord.Interaction):
            g = interaction.guild
            if not g:
                await interaction.response.send_message("This command only works in a server.", ephemeral=True)
                return

            owner = g.owner
            if owner is None and g.owner_id:
                try:
                    owner = await bot.fetch_user(g.owner_id)
                except Exception:
                    owner = "Unknown"

            text = (
                f"**{g.name}** (ID: {g.id})\n"
                f"Members: {g.member_count}\n"
                f"Roles: {len(g.roles)}\n"
                f"Channels: {len(g.channels)}\n"
                f"Owner: {getattr(owner, 'mention', str(owner))}\n"
            )
            await interaction.response.send_message(text)

@bot.tree.command(name="userinfo", description="Show info about a user")
@app_commands.describe(user="User to get info about (optional)")
async def userinfo(interaction: discord.Interaction, user: Optional[discord.Member] = None):
            member = user or (interaction.user if isinstance(interaction.user, discord.Member) else None)
            if member is None:
                # fallback: try to fetch member if in guild
                if interaction.guild and interaction.user:
                    member = await interaction.guild.fetch_member(interaction.user.id)
            if member is None:
                await interaction.response.send_message("Could not resolve member info.", ephemeral=True)
                return

            roles = ", ".join(r.name for r in member.roles[1:]) or "None"
            joined = member.joined_at.isoformat() + " UTC" if getattr(member, "joined_at", None) else "Unknown"
            created = member.created_at.isoformat() + " UTC" if getattr(member, "created_at", None) else "Unknown"
            text = (
                f"**{member}** (ID: {member.id})\n"
                f"Joined: {joined}\n"
                f"Account created: {created}\n"
                f"Roles: {roles}\n"
            )
            await interaction.response.send_message(text)

@bot.tree.command(name="avatar-2", description="Show a user's avatar")
@app_commands.describe(user="User to show avatar for (optional)")
async def avatar(interaction: discord.Interaction, user: Optional[discord.User] = None):
            target = user or interaction.user
            # use display_avatar for best result
            url = target.display_avatar.url
            await interaction.response.send_message(url)

@bot.tree.command(name="uptime", description="Show bot uptime")
async def uptime(interaction: discord.Interaction):
            if start_time is None:
                await interaction.response.send_message("Uptime not available (bot hasn't fully started).", ephemeral=True)
                return
            delta = datetime.datetime.utcnow() - start_time
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(rem, 60)
            await interaction.response.send_message(f"Uptime: {hours}h {minutes}m {seconds}s")

@bot.tree.command(name="invite-bot", description="Get the bot invite link template")
async def invite(interaction: discord.Interaction):
            await interaction.response.send_message(
                "Invite me with this template (replace CLIENT_ID and permissions as needed):\n"
                "https://discord.com/oauth2/authorize?client_id=1360329809670045731&scope=bot%20applications.commands&permissions=8"
            )

        # ---------------------------
        # Fun / utility
        # ---------------------------
@bot.tree.command(name="8ball-2", description="Ask the magic 8-ball")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
            answers = [
                "It is certain.", "Without a doubt.", "Yes — definitely.", "Ask again later.",
                "Cannot predict now.", "Don't count on it.", "My sources say no.", "Very doubtful."
            ]
            await interaction.response.send_message(f"🎱 {random.choice(answers)}")

@bot.tree.command(name="roll-2", description="Roll dice or a number (e.g. 1d6 or 20)")
@app_commands.describe(dice="1d6 style or single number")
async def roll(interaction: discord.Interaction, dice: str = "1d6"):
            try:
                if "d" in dice.lower():
                    num_s, sides_s = dice.lower().split("d", 1)
                    num = int(num_s) if num_s else 1
                    sides = int(sides_s)
                    num = max(1, min(num, 100))      # safety limits
                    sides = max(1, min(sides, 10000))# safety limits
                    rolls = [random.randint(1, sides) for _ in range(num)]
                    total = sum(rolls)
                    await interaction.response.send_message(f"Rolled: {rolls} (total {total})")
                else:
                    n = int(dice)
                    n = max(1, min(n, 1000000))
                    r = random.randint(1, n)
                    await interaction.response.send_message(f"Rolled: {r}")
            except Exception:
                await interaction.response.send_message("Invalid format. Use like `1d6` or `20`.", ephemeral=True)

@bot.tree.command(name="coinflip-2", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
            await interaction.response.send_message(random.choice(["Heads", "Tails"]))

@bot.tree.command(name="rps-2", description="Play rock-paper-scissors")
@app_commands.describe(choice="rock, paper or scissors")
async def rps(interaction: discord.Interaction, choice: str):
            choice = choice.lower()
            options = ["rock", "paper", "scissors"]
            if choice not in options:
                await interaction.response.send_message("Pick rock, paper, or scissors.", ephemeral=True)
                return
            bot_choice = random.choice(options)
            if choice == bot_choice:
                outcome = "tie"
            elif (choice, bot_choice) in [("rock","scissors"),("paper","rock"),("scissors","paper")]:
                outcome = "you win"
            else:
                outcome = "you lose"
            await interaction.response.send_message(f"You: {choice} — Bot: {bot_choice} — {outcome}")

@bot.tree.command(name="slap", description="Slap someone")
@app_commands.describe(user="Member to slap")
async def slap(interaction: discord.Interaction, user: discord.Member):
            await interaction.response.send_message(f"{interaction.user.mention} slaps {user.mention}! Ow!")

@bot.tree.command(name="hug", description="Hug someone")
@app_commands.describe(user="Member to hug")
async def hug(interaction: discord.Interaction, user: discord.Member):
            await interaction.response.send_message(f"{interaction.user.mention} gives {user.mention} a warm hug 🤗")

@bot.tree.command(name="pat", description="Pat someone")
@app_commands.describe(user="Member to pat")
async def pat(interaction: discord.Interaction, user: discord.Member):
            await interaction.response.send_message(f"{interaction.user.mention} gently pats {user.mention}.")

        # ---------------------------
        # Poll (quick)
        # ---------------------------
@bot.tree.command(name="poll-2", description="Create a quick poll (text only, adds 👍👎🤷)")
@app_commands.describe(question="Question for the poll")
async def poll(interaction: discord.Interaction, question: str):
            await interaction.response.send_message(f"**Poll:** {question}")
            # add reactions to original response (bot needs add_reactions permission)
            try:
                msg = await interaction.original_response()  # returns Message
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
                await msg.add_reaction("🤷")
            except Exception:
                pass

# ---------------------------
# Moderation helpers & commands
# ---------------------------
def _no_perm(ephemeral=True):
    return {"ephemeral": ephemeral}

@bot.tree.command(name="kick-2", description="Kick a member")
@app_commands.describe(member="Member to kick", reason="Reason (optional)")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message("You don't have permission to kick members.", **_no_perm())
                return
            try:
                await member.kick(reason=reason)
                await interaction.response.send_message(f"Kicked {member} ({member.id}).")
            except Exception as e:
                await interaction.response.send_message(f"Failed to kick: {e}", **_no_perm())

@bot.tree.command(name="ban-2", description="Ban a member")
@app_commands.describe(member="Member to ban", reason="Reason (optional)")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("You don't have permission to ban members.", **_no_perm())
                return
            try:
                await interaction.guild.ban(member, reason=reason)
                await interaction.response.send_message(f"Banned {member} ({member.id}).")
            except Exception as e:
                await interaction.response.send_message(f"Failed to ban: {e}", **_no_perm())

@bot.tree.command(name="unban", description="Unban a user by ID or mention")
@app_commands.describe(user="User to unban (mention or ID)")
async def unban(interaction: discord.Interaction, user: discord.User):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("You don't have permission to unban members.", **_no_perm())
                return
            try:
                await interaction.guild.unban(user)
                await interaction.response.send_message(f"Unbanned {user} ({user.id}).")
            except Exception as e:
                await interaction.response.send_message(f"Failed to unban: {e}", **_no_perm())

@bot.tree.command(name="softban", description="Softban = ban+unban to clear messages")
@app_commands.describe(member="Member to softban", reason="Reason (optional)")
async def softban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("You don't have permission to softban.", **_no_perm())
                return
            try:
                await interaction.guild.ban(member, reason=reason, delete_message_days=1)
                await interaction.guild.unban(discord.Object(id=member.id))
                await interaction.response.send_message(f"Softbanned {member}.")
            except Exception as e:
                await interaction.response.send_message(f"Failed: {e}", **_no_perm())

@bot.tree.command(name="purge", description="Delete recent messages (number)")
@app_commands.describe(limit="Number of messages to delete (default 10)")
async def purge(interaction: discord.Interaction, limit: int = 10):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("No permission to manage messages.", **_no_perm())
                return
            try:
                await interaction.response.send_message(f"Deleting {limit} messages...", ephemeral=True)
                channel = interaction.channel
                # some channel types may not support purge; try best-effort
                deleted = []
                try:
                    deleted = await channel.purge(limit=limit)  # type: ignore
                except Exception:
                    # fallback: manual bulk delete using history
                    msgs = [m async for m in channel.history(limit=limit)]
                    await channel.delete_messages(msgs)
                    deleted = msgs
                await interaction.followup.send(f"Deleted {len(deleted)} messages.")
            except Exception as e:
                await interaction.response.send_message(f"Failed: {e}", **_no_perm())

@bot.tree.command(name="nick", description="Change a member's nickname")
@app_commands.describe(member="Member", nickname="New nickname")
async def nick(interaction: discord.Interaction, member: discord.Member, *, nickname: Optional[str] = None):
            if not interaction.user.guild_permissions.manage_nicknames:
                await interaction.response.send_message("No permission to change nicknames.", **_no_perm())
                return
            try:
                await member.edit(nick=nickname)
                await interaction.response.send_message(f"Changed nickname for {member} to {nickname!s}.")
            except Exception as e:
                await interaction.response.send_message(f"Failed: {e}", **_no_perm())

@bot.tree.command(name="addrole", description="Add a role to a user")
@app_commands.describe(member="Member", role="Role to add")
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
            if not interaction.user.guild_permissions.manage_roles:
                await interaction.response.send_message("No permission to manage roles.", **_no_perm())
                return
            try:
                await member.add_roles(role)
                await interaction.response.send_message(f"Added {role.name} to {member}.")
            except Exception as e:
                await interaction.response.send_message(f"Failed: {e}", **_no_perm())

@bot.tree.command(name="removerole", description="Remove a role from a user")
@app_commands.describe(member="Member", role="Role to remove")
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
            if not interaction.user.guild_permissions.manage_roles:
                await interaction.response.send_message("No permission to manage roles.", **_no_perm())
                return
            try:
                await member.remove_roles(role)
                await interaction.response.send_message(f"Removed {role.name} from {member}.")
            except Exception as e:
                await interaction.response.send_message(f"Failed: {e}", **_no_perm())

@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="Member to warn", reason="Reason")
async def warn(interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message("No permission to warn.", **_no_perm())
                return
            gw = _get_guild_warns(interaction.guild.id)
            gw.setdefault(member.id, []).append(reason)
            await interaction.response.send_message(f"Warned {member}. Reason: {reason}")

@bot.tree.command(name="warnings", description="Show warnings for a user")
@app_commands.describe(member="Member (optional)")
async def warnings(interaction: discord.Interaction, member: Optional[discord.Member] = None):
            member = member or interaction.user
            gw = _get_guild_warns(interaction.guild.id)
            user_warns = gw.get(getattr(member, "id", None), [])
            if not user_warns:
                await interaction.response.send_message(f"{member} has no warnings.")
            else:
                text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(user_warns))
                await interaction.response.send_message(f"Warnings for {member}:\n{text}")

@bot.tree.command(name="clearwarns", description="Clear warnings for a user")
@app_commands.describe(member="Member to clear warnings for")
async def clearwarns(interaction: discord.Interaction, member: discord.Member):
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message("No permission to clear warnings.", **_no_perm())
                return
            gw = _get_guild_warns(interaction.guild.id)
            gw.pop(member.id, None)
            await interaction.response.send_message(f"Cleared warnings for {member}.")

@bot.tree.command(name="announce", description="Make an announcement in this channel")
@app_commands.describe(message="Message to announce")
async def announce(interaction: discord.Interaction, message: str):
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("No permission to announce.", **_no_perm())
                return
            await interaction.response.send_message(f"📢 Announcement:\n{message}")

@bot.tree.command(name="dm", description="DM a user (mod use only)")
@app_commands.describe(user="User to DM", message="Message content")
async def dm(interaction: discord.Interaction, user: discord.User, message: str):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("No permission to DM as bot.", **_no_perm())
                return
            try:
                await user.send(message)
                await interaction.response.send_message(f"Sent DM to {user}.")
            except Exception as e:
                await interaction.response.send_message(f"Failed to DM: {e}", **_no_perm())

@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.describe(message="Message to send")
async def say(interaction: discord.Interaction, message: str):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("No permission to use say.", **_no_perm())
                return
            await interaction.response.send_message(message)

        # ---------------------------
        # Channel controls
        # ---------------------------
@bot.tree.command(name="lock", description="Lock the current channel (remove send messages)")
async def lock(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("No permission to manage channels.", **_no_perm())
                return
            ch = interaction.channel
            await ch.set_permissions(interaction.guild.default_role, send_messages=False)
            await interaction.response.send_message("Channel locked.")

@bot.tree.command(name="unlock", description="Unlock the current channel")
async def unlock(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("No permission to manage channels.", **_no_perm())
                return
            ch = interaction.channel
            await ch.set_permissions(interaction.guild.default_role, send_messages=True)
            await interaction.response.send_message("Channel unlocked.")

@bot.tree.command(name="slowmode", description="Set channel slowmode (seconds)")
@app_commands.describe(seconds="Slowmode seconds")
async def slowmode(interaction: discord.Interaction, seconds: int = 0):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("No permission to manage channels.", **_no_perm())
                return
            await interaction.channel.edit(slowmode_delay=seconds)
            await interaction.response.send_message(f"Set slowmode to {seconds}s.")

        # ---------------------------
        # Text transforms & small fun
        # ---------------------------
@bot.tree.command(name="mewmew", description="Mew-mew text")
async def mewmew(interaction: discord.Interaction, *, text: str):
            out = "".join(ch + "w" if ch.isalpha() else ch for ch in text)
            await interaction.response.send_message(out)

@bot.tree.command(name="emojify", description="Turn text into regional indicator emojis")
async def emojify(interaction: discord.Interaction, *, text: str):
            mapping = {c: f":regional_indicator_{c}:" for c in "abcdefghijklmnopqrstuvwxyz"}
            out = " ".join(mapping.get(c.lower(), c) for c in text)
            await interaction.response.send_message(out)

@bot.tree.command(name="spoiler", description="Wrap text in spoiler tags")
async def spoiler(interaction: discord.Interaction, *, text: str):
            await interaction.response.send_message("||" + text + "||")

@bot.tree.command(name="reverse", description="Reverse text")
async def reverse(interaction: discord.Interaction, *, text: str):
            await interaction.response.send_message(text[::-1])

@bot.tree.command(name="mock", description="Mock text (sPoNgEbOb case)")
async def mock(interaction: discord.Interaction, *, text: str):
            out = "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
            await interaction.response.send_message(out)

@bot.tree.command(name="vaporwave", description="Vaporwave text")
async def vaporwave(interaction: discord.Interaction, *, text: str):
            wide = "".join(chr(ord(c) + 0xFEE0) if 33 <= ord(c) <= 126 else c for c in text)
            await interaction.response.send_message(wide)

@bot.tree.command(name="binary", description="Text -> binary")
async def binary(interaction: discord.Interaction, *, text: str):
            out = " ".join(format(ord(c), "08b") for c in text)
            await interaction.response.send_message(out)

@bot.tree.command(name="morse", description="Text -> morse (simple)")
async def morse(interaction: discord.Interaction, *, text: str):
            table = {
                "a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".",
                "f": "..-.", "g": "--.", "h": "....", "i": "..", "j": ".---",
                "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---",
                "p": ".--.", "q": "--.-", "r": ".-.", "s": "...", "t": "-",
                "u": "..-", "v": "...-", "w": ".--", "x": "-..-", "y": "-.--",
                "z": "--..", " ": "/"
            }
            out = " ".join(table.get(c.lower(), "?") for c in text)
            await interaction.response.send_message(out)

@bot.tree.command(name="piglatin", description="Convert text to pig latin")
async def piglatin(interaction: discord.Interaction, *, text: str):
            def pl(word):
                vowels = "aeiou"
                if not word:
                    return word
                if word[0].lower() in vowels:
                    return word + "way"
                for i, ch in enumerate(word):
                    if ch.lower() in vowels:
                        return word[i:] + word[:i] + "ay"
                return word + "ay"
            out = " ".join(pl(w) for w in text.split())
            await interaction.response.send_message(out)

@bot.tree.command(name="advice", description="Get a random piece of advice")
async def advice(interaction: discord.Interaction):
            adv = [
                "Trust the process.", "Break big tasks into small steps.", "Drink water.",
                "Ask questions — curiosity scales fast."
            ]
            await interaction.response.send_message(random.choice(adv))

@bot.tree.command(name="truth", description="Get a truth prompt")
async def truth(interaction: discord.Interaction):
            choices = [
                "What's a small secret you've never told?", "What's your biggest goal right now?"
            ]
            await interaction.response.send_message(random.choice(choices))

@bot.tree.command(name="dare", description="Get a dare prompt")
async def dare(interaction: discord.Interaction):
            choices = [
                "Send a funny selfie to a friend.", "Use only emojis for 5 minutes in chat."
            ]
            await interaction.response.send_message(random.choice(choices))

@bot.tree.command(name="joke", description="Tell a joke")
async def joke(interaction: discord.Interaction):
            jokes = [
                "Why did the scarecrow win an award? He was outstanding in his field.",
                "I told my computer I needed a break, it said 'No problem — I'll go to sleep.'"
            ]
            await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name="iq", description="Roll an IQ score (for fun)")
@app_commands.describe(who="User (optional)")
async def iq(interaction: discord.Interaction, who: Optional[discord.User] = None):
            who = who or interaction.user
            score = random.randint(70, 160)
            await interaction.response.send_message(f"{who} has an IQ of {score} (totally for fun).")

        # ---------------------------
        # Reminder (background task inside bot; note: bot must remain online)
        # ---------------------------
@bot.tree.command(name="remindme", description="Set a reminder (seconds) — bot must remain online")
@app_commands.describe(seconds="Seconds until reminder", message="Reminder message")
async def remindme(interaction: discord.Interaction, seconds: int, *, message: str):
            await interaction.response.send_message(f"Okay! I will remind you in {seconds} seconds (if I'm online).", ephemeral=True)

            async def _reminder():
                try:
                    await asyncio.sleep(max(1, seconds))
                    await interaction.user.send(f"🔔 Reminder: {message}")
                except Exception:
                    pass

            try:
                asyncio.create_task(_reminder())
            except Exception:
                pass

        # ---------------------------
# Global sync command with admin check
        # ---------------------------
@bot.tree.command(name="sync", description="🌍 Sync all slash commands globally.")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            loading_steps = [
                "🔄 Initializing sync module...",
                "📡 Connecting to Discord API...",
                "🌍 Pushing global commands...",
                "⚡ Finalizing deployment...",
                "✅ Sync complete!"
            ]
            message = await interaction.followup.send("🚀 Starting global sync...")
            for step in loading_steps:
                await asyncio.sleep(1.2)
                await message.edit(content=step)

            try:
                synced = await bot.tree.sync()  # Global sync
                embed = discord.Embed(
                    title="🌍 Global Sync Successful!",
                    description=f"✨ **{len(synced)} commands** synced globally.\n\n⚠️ Global sync may take up to **1 hour** to fully update everywhere.",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Anna Guardian System 🌟")
                await message.edit(content="", embed=embed)
            except Exception as e:
                await message.edit(content=f"❌ Sync failed:\n```{e}```")

# Global app-command error handler
@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            # Missing perms from checks
            if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.CheckFailure):
                try:
                    await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
                except Exception:
                    pass
                return
            # Other errors
            try:
                await interaction.response.send_message(f"An error occurred: `{error}`", ephemeral=True)
            except Exception:
                pass

# ---------------------------
# Small convenience command to show there is more
@bot.tree.command(name="advice_short", description="Short advice")
async def advice_short(interaction: discord.Interaction):
    await interaction.response.send_message("Take one focused 25-minute session on something important today.")



# register done (functions decorated — nothing to return)
# (No explicit return necessary)

# ----- RUN BOT -----
bot.run(TOKEN)
