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
from utils.i18n import make_flat_msg
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

DATA_FILE = "data/highlights.json"
MAX_KEYWORDS = 25
COOLDOWN_SECONDS = 60


MESSAGES = load_locales("cogs.utility", "highlights")


def _lang(ctx) -> str:
    if ctx and ctx.guild and ctx.guild.preferred_locale:
        l = str(ctx.guild.preferred_locale).lower()
        if l.startswith("de"): return "de"
        if l.startswith("es"): return "es"
    return "en"


msg = make_flat_msg(MESSAGES)


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
        description=CMDS.text("highlight.description"),
        help=CMDS.help("highlight"),
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def highlight(self, ctx: commands.Context):
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.highlight)
        await ctx.invoke(help_cmd, command_name="highlight")

    @highlight.command(
        name="add",
        description=CMDS.text("highlight.add.description"),
        help=CMDS.help("highlight.add"),
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
        description=CMDS.text("highlight.remove.description"),
        help=CMDS.help("highlight.remove"),
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
        description=CMDS.text("highlight.list.description"),
        help=CMDS.help("highlight.list"),
    )
    async def highlight_list(self, ctx: commands.Context):
        u = self._user(ctx.guild.id, ctx.author.id)
        if not u["keywords"]:
            return await ctx.send(view=cv2(msg(ctx, "list_empty")),
                                  ephemeral=True if ctx.interaction else False)
        body = msg(ctx, "list_title", icon=get_emoji("message")) + "\n" + "\n".join(
            f"• `{k}`" for k in u["keywords"]
        )
        if u["ignore_users"]:
            body += "\n\n**Ignored users:** " + ", ".join(f"<@{i}>" for i in u["ignore_users"][:20])
        if u["ignore_channels"]:
            body += "\n**Ignored channels:** " + ", ".join(f"<#{i}>" for i in u["ignore_channels"][:20])
        await ctx.send(view=cv2(body), ephemeral=True if ctx.interaction else False)

    @highlight.command(
        name="clear",
        description=CMDS.text("highlight.clear.description"),
        help=CMDS.help("highlight.clear"),
    )
    async def highlight_clear(self, ctx: commands.Context):
        u = self._user(ctx.guild.id, ctx.author.id)
        u["keywords"] = []
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "cleared")), ephemeral=True if ctx.interaction else False)

    @highlight.group(
        name="ignore",
        description=CMDS.text("highlight.ignore.description"),
        help=CMDS.help("highlight.ignore"),
        invoke_without_command=True,
    )
    async def highlight_ignore(self, ctx: commands.Context):
        await ctx.send_help(self.highlight_ignore)

    @highlight_ignore.command(
        name="user",
        help=CMDS.help("highlight.ignore.user"),
    )
    async def highlight_ignore_user(self, ctx: commands.Context, user: discord.Member):
        u = self._user(ctx.guild.id, ctx.author.id)
        if user.id not in u["ignore_users"]:
            u["ignore_users"].append(user.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "ignore_user_ok", user=user.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight_ignore.command(
        name="channel",
        help=CMDS.help("highlight.ignore.channel"),
    )
    async def highlight_ignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        u = self._user(ctx.guild.id, ctx.author.id)
        if channel.id not in u["ignore_channels"]:
            u["ignore_channels"].append(channel.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "ignore_chan_ok", channel=channel.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight.group(
        name="unignore",
        description=CMDS.text("highlight.unignore.description"),
        help=CMDS.help("highlight.unignore"),
        invoke_without_command=True,
    )
    async def highlight_unignore(self, ctx: commands.Context):
        await ctx.send_help(self.highlight_unignore)

    @highlight_unignore.command(
        name="user",
        help=CMDS.help("highlight.unignore.user"),
    )
    async def highlight_unignore_user(self, ctx: commands.Context, user: discord.Member):
        u = self._user(ctx.guild.id, ctx.author.id)
        if user.id in u["ignore_users"]:
            u["ignore_users"].remove(user.id)
            _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "unignore_user_ok", user=user.mention)),
                       ephemeral=True if ctx.interaction else False)

    @highlight_unignore.command(
        name="channel",
        help=CMDS.help("highlight.unignore.channel"),
    )
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

                title = msg(message.guild, "notify_title", icon=get_emoji("lightbulb"), kw=kw)
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
