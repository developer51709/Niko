"""The single ``.staff`` command group that every staff module extends.

Each feature module declares its own subcommands with
``@StaffCommands.staff.command(...)`` and is mixed into ``StaffCog``. Discord.py
collects commands from the whole class hierarchy, so the subcommands need no
copying, renaming or re-registration at runtime.
"""

from discord.ext import commands

from utils.command_locales import command_texts
from utils.prefix_manager import resolve_prefix as _dynamic_prefix

CMDS = command_texts(__package__)


async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await _dynamic_prefix(bot, ctx_or_interaction)


class StaffCommands:
    """Owns the ``.staff`` group; mixins add the subcommands to it."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="staff",
        invoke_without_command=True,
        hidden=True,
        help=CMDS.help("staff"),
    )
    async def staff(self, ctx: commands.Context):
        from cogs.staff.help import build_staff_help

        await ctx.send(view=build_staff_help(self.bot, ctx, "all"))
