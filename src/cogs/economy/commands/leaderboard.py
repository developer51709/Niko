"""
Economy — leaderboard command.
"""

import discord
from discord.ext import commands
from config.links import WEBSITE
from ..data import _info_view, _reply, locale_t
from utils.i18n import get_lang
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "leaderboard"))


class LeaderboardMixin:
    """Public global economy leaderboard command.

    Links to the paginated public leaderboard on the website, where private
    profiles stay ranked but their identity is protected.
    """

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description=CMDS.text("leaderboard.description"),
        help=CMDS.help("leaderboard"),
    )
    async def leaderboard(self, ctx: commands.Context):
        lang = get_lang(ctx)
        view = _info_view(
            T(lang, "title"),
            T(lang, "body", url=WEBSITE),
        )
        if ctx.interaction:
            await ctx.interaction.response.send_message(view=view)
        else:
            await ctx.send(view=view)
