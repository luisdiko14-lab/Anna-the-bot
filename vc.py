import discord
from discord.ext import commands

# ---------- CONFIG ----------
TOKEN = "MTM2MDMyOTgwOTY3MDA0NTczMQ.GLJsTj.DWHaO6L4NFviUTIMPgVHY9jxIH-hvHq8NF4yww"
INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.voice_states = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)

# Tracks which user the bot is following (so it stays until that user leaves)
_following_user_id = None
_following_channel_id = None

# Path to your hello sound file (download from one of the suggested sources)
HELLO_FILE = "hello.mp3"  # or "hello.wav"

# ---------- HELPERS ----------
def is_user_join(after, before):
    """Return True when a real user joined a voice channel (not moved)."""
    return (before.channel is None) and (after.channel is not None)

def user_left_channel(before, after, tracked_user_id, tracked_channel_id):
    """Return True when tracked user left the tracked channel or disconnected."""
    if tracked_user_id is None or tracked_channel_id is None:
        return False
    # If before.channel was tracked and after.channel is None (disconnected) OR moved to a different channel
    return (before.channel is not None and before.channel.id == tracked_channel_id and
           (after.channel is None or (after.channel is not None and after.channel.id != tracked_channel_id))
    )

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Ready — listening for voice joins...")

@bot.event
async def on_voice_state_update(member, before, after):
    global _following_user_id, _following_channel_id

    # ignore bots (including our bot)
    if member.bot:
        return

    # 1) a user joined a voice channel -> bot should join and say hello (if not already in a VC)
    if is_user_join(after, before):
        join_channel = after.channel

        # If bot is not connected anywhere, connect to that channel
        if not bot.voice_clients:  # no voice clients connected
            try:
                voice_client = await join_channel.connect(timeout=20)
            except Exception as e:
                print(f"Failed to connect to VC: {e}")
                return

            # play hello file
            try:
                source = discord.FFmpegPCMAudio(HELLO_FILE)
                voice_client.play(source)
            except Exception as e:
                print(f"Failed to play audio: {e}")

            # start following this user until they leave
            _following_user_id = member.id
            _following_channel_id = join_channel.id
            print(f"Joined {join_channel} to greet {member}. Tracking user id {_following_user_id}")

        else:
            # bot already connected somewhere.
            # If the bot is in the same channel, just optionally play hello for this user
            for vc in bot.voice_clients:
                if vc.channel.id == join_channel.id:
                    try:
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(HELLO_FILE))
                    except Exception as e:
                        print(f"Could not play in existing client: {e}")
                    # set following to this user (so bot will leave when they leave)
                    _following_user_id = member.id
                    _following_channel_id = join_channel.id
                    print(f"Already in channel — greeting {member} and tracking them.")
                    break
            # If bot is connected to other channel and you'd like it to move, implement that logic here.

    # 2) If the tracked user left the tracked channel -> bot should disconnect
    if user_left_channel(before, after, _following_user_id, _following_channel_id):
        # find voice client in that channel and disconnect
        for vc in bot.voice_clients:
            if vc.channel.id == _following_channel_id:
                try:
                    await vc.disconnect()
                    print(f"Tracked user {_following_user_id} left — disconnected from channel {_following_channel_id}")
                except Exception as e:
                    print(f"Error disconnecting: {e}")
                break

        # clear tracking
        _following_user_id = None
        _following_channel_id = None

# ---------- RUN ----------
if __name__ == "__main__":
    bot.run(TOKEN)
