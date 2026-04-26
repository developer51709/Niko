"""
Birthdays — set/list/announce server member birthdays with optional auto role.

Commands (single `birthday` group):
    birthday set <MM-DD>       — set/update your birthday
    birthday remove            — remove your birthday
    birthday show [user]       — show a user's birthday
    birthday today             — list today's birthdays in this server
    birthday upcoming          — list upcoming birthdays (next 30 days)
    birthday channel <channel> — set the announcement channel (admin)
    birthday role <role>       — set the auto-assigned birthday role (admin)
    birthday config            — show server birthday config (admin)
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import discord
from discord.ext import commands, tasks

from config.emojis import get_emoji
from utils.ai_config import get_personality

DATA_FILE = "data/birthdays.json"
DATE_RE = re.compile(r"^\s*(\d{1,2})[-/](\d{1,2})\s*$")


MESSAGES = {
    "normal": {
        "en": {
            "set_ok":         "🎂 Your birthday has been set to **{date}**.",
            "removed":        "✅ Your birthday has been removed.",
            "invalid_date":   "❌ Invalid date. Use `MM-DD` format (e.g. `07-23`).",
            "show_self":      "🎂 Your birthday is **{date}**.",
            "show_other":     "🎂 {user}'s birthday is **{date}**.",
            "show_none":      "📭 {user} has no birthday set.",
            "today_empty":    "🎂 No birthdays today.",
            "today_title":    "### {icon} Birthdays Today",
            "upcoming_empty": "📭 No upcoming birthdays in the next 30 days.",
            "upcoming_title": "### {icon} Upcoming Birthdays",
            "channel_set":    "✅ Birthday announcement channel set to {channel}.",
            "role_set":       "✅ Birthday role set to {role}.",
            "config_title":   "### {icon} Birthday Config",
            "config_body":    "**Channel:** {channel}\n**Role:** {role}",
            "happy_birthday": "🎂🎉 happy birthday {mention}! wishing you the most wonderful day! 🎈",
        },
        "de": {
            "set_ok":         "🎂 Dein Geburtstag wurde auf **{date}** gesetzt.",
            "removed":        "✅ Dein Geburtstag wurde entfernt.",
            "invalid_date":   "❌ Ungültiges Datum. Verwende `MM-TT` (z.B. `07-23`).",
            "show_self":      "🎂 Dein Geburtstag ist **{date}**.",
            "show_other":     "🎂 {user}s Geburtstag ist **{date}**.",
            "show_none":      "📭 {user} hat keinen Geburtstag gesetzt.",
            "today_empty":    "🎂 Heute gibt es keine Geburtstage.",
            "today_title":    "### {icon} Geburtstage heute",
            "upcoming_empty": "📭 Keine Geburtstage in den nächsten 30 Tagen.",
            "upcoming_title": "### {icon} Bevorstehende Geburtstage",
            "channel_set":    "✅ Geburtstags-Ankündigungskanal auf {channel} gesetzt.",
            "role_set":       "✅ Geburtstagsrolle auf {role} gesetzt.",
            "config_title":   "### {icon} Geburtstags-Konfiguration",
            "config_body":    "**Kanal:** {channel}\n**Rolle:** {role}",
            "happy_birthday": "🎂🎉 herzlichen glückwunsch zum geburtstag {mention}! ich wünsche dir den schönsten tag! 🎈",
        },
        "es": {
            "set_ok":         "🎂 Tu cumpleaños se ha establecido en **{date}**.",
            "removed":        "✅ Tu cumpleaños se ha eliminado.",
            "invalid_date":   "❌ Fecha inválida. Usa el formato `MM-DD` (ej. `07-23`).",
            "show_self":      "🎂 Tu cumpleaños es el **{date}**.",
            "show_other":     "🎂 El cumpleaños de {user} es el **{date}**.",
            "show_none":      "📭 {user} no tiene cumpleaños configurado.",
            "today_empty":    "🎂 No hay cumpleaños hoy.",
            "today_title":    "### {icon} Cumpleaños de hoy",
            "upcoming_empty": "📭 No hay cumpleaños en los próximos 30 días.",
            "upcoming_title": "### {icon} Próximos cumpleaños",
            "channel_set":    "✅ Canal de anuncios de cumpleaños establecido en {channel}.",
            "role_set":       "✅ Rol de cumpleaños establecido en {role}.",
            "config_title":   "### {icon} Configuración de cumpleaños",
            "config_body":    "**Canal:** {channel}\n**Rol:** {role}",
            "happy_birthday": "🎂🎉 ¡feliz cumpleaños {mention}! ¡te deseo el día más maravilloso! 🎈",
        },
    },
    "cafe": {
        "en": {
            "set_ok":         "🎂 noted! your birthday is **{date}** ☕✨",
            "removed":        "✅ wiped your birthday off the calendar ☕",
            "invalid_date":   "❌ that date looks weird hun~ use `MM-DD` like `07-23` ☕",
            "show_self":      "🎂 your cozy birthday is **{date}** ☕",
            "show_other":     "🎂 {user}'s birthday is **{date}** ☕",
            "show_none":      "📭 {user} hasn't told me their birthday yet ☕",
            "today_empty":    "🎂 nobody's celebrating today — quiet café day ☕",
            "today_title":    "### {icon} cake party today ☕✨",
            "upcoming_empty": "📭 no birthdays coming up — calm café month ☕",
            "upcoming_title": "### {icon} upcoming birthdays ☕✨",
            "channel_set":    "✅ I'll yell happy birthday in {channel} ☕✨",
            "role_set":       "✅ birthday folks will get the {role} role ☕",
            "config_title":   "### {icon} birthday corner setup ☕",
            "config_body":    "**channel:** {channel}\n**role:** {role}",
            "happy_birthday": "🎂🎉 happy birthday {mention} ☕✨ wishing you the comfiest, sweetest day with extra cake 🍰",
        },
        "de": {
            "set_ok":         "🎂 notiert! dein geburtstag ist **{date}** ☕✨",
            "removed":        "✅ deinen geburtstag vom kalender gewischt ☕",
            "invalid_date":   "❌ das datum sieht komisch aus~ nutz `MM-TT` wie `07-23` ☕",
            "show_self":      "🎂 dein gemütlicher geburtstag ist **{date}** ☕",
            "show_other":     "🎂 {user}s geburtstag ist **{date}** ☕",
            "show_none":      "📭 {user} hat mir den geburtstag noch nicht verraten ☕",
            "today_empty":    "🎂 niemand feiert heute — ruhiger café-tag ☕",
            "today_title":    "### {icon} kuchenparty heute ☕✨",
            "upcoming_empty": "📭 keine geburtstage in sicht — ruhiger café-monat ☕",
            "upcoming_title": "### {icon} bevorstehende geburtstage ☕✨",
            "channel_set":    "✅ ich rufe happy birthday in {channel} ☕✨",
            "role_set":       "✅ geburtstagskinder bekommen die {role} rolle ☕",
            "config_title":   "### {icon} geburtstags-ecke setup ☕",
            "config_body":    "**kanal:** {channel}\n**rolle:** {role}",
            "happy_birthday": "🎂🎉 happy birthday {mention} ☕✨ ich wünsch dir den gemütlichsten süßesten tag mit extra kuchen 🍰",
        },
        "es": {
            "set_ok":         "🎂 ¡anotado! tu cumple es el **{date}** ☕✨",
            "removed":        "✅ borré tu cumple del calendario ☕",
            "invalid_date":   "❌ esa fecha se ve rara~ usa `MM-DD` como `07-23` ☕",
            "show_self":      "🎂 tu cumple acogedor es el **{date}** ☕",
            "show_other":     "🎂 el cumple de {user} es el **{date}** ☕",
            "show_none":      "📭 {user} aún no me ha dicho su cumple ☕",
            "today_empty":    "🎂 nadie celebra hoy — día tranquilo en el café ☕",
            "today_title":    "### {icon} fiesta de pastel hoy ☕✨",
            "upcoming_empty": "📭 no hay cumples próximos — mes tranquilo en el café ☕",
            "upcoming_title": "### {icon} próximos cumpleaños ☕✨",
            "channel_set":    "✅ gritaré feliz cumple en {channel} ☕✨",
            "role_set":       "✅ los cumpleañeros recibirán el rol {role} ☕",
            "config_title":   "### {icon} rincón de cumples ☕",
            "config_body":    "**canal:** {channel}\n**rol:** {role}",
            "happy_birthday": "🎂🎉 ¡feliz cumpleaños {mention} ☕✨ te deseo el día más acogedor y dulce con pastel extra 🍰",
        },
    },
}


def _lang(ctx) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        l = str(ctx.guild.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


def _personality(ctx_or_guild) -> str:
    if isinstance(ctx_or_guild, commands.Context):
        return get_personality(ctx_or_guild)
    class _S:
        guild = ctx_or_guild if isinstance(ctx_or_guild, discord.Guild) else None
    return get_personality(_S())


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
        return {"users": {}, "guilds": {}, "last_run": None}
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
            d.setdefault("users", {})
            d.setdefault("guilds", {})
            d.setdefault("last_run", None)
            return d
    except Exception:
        return {"users": {}, "guilds": {}, "last_run": None}


def _save(d: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)


def _parse_date(text: str) -> Optional[str]:
    m = DATE_RE.fullmatch(text)
    if not m:
        return None
    mo, d = int(m.group(1)), int(m.group(2))
    try:
        # use a leap year so feb 29 is allowed
        datetime(2024, mo, d)
    except ValueError:
        return None
    return f"{mo:02d}-{d:02d}"


def _format_date(s: str) -> str:
    try:
        m, d = s.split("-")
        return datetime(2024, int(m), int(d)).strftime("%B %d")
    except Exception:
        return s


class Birthdays(commands.Cog):
    """Server birthday announcements with optional auto-role."""

    def __init__(self, bot):
        self.bot = bot
        self.data = _load()
        self.daily_check.start()

    def cog_unload(self):
        self.daily_check.cancel()

    # ───── group ────────────────────────────────

    @commands.hybrid_group(
        name="birthday",
        description="Birthday system.",
        help="{ 'en': 'Birthday system: set, list, announce.', 'de': 'Geburtstagssystem: setzen, anzeigen, ankündigen.', 'es': 'Sistema de cumpleaños: establecer, listar, anunciar.' }",
        invoke_without_command=True,
    )
    async def birthday(self, ctx: commands.Context):
        await ctx.send_help(self.birthday)

    @birthday.command(
        name="set",
        description="Set your birthday (MM-DD).",
        help="{ 'en': 'Set your birthday in MM-DD format.', 'de': 'Geburtstag im Format MM-TT setzen.', 'es': 'Establece tu cumpleaños en formato MM-DD.' }",
    )
    async def birthday_set(self, ctx: commands.Context, date: str):
        d = _parse_date(date)
        if not d:
            return await ctx.send(view=cv2(msg(ctx, "invalid_date")))
        self.data["users"][str(ctx.author.id)] = d
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "set_ok", date=_format_date(d))))

    @birthday.command(
        name="remove",
        description="Remove your birthday.",
        help="{ 'en': 'Remove your birthday.', 'de': 'Deinen Geburtstag entfernen.', 'es': 'Elimina tu cumpleaños.' }",
    )
    async def birthday_remove(self, ctx: commands.Context):
        self.data["users"].pop(str(ctx.author.id), None)
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "removed")))

    @birthday.command(
        name="show",
        description="Show a user's birthday.",
        help="{ 'en': 'Show a user\\'s birthday.', 'de': 'Geburtstag eines Nutzers anzeigen.', 'es': 'Muestra el cumpleaños de un usuario.' }",
    )
    async def birthday_show(self, ctx: commands.Context, user: discord.Member = None):
        target = user or ctx.author
        d = self.data["users"].get(str(target.id))
        if not d:
            return await ctx.send(view=cv2(msg(ctx, "show_none", user=target.mention)))
        formatted = _format_date(d)
        if target == ctx.author:
            await ctx.send(view=cv2(msg(ctx, "show_self", date=formatted)))
        else:
            await ctx.send(view=cv2(msg(ctx, "show_other", user=target.mention, date=formatted)))

    @birthday.command(
        name="today",
        description="List members with a birthday today.",
        help="{ 'en': 'List today\\'s birthdays.', 'de': 'Heutige Geburtstage anzeigen.', 'es': 'Lista los cumpleaños de hoy.' }",
    )
    async def birthday_today(self, ctx: commands.Context):
        today = datetime.now(timezone.utc).strftime("%m-%d")
        results = []
        for m in ctx.guild.members:
            d = self.data["users"].get(str(m.id))
            if d == today:
                results.append(f"• {m.mention}")
        if not results:
            return await ctx.send(view=cv2(msg(ctx, "today_empty")))
        body = msg(ctx, "today_title", icon=get_emoji("icon_heart")) + "\n" + "\n".join(results[:50])
        await ctx.send(view=cv2(body))

    @birthday.command(
        name="upcoming",
        description="Upcoming birthdays in the next 30 days.",
        help="{ 'en': 'Upcoming birthdays in the next 30 days.', 'de': 'Bevorstehende Geburtstage in den nächsten 30 Tagen.', 'es': 'Próximos cumpleaños en los próximos 30 días.' }",
    )
    async def birthday_upcoming(self, ctx: commands.Context):
        today = datetime.now(timezone.utc).date()
        entries: List[tuple] = []
        for m in ctx.guild.members:
            d = self.data["users"].get(str(m.id))
            if not d:
                continue
            try:
                mo, da = (int(x) for x in d.split("-"))
                this_year = today.replace(month=mo, day=min(da, 28))  # safe
                this_year = today.replace(month=mo, day=da) if (mo, da) != (2, 29) else today.replace(month=2, day=28)
            except Exception:
                continue
            target = this_year
            if target < today:
                try:
                    target = target.replace(year=today.year + 1)
                except Exception:
                    pass
            delta = (target - today).days
            if 0 <= delta <= 30:
                entries.append((delta, m.mention, _format_date(d)))
        if not entries:
            return await ctx.send(view=cv2(msg(ctx, "upcoming_empty")))
        entries.sort()
        body = msg(ctx, "upcoming_title", icon=get_emoji("icon_heart")) + "\n" + "\n".join(
            f"• **{date}** · {who} · `in {d}d`" for d, who, date in entries[:30]
        )
        await ctx.send(view=cv2(body))

    # ───── admin ──────────────────────────────

    @birthday.command(
        name="channel",
        description="Set the birthday announcement channel.",
        help="{ 'en': 'Set the birthday announcement channel (admin).', 'de': 'Geburtstags-Ankündigungskanal setzen (Admin).', 'es': 'Establece el canal de anuncios de cumpleaños (admin).' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def birthday_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        gcfg = self.data["guilds"].setdefault(str(ctx.guild.id), {})
        gcfg["channel_id"] = channel.id
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "channel_set", channel=channel.mention)))

    @birthday.command(
        name="role",
        description="Set the auto-assigned birthday role.",
        help="{ 'en': 'Set the birthday role (admin).', 'de': 'Geburtstagsrolle setzen (Admin).', 'es': 'Establece el rol de cumpleaños (admin).' }",
    )
    @commands.has_permissions(manage_guild=True)
    async def birthday_role(self, ctx: commands.Context, role: discord.Role):
        gcfg = self.data["guilds"].setdefault(str(ctx.guild.id), {})
        gcfg["role_id"] = role.id
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "role_set", role=role.mention)))

    @birthday.command(
        name="config",
        description="Show server birthday config.",
        help="{ 'en': 'Show this server\\'s birthday config.', 'de': 'Geburtstags-Konfiguration dieses Servers anzeigen.', 'es': 'Muestra la configuración de cumpleaños de este servidor.' }",
    )
    async def birthday_config(self, ctx: commands.Context):
        gcfg = self.data["guilds"].get(str(ctx.guild.id), {})
        ch = ctx.guild.get_channel(gcfg.get("channel_id", 0))
        rl = ctx.guild.get_role(gcfg.get("role_id", 0))
        title = msg(ctx, "config_title", icon=get_emoji("icon_settings"))
        body = msg(ctx, "config_body",
                   channel=ch.mention if ch else "—",
                   role=rl.mention if rl else "—")
        await ctx.send(view=cv2(title + "\n" + body))

    # ───── daily task ──────────────────────────

    @tasks.loop(minutes=15)
    async def daily_check(self):
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        last = self.data.get("last_run")
        # only run once per UTC day, after 09:00 UTC
        if last == date_str:
            # but still strip stale roles
            await self._strip_stale_birthday_roles(now)
            return
        if now.hour < 9:
            return

        today = now.strftime("%m-%d")
        for guild in self.bot.guilds:
            gcfg = self.data["guilds"].get(str(guild.id), {})
            ch = guild.get_channel(gcfg.get("channel_id", 0)) if gcfg.get("channel_id") else None
            role = guild.get_role(gcfg.get("role_id", 0)) if gcfg.get("role_id") else None
            for member in guild.members:
                d = self.data["users"].get(str(member.id))
                if d != today:
                    continue
                if ch:
                    try:
                        await ch.send(view=cv2(msg(guild, "happy_birthday", mention=member.mention)))
                    except Exception:
                        pass
                if role:
                    try:
                        await member.add_roles(role, reason="Birthday")
                    except Exception:
                        pass
        self.data["last_run"] = date_str
        _save(self.data)
        await self._strip_stale_birthday_roles(now)

    async def _strip_stale_birthday_roles(self, now: datetime):
        today = now.strftime("%m-%d")
        for guild in self.bot.guilds:
            gcfg = self.data["guilds"].get(str(guild.id), {})
            role = guild.get_role(gcfg.get("role_id", 0)) if gcfg.get("role_id") else None
            if not role:
                continue
            for member in role.members:
                d = self.data["users"].get(str(member.id))
                if d != today:
                    try:
                        await member.remove_roles(role, reason="Birthday over")
                    except Exception:
                        pass

    @daily_check.before_loop
    async def _wait(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Birthdays(bot))
