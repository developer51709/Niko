"""
Suggestions — server suggestions with up/down voting and admin approve/deny.

Commands (single `suggest` group):
    suggest <text>             — submit a suggestion to the configured channel
    suggest channel <channel>  — set the suggestion channel (admin)
    suggest approve <id> [reason] — approve a suggestion (manage_guild)
    suggest deny <id> [reason]    — deny a suggestion (manage_guild)
    suggest config             — show server config (admin)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

MESSAGES = load_locales("cogs.social", "suggestions")


def _lang(ctx) -> str:
    g = getattr(ctx, "guild", None)
    if g and g.preferred_locale:
        l = str(g.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


msg = make_flat_msg(MESSAGES)


# ───────────────────────────────────────────────────
#  VOTE BUTTONS
# ───────────────────────────────────────────────────

class _UpBtn(discord.ui.Button):
    def __init__(self, sid: int):
        super().__init__(emoji=f"{get_emoji('thumbs_up')}", style=discord.ButtonStyle.success,
                         custom_id=f"sug_up:{sid}")
        self.sid = sid

    async def callback(self, interaction: discord.Interaction):
        cog: "Suggestions" = interaction.client.get_cog("Suggestions")
        if cog:
            await cog.handle_vote(interaction, self.sid, +1)


class _DownBtn(discord.ui.Button):
    def __init__(self, sid: int):
        super().__init__(emoji=f"{get_emoji('thumbs_down')}", style=discord.ButtonStyle.danger,
                         custom_id=f"sug_down:{sid}")
        self.sid = sid

    async def callback(self, interaction: discord.Interaction):
        cog: "Suggestions" = interaction.client.get_cog("Suggestions")
        if cog:
            await cog.handle_vote(interaction, self.sid, -1)


def _build_view(s: dict, ctx_like) -> discord.ui.LayoutView:
    status = s.get("status", "open")
    if status == "approved":
        title_key = "title_approved"
    elif status == "denied":
        title_key = "title_denied"
    else:
        title_key = "title_open"

    title = msg(ctx_like, title_key, icon=get_emoji("lightbulb"), id=s["id"], tick=get_emoji("tick"), cross=get_emoji("cross"))
    author = ctx_like.guild.get_member(s["author_id"]) if (ctx_like and ctx_like.guild) else None
    author_str = author.mention if author else f"<@{s['author_id']}>"
    body = msg(ctx_like, "body", text=s["text"], author=author_str)
    votes = msg(ctx_like, "votes", up=s.get("up", 0), down=s.get("down", 0), up_emoji=get_emoji("thumbs_up"), down_emoji=get_emoji("thumbs_down"))

    full = title + "\n" + body + "\n\n" + votes
    if s.get("verdict"):
        full += "\n\n" + msg(ctx_like, "verdict", who=s["verdict"]["by"], reason=s["verdict"]["reason"])

    view = discord.ui.LayoutView(timeout=None)
    children = [discord.ui.TextDisplay(content=full)]
    if status == "open":
        children.append(discord.ui.ActionRow(_UpBtn(s["id"]), _DownBtn(s["id"])))
    view.add_item(discord.ui.Container(*children))
    return view


class Suggestions(commands.Cog):
    """Server suggestion system."""

    def __init__(self, bot):
        self.bot = bot
        # The cache is only a hot-path representation. The main database is
        # authoritative and is loaded before persistent views are registered.
        self.data = {"guilds": {}}

    async def cog_load(self):
        await self._load_database()
        await self._register_persistent_views()

    @staticmethod
    def _decode_json(value, default):
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value) if value else default
        except (TypeError, ValueError):
            return default

    async def _load_database(self):
        rows = await self.bot.cxn.fetch("SELECT guild_id, channel_id, next_id FROM suggestion_config")
        for row in rows:
            self.data["guilds"][str(row["guild_id"])] = {
                "channel_id": row.get("channel_id"),
                "next_id": row.get("next_id", 1),
                "items": {},
            }
        rows = await self.bot.cxn.fetch("SELECT * FROM suggestions")
        for row in rows:
            guild = self.data["guilds"].setdefault(str(row["guild_id"]), {
                "channel_id": None, "next_id": row.get("suggestion_id", 1) + 1, "items": {},
            })
            suggestion = dict(row)
            suggestion["id"] = suggestion.pop("suggestion_id")
            suggestion["voters"] = self._decode_json(suggestion.get("voters"), {})
            suggestion["verdict"] = self._decode_json(suggestion.get("verdict"), None)
            guild["items"][str(suggestion["id"])] = suggestion

    async def _register_persistent_views(self):
        registered = 0
        for guild in self.data["guilds"].values():
            for suggestion in guild["items"].values():
                if suggestion.get("status") != "open" or not suggestion.get("message_id"):
                    continue
                try:
                    self.bot.add_view(_build_view(suggestion, None), message_id=suggestion["message_id"])
                    registered += 1
                except Exception as exc:
                    print(f"[Suggestions] Could not register view for {suggestion['message_id']}: {exc}")
        if registered:
            print(f"[Suggestions] Registered {registered} persistent suggestion view(s)")

    def _g(self, gid: int) -> dict:
        return self.data["guilds"].setdefault(str(gid), {
            "channel_id": None,
            "next_id": 1,
            "items": {},
        })

    async def _persist_config(self, gid: int, g: dict):
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO suggestion_config (guild_id, channel_id, next_id) VALUES ($1, $2, $3)",
            gid, g.get("channel_id"), g.get("next_id", 1),
        )

    async def _persist_suggestion(self, gid: int, suggestion: dict):
        await self.bot.cxn.execute(
            "INSERT OR REPLACE INTO suggestions "
            "(message_id, guild_id, suggestion_id, text, author_id, status, up, down, voters, channel_id, verdict, created_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)",
            suggestion["message_id"], gid, suggestion["id"], suggestion["text"],
            suggestion["author_id"], suggestion.get("status", "open"), suggestion.get("up", 0),
            suggestion.get("down", 0), suggestion.get("voters", {}), suggestion["channel_id"],
            suggestion.get("verdict"), suggestion.get("created_at", 0),
        )

    @commands.hybrid_group(
        name="suggest",
        description=CMDS.text("suggest.description"),
        help=CMDS.help("suggest"),
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def suggest(self, ctx: commands.Context, *, text: str = None):
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.suggest)
        await ctx.invoke(help_cmd, command_name="suggest")

    @suggest.command(
        name="submit",
        description=CMDS.text("suggest.submit.description"),
        help=CMDS.help("suggest.submit"),
    )
    async def suggest_submit(self, ctx: commands.Context, *, text: str):
        await self._submit(ctx, text)

    async def _submit(self, ctx: commands.Context, text: str):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g.get("channel_id") or 0) if g.get("channel_id") else None
        if not ch:
            return await ctx.send(f"{get_emoji('cross')} {msg(ctx, 'no_channel')}")
        sid = g["next_id"]
        g["next_id"] = sid + 1

        s = {
            "id": sid,
            "text": text[:1500],
            "author_id": ctx.author.id,
            "status": "open",
            "up": 0,
            "down": 0,
            "voters": {},  # uid -> "up"/"down"
            "message_id": None,
            "channel_id": ch.id,
            "verdict": None,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
        }
        view = _build_view(s, ctx)
        sent = await ch.send(view=view)
        s["message_id"] = sent.id
        g["items"][str(sid)] = s
        await self._persist_config(ctx.guild.id, g)
        await self._persist_suggestion(ctx.guild.id, s)
        self.bot.dispatch("sticky_feature_message", ctx.guild.id, ch.id)
        try:
            self.bot.add_view(_build_view(s, ctx), message_id=sent.id)
        except Exception:
            pass

        if ctx.interaction:
            await ctx.send(f"{get_emoji('tick')} {msg(ctx, 'submitted', channel=ch.mention, id=sid)}", ephemeral=True)
        else:
            await ctx.send(f"{get_emoji('tick')} {msg(ctx, 'submitted', channel=ch.mention, id=sid)}")

    @suggest.command(
        name="channel",
        description=CMDS.text("suggest.channel.description"),
        help=CMDS.help("suggest.channel"),
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        g["channel_id"] = channel.id
        await self._persist_config(ctx.guild.id, g)
        await ctx.send(f"{get_emoji('tick')} {msg(ctx, 'channel_set', channel=channel.mention)}")

    @suggest.command(
        name="config",
        description=CMDS.text("suggest.config.description"),
        help=CMDS.help("suggest.config"),
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_config(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g.get("channel_id") or 0) if g.get("channel_id") else None
        view = discord.ui.LayoutView()
        body = msg(ctx, "config_title", icon=get_emoji("settings")) + "\n" + \
            msg(ctx, "config_body", channel=ch.mention if ch else "—")
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=body)))
        await ctx.send(view=view)

    @suggest.command(
        name="approve",
        description=CMDS.text("suggest.approve.description"),
        help=CMDS.help("suggest.approve"),
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_approve(self, ctx: commands.Context, suggestion_id: int, *, reason: str = "—"):
        await self._verdict(ctx, suggestion_id, "approved", reason, "approved")

    @suggest.command(
        name="deny",
        description=CMDS.text("suggest.deny.description"),
        help=CMDS.help("suggest.deny"),
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_deny(self, ctx: commands.Context, suggestion_id: int, *, reason: str = "—"):
        await self._verdict(ctx, suggestion_id, "denied", reason, "denied")

    async def _verdict(self, ctx, sid: int, status: str, reason: str, ack_key: str):
        g = self._g(ctx.guild.id)
        s = g["items"].get(str(sid))
        if not s:
            return await ctx.send(f"{get_emoji('warning')} {msg(ctx, 'missing', id=sid)}")
        s["status"] = status
        s["verdict"] = {"by": ctx.author.mention, "reason": reason[:500]}
        await self._persist_suggestion(ctx.guild.id, s)
        ch = ctx.guild.get_channel(s["channel_id"])
        if ch:
            try:
                m = await ch.fetch_message(s["message_id"])
                await m.edit(view=_build_view(s, ctx))
            except Exception:
                pass
        await ctx.send(f"{get_emoji('tick')} {msg(ctx, ack_key, id=sid)}")

    # ───── voting ───────────────────────────────

    async def handle_vote(self, interaction: discord.Interaction, sid: int, direction: int):
        gid = interaction.guild.id if interaction.guild else None
        if not gid:
            return
        g = self._g(gid)
        s = g["items"].get(str(sid))
        if not s or s.get("status") != "open":
            return await interaction.response.defer()
        uid = str(interaction.user.id)
        prev = s["voters"].get(uid)
        new = "up" if direction > 0 else "down"
        if prev == new:
            # toggle off
            s["voters"].pop(uid, None)
            if new == "up":
                s["up"] = max(0, s.get("up", 0) - 1)
            else:
                s["down"] = max(0, s.get("down", 0) - 1)
        else:
            if prev == "up":
                s["up"] = max(0, s.get("up", 0) - 1)
            elif prev == "down":
                s["down"] = max(0, s.get("down", 0) - 1)
            s["voters"][uid] = new
            if new == "up":
                s["up"] = s.get("up", 0) + 1
            else:
                s["down"] = s.get("down", 0) + 1
        await self._persist_suggestion(gid, s)

        try:
            await interaction.response.edit_message(view=_build_view(s, interaction))
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
