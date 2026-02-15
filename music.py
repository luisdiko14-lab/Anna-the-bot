# bot.py
import os
import asyncio
import random
from dataclasses import dataclass
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import yt_dlp
from aiohttp import web

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SUPPORT_SERVER = os.getenv("SUPPORT_SERVER", "https://discord.gg/")

if not TOKEN:
    raise SystemExit("Please set DISCORD_BOT_TOKEN in your .env")

INTENTS = discord.Intents.default()
INTENTS.message_content = False
INTENTS.guilds = True
INTENTS.voice_states = True
INTENTS.members = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ----- YTDL -----
YTDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "forceduration": True,
    "simulate": False,
    "noplaylist": True
}
ytdl = yt_dlp.YoutubeDL(YTDL_OPTS)

FFMPEG_OPTIONS = (
    "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -vn"
)

@dataclass
class Song:
    title: str
    webpage_url: str
    stream_url: str
    duration: Optional[int]  # seconds
    requester: discord.Member

class GuildState:
    def __init__(self):
        self.queue: List[Song] = []
        self.current: Optional[Song] = None
        self.volume: float = 0.25  # 25%
        self.loop_track: bool = False
        self.loop_queue: bool = False
        self.twentyfourseven: bool = False
        self.manual_stop: bool = False
        self.current_msg: Optional[discord.Message] = None

GUILDS = {}  # guild_id -> GuildState

# ---------- aiohttp heartbeat ----------
async def _root(request):
    return web.Response(text="Discord Music Bot is running!")

async def start_webserver():
    app = web.Application()
    app.add_routes([web.get("/", _root)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    await site.start()
    print("Webserver started on port 3000")


# ---------- helpers ----------
def guild_state(guild_id: int) -> GuildState:
    return GUILDS.setdefault(guild_id, GuildState())

async def extract_info(query: str):
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
    except Exception as e:
        raise e

    # If it's a playlist or a search result we may get 'entries'
    if "entries" in data:
        # take first entry
        entry = data["entries"][0]
        return entry
    return data

def make_embed_nowplaying(song: Song):
    dur = "Unknown"
    if song.duration:
        m, s = divmod(song.duration, 60)
        dur = f"{m}:{str(s).zfill(2)}"
    embed = discord.Embed(title="🎵 Now Playing",
                          description=f"[{song.title}]({song.webpage_url})",
                          color=0xFF0000)
    embed.add_field(name="👤 Requested by", value=str(song.requester), inline=True)
    embed.add_field(name="⏱️ Duration", value=dur, inline=True)
    return embed

def make_embed_queue(gs: GuildState):
    if not gs.queue and not gs.current:
        return discord.Embed(description="No songs in queue.", color=0xFF0000)

    lines = []
    for i, s in enumerate(gs.queue[:20]):
        lines.append(f"{i+1}. [{s.title}]({s.webpage_url}) — {s.requester.display_name}")
    desc = "\n".join(lines) if lines else "No songs in queue."
    if gs.current:
        desc = f"**Now Playing:**\n[{gs.current.title}]({gs.current.webpage_url})\n\n**Queue:**\n{desc}"
    embed = discord.Embed(title="🎵 Queue", description=desc, color=0xFF0000)
    return embed

def create_controls_view(guild_id: int):
    class ControlsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.response.send_message("You must be in a voice channel to use controls.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Pause/Resume", style=discord.ButtonStyle.primary, custom_id=f"pause-{guild_id}")
        async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
            vc = interaction.guild.voice_client
            if not vc or not vc.is_connected():
                await interaction.response.send_message("Bot is not connected.", ephemeral=True); return
            if vc.is_paused():
                vc.resume()
                await interaction.response.send_message("▶️ Resumed", ephemeral=True)
            else:
                vc.pause()
                await interaction.response.send_message("⏸️ Paused", ephemeral=True)

        @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, custom_id=f"skip-{guild_id}")
        async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
            vc = interaction.guild.voice_client
            if not vc or not vc.is_connected():
                await interaction.response.send_message("Nothing is playing.", ephemeral=True); return
            vc.stop()  # triggers after callback -> plays next
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)

        @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, custom_id=f"stop-{guild_id}")
        async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
            vc = interaction.guild.voice_client
            gs = guild_state(interaction.guild.id)
            gs.manual_stop = True
            gs.queue.clear()
            if vc and vc.is_connected():
                await vc.disconnect()
            await interaction.response.send_message("⏹️ Stopped and left voice channel", ephemeral=True)

        @discord.ui.button(label="Loop", style=discord.ButtonStyle.secondary, custom_id=f"loop-{guild_id}")
        async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
            gs = guild_state(interaction.guild.id)
            gs.loop_queue = not gs.loop_queue
            await interaction.response.send_message(f"🔁 Loop queue: {'Enabled' if gs.loop_queue else 'Disabled'}", ephemeral=True)

        @discord.ui.button(label="Queue", style=discord.ButtonStyle.secondary, custom_id=f"queue-{guild_id}")
        async def queue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
            gs = guild_state(interaction.guild.id)
            embed = make_embed_queue(gs)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    return ControlsView()

# ---------- playback flow ----------
async def play_next_in_guild(guild: discord.Guild):
    gs = guild_state(guild.id)
    vc = guild.voice_client
    if not vc or not vc.is_connected():
        return

    # Loop track
    if gs.loop_track and gs.current:
        # replay the current
        song = gs.current
    else:
        if not gs.queue:
            # nothing left
            if not gs.twentyfourseven:
                # disconnect
                await vc.disconnect()
            gs.current = None
            return
        # take next
        song = gs.queue.pop(0)
        gs.current = song

    # create source and play
    try:
        ffmpeg_opts = FFMPEG_OPTIONS.split()
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, executable="ffmpeg", options=FFMPEG_OPTIONS),
            volume=gs.volume
        )
        def after_playing(err):
            if err:
                print("Player after error:", err)
            # schedule coroutine to continue playback
            coro = play_next_in_guild(guild)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except Exception as e:
                print("Error scheduling next track:", e)

        vc.play(source, after=after_playing)

        # send/update now playing embed + controls
        try:
            embed = make_embed_nowplaying(song)
            view = create_controls_view(guild.id)
            if gs.current_msg and not gs.current_msg.deleted:
                await gs.current_msg.edit(embed=embed, view=view)
            else:
                gs.current_msg = await guild.text_channels[0].send(embed=embed, view=view)
        except Exception:
            # fall back to sending to the default text channel
            pass

    except Exception as e:
        print("Error playing track:", e)
        # try next
        await play_next_in_guild(guild)

# ---------- slash commands ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    # start heartbeat webserver
    bot.loop.create_task(start_webserver())
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Failed to sync commands:", e)

# Play command (slash)
@bot.tree.command(name="play", description="Plays a song")
@app_commands.describe(query="Song name or URL")
async def slash_play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("Join a voice channel first!", ephemeral=True); return

    # ensure voice connection
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        vc = await channel.connect()

    # extract track info
    try:
        info = await extract_info(query)
    except Exception:
        await interaction.followup.send("Failed to fetch track. Try a different link or search.", ephemeral=True)
        return

    # yt-dlp may give a direct url in 'url' or 'formats'
    stream_url = info.get("url") or info.get("formats", [{}])[-1].get("url")
    title = info.get("title", "Unknown title")
    webpage = info.get("webpage_url", info.get("webpage_url") or query)
    duration = info.get("duration")

    song = Song(title=title, webpage_url=webpage, stream_url=stream_url, duration=duration, requester=interaction.user)

    gs = guild_state(interaction.guild.id)
    if vc.is_playing() or vc.is_paused() or gs.current:
        gs.queue.append(song)
        embed = discord.Embed(description=f"Added [{title}]({webpage}) to the queue", color=0xFF0000)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)
    else:
        gs.current = song
        # start playing immediately
        await interaction.followup.send("Now playing...", ephemeral=True)
        await play_next_in_guild(interaction.guild)

@bot.tree.command(name="pause", description="Pause the current song")
async def slash_pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Not playing anything!", ephemeral=True); return
    vc.pause()
    await interaction.response.send_message("⏸️ Paused")

@bot.tree.command(name="resume", description="Resume the current song")
async def slash_resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Not playing anything!", ephemeral=True); return
    vc.resume()
    await interaction.response.send_message("▶️ Resumed")

@bot.tree.command(name="skip", description="Skip to the next song")
async def slash_skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc:
        await interaction.response.send_message("Not playing anything!", ephemeral=True); return
    vc.stop()
    await interaction.response.send_message("⏭️ Skipped")

@bot.tree.command(name="queue", description="Show the current queue")
async def slash_queue(interaction: discord.Interaction):
    gs = guild_state(interaction.guild.id)
    embed = make_embed_queue(gs)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nowplaying", description="Show currently playing song")
async def slash_nowplaying(interaction: discord.Interaction):
    gs = guild_state(interaction.guild.id)
    if not gs.current:
        await interaction.response.send_message("Not playing anything!", ephemeral=True); return
    embed = make_embed_nowplaying(gs.current)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="shuffle", description="Shuffle the queue")
async def slash_shuffle(interaction: discord.Interaction):
    gs = guild_state(interaction.guild.id)
    random.shuffle(gs.queue)
    await interaction.response.send_message("🔀 Shuffled the queue")

@bot.tree.command(name="loop", description="Toggle loop mode")
@app_commands.describe(mode="Loop mode (off|track|queue)")
async def slash_loop(interaction: discord.Interaction, mode: str):
    gs = guild_state(interaction.guild.id)
    mode = mode.lower()
    if mode == "off":
        gs.loop_track = False; gs.loop_queue = False
    elif mode == "track":
        gs.loop_track = True; gs.loop_queue = False
    elif mode == "queue":
        gs.loop_track = False; gs.loop_queue = True
    else:
        await interaction.response.send_message("Choose off, track, or queue", ephemeral=True); return
    await interaction.response.send_message(f"🔄 Loop mode set to: {mode}")

@bot.tree.command(name="remove", description="Remove a song from the queue")
@app_commands.describe(position="Position in queue (1-based)")
async def slash_remove(interaction: discord.Interaction, position: int):
    gs = guild_state(interaction.guild.id)
    idx = position - 1
    if idx < 0 or idx >= len(gs.queue):
        await interaction.response.send_message("Invalid position!", ephemeral=True); return
    removed = gs.queue.pop(idx)
    await interaction.response.send_message(f"❌ Removed [{removed.title}]({removed.webpage_url})")

@bot.tree.command(name="move", description="Move a song to a different position")
@app_commands.describe(from_pos="From position", to_pos="To position")
async def slash_move(interaction: discord.Interaction, from_pos: int, to_pos: int):
    gs = guild_state(interaction.guild.id)
    f, t = from_pos - 1, to_pos - 1
    if f < 0 or f >= len(gs.queue) or t < 0 or t >= len(gs.queue):
        await interaction.response.send_message("Invalid position!", ephemeral=True); return
    track = gs.queue.pop(f)
    gs.queue.insert(t, track)
    await interaction.response.send_message(f"📦 Moved [{track.title}] to position {to_pos}")

@bot.tree.command(name="clearqueue", description="Clear the queue")
async def slash_clearqueue(interaction: discord.Interaction):
    gs = guild_state(interaction.guild.id)
    gs.queue.clear()
    await interaction.response.send_message("🗑️ Cleared the queue")

@bot.tree.command(name="stop", description="Stops the music and leaves")
async def slash_stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    gs = guild_state(interaction.guild.id)
    if vc:
        gs.manual_stop = True
        gs.queue.clear()
        await vc.disconnect()
        await interaction.response.send_message("⏹️ Stopped and left voice channel")
    else:
        await interaction.response.send_message("Not playing anything!", ephemeral=True)

@bot.tree.command(name="volume", description="Set the volume")
@app_commands.describe(level="Volume level (0-100)")
async def slash_volume(interaction: discord.Interaction, level: int):
    gs = guild_state(interaction.guild.id)
    if level < 0 or level > 100:
        await interaction.response.send_message("Volume must be 0-100", ephemeral=True); return
    gs.volume = level / 100.0
    # update current playing source volume (if any)
    vc = interaction.guild.voice_client
    if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
        vc.source.volume = gs.volume
    await interaction.response.send_message(f"🔊 Volume set to {level}%")

@bot.tree.command(name="247", description="Toggle 24/7 mode")
async def slash_247(interaction: discord.Interaction):
    gs = guild_state(interaction.guild.id)
    gs.twentyfourseven = not gs.twentyfourseven
    await interaction.response.send_message(f"🎵 24/7 mode {'enabled' if gs.twentyfourseven else 'disabled'}")

@bot.tree.command(name="help", description="Shows all commands")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title=f"🎵 {bot.user.name} Commands", color=0xFF0000)
    embed.add_field(name="Music", value="`/play` `/pause` `/resume` `/stop` `/skip` `/volume`", inline=False)
    embed.add_field(name="Queue", value="`/queue` `/nowplaying` `/shuffle` `/loop` `/remove` `/move`", inline=False)
    embed.add_field(name="Utility", value="`/247` `/ping` `/stats` `/invite` `/support`", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="invite", description="Get bot invite link")
async def slash_invite(interaction: discord.Interaction):
    perms = discord.Permissions(permissions=8)
    invite = discord.utils.oauth_url(bot.user.id, permissions=perms, scopes=("bot", "applications.commands"))
    embed = discord.Embed(title="📨 Invite Me", description=f"[Click here to invite me]({invite})", color=0xFF0000)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Shows bot ping")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency*1000)}ms")

@bot.tree.command(name="stats", description="Shows bot statistics")
async def slash_stats(interaction: discord.Interaction):
    # basic stats
    total_guilds = len(bot.guilds)
    total_users_cached = len(bot.users)
    active_players = sum(1 for gs in GUILDS.values() if gs.current)
    embed = discord.Embed(title="📊 Bot Statistics", color=0xFF0000)
    embed.add_field(name="🌐 Servers", value=str(total_guilds), inline=True)
    embed.add_field(name="👥 Users (cached)", value=str(total_users_cached), inline=True)
    embed.add_field(name="🎵 Active Players", value=str(active_players), inline=True)
    embed.add_field(name="📡 Ping", value=f"{round(bot.latency*1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="support", description="Join our support server")
async def slash_support(interaction: discord.Interaction):
    embed = discord.Embed(title="💬 Support Server", description=f"[Click here]({SUPPORT_SERVER})", color=0xFF0000)
    await interaction.response.send_message(embed=embed)

# ---------- run ----------
if __name__ == "__main__":
    bot.run(TOKEN)
