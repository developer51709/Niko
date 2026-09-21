"""Focused regression checks for the interactive massrole command."""

from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.moderation._members import (
    MASSROLE_ACTIONS,
    MASSROLE_TARGETS,
    _massrole_estimate_seconds,
    _massrole_member_matches,
)
from cogs.moderation.commands import Moderation
from utils.ratelimit import mass_role_limiter


assert MASSROLE_ACTIONS == {"add": "Add", "remove": "Remove"}
assert MASSROLE_TARGETS == {
    "humans": "Humans",
    "bots": "Bots",
    "all": "All",
}
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
