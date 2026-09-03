from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

import discord
from discord.ext import commands
from config.emojis import get_emoji
from utils import logging as log


# ===================================================
#  DATA MODEL (GLOBAL AFK)
# ===================================================

class AFKState:
    """Represents a user's AFK state globally across all servers."""
    __slots__ = ("user_id", "reason", "since")

    def __init__(self, user_id: int, reason: str, since: datetime):
        self.user_id = user_id
        self.reason = reason
        self.since = since


# In-memory cache (fast lookups): user_id -> AFKState
AFK_CACHE: Dict[int, AFKState] = {}


# ===================================================
#  DATABASE HELPERS
# ===================================================

async def _db_load_all_afk(bot) -> Dict[int, AFKState]:
    """Load all AFK entries from the database into a dict."""
    cache: Dict[int, AFKState] = {}
    try:
        rows = await bot.cxn.fetch("SELECT user_id, reason, since FROM afk_users")
        for row in rows:
            try:
                uid = int(row["user_id"])
                since_str = row["since"]
                if isinstance(since_str, str):
                    since = datetime.fromisoformat(since_str)
                elif isinstance(since_str, datetime):
                    since = since_str
                else:
                    since = datetime.now(timezone.utc)
                # Ensure timezone-aware
                if since.tzinfo is None:
                    since = since.replace(tzinfo=timezone.utc)
                cache[uid] = AFKState(uid, row["reason"], since)
            except Exception as exc:
                log.warning("AFK", f"Could not load AFK row {row}: {exc}")
    except Exception as exc:
        log.error("AFK", f"Failed to load AFK data from database: {exc}")
    return cache


async def _db_set_afk(bot, user_id: int, reason: str, since: datetime) -> None:
    """Insert or replace an AFK entry in the database."""
    since_str = since.isoformat()
    try:
        await bot.cxn.execute(
            "INSERT OR REPLACE INTO afk_users (user_id, reason, since) VALUES ($1, $2, $3)",
            user_id, reason, since_str,
        )
    except Exception as exc:
        log.error("AFK", f"Failed to save AFK for {user_id}: {exc}")


async def _db_remove_afk(bot, user_id: int) -> None:
    """Remove an AFK entry from the database."""
    try:
        await bot.cxn.execute("DELETE FROM afk_users WHERE user_id = $1", user_id)
    except Exception as exc:
        log.error("AFK", f"Failed to remove AFK for {user_id}: {exc}")


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
    view = discord.ui.LayoutView()
    container = discord.ui.Container()

    header = discord.ui.TextDisplay(content="### 🌙 AFK Enabled")
    container.add_item(header)
    container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

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


def _afk_ping_view(afk_user: discord.Member | discord.User, state: AFKState) -> discord.ui.LayoutView:
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
    view = discord.ui.LayoutView()
    container = discord.ui.Container()

    header = discord.ui.TextDisplay(content=f"### {get_emoji('icon_tick')} AFK Removed")
    container.add_item(header)
    container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))

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
    Global AFK system with database persistence.

    Features:
    - AFK applies across ALL servers
    - `afk` command to set AFK with optional reason
    - AFK removed when user speaks anywhere
    - AFK notifications when pinged anywhere
    - State survives bot restarts via database
    - Clean CV2 UI panels
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._loaded = False

    async def _ensure_loaded(self):
        """Lazily load AFK state from database on first use."""
        if not self._loaded:
            global AFK_CACHE
            AFK_CACHE = await _db_load_all_afk(self.bot)
            self._loaded = True

    # ------------------------------
    #  COMMAND: !afk [reason]
    # ------------------------------

    @commands.command(
        name="afk",
        help="Set yourself as AFK with an optional reason.",
    )
    async def afk(self, ctx: commands.Context, *, reason: Optional[str] = None):
        """Mark the invoking user as AFK globally."""
        await self._ensure_loaded()

        state = AFKState(
            user_id=ctx.author.id,
            reason=reason or "No reason provided.",
            since=_utcnow(),
        )
        AFK_CACHE[ctx.author.id] = state
        await _db_set_afk(self.bot, ctx.author.id, state.reason, state.since)

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
        """Global AFK logic:
        1. If the author is AFK and sends a message → remove AFK globally
        2. If the message mentions AFK users → notify the author
        """
        if message.author.bot:
            return

        prefixes = await self.bot.get_prefix(message)
        if any(message.content.startswith(p) for p in prefixes):
            return

        await self._ensure_loaded()

        # 1) Author is AFK → remove AFK globally
        author_state = AFK_CACHE.pop(message.author.id, None)
        if author_state is not None:
            await _db_remove_afk(self.bot, message.author.id)
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
