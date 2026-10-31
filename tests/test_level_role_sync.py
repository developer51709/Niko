"""Regression tests for reward-role reconciliation.

Adding, moving or removing a leveling reward used to change only the mapping:
members who already passed the level never received the role, members who had
earned a reward that was moved out of reach kept it, and a deleted reward left
the role on every member who had it.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cogs.leveling import cog as leveling_cog
from utils.ratelimit import mass_role_limiter


# The reward sync shares /massrole's per-guild bucket rather than opening a
# second, faster path to Discord's role endpoint.
assert leveling_cog.mass_role_limiter is mass_role_limiter


class FakeRole:
    def __init__(self, role_id):
        self.id = role_id


class FakeMember:
    def __init__(self, member_id, role_ids=(), bot=False):
        self.id = member_id
        self.bot = bot
        self.roles = [FakeRole(role_id) for role_id in role_ids]
        self.added = []
        self.removed = []

    async def add_roles(self, *roles, reason=None):
        for role in roles:
            self.added.append(role.id)
            self.roles.append(role)

    async def remove_roles(self, *roles, reason=None):
        dropped = {role.id for role in roles}
        for role_id in dropped:
            self.removed.append(role_id)
        self.roles = [role for role in self.roles if role.id not in dropped]


class FakeGuild:
    def __init__(self, members, role_ids):
        self.id = 42
        self.members = list(members)
        self._roles = {role_id: FakeRole(role_id) for role_id in role_ids}

    def get_role(self, role_id):
        return self._roles.get(int(role_id))


class FakePool:
    def __init__(self, levels):
        self.levels = dict(levels)

    async def fetch(self, _query, guild_id):
        assert int(guild_id) == 42
        return [
            {"user_id": user_id, "level": level}
            for user_id, level in self.levels.items()
        ]


class CountingLimiter:
    """Stand-in that records every bucket the sync waits on."""

    def __init__(self):
        self.called = []

    async def acquire(self, key):
        self.called.append(key)


def make_cog(levels):
    cog = object.__new__(leveling_cog.Leveling)
    cog.bot = SimpleNamespace(cxn=FakePool(levels))
    return cog


def sync(cog, guild, level_roles, previous_roles=None, members=None):
    return asyncio.run(cog._sync_level_roles(
        guild, level_roles, previous_roles, members))


class LevelRoleSyncTests(unittest.TestCase):
    def setUp(self):
        self.limiter = CountingLimiter()
        patcher = mock.patch.object(leveling_cog, "mass_role_limiter", self.limiter)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_adding_a_reward_grants_it_to_members_who_already_reached_it(self):
        eligible = FakeMember(1)
        too_low = FakeMember(2)
        guild = FakeGuild([eligible, too_low], [900])
        cog = make_cog({1: 9, 2: 4})

        updated, failed = sync(cog, guild, {"5": 900})

        self.assertEqual((updated, failed), (1, 0))
        self.assertEqual(eligible.added, [900])
        self.assertEqual(too_low.added, [])
        self.assertEqual(self.limiter.called, [42])

    def test_moving_a_reward_to_a_higher_level_takes_it_back(self):
        reached = FakeMember(1, role_ids=[900])
        still_short = FakeMember(2, role_ids=[900])
        guild = FakeGuild([reached, still_short], [900])
        cog = make_cog({1: 12, 2: 7})

        # The reward used to sit at level 5 and has been moved to level 10.
        updated, _ = sync(cog, guild, {"10": 900}, {"5": 900})

        self.assertEqual(updated, 1)
        self.assertEqual(reached.removed, [])
        self.assertEqual(still_short.removed, [900])

    def test_moving_a_reward_to_another_role_replaces_it(self):
        member = FakeMember(1, role_ids=[900])
        guild = FakeGuild([member], [900, 901])
        cog = make_cog({1: 6})

        sync(cog, guild, {"5": 901}, {"5": 900})

        self.assertEqual(member.added, [901])
        self.assertEqual(member.removed, [900])

    def test_removing_a_reward_strips_the_role_from_every_holder(self):
        holder = FakeMember(1, role_ids=[900])
        other = FakeMember(2)
        guild = FakeGuild([holder, other], [900])
        cog = make_cog({1: 30})

        updated, _ = sync(cog, guild, {}, {"5": 900})

        self.assertEqual(updated, 1)
        self.assertEqual(holder.removed, [900])
        self.assertEqual(other.removed, [])

    def test_members_keep_roles_from_rewards_they_still_pass(self):
        member = FakeMember(1, role_ids=[900])
        guild = FakeGuild([member], [900, 901])
        cog = make_cog({1: 12})

        updated, _ = sync(cog, guild, {"5": 900, "10": 901})

        self.assertEqual(updated, 1)
        self.assertEqual(member.added, [901])
        self.assertEqual(member.removed, [])

    def test_bots_and_unreachable_roles_are_left_alone(self):
        bot = FakeMember(1, bot=True)
        guild = FakeGuild([bot], [])
        cog = make_cog({1: 99})

        updated, failed = sync(cog, guild, {"5": 900})

        self.assertEqual((updated, failed), (0, 0))
        self.assertEqual(bot.added, [])

    def test_a_missing_role_does_not_abort_the_rest_of_the_sync(self):
        first = FakeMember(1)
        second = FakeMember(2)
        guild = FakeGuild([first, second], [901])
        cog = make_cog({1: 12, 2: 12})

        # Role 900 is still configured but no longer exists in the guild, so
        # only the surviving reward is granted and nothing raises.
        updated, failed = sync(cog, guild, {"5": 900, "10": 901})

        self.assertEqual((updated, failed), (2, 0))
        self.assertEqual(first.added, [901])
        self.assertEqual(second.added, [901])


if __name__ == "__main__":
    unittest.main()
