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
import json
import os
from typing import Optional

import discord
from discord.ext import commands

from config.emojis import get_emoji

DATA_FILE = "data/sticky.json"
MAX_CONTENT_LEN = 1000
MAX_STICKIES_PER_GUILD = 50
REPOST_DELAY = 3.0  # seconds — debounce window so bursts only trigger one repost
DEFAULT_COLOR = 0x5865F2


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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
        self.data: dict = _load()
        self._pending: set[int] = set()  # channel_ids with a repost currently scheduled

    # ── helpers ──────────────────────────────────────────────────────────

    def _guild_data(self, guild_id: int) -> dict:
        return self.data.setdefault(str(guild_id), {})

    def _get(self, guild_id: int, channel_id: int) -> Optional[dict]:
        return self._guild_data(guild_id).get(str(channel_id))

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

        gdata = self._guild_data(ctx.guild.id)
        existing = gdata.get(str(ctx.channel.id))
        if existing is None and len(gdata) >= MAX_STICKIES_PER_GUILD:
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

        gdata[str(ctx.channel.id)] = {
            "content": message,
            "color": color,
            "message_id": posted.id,
            "created_by": ctx.author.id,
        }
        _save(self.data)

        await ctx.send(
            view=_feedback("Sticky message set." if existing is None else "Sticky message updated."),
            ephemeral=ephemeral,
        )

    @sticky.command(name="remove", aliases=["clear", "delete"], description="Remove the sticky message from this channel.")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def sticky_remove(self, ctx: commands.Context):
        ephemeral = bool(ctx.interaction)
        gdata = self._guild_data(ctx.guild.id)
        entry = gdata.pop(str(ctx.channel.id), None)
        if entry is None:
            return await ctx.send(
                view=_feedback("This channel doesn't have a sticky message.", ok=False),
                ephemeral=ephemeral,
            )
        _save(self.data)

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
        gdata = self._guild_data(ctx.guild.id)
        if not gdata:
            return await ctx.send(
                view=_feedback("This server has no sticky messages yet.", ok=False),
                ephemeral=ephemeral,
            )

        lines = []
        for cid_str, entry in gdata.items():
            content = entry.get("content", "")
            preview = content[:80] + ("…" if len(content) > 80 else "")
            lines.append(f"• <#{cid_str}> — {preview}")

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### 📌 Sticky Messages ({len(gdata)})"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content="\n".join(lines)),
        ))
        await ctx.send(view=view, ephemeral=ephemeral, allowed_mentions=discord.AllowedMentions.none())

    # ── restick logic ────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.id == self.bot.user.id:
            return

        entry = self._get(message.guild.id, message.channel.id)
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

            entry = self._get(guild_id, channel_id)
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

            entry["message_id"] = posted.id
            _save(self.data)
        except Exception:
            # Never let a background repost task crash the event loop silently.
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(StickyCog(bot))
