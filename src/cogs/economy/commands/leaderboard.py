"""
Economy — leaderboard command.
"""

import discord
from discord.ext import commands
from config.links import WEBSITE
from ..data import _info_view


class LeaderboardMixin:
    """Public global economy leaderboard command.

    Links to the paginated public leaderboard on the website, where private
    profiles stay ranked but their identity is protected.
    """

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="See the global economy leaderboard",
        help="{ 'en': 'see who has the most coins 🏆🪙', 'de': 'sieh, wer die meisten Münzen hat 🏆🪙', 'es': 'mira quién tiene más 🏆🪙' }",
    )
    async def leaderboard(self, ctx: commands.Context):
        view = _info_view(
            "🏆 Rich List",
            f"See the live, paginated leaderboard on the website — private profiles stay ranked while their identity is protected.\n\n[Open the leaderboard]({WEBSITE}/leaderboard)",
        )
        if ctx.interaction:
            await ctx.interaction.response.send_message(view=view)
        else:
            await ctx.send(view=view)
