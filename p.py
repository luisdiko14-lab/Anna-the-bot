import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "MTM2MDMyOTgwOTY3MDA0NTczMQ.GLJsTj.DWHaO6L4NFviUTIMPgVHY9jxIH-hvHq8NF4yww"  # <-- put token here

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # IMPORTANT

bot = commands.Bot(command_prefix="!", intents=intents)


# ------------------ CONFIRM VIEW ------------------ #

class ConfirmDelete(discord.ui.View):
    def __init__(self, author: discord.Member, category_name: str, timeout=30):
        super().__init__(timeout=timeout)
        self.author = author
        self.category_name = category_name

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only command author can press buttons
        if interaction.user != self.author:
            await interaction.response.send_message(
                "You cannot use these buttons.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        matches = [
            c for c in guild.categories
            if c.name.lower() == self.category_name.lower()
        ]

        if not matches:
            await interaction.response.edit_message(
                content=f"❌ Category `{self.category_name}` not found.",
                view=None
            )
            return

        deleted = []
        for cat in matches:
            try:
                await cat.delete(reason=f"Deleted by {self.author}")
                deleted.append(cat.name)
            except:
                pass

        await interaction.response.edit_message(
            content=f"✅ Deleted {len(deleted)} category(s): {', '.join(deleted)}",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ Deletion cancelled.",
            view=None
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ------------------ COMMAND ------------------ #

@bot.command()
@commands.guild_only()
@commands.has_permissions(manage_channels=True)
async def deleteCategory(ctx, *, name: str):
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ I need **Manage Channels** permission.")
        return

    matches = [
        c for c in ctx.guild.categories
        if c.name.lower() == name.lower()
    ]

    if not matches:
        await ctx.send(f"❌ No category named `{name}` found.")
        return

    view = ConfirmDelete(ctx.author, name)

    await ctx.send(
        f"⚠️ Are you sure you want to delete category `{name}`?\n"
        f"This cannot be undone.",
        view=view
    )


# ------------------ READY ------------------ #

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game("Managing Categories"))


# ------------------ ERROR HANDLER ------------------ #

@deleteCategory.error
async def delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need **Manage Channels** permission.")
    else:
        await ctx.send(f"⚠️ Error: {error}")


bot.run(TOKEN)
