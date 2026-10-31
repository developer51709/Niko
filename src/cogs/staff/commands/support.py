"""``.staff supportsetup``, ``supportupdate`` and ``getreport``."""

import io

import discord
from discord.ext import commands

from config.ids import SUPPORT_GUILD
from cogs.staff.base import CMDS, StaffCommands
from cogs.staff.support_server import (
    assign_support_roles,
    create_support_invite,
    persist_support_ids,
    reconcile_structure,
)
from cogs.staff.support_setup import (
    _configure_support_systems,
    _send_support_panels,
    bot_member_preflight,
)
from utils.error_reports import get_error_report


class SupportCommands:
    """Rebuild or refresh the official support server, and read error reports."""

    @StaffCommands.staff.command(name="supportsetup", help=CMDS.help("staff.supportsetup"), hidden=True)
    @commands.guild_only()
    async def support_setup(self, ctx: commands.Context):
        if ctx.guild.id != SUPPORT_GUILD:
            return await ctx.send("This command only works inside the configured support guild.")
        decision = {"confirmed": False}
        confirmation = discord.ui.LayoutView(timeout=120)
        confirmation_text = discord.ui.TextDisplay(content="## ⚠️ Rebuild the official support server? — This deletes all channels and manageable custom roles, then recreates the configured community. Managed roles and Niko’s own role are preserved. This cannot be undone.")
        confirm_button = discord.ui.Button(label="Rebuild server", style=discord.ButtonStyle.danger)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)

        def set_confirmation_text(content: str) -> None:
            for component in confirmation.walk_children():
                if isinstance(component, discord.ui.TextDisplay):
                    component.content = content
                    return

        async def choose(interaction: discord.Interaction, confirmed: bool):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("Only the command author can confirm this rebuild.", ephemeral=True)
            decision["confirmed"] = confirmed
            for item in (confirm_button, cancel_button):
                item.disabled = True
            set_confirmation_text(
                "Confirmed. Rebuilding the support server… this may take a few minutes."
                if confirmed else "Support-server rebuild cancelled."
            )
            await interaction.response.edit_message(view=confirmation)
            confirmation.stop()

        confirm_button.callback = lambda interaction: choose(interaction, True)
        cancel_button.callback = lambda interaction: choose(interaction, False)
        confirmation.add_item(discord.ui.Container(
            confirmation_text,
            discord.ui.ActionRow(confirm_button, cancel_button),
            accent_colour=discord.Colour.red(),
        ))
        response = await ctx.send(view=confirmation)
        if await confirmation.wait() or not decision["confirmed"]:
            for item in (confirm_button, cancel_button):
                item.disabled = True
            set_confirmation_text(
                "Support-server rebuild cancelled (confirmation timed out)."
                if not decision["confirmed"] else "Support-server rebuild cancelled."
            )
            await response.edit(view=confirmation)
            return
        # The invoking channel is about to be deleted during rebuild, so secure
        # a durable progress channel before making any destructive API calls.
        try:
            progress = await ctx.author.send("Support-server rebuild confirmed; setup is in progress…")
        except discord.Forbidden:
            set_confirmation_text(
                "Setup was not started: I could not DM you progress updates. "
                "Enable DMs from this server, then run `.staff supportsetup` again."
            )
            await response.edit(view=confirmation)
            return
        try:
            await bot_member_preflight(ctx.guild)
            roles, channels = await reconcile_structure(ctx.guild, destructive=True)
            await persist_support_ids(self.bot, ctx.guild, roles, channels)
            invite_url = await create_support_invite(self.bot, ctx.guild, channels)
            await _configure_support_systems(self.bot, ctx.guild, roles, channels)
            await _send_support_panels(self.bot, ctx.guild, roles, channels, invite_url=invite_url)
            await assign_support_roles(self.bot, ctx.guild, roles)
        except Exception as exc:
            report = f"Support setup stopped: `{type(exc).__name__}: {exc}`. Review permissions/role hierarchy, then run `.staff supportupdate` to finish safely."
            try:
                await progress.edit(content=report)
            except discord.HTTPException:
                await ctx.author.send(report)
            return
        report = f"✅ Support server rebuilt: **{len(roles)} roles**, **{len(channels)} channels**, panels posted and current members synchronized."
        try:
            await progress.edit(content=report)
        except discord.HTTPException:
            await ctx.author.send(report)

    @StaffCommands.staff.command(name="supportupdate", help=CMDS.help("staff.supportupdate"), hidden=True)
    @commands.guild_only()
    async def support_update(self, ctx: commands.Context):
        if ctx.guild.id != SUPPORT_GUILD:
            return await ctx.send("This command only works inside the configured support guild.")
        progress = await ctx.send("Checking and reconciling the support server…")
        try:
            roles, channels = await reconcile_structure(ctx.guild)
            await persist_support_ids(self.bot, ctx.guild, roles, channels)
            invite_url = await create_support_invite(self.bot, ctx.guild, channels)
            await _configure_support_systems(self.bot, ctx.guild, roles, channels)
            await _send_support_panels(self.bot, ctx.guild, roles, channels, invite_url=invite_url)
            await assign_support_roles(self.bot, ctx.guild, roles)
        except Exception as exc:
            await progress.edit(content=f"Support update incomplete: `{type(exc).__name__}: {exc}`.")
            return
        await progress.edit(content=f"✅ Support server reconciled: **{len(roles)} roles** and **{len(channels)} channels** verified; panels and member roles refreshed.")

    @StaffCommands.staff.command(name="getreport", help=CMDS.help("staff.getreport"), hidden=True)
    async def get_report(self, ctx: commands.Context, code: str):
        """Fetch an error report by its six-character code."""
        report = await get_error_report(code, self.bot)
        if report is None:
            return await ctx.send("No error report was found for that code.")

        report_file = discord.File(
            io.BytesIO(report.encode("utf-8")),
            filename=f"error-report-{code.strip().upper()}.txt",
        )
        try:
            await ctx.author.send(
                content=f"Error report `{code.strip().upper()}` attached.",
                file=report_file,
            )
        except discord.Forbidden:
            return await ctx.send("I couldn't DM you the report. Please enable DMs from this server and try again.")
        await ctx.send(f"Sent error report `{code.strip().upper()}` to your DMs.")
