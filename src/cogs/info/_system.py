"""Info — diagnostics about the bot process and its host: /debuginfo, /hostinfo,
/shards."""

import os
import platform
import time

import psutil
from discord.ext import commands

from config.emojis import get_emoji
from utils.paginator import PaginatedView, paginate
from ._messages import cv2_text, msg

from utils.command_locales import command_texts

CMDS = command_texts(__package__)


class SystemMixin:
    """Runtime and host diagnostics."""

    # -------------------------------
    # DEBUG INFO
    # -------------------------------
    @commands.hybrid_command(
        name="debuginfo",
        description=CMDS.text("debuginfo.description"),
        help=CMDS.help("debuginfo"),
    )
    async def debuginfo(self, ctx):
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
        ai_model = os.getenv("AI_MODEL", "Unknown")
        command_count = len(self.bot.commands)
        ping_latency = round(self.bot.latency * 1000)
        try:
            cpu_usage = psutil.cpu_percent()
        except Exception:
            cpu_usage = "N/A"
        try:
            memory_usage = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
        except Exception:
            memory_usage = "N/A"

        text = (
            f"### {msg(ctx, 'debuginfo_title')}\n"
            f"**{msg(ctx, 'debuginfo_uptime')}:** `{uptime}`\n"
            f"**{msg(ctx, 'debuginfo_model')}:** `{ai_model}`\n"
            f"**{msg(ctx, 'debuginfo_commands')}:** `{command_count}`\n"
            f"**{msg(ctx, 'debuginfo_ping')}:** `{ping_latency}ms`\n"
            f"{get_emoji('cpu')} **{msg(ctx, 'debuginfo_cpu')}:** `{cpu_usage}%`\n"
            f"{get_emoji('ram')} **{msg(ctx, 'debuginfo_ram')}:** `{memory_usage}MB`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # HOST INFO
    # -------------------------------
    @commands.hybrid_command(
        name="hostinfo",
        description=CMDS.text("hostinfo.description"),
        help=CMDS.help("hostinfo"),
    )
    async def hostinfo(self, ctx):
        hostname = platform.node()
        os_info = f"{platform.system()} {platform.release()}"
        cpu = platform.processor() or "N/A"
        try:
            ram = round(psutil.virtual_memory().total / (1024**3), 2)
        except Exception:
            ram = "N/A"

        text = (
            f"### {msg(ctx, 'hostinfo_title')}\n"
            f"**{msg(ctx, 'hostinfo_hostname')}:** `{hostname}`\n"
            f"**{msg(ctx, 'hostinfo_os')}:** `{os_info}`\n"
            f"{get_emoji('cpu')} **{msg(ctx, 'hostinfo_cpu')}:** `{cpu}`\n"
            f"{get_emoji('ram')} **{msg(ctx, 'hostinfo_ram')}:** `{ram}GB`"
        )
        await ctx.send(view=cv2_text(text))

    # -------------------------------
    # SHARDS
    # -------------------------------
    @commands.hybrid_command(
        name="shards",
        description=CMDS.text("shards.description"),
        help=CMDS.help("shards"),
    )
    async def shards_command(self, ctx):
        """Display current shard information."""
        if not self.bot.shards:
            return await ctx.send(msg(ctx, "not_sharded", cross=get_emoji("cross")))

        shard_guilds = {}
        shard_members = {}
        total_guilds = 0
        total_members = 0

        # Count guilds and members per shard
        for guild in self.bot.guilds:
            shard_id = guild.shard_id or 0
            shard_guilds[shard_id] = shard_guilds.get(shard_id, 0) + 1
            total_guilds += 1
            if guild.member_count:
                shard_members[shard_id] = shard_members.get(shard_id, 0) + guild.member_count
                total_members += guild.member_count

        lines = []
        for shard_id in range(self.bot.shard_count):
            guild_count = shard_guilds.get(shard_id, 0)
            member_count = shard_members.get(shard_id, 0)
            shard = self.bot.shards.get(shard_id)
            latency = f"{round(shard.latency * 1000)}ms" if shard else "N/A"
            lines.append(
                f"**Shard {shard_id}**\n"
                f"-# {msg(ctx, 'shardinfo_guild_count')}: {guild_count} · "
                f"{msg(ctx, 'shardinfo_member_count')}: {member_count:,} · "
                f"{msg(ctx, 'shardinfo_latency')}: {latency}"
            )

        pages = paginate(lines, per_page=8)
        view = PaginatedView(
            title=f"{get_emoji('host')} {msg(ctx, 'shardinfo_title')}\n-# {msg(ctx, 'shardinfo_total')}: {self.bot.shard_count}",
            pages=pages
        )
        await ctx.send(view=view)
