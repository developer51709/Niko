"""Unified private staff command surface.

The legacy owner/development implementations are reused as command callbacks,
but they are only registered below ``staff`` so private tooling has one
consistent entry point.
"""

from __future__ import annotations

import time
import io
import asyncio


import discord
from discord.ext import commands

from config.ids import OWNER_IDS, SUPPORT_GUILD
from cogs.staff.support_server import (
    CHANNEL_SPECS, ROLE_SPECS, SupportGuidePanel, SupportPingPanel, assign_support_roles,
    create_support_invite, get_support_ids, persist_support_ids,
    reconcile_structure, support_rules_text,
)
from cogs.staff.owner import OwnerCog, _StatusPanelCog
from cogs.staff.development import Development
from utils.error_reports import get_error_report


STAFF_ROLES = {
    "head_admin": "Head Admin",
    "moderator": "Moderator",
    "head_support": "Head of Support",
    "graphic_designer": "Graphic Designer",
    "support": "Support Team",
}
ROLE_ORDER = ("head_admin", "moderator", "graphic_designer", "head_support", "support")

# Commands which are deliberately reserved for the bot owner, even when a
# staff member has another role. Blacklist is relaxed below for Head Admins.
OWNER_ONLY_COMMANDS = {
    "broadcast", "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
    "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "dev01",
    "devexec", "devsay",
    "sendpanel", "supportsetup", "supportupdate",
}

HEAD_ADMIN_COMMANDS = {
    "blacklist", "premium", "servers", "serverinvite", "announce",
}
SUPPORT_COMMANDS = {"ping", "latency", "uptime", "getreport"}
GRAPHIC_DESIGNER_COMMANDS = SUPPORT_COMMANDS | {"mem", "tasks", "guild", "channels", "roles", "members"}
HEAD_SUPPORT_COMMANDS = GRAPHIC_DESIGNER_COMMANDS
MODERATOR_COMMANDS = {"ping", "latency", "uptime"}


def _is_owner_user(user, bot) -> bool:
    return user.id in OWNER_IDS


async def get_staff_role(bot, user_id: int) -> str | None:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return None
    row = await pool.fetchrow(
        "SELECT role FROM staff_members WHERE user_id = $1", int(user_id)
    )
    return str(row["role"]) if row and row.get("role") in STAFF_ROLES else None


async def set_staff_role(bot, user_id: int, role: str | None, assigned_by: int) -> None:
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The staff database is not ready yet.")
    if role is not None and role not in STAFF_ROLES:
        raise ValueError(f"Unknown Niko staff role: {role}")
    if role is None:
        await pool.execute("DELETE FROM staff_members WHERE user_id = $1", int(user_id))
        support_guild = bot.get_guild(SUPPORT_GUILD)
        member = support_guild.get_member(int(user_id)) if support_guild else None
        if member:
            await sync_member_staff_roles(bot, member, None)
        return
    await pool.execute(
        "INSERT OR REPLACE INTO staff_members (user_id, role, assigned_by, assigned_at) VALUES ($1, $2, $3, $4)",
        int(user_id), role, int(assigned_by), int(time.time()),
    )
    support_guild = bot.get_guild(SUPPORT_GUILD)
    member = support_guild.get_member(int(user_id)) if support_guild else None
    if member:
        await sync_member_staff_roles(bot, member, role)


async def is_staff_member(ctx: commands.Context) -> bool:
    if _is_owner_user(ctx.author, ctx.bot):
        return True
    return await get_staff_role(ctx.bot, ctx.author.id) is not None


async def _role_for(ctx: commands.Context) -> str | None:
    if _is_owner_user(ctx.author, ctx.bot):
        return "owner"
    return await get_staff_role(ctx.bot, ctx.author.id)


async def sync_member_staff_roles(bot, member: discord.Member, staff_key: str | None) -> None:
    if member.guild.id != SUPPORT_GUILD:
        return
    roles = (await get_support_ids(bot))["roles"]

    to_add, to_remove = [], []
    shared_id = roles.get("staff")
    shared = member.guild.get_role(int(shared_id)) if shared_id else None
    valid_staff_key = staff_key if staff_key in ROLE_ORDER else None
    if shared and valid_staff_key and shared not in member.roles:
        to_add.append(shared)
    elif shared and not valid_staff_key and shared in member.roles:
        to_remove.append(shared)
    for key in ROLE_ORDER:
        role_id = roles.get(key)
        role = member.guild.get_role(int(role_id)) if role_id else None
        if role and key == valid_staff_key and role not in member.roles:
            to_add.append(role)
        elif role and key != valid_staff_key and role in member.roles:
            to_remove.append(role)
    if to_remove:
        await member.remove_roles(*to_remove, reason="Niko staff assignment changed")
    if to_add:
        await member.add_roles(*to_add, reason="Niko staff assignment changed")


class StaffRoleSelect(discord.ui.Select):
    def __init__(self, bot, target: discord.Member, owner_id: int):
        self.bot = bot
        self.target = target
        self.owner_id = owner_id
        options = [
            discord.SelectOption(
                label=STAFF_ROLES[key],
                value=key,
                description=f"Assign the {STAFF_ROLES[key]} staff role.",
            )
            for key in ROLE_ORDER
        ]
        options.append(discord.SelectOption(
            label="Revoke staff access",
            value="revoke",
            description="Remove the user's staff role.",
        ))
        super().__init__(placeholder="Choose a staff role…", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("Only the bot owner can manage staff access.", ephemeral=True)
        value = self.values[0]
        role = None if value == "revoke" else value
        await set_staff_role(self.bot, self.target.id, role, interaction.user.id)
        message = (
            f"Revoked staff access from {self.target.mention}."
            if role is None
            else f"Assigned **{STAFF_ROLES[role]}** to {self.target.mention}."
        )
        view = discord.ui.LayoutView()
        view.add_item(discord.ui.Container(discord.ui.TextDisplay(content=f"### Staff access updated\n{message}"), accent_colour=discord.Colour.green()))
        await interaction.response.edit_message(view=view)


class StaffManageView(discord.ui.LayoutView):
    def __init__(self, bot, target: discord.Member, owner_id: int, current_role: str | None = None):
        super().__init__(timeout=300)
        current = "Owner" if target.id in OWNER_IDS else STAFF_ROLES.get(current_role, "No staff role assigned")
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### Manage staff access\n**User:** {target.mention}\n**Current:** {current}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(StaffRoleSelect(bot, target, owner_id)),
            accent_colour=discord.Colour(0xC8A882),
        )
        self.add_item(container)


class StaffHelpSelect(discord.ui.Select):
    def __init__(self, bot, ctx: commands.Context):
        self.bot = bot
        self.ctx = ctx
        options = [
            discord.SelectOption(label="All staff commands", value="all", description="Show commands available to every staff role."),
            discord.SelectOption(label="Owner commands", value="owner", description="Show bot-owner-only commands."),
            *[
                discord.SelectOption(label=STAFF_ROLES[key], value=key, description=f"Show {STAFF_ROLES[key]} commands.")
                for key in ROLE_ORDER
            ],
        ]
        super().__init__(placeholder="Choose a staff role to view…", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not await _is_staff_interaction(interaction):
            return await interaction.response.send_message("This help menu is for official Niko staff only.", ephemeral=True)
        value = self.values[0]
        if value == "owner" and interaction.user.id not in OWNER_IDS:
            return await interaction.response.send_message(
                "Only the bot owner can view owner commands.", ephemeral=True
            )
        await interaction.response.edit_message(view=build_staff_help(self.bot, interaction, value))


async def _is_staff_interaction(interaction: discord.Interaction) -> bool:
    if interaction.user.id in OWNER_IDS:
        return True
    return await get_staff_role(interaction.client, interaction.user.id) is not None


def _command_names_for_role(role: str) -> set[str]:
    if role == "owner":
        return {"*"}
    if role == "head_admin":
        return HEAD_ADMIN_COMMANDS | HEAD_SUPPORT_COMMANDS | MODERATOR_COMMANDS
    if role == "graphic_designer":
        return GRAPHIC_DESIGNER_COMMANDS
    if role == "head_support":
        return HEAD_SUPPORT_COMMANDS
    if role == "moderator":
        return MODERATOR_COMMANDS | {"getreport"}
    if role == "support":
        return SUPPORT_COMMANDS
    return set()


def build_staff_help(bot, ctx_or_interaction, selected_role: str = "all") -> discord.ui.LayoutView:
    role = selected_role
    if role == "all":
        role_label = "All staff"
        names = SUPPORT_COMMANDS
    else:
        role_label = "Owner" if role == "owner" else STAFF_ROLES.get(role, role)
        names = _command_names_for_role(role)

    lines = []
    for command in sorted(bot.get_command("staff").commands, key=lambda item: item.name):
        if command.name in {"help", "manage"}:
            continue
        short_name = command.name
        if names == {"*"} or short_name in names:
            lines.append(f"**`.staff {short_name}`** — {command.help or 'No description.'}")
    if not lines:
        lines.append("No commands are assigned to this role yet.")

    view = discord.ui.LayoutView(timeout=300)
    view.add_item(discord.ui.Container(
        discord.ui.TextDisplay(content=f"# Staff commands — {role_label}\n" + "\n".join(lines)),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
        discord.ui.ActionRow(StaffHelpSelect(bot, ctx_or_interaction)),
        accent_colour=discord.Colour(0x5865F2),
    ))
    return view


class StaffCog(commands.Cog):
    """One private command group for Niko owners and official staff."""

    def __init__(self, bot):
        self.bot = bot
        self._owner_source = OwnerCog(bot)
        self._development_source = Development(bot)
        self._register_legacy_commands()

    @commands.group(name="staff", invoke_without_command=True, hidden=True)
    async def staff(self, ctx: commands.Context):
        """Private Niko staff tools."""
        if not await is_staff_member(ctx):
            return await ctx.send("This command is restricted to official Niko staff.")
        await ctx.send(view=build_staff_help(self.bot, ctx, "all"))

    @staff.command(name="help", help="Show staff commands available to your role.", hidden=True)
    async def staff_help(self, ctx: commands.Context):
        if not await is_staff_member(ctx):
            return await ctx.send("This command is restricted to official Niko staff.")
        await ctx.send(view=build_staff_help(self.bot, ctx, "all"))

    @staff.command(name="supportsetup", help="Rebuild the official support server after an explicit confirmation.", hidden=True)
    @commands.guild_only()
    async def support_setup(self, ctx: commands.Context):
        if not _is_owner_user(ctx.author, ctx.bot):
            return await ctx.send("Only the bot owner can rebuild the support server.")
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

    @staff.command(name="supportupdate", help="Repair the support server structure and refresh its panels.", hidden=True)
    @commands.guild_only()
    async def support_update(self, ctx: commands.Context):
        if not _is_owner_user(ctx.author, ctx.bot):
            return await ctx.send("Only the bot owner can update the support server.")
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

    @staff.command(name="getreport", help="Fetch a full error report using its six-character code.", hidden=True)
    async def get_report(self, ctx: commands.Context, code: str):
        """Fetch an error report by its six-character code."""
        if not await is_staff_member(ctx):
            return await ctx.send("This command is restricted to official Niko staff.")
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

    @staff.command(name="manage", help="Assign or revoke a staff role for a member.", hidden=True)
    async def staff_manage(self, ctx: commands.Context, target: discord.Member):
        if not _is_owner_user(ctx.author, ctx.bot):
            return await ctx.send("Only the bot owner can manage staff access.")
        current_role = await get_staff_role(self.bot, target.id)
        await ctx.send(view=StaffManageView(self.bot, target, ctx.author.id, current_role))

    async def _staff_check(self, ctx: commands.Context) -> bool:
        if not await is_staff_member(ctx):
            return False
        command = ctx.command
        # ``root_parent`` is the ``staff`` group itself. Resolve the first
        # command below that group so direct commands (``servers``) and nested
        # commands (``blacklist info``) are checked against the right role.
        command_name = getattr(command, "name", "")
        parent = getattr(command, "parent", None)
        while parent is not None and getattr(parent, "name", None) != "staff":
            command_name = parent.name
            parent = getattr(parent, "parent", None)
        role = await _role_for(ctx)
        if role == "owner":
            return True
        if command_name == "getreport":
            return True
        if command_name in OWNER_ONLY_COMMANDS:
            return False
        allowed = _command_names_for_role(role)
        return command_name in allowed or command_name in HEAD_ADMIN_COMMANDS

    @staticmethod
    def _remove_owner_checks(command):
        command.checks = [check for check in command.checks if "error_handler" not in getattr(check, "__module__", "")]
        for child in getattr(command, "commands", ()):
            StaffCog._remove_owner_checks(child)

    def _register_legacy_commands(self):
        seen: set[str] = {"help", "manage"}
        sources = (self._owner_source, self._development_source)
        for source in sources:
            for command in source.get_commands():
                original = command.name
                if original in {"ownerhelp", "devhelp"}:
                    continue
                name = original[3:] if original.startswith("dev") else original
                if name in seen:
                    continue
                seen.add(name)
                command.name = name
                command.aliases = []
                command.hidden = True
                # Command callbacks retrieved from a Cog are unbound
                # functions. Once moved under StaffCog, discord.py supplies
                # StaffCog as ``self``; explicitly forward the callback to
                # the source cog instance or commands such as broadcast lose
                # their original ``ctx`` argument.
                def _forward_command_tree(subcommand):
                    source_callback = subcommand.callback
                    original_params = subcommand.params.copy()

                    async def _forward_callback(
                        ctx,
                        *args,
                        _source=source,
                        _callback=source_callback,
                        **kwargs,
                    ):
                        return await _callback(_source, ctx, *args, **kwargs)

                    subcommand.callback = _forward_callback
                    # Replacing the callback must not expose the forwarding
                    # implementation's internal parameters to the parser.
                    subcommand.params = original_params
                    for child in getattr(subcommand, "commands", ()):
                        _forward_command_tree(child)

                _forward_command_tree(command)
                # Head Admins may use the blacklist workflow; other owner
                # commands retain their existing owner check.
                if name in HEAD_ADMIN_COMMANDS:
                    self._remove_owner_checks(command)
                if original == "dev01":
                    command.name = name = "dev01"
                command.add_check(self._staff_check)
                self.staff.add_command(command)


async def bot_member_preflight(guild):
    bot_member = guild.me
    if bot_member is None or not bot_member.guild_permissions.administrator:
        raise RuntimeError("For the destructive setup, give Niko Administrator temporarily; then rerun the confirmed command. This prevents partial loss from inaccessible channels/roles.")


async def _save_support_panel_record(pool, guild_id: int, panel_key: str, channel_id: int, message_id: int) -> None:
    """Upsert a panel registry row using adapter-compatible conflict arguments."""
    await pool.execute(
        "INSERT INTO support_server_panels (guild_id, panel_key, channel_id, message_id, updated_at) "
        "VALUES ($1, $2, $3, $4, datetime('now')) "
        "ON CONFLICT (guild_id, panel_key) DO UPDATE SET channel_id = $5, message_id = $6, updated_at = datetime('now')",
        guild_id, panel_key, channel_id, message_id, channel_id, message_id,
    )


async def _save_voice_master_settings(pool, guild_id: int, channel_id: int, category_id: int) -> None:
    """Upsert the support guild's voice-master channel configuration."""
    await pool.execute(
        "INSERT INTO voicemaster_settings (guild_id, join_channel_id, category_id, default_name, default_limit, default_bitrate) "
        "VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (guild_id) DO UPDATE SET join_channel_id = $7, category_id = $8",
        guild_id, channel_id, category_id, "{user}'s Channel", 0, 64000, channel_id, category_id,
    )


async def _configure_support_systems(bot, guild, roles, channels):
    from utils.onboarding.utils import get_config, update_config
    from utils.tickets.utils import get_ticket_config, async_update_ticket_config

    onboarding = await get_config(guild.id)
    onboarding.welcome_channel = int(channels["welcome"])
    onboarding.welcome_title = "Welcome to the Niko community"
    onboarding.welcome_description = "Welcome {user}! Start with the rules, choose your notification roles, and ask for help any time."
    onboarding.autorole_ids = [int(roles["member"])]
    onboarding.welcome_color = 0xC8A882
    onboarding.welcome_image = None
    onboarding.captcha_enabled = False
    onboarding.captcha_channel_id = None
    onboarding.captcha_panel_message_id = None
    onboarding.captcha_add_role_ids = []
    onboarding.captcha_remove_role_ids = []
    onboarding.captcha_kick_on_fail = False

    await update_config(guild.id, onboarding)
    from utils.onboarding.config import _pool
    onboarding_pool = _pool()
    if onboarding_pool is None:
        raise RuntimeError("The database is unavailable; onboarding settings could not be saved.")
    if onboarding_pool.db_type != "mongodb":
        saved_config = await onboarding_pool.fetchrow("SELECT guild_id FROM onboarding WHERE guild_id = $1", guild.id)
    else:
        saved_config = await onboarding_pool.collection("onboarding").find_one({"_id": str(guild.id)})
    if not saved_config:
        raise RuntimeError("Onboarding settings could not be saved to the database.")

    ticket_cfg = get_ticket_config(guild.id)
    ticket_cfg.panel_title = "Contact Niko Support"
    ticket_cfg.panel_description = "Open a private ticket for account help, bot troubleshooting, safety concerns, or other questions that need staff attention."
    ticket_cfg.panel_categories = ["General Support", "Bug Report", "Account & Billing", "Moderation Appeal"]
    ticket_cfg.support_roles = [int(roles[key]) for key in ("staff", "head_admin", "moderator", "head_support", "support")]
    ticket_cfg.panel_channel_id = int(channels["tickets"])
    ticket_cfg.panel_message_id = None
    if not await async_update_ticket_config(guild.id, ticket_cfg):
        raise RuntimeError("Ticket settings could not be saved to the database.")

    from cogs.logging.formatters import _guild_config, _load_log_config, _save_guild_log_config
    all_logs = await _load_log_config()
    log_cfg = dict(_guild_config(all_logs, guild.id))
    log_cfg.update(_support_log_channels(channels))
    await _save_guild_log_config(guild.id, log_cfg)

    from cogs.automod import mrbeast_scam
    await mrbeast_scam.set_review_channel(bot, int(channels["scam_review"]))

    join_channel = guild.get_channel(int(channels["voice_join"]))
    if join_channel is None:
        raise RuntimeError("The configured voice-master join channel disappeared before its settings were saved.")
    await _save_voice_master_settings(
        bot.cxn, guild.id, join_channel.id, join_channel.category_id,
    )
    voice_cog = bot.get_cog("VoiceMaster")
    if voice_cog:
        voice_cog._bust_cache(guild.id)


def _panel_channel_key(panel_key: str, channel_key: str | None = None) -> str:
    """Resolve a panel's target channel without evaluating a parameter as a default."""
    return channel_key or panel_key


def _support_log_channels(channels: dict) -> dict[str, int]:
    """Map each logging event group to its dedicated support-server channel."""
    return {
        "moderation": int(channels["logs"]),
        "automod": int(channels["automod_logs"]),
        "members": int(channels["member_logs"]),
        "messages": int(channels["message_logs"]),
        "channels": int(channels["channel_logs"]),
    }


async def _send_support_panels(bot, guild, roles, channels, *, invite_url: str | None = None):
    from cogs.staff.owner import _build_status_panel, _collect_status
    from cogs.tickets.views import TicketPanelView
    from utils.tickets.utils import get_ticket_config, async_update_ticket_config
    from cogs.voicemaster.cog import VoiceMasterInterface

    pool = bot.cxn

    async def post(key, view, *, unique_table=None, channel_key=None):
        channel_key = _panel_channel_key(key, channel_key)
        channel = guild.get_channel(int(channels[channel_key]))
        if channel is None:
            raise RuntimeError(f"Configured channel `{channel_key}` disappeared before panel post.")
        old = await pool.fetchrow("SELECT message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = $2", guild.id, key)
        if old:
            try:
                await channel.get_partial_message(int(old["message_id"])).delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        message = await channel.send(view=view)
        await _save_support_panel_record(pool, guild.id, key, channel.id, message.id)
        if unique_table:
            old_unique = await pool.fetchrow(f"SELECT message_id FROM {unique_table} WHERE channel_id = $1 AND guild_id = $2", channel.id, guild.id)
            if old_unique:
                try:
                    await channel.get_partial_message(int(old_unique["message_id"])).delete()
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
            await pool.execute(f"DELETE FROM {unique_table} WHERE channel_id = $1 AND guild_id = $2", channel.id, guild.id)
            await pool.execute(
                f"INSERT INTO {unique_table} (channel_id, guild_id, message_id, created_at) VALUES ($1, $2, $3, datetime('now'))",
                channel.id, guild.id, message.id,
            )
        return message

    status = await _collect_status(bot)
    await post("status", _build_status_panel(bot, status), unique_table="persistent_status_panels")
    # Rules panel content is intentionally the established `.staff sendpanel rules` panel,
    # not the onboarding rules acknowledgement flow.
    from cogs.staff.owner import _build_rules_panel
    await post("rules", _build_rules_panel(bot), unique_table="persistent_rules_panels")
    await post("staff_rules", _staff_rules_panel(), channel_key="staff_rules")
    await post("staff_announcements", discord.ui.LayoutView().add_item(discord.ui.Container(discord.ui.TextDisplay(content="# Staff announcements\nOfficial internal updates and operational notices are posted here."), accent_colour=0xC8A882)), channel_key="staff_announcements")
    welcome_content = f"# Welcome to Niko\nStart with the server rules, choose your notification roles, and ask the community whenever you need a hand.\n\n[Join the support server]({invite_url})" if invite_url else "# Welcome to Niko\nStart with the server rules, choose your notification roles, and ask the community whenever you need a hand."
    await post("welcome", discord.ui.LayoutView().add_item(discord.ui.Container(discord.ui.TextDisplay(content=welcome_content), accent_colour=0xC8A882)), channel_key="welcome")
    await post("support_guide", SupportGuidePanel(channels), channel_key="support_guide")
    roles_message = await post("notification_roles", SupportPingPanel(), channel_key="roles")
    ticket_message = await post("tickets", TicketPanelView(guild.id, get_ticket_config(guild.id)))
    ticket_cfg = get_ticket_config(guild.id)
    ticket_cfg.panel_channel_id = ticket_message.channel.id
    ticket_cfg.panel_message_id = ticket_message.id
    if not await async_update_ticket_config(guild.id, ticket_cfg):
        raise RuntimeError("Ticket panel message settings could not be saved to the database.")
    voice_message = await post("voice_panel", VoiceMasterInterface())
    forum = guild.get_channel(int(channels["help"]))
    if not isinstance(forum, discord.ForumChannel):
        raise RuntimeError("The configured public help channel is not a forum.")
    old_guidelines = await pool.fetchrow("SELECT message_id FROM support_server_panels WHERE guild_id = $1 AND panel_key = 'forum-guidelines'", guild.id)
    if old_guidelines:
        old_thread = guild.get_thread(int(old_guidelines["message_id"]))
        if old_thread:
            try:
                await old_thread.delete(reason="Refresh support forum guidelines")
                await _support_api_pause()
            except discord.HTTPException:
                pass
    guideline_post = await forum.create_thread(
        name="Read first · community guidelines",
        content="# Welcome to Niko Support\n\n• Be kind and respectful.\n• Search existing posts before opening a new help topic.\n• Never share passwords, tokens, payment details, or other private information.\n• Use a private support ticket for account-specific or sensitive matters.\n• Keep each post focused and include relevant steps, error messages, and screenshots.",
        reason="Publish support forum guidelines",
    )
    await _support_api_pause()
    await guideline_post.message.pin(reason="Keep support forum guidelines at the top")
    await _support_api_pause()
    await guideline_post.thread.edit(locked=True, archived=True, reason="Lock the read-only forum guidelines thread")
    await _save_support_panel_record(
        pool, guild.id, "forum-guidelines", forum.id, guideline_post.thread.id,
    )

    bot.add_view(SupportGuidePanel(channels))
    bot.add_view(VoiceMasterInterface(), message_id=voice_message.id)
    bot.add_view(TicketPanelView(guild.id, get_ticket_config(guild.id)), message_id=ticket_message.id)
    bot.add_view(SupportPingPanel(), message_id=roles_message.id)


async def _support_api_pause():
    await asyncio.sleep(0.35)


def _staff_rules_panel():
    view = discord.ui.LayoutView()
    sections = support_rules_text().split("\n\n")
    items = [
        discord.ui.TextDisplay(content="# Staff guidelines\n-# Niko Support · Internal team handbook"),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
    ]
    items.extend(discord.ui.TextDisplay(content=section) for section in sections)
    view.add_item(discord.ui.Container(*items, accent_colour=0xC8A882))
    return view


async def setup(bot):
    # OwnerCog used to be loaded directly and also owned the status refresh
    # loop. The command surface now lives under StaffCog, so register the
    # internal panel cog explicitly without re-registering owner commands.
    await bot.add_cog(StaffCog(bot))
    await bot.add_cog(_StatusPanelCog(bot))
