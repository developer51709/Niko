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

import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import discord
from discord.ext import commands, tasks

from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

DATE_RE = re.compile(r"^\s*(\d{1,2})[-/](\d{1,2})\s*$")


MESSAGES = load_locales("cogs.social", "birthdays")


msg = make_flat_msg(MESSAGES)


def cv2(text: str) -> discord.ui.LayoutView:
    v = discord.ui.LayoutView()
    v.add_item(discord.ui.Container(discord.ui.TextDisplay(content=text)))
    return v


def _parse_date(text: str) -> Optional[str]:
    m = DATE_RE.fullmatch(text)
    if not m:
        return None
    mo, d = int(m.group(1)), int(m.group(2))
    try:
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
        self.daily_check.start()

    def cog_unload(self):
        self.daily_check.cancel()

    # ───── database helpers ──────────────────────

    async def _db_get_user_birthday(self, user_id: int) -> Optional[str]:
        row = await self.bot.cxn.fetchrow(
            "SELECT birth_date FROM birthday_users WHERE user_id = $1",
            user_id,
        )
        return row["birth_date"] if row else None

    async def _db_set_user_birthday(self, user_id: int, birth_date: str):
        await self.bot.cxn.execute(
            "INSERT INTO birthday_users (user_id, birth_date) VALUES ($1, $2) "
            "ON CONFLICT (user_id) DO UPDATE SET birth_date = $3",
            user_id, birth_date, birth_date,
        )

    async def _db_remove_user_birthday(self, user_id: int):
        await self.bot.cxn.execute(
            "DELETE FROM birthday_users WHERE user_id = $1",
            user_id,
        )

    async def _db_get_all_birthdays(self) -> list:
        return await self.bot.cxn.fetch("SELECT user_id, birth_date FROM birthday_users")

    async def _db_get_guild_config(self, guild_id: int) -> dict:
        row = await self.bot.cxn.fetchrow(
            "SELECT channel_id, role_id FROM birthday_guilds WHERE guild_id = $1",
            guild_id,
        )
        if row:
            return {"channel_id": row.get("channel_id"), "role_id": row.get("role_id")}
        return {}

    async def _db_set_guild_config(self, guild_id: int, **kwargs):
        existing = await self._db_get_guild_config(guild_id)
        channel_id = kwargs.get("channel_id", existing.get("channel_id"))
        role_id = kwargs.get("role_id", existing.get("role_id"))
        await self.bot.cxn.execute(
            "INSERT INTO birthday_guilds (guild_id, channel_id, role_id) VALUES ($1, $2, $3) "
            "ON CONFLICT (guild_id) DO UPDATE SET channel_id = $4, role_id = $5",
            guild_id, channel_id, role_id, channel_id, role_id,
        )

    async def _db_get_last_run(self) -> Optional[str]:
        row = await self.bot.cxn.fetchrow(
            "SELECT value FROM birthday_state WHERE key = 'last_run'",
        )
        return row["value"] if row else None

    async def _db_set_last_run(self, value: str):
        await self.bot.cxn.execute(
            "INSERT INTO birthday_state (key, value) VALUES ('last_run', $1) "
            "ON CONFLICT (key) DO UPDATE SET value = $2",
            value, value,
        )

    # ───── group ────────────────────────────────

    @commands.hybrid_group(
        name="birthday",
        description=CMDS.text("birthday.description"),
        help=CMDS.help("birthday"),
        invoke_without_command=True,
    )
    async def birthday(self, ctx: commands.Context):
        await ctx.send_help(self.birthday)

    @birthday.command(
        name="set",
        description=CMDS.text("birthday.set.description"),
        help=CMDS.help("birthday.set"),
    )
    async def birthday_set(self, ctx: commands.Context, date: str):
        d = _parse_date(date)
        if not d:
            return await ctx.send(view=cv2(msg(ctx, "invalid_date")))
        await self._db_set_user_birthday(ctx.author.id, d)
        await ctx.send(view=cv2(msg(ctx, "set_ok", date=_format_date(d))))

    @birthday.command(
        name="remove",
        description=CMDS.text("birthday.remove.description"),
        help=CMDS.help("birthday.remove"),
    )
    async def birthday_remove(self, ctx: commands.Context):
        await self._db_remove_user_birthday(ctx.author.id)
        await ctx.send(view=cv2(msg(ctx, "removed")))

    @birthday.command(
        name="show",
        description=CMDS.text("birthday.show.description"),
        help=CMDS.help("birthday.show"),
    )
    async def birthday_show(self, ctx: commands.Context, user: discord.Member = None):
        target = user or ctx.author
        d = await self._db_get_user_birthday(target.id)
        if not d:
            return await ctx.send(view=cv2(msg(ctx, "show_none", user=target.mention)))
        formatted = _format_date(d)
        if target == ctx.author:
            await ctx.send(view=cv2(msg(ctx, "show_self", date=formatted)))
        else:
            await ctx.send(view=cv2(msg(ctx, "show_other", user=target.mention, date=formatted)))

    @birthday.command(
        name="today",
        description=CMDS.text("birthday.today.description"),
        help=CMDS.help("birthday.today"),
    )
    async def birthday_today(self, ctx: commands.Context):
        today = datetime.now(timezone.utc).strftime("%m-%d")
        all_birthdays = await self._db_get_all_birthdays()
        birthday_map = {row["user_id"]: row["birth_date"] for row in all_birthdays}
        results = []
        for m in ctx.guild.members:
            d = birthday_map.get(m.id)
            if d == today:
                results.append(f"• {m.mention}")
        if not results:
            return await ctx.send(view=cv2(msg(ctx, "today_empty")))
        body = msg(ctx, "today_title", icon=get_emoji("heart")) + "\n" + "\n".join(results[:50])
        await ctx.send(view=cv2(body))

    @birthday.command(
        name="upcoming",
        description=CMDS.text("birthday.upcoming.description"),
        help=CMDS.help("birthday.upcoming"),
    )
    async def birthday_upcoming(self, ctx: commands.Context):
        today = datetime.now(timezone.utc).date()
        all_birthdays = await self._db_get_all_birthdays()
        birthday_map = {row["user_id"]: row["birth_date"] for row in all_birthdays}
        entries: List[tuple] = []
        for m in ctx.guild.members:
            d = birthday_map.get(m.id)
            if not d:
                continue
            try:
                mo, da = (int(x) for x in d.split("-"))
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
        body = msg(ctx, "upcoming_title", icon=get_emoji("heart")) + "\n" + "\n".join(
            f"• **{date}** · {who} · `in {d}d`" for d, who, date in entries[:30]
        )
        await ctx.send(view=cv2(body))

    # ───── admin ──────────────────────────────

    @birthday.command(
        name="channel",
        description=CMDS.text("birthday.channel.description"),
        help=CMDS.help("birthday.channel"),
    )
    @commands.has_permissions(manage_guild=True)
    async def birthday_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        await self._db_set_guild_config(ctx.guild.id, channel_id=channel.id)
        await ctx.send(view=cv2(msg(ctx, "channel_set", channel=channel.mention)))

    @birthday.command(
        name="role",
        description=CMDS.text("birthday.role.description"),
        help=CMDS.help("birthday.role"),
    )
    @commands.has_permissions(manage_guild=True)
    async def birthday_role(self, ctx: commands.Context, role: discord.Role):
        await self._db_set_guild_config(ctx.guild.id, role_id=role.id)
        await ctx.send(view=cv2(msg(ctx, "role_set", role=role.mention)))

    @birthday.command(
        name="config",
        description=CMDS.text("birthday.config.description"),
        help=CMDS.help("birthday.config"),
    )
    async def birthday_config(self, ctx: commands.Context):
        gcfg = await self._db_get_guild_config(ctx.guild.id)
        ch = ctx.guild.get_channel(gcfg.get("channel_id", 0)) if gcfg.get("channel_id") else None
        rl = ctx.guild.get_role(gcfg.get("role_id", 0)) if gcfg.get("role_id") else None
        title = msg(ctx, "config_title", icon=get_emoji("settings"))
        body = msg(ctx, "config_body",
                   channel=ch.mention if ch else "—",
                   role=rl.mention if rl else "—")
        await ctx.send(view=cv2(title + "\n" + body))

    # ───── daily task ──────────────────────────

    @tasks.loop(minutes=15)
    async def daily_check(self):
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        last = await self._db_get_last_run()
        # only run once per UTC day, after 09:00 UTC
        if last == date_str:
            # but still strip stale roles
            await self._strip_stale_birthday_roles(now)
            return
        if now.hour < 9:
            return

        today = now.strftime("%m-%d")
        all_birthdays = await self._db_get_all_birthdays()
        birthday_map = {row["user_id"]: row["birth_date"] for row in all_birthdays}

        for guild in self.bot.guilds:
            gcfg = await self._db_get_guild_config(guild.id)
            ch = guild.get_channel(gcfg.get("channel_id", 0)) if gcfg.get("channel_id") else None
            role = guild.get_role(gcfg.get("role_id", 0)) if gcfg.get("role_id") else None
            for member in guild.members:
                d = birthday_map.get(member.id)
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
        await self._db_set_last_run(date_str)
        await self._strip_stale_birthday_roles(now)

    async def _strip_stale_birthday_roles(self, now: datetime):
        today = now.strftime("%m-%d")
        all_birthdays = await self._db_get_all_birthdays()
        birthday_map = {row["user_id"]: row["birth_date"] for row in all_birthdays}
        for guild in self.bot.guilds:
            gcfg = await self._db_get_guild_config(guild.id)
            role = guild.get_role(gcfg.get("role_id", 0)) if gcfg.get("role_id") else None
            if not role:
                continue
            for member in role.members:
                d = birthday_map.get(member.id)
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
