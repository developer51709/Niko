"""
Starboard — repost popular messages to a starboard channel based on ⭐ reactions.

Commands (single `starboard` group, manage_guild required):
    starboard channel <channel>  — set the starboard channel
    starboard threshold <n>      — set the star threshold (default 3)
    starboard emoji <emoji>      — set the trigger emoji (default ⭐)
    starboard ignore <channel>   — ignore a channel (no starring from it)
    starboard unignore <channel> — stop ignoring a channel
    starboard disable            — turn the starboard off
    starboard config             — show current config
"""

from __future__ import annotations

import json
import os
from typing import Dict

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.ai_config import get_personality

DATA_FILE = "data/starboard.json"
DEFAULT_THRESHOLD = 3
DEFAULT_EMOJI = "⭐"


MESSAGES = {
    "normal": {
        "en": {
            "channel_set":   "✅ Starboard channel set to {channel}.",
            "threshold_set": "✅ Threshold set to **{n}**.",
            "emoji_set":     "✅ Starboard emoji set to {emoji}.",
            "ignored":       "✅ Now ignoring {channel}.",
            "unignored":     "✅ No longer ignoring {channel}.",
            "disabled":      "✅ Starboard disabled.",
            "config_title":  "### {icon} Starboard Config",
            "config_body":   "**Channel:** {channel}\n**Threshold:** `{threshold}`\n**Emoji:** {emoji}\n**Ignored channels:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
        "de": {
            "channel_set":   "✅ Starboard-Kanal auf {channel} gesetzt.",
            "threshold_set": "✅ Schwelle auf **{n}** gesetzt.",
            "emoji_set":     "✅ Starboard-Emoji auf {emoji} gesetzt.",
            "ignored":       "✅ Ignoriere jetzt {channel}.",
            "unignored":     "✅ Ignoriere {channel} nicht mehr.",
            "disabled":      "✅ Starboard deaktiviert.",
            "config_title":  "### {icon} Starboard-Konfiguration",
            "config_body":   "**Kanal:** {channel}\n**Schwelle:** `{threshold}`\n**Emoji:** {emoji}\n**Ignorierte Kanäle:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
        "es": {
            "channel_set":   "✅ Canal del starboard establecido en {channel}.",
            "threshold_set": "✅ Umbral establecido en **{n}**.",
            "emoji_set":     "✅ Emoji del starboard establecido en {emoji}.",
            "ignored":       "✅ Ahora ignorando {channel}.",
            "unignored":     "✅ Ya no se ignora {channel}.",
            "disabled":      "✅ Starboard desactivado.",
            "config_title":  "### {icon} Configuración del Starboard",
            "config_body":   "**Canal:** {channel}\n**Umbral:** `{threshold}`\n**Emoji:** {emoji}\n**Canales ignorados:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
    },
    "cafe": {
        "en": {
            "channel_set":   "✅ starboard wall is now {channel} ☕✨",
            "threshold_set": "✅ stars needed: **{n}** ✨",
            "emoji_set":     "✅ trigger emoji is now {emoji} ☕",
            "ignored":       "✅ ignoring {channel} from now on ☕",
            "unignored":     "✅ listening to {channel} again ☕",
            "disabled":      "✅ starboard turned off cozily ☕",
            "config_title":  "### {icon} starboard wall ☕✨",
            "config_body":   "**channel:** {channel}\n**threshold:** `{threshold}`\n**emoji:** {emoji}\n**ignored channels:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
        "de": {
            "channel_set":   "✅ starboard-wand ist jetzt {channel} ☕✨",
            "threshold_set": "✅ benötigte sterne: **{n}** ✨",
            "emoji_set":     "✅ trigger-emoji ist jetzt {emoji} ☕",
            "ignored":       "✅ ignoriere {channel} ab jetzt ☕",
            "unignored":     "✅ höre {channel} wieder zu ☕",
            "disabled":      "✅ starboard gemütlich ausgeschaltet ☕",
            "config_title":  "### {icon} starboard-wand ☕✨",
            "config_body":   "**kanal:** {channel}\n**schwelle:** `{threshold}`\n**emoji:** {emoji}\n**ignorierte kanäle:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
        "es": {
            "channel_set":   "✅ pared del starboard ahora es {channel} ☕✨",
            "threshold_set": "✅ estrellas necesarias: **{n}** ✨",
            "emoji_set":     "✅ emoji activador es ahora {emoji} ☕",
            "ignored":       "✅ ignorando {channel} desde ahora ☕",
            "unignored":     "✅ volviendo a escuchar {channel} ☕",
            "disabled":      "✅ starboard apagado acogedoramente ☕",
            "config_title":  "### {icon} pared del starboard ☕✨",
            "config_body":   "**canal:** {channel}\n**umbral:** `{threshold}`\n**emoji:** {emoji}\n**canales ignorados:** {ignored}",
            "starred":       "{emoji} **{count}** · {channel}",
        },
    },
}


def _lang(ctx) -> str:
    g = getattr(ctx, "guild", None) if not isinstance(ctx, discord.Guild) else ctx
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
    s.guild = ctx if isinstance(ctx, discord.Guild) else getattr(ctx, "guild", None)
    return get_personality(s)


def msg(ctx, key: str, **kw) -> str:
    p = _personality(ctx)
    lang = _lang(ctx)
    table = MESSAGES.get(p, MESSAGES["normal"])
    text = table.get(lang, {}).get(key) or table.get("en", {}).get(key) or MESSAGES["normal"]["en"].get(key, key)
    return text.format(**kw) if kw else text


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"guilds": {}, "starred": {}}
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
            d.setdefault("guilds", {})
            d.setdefault("starred", {})
            return d
    except Exception:
        return {"guilds": {}, "starred": {}}


def _save(d: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


class Starboard(commands.Cog):
    """Star-based highlight wall for popular messages."""

    def __init__(self, bot):
        self.bot = bot
        self.data = _load()

    def _g(self, gid: int) -> dict:
        return self.data["guilds"].setdefault(str(gid), {
            "channel_id": None,
            "threshold": DEFAULT_THRESHOLD,
            "emoji": DEFAULT_EMOJI,
            "ignored_channels": [],
        })

    @commands.hybrid_group(
        name="starboard",
        description="Starboard configuration.",
        help="{ 'en': 'Starboard configuration (admin).', 'de': 'Starboard-Konfiguration (Admin).', 'es': 'Configuración del starboard (admin).' }",
        invoke_without_command=True,
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def starboard(self, ctx: commands.Context):
        await ctx.send_help(self.starboard)

    @starboard.command(
        name="channel",
        description="Set the starboard channel.",
        help="{ 'en': 'Set the starboard channel.', 'de': 'Starboard-Kanal setzen.', 'es': 'Establece el canal del starboard.' }",
    )
    async def starboard_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        g["channel_id"] = channel.id
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "channel_set", channel=channel.mention)))

    @starboard.command(
        name="threshold",
        description="Set the star threshold.",
        help="{ 'en': 'Set the star threshold (default 3).', 'de': 'Stern-Schwelle setzen (Standard 3).', 'es': 'Establece el umbral de estrellas (por defecto 3).' }",
    )
    async def starboard_threshold(self, ctx: commands.Context, count: int):
        count = max(1, min(50, count))
        g = self._g(ctx.guild.id)
        g["threshold"] = count
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "threshold_set", n=count)))

    @starboard.command(
        name="emoji",
        description="Set the trigger emoji.",
        help="{ 'en': 'Set the trigger emoji (default ⭐).', 'de': 'Trigger-Emoji setzen (Standard ⭐).', 'es': 'Establece el emoji activador (por defecto ⭐).' }",
    )
    async def starboard_emoji(self, ctx: commands.Context, emoji: str):
        g = self._g(ctx.guild.id)
        g["emoji"] = emoji
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "emoji_set", emoji=emoji)))

    @starboard.command(
        name="ignore",
        description="Ignore a channel.",
        help="{ 'en': 'Stop the starboard from picking up messages from this channel.', 'de': 'Nachrichten dieses Kanals nicht mehr aufnehmen.', 'es': 'Deja de recoger mensajes de este canal.' }",
    )
    async def starboard_ignore(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        if channel.id not in g["ignored_channels"]:
            g["ignored_channels"].append(channel.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "ignored", channel=channel.mention)))

    @starboard.command(
        name="unignore",
        description="Stop ignoring a channel.",
        help="{ 'en': 'Stop ignoring a channel.', 'de': 'Einen Kanal nicht mehr ignorieren.', 'es': 'Deja de ignorar un canal.' }",
    )
    async def starboard_unignore(self, ctx: commands.Context, channel: discord.TextChannel):
        g = self._g(ctx.guild.id)
        if channel.id in g["ignored_channels"]:
            g["ignored_channels"].remove(channel.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "unignored", channel=channel.mention)))

    @starboard.command(
        name="disable",
        description="Disable the starboard.",
        help="{ 'en': 'Disable the starboard.', 'de': 'Starboard deaktivieren.', 'es': 'Desactiva el starboard.' }",
    )
    async def starboard_disable(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        g["channel_id"] = None
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "disabled")))

    @starboard.command(
        name="config",
        description="Show current starboard config.",
        help="{ 'en': 'Show the current starboard config.', 'de': 'Aktuelle Starboard-Konfiguration anzeigen.', 'es': 'Muestra la configuración actual del starboard.' }",
    )
    async def starboard_config(self, ctx: commands.Context):
        g = self._g(ctx.guild.id)
        ch = ctx.guild.get_channel(g["channel_id"]) if g.get("channel_id") else None
        ignored = ", ".join(f"<#{c}>" for c in g["ignored_channels"]) or "—"
        body = msg(ctx, "config_title", icon=get_emoji("icon_settings")) + "\n" + msg(
            ctx, "config_body",
            channel=ch.mention if ch else "—",
            threshold=g["threshold"],
            emoji=g["emoji"],
            ignored=ignored,
        )
        await ctx.send(view=cv2(body))

    # ───── reaction handler ───────────────────────

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self._on_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self._on_reaction(payload)

    async def _on_reaction(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return
        g = self.data["guilds"].get(str(payload.guild_id))
        if not g or not g.get("channel_id"):
            return
        emoji_str = str(payload.emoji)
        if emoji_str != g.get("emoji", DEFAULT_EMOJI):
            return
        if payload.channel_id in g.get("ignored_channels", []):
            return
        if payload.channel_id == g["channel_id"]:
            return  # ignore reactions on the starboard itself

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return
        if message.author.bot:
            return

        # count the trigger reaction
        count = 0
        for r in message.reactions:
            if str(r.emoji) == g["emoji"]:
                count = r.count
                break

        starboard_ch = guild.get_channel(g["channel_id"])
        if not starboard_ch:
            return

        starred = self.data["starred"].setdefault(str(payload.guild_id), {})
        existing_id = starred.get(str(message.id))

        if count >= g["threshold"]:
            view = self._build_starred_view(message, count, g)
            if existing_id:
                try:
                    m = await starboard_ch.fetch_message(int(existing_id))
                    await m.edit(view=view)
                    return
                except Exception:
                    pass
            try:
                sent = await starboard_ch.send(view=view)
                starred[str(message.id)] = sent.id
                _save(self.data)
            except Exception:
                pass
        else:
            # below threshold — remove if present
            if existing_id:
                try:
                    m = await starboard_ch.fetch_message(int(existing_id))
                    await m.delete()
                except Exception:
                    pass
                starred.pop(str(message.id), None)
                _save(self.data)

    def _build_starred_view(self, message: discord.Message, count: int, g: dict) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView(timeout=None)

        header = msg(message.guild, "starred",
                     emoji=g.get("emoji", DEFAULT_EMOJI),
                     count=count,
                     channel=message.channel.mention)

        body_parts = [
            f"### {header}",
            f"**{message.author.display_name}** · <t:{int(message.created_at.timestamp())}:R>",
        ]
        if message.content:
            txt = message.content
            if len(txt) > 1500:
                txt = txt[:1500] + "…"
            body_parts.append(txt)

        body_parts.append(f"[Jump to message]({message.jump_url})")

        container = discord.ui.Container(
            discord.ui.TextDisplay(content="\n\n".join(body_parts)),
        )

        # Embed first attachment as media if it's an image
        att_image = None
        for att in message.attachments:
            if (att.content_type or "").startswith("image/") or att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                att_image = att.url
                break
        if att_image:
            container.add_item(
                discord.ui.MediaGallery(discord.MediaGalleryItem(media=att_image))
            )

        view.add_item(container)
        return view


async def setup(bot):
    await bot.add_cog(Starboard(bot))
