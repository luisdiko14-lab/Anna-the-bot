import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import psutil
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# --- CONFIGURATION & SECURITY ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZED_USER = "luisthegoat7301"

if not TOKEN:
    print(
        "ERROR: Token not found! Make sure you have a .env file with DISCORD_TOKEN inside."
    )
    exit()

PREFIX = 'anna' , "!"

# --- SETUP ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# --- NATURE STATUS LOOP ---
nature_scenes = [
    "Pokemon! 🌲", "MEW! 🌅", "Flowing Rivers 🌊",
    "Pikachu 🏔️", "Starry Nights 🌌", "Blooming Pokemons 🌸",
    "Falling Rain 🌧️", "Mew is cool! i like it", "Just Got verifed! ✅"
]


@tasks.loop(seconds=5)
async def change_status():
    activity_name = random.choice(nature_scenes)
    activity = discord.Activity(type=discord.ActivityType.playing,
                                
                                name=activity_name)
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    print(f" Status has been changed to: {activity_name}")


@change_status.before_loop
async def before_status():
    await bot.wait_until_ready()


# --- EVENTS ---
@bot.event
async def on_ready():
    print("==========================")
    print(f"✅ Logged in as {bot.user.name} - ID: {bot.user.id}")
    print("==========================")
    print("✅ Connected to Discord!")
    print("==========================")
    print(f"📡 Ping: {round(bot.latency * 1000)}ms")
    print("==========================")

    change_status.start()




# --- ERROR HANDLING ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "⛔ **Access Denied:** You do not have the required permissions.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ **Missing Argument:** Check command usage.")
    else:
        print(f"Error: {error}")


# --- COMMAND LOGGING ---
@bot.before_invoke
async def log_command_usage(ctx):
    """Logs every command used by Discord users"""
    print(
        f"{ctx.author} used {ctx.command.name} in {ctx.channel.name} or {ctx.channel.id} in the server {ctx.guild.name} , server id: {ctx.guild.id} with the permission adminstrator: {ctx.author.guild_permissions.administrator}"
    )


# ==============================================================================
# NEW SECTION: BOT CONTROL COMMANDS
# ==============================================================================


@bot.command()
async def start(ctx):
    """Starts/Signals the bot is active"""
    await ctx.send("🌲 **AnnaBot is online and patrolling the forest!**")
    message = (
        "*turning on @Anna-the-Guardian*\n"
        "please wait! (connection speed: Medium Fast) Upgrade to premium for Ultra Fast speed. 100 mbs per second/ 100000gbs\n"
        "Connecting to Discord api services! ...\n"
        f"{bot.user.name} is connecting to the gateway ip : {bot.user.id}\n"
        "Launching….\n"
        "RAM: 86 GBS\n"
        "CPU: AMD Ryzen Threadripper 7980X / PRO 7995WX 96 Cores\n"
        "SYSTEM: Windows 11 Server 2025\n"
        "INSTALLING PACKAGES :loading_w:  …\n"
        "INSTALLING DISCORD.PY , PYTHON-DOTENV , SYNC, OS, INFO\n"
        "SUCSESFULLY INSTALLED!\n"
        "RUNNING: cd A:/Bot/Python-Bot/Anna/Visual-Studio-Code/py\n"
        "RUNNING: Python bot.\n"
        "— 08/01/2026, 16:49\n"
        "Error: Exit code with process 1\n"
        "/fix\n"
        "RUN_DEBUG= bot.py/anna\n"
        "SUCSESFULLY LAUNCHED!\n"
        "🟢 <@1360329809670045731> is online! 🟢")
    await ctx.send(message)


@bot.command()
async def shutdown(ctx):
    """Exits the python code entirely"""
    if str(ctx.author) != AUTHORIZED_USER:
        return await ctx.send("⛔ Only Luisthegoat7301 can shut me down.")
    await ctx.send("💤 Powering down... Goodbye.")
    print('==========================')
    print("bot is shutting down..")
    print('==========================')
    await bot.close()
    sys.exit()


@bot.command()
async def restart(ctx):
    """Pretends to restart with status changes"""
    if str(ctx.author) != AUTHORIZED_USER:
        return await ctx.send("⛔ Unauthorized.")
    change_status.stop()
    await bot.change_presence(status=discord.Status.invisible)
    msg = await ctx.send("🔄 **Restarting systems...**")
    await asyncio.sleep(5)
    await msg.edit(content="✅ **Systems rebooted.** Reconnecting to nature...")
    change_status.start()


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
        change_status.stop(
        )  # Stop loop so it doesn't overwrite your manual choice
        await bot.change_presence(status=choice)
        await ctx.send(f"✅ Status updated to **{status_name}**.")
    else:
        await ctx.send("❌ Valid: online, idle, dnd, invisible")


@bot.command()
async def changePresence(ctx, p_type: str, *, text: str):
    """Example: !changePresence watching YouTube"""
    type_map = {
        "playing": discord.ActivityType.playing,
        "watching": discord.ActivityType.watching,
        "listening": discord.ActivityType.listening,
        "streaming": discord.ActivityType.streaming
    }
    act_type = type_map.get(p_type.lower())
    if act_type:
        change_status.stop()
        await bot.change_presence(
            activity=discord.Activity(type=act_type, name=text))
        await ctx.send(f"✅ Now {p_type} **{text}**.")
    else:
        await ctx.send("❌ Valid: playing, watching, listening, streaming")


@bot.command()
async def makerole(ctx, perm: str, *, name: str):
    """Owner command to create roles with perms"""
    if str(ctx.author) != AUTHORIZED_USER:
        return await ctx.send("⛔ Luisthegoat7301 access only.")

    perms = discord.Permissions.none()
    p = perm.lower()
    if p == "admin": perms = discord.Permissions(administrator=True)
    elif p == "ban": perms = discord.Permissions(ban_members=True)
    elif p == "kick": perms = discord.Permissions(kick_members=True)

    try:
        role = await ctx.guild.create_role(name=name,
                                           permissions=perms,
                                           color=discord.Color.random(),
                                           hoist=True)
        await ctx.send(
            f"✅ Created role **{role.name}** with **{p}** permissions!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


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
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Info",
                          color=discord.Color.blue())
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Members", value=guild.member_count)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


from discord import ui


class UserInfoView(ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.member = member

    @ui.button(label="Is User Owner?", style=discord.ButtonStyle.primary)
    async def owner_button(self, interaction: discord.Interaction, button:ui.Button):
        is_owner = "Yes 👑" if self.member.id == interaction.guild.owner_id else "No ❌"
        message = f"👤 User===={self.member}\n👑 Is Owner===={is_owner}"
        await interaction.response.send_message(message, ephemeral=True)

    @ui.button(label="Show All Roles", style=discord.ButtonStyle.secondary)
    async def roles_button(self, interaction: discord.Interaction, button: ui.Button):
        roles = [role.mention for role in self.member.roles if role.name != "@everyone"]
        roles_text = ", ".join(roles) if roles else "None"
        message = f"👤 User===={self.member}\n🎭 Roles ({len(roles)})===={roles_text}"
        await interaction.response.send_message(message, ephemeral=True)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author

    # Permissions
    perms = [perm.replace("_", " ").title() for perm, value in member.guild_permissions if value]
    perms_text = ", ".join(perms[:10]) + ("..." if len(perms) > 10 else "")

    message = f"""👤 User===={member}
🆔 ID===={member.id}
📅 Account Created====<t:{int(member.created_at.timestamp())}:F>
🚪 Joined Server====<t:{int(member.joined_at.timestamp())}:F>
🔐 Key Permissions===={perms_text or "None"}"""

    view = UserInfoView(member)
    await ctx.send(message, view=view)


@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar")
    embed.set_image(
        url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)


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
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    new = await ctx.channel.clone()
    await ctx.channel.delete()
    await new.send("💥 **Channel Nuked.**")


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


# --- RUN ---
bot.run(TOKEN)
