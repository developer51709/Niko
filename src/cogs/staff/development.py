import discord
import asyncio
import traceback
import textwrap
import time
import os
import psutil
import aiohttp
from discord.ext import commands
import colorama
from utils.paginator import PaginatedView, paginate
from utils.emoji_sync import sync_application_emojis, list_application_emojis, parse_config
from config.emojis import get_emoji
from config.ids import DEVELOPER_IDS, OWNER_IDS

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """
    Resolve the primary prefix for the current context/interaction.

    Supports:
    - Static string prefix
    - Static list/tuple of prefixes
    - Dynamic prefix function: command_prefix(bot, message) -> list[str]
    """
    raw = bot.command_prefix

    # Static prefix (string)
    if isinstance(raw, str):
        return raw

    # Static list/tuple of prefixes
    if isinstance(raw, (list, tuple)):
        return raw[0]

    # Dynamic prefix function
    try:
        # Context: has .message
        msg = getattr(ctx_or_interaction, "message", None)

        # Interaction: use the original message if present
        if msg is None and isinstance(ctx_or_interaction, discord.Interaction):
            msg = ctx_or_interaction.message

        if msg is None:
            return "!"

        prefixes = raw(bot, msg)
        if isinstance(prefixes, (list, tuple)) and prefixes:
            return prefixes[0]
    except Exception:
        pass

    # Fallback prefix if everything else fails
    return "."


class Development(commands.Cog):
    """Developer-only debugging and control commands."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # -------------------------------
    # Developer-only check
    # -------------------------------
    async def cog_check(self, ctx: commands.Context):
        # Owners retain developer access without being duplicated in the
        # developer allow-list, keeping the role definitions independent.
        return ctx.author.id in DEVELOPER_IDS or ctx.author.id in OWNER_IDS

    # -------------------------------
    # Developer Help
    # -------------------------------
    @commands.command(name="devhelp")
    async def dev_help(self, ctx):
        prefix = await _resolve_prefix(self.bot, ctx)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"# {get_emoji('icon_bug')} Developer Toolkit\n> Easy-to-use debugging and control commands."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=f"### Diagnostics\n`{prefix}devping`\n`{prefix}devlatency`\n`{prefix}devuptime`\n`{prefix}devmem`\n`{prefix}devtasks`"
            ),
            discord.ui.TextDisplay(
                content=f"### Guild Tools\n`{prefix}devguild`\n`{prefix}devchannels`\n`{prefix}devroles`\n`{prefix}devmembers`"
            ),
            discord.ui.TextDisplay(
                content=f"### Eval / Exec\n`{prefix}devexec <code>` (executes code; owner eval is available in the owner command set)"
            ),
            discord.ui.TextDisplay(
                content=f"### Bot Control\n`{prefix}devsay <msg>`"
            ),
            discord.ui.TextDisplay(
                content=f"### Emoji Sync\n`{prefix}syncemojis`\n`{prefix}appemojis`\n`{prefix}emojistatus`"
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
        try:
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / 1024 / 1024
            mem_str = f"{mem:.2f} MB"
        except Exception:
            mem_str = "N/A"
        await ctx.send(f"Memory usage: `{mem_str}`")

    @commands.command(name="devtasks", help="View the active asyncio task count")
    async def dev_tasks(self, ctx):
        tasks = asyncio.all_tasks()
        await ctx.send(f"Active asyncio tasks: `{len(tasks)}`")

    # -------------------------------
    # Guild Inspection
    # -------------------------------
    @commands.command(name="devguild", help="View info about a guild.")
    async def dev_guild(self, ctx, guild_id: int = None):
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
            + (f" {get_emoji('icon_bot')}" if m.bot else "")
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
                    content=f"## {get_emoji('icon_danger')} Execution Error\nAn error occurred while executing the code."
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

    # -------------------------------
    # Emoji Sync
    # -------------------------------
    @commands.command(name="syncemojis", help="Sync bot emojis as application emojis and download assets")
    async def sync_emojis(self, ctx):
        """Manually trigger the application emoji sync."""
        status_msg = await ctx.send(f"{get_emoji('icon_loading')} Syncing application emojis…")
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    stats = await sync_application_emojis(self.bot, session=session)
            except Exception as exc:
                await status_msg.edit(content=f"{get_emoji('icon_cross')} Sync failed: `{exc}`")
                return

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_paint')} Application Emoji Sync — Complete"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**Emojis in config:** `{stats['parsed']}`\n"
                    f"**Images downloaded/cached:** `{stats['downloaded']}`\n"
                    f"**Already registered:** `{stats['already']}`\n"
                    f"**Newly uploaded:** `{stats['uploaded']}`\n"
                    f"**Failed:** `{stats['failed']}`\n"
                    f"**Config updated:** `{stats['config_updated']}`"
                )
            ),
        )
        view.add_item(container)
        await status_msg.delete()
        await ctx.send(view=view)

    @commands.command(name="appemojis", help="List all registered application emojis")
    async def list_app_emojis(self, ctx):
        """Show all emojis registered to this application."""
        try:
            emojis = await list_application_emojis(self.bot)
        except Exception as exc:
            await ctx.send(f"{get_emoji('icon_cross')} Could not fetch application emojis: `{exc}`")
            return

        if not emojis:
            await ctx.send("No application emojis registered yet. Run `.syncemojis` to upload them.")
            return

        lines = [f"{e} `:{e.name}:` — `{e.id}`" for e in sorted(emojis, key=lambda e: e.name.lower())]
        from utils.paginator import PaginatedView, paginate
        pages = paginate(lines, per_page=15)
        view = PaginatedView(title=f"{get_emoji('icon_paint')} Application Emojis ({len(emojis)} total)", pages=pages)
        await ctx.send(view=view)

    @commands.command(name="emojistatus", help="Show which config emojis are/aren't uploaded as application emojis")
    async def emoji_status(self, ctx):
        """Compare config emojis vs registered application emojis."""
        try:
            app_emojis = await list_application_emojis(self.bot)
        except Exception as exc:
            await ctx.send(f"{get_emoji('icon_cross')} Could not fetch application emojis: `{exc}`")
            return

        config_emojis = parse_config()
        app_names = {e.name.lower() for e in app_emojis}

        synced   = [pe for pe in config_emojis if pe.discord_name.lower() in app_names]
        missing  = [pe for pe in config_emojis if pe.discord_name.lower() not in app_names]

        synced_list  = ", ".join(f"`:{pe.discord_name}:`" for pe in synced)  or "none"
        missing_list = ", ".join(f"`:{pe.discord_name}:`" for pe in missing) or "none"

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('icon_paint')} Emoji Sync Status"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**{get_emoji('icon_tick')} Synced ({len(synced)}):**\n{synced_list}\n\n"
                    f"**{get_emoji('icon_danger')} Missing ({len(missing)}):**\n{missing_list}"
                )
            ),
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(Development(bot))
