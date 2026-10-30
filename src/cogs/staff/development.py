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
from utils.prefix_manager import resolve_prefix
from config.emojis import get_emoji
from config.ids import OWNER_IDS

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

async def _resolve_prefix(bot: commands.Bot, ctx_or_interaction) -> str:
    """Return the primary prefix for this context, honouring a dynamic prefix."""
    return await resolve_prefix(bot, ctx_or_interaction)


# Arguments accepted after ``.staff replaceemojis`` to skip its confirmation
# prompt. Deleting every application emoji cannot be undone, so the bypass is
# something the caller has to spell out rather than an easy-to-hit default.
SKIP_CONFIRM_ARGS = {"--force", "-f", "force", "--yes", "-y", "yes"}


def skips_confirmation(raw: str = None) -> bool:
    """Whether a ``replaceemojis`` argument means "don't ask, just do it"."""
    return (raw or "").strip().lower() in SKIP_CONFIRM_ARGS


class Development(commands.Cog):
    """Developer-only debugging and control commands."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # -------------------------------
    # Developer-only check
    # -------------------------------
    async def cog_check(self, ctx: commands.Context):
        # These commands are registered under ``.staff`` and gated by the staff
        # role allow-lists; the check only applies if this module is loaded on
        # its own, where the bot owner is the only permitted caller.
        return ctx.author.id in OWNER_IDS

    # -------------------------------
    # Developer Help
    # -------------------------------
    @commands.command(name="devhelp", help=CMDS.help("devhelp"))
    async def dev_help(self, ctx):
        prefix = await _resolve_prefix(self.bot, ctx)

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(
                content=f"# {get_emoji('bug')} Developer Toolkit\n> Easy-to-use debugging and control commands."
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
    @commands.command(name="devping", help=CMDS.help("devping"))
    async def dev_ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pinging…")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"Pong! `{ping:.2f}ms`")

    @commands.command(name="devlatency", help=CMDS.help("devlatency"))
    async def dev_latency(self, ctx):
        await ctx.send(f"Websocket latency: `{self.bot.latency * 1000:.2f}ms`")

    @commands.command(name="devuptime", help=CMDS.help("devuptime"))
    async def dev_uptime(self, ctx):
        delta = time.time() - self.start_time
        hours, remainder = divmod(delta, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f"Uptime: `{int(hours)}h {int(minutes)}m {int(seconds)}s`")

    @commands.command(name="devmem", help=CMDS.help("devmem"))
    async def dev_memory(self, ctx):
        try:
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / 1024 / 1024
            mem_str = f"{mem:.2f} MB"
        except Exception:
            mem_str = "N/A"
        await ctx.send(f"Memory usage: `{mem_str}`")

    @commands.command(name="devtasks", help=CMDS.help("devtasks"))
    async def dev_tasks(self, ctx):
        tasks = asyncio.all_tasks()
        await ctx.send(f"Active asyncio tasks: `{len(tasks)}`")

    # -------------------------------
    # Guild Inspection
    # -------------------------------
    @commands.command(name="devguild", help=CMDS.help("devguild"))
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

    @commands.command(name="devchannels", help=CMDS.help("devchannels"))
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

    @commands.command(name="devroles", help=CMDS.help("devroles"))
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

    @commands.command(name="devmembers", help=CMDS.help("devmembers"))
    async def dev_members(self, ctx):
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

    # -------------------------------
    # Eval / Exec
    # -------------------------------
    @commands.command(name="devexec", help=CMDS.help("devexec"))
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
                    content=f"## {get_emoji('danger')} Execution Error\nAn error occurred while executing the code."
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
    @commands.command(name="devsay", help=CMDS.help("devsay"))
    async def dev_say(self, ctx, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)

    # -------------------------------
    # Emoji Sync
    # -------------------------------
    @commands.command(name="syncemojis", help=CMDS.help("syncemojis"))
    async def sync_emojis(self, ctx):
        """Manually trigger the application emoji sync."""
        status_msg = await ctx.send(f"{get_emoji('loading')} Syncing application emojis…")
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    stats = await sync_application_emojis(self.bot, session=session)
            except Exception as exc:
                await status_msg.edit(content=f"{get_emoji('cross')} Sync failed: `{exc}`")
                return

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('paint')} Application Emoji Sync — Complete"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**Emojis in config:** `{stats['parsed']}`\n"
                    f"**Images downloaded/cached:** `{stats['downloaded']}`\n"
                    f"**Already registered:** `{stats['already']}`\n"
                    f"**Newly uploaded:** `{stats['uploaded']}`\n"
                    f"**Failed:** `{stats['failed']}`\n"
                    f"**Config updated:** `{stats['config_updated']}`\n"
                    f"**Live ids adopted:** `{stats['live_ids']}` — no restart needed."
                )
            ),
        )
        view.add_item(container)
        await status_msg.delete()
        await ctx.send(view=view)

    @commands.command(
        name="replaceemojis",
        help=CMDS.help("replaceemojis"),
    )
    async def replace_emojis(self, ctx, force: str = None):
        """Owner-only: rebuild the application emoji set from ``src/assets/emojis``.

        Discord cannot replace an emoji's image, so regenerated artwork only
        reaches Discord by deleting the emoji and uploading it again. That
        changes every emoji id, so the config is rewritten and the running bot
        is handed the new ids — nothing needs a restart afterwards.

        There is no way to undo a replacement, so it is confirmed first; an
        explicit ``--force`` skips that prompt for an already-decided run.
        """
        if ctx.author.id not in OWNER_IDS:
            return await ctx.send(
                f"{get_emoji('cross')} Only the bot owner can replace application emojis."
            )

        if not skips_confirmation(force) and not await self._confirm_replacement(ctx):
            return

        status = await ctx.send(f"{get_emoji('loading')} Deleting application emojis…")

        async def progress(message: str) -> None:
            try:
                await status.edit(content=f"{get_emoji('loading')} {message}")
            except discord.HTTPException:
                pass

        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    stats = await sync_application_emojis(
                        self.bot, session=session, replace=True, on_progress=progress,
                    )
            except Exception as exc:
                await status.edit(content=f"{get_emoji('cross')} Replacement failed: `{exc}`")
                return

        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('paint')} Application Emoji Replacement — Complete"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**Deleted:** `{stats['deleted']}` (failed: `{stats['delete_failed']}`)\n"
                    f"**Uploaded from local art:** `{stats['uploaded']}`\n"
                    f"**Still registered:** `{stats['already']}`\n"
                    f"**Failed to upload:** `{stats['failed']}`\n"
                    f"**Config rewritten:** `{stats['config_updated']}`\n"
                    f"**Live ids in the running bot:** `{stats['live_ids']}` — no restart needed."
                )
            ),
        ))
        try:
            await status.delete()
        except discord.HTTPException:
            pass
        await ctx.send(view=view)

    async def _confirm_replacement(self, ctx) -> bool:
        """Show the replace-emojis card; ``True`` only on an explicit confirm.

        Both buttons are disabled once the card is answered, so a slow second
        click cannot start a second replacement, and a timeout counts as a
        refusal — deleting every emoji cannot be undone.
        """
        decision = {"confirmed": False}
        confirmation = discord.ui.LayoutView(timeout=120)
        text = discord.ui.TextDisplay(content=(
            "## Replace every application emoji?\n"
            "Every application emoji is deleted, then the whole set is uploaded again from "
            "`src/assets/emojis/` — from the local PNGs, never from Discord's copies. Discord has "
            "no way to replace an emoji's image, so this is the only way to push regenerated art.\n\n"
            "**Every emoji id changes** and `src/config/emojis.py` is rewritten to match. The bot "
            "starts using the new ids immediately; messages that already contain the old ones show "
            "their raw `:name:` text until they are re-sent. This cannot be undone while it runs.\n\n"
            "-# Add `--force` to skip this prompt."
        ))
        confirm_button = discord.ui.Button(label="Replace emoji set", style=discord.ButtonStyle.danger)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)

        def set_text(content: str) -> None:
            text.content = content

        async def choose(interaction: discord.Interaction, confirmed: bool):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message(
                    "Only the command author can confirm this replacement.", ephemeral=True
                )
            decision["confirmed"] = confirmed
            for item in (confirm_button, cancel_button):
                item.disabled = True
            set_text(
                "Replacing the emoji set — deleting the current emojis, then uploading "
                "the local art. This can take a few minutes."
                if confirmed else "Emoji replacement cancelled."
            )
            await interaction.response.edit_message(view=confirmation)
            confirmation.stop()

        confirm_button.callback = lambda interaction: choose(interaction, True)
        cancel_button.callback = lambda interaction: choose(interaction, False)
        confirmation.add_item(discord.ui.Container(
            text,
            discord.ui.ActionRow(confirm_button, cancel_button),
            accent_colour=discord.Colour.red(),
        ))
        response = await ctx.send(view=confirmation)
        if await confirmation.wait() or not decision["confirmed"]:
            for item in (confirm_button, cancel_button):
                item.disabled = True
            set_text(
                "Emoji replacement cancelled (confirmation timed out)."
                if not decision["confirmed"] else "Emoji replacement cancelled."
            )
            await response.edit(view=confirmation)
            return False
        return True

    @commands.command(name="appemojis", help=CMDS.help("appemojis"))
    async def list_app_emojis(self, ctx):
        """Show all emojis registered to this application."""
        try:
            emojis = await list_application_emojis(self.bot)
        except Exception as exc:
            await ctx.send(f"{get_emoji('cross')} Could not fetch application emojis: `{exc}`")
            return

        if not emojis:
            await ctx.send("No application emojis registered yet. Run `.syncemojis` to upload them.")
            return

        lines = [f"{e} `:{e.name}:` — `{e.id}`" for e in sorted(emojis, key=lambda e: e.name.lower())]
        from utils.paginator import PaginatedView, paginate
        pages = paginate(lines, per_page=15)
        view = PaginatedView(title=f"{get_emoji('paint')} Application Emojis ({len(emojis)} total)", pages=pages)
        await ctx.send(view=view)

    @commands.command(name="emojistatus", help=CMDS.help("emojistatus"))
    async def emoji_status(self, ctx):
        """Compare config emojis vs registered application emojis."""
        try:
            app_emojis = await list_application_emojis(self.bot)
        except Exception as exc:
            await ctx.send(f"{get_emoji('cross')} Could not fetch application emojis: `{exc}`")
            return

        config_emojis = parse_config()
        app_names = {e.name.lower() for e in app_emojis}

        synced   = [pe for pe in config_emojis if pe.discord_name.lower() in app_names]
        missing  = [pe for pe in config_emojis if pe.discord_name.lower() not in app_names]

        synced_list  = ", ".join(f"`:{pe.discord_name}:`" for pe in synced)  or "none"
        missing_list = ", ".join(f"`:{pe.discord_name}:`" for pe in missing) or "none"

        view = discord.ui.LayoutView()
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {get_emoji('paint')} Emoji Sync Status"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                content=(
                    f"**{get_emoji('tick')} Synced ({len(synced)}):**\n{synced_list}\n\n"
                    f"**{get_emoji('danger')} Missing ({len(missing)}):**\n{missing_list}"
                )
            ),
        )
        view.add_item(container)
        await ctx.send(view=view)


async def setup(bot):
    await bot.add_cog(Development(bot))
