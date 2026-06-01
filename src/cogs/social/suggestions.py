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
import os
from datetime import datetime, timezone
from typing import Dict

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg

DATA_FILE = "data/suggestions.json"


MESSAGES = {
    "normal": {
        "en": {
            "no_channel":     "❌ No suggestion channel configured. An admin must run `suggest channel <channel>` first.",
            "submitted":      "✅ Suggestion submitted in {channel} — ID `#{id}`.",
            "channel_set":    "✅ Suggestion channel set to {channel}.",
            "config_title":   "### {icon} Suggestion Config",
            "config_body":    "**Channel:** {channel}",
            "missing":        "⚠️ No suggestion with ID `#{id}` found.",
            "approved":       "✅ Suggestion `#{id}` approved.",
            "denied":         "✅ Suggestion `#{id}` denied.",
            "title_open":     "### {icon} Suggestion #{id}",
            "title_approved": "### {icon} Suggestion #{id} · ✅ Approved",
            "title_denied":   "### {icon} Suggestion #{id} · ❌ Denied",
            "body":           "{text}\n\n-# By {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**Verdict by {who}:** {reason}",
        },
        "de": {
            "no_channel":     "❌ Kein Vorschlagskanal konfiguriert. Ein Admin muss zuerst `suggest channel <channel>` ausführen.",
            "submitted":      "✅ Vorschlag in {channel} eingereicht — ID `#{id}`.",
            "channel_set":    "✅ Vorschlagskanal auf {channel} gesetzt.",
            "config_title":   "### {icon} Vorschlags-Konfiguration",
            "config_body":    "**Kanal:** {channel}",
            "missing":        "⚠️ Kein Vorschlag mit ID `#{id}` gefunden.",
            "approved":       "✅ Vorschlag `#{id}` angenommen.",
            "denied":         "✅ Vorschlag `#{id}` abgelehnt.",
            "title_open":     "### {icon} Vorschlag #{id}",
            "title_approved": "### {icon} Vorschlag #{id} · ✅ Angenommen",
            "title_denied":   "### {icon} Vorschlag #{id} · ❌ Abgelehnt",
            "body":           "{text}\n\n-# Von {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**Urteil von {who}:** {reason}",
        },
        "es": {
            "no_channel":     "❌ No hay canal de sugerencias configurado. Un admin debe ejecutar `suggest channel <canal>` primero.",
            "submitted":      "✅ Sugerencia enviada en {channel} — ID `#{id}`.",
            "channel_set":    "✅ Canal de sugerencias establecido en {channel}.",
            "config_title":   "### {icon} Configuración de Sugerencias",
            "config_body":    "**Canal:** {channel}",
            "missing":        "⚠️ No se encontró sugerencia con ID `#{id}`.",
            "approved":       "✅ Sugerencia `#{id}` aprobada.",
            "denied":         "✅ Sugerencia `#{id}` denegada.",
            "title_open":     "### {icon} Sugerencia #{id}",
            "title_approved": "### {icon} Sugerencia #{id} · ✅ Aprobada",
            "title_denied":   "### {icon} Sugerencia #{id} · ❌ Denegada",
            "body":           "{text}\n\n-# Por {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**Veredicto de {who}:** {reason}",
        },
    },
    "cafe": {
        "en": {
            "no_channel":     "❌ no suggestions corner set yet — admin needs to run `suggest channel <channel>` first ☕",
            "submitted":      "✅ pinned your idea in {channel} — `#{id}` ☕✨",
            "channel_set":    "✅ suggestions corner is now {channel} ☕",
            "config_title":   "### {icon} suggestions corner ☕",
            "config_body":    "**channel:** {channel}",
            "missing":        "⚠️ no idea with id `#{id}` here hun~",
            "approved":       "✅ idea `#{id}` brewed and approved ☕✨",
            "denied":         "✅ idea `#{id}` gently set aside ☕",
            "title_open":     "### {icon} idea #{id} ☕",
            "title_approved": "### {icon} idea #{id} · ✅ approved ☕✨",
            "title_denied":   "### {icon} idea #{id} · ❌ set aside ☕",
            "body":           "{text}\n\n-# by {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**verdict by {who}:** {reason}",
        },
        "de": {
            "no_channel":     "❌ noch keine vorschlags-ecke — admin muss erst `suggest channel <channel>` machen ☕",
            "submitted":      "✅ deine idee in {channel} angepinnt — `#{id}` ☕✨",
            "channel_set":    "✅ die vorschlags-ecke ist jetzt {channel} ☕",
            "config_title":   "### {icon} vorschlags-ecke ☕",
            "config_body":    "**kanal:** {channel}",
            "missing":        "⚠️ keine idee mit id `#{id}` hier hun~",
            "approved":       "✅ idee `#{id}` gebraut und angenommen ☕✨",
            "denied":         "✅ idee `#{id}` sanft beiseite gelegt ☕",
            "title_open":     "### {icon} idee #{id} ☕",
            "title_approved": "### {icon} idee #{id} · ✅ angenommen ☕✨",
            "title_denied":   "### {icon} idee #{id} · ❌ beiseite gelegt ☕",
            "body":           "{text}\n\n-# von {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**urteil von {who}:** {reason}",
        },
        "es": {
            "no_channel":     "❌ aún no hay rincón de sugerencias — un admin debe correr `suggest channel <canal>` primero ☕",
            "submitted":      "✅ pegué tu idea en {channel} — `#{id}` ☕✨",
            "channel_set":    "✅ el rincón de sugerencias ahora es {channel} ☕",
            "config_title":   "### {icon} rincón de sugerencias ☕",
            "config_body":    "**canal:** {channel}",
            "missing":        "⚠️ no hay idea con id `#{id}` aquí~",
            "approved":       "✅ idea `#{id}` preparada y aprobada ☕✨",
            "denied":         "✅ idea `#{id}` apartada con cariño ☕",
            "title_open":     "### {icon} idea #{id} ☕",
            "title_approved": "### {icon} idea #{id} · ✅ aprobada ☕✨",
            "title_denied":   "### {icon} idea #{id} · ❌ apartada ☕",
            "body":           "{text}\n\n-# por {author}",
            "votes":          "👍 `{up}`  👎 `{down}`",
            "verdict":        "**veredicto de {who}:** {reason}",
        },
    },
}


def _lang(ctx) -> str:
    g = getattr(ctx, "guild", None)
    if g and g.preferred_locale:
        l = str(g.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def _personality(ctx) -> str:
    if isinstance(ctx, commands.Context):
        return get_personality(ctx)
    class _S: pass
    s = _S()
    s.guild = getattr(ctx, "guild", None) if not isinstance(ctx, discord.Guild) else ctx
    return get_personality(s)


msg = make_msg(MESSAGES)


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"guilds": {}}
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
            d.setdefault("guilds", {})
            return d
    except Exception:
        return {"guilds": {}}


def _save(d: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


# ───────────────────────────────────────────────────
#  VOTE BUTTONS
# ───────────────────────────────────────────────────

class _UpBtn(discord.ui.Button):
    def __init__(self, sid: int):
        super().__init__(emoji="👍", style=discord.ButtonStyle.success,
                         custom_id=f"sug_up:{sid}")
        self.sid = sid

    async def callback(self, interaction: discord.Interaction):
        cog: "Suggestions" = interaction.client.get_cog("Suggestions")
        if cog:
            await cog.handle_vote(interaction, self.sid, +1)


class _DownBtn(discord.ui.Button):
    def __init__(self, sid: int):
        super().__init__(emoji="👎", style=discord.ButtonStyle.danger,
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

    title = msg(ctx_like, title_key, icon=get_emoji("icon_lightbulb"), id=s["id"])
    author = ctx_like.guild.get_member(s["author_id"]) if (ctx_like and ctx_like.guild) else None
    author_str = author.mention if author else f"<@{s['author_id']}>"
    body = msg(ctx_like, "body", text=s["text"], author=author_str)
    votes = msg(ctx_like, "votes", up=s.get("up", 0), down=s.get("down", 0))

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
        self.data = _load()
        self._reattach()

    def _g(self, gid: int) -> dict:
        return self.data["guilds"].setdefault(str(gid), {
            "channel_id": None,
            "next_id": 1,
            "items": {},
        })

    def _reattach(self):
        for gid_str, g in self.data["guilds"].items():
            for sid_str, s in g["items"].items():
                if s.get("status") == "open":
                    try:
                        view = _build_view(s, None)
                        self.bot.add_view(view, message_id=s["message_id"])
                    except Exception:
                        pass

    @commands.hybrid_group(
        name="suggest",
        description="Submit and manage suggestions.",
        help="{ 'en': 'Submit and manage suggestions.', 'de': 'Vorschläge einreichen und verwalten.', 'es': 'Envía y gestiona sugerencias.' }",
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def suggest(self, ctx: commands.Context, *, text: str = None):
        if text:
            return await self._submit(ctx, text)
        await ctx.send_help(self.suggest)

    @suggest.command(
        name="submit",
        description="Submit a suggestion.",
        help="{ 'en': 'Submit a suggestion.', 'de': 'Einen Vorschlag einreichen.', 'es': 'Envía una sugerencia.' }",
    )
    async def suggest_submit(self, ctx: commands.Context, *, text: str):
        await self._submit(ctx, text)

    async def _submit(self, ctx: commands.Context, text: str):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g.get("channel_id") or 0) if g.get("channel_id") else None
        if not ch:
            return await ctx.send(msg(ctx, "no_channel"))
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
        _save(self.data)
        try:
            self.bot.add_view(_build_view(s, ctx), message_id=sent.id)
        except Exception:
            pass

        if ctx.interaction:
            await ctx.send(msg(ctx, "submitted", channel=ch.mention, id=sid), ephemeral=True)
        else:
            await ctx.send(msg(ctx, "submitted", channel=ch.mention, id=sid))

    @suggest.command(
        name="channel",
        description="Set the suggestion channel.",
        help="{ 'en': 'Set the suggestion channel (admin).', 'de': 'Vorschlagskanal setzen (Admin).', 'es': 'Establece el canal de sugerencias (admin).' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        g["channel_id"] = channel.id
        _save(self.data)
        await ctx.send(msg(ctx, "channel_set", channel=channel.mention))

    @suggest.command(
        name="config",
        description="Show suggestion config.",
        help="{ 'en': 'Show suggestion config.', 'de': 'Vorschlags-Konfiguration anzeigen.', 'es': 'Muestra la configuración de sugerencias.' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_config(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g.get("channel_id") or 0) if g.get("channel_id") else None
        view = discord.ui.LayoutView()
        body = msg(ctx, "config_title", icon=get_emoji("icon_settings")) + "\n" + \
            msg(ctx, "config_body", channel=ch.mention if ch else "—")
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=body)))
        await ctx.send(view=view)

    @suggest.command(
        name="approve",
        description="Approve a suggestion.",
        help="{ 'en': 'Approve a suggestion (manage_guild).', 'de': 'Einen Vorschlag annehmen (manage_guild).', 'es': 'Aprueba una sugerencia (manage_guild).' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_approve(self, ctx: commands.Context, suggestion_id: int, *, reason: str = "—"):
        await self._verdict(ctx, suggestion_id, "approved", reason, "approved")

    @suggest.command(
        name="deny",
        description="Deny a suggestion.",
        help="{ 'en': 'Deny a suggestion (manage_guild).', 'de': 'Einen Vorschlag ablehnen (manage_guild).', 'es': 'Deniega una sugerencia (manage_guild).' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def suggest_deny(self, ctx: commands.Context, suggestion_id: int, *, reason: str = "—"):
        await self._verdict(ctx, suggestion_id, "denied", reason, "denied")

    async def _verdict(self, ctx, sid: int, status: str, reason: str, ack_key: str):
        g = self._g(ctx.guild.id)
        s = g["items"].get(str(sid))
        if not s:
            return await ctx.send(msg(ctx, "missing", id=sid))
        s["status"] = status
        s["verdict"] = {"by": ctx.author.mention, "reason": reason[:500]}
        _save(self.data)
        ch = ctx.guild.get_channel(s["channel_id"])
        if ch:
            try:
                m = await ch.fetch_message(s["message_id"])
                await m.edit(view=_build_view(s, ctx))
            except Exception:
                pass
        await ctx.send(msg(ctx, ack_key, id=sid))

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
        _save(self.data)

        try:
            await interaction.response.edit_message(view=_build_view(s, interaction))
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Suggestions(bot))
