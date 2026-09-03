"""
Sticky Messages — keep a chosen message pinned to the bottom of a channel.

Commands (`sticky` group):
    sticky set <message>   — create or update the sticky message for this channel
    sticky remove          — remove the sticky message from this channel
    sticky list             — list every channel with an active sticky in this server

Behaviour: whenever a new (non-bot) message is sent in a channel with an
active sticky, the old sticky post is deleted and a fresh copy is sent
underneath it after a short debounce window — so a busy channel doesn't
trigger a delete+repost on every single message.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import discord
from discord.ext import commands

from config.emojis import get_emoji

MAX_CONTENT_LEN = 1000
MAX_STICKIES_PER_GUILD = 50
REPOST_DELAY = 3.0  # seconds — debounce window so bursts only trigger one repost
DEFAULT_COLOR = 0x5865F2


def _sticky_view(content: str, color: int) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"## 📌 Sticky Message"),
        discord.ui.Separator(),
        discord.ui.TextDisplay(content=f"{content}"),
        accent_colour=discord.Colour(color),
    ))
    return view


def _feedback(content: str, ok: bool = True) -> discord.ui.LayoutView:
    view = discord.ui.LayoutView()
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"{get_emoji('icon_tick') if ok else get_emoji('icon_cross')} {content}"),
        accent_colour=discord.Colour.green() if ok else discord.Colour.red(),
    ))
    return view


class StickyCog(commands.Cog, name="Sticky"):
    """Keep a message stuck to the bottom of a channel."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._pending: set[int] = set()  # channel_ids with a repost currently scheduled

    # ── database helpers ────────────────────────────────────────────────

    async def _get(self, guild_id: int, channel_id: int) -> Optional[dict]:
        """Fetch a sticky entry from the database."""
        row = await self.bot.cxn.fetchrow(
            "SELECT * FROM sticky_messages WHERE channel_id = $1",
            channel_id,
        )
        if row is None:
            return None
        return dict(row)

    async def _get_count(self, guild_id: int) -> int:
        """Count sticky messages in a guild."""
        return await self.bot.cxn.fetchval(
            "SELECT COUNT(*) FROM sticky_messages WHERE guild_id = $1",
            guild_id,
        ) or 0

    # ── commands ─────────────────────────────────────────────────────────

    @commands.hybrid_group(
        name="sticky",
        description="Create and manage sticky messages for this server.",
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def sticky(self, ctx: commands.Context):
        prefix = ctx.prefix or "."
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content="### 📌 Sticky Messages"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    "Sticky messages stay pinned to the bottom of a channel — every time "
                    "someone posts, I delete the old copy and repost it underneath.\n\n"
                    f"**`{prefix}sticky set <message>`** — create or update the sticky message here\n"
                    f"**`{prefix}sticky remove`** — remove the sticky message from this channel\n"
                    f"**`{prefix}sticky list`** — list every sticky message in this server"
                )
            ),
        ))
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    @sticky.command(name="set", description="Create or update the sticky message for this channel.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sticky_set(self, ctx: commands.Context, *, message: str):
        message = message.strip()
        ephemeral = bool(ctx.interaction)

        if not message:
            return await ctx.send(view=_feedback("Please provide the message to stick.", ok=False), ephemeral=ephemeral)
        if len(message) > MAX_CONTENT_LEN:
            return await ctx.send(
                view=_feedback(f"Sticky messages can be at most {MAX_CONTENT_LEN} characters.", ok=False),
                ephemeral=ephemeral,
            )

        existing = await self._get(ctx.guild.id, ctx.channel.id)
        if existing is None:
            count = await self._get_count(ctx.guild.id)
            if count >= MAX_STICKIES_PER_GUILD:
                return await ctx.send(
                    view=_feedback(f"This server already has the maximum of {MAX_STICKIES_PER_GUILD} sticky messages.", ok=False),
                    ephemeral=ephemeral,
                )

        # Delete the previous sticky post (if any) before sending the new one.
        old_message_id = existing.get("message_id") if existing else None
        if old_message_id:
            try:
                old_msg = await ctx.channel.fetch_message(old_message_id)
                await old_msg.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        color = existing.get("color") if existing else DEFAULT_COLOR

        try:
            posted = await ctx.channel.send(view=_sticky_view(message, color))
        except discord.Forbidden:
            return await ctx.send(
                view=_feedback("I don't have permission to send messages in this channel.", ok=False),
                ephemeral=ephemeral,
            )

        if existing:
            await self.bot.cxn.execute(
                "UPDATE sticky_messages SET content = $1, message_id = $2 WHERE channel_id = $3",
                message, posted.id, ctx.channel.id,
            )
        else:
            await self.bot.cxn.execute(
                "INSERT INTO sticky_messages (channel_id, guild_id, content, color, message_id, created_by) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                ctx.channel.id, ctx.guild.id, message, color, posted.id, ctx.author.id,
            )

        await ctx.send(
            view=_feedback("Sticky message set." if existing is None else "Sticky message updated."),
            ephemeral=ephemeral,
        )

    @sticky.command(name="remove", aliases=["clear", "delete"], description="Remove the sticky message from this channel.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sticky_remove(self, ctx: commands.Context):
        ephemeral = bool(ctx.interaction)
        entry = await self._get(ctx.guild.id, ctx.channel.id)
        if entry is None:
            return await ctx.send(
                view=_feedback("This channel doesn't have a sticky message.", ok=False),
                ephemeral=ephemeral,
            )

        await self.bot.cxn.execute(
            "DELETE FROM sticky_messages WHERE channel_id = $1",
            ctx.channel.id,
        )

        if entry.get("message_id"):
            try:
                old_msg = await ctx.channel.fetch_message(entry["message_id"])
                await old_msg.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        await ctx.send(view=_feedback("Sticky message removed."), ephemeral=ephemeral)

    @sticky.command(name="list", description="List every sticky message in this server.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sticky_list(self, ctx: commands.Context):
        ephemeral = bool(ctx.interaction)
        rows = await self.bot.cxn.fetch(
            "SELECT channel_id, content FROM sticky_messages WHERE guild_id = $1",
            ctx.guild.id,
        )
        if not rows:
            return await ctx.send(
                view=_feedback("This server has no sticky messages yet.", ok=False),
                ephemeral=ephemeral,
            )

        lines = []
        for row in rows:
            content = row["content"]
            preview = content[:80] + ("…" if len(content) > 80 else "")
            lines.append(f"• <#{row['channel_id']}> — {preview}")

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### 📌 Sticky Messages ({len(rows)})"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="\n".join(lines)),
        ))
        await ctx.send(view=view, ephemeral=ephemeral, allowed_mentions=discord.AllowedMentions.none())

    # ── restick logic ────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.id == self.bot.user.id:
            return

        entry = await self._get(message.guild.id, message.channel.id)
        if entry is None:
            return

        channel_id = message.channel.id
        if channel_id in self._pending:
            return  # a repost is already scheduled for this channel — let it handle this burst
        self._pending.add(channel_id)

        task = asyncio.create_task(self._repost_after_delay(message.guild.id, channel_id))
        task.add_done_callback(lambda t: self._pending.discard(channel_id))

    async def _repost_after_delay(self, guild_id: int, channel_id: int):
        try:
            await asyncio.sleep(REPOST_DELAY)

            entry = await self._get(guild_id, channel_id)
            if entry is None:
                return  # sticky was removed while we were waiting

            channel = self.bot.get_channel(channel_id)
            if channel is None:
                return

            old_message_id = entry.get("message_id")
            if old_message_id:
                try:
                    old_msg = await channel.fetch_message(old_message_id)
                    await old_msg.delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass

            try:
                posted = await channel.send(view=_sticky_view(entry["content"], entry.get("color", DEFAULT_COLOR)))
            except (discord.Forbidden, discord.HTTPException):
                return

            await self.bot.cxn.execute(
                "UPDATE sticky_messages SET message_id = $1 WHERE channel_id = $2",
                posted.id, channel_id,
            )
        except Exception:
            # Never let a background repost task crash the event loop silently.
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(StickyCog(bot))
