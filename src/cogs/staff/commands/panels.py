"""``.staff sendpanel status|rules``: post and refresh the persistent panels."""

import discord
from discord.ext import commands

from config.emojis import get_emoji
from cogs.staff.base import CMDS, StaffCommands
from cogs.staff.panels.rules import _build_rules_panel
from cogs.staff.panels.status import STATUS_PANEL_INTERVAL, _build_status_panel, _collect_status
from utils import logging


class PanelCommands:
    """The status panel and the server rules panel."""

    @StaffCommands.staff.group(
        name="sendpanel",
        invoke_without_command=True,
        help=CMDS.help("sendpanel"),
        hidden=True,
    )
    async def sendpanel(self, ctx):
        """Overview of the sendpanel sub-commands."""
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('important')} **Persistent panels**\n"
                "Use `.staff sendpanel status` for the realtime status panel or "
                "`.staff sendpanel rules` for the server rules panel."
            )),
            accent_colour=discord.Color.blurple(),
        ))
        await ctx.send(view=view)

    @sendpanel.command(
        name="status",
        aliases=["statuspanel"],
        help=CMDS.help("sendpanel.status"),
    )
    async def sendpanel_status(self, ctx, channel: discord.TextChannel = None):
        """Post (or refresh) the persistent realtime status panel in a channel."""
        target = channel or ctx.channel
        guild_id = getattr(getattr(target, "guild", None), "id", None)
        if guild_id is None:
            guild_id = getattr(ctx.guild, "id", None)
        if guild_id is None:
            return await ctx.send("This command must be used inside a server.")

        # Show progress in the invoking channel while we probe + post.
        busy_view = discord.ui.LayoutView()
        busy_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('loading')} Building status panel...")
        ))
        busy_message = await ctx.send(view=busy_view)

        # Remove the previous panel for this channel so re-running replaces it.
        cxn = getattr(self.bot, "cxn", None)
        if cxn is not None:
            try:
                row = await cxn.fetchrow(
                    "SELECT message_id FROM persistent_status_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
                if row:
                    old = target.get_partial_message(int(row["message_id"]))
                    await old.delete()
            except Exception:
                pass
            try:
                await cxn.execute(
                    "DELETE FROM persistent_status_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
            except Exception:
                pass

        # Fresh snapshot at send time, then persist the message so the refresh
        # loop keeps it in sync every STATUS_PANEL_INTERVAL seconds.
        status = await _collect_status(self.bot)
        panel_message = await target.send(view=_build_status_panel(self.bot, status))

        if cxn is not None:
            try:
                await cxn.execute(
                    "INSERT OR REPLACE INTO persistent_status_panels "
                    "(channel_id, guild_id, message_id, created_at) "
                    "VALUES ($1, $2, $3, datetime('now'))",
                    target.id,
                    guild_id,
                    panel_message.id,
                )
            except Exception as exc:
                logging.warning("StaffPanels", f"Could not persist status panel: {exc}")

        done_view = discord.ui.LayoutView()
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('tick')} Status panel sent to {target.mention}.\n"
                f"-# It auto-refreshes every {int(STATUS_PANEL_INTERVAL)} seconds."
            )),
            accent_colour=discord.Color.green(),
        ))
        await busy_message.edit(view=done_view)

    @sendpanel.command(
        name="rules",
        help=CMDS.help("sendpanel.rules"),
    )
    async def sendpanel_rules(self, ctx, channel: discord.TextChannel = None):
        """Post (or replace) the persistent rules panel in a channel."""
        target = channel or ctx.channel
        guild_id = getattr(getattr(target, "guild", None), "id", None)
        if guild_id is None:
            guild_id = getattr(ctx.guild, "id", None)
        if guild_id is None:
            return await ctx.send("This command must be used inside a server.")

        busy_view = discord.ui.LayoutView()
        busy_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{get_emoji('loading')} Building rules panel...")
        ))
        busy_message = await ctx.send(view=busy_view)

        # Remove the previous rules panel for this channel so re-running
        # replaces it instead of stacking duplicates.
        cxn = getattr(self.bot, "cxn", None)
        if cxn is not None:
            try:
                row = await cxn.fetchrow(
                    "SELECT message_id FROM persistent_rules_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
                if row:
                    old = target.get_partial_message(int(row["message_id"]))
                    await old.delete()
            except Exception:
                pass
            try:
                await cxn.execute(
                    "DELETE FROM persistent_rules_panels "
                    "WHERE channel_id = $1 AND guild_id = $2",
                    target.id,
                    guild_id,
                )
            except Exception:
                pass

        panel_message = await target.send(view=_build_rules_panel(self.bot))

        if cxn is not None:
            try:
                await cxn.execute(
                    "INSERT OR REPLACE INTO persistent_rules_panels "
                    "(channel_id, guild_id, message_id, created_at) "
                    "VALUES ($1, $2, $3, datetime('now'))",
                    target.id,
                    guild_id,
                    panel_message.id,
                )
            except Exception as exc:
                logging.warning("StaffPanels", f"Could not persist rules panel: {exc}")

        done_view = discord.ui.LayoutView()
        done_view.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=(
                f"{get_emoji('tick')} Rules panel sent to {target.mention}.\n"
                "-# Its buttons and menus keep working across restarts."
            )),
            accent_colour=discord.Color.green(),
        ))
        await busy_message.edit(view=done_view)
