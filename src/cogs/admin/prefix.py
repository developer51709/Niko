import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.prefix_manager import (
    get_prefixes,
    add_prefix,
    remove_prefix,
    reset_prefixes,
)


async def build_prefix_panel(bot, guild_id):
    prefixes = await get_prefixes(guild_id, getattr(bot, "cxn", None))
    return PrefixConfigPanel(bot, guild_id, prefixes)


class AddPrefixModal(discord.ui.Modal, title="Add Prefix"):
    prefix = discord.ui.TextInput(label="Prefix", max_length=10)

    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        await add_prefix(self.guild_id, str(self.prefix), getattr(self.bot, "cxn", None))
        await interaction.response.edit_message(
            view=await build_prefix_panel(self.bot, self.guild_id)
        )


class RemovePrefixSelect(discord.ui.Select):
    def __init__(self, bot, guild_id, message, prefixes):
        self.bot = bot
        self.guild_id = guild_id
        self.message = message
        options = [discord.SelectOption(label=p, value=p) for p in prefixes]
        super().__init__(placeholder="Select a prefix to remove", options=options)

    async def callback(self, interaction: discord.Interaction):
        prefix = self.values[0]
        await remove_prefix(self.guild_id, prefix, getattr(self.bot, "cxn", None))

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_check')} Prefix Removed"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(content=f"Removed prefix: `{prefix}`"),
            accent_colour=discord.Color.green(),
        )
        view.add_item(container)
        await self.message.edit(view=await build_prefix_panel(self.bot, self.guild_id))
        await interaction.response.edit_message(view=view)


class AddPrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id):
        super().__init__(label="Add Prefix", style=discord.ButtonStyle.primary)
        self.bot = bot
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            view = _permission_error_view()
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(AddPrefixModal(self.bot, self.guild_id))


class RemovePrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id, prefixes):
        super().__init__(label="Remove Prefix", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.guild_id = guild_id
        self.prefixes = prefixes

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(view=_permission_error_view(), ephemeral=True)

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### Remove Prefix"),
            discord.ui.Separator(),
            discord.ui.ActionRow(RemovePrefixSelect(
                self.bot, self.guild_id, interaction.message, self.prefixes
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class ResetPrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id):
        super().__init__(label="Reset Prefixes", style=discord.ButtonStyle.danger)
        self.bot = bot
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(view=_permission_error_view(), ephemeral=True)
        await reset_prefixes(self.guild_id, getattr(self.bot, "cxn", None))
        await interaction.response.edit_message(
            view=await build_prefix_panel(self.bot, self.guild_id)
        )


def _permission_error_view():
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"### {get_emoji('icon_danger')} Error"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content="You need the `manage_guild` permission to use this button."),
        accent_colour=discord.Color.yellow(),
    ))
    return view


class PrefixConfigPanel(discord.ui.LayoutView):
    def __init__(self, bot, guild_id, prefixes):
        super().__init__()
        prefix_list = ", ".join(f"`{p}`" for p in prefixes)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_settings')} Prefix Configuration"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(content=f"**Current Prefixes:** {prefix_list}"),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                AddPrefixButton(bot, guild_id),
                RemovePrefixButton(bot, guild_id, prefixes),
                ResetPrefixButton(bot, guild_id),
            ),
            accent_colour=discord.Color.blurple(),
        ))


class PrefixConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix", help="Configure custom prefixes for this server.")
    @commands.has_permissions(manage_guild=True)
    async def prefix_config(self, ctx):
        await ctx.send(view=await build_prefix_panel(self.bot, ctx.guild.id))


async def setup(bot):
    await bot.add_cog(PrefixConfig(bot))
