"""``/leveling reset``: wipe a server's levels and take the reward roles back.

The wipe is immediate and unrecoverable, so it sits behind a confirmation that
only the invoker can answer. The role removal is queued like every other reward
edit — the command replies straight away — and still waits on
``mass_role_limiter`` per member, so a large server never exceeds the guild's
role-edit budget.
"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from discord.ext import commands

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import discord  # noqa: E402

from cogs.leveling import cog as leveling_cog  # noqa: E402

GUILD_ID = 42
#: The reward mapping the guild has configured: level 5 → role 900, level 10 → 901.
REWARDS = {"5": 900, "10": 901}
#: A role members hold that no reward names, so it must survive the reset.
UNRELATED_ROLE = 555


class FakeRole:
    def __init__(self, role_id):
        self.id = role_id


class FakeMember:
    def __init__(self, member_id, role_ids=(), fail_removals=False):
        self.id = member_id
        self.bot = False
        self.fail_removals = fail_removals
        self.roles = [FakeRole(role_id) for role_id in role_ids]
        self.added = []
        self.removed = []

    async def add_roles(self, *roles, reason=None):
        for role in roles:
            self.added.append(role.id)
            self.roles.append(role)

    async def remove_roles(self, *roles, reason=None):
        if self.fail_removals:
            raise RuntimeError("Missing Permissions")
        dropped = {role.id for role in roles}
        self.removed.extend(sorted(dropped))
        self.roles = [role for role in self.roles if role.id not in dropped]


class FakeGuild:
    id = GUILD_ID
    name = "Test Guild"
    preferred_locale = "en"

    def __init__(self, members):
        self.members = list(members)
        self._roles = {
            role_id: FakeRole(role_id)
            for role_id in (900, 901, UNRELATED_ROLE)
        }

    def get_role(self, role_id):
        return self._roles.get(int(role_id))


class FakePool:
    """Just enough of the database for the reset and the reward sync."""

    def __init__(self, levels):
        self.rows = dict(levels)
        self.executed = []

    async def fetchval(self, query, *args):
        assert "COUNT(*)" in query
        return len(self.rows)

    async def fetch(self, _query, _guild_id):
        return [
            {"user_id": user_id, "level": level}
            for user_id, level in self.rows.items()
        ]

    async def execute(self, query, *args):
        self.executed.append((query, args))
        if query.startswith("DELETE FROM levels"):
            self.rows.clear()


class CountingLimiter:
    """Stand-in for the shared bucket that records every guild it waits on."""

    def __init__(self):
        self.keys = []

    async def acquire(self, key):
        self.keys.append(key)


class _Status:
    """The message the prompt and the progress lines are edited into."""

    def __init__(self):
        self.views = []

    async def edit(self, view=None, **kwargs):
        self.views.append(view)


class _Ctx:
    def __init__(self, guild):
        self.guild = guild
        self.author = SimpleNamespace(id=7)
        self.interaction = None
        self.prompts = []
        self.status = None

    async def send(self, *, view=None, **kwargs):
        self.prompts.append(view)
        self.status = _Status()
        return self.status


class _Answer:
    """A confirmation prompt that has already been answered."""

    def __init__(self, answer, **kwargs):
        self.answer = answer
        self.kwargs = kwargs

    async def wait_for_response(self):
        return self.answer


def _cog(pool):
    cog = object.__new__(leveling_cog.Leveling)
    cog.bot = SimpleNamespace(cxn=pool)

    async def guild_cfg(_guild_id):
        return {"xp_enabled": True, "level_roles": dict(REWARDS)}

    cog._guild_cfg = guild_cfg
    return cog


def _texts(view) -> list[str]:
    out = []
    for child in getattr(view, "children", []) or []:
        content = getattr(child, "content", None)
        if isinstance(content, str):
            out.append(content)
        out.extend(_texts(child))
    return out


def _run(monkeypatch, *, confirm=True, failing_ids=()):
    """Run the command once and return everything a test can assert on."""
    member = FakeMember(
        11, role_ids=[900, 901, UNRELATED_ROLE], fail_removals=11 in failing_ids)
    other = FakeMember(12, role_ids=[900], fail_removals=12 in failing_ids)
    guild = FakeGuild([member, other])
    pool = FakePool({11: 12, 12: 6})
    limiter = CountingLimiter()
    cog = _cog(pool)
    ctx = _Ctx(guild)

    # The sync is queued, never awaited, so the command can answer at once.
    queued = []
    real_create_task = asyncio.create_task

    def record(coro, **kwargs):
        task = real_create_task(coro, **kwargs)
        queued.append(task)
        return task

    monkeypatch.setattr(leveling_cog, "asyncio", SimpleNamespace(create_task=record))
    monkeypatch.setattr(leveling_cog, "mass_role_limiter", limiter)
    monkeypatch.setattr(
        leveling_cog, "_LevelResetConfirmView",
        lambda **kwargs: _Answer(confirm, **kwargs),
    )

    async def scenario():
        await leveling_cog.Leveling.__dict__["leveling_reset"].callback(cog, ctx)
        if queued:
            # The done message reports the wipe, so the role removal is still
            # in flight at this point — finish it before asserting on roles.
            await asyncio.gather(*queued)

    asyncio.run(scenario())
    return SimpleNamespace(
        member=member, other=other, pool=pool, limiter=limiter,
        ctx=ctx, queued=queued,
    )


def test_the_wipe_deletes_every_level_row_for_the_guild(monkeypatch):
    result = _run(monkeypatch)

    deletes = [
        (query, args) for query, args in result.pool.executed
        if query.startswith("DELETE FROM levels")
    ]
    assert deletes, "the reset never deleted the level rows"
    assert deletes[0][1] == (GUILD_ID,)
    assert result.pool.rows == {}

    # The message is edited before the removal starts, then again with counts.
    progress = "\n".join(_texts(result.ctx.status.views[-2]))
    assert "**2** member(s)" in progress
    assert "Removing their reward roles now" in progress

    report = "\n".join(_texts(result.ctx.status.views[-1]))
    assert "**2** member(s)" in report
    assert "Removed reward roles from **2** member(s)" in report
    assert "could not be updated" not in report


def test_reward_roles_come_off_through_the_shared_rate_limiter(monkeypatch):
    result = _run(monkeypatch)

    # Queued rather than awaited: the command itself must not wait on Discord.
    assert result.queued, "the role removal was never queued"
    assert result.member.removed == [900, 901]
    assert result.other.removed == [900]
    # Only reward roles go; anything else the member holds stays.
    assert UNRELATED_ROLE in [role.id for role in result.member.roles]
    # One wait per member update, on the same per-guild bucket /massrole uses.
    assert result.limiter.keys == [GUILD_ID, GUILD_ID]


def test_failed_member_updates_are_reported(monkeypatch):
    result = _run(monkeypatch, failing_ids=(12,))

    report = "\n".join(_texts(result.ctx.status.views[-1]))
    assert "Removed reward roles from **1** member(s)" in report
    assert "**1** member(s) could not be updated" in report
    # The member that failed keeps their role so a later retry can still take it.
    assert result.member.removed == [900, 901]
    assert result.other.removed == []


def test_only_administrators_can_run_it():
    command = leveling_cog.Leveling.__dict__["leveling_reset"]
    assert command.name == "reset"
    # Hidden from non-admins in the slash picker …
    assert command.app_command.default_permissions.administrator is True

    # … and the runtime check refuses a prefix invocation too.
    check = command.checks[0]
    assert check(SimpleNamespace(permissions=discord.Permissions(administrator=True))) is True
    with pytest.raises(commands.MissingPermissions):
        check(SimpleNamespace(permissions=discord.Permissions.none()))


def test_cancelling_leaves_the_data_and_the_roles_alone(monkeypatch):
    result = _run(monkeypatch, confirm=False)

    assert not [
        query for query, _ in result.pool.executed if query.startswith("DELETE")
    ]
    assert result.pool.rows == {11: 12, 12: 6}
    assert result.queued == []
    assert result.member.removed == []
    assert result.other.removed == []


def test_the_prompt_warns_and_its_cancel_button_changes_nothing():
    guild = SimpleNamespace(id=GUILD_ID, name="Test Guild", preferred_locale="en")
    locale = SimpleNamespace(guild=guild, author=SimpleNamespace(id=7))
    view = leveling_cog._LevelResetConfirmView(
        invoker_id=7, locale=locale, members=3, roles=2)

    body = "\n".join(_texts(view))
    assert "This cannot be undone." in body
    assert "**3** member record(s)" in body

    class Response:
        def __init__(self):
            self.edits = []

        async def edit_message(self, view=None, **kwargs):
            self.edits.append(view)

    response = Response()
    interaction = SimpleNamespace(
        user=SimpleNamespace(id=7), guild=guild, response=response)

    asyncio.run(view._on_cancel(interaction))

    assert view.confirmed is False
    assert view._confirm.disabled and view._cancel.disabled
    assert response.edits, "cancelling did not replace the prompt"
    assert "cancelled" in "\n".join(_texts(response.edits[0]))
