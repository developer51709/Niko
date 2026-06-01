"""
Economy — leaderboard command.
"""
import asyncio

import discord
from discord.ext import commands
from ..data import (
    _info_view, _card_view,
    render_leaderboard_card, fetch_avatar_bytes,
)


class LeaderboardMixin:
    """leaderboard command."""

    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"],
                             description="See the café rich list as image cards",
                             help="{ 'en': 'see who has the most treats 🏆🥐', 'de': 'sieh die reichsten Gäste', 'es': 'mira quién tiene más 🏆🥐' }")
    async def leaderboard(self, ctx: commands.Context):
        sorted_users = sorted(
            self.economy_data.items(),
            key=lambda x: x[1].get("balance", 0) + x[1].get("bank", 0),
            reverse=True,
        )
        if not sorted_users:
            return await ctx.send(view=_info_view("☕ Quiet café", "No one has any coins yet — the café is just opening!"))

        top = sorted_users[:10]

        async def _entry(idx_uid):
            i, (uid, d) = idx_uid
            user = self.bot.get_user(int(uid)) or None
            if user is None and uid.isdigit():
                try:
                    user = await self.bot.fetch_user(int(uid))
                except Exception:
                    user = None
            avatar = None
            name   = uid
            if user is not None:
                avatar = await fetch_avatar_bytes(str(user.display_avatar.replace(size=128, format="png")), size=128)
                name = user.display_name if hasattr(user, "display_name") else user.name
            return {"rank": i + 1, "name": name, "total": int(d.get("balance", 0) + d.get("bank", 0)), "avatar": avatar}

        entries = await asyncio.gather(*(_entry(item) for item in enumerate(top)))
        buf = await render_leaderboard_card(title="🏆 Café Rich List", entries=entries, page=1, pages=1)

        view = _card_view(
            title="🏆 Leaderboard",
            image_name="leaderboard.png",
            footer_lines=[f"-# Showing top **{len(entries)}** of **{len(sorted_users)}** café-goers."],
        )
        await ctx.send(view=view, file=discord.File(buf, "leaderboard.png"), allowed_mentions=discord.AllowedMentions.none())
