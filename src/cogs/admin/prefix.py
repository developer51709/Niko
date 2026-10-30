import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils.prefix_manager import (
    PREFIX_OVERRIDE,
    get_prefixes,
    add_prefix,
    remove_prefix,
    reset_prefixes,
)

from utils.command_locales import command_texts
from utils.i18n import make_flat_msg
from utils.locales import load_locales

CMDS = command_texts(__package__)
MESSAGES = load_locales(__package__, "prefix")
msg = make_flat_msg(MESSAGES, {
    "warning": get_emoji("warning"),
    "tick": get_emoji("tick"),
    "danger": get_emoji("danger"),
    "settings": get_emoji("settings"),
})


async def build_prefix_panel(bot, guild_id, ctx):
    prefixes = await get_prefixes(guild_id, getattr(bot, "cxn", None))
    return PrefixConfigPanel(bot, guild_id, prefixes, ctx)


def _development_notice_view(ctx):
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "production_only_title")),
        discord.ui.Separator(),
        discord.ui.TextDisplay(content=msg(ctx, "production_only_body")),
        accent_colour=discord.Color.orange(),
    ))
    return view


async def _development_blocked(interaction: discord.Interaction) -> bool:
    if not PREFIX_OVERRIDE:
        return False
    await interaction.response.send_message(
        view=_development_notice_view(interaction), ephemeral=True)
    return True


class AddPrefixModal(discord.ui.Modal):
    def __init__(self, bot, guild_id, ctx):
        super().__init__(title=msg(ctx, "add_modal_title"))
        self.bot = bot
        self.guild_id = guild_id
        self.prefix_input = discord.ui.TextInput(
            label=msg(ctx, "prefix_label"), max_length=10)
        self.add_item(self.prefix_input)

    async def on_submit(self, interaction: discord.Interaction):
        if await _development_blocked(interaction):
            return
        await add_prefix(
            self.guild_id, str(self.prefix_input), getattr(self.bot, "cxn", None))
        await interaction.response.edit_message(
            view=await build_prefix_panel(self.bot, self.guild_id, interaction)
        )


class RemovePrefixSelect(discord.ui.Select):
    def __init__(self, bot, guild_id, message, prefixes, ctx):
        self.bot = bot
        self.guild_id = guild_id
        self.message = message
        options = [discord.SelectOption(label=p, value=p) for p in prefixes]
        super().__init__(
            placeholder=msg(ctx, "remove_select_placeholder"), options=options)

    async def callback(self, interaction: discord.Interaction):
        if await _development_blocked(interaction):
            return
        prefix = self.values[0]
        await remove_prefix(self.guild_id, prefix, getattr(self.bot, "cxn", None))

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "prefix_removed_title")),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content=msg(interaction, "prefix_removed_body", prefix=prefix)
            ),
            accent_colour=discord.Color.green(),
        )
        view.add_item(container)
        await self.message.edit(
            view=await build_prefix_panel(self.bot, self.guild_id, interaction))
        await interaction.response.edit_message(view=view)


class AddPrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id, ctx):
        super().__init__(label=msg(ctx, "btn_add"), style=discord.ButtonStyle.primary)
        self.bot = bot
        self.guild_id = guild_id
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if await _development_blocked(interaction):
            return
        if not interaction.user.guild_permissions.manage_guild:
            view = _permission_error_view(interaction)
            return await interaction.response.send_message(view=view, ephemeral=True)
        await interaction.response.send_modal(
            AddPrefixModal(self.bot, self.guild_id, interaction))


class RemovePrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id, prefixes, ctx):
        super().__init__(label=msg(ctx, "btn_remove"), style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.guild_id = guild_id
        self.prefixes = prefixes
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if await _development_blocked(interaction):
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True)

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(interaction, "remove_heading")),
            discord.ui.Separator(),
            discord.ui.ActionRow(RemovePrefixSelect(
                self.bot, self.guild_id, interaction.message, self.prefixes, interaction
            )),
        ))
        await interaction.response.send_message(view=view, ephemeral=True)


class ResetPrefixButton(discord.ui.Button):
    def __init__(self, bot, guild_id, ctx):
        super().__init__(label=msg(ctx, "btn_reset"), style=discord.ButtonStyle.danger)
        self.bot = bot
        self.guild_id = guild_id
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if await _development_blocked(interaction):
            return
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                view=_permission_error_view(interaction), ephemeral=True)
        await reset_prefixes(self.guild_id, getattr(self.bot, "cxn", None))
        await interaction.response.edit_message(
            view=await build_prefix_panel(self.bot, self.guild_id, interaction)
        )


def _permission_error_view(ctx):
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=msg(ctx, "error_title")),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.TextDisplay(content=msg(ctx, "permission_error")),
        accent_colour=discord.Color.yellow(),
    ))
    return view


class PrefixConfigPanel(discord.ui.LayoutView):
    def __init__(self, bot, guild_id, prefixes, ctx):
        super().__init__()
        prefix_list = ", ".join(f"`{p}`" for p in prefixes)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=msg(ctx, "panel_heading")),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content=msg(ctx, "panel_current", prefixes=prefix_list)),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                AddPrefixButton(bot, guild_id, ctx),
                RemovePrefixButton(bot, guild_id, prefixes, ctx),
                ResetPrefixButton(bot, guild_id, ctx),
            ),
            accent_colour=discord.Color.blurple(),
        ))


class PrefixConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prefix", help=CMDS.help("prefix"))
    @commands.has_permissions(manage_guild=True)
    async def prefix_config(self, ctx):
        if PREFIX_OVERRIDE:
            await ctx.send(view=_development_notice_view(ctx))
            return
        await ctx.send(view=await build_prefix_panel(self.bot, ctx.guild.id, ctx))


async def setup(bot):
    await bot.add_cog(PrefixConfig(bot))
