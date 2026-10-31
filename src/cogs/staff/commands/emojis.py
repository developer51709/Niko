"""``.staff syncemojis`` and friends: the application emoji set."""

import aiohttp
import discord
from discord.ext import commands

from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from utils.emoji_sync import sync_application_emojis, list_application_emojis, parse_config
from utils.paginator import PaginatedView, paginate

# Arguments accepted after ``.staff replaceemojis`` to skip its confirmation
# prompt. Deleting every application emoji cannot be undone, so the bypass is
# something the caller has to spell out rather than an easy-to-hit default.
SKIP_CONFIRM_ARGS = {"--force", "-f", "force", "--yes", "-y", "yes"}


def skips_confirmation(raw: str = None) -> bool:
    """Whether a ``replaceemojis`` argument means "don't ask, just do it"."""
    return (raw or "").strip().lower() in SKIP_CONFIRM_ARGS


class EmojiCommands:
    """Sync, replace and inspect the emojis registered to the application."""

    @StaffCommands.staff.command(name="syncemojis", help=CMDS.help("syncemojis"), hidden=True)
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

    @StaffCommands.staff.command(
        name="replaceemojis",
        help=CMDS.help("replaceemojis"),
        hidden=True,
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

    @StaffCommands.staff.command(name="appemojis", help=CMDS.help("appemojis"), hidden=True)
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
        pages = paginate(lines, per_page=15)
        view = PaginatedView(title=f"{get_emoji('paint')} Application Emojis ({len(emojis)} total)", pages=pages)
        await ctx.send(view=view)

    @StaffCommands.staff.command(name="emojistatus", help=CMDS.help("emojistatus"), hidden=True)
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
