from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

import discord
from discord.ext import commands
from config.emojis import get_emoji


# ===================================================
#  DATA MODEL (GLOBAL AFK)
# ===================================================

@dataclass
class AFKState:
    """Represents a user's AFK state globally across all servers."""
    user_id: int
    reason: str
    since: datetime


# Global AFK cache: user_id -> AFKState
AFK_CACHE: Dict[int, AFKState] = {}


# ===================================================
#  SMALL UTILITIES
# ===================================================

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _format_timedelta(start: datetime) -> str:
    """Return a human-readable duration string."""
    delta = _utcnow() - start
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"


# ===================================================
#  CV2 LAYOUT HELPERS
# ===================================================

def _afk_set_view(user: discord.User, reason: str) -> discord.ui.LayoutView:
    """
    AFK set panel (matches AFK removed layout).

    Layout:
    - Container
      - TextDisplay (header)
      - Separator
      - TextDisplay (body)
    """
    view = discord.ui.LayoutView()
    container = discord.ui.Container()

    header = discord.ui.TextDisplay(
        content="### 🌙 AFK Enabled"
    )
    container.add_item(header)

    container.add_item(
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
    )

    body = discord.ui.TextDisplay(
        content=(
            f"{user.mention} is now marked as AFK.\n"
            f"-# **Reason:** {reason or 'No reason provided.'}\n"
            f"-# Your AFK will be removed automatically when you speak again."
        )
    )
    container.add_item(body)

    view.add_item(container)
    return view


def _afk_ping_view(
    afk_user: discord.Member | discord.User,
    state: AFKState,
) -> discord.ui.LayoutView:
    """
    AFK notification panel when someone pings an AFK user.

    Layout:
    - Container
      - TextDisplay (AFK info)
    """
    view = discord.ui.LayoutView()
    container = discord.ui.Container()

    duration = _format_timedelta(state.since)
    text = discord.ui.TextDisplay(
        content=(
            f"### 🌙 {afk_user.display_name} is AFK\n"
            f"**Reason:** {state.reason or 'No reason provided.'}\n"
            f"**Since:** <t:{int(state.since.timestamp())}:R> ({duration} ago)"
        )
    )
    container.add_item(text)

    view.add_item(container)
    return view


def _afk_removed_view(user: discord.User, state: AFKState) -> discord.ui.LayoutView:
    """
    AFK-removed panel.

    Layout:
    - Container
      - TextDisplay (header)
      - Separator
      - TextDisplay (body)
    """
    view = discord.ui.LayoutView()
    container = discord.ui.Container()

    header = discord.ui.TextDisplay(
        content=f"### {get_emoji('icon_tick')} AFK Removed"
    )
    container.add_item(header)

    container.add_item(
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small)
    )

    duration = _format_timedelta(state.since)
    body = discord.ui.TextDisplay(
        content=(
            f"Welcome back {user.mention}!\n"
            f"-# You were away for **{duration}**"
        )
    )
    container.add_item(body)

    view.add_item(container)
    return view


# ===================================================
#  AFK COG
# ===================================================

class AFKCog(commands.Cog):
    """
    Global AFK system.

    Features:
    - AFK applies across ALL servers
    - `afk` command to set AFK with optional reason
    - AFK removed when user speaks anywhere
    - AFK notifications when pinged anywhere
    - Clean CV2 UI panels
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ------------------------------
    #  COMMAND: !afk [reason]
    # ------------------------------

    @commands.command(
        name="afk",
        help="Set yourself as AFK with an optional reason.",
    )
    async def afk(self, ctx: commands.Context, *, reason: Optional[str] = None):
        """
        Mark the invoking user as AFK globally.
        """
        state = AFKState(
            user_id=ctx.author.id,
            reason=reason or "No reason provided.",
            since=_utcnow(),
        )
        AFK_CACHE[ctx.author.id] = state

        view = _afk_set_view(ctx.author, state.reason)
        try:
            await ctx.reply(view=view, allowed_mentions=discord.AllowedMentions.none())
        except Exception:
            await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # ------------------------------
    #  LISTENER: on_message
    # ------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Global AFK logic:

        1. If the author is AFK and sends a message:
           - Remove AFK globally
           - Send AFK-removed panel

        2. If the message mentions AFK users:
           - Notify the author globally
        """
        if message.author.bot:
            return

        prefixes = await self.bot.get_prefix(message)
        if any(message.content.startswith(p) for p in prefixes):
            return

        # 1) Author is AFK → remove AFK globally
        author_state = AFK_CACHE.pop(message.author.id, None)
        if author_state is not None:
            try:
                view = _afk_removed_view(message.author, author_state)
                await message.channel.send(view=view, allowed_mentions=discord.AllowedMentions.none())
            except discord.HTTPException:
                pass

        # 2) Check mentions for AFK users
        if not message.mentions:
            return

        notified_ids = set()

        for user in message.mentions:
            if user.bot:
                continue
            state = AFK_CACHE.get(user.id)
            if not state or user.id in notified_ids:
                continue

            notified_ids.add(user.id)

            view = _afk_ping_view(user, state)
            try:
                try:
                    await message.reply(view=view, allowed_mentions=discord.AllowedMentions.none())
                except Exception:
                    await message.channel.send(view=view, allowed_mentions=discord.AllowedMentions.none())
            except discord.HTTPException:
                pass


# ===================================================
#  SETUP
# ===================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(AFKCog(bot))