"""
Highlights — keyword-based DM notifications.

Commands (single `highlight` group):
    highlight add <keyword>      — add a keyword (DM you when said in this server)
    highlight remove <keyword>   — remove a keyword
    highlight list               — list your keywords for this server
    highlight clear              — remove all your keywords for this server
    highlight ignore user <user> — ignore a user
    highlight ignore channel <channel> — ignore a channel
    highlight unignore user <user>
    highlight unignore channel <channel>

Limits: 25 keywords per user per server. Cooldown of 60s per keyword per channel
to avoid spam. Won't trigger on your own messages.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Dict, List

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai.config import get_personality
from utils.i18n import make_msg

DATA_FILE = "data/highlights.json"
MAX_KEYWORDS = 25
COOLDOWN_SECONDS = 60


MESSAGES = {
    "normal": {
        "en": {
            "added":           "✅ Highlight **`{kw}`** added.",
            "removed":         "✅ Highlight **`{kw}`** removed.",
            "exists":          "⚠️ You already have **`{kw}`** as a highlight.",
            "missing":         "⚠️ You don't have **`{kw}`** as a highlight.",
            "limit":           "⚠️ You've reached the highlight limit ({max}). Remove some first.",
            "list_empty":      "You have no highlights in this server.",
            "list_title":      "### {icon} Your Highlights",
            "cleared":         "✅ All highlights removed.",
            "ignore_user_ok":  "✅ Ignoring {user}.",
            "ignore_chan_ok":  "✅ Ignoring {channel}.",
            "unignore_user_ok":"✅ No longer ignoring {user}.",
            "unignore_chan_ok":"✅ No longer ignoring {channel}.",
            "notify_title":    "### {icon} Highlight: `{kw}`",
            "notify_body":     "**In:** {channel} of **{guild}**\n**By:** {author}\n\n{quote}\n\n[Jump to message]({link})",
        },
        "de": {
            "added":           "✅ Highlight **`{kw}`** hinzugefügt.",
            "removed":         "✅ Highlight **`{kw}`** entfernt.",
            "exists":          "⚠️ Du hast **`{kw}`** bereits als Highlight.",
            "missing":         "⚠️ Du hast **`{kw}`** nicht als Highlight.",
            "limit":           "⚠️ Du hast das Highlight-Limit ({max}) erreicht. Entferne zuerst einige.",
            "list_empty":      "Du hast keine Highlights auf diesem Server.",
            "list_title":      "### {icon} Deine Highlights",
            "cleared":         "✅ Alle Highlights entfernt.",
            "ignore_user_ok":  "✅ Ignoriere {user}.",
            "ignore_chan_ok":  "✅ Ignoriere {channel}.",
            "unignore_user_ok":"✅ Ignoriere {user} nicht mehr.",
            "unignore_chan_ok":"✅ Ignoriere {channel} nicht mehr.",
            "notify_title":    "### {icon} Highlight: `{kw}`",
            "notify_body":     "**In:** {channel} auf **{guild}**\n**Von:** {author}\n\n{quote}\n\n[Zur Nachricht springen]({link})",
        },
        "es": {
            "added":           "✅ Highlight **`{kw}`** añadido.",
            "removed":         "✅ Highlight **`{kw}`** eliminado.",
            "exists":          "⚠️ Ya tienes **`{kw}`** como highlight.",
            "missing":         "⚠️ No tienes **`{kw}`** como highlight.",
            "limit":           "⚠️ Has alcanzado el límite de highlights ({max}). Elimina algunos primero.",
            "list_empty":      "No tienes highlights en este servidor.",
            "list_title":      "### {icon} Tus Highlights",
            "cleared":         "✅ Todos los highlights eliminados.",
            "ignore_user_ok":  "✅ Ignorando a {user}.",
            "ignore_chan_ok":  "✅ Ignorando {channel}.",
            "unignore_user_ok":"✅ Ya no se ignora a {user}.",
            "unignore_chan_ok":"✅ Ya no se ignora {channel}.",
            "notify_title":    "### {icon} Highlight: `{kw}`",
            "notify_body":     "**En:** {channel} de **{guild}**\n**Por:** {author}\n\n{quote}\n\n[Saltar al mensaje]({link})",
        },
    },
    "cafe": {
        "en": {
            "added":           "✅ pinned **`{kw}`** to your highlight board ☕",
            "removed":         "✅ took **`{kw}`** off your highlight board ☕",
            "exists":          "⚠️ **`{kw}`** is already on your board ☕",
            "missing":         "⚠️ no **`{kw}`** on your board hun~",
            "limit":           "⚠️ board is full ({max} pins) — take some down first ☕",
            "list_empty":      "your highlight board is empty ☕",
            "list_title":      "### {icon} your highlight board ☕",
            "cleared":         "✅ wiped your highlight board clean ☕",
            "ignore_user_ok":  "✅ ignoring {user} from now on ☕",
            "ignore_chan_ok":  "✅ ignoring {channel} from now on ☕",
            "unignore_user_ok":"✅ listening to {user} again ☕",
            "unignore_chan_ok":"✅ listening to {channel} again ☕",
            "notify_title":    "### {icon} highlight! `{kw}` ☕",
            "notify_body":     "**in:** {channel} of **{guild}**\n**by:** {author}\n\n{quote}\n\n[hop over]({link}) ✨",
        },
        "de": {
            "added":           "✅ **`{kw}`** an dein highlight-board gepinnt ☕",
            "removed":         "✅ **`{kw}`** vom highlight-board genommen ☕",
            "exists":          "⚠️ **`{kw}`** ist schon auf deinem board ☕",
            "missing":         "⚠️ kein **`{kw}`** auf deinem board~",
            "limit":           "⚠️ board ist voll ({max} pins) — nimm zuerst welche ab ☕",
            "list_empty":      "dein highlight-board ist leer ☕",
            "list_title":      "### {icon} dein highlight-board ☕",
            "cleared":         "✅ dein highlight-board ist sauber ☕",
            "ignore_user_ok":  "✅ ignoriere {user} ab jetzt ☕",
            "ignore_chan_ok":  "✅ ignoriere {channel} ab jetzt ☕",
            "unignore_user_ok":"✅ höre {user} wieder zu ☕",
            "unignore_chan_ok":"✅ höre {channel} wieder zu ☕",
            "notify_title":    "### {icon} highlight! `{kw}` ☕",
            "notify_body":     "**in:** {channel} auf **{guild}**\n**von:** {author}\n\n{quote}\n\n[hin springen]({link}) ✨",
        },
        "es": {
            "added":           "✅ **`{kw}`** pegada en tu tablero de highlights ☕",
            "removed":         "✅ **`{kw}`** quitada del tablero ☕",
            "exists":          "⚠️ **`{kw}`** ya está en tu tablero ☕",
            "missing":         "⚠️ no hay **`{kw}`** en tu tablero~",
            "limit":           "⚠️ el tablero está lleno ({max}) — quita algunos primero ☕",
            "list_empty":      "tu tablero de highlights está vacío ☕",
            "list_title":      "### {icon} tu tablero de highlights ☕",
            "cleared":         "✅ tablero de highlights limpio ☕",
            "ignore_user_ok":  "✅ ignorando a {user} desde ahora ☕",
            "ignore_chan_ok":  "✅ ignorando {channel} desde ahora ☕",
            "unignore_user_ok":"✅ volviendo a escuchar a {user} ☕",
            "unignore_chan_ok":"✅ volviendo a escuchar {channel} ☕",
            "notify_title":    "### {icon} ¡highlight! `{kw}` ☕",
            "notify_body":     "**en:** {channel} de **{guild}**\n**por:** {author}\n\n{quote}\n\n[saltar]({link}) ✨",
        },
    },
}


def _lang(ctx) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        l = str(ctx.guild.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def _personality(ctx) -> str:
    if isinstance(ctx, commands.Context):
        return get_personality(ctx)
    class _S: pass
    s = _S()
    s.guild = ctx if isinstance(ctx, discord.Guild) else getattr(ctx, "guild", None)
    return get_personality(s)


msg = make_msg(MESSAGES)


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save(d: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


class Highlights(commands.Cog):
    """Keyword-based DM notifications."""

    def __init__(self, bot):
        self.bot = bot
        self.data = _load()
        self._cooldowns: Dict[str, float] = {}

    def _user(self, gid: int, uid: int) -> dict:
        return (
            self.data
            .setdefault(str(gid), {})
            .setdefault(str(uid), {"keywords": [], "ignore_users": [], "ignore_channels": []})
        )

    # ───── group ────────────────────────────────

    @commands.hybrid_group(
        name="highlight",
        description="Keyword DM notifications.",
        help="{ 'en': 'Keyword DM notifications.', 'de': 'Schlüsselwort-DM-Benachrichtigungen.', 'es': 'Notificaciones por DM por palabras clave.' }",
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def highlight(self, ctx: commands.Context):
        await ctx.send_help(self.highlight)

    @highlight.command(
        name="add",
        description="Add a highlight keyword.",
        help="{ 'en': 'Add a highlight keyword (you\\'ll be DMed when it\\'s mentioned).', 'de': 'Schlüsselwort hinzufügen (DM bei Erwähnung).', 'es': 'Añade una palabra clave (te avisaré por DM al mencionarla).' }",
    )
    async def highlight_add(self, ctx: commands.Context, *, keyword: str):
        keyword = keyword.lower().strip()[:50]
        if not keyword:
            return
        u = self._user(ctx.guild.id, ctx.author.id)
        if keyword in u["keywords"]:
            return await ctx.send(view=cv2(msg(ctx, "exists", kw=keyword)),
                                  ephemeral=True if ctx.interaction else False)
        if len(u["keywords"]) >= MAX_KEYWORDS:
            return await ctx.send(view=cv2(msg(ctx, "limit", max=MAX_KEYWORDS)),
                                  ephemeral=True if ctx.interaction else False)
        u["keywords"].append(keyword)
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "added", kw=keyword)),
                       ephemeral=True if ctx.interaction else False)
        try:
            await ctx.message.delete()
        except Exception:
            pass

    @highlight.command(
        name="remove",
        description="Remove a highlight keyword.",
        help="{ 'en': 'Remove a highlight keyword.', 'de': 'Ein Highlight-Schlüsselwort entfernen.', 'es': 'Elimina una palabra clave de highlight.' }",
    )
    async def highlight_remove(self, ctx: commands.Context, *, keyword: str):
        keyword = keyword.lower().strip()
        u = self._user(ctx.guild.id, ctx.author.id)
        if keyword not in u["keywords"]:
            return await ctx.send(view=cv2(msg(ctx, "missing", kw=keyword)),
                                  ephemeral=True if ctx.interaction else False)
        u["keywords"].remove(keyword)
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "removed", kw=keyword)),
                       ephemeral=True if ctx.interaction else False)

    @highlight.command(
        name="list",
        description="List your highlights for this server.",
        help="{ 'en': 'List your highlights for this server.', 'de': 'Deine Highlights für diesen Server anzeigen.', 'es': 'Lista tus highlights para este servidor.' }",
    )
    async def highlight_list(self, ctx: commands.Context):
        u = self._user(ctx.guild.id, ctx.author.id)
        if not u["keywords"]:
            return await ctx.send(view=cv2(msg(ctx, "list_empty")),
                                  ephemeral=True if ctx.interaction else False)
        body = msg(ctx, "list_title", icon=get_emoji("icon_message")) + "\n" + "\n".join(
            f"• `{k}`" for k in u["keywords"]
        )
        if u["ignore_users"]:
            body += "\n\n**Ignored users:** " + ", ".join(f"<@{i}>" for i in u["ignore_users"][:20])
        if u["ignore_channels"]:
            body += "\n**Ignored channels:** " + ", ".join(f"<#{i}>" for i in u["ignore_channels"][:20])
        await ctx.send(view=cv2(body), ephemeral=True if ctx.interaction else False)

    @highlight.command(
        name="clear",
        description="Remove all your highlights for this server.",
        help="{ 'en': 'Remove all your highlights for this server.', 'de': 'Alle deine Highlights für diesen Server entfernen.', 'es': 'Elimina todos tus highlights de este servidor.' }",
    )
    async def highlight_clear(self, ctx: commands.Context):
        u = self._user(ctx.guild.id, ctx.author.id)
        u["keywords"] = []
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "cleared")), ephemeral=True if ctx.interaction else False)

    @highlight.group(
        name="ignore",
        description="Ignore users or channels.",
        help="{ 'en': 'Ignore users or channels for highlights.', 'de': 'Nutzer oder Kanäle bei Highlights ignorieren.', 'es': 'Ignora usuarios o canales para highlights.' }",
        invoke_without_command=True,
    )
    async def highlight_ignore(self, ctx: commands.Context):
        await ctx.send_help(self.highlight_ignore)

    @highlight_ignore.command(name="user")
    async def highlight_ignore_user(self, ctx: commands.Context, user: discord.Member):
        u = self._user(ctx.guild.id, ctx.author.id)
        if user.id not in u["ignore_users"]:
            u["ignore_users"].append(user.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "ignore_user_ok", user=user.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight_ignore.command(name="channel")
    async def highlight_ignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        u = self._user(ctx.guild.id, ctx.author.id)
        if channel.id not in u["ignore_channels"]:
            u["ignore_channels"].append(channel.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "ignore_chan_ok", channel=channel.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight.group(
        name="unignore",
        description="Stop ignoring users or channels.",
        help="{ 'en': 'Stop ignoring users or channels.', 'de': 'Nutzer oder Kanäle nicht mehr ignorieren.', 'es': 'Deja de ignorar usuarios o canales.' }",
        invoke_without_command=True,
    )
    async def highlight_unignore(self, ctx: commands.Context):
        await ctx.send_help(self.highlight_unignore)

    @highlight_unignore.command(name="user")
    async def highlight_unignore_user(self, ctx: commands.Context, user: discord.Member):
        u = self._user(ctx.guild.id, ctx.author.id)
        if user.id in u["ignore_users"]:
            u["ignore_users"].remove(user.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "unignore_user_ok", user=user.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight_unignore.command(name="channel")
    async def highlight_unignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        u = self._user(ctx.guild.id, ctx.author.id)
        if channel.id in u["ignore_channels"]:
            u["ignore_channels"].remove(channel.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "unignore_chan_ok", channel=channel.mention)),
                       ephemeral=True if ctx.interaction else False)

    # ───── listener ────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        gdata = self.data.get(str(message.guild.id))
        if not gdata:
            return
        content = message.content.lower()
        if not content:
            return

        for uid_str, u in gdata.items():
            try:
                uid = int(uid_str)
            except Exception:
                continue
            if uid == message.author.id:
                continue
            if message.author.id in u.get("ignore_users", []):
                continue
            if message.channel.id in u.get("ignore_channels", []):
                continue
            member = message.guild.get_member(uid)
            if not member or not message.channel.permissions_for(member).read_messages:
                continue

            for kw in u.get("keywords", []):
                if not kw:
                    continue
                if not re.search(r"\b" + re.escape(kw) + r"\b", content):
                    continue
                key = f"{uid}:{kw}:{message.channel.id}"
                now = time.monotonic()
                if now - self._cooldowns.get(key, 0) < COOLDOWN_SECONDS:
                    break
                self._cooldowns[key] = now

                quote = message.content
                if len(quote) > 800:
                    quote = quote[:800] + "…"
                quote = "\n".join(f"> {l}" for l in quote.splitlines())

                title = msg(message.guild, "notify_title", icon=get_emoji("icon_lightbulb"), kw=kw)
                body = msg(message.guild, "notify_body",
                           channel=message.channel.mention,
                           guild=message.guild.name,
                           author=message.author.mention,
                           quote=quote,
                           link=message.jump_url)
                try:
                    await member.send(view=cv2(title + "\n" + body))
                except Exception:
                    pass
                break  # one DM per message per user


async def setup(bot):
    await bot.add_cog(Highlights(bot))
