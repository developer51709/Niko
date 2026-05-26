"""
Reminders — premium personal reminder system with persistent JSON storage.

Commands (single `reminder` group):
    reminder set <duration> <text>   — schedule a reminder (1m, 2h, 3d, …)
    reminder list                    — list your active reminders
    reminder delete <id>             — delete a reminder you own
    reminder clear                   — delete all your reminders
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import discord
from discord.ext import commands, tasks

from config.emojis import get_emoji
from utils.ai.config import get_personality

DATA_FILE = "data/reminders.json"


# ───────────────────────────────────────────────────
#  TRILINGUAL MESSAGES
# ───────────────────────────────────────────────────

MESSAGES = {
    "normal": {
        "en": {
            "set_ok":          "### {icon} Reminder Set\nI will remind you about **{text}** {ts}.",
            "list_empty":      "You have no active reminders.",
            "list_title":      "### {icon} Your Reminders",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ Reminder `{id}` deleted.",
            "delete_missing":  "⚠️ No reminder with ID `{id}` found that belongs to you.",
            "clear_ok":        "✅ Cleared all your reminders.",
            "invalid_duration":"❌ Invalid duration. Use forms like `30s`, `10m`, `2h`, `1d`.",
            "remind_dm":       "### {icon} Reminder\n{text}\n-# Set {ago} ago.",
            "remind_chan":     "### {icon} Reminder for {mention}\n{text}\n-# Set {ago} ago.",
        },
        "de": {
            "set_ok":          "### {icon} Erinnerung gesetzt\nIch erinnere dich an **{text}** {ts}.",
            "list_empty":      "Du hast keine aktiven Erinnerungen.",
            "list_title":      "### {icon} Deine Erinnerungen",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ Erinnerung `{id}` gelöscht.",
            "delete_missing":  "⚠️ Keine Erinnerung mit ID `{id}` gefunden, die dir gehört.",
            "clear_ok":        "✅ Alle Erinnerungen gelöscht.",
            "invalid_duration":"❌ Ungültige Dauer. Verwende `30s`, `10m`, `2h`, `1d`.",
            "remind_dm":       "### {icon} Erinnerung\n{text}\n-# vor {ago} gesetzt.",
            "remind_chan":     "### {icon} Erinnerung für {mention}\n{text}\n-# vor {ago} gesetzt.",
        },
        "es": {
            "set_ok":          "### {icon} Recordatorio establecido\nTe recordaré sobre **{text}** {ts}.",
            "list_empty":      "No tienes recordatorios activos.",
            "list_title":      "### {icon} Tus recordatorios",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ Recordatorio `{id}` eliminado.",
            "delete_missing":  "⚠️ No se encontró un recordatorio con ID `{id}` que te pertenezca.",
            "clear_ok":        "✅ Todos tus recordatorios eliminados.",
            "invalid_duration":"❌ Duración inválida. Usa `30s`, `10m`, `2h`, `1d`.",
            "remind_dm":       "### {icon} Recordatorio\n{text}\n-# Establecido hace {ago}.",
            "remind_chan":     "### {icon} Recordatorio para {mention}\n{text}\n-# Establecido hace {ago}.",
        },
    },
    "cafe": {
        "en": {
            "set_ok":          "### {icon} reminder saved ☕\nI'll nudge you about **{text}** {ts} ✨",
            "list_empty":      "no reminders yet — your café notebook is empty ☕",
            "list_title":      "### {icon} your cozy reminders ☕",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ reminder `{id}` torn out of the notebook ☕",
            "delete_missing":  "⚠️ couldn't find reminder `{id}` in your notebook hun~",
            "clear_ok":        "✅ wiped your reminder notebook clean ☕",
            "invalid_duration":"❌ that duration looks weird, try `30s`, `10m`, `2h`, `1d` ☕",
            "remind_dm":       "### {icon} hey hey ☕\n{text}\n-# you saved this {ago} ago ✨",
            "remind_chan":     "### {icon} hey {mention} ☕\n{text}\n-# saved {ago} ago ✨",
        },
        "de": {
            "set_ok":          "### {icon} erinnerung gespeichert ☕\nich stupse dich an **{text}** {ts} ✨",
            "list_empty":      "noch keine erinnerungen — dein café-notizbuch ist leer ☕",
            "list_title":      "### {icon} deine gemütlichen erinnerungen ☕",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ erinnerung `{id}` aus dem notizbuch gerissen ☕",
            "delete_missing":  "⚠️ konnte erinnerung `{id}` in deinem notizbuch nicht finden~",
            "clear_ok":        "✅ dein notizbuch ist sauber ☕",
            "invalid_duration":"❌ die dauer sieht komisch aus, versuch `30s`, `10m`, `2h`, `1d` ☕",
            "remind_dm":       "### {icon} hey hey ☕\n{text}\n-# vor {ago} gespeichert ✨",
            "remind_chan":     "### {icon} hey {mention} ☕\n{text}\n-# vor {ago} gespeichert ✨",
        },
        "es": {
            "set_ok":          "### {icon} recordatorio guardado ☕\nte daré un toque sobre **{text}** {ts} ✨",
            "list_empty":      "sin recordatorios aún — tu cuaderno del café está vacío ☕",
            "list_title":      "### {icon} tus recordatorios acogedores ☕",
            "list_entry":      "**`{id}`** · {when}\n-# {text}",
            "delete_ok":       "✅ recordatorio `{id}` arrancado del cuaderno ☕",
            "delete_missing":  "⚠️ no encontré el recordatorio `{id}` en tu cuaderno~",
            "clear_ok":        "✅ tu cuaderno está limpio ☕",
            "invalid_duration":"❌ la duración se ve rara, prueba `30s`, `10m`, `2h`, `1d` ☕",
            "remind_dm":       "### {icon} oye ☕\n{text}\n-# lo guardaste hace {ago} ✨",
            "remind_chan":     "### {icon} oye {mention} ☕\n{text}\n-# guardado hace {ago} ✨",
        },
    },
}


def _lang(ctx) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        l = str(ctx.guild.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def msg(ctx, key: str, **kwargs) -> str:
    p = get_personality(ctx) if isinstance(ctx, commands.Context) else "cafe"
    lang = _lang(ctx)
    table = MESSAGES.get(p, MESSAGES["normal"])
    text = (
        table.get(lang, {}).get(key)
        or table.get("en", {}).get(key)
        or MESSAGES["normal"]["en"].get(key, key)
    )
    return text.format(**kwargs) if kwargs else text


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


# ───────────────────────────────────────────────────
#  DURATION PARSER
# ───────────────────────────────────────────────────

DURATION_RE = re.compile(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?$")


def parse_duration(text: str) -> Optional[int]:
    text = text.strip().lower()
    if not text:
        return None
    m = DURATION_RE.fullmatch(text.replace(" ", ""))
    if not m or not any(m.groups()):
        return None
    d, h, mi, s = (int(g or 0) for g in m.groups())
    total = d * 86400 + h * 3600 + mi * 60 + s
    return total or None


def humanize_delta(seconds: int) -> str:
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, s = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {s}s" if s else f"{minutes}m"
    hours, mi = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {mi}m" if mi else f"{hours}h"
    days, hr = divmod(hours, 24)
    return f"{days}d {hr}h" if hr else f"{days}d"


# ───────────────────────────────────────────────────
#  STORAGE
# ───────────────────────────────────────────────────

def _load() -> Dict[str, dict]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class Reminders(commands.Cog):
    """Premium personal reminder system."""

    def __init__(self, bot):
        self.bot = bot
        self.reminders: Dict[str, dict] = _load()
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    @tasks.loop(seconds=15)
    async def check_loop(self):
        now = datetime.now(timezone.utc)
        fired: List[str] = []
        for rid, r in list(self.reminders.items()):
            try:
                due = datetime.fromisoformat(r["due_at"])
            except Exception:
                fired.append(rid)
                continue
            if now < due:
                continue
            await self._fire(r)
            fired.append(rid)
        if fired:
            for rid in fired:
                self.reminders.pop(rid, None)
            _save(self.reminders)

    @check_loop.before_loop
    async def _before(self):
        await self.bot.wait_until_ready()

    async def _fire(self, r: dict):
        user = self.bot.get_user(r["user_id"]) or await self.bot.fetch_user(r["user_id"])
        if not user:
            return
        ago = humanize_delta(int((datetime.now(timezone.utc) - datetime.fromisoformat(r["created_at"])).total_seconds()))
        # personality/lang shim (use guild if remembered, else cafe en)
        guild = self.bot.get_guild(r.get("guild_id") or 0)

        class _Shim:
            pass
        s = _Shim(); s.guild = guild
        text = msg(s, "remind_dm", icon=get_emoji("icon_loading"), text=r["text"], ago=ago)
        # try DM first
        try:
            await user.send(view=cv2(text))
            return
        except Exception:
            pass
        # fallback to original channel
        ch_id = r.get("channel_id")
        if ch_id:
            ch = self.bot.get_channel(ch_id)
            if ch:
                try:
                    await ch.send(content=user.mention, view=cv2(
                        msg(s, "remind_chan", icon=get_emoji("icon_loading"),
                            mention=user.mention, text=r["text"], ago=ago)))
                except Exception:
                    pass

    # ───── group ────────────────────────────────

    @commands.hybrid_group(
        name="reminder",
        description="Personal reminders.",
        help="{ 'en': 'Personal reminders (set, list, delete).', 'de': 'Persönliche Erinnerungen.', 'es': 'Recordatorios personales.' }",
        invoke_without_command=True,
    )
    async def reminder(self, ctx: commands.Context):
        await ctx.send_help(self.reminder)

    @reminder.command(
        name="set",
        description="Schedule a reminder.",
        help="{ 'en': 'Schedule a reminder. Example: reminder set 30m drink water', 'de': 'Eine Erinnerung planen. Beispiel: reminder set 30m Wasser trinken', 'es': 'Programa un recordatorio. Ejemplo: reminder set 30m beber agua' }",
    )
    async def reminder_set(self, ctx: commands.Context, duration: str, *, text: str):
        secs = parse_duration(duration)
        if secs is None or secs > 60 * 60 * 24 * 365:
            return await ctx.send(view=cv2(msg(ctx, "invalid_duration")))
        due = datetime.now(timezone.utc) + timedelta(seconds=secs)
        rid = uuid.uuid4().hex[:6]
        self.reminders[rid] = {
            "id": rid,
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id if ctx.guild else None,
            "channel_id": ctx.channel.id if ctx.channel else None,
            "text": text[:1500],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "due_at": due.isoformat(),
        }
        _save(self.reminders)
        ts = f"<t:{int(due.timestamp())}:R>"
        await ctx.send(view=cv2(msg(ctx, "set_ok", icon=get_emoji("icon_loading"), text=text, ts=ts)))

    @reminder.command(
        name="list",
        description="List your active reminders.",
        help="{ 'en': 'List your active reminders.', 'de': 'Deine aktiven Erinnerungen anzeigen.', 'es': 'Lista tus recordatorios activos.' }",
    )
    async def reminder_list(self, ctx: commands.Context):
        mine = [r for r in self.reminders.values() if r["user_id"] == ctx.author.id]
        if not mine:
            return await ctx.send(view=cv2(msg(ctx, "list_empty")))
        mine.sort(key=lambda r: r["due_at"])
        lines = []
        for r in mine[:25]:
            try:
                ts = int(datetime.fromisoformat(r["due_at"]).timestamp())
                when = f"<t:{ts}:R>"
            except Exception:
                when = "?"
            lines.append(msg(ctx, "list_entry", id=r["id"], when=when, text=r["text"][:200]))
        body = msg(ctx, "list_title", icon=get_emoji("icon_loading")) + "\n" + "\n".join(lines)
        await ctx.send(view=cv2(body))

    @reminder.command(
        name="delete",
        description="Delete one of your reminders.",
        help="{ 'en': 'Delete a reminder by its ID.', 'de': 'Erinnerung anhand der ID löschen.', 'es': 'Elimina un recordatorio por su ID.' }",
    )
    async def reminder_delete(self, ctx: commands.Context, reminder_id: str):
        r = self.reminders.get(reminder_id)
        if not r or r["user_id"] != ctx.author.id:
            return await ctx.send(view=cv2(msg(ctx, "delete_missing", id=reminder_id)))
        self.reminders.pop(reminder_id, None)
        _save(self.reminders)
        await ctx.send(view=cv2(msg(ctx, "delete_ok", id=reminder_id)))

    @reminder.command(
        name="clear",
        description="Delete all your reminders.",
        help="{ 'en': 'Delete all your reminders.', 'de': 'Alle deine Erinnerungen löschen.', 'es': 'Elimina todos tus recordatorios.' }",
    )
    async def reminder_clear(self, ctx: commands.Context):
        self.reminders = {rid: r for rid, r in self.reminders.items() if r["user_id"] != ctx.author.id}
        _save(self.reminders)
        await ctx.send(view=cv2(msg(ctx, "clear_ok")))


async def setup(bot):
    await bot.add_cog(Reminders(bot))
