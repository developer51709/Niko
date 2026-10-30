"""
Tags — server-specific custom commands / quick-replies.

Commands (single `tag` group):
    tag show <name>          — show a tag (also: just `<prefix>name`)
    tag create <name> <text> — create a new tag (anyone)
    tag edit <name> <text>   — edit a tag (owner or manage_messages)
    tag delete <name>        — delete a tag (owner or manage_messages)
    tag list                 — list all tags in this server
    tag info <name>          — show metadata about a tag
    tag raw <name>           — show the raw markdown
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict

import discord
from discord.ext import commands

from config.emojis import get_emoji
from utils.i18n import make_flat_msg
from utils.paginator import paginate, PaginatedView
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

DATA_FILE = "data/tags.json"
MAX_TAGS_PER_GUILD = 500
MAX_TAG_LEN = 1900


MESSAGES = load_locales("cogs.utility", "tags")


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


# ───────────────────────────────────────────────────
#  STORAGE
# ───────────────────────────────────────────────────

def _load() -> Dict[str, Dict[str, dict]]:
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


# ───────────────────────────────────────────────────
#  COG
# ───────────────────────────────────────────────────

class Tags(commands.Cog):
    """Custom server tags — quick text snippets keyed by name."""

    def __init__(self, bot):
        self.bot = bot
        self.data: Dict[str, Dict[str, dict]] = _load()

    def _gtags(self, gid: int) -> Dict[str, dict]:
        return self.data.setdefault(str(gid), {})

    @commands.hybrid_group(
        name="tag",
        description=CMDS.text("tag.description"),
        help=CMDS.help("tag"),
        invoke_without_command=True,
    )
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, *, name: str = None):
        if name:
            return await self._show(ctx, name)
        help_cmd = self.bot.get_command("help")
        if help_cmd is None:
            return await ctx.send_help(self.tag)
        await ctx.invoke(help_cmd, command_name="tag")

    @tag.command(
        name="show",
        description=CMDS.text("tag.show.description"),
        help=CMDS.help("tag.show"),
    )
    async def tag_show(self, ctx: commands.Context, *, name: str):
        await self._show(ctx, name)

    async def _show(self, ctx: commands.Context, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        t["uses"] = int(t.get("uses", 0)) + 1
        _save(self.data)
        await ctx.send(view=cv2(t["content"]))

    @tag.command(
        name="create",
        description=CMDS.text("tag.create.description"),
        help=CMDS.help("tag.create"),
    )
    async def tag_create(self, ctx: commands.Context, name: str, *, content: str):
        tags = self._gtags(ctx.guild.id)
        if len(tags) >= MAX_TAGS_PER_GUILD:
            return await ctx.send(view=cv2(msg(ctx, "limit_hit", max=MAX_TAGS_PER_GUILD)))
        if len(content) > MAX_TAG_LEN:
            return await ctx.send(view=cv2(msg(ctx, "too_long", n=MAX_TAG_LEN)))
        key = name.lower()[:50]
        if key in tags:
            return await ctx.send(view=cv2(msg(ctx, "exists", name=name)))
        tags[key] = {
            "name": key,
            "content": content,
            "owner_id": ctx.author.id,
            "created_at": int(datetime.now(timezone.utc).timestamp()),
            "uses": 0,
        }
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "created", name=key)))

    @tag.command(
        name="edit",
        description=CMDS.text("tag.edit.description"),
        help=CMDS.help("tag.edit"),
    )
    async def tag_edit(self, ctx: commands.Context, name: str, *, content: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        if t["owner_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(view=cv2(msg(ctx, "no_perm")))
        if len(content) > MAX_TAG_LEN:
            return await ctx.send(view=cv2(msg(ctx, "too_long", n=MAX_TAG_LEN)))
        t["content"] = content
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "edited", name=name.lower())))

    @tag.command(
        name="delete",
        description=CMDS.text("tag.delete.description"),
        help=CMDS.help("tag.delete"),
    )
    async def tag_delete(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        if t["owner_id"] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            return await ctx.send(view=cv2(msg(ctx, "no_perm")))
        tags.pop(name.lower(), None)
        _save(self.data)
        await ctx.send(view=cv2(msg(ctx, "deleted", name=name.lower())))

    @tag.command(
        name="list",
        description=CMDS.text("tag.list.description"),
        help=CMDS.help("tag.list"),
    )
    async def tag_list(self, ctx: commands.Context):
        tags = self._gtags(ctx.guild.id)
        if not tags:
            return await ctx.send(view=cv2(msg(ctx, "list_empty")))
        sorted_t = sorted(tags.values(), key=lambda x: x["name"])
        lines = [f"• `{t['name']}` · -# uses: {t.get('uses', 0)}" for t in sorted_t]
        title = msg(ctx, "list_title", icon=get_emoji("message"), n=len(sorted_t))
        if len(lines) <= 20:
            body = title + "\n" + "\n".join(lines)
            return await ctx.send(view=cv2(body))
        pages = paginate(lines, per_page=20)
        # prepend title to each page
        pages = [title + "\n" + p for p in pages]
        view = PaginatedView(title=msg(ctx, "list_title", icon=get_emoji("message"), n=len(sorted_t)),
                             pages=pages, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(view=view)

    @tag.command(
        name="info",
        description=CMDS.text("tag.info.description"),
        help=CMDS.help("tag.info"),
    )
    async def tag_info(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        owner = ctx.guild.get_member(t["owner_id"])
        owner_str = owner.mention if owner else f"<@{t['owner_id']}>"
        body = msg(ctx, "info",
                   icon=get_emoji("message"), name=t["name"],
                   owner=owner_str, uses=t.get("uses", 0), created=t.get("created_at", 0))
        await ctx.send(view=cv2(body))

    @tag.command(
        name="raw",
        description=CMDS.text("tag.raw.description"),
        help=CMDS.help("tag.raw"),
    )
    async def tag_raw(self, ctx: commands.Context, *, name: str):
        tags = self._gtags(ctx.guild.id)
        t = tags.get(name.lower())
        if not t:
            return await ctx.send(view=cv2(msg(ctx, "missing", name=name)))
        body = msg(ctx, "raw_title", name=t["name"]) + f"\n```\n{t['content'][:1700]}\n```"
        await ctx.send(view=cv2(body))


async def setup(bot):
    await bot.add_cog(Tags(bot))
