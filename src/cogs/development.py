import discord
import asyncio
import traceback
import textwrap
import time
import os
import psutil
from discord.ext import commands
import colorama
from utils.paginator import PaginatedView, paginate

# Developer user IDs
DEVELOPERS = {
    1479968201319125013,  # Nyxen
}


class Development(commands.Cog):
    """Developer-only debugging and control commands."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # -------------------------------
    # Developer-only check
    # -------------------------------
    async def cog_check(self, ctx: commands.Context):
        return ctx.author.id in DEVELOPERS

    # -------------------------------
    # Developer Help
    # -------------------------------
    @commands.command(name="devhelp")
    async def dev_help(self, ctx):
        prefix = self.bot.command_prefix if isinstance(self.bot.command_prefix, str) else self.bot.command_prefix[0]
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="# 🛠 Developer Toolkit\n> Easy-to-use debugging and control commands."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"### Cog Management\n`{prefix}devload <cog>`\n`{prefix}devunload <cog>`\n`{prefix}devreload <cog>`"
            ),
            discord.ui.TextDisplay(
                content=f"### Diagnostics\n`{prefix}devping`\n`{prefix}devlatency`\n`{prefix}devuptime`\n`{prefix}devmem`\n`{prefix}devtasks`"
            ),
            discord.ui.TextDisplay(
                content=f"### Guild Tools\n`{prefix}devguild`\n`{prefix}devchannels`\n`{prefix}devroles`\n`{prefix}devmembers`"
            ),
            discord.ui.TextDisplay(
                content=f"### Eval / Exec\n`{prefix}deveval <code>`\n`{prefix}devexec <code>`"
            ),
            discord.ui.TextDisplay(
                content=f"### Bot Control\n`{prefix}devsay <msg>`\n`{prefix}devshutdown`"
            ),
        )
        view.add_item(container)

        await ctx.send(view=view)

    # -------------------------------
    # Cog Management
    # -------------------------------
    @commands.command(name="devload")
    async def dev_load(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Loaded `{cog}`.")
        except Exception as e:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ⚠️ Cog Load Error\nAn error occurred while loading the {cog} cog."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{e}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @commands.command(name="devunload")
    async def dev_unload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"Unloaded `{cog}`.")
        except Exception as e:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ⚠️ Cog Unload Error\nAn error occurred while unloading the {cog} cog."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{e}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @commands.command(name="devreload")
    async def dev_reload(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"Reloaded `{cog}`.")
        except Exception as e:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ⚠️ Cog Reload Error\nAn error occurred while reloading the {cog} cog."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{e}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    # -------------------------------
    # Diagnostics
    # -------------------------------
    @commands.command(name="devping")
    async def dev_ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pinging…")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"Pong! `{ping:.2f}ms`")

    @commands.command(name="devlatency")
    async def dev_latency(self, ctx):
        await ctx.send(f"Websocket latency: `{self.bot.latency * 1000:.2f}ms`")

    @commands.command(name="devuptime")
    async def dev_uptime(self, ctx):
        delta = time.time() - self.start_time
        hours, remainder = divmod(delta, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: `{int(hours)}h {int(minutes)}m {int(seconds)}s`")

    @commands.command(name="devmem")
    async def dev_memory(self, ctx):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024
        await ctx.send(f"Memory usage: `{mem:.2f} MB`")

    @commands.command(name="devtasks")
    async def dev_tasks(self, ctx):
        tasks = asyncio.all_tasks()
        await ctx.send(f"Active asyncio tasks: `{len(tasks)}`")

    # -------------------------------
    # Guild Inspection
    # -------------------------------
    @commands.command(name="devguild")
    async def dev_guild(self, ctx):
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

    @commands.command(name="devchannels")
    async def dev_channels(self, ctx):
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

    @commands.command(name="devroles")
    async def dev_roles(self, ctx):
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

    @commands.command(name="devmembers")
    async def dev_members(self, ctx):
        lines = [
            f"`{m.id}` — **{m.display_name}** ({m.name})"
            + (" 🤖" if m.bot else "")
            for m in sorted(ctx.guild.members, key=lambda m: m.display_name.lower())
        ]
        pages = paginate(lines, per_page=15)
        view = PaginatedView(
            title=f"👥 Members — {ctx.guild.name} ({len(ctx.guild.members)} total)",
            pages=pages,
        )
        await ctx.send(view=view)

    # -------------------------------
    # Eval / Exec
    # -------------------------------
    @commands.command(name="deveval")
    async def dev_eval(self, ctx, *, code: str):
        """Evaluate Python code."""
        code = code.strip("` ")

        try:
            result = eval(code)
            if asyncio.iscoroutine(result):
                result = await result
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ✅️ Evaluation Success\nThe code was evaluated successfully."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Result\n```\n{result}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)
        except Exception as e:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ⚠️ Evaluation Error\nAn error occurred while evaluating the code."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{e}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    @commands.command(name="devexec")
    async def dev_exec(self, ctx, *, code: str):
        """Execute Python code."""
        code = textwrap.dedent(code.strip("` "))

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "asyncio": asyncio,
            "__import__": __import__,
            "self": self,
        }

        try:
            exec(code, env)
            await ctx.send("Executed successfully.")
        except Exception:
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=f"## ⚠️ Execution Error\nAn error occurred while executing the code."
                ),
                discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
                discord.ui.TextDisplay(
                    content=f"### Traceback\n```\n{traceback.format_exc()}\n```"
                )
            )
            view.add_item(container)
            await ctx.send(view=view)

    # -------------------------------
    # Bot Control
    # -------------------------------
    @commands.command(name="devsay")
    async def dev_say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="devshutdown")
    async def dev_shutdown(self, ctx):
        await ctx.send("Shutting down…")
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Development(bot))