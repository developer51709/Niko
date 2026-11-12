"""top.gg review requirements that are enforced by code, not by chance.

Two things get a bot rejected over and over: an invite that asks for
Administrator, and a feature that only works when the bot has Manage Channels.
The first is pinned by :data:`config.links.BOT_PERMISSIONS`; the second by the
overwrite helper the lock/unlock commands use. The last group keeps every
channel-posted settings panel behind a Manage Server check so a normal member
cannot drive one.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import discord  # noqa: E402

from config import links  # noqa: E402


# ──────────────────────────────────────────────────
#  Invite permissions
# ──────────────────────────────────────────────────

def test_the_invite_never_asks_for_administrator():
    permissions = discord.Permissions(links.BOT_PERMISSIONS)

    assert not permissions.administrator
    # The scoped set still has to cover what the features actually use.
    assert permissions.manage_roles        # lock/unlock, level rewards
    assert permissions.manage_channels     # tickets, temporary voice rooms
    assert permissions.view_audit_log      # anti-nuke, invite tracking
    assert permissions.manage_messages     # purge, censor
    assert permissions.kick_members and permissions.ban_members
    assert permissions.read_message_history
    assert permissions.connect and permissions.speak


def test_the_invite_url_carries_the_scoped_permission_integer():
    url = links.invite_url(123456789)
    query = parse_qs(urlparse(url).query)

    assert query["client_id"] == ["123456789"]
    assert query["permissions"] == [str(links.BOT_PERMISSIONS)]
    assert query["scope"] == ["bot applications.commands"]
    assert "guild_id" not in query


def test_the_invite_url_can_preselect_a_guild():
    query = parse_qs(urlparse(links.invite_url(1, guild_id=42)).query)

    assert query["guild_id"] == ["42"]


def test_no_invite_anywhere_still_hardcodes_administrator():
    offenders = []
    for path in list((ROOT / "src").rglob("*.py")):
        # ``permissions=8&`` is an actual query string; the constant in
        # config/links.py only documents the integer it replaced.
        if "permissions=8&" in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        "these modules still build an Administrator invite; use config.links.invite_url: "
        + ", ".join(offenders)
    )


# ──────────────────────────────────────────────────
#  lock / unlock only need Manage Roles
# ──────────────────────────────────────────────────

class _Role:
    id = 555


class _Guild:
    default_role = _Role()


class _Channel:
    id = 777

    def __init__(self):
        self.calls = []
        self.overwrite = None

    def overwrites_for(self, role):
        assert role is _Guild.default_role
        return self.overwrite

    async def set_permissions(self, target, *, overwrite, reason=None):
        self.calls.append(("set_permissions", target.id, overwrite.send_messages, reason))

    async def edit(self, **kwargs):
        raise AssertionError("lock must not edit the channel (that needs Manage Channels)")


def test_lock_writes_the_overwrite_through_the_permission_endpoint():
    from cogs.moderation._channels import set_everyone_send_messages

    channel = _Channel()
    channel.overwrite = discord.PermissionOverwrite(send_messages=True, manage_messages=True)

    asyncio.run(set_everyone_send_messages(
        channel, _Guild(), False, reason="Locked by tester"))

    assert channel.calls == [("set_permissions", 555, False, "Locked by tester")]
    # Everything else the overwrite already granted is preserved.
    assert channel.overwrite.manage_messages is True


def test_unlock_restores_inheritance_instead_of_denying():
    from cogs.moderation._channels import set_everyone_send_messages

    channel = _Channel()
    channel.overwrite = discord.PermissionOverwrite(send_messages=False)

    asyncio.run(set_everyone_send_messages(
        channel, _Guild(), None, reason="Unlocked by tester"))

    assert channel.calls == [("set_permissions", 555, None, "Unlocked by tester")]


def test_the_lock_commands_never_edit_the_channel():
    source = (ROOT / "src" / "cogs" / "moderation" / "_channels.py").read_text(encoding="utf-8")
    lock_body = source.split("async def lock(", 1)[1].split("async def unlock(", 1)[0]
    unlock_body = source.split("async def unlock(", 1)[1]

    assert ".edit(" not in lock_body
    assert ".edit(" not in unlock_body
    assert "set_everyone_send_messages(" in lock_body
    assert "set_everyone_send_messages(" in unlock_body


def _declared_permissions(command):
    """Permission names a command declares, read the way the command registry is."""
    declared = set()
    for check in getattr(command, "checks", ()) or ():
        for cell in getattr(check, "__closure__", ()) or ():
            try:
                value = cell.cell_contents
            except ValueError:
                continue
            if isinstance(value, dict):
                declared.update(name for name, enabled in value.items() if enabled)
    return declared


def test_lock_and_unlock_declare_manage_roles_not_manage_channels():
    """A rejected review, in code: the requirement has to match the endpoint."""
    from cogs.moderation._channels import ChannelsMixin

    for name in ("lock", "unlock"):
        declared = _declared_permissions(getattr(ChannelsMixin, name))
        assert declared == {"manage_roles"}, (
            f"{name} declares {sorted(declared) or 'no permissions'}; writing the "
            "@everyone overwrite only needs Manage Roles, and the published "
            "command registry reports this requirement to reviewers"
        )


# ──────────────────────────────────────────────────
#  Channel-posted panels are guarded
# ──────────────────────────────────────────────────

GUARDED_VIEWS = [
    ("cogs.automod.views", "_SettingsPanelView"),
    ("cogs.moderation._badwords_panel", "_BadWordsPanelView"),
    ("cogs.admin.triggers", "TriggersView"),
    ("cogs.leveling.panel", "_LevelPanelView"),
    ("cogs.giveaway.views", "_GiveawaySetupView"),
    ("cogs.tickets.cog", "TicketSetupView"),
    ("cogs.social.polls", "PollSetupView"),
    ("cogs.setup.cog", "SetupWizard"),
    ("cogs.onboarding.views", "OnboardingSetupView"),
    ("cogs.onboarding.views", "AutoroleSetupView"),
    ("cogs.onboarding.views", "CaptchaSetupView"),
    ("cogs.onboarding.views", "RoleMenuManagerView"),
    ("cogs.onboarding.views", "RoleMenuEditView"),
    ("cogs.onboarding.views", "RoleMenuWizardTypeView"),
    ("cogs.onboarding.views", "RoleMenuWizardAddRolesView"),
]

#: Panels members are supposed to press: a gate here would break the feature.
PUBLIC_VIEWS = [
    ("cogs.onboarding.views", "RoleMenuView"),
    ("cogs.onboarding.views", "CaptchaPanelView"),
    ("cogs.onboarding.views", "RulesAcknowledgeView"),
    ("cogs.tickets.views", "TicketPanelView"),
    ("cogs.giveaway.views", "_GiveawayJoinBtn"),
]


def test_settings_panels_define_a_view_level_permission_check():
    missing = []
    for module_name, class_name in GUARDED_VIEWS:
        module = importlib.import_module(module_name)
        view = getattr(module, class_name)
        if not hasattr(view, "interaction_check"):
            missing.append(f"{module_name}.{class_name}")
    assert not missing, "channel-posted panels without a permission gate: " + ", ".join(missing)


def test_member_facing_panels_stay_open():
    for module_name, class_name in PUBLIC_VIEWS:
        module = importlib.import_module(module_name)
        view = getattr(module, class_name)
        assert "interaction_check" not in view.__dict__, (
            f"{module_name}.{class_name} is member-facing and must not be gated"
        )


def test_every_guarded_check_actually_counts_manage_server():
    """A gate that delegates still has to reach a Manage Server comparison."""
    for module_name, class_name in GUARDED_VIEWS:
        module = importlib.import_module(module_name)
        source = inspect.getsource(getattr(module, class_name).interaction_check)
        helpers = [name for name in ("_may_manage", "manage_gate") if f"{name}(" in source]
        if helpers:
            source = "\n".join(inspect.getsource(getattr(module, name)) for name in helpers)
        assert "manage_guild" in source, (
            f"{module_name}.{class_name}.interaction_check does not check Manage Server"
        )
