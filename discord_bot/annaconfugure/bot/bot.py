import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import os
import sys
from datetime import timedelta
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

@bot.command()
async def start(ctx):
            """Signals bot is active"""
            await ctx.send("🌲 **AnnaBot is online and guarding the forest!**")

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

            await ctx.send(message)

        # --------------------------------------------------

@bot.command()
async def shutdown(ctx):
            """Shuts down the bot"""
            if str(ctx.author) not in AUTHORIZED_USERS:
                return await ctx.send("⛔ Only authorized developers can shut me down.")

            await ctx.send("💤 Powering down... Goodbye.")
            print("Bot shutting down...")
            await bot.close()
            sys.exit()

        # --------------------------------------------------

@bot.command()
async def restart(ctx):
            """Restarts the bot systems"""
            if str(ctx.author) not in AUTHORIZED_USERS:
                return await ctx.send("⛔ Unauthorized.")

            change_status.stop()
            await bot.change_presence(status=discord.Status.invisible)

            msg = await ctx.send("🔄 Restarting systems...")
            await asyncio.sleep(5)

            await msg.edit(content="✅ Systems rebooted successfully.")
            change_status.start()

        # --------------------------------------------------

@bot.command()
async def changeStatus(ctx, status_name: str):
            """Example: !changeStatus idle"""
            status_map = {
                "online": discord.Status.online,
                "idle": discord.Status.idle,
                "dnd": discord.Status.dnd,
                "invisible": discord.Status.invisible
            }

            choice = status_map.get(status_name.lower())

            if choice:
                change_status.stop()
                await bot.change_presence(status=choice)
                await ctx.send(f"✅ Status updated to **{status_name}**.")
            else:
                await ctx.send("❌ Valid options: online, idle, dnd, invisible")

        # --------------------------------------------------
@bot.command()
async def changePresence(ctx, p_type: str, status: str, *, text: str):
        # --- AUTH CHECK (like your other commands) ---
        if ctx.author.name not in AUTHORIZED_USERS:
            return await ctx.send("❌ You are not authorized to use this command.")

        type_map = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "streaming": discord.ActivityType.streaming
        }

        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }

        act_type = type_map.get(p_type.lower())
        new_status = status_map.get(status.lower())

        if not act_type:
            return await ctx.send("❌ Valid activity types: playing, watching, listening, streaming")

        if not new_status:
            return await ctx.send("❌ Valid statuses: online, idle, dnd, invisible")

        # If bot is in VC → force online
        if ctx.guild and ctx.guild.me.voice:
            new_status = discord.Status.online

        await bot.change_presence(
            status=new_status,
            activity=discord.Activity(type=act_type, name=text)
        )

        await ctx.send(f"✅ Presence updated: **{status}** | {p_type.title()} **{text}**")


        # --------------------------------------------------

@bot.command()
async def makerole(ctx, perm: str, *, name: str):
            """Create roles with permissions (Dev Only)"""

            if str(ctx.author) not in AUTHORIZED_USERS:
                return await ctx.send("⛔ Developer access only.")

            perms = discord.Permissions.none()
            p = perm.lower()

            if p == "admin":
                perms = discord.Permissions(administrator=True)
            elif p == "ban":
                perms = discord.Permissions(ban_members=True)
            elif p == "kick":
                perms = discord.Permissions(kick_members=True)
            elif p == "mod":
                perms = discord.Permissions(
                    manage_messages=True,
                    kick_members=True,
                    ban_members=True
                )

            try:
                role = await ctx.guild.create_role(
                    name=name,
                    permissions=perms,
                    color=discord.Color.random(),
                    hoist=True
                )

                await ctx.send(
                    f"✅ Created role **{role.name}** with **{p}** permissions!"
                )

            except Exception as e:
                await ctx.send(f"❌ Error creating role: {e}")

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
        "`ping`, `serverinfo`, `userinfo`, `avatar`, `uptime`, `invite`, `poll`, `8ball`, `roll`, `coinflip`, `slap`, `hug`, `pat`"
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
async def invite(ctx):
    await ctx.send(
        "Invite me: https://discord.com/oauth2/authorize?client_id=1360329809670045731&scope=identify+bot%20applications.commands&permissions=1099511627775&redirect_uri=https%3A%2F%2Fsites.google.com%2Fview%2Finfo-about-anna%2Fhome&response_type=code"
    )


@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Poll",
                          description=question,
                          color=discord.Color.gold())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


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




 


@bot.command()
async def pat(ctx, member: discord.Member):
    await ctx.send(f"**{ctx.author.name}** pats **{member.name}** on the head."
                   )


@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"😘 **{ctx.author.name}** kisses **{member.name}**!")


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


@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

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


# --- ADDITIONAL SLASH COMMANDS ---

# 1. Moderation
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ Banned **{member}** for: {reason}")

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for the kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ Kicked **{member}** for: {reason}")

@bot.tree.command(name="clear", description="Clear a number of messages")
@app_commands.describe(amount="Number of messages to clear")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_slash(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ Cleared **{len(deleted)}** messages.")

# 2. General
@bot.tree.command(name="server_info", description="Get information about the server")
async def server_info_slash(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Created At", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=False)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

# 3. Fun
@bot.tree.command(name="roll_dice", description="Roll a dice")
@app_commands.describe(sides="Number of sides (default 6)")
async def roll_slash(interaction: discord.Interaction, sides: int = 6):
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 Rolled a **{result}**!")

@bot.tree.command(name="random_joke", description="Get a funny joke")
async def joke_slash(interaction: discord.Interaction):
    jokes = [
        "Why did the bot cross the road? To get to the nature side!",
        "What do you call a fake noodle? An Impasta!",
        "Why don't scientists trust atoms? Because they make up everything!"
    ]
    await interaction.response.send_message(f"🤣 {random.choice(jokes)}")

# 4. Restart
@bot.tree.command(name="restart", description="Restarts the bot (Authorized users only)")
async def restart_slash(interaction: discord.Interaction):
    if str(interaction.user) != AUTHORIZED_USER:
        return await interaction.response.send_message("⛔ You are not authorized to restart me!", ephemeral=True)
    
    await interaction.response.send_message("🔄 Restarting... See you in a bit!")
    # Subprocess will handle the restart via ping.py
    os.execv(sys.executable, ['python'] + sys.argv)


# --- CONFIGURATION COMMANDS ---

@bot.tree.command(name="status", description="Change the bot's presence and status")
@app_commands.describe(
    activity_type="Type of activity (playing, watching, listening, competing)",
    status_text="The text for the activity",
    status_state="Online status (online, idle, dnd, invisible)"
)
async def status_slash(
    interaction: discord.Interaction, 
    activity_type: str, 
    status_text: str, 
    status_state: str = "online"
):
    if str(interaction.user) != AUTHORIZED_USER:
        return await interaction.response.send_message("⛔ You are not authorized to change my status!", ephemeral=True)

    # Activity Type Mapping
    activity_mapping = {
        "playing": discord.ActivityType.playing,
        "watching": discord.ActivityType.watching,
        "listening": discord.ActivityType.listening,
        "competing": discord.ActivityType.competing
    }
    
    # Status Mapping
    status_mapping = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.dnd,
        "invisible": discord.Status.invisible,
        "offline": discord.Status.invisible
    }

    act_type = activity_mapping.get(activity_type.lower())
    stat_state = status_mapping.get(status_state.lower())

    if not act_type:
        return await interaction.response.send_message("❌ Invalid activity type! Choose: playing, watching, listening, competing", ephemeral=True)
    if not stat_state:
        return await interaction.response.send_message("❌ Invalid status! Choose: online, idle, dnd, invisible", ephemeral=True)

    # Stop the auto-rotation loop to keep the manual status
    if change_status.is_running():
        change_status.stop()

    activity = discord.Activity(type=act_type, name=status_text)
    await bot.change_presence(status=stat_state, activity=activity)
    
    await interaction.response.send_message(f"✅ Status updated to **{activity_type.title()} {status_text}** ({status_state.title()})")

@bot.tree.command(name="auto_status", description="Resume automatic status rotation")
async def auto_status_slash(interaction: discord.Interaction):
    if str(interaction.user) != AUTHORIZED_USER:
        return await interaction.response.send_message("⛔ You are not authorized!", ephemeral=True)
    
    if not change_status.is_running():
        change_status.start()
        await interaction.response.send_message("✅ Automatic status rotation resumed!")
    else:
        await interaction.response.send_message("ℹ️ Automatic status rotation is already running.")


# --- RUN ---
bot.run(TOKEN)
