import asyncio
import sys
import types
from pathlib import Path

import discord
from discord.ext import commands

sys.path.insert(0, "src")

from config import ids as config_ids  # noqa: E402
from cogs.staff.help import build_staff_help  # noqa: E402
from cogs.staff.permissions import (  # noqa: E402
    HEAD_ADMIN_COMMANDS,
    OWNER_ONLY_COMMANDS,
    command_allowed_for_role,
)
from cogs.staff.records import STAFF_ROLES, get_staff_role  # noqa: E402
from cogs.staff.staff import StaffCog  # noqa: E402


NON_ADMIN_ROLES = (
    "moderator",
    "head_support",
    "graphic_designer",
    "support",
    "event_coordinator",
    "partnerships_promotions_lead",
    "partnership_manager",
)


async def _check_staff_cog():
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    await bot.add_cog(StaffCog(bot))
    root = bot.get_command("staff")
    assert root is not None
    assert root.hidden is True
    names = {command.name for command in root.commands}
    assert {"help", "manage", "ping", "latency", "dev01"} <= names
    assert "devhelp" not in names
    assert "ownerhelp" not in names
    assert len(names) == len(root.commands)
    assert all(command.hidden for command in root.commands)
    assert set(STAFF_ROLES) == {
        "head_admin",
        "moderator",
        "head_support",
        "graphic_designer",
        "support",
        "event_coordinator",
        "partnerships_promotions_lead",
        "partnership_manager",
    }


def _staff_command_names() -> set[str]:
    """Return the top-level names registered under ``.staff``."""
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    asyncio.run(bot.add_cog(StaffCog(bot)))
    return {command.name for command in bot.get_command("staff").commands}


def test_head_admin_tooling_is_reserved_for_head_admins():
    """Head Admin commands must never fall through to the other staff roles.

    Their owner check is removed so Head Admins can use them, which means the
    role allow-list is the only guard left.
    """
    for command in sorted(HEAD_ADMIN_COMMANDS):
        assert command_allowed_for_role("head_admin", command), command
        for role in NON_ADMIN_ROLES:
            assert not command_allowed_for_role(role, command), f"{role} must not reach .staff {command}"


def test_owner_only_commands_stay_reserved():
    for command in sorted(OWNER_ONLY_COMMANDS):
        assert command_allowed_for_role("owner", command), command
        for role in NON_ADMIN_ROLES + ("head_admin",):
            assert not command_allowed_for_role(role, command), f"{role} must not reach .staff {command}"


def test_owner_only_names_exist_as_commands():
    """Stale names would silently leave a command unguarded."""
    registered = _staff_command_names()
    assert OWNER_ONLY_COMMANDS <= registered, sorted(OWNER_ONLY_COMMANDS - registered)
    assert HEAD_ADMIN_COMMANDS <= registered
    assert "exec" in registered and "say" in registered


def test_retired_developer_role_is_unreachable():
    """The developer role was removed; nothing may reintroduce a path to it."""
    assert not hasattr(config_ids, "DEVELOPER_IDS")
    for command in ("ping", "mem", "tasks", "syncemojis", "guild", "getreport"):
        assert not command_allowed_for_role("developer", command), command


def test_no_source_references_the_removed_developer_list():
    root = Path(__file__).resolve().parent.parent / "src"
    offenders = [
        str(path.relative_to(root.parent))
        for path in root.rglob("*.py")
        if "DEVELOPER_IDS" in path.read_text(encoding="utf-8")
    ]
    assert not offenders, offenders


def test_non_staff_and_unknown_roles_are_denied():
    for role in (None, ""):
        for command in ("ping", "getreport", "blacklist", "exec"):
            assert not command_allowed_for_role(role, command), f"{role!r} must not reach .staff {command}"


def _help_panel_text(locale: str) -> str:
    """Render ``.staff help`` for a guild whose preferred locale is ``locale``."""
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.none())
    asyncio.run(bot.add_cog(StaffCog(bot)))
    guild = types.SimpleNamespace(preferred_locale=discord.Locale(locale), id=1)
    ctx = types.SimpleNamespace(guild=guild, author=types.SimpleNamespace(id=1))
    view = build_staff_help(bot, ctx, "owner")
    return "\n".join(
        child.content for child in view.walk_children()
        if isinstance(child, discord.ui.TextDisplay)
    )


def test_staff_help_reads_the_localised_description_maps():
    """``command.help`` holds a ``{language: text}`` map, not a plain string."""
    expected = {
        "en-US": "Announce the latest Niko update",
        "de": "Kündige das neueste Niko-Update",
        "es-ES": "Anuncia la última actualización de Niko",
    }
    for locale, wording in expected.items():
        text = _help_panel_text(locale)
        assert f"**`.staff announce`** — {wording}" in text, locale
        # The serialised map itself must never reach the panel.
        assert '"de"' not in text and '"es"' not in text, locale


def test_unknown_users_are_not_staff():
    bot = types.SimpleNamespace(cxn=None)
    assert asyncio.run(get_staff_role(bot, 987654321098765432)) is None
    assert asyncio.run(get_staff_role(bot, "not-an-id")) is None


if __name__ == "__main__":
    asyncio.run(_check_staff_cog())
    print("staff cog regression checks passed")
