"""``.staff ping`` and the guild-inspection tooling behind it."""

import asyncio
import os
import time

import psutil
import discord
from discord.ext import commands

from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from utils.paginator import PaginatedView, paginate


class DiagnosticsCommands:
    """Health, memory, task and guild inspection for staff."""

    @StaffCommands.staff.command(name="ping", help=CMDS.help("devping"), hidden=True)
    async def ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pinging…")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"Pong! `{ping:.2f}ms`")

    @StaffCommands.staff.command(name="latency", help=CMDS.help("devlatency"), hidden=True)
    async def latency(self, ctx):
        await ctx.send(f"Websocket latency: `{self.bot.latency * 1000:.2f}ms`")

    @StaffCommands.staff.command(name="uptime", help=CMDS.help("devuptime"), hidden=True)
    async def uptime(self, ctx):
        delta = time.time() - self.start_time
        hours, remainder = divmod(delta, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: `{int(hours)}h {int(minutes)}m {int(seconds)}s`")

    @StaffCommands.staff.command(name="mem", help=CMDS.help("devmem"), hidden=True)
    async def memory(self, ctx):
        try:
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / 1024 / 1024
            mem_str = f"{mem:.2f} MB"
        except Exception:
            mem_str = "N/A"
        await ctx.send(f"Memory usage: `{mem_str}`")

    @StaffCommands.staff.command(name="tasks", help=CMDS.help("devtasks"), hidden=True)
    async def tasks(self, ctx):
        tasks = asyncio.all_tasks()
        await ctx.send(f"Active asyncio tasks: `{len(tasks)}`")

    @StaffCommands.staff.command(name="guild", help=CMDS.help("devguild"), hidden=True)
    async def guild_info(self, ctx, guild_id: int = None):
        if guild_id:
            g = self.bot.get_guild(guild_id)
            if not g:
                return await ctx.send("Guild not found.")
        else:
            g = ctx.guild
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"## ℹ️ Guild Information\nGuild: {g.name}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"### Details\n\n**ID:** `{g.id}`\n**Members:** `{g.member_count}`\n**Owner:** `{g.owner}`\n**Channels:** `{len(g.channels)}`\n**Roles:** `{len(g.roles)}`\n**Created:** `{g.created_at.strftime('%Y-%m-%d %H:%M:%S')}`"
            )
        )
        view.add_item(container)
        await ctx.send(view=view)

    @StaffCommands.staff.command(name="channels", help=CMDS.help("devchannels"), hidden=True)
    async def channels(self, ctx):
        lines = [
            f"`{c.id}` — **{c.name}** ({type(c).__name__})"
            for c in sorted(ctx.guild.channels, key=lambda c: c.name)
        ]
        pages = paginate(lines, per_page=15)
        view = PaginatedView(
            title=f"📋 Channels — {ctx.guild.name}",
            pages=pages,
        )
        await ctx.send(view=view)

    @StaffCommands.staff.command(name="roles", help=CMDS.help("devroles"), hidden=True)
    async def roles(self, ctx):
        lines = [
            f"`{r.id}` — **{r.name}**"
            + (" *(managed)*" if r.managed else "")
            for r in sorted(ctx.guild.roles, key=lambda r: -r.position)
        ]
        pages = paginate(lines, per_page=15)
        view = PaginatedView(
            title=f"🏷️ Roles — {ctx.guild.name}",
            pages=pages,
        )
        await ctx.send(view=view)

    @StaffCommands.staff.command(name="members", help=CMDS.help("devmembers"), hidden=True)
    async def members(self, ctx):
        lines = [
            f"`{m.id}` — **{m.display_name}** ({m.name})"
            + (f" {get_emoji('bot')}" if m.bot else "")
            for m in sorted(ctx.guild.members, key=lambda m: m.display_name.lower())
        ]
        pages = paginate(lines, per_page=15)
        view = PaginatedView(
            title=f"👥 Members — {ctx.guild.name} ({len(ctx.guild.members)} total)",
            pages=pages,
        )
        await ctx.send(view=view)
