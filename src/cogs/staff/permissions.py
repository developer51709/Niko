"""Who may run which ``.staff`` subcommand.

The ``.staff`` group is one command tree, so a single role allow-list keyed by
the subcommand name decides access for every command, and the staff cog's
``cog_check`` is the only place that runs it.
"""

import json

from discord.ext import commands

from cogs.staff.records import STAFF_ROLES, is_staff_member, role_for

# Commands which are deliberately reserved for the bot owner, even when a
# staff member has another role. Blacklist is relaxed below for Head Admins.
OWNER_ONLY_COMMANDS = {
    "setpfp", "setbanner", "setusername", "setstatus", "setactivity",
    "load", "unload", "reload", "restart", "shutdown", "sync", "eval", "exec",
    "say", "dev01", "shardinfo", "shardstats", "shardhealth",
    # replaceemojis deletes and re-uploads every application emoji and rewrites
    # the ids the rest of the bot sends, so it stays with the owner.
    "replaceemojis",
    "sendpanel", "supportsetup", "supportupdate",
    # The staff roster is the owner's call — never a peer's.
    "manage",
}

#: Available to every recognised staff role, owner included.
STAFF_ONLY_COMMANDS = {"help"}

HEAD_ADMIN_COMMANDS = {
    "blacklist", "premium", "servers", "serverinvite", "announce",
}
SUPPORT_COMMANDS = {"ping", "latency", "uptime", "getreport"}
GRAPHIC_DESIGNER_COMMANDS = SUPPORT_COMMANDS | {"mem", "tasks", "guild", "channels", "roles", "members"}
HEAD_SUPPORT_COMMANDS = GRAPHIC_DESIGNER_COMMANDS
MODERATOR_COMMANDS = {"ping", "latency", "uptime"}

_KNOWN_ROLES = frozenset({"owner", *STAFF_ROLES})


def command_names_for_role(role: str) -> set[str]:
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
    if role in {"event_coordinator", "partnerships_promotions_lead", "partnership_manager"}:
        return SUPPORT_COMMANDS
    return set()


def role_label(role: str) -> str:
    """Public label for a staff role key, including the owner."""
    if role == "owner":
        return "Owner"
    return STAFF_ROLES.get(role, role)


def staff_command_name(command) -> str:
    """Resolve the top-level ``staff`` subcommand a command belongs to.

    The ``staff`` group is the top of the tree, so resolving the first command
    below it lets direct commands (``servers``) and nested commands
    (``blacklist info``) share one name for the role allow-lists.
    """
    name = getattr(command, "name", "") or ""
    parent = getattr(command, "parent", None)
    while parent is not None and getattr(parent, "name", None) != "staff":
        name = getattr(parent, "name", None) or name
        parent = getattr(parent, "parent", None)
    return name


def command_allowed_for_role(role: str | None, command_name: str) -> bool:
    """Return whether ``role`` may use one top-level ``staff`` subcommand.

    Deny by default: a command is available only when the role lists it, so an
    unknown or empty role reaches nothing. Owner-reserved tooling stays reserved
    for the owner, and Head Admin tooling (blacklist, premium, invites,
    announcements) is never inherited by the other staff roles.
    """
    if command_name in OWNER_ONLY_COMMANDS:
        return role == "owner"
    if role == "owner":
        return True
    if role not in _KNOWN_ROLES:
        return False
    if command_name in STAFF_ONLY_COMMANDS:
        return True
    if command_name == "getreport":
        return True
    return command_name in command_names_for_role(role)


async def staff_permission(ctx: commands.Context) -> bool:
    """The cog check: are they staff, and may their role run this subcommand?"""
    if not await is_staff_member(ctx):
        return False
    return command_allowed_for_role(await role_for(ctx), staff_command_name(ctx.command))


def help_line(command, lang: str) -> str:
    """A command's help line, read from its ``{language: text}`` map.

    ``CMDS.help`` serialises every translation of a command's wording onto
    ``command.help``, so the panel has to pick one language out of that map
    instead of printing the map itself.
    """
    raw = getattr(command, "help", None)
    if not raw:
        return "No description."
    if isinstance(raw, dict):
        values = raw
    else:
        try:
            values = json.loads(raw)
        except (TypeError, ValueError):
            # A command that only declared a plain help string.
            return str(raw)
    if not isinstance(values, dict):
        return str(raw)
    return values.get(lang) or values.get("en") or "No description."
