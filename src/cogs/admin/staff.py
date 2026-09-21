"""Unified private staff command surface.

The legacy owner/development implementations are reused as command callbacks,
but they are only registered below ``staff`` so private tooling has one
consistent entry point.
"""

from __future__ import annotations

import time

import discord
from discord.ext import commands

from config.ids import OWNER_IDS
from cogs.admin.owner import OwnerCog, _StatusPanelCog
from cogs.admin.development import Development


STAFF_ROLES = {
    "head_admin": "Head Admin",
    "moderator": "Moderator",
    "head_support": "Head of Support",
    "support": "Support Team",
}
ROLE_ORDER = ("head_admin", "moderator", "head_support", "support")

# Commands which are deliberately reserved for the bot owner, even when a
# staff member has another role. Blacklist is relaxed below for Head Admins.
OWNER_ONLY_COMMANDS = {
    "broadcast", "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
    "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "dev01",
    "deveval", "devexec", "devsay", "devshutdown", "devload", "devunload", "devreload",
    "sendstatuspanel",
}

HEAD_ADMIN_COMMANDS = {
    "blacklist", "premium", "servers", "serverinvite", "announce",
}
SUPPORT_COMMANDS = {"ping", "latency", "uptime"}
HEAD_SUPPORT_COMMANDS = SUPPORT_COMMANDS | {"mem", "tasks", "guild", "channels", "roles", "members"}
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
    if role is None:
        await pool.execute("DELETE FROM staff_members WHERE user_id = $1", int(user_id))
        return
    await pool.execute(
        "INSERT OR REPLACE INTO staff_members (user_id, role, assigned_by, assigned_at) VALUES ($1, $2, $3, $4)",
        int(user_id), role, int(assigned_by), int(time.time()),
    )


async def is_staff_member(ctx: commands.Context) -> bool:
    if _is_owner_user(ctx.author, ctx.bot):
        return True
    return await get_staff_role(ctx.bot, ctx.author.id) is not None


async def _role_for(ctx: commands.Context) -> str | None:
    if _is_owner_user(ctx.author, ctx.bot):
        return "owner"
    return await get_staff_role(ctx.bot, ctx.author.id)


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
    if role == "head_support":
        return HEAD_SUPPORT_COMMANDS
    if role == "moderator":
        return MODERATOR_COMMANDS
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

    @staff.command(name="help", hidden=True)
    async def staff_help(self, ctx: commands.Context):
        if not await is_staff_member(ctx):
            return await ctx.send("This command is restricted to official Niko staff.")
        await ctx.send(view=build_staff_help(self.bot, ctx, "all"))

    @staff.command(name="manage", hidden=True)
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


async def setup(bot):
    # OwnerCog used to be loaded directly and also owned the status refresh
    # loop. The command surface now lives under StaffCog, so register the
    # internal panel cog explicitly without re-registering owner commands.
    await bot.add_cog(StaffCog(bot))
    await bot.add_cog(_StatusPanelCog(bot))
