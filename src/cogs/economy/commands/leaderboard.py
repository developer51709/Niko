"""
Economy — leaderboard command.
"""

import discord
from discord.ext import commands
from config.links import WEBSITE
from ..data import _info_view


class LeaderboardMixin:
    """Leaderboard command linking to the paginated public café rich list."""

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="See the café rich list",
        help="{ 'en': 'see who has the most treats 🏆🥐', 'de': 'sieh die reichsten Gäste', 'es': 'mira quién tiene más 🏆🥐' }",
    )
    async def leaderboard(self, ctx: commands.Context):
        view = _info_view(
            "🏆 Café Rich List",
            f"See the live, paginated café leaderboard on the website — private profiles stay ranked while their identity is protected.\n\n[Open the leaderboard]({WEBSITE}/leaderboard)",
        )
        if ctx.interaction:
            await ctx.interaction.response.send_message(view=view)
        else:
            await ctx.send(view=view)
