"""The warning panel's API footer and the source bookkeeping behind it.

A warning written by a reviewed application has to say so, and the case must
keep that source when a moderator edits it: the panel is what staff act on days
later, when nobody remembers which bot wrote what.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import discord

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.moderation import utils as mod_utils  # noqa: E402

WARN_SOURCE = "https://niko.sryze.cc/docs/verified-applications"


class FakePool:
    """Enough of the database adapter for the warning methods."""

    db_type = "sqlite"

    def __init__(self, rows=()):
        self.rows = list(rows)
        self.calls: list[tuple[str, tuple]] = []

    async def execute(self, sql, *args):
        self.calls.append((sql, args))

    async def fetchrow(self, sql, *args):
        for row in self.rows:
            if row["id"] == args[0]:
                return row
        return None

    async def fetch(self, sql, *args):
        return list(self.rows)

    async def fetchval(self, sql, *args):
        return len(self.rows)


def _utils(monkeypatch, pool) -> mod_utils.ModerationUtils:
    monkeypatch.setattr(mod_utils, "_pool", lambda: pool)
    monkeypatch.setattr(mod_utils, "_publish_warn_event", lambda *args, **kwargs: None)
    # __init__ loads the legacy config files; these tests only touch warns.
    return object.__new__(mod_utils.ModerationUtils)


def test_an_api_warning_records_the_application_bot(monkeypatch):
    pool = FakePool()
    utils = _utils(monkeypatch, pool)

    record = asyncio.run(utils.add_warn(10, 20, 30, "spam", source_bot_id=777))

    assert record["source_bot_id"] == 777
    insert = [call for call in pool.calls if "INSERT INTO warns" in call[0]][0]
    assert "source_bot_id" in insert[0]
    assert insert[1][-1] == 777


def test_a_moderator_warning_has_no_source(monkeypatch):
    pool = FakePool()
    utils = _utils(monkeypatch, pool)

    record = asyncio.run(utils.add_warn(10, 20, 30, "spam"))

    assert record["source_bot_id"] is None


def test_get_warnings_exposes_the_case_id_and_source(monkeypatch):
    pool = FakePool([{
        "id": 5, "moderator_id": 30, "reason": "spam",
        "created_at": "2026-11-05T00:00:00+00:00", "source_bot_id": 777,
    }])
    utils = _utils(monkeypatch, pool)

    warns = asyncio.run(utils.get_warnings(10, 20))

    assert warns[0]["id"] == 5
    assert warns[0]["source_bot_id"] == 777


def test_editing_a_warning_keeps_its_id_and_source(monkeypatch):
    pool = FakePool([{
        "id": 5, "guild_id": "10", "user_id": "20", "moderator_id": 30,
        "reason": "old", "created_at": "2026-11-05T00:00:00+00:00",
        "source_bot_id": 777,
    }])
    utils = _utils(monkeypatch, pool)

    updated = asyncio.run(utils.update_warning(10, 5, "  corrected reason  "))

    assert updated["id"] == 5
    assert updated["source_bot_id"] == 777
    assert updated["reason"] == "corrected reason"
    assert any("UPDATE warns SET reason" in sql for sql, _ in pool.calls)


def test_deleting_one_case_does_not_touch_the_rest(monkeypatch):
    pool = FakePool([{
        "id": 5, "guild_id": "10", "user_id": "20", "moderator_id": 30,
        "reason": "spam", "created_at": "2026-11-05T00:00:00+00:00",
        "source_bot_id": None,
    }])
    utils = _utils(monkeypatch, pool)

    removed = asyncio.run(utils.delete_warning(10, 5))

    assert removed["id"] == 5
    deletes = [call for call in pool.calls if call[0].startswith("DELETE FROM warns")]
    assert deletes and "id = $1 AND guild_id = $2" in deletes[0][0]


def test_the_panel_pages_four_warnings_at_a_time():
    from cogs.moderation._warnings import PAGE_SIZE, WarningsView

    assert PAGE_SIZE == 4
    panel = object.__new__(WarningsView)
    panel.warnings = [{"id": index} for index in range(9)]

    panel.current_page = 1
    assert panel.page_count() == 3
    assert [warn["id"] for warn in panel.page_warnings()] == [4, 5, 6, 7]

    panel.current_page = 2
    assert [warn["id"] for warn in panel.page_warnings()] == [8]


def test_timeout_disables_every_button_and_says_so():
    from cogs.moderation._warnings import WarningsView

    member = SimpleNamespace(
        id=20, mention="<@20>",
        display_avatar=SimpleNamespace(url="https://cdn.example/avatar.png"),
    )
    member.__str__ = lambda self: "someone#0001"
    guild = SimpleNamespace(id=1, get_member=lambda _id: None)
    ctx = SimpleNamespace(guild=SimpleNamespace(id=1, preferred_locale="en"))
    warns = [{
        "id": 5, "mod": 30, "reason": "spam",
        "time": "2026-11-05T00:00:00+00:00", "source_bot_id": None,
    } for _ in range(5)]
    panel = WarningsView(
        utils=None, guild=guild, member=member, ctx=ctx,
        warnings=warns, cog=None, timeout=0.01,
    )

    edits = []

    async def edit(**kwargs):
        edits.append(kwargs)

    panel.message = SimpleNamespace(edit=edit)

    asyncio.run(panel.on_timeout())

    assert panel.timed_out
    buttons = [item for item in panel.walk_children() if isinstance(item, discord.ui.Button)]
    assert buttons
    assert all(button.disabled for button in buttons)
    texts = [item.content for item in panel.walk_children() if isinstance(item, discord.ui.TextDisplay)]
    assert any("timed out" in text for text in texts)
    assert edits and edits[0]["view"] is panel


def _permissions(**grants):
    values = {"moderate_members": False, "manage_messages": False}
    values.update(grants)
    return SimpleNamespace(**values)


def test_viewing_accepts_either_permission():
    from cogs.moderation._warnings import can_view_warnings

    assert can_view_warnings(SimpleNamespace(permissions=_permissions(moderate_members=True)))
    assert can_view_warnings(SimpleNamespace(permissions=_permissions(manage_messages=True)))
    assert not can_view_warnings(SimpleNamespace(permissions=_permissions()))


def test_editing_and_removing_need_moderate_members():
    """A removal is as destructive as /clearwarnings, so Manage Messages is not
    enough for the panel's buttons even though it is enough to read the list."""
    from cogs.moderation._warnings import can_manage_warnings

    assert can_manage_warnings(SimpleNamespace(permissions=_permissions(moderate_members=True)))
    assert not can_manage_warnings(SimpleNamespace(permissions=_permissions(manage_messages=True)))
    assert not can_manage_warnings(SimpleNamespace(permissions=_permissions()))


def _panel_text(source_bot_id):
    from cogs.moderation._warnings import warning_text

    guild = SimpleNamespace(get_member=lambda _id: None)
    ctx = SimpleNamespace(guild=SimpleNamespace(id=1, preferred_locale="en"))
    return warning_text(
        guild,
        {
            "id": 5, "mod": 30, "reason": "spam",
            "time": "2026-11-05T00:00:00+00:00",
            "source_bot_id": source_bot_id,
        },
        index=2,
        ctx=ctx,
    )


def test_the_panel_footer_names_the_application_and_links_the_explainer():
    text = _panel_text(777)

    assert "Case #2" in text
    assert "<@777>" in text
    assert "Added via" in text
    assert WARN_SOURCE in text
    # The notepad is the bot's own emoji markup, not a Unicode fallback.
    assert "<:notepad:" in text


def test_a_moderator_warning_has_no_footer():
    assert "Added via" not in _panel_text(None)


def test_a_long_reason_is_shortened_on_the_panel_but_keeps_its_footer():
    from cogs.moderation._warnings import REASON_CHARS, warning_text

    guild = SimpleNamespace(get_member=lambda _id: None)
    ctx = SimpleNamespace(guild=SimpleNamespace(id=1, preferred_locale="en"))
    text = warning_text(
        guild,
        {
            "id": 5, "mod": 30, "reason": "x" * 1000,
            "time": "2026-11-05T00:00:00+00:00", "source_bot_id": 777,
        },
        index=1,
        ctx=ctx,
        reason_limit=REASON_CHARS,
    )

    assert "x" * (REASON_CHARS + 1) not in text
    assert "…" in text
    # Clipping the reason by itself keeps the markup after it intact.
    assert text.endswith(f"({WARN_SOURCE})")
