import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.prefix_manager import (
    get_prefixes,
    add_prefix,
    remove_prefix,
    reset_prefixes
)


# ------------------------------
# Modal for adding a prefix
# ------------------------------

class AddPrefixModal(discord.ui.Modal, title="Add Prefix"):
    prefix = discord.ui.TextInput(label="Prefix", max_length=10)

    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        add_prefix(self.guild_id, str(self.prefix))
        await interaction.response.edit_message(view=PrefixConfigPanel(self.guild_id))


# ------------------------------
# Remove prefix select menu
# ------------------------------

class RemovePrefixSelect(discord.ui.Select):
    def __init__(self, guild_id, message):
        self.message = message
        prefixes = get_prefixes(guild_id)
        options = [discord.SelectOption(label=p, value=p) for p in prefixes]

        super().__init__(
            placeholder="Select a prefix to remove",
            options=options
        )

        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        prefix = self.values[0]
        remove_prefix(self.guild_id, prefix)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_check')} Prefix Removed"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(content=f"Removed prefix: `{prefix}`"),
            accent_colour=discord.Color.green()
        )
        view.add_item(container)
        # we must edit the message passed in the constructor
        await self.message.edit(view=PrefixConfigPanel(self.guild_id))
        await interaction.response.edit_message(view=view)


# ------------------------------
# Buttons
# ------------------------------

class AddPrefixButton(discord.ui.Button):
    def __init__(self, guild_id):
        super().__init__(label="Add Prefix", style=discord.ButtonStyle.primary)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        await interaction.response.send_modal(AddPrefixModal(self.guild_id))


class RemovePrefixButton(discord.ui.Button):
    def __init__(self, guild_id):
        super().__init__(label="Remove Prefix", style=discord.ButtonStyle.secondary)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content="### Remove Prefix"),
            discord.ui.Separator(),
            discord.ui.ActionRow(RemovePrefixSelect(self.guild_id, interaction.message))
        )
        view.add_item(container)
        await interaction.response.send_message(view=view, ephemeral=True)


class ResetPrefixButton(discord.ui.Button):
    def __init__(self, guild_id):
        super().__init__(label="Reset Prefixes", style=discord.ButtonStyle.danger)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"### {get_emoji('icon_danger')} Error"
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content="You need the `manage_guild` permission to use this button."
                ),
                accent_colour=discord.Color.yellow()
            )
            view.add_item(container)
            return await interaction.response.send_message(view=view, ephemeral=True)

        reset_prefixes(self.guild_id)

        await interaction.response.edit_message(view=PrefixConfigPanel(self.guild_id))


# ------------------------------
# Main Panel
# ------------------------------

class PrefixConfigPanel(discord.ui.LayoutView):
    def __init__(self, guild_id):
        super().__init__()

        prefixes = get_prefixes(guild_id)
        prefix_list = ", ".join(f"`{p}`" for p in prefixes)

        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_settings')} Prefix Configuration"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(content=f"**Current Prefixes:** {prefix_list}"),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                AddPrefixButton(guild_id),
                RemovePrefixButton(guild_id),
                ResetPrefixButton(guild_id)
            ),
            accent_colour=discord.Color.blurple()
        )

        self.add_item(container)


# ------------------------------
# Cog
# ------------------------------

class PrefixConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix", help="Configure custom prefixes for this server.")
    @commands.has_permissions(manage_guild=True)
    async def prefix_config(self, ctx):
        view = PrefixConfigPanel(ctx.guild.id)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(PrefixConfig(bot))
