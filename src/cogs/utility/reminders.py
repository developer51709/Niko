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
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

DATA_FILE = "data/reminders.json"


# ───────────────────────────────────────────────────
#  TRILINGUAL MESSAGES
# ───────────────────────────────────────────────────

MESSAGES = load_locales("cogs.utility", "reminders")


msg = make_flat_msg(MESSAGES)


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
        # language shim (use the stored guild if remembered, else English)
        guild = self.bot.get_guild(r.get("guild_id") or 0)

        class _Shim:
            pass
        s = _Shim(); s.guild = guild
        text = msg(s, "remind_dm", icon=get_emoji("reminder"), text=r["text"], ago=ago)
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
                        msg(s, "remind_chan", icon=get_emoji("reminder"),
                            mention=user.mention, text=r["text"], ago=ago)))
                except Exception:
                    pass

    # ───── group ────────────────────────────────

    @commands.hybrid_group(
        name="reminder",
        description=CMDS.text("reminder.description"),
        help=CMDS.help("reminder"),
        invoke_without_command=True,
    )
    async def reminder(self, ctx: commands.Context):
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.reminder)
        await ctx.invoke(help_cmd, command_name="reminder")

    @reminder.command(
        name="set",
        description=CMDS.text("reminder.set.description"),
        help=CMDS.help("reminder.set"),
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
        await ctx.send(view=cv2(msg(ctx, "set_ok", icon=get_emoji("reminder"), text=text, ts=ts)))

    @reminder.command(
        name="list",
        description=CMDS.text("reminder.list.description"),
        help=CMDS.help("reminder.list"),
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
        body = msg(ctx, "list_title", icon=get_emoji("reminder")) + "\n" + "\n".join(lines)
        await ctx.send(view=cv2(body))

    @reminder.command(
        name="delete",
        description=CMDS.text("reminder.delete.description"),
        help=CMDS.help("reminder.delete"),
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
        description=CMDS.text("reminder.clear.description"),
        help=CMDS.help("reminder.clear"),
    )
    async def reminder_clear(self, ctx: commands.Context):
        self.reminders = {rid: r for rid, r in self.reminders.items() if r["user_id"] != ctx.author.id}
        _save(self.reminders)
        await ctx.send(view=cv2(msg(ctx, "clear_ok")))


async def setup(bot):
    await bot.add_cog(Reminders(bot))
