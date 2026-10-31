"""Niko's private ``.staff`` command tree.

The cog itself is only the assembly: the ``.staff`` group in ``base``, one
mix-in per area of the command surface, and the role check every subcommand
shares. Adding a command means adding a method to the right module — nothing
here needs to know about it.
"""

import time

import discord
from discord.ext import commands

from config.ids import SUPPORT_GUILD
from cogs.staff.base import StaffCommands
from cogs.staff.commands.administration import AdministrationCommands
from cogs.staff.commands.diagnostics import DiagnosticsCommands
from cogs.staff.commands.emojis import EmojiCommands
from cogs.staff.commands.moderation import ModerationCommands
from cogs.staff.commands.panels import PanelCommands
from cogs.staff.commands.profile import ProfileCommands
from cogs.staff.commands.runtime import RuntimeCommands
from cogs.staff.commands.support import SupportCommands
from cogs.staff.help import HelpCommands
from cogs.staff.manage import ManageCommands
from cogs.staff.panels.rules import PERSISTENT_ITEMS
from cogs.staff.panels.status import StatusPanelCog
from cogs.staff.permissions import role_label, staff_command_name, staff_permission
from cogs.staff.records import role_for
from cogs.staff.support_server import (
    apply_role_icons,
    get_support_ids,
    role_icons_available,
)


class StaffCog(
    StaffCommands,
    HelpCommands,
    ManageCommands,
    ProfileCommands,
    RuntimeCommands,
    AdministrationCommands,
    ModerationCommands,
    PanelCommands,
    DiagnosticsCommands,
    EmojiCommands,
    SupportCommands,
    commands.Cog,
):
    """One private command group for Niko owners and official staff."""

    def __init__(self, bot):
        super().__init__(bot)
        self.start_time = time.time()
        # The rules panel's buttons are persistent dynamic items.
        bot.add_dynamic_items(*PERSISTENT_ITEMS)

    async def cog_unload(self) -> None:
        self.bot.remove_dynamic_items(*PERSISTENT_ITEMS)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Apply role icons the moment the support server unlocks the perk."""
        if after.id != SUPPORT_GUILD:
            return
        if not role_icons_available(after) or role_icons_available(before):
            return
        roles = (await get_support_ids(self.bot)).get("roles", {})
        if roles:
            await apply_role_icons(after, roles)

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Gate every ``.staff`` subcommand on the caller's staff role."""
        return await staff_permission(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Explain a staff check failure instead of the generic check message."""
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        # ``supportsetup``/``supportupdate`` are guild-only; every other
        # failure keeps the shared handler's wording and reporting.
        if not isinstance(error, commands.CheckFailure) or isinstance(error, commands.NoPrivateMessage):
            ctx.bot.dispatch("command_error", ctx, error)
            return
        role = await role_for(ctx)
        if role is None:
            return await ctx.send("This command is restricted to official Niko staff.")
        await ctx.send(
            f"`.staff {staff_command_name(ctx.command)}` is not available to your "
            f"**{role_label(role)}** role. Run `.staff help` to see what your role can use."
        )


async def setup(bot):
    await bot.add_cog(StaffCog(bot))
    await bot.add_cog(StatusPanelCog(bot))
