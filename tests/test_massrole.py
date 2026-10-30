"""Focused regression checks for the interactive massrole command."""

from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.moderation._members import (
    MASSROLE_ACTIONS,
    MASSROLE_TARGETS,
    _massrole_action,
    _massrole_estimate_seconds,
    _massrole_member_matches,
    _massrole_target,
)
from cogs.moderation.commands import Moderation
from utils.locales import missing_translations
from utils.ratelimit import mass_role_limiter


# The labels themselves live in locales/massrole so they follow the guild's
# language; these tuples only name the values stored in the panel.
assert tuple(MASSROLE_ACTIONS) == ("add", "remove")
assert tuple(MASSROLE_TARGETS) == ("humans", "bots", "all")
assert _massrole_action(None, "add") == "Add"
assert _massrole_action(SimpleNamespace(preferred_locale="de"), "remove") == "Entfernen"
assert _massrole_target(None, "all") == "All"
assert _massrole_target(SimpleNamespace(preferred_locale="es"), "humans") == "Humanos"
assert not missing_translations("cogs.moderation")["de"]
assert not missing_translations("cogs.moderation")["es"]
assert _massrole_member_matches(SimpleNamespace(bot=False), "humans")
assert not _massrole_member_matches(SimpleNamespace(bot=True), "humans")
assert _massrole_member_matches(SimpleNamespace(bot=True), "bots")
assert _massrole_member_matches(SimpleNamespace(bot=False), "all")
assert _massrole_estimate_seconds(0) == 0
assert _massrole_estimate_seconds(1) >= 1
assert mass_role_limiter.rate == 2
assert mass_role_limiter.per == 1.0

# The mixin command is composed into the live moderation cog and must remain
# a hybrid command so both prefix and slash invocation open the same panel.
assert getattr(Moderation.massrole, "with_app_command", False)

print("massrole regression checks passed")
