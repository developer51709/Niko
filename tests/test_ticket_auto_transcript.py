"""Automatic ticket transcripts.

Closing or deleting a ticket can save its transcript when the guild turns the
setting on. The transcript is stored once: a ticket that is reopened and closed
again rewrites the same row with the newer messages rather than creating a
second copy. A failing transcript must never block the close itself.
"""

from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.tickets import transcripts as transcript_utils  # noqa: E402
from utils.tickets.auto import auto_capture_transcript  # noqa: E402
from utils.tickets.config import TicketConfig  # noqa: E402
from utils.tickets.utils import _config_to_doc, _row_to_config  # noqa: E402
from webapp import app  # noqa: E402
from webapp.routes import dashboard_routes  # noqa: E402


class _Author:
    id = 7

    def __str__(self) -> str:
        return "opener#0001"


class _Message:
    created_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    author = _Author()
    content = "hello"
    attachments = ()
    embeds = ()
    components = ()
    stickers = ()


class _Channel:
    id = 99
    name = "ticket-0099"

    def history(self, limit=2000, oldest_first=True):
        async def _iterate():
            yield _Message()

        return _iterate()


class _Cxn:
    """The bits of the bot's database pool the transcript helpers touch."""

    def __init__(self, existing: str | None = None, fail: bool = False):
        self.existing = existing
        self.fail = fail
        self.executed: list[tuple[str, tuple]] = []

    async def execute(self, sql, *args):
        if self.fail:
            raise RuntimeError("database unavailable")
        self.executed.append((sql, args))

    async def fetchval(self, sql, *args):
        return self.existing

    @property
    def sql(self) -> list[str]:
        return [statement for statement, _ in self.executed]


def _ticket(**overrides) -> dict:
    values = {"channel_id": 99, "opener_id": 7, "category": "Billing", "claimed_by": None}
    values.update(overrides)
    return values


def _cfg(**overrides) -> TicketConfig:
    return TicketConfig(guild_id=111, **overrides)


def test_the_setting_defaults_to_off_and_round_trips_through_storage():
    assert _cfg().auto_transcript is False
    assert _row_to_config({"guild_id": 111}).auto_transcript is False
    assert _row_to_config({"guild_id": 111, "auto_transcript": 1}).auto_transcript is True
    assert _config_to_doc(_cfg(auto_transcript=True))["auto_transcript"] is True


def test_the_config_save_writes_the_setting(monkeypatch):
    import database
    from utils.tickets import utils as ticket_utils

    class _Pool:
        def __init__(self):
            self.calls = []

        async def execute(self, sql, *args):
            self.calls.append((sql, args))

    pool = _Pool()
    monkeypatch.setattr(database, "_shared_pool", pool)

    assert asyncio.run(
        ticket_utils._save_config_to_db(111, _cfg(auto_transcript=True))
    ) is True

    sql, args = pool.calls[0]
    assert "auto_transcript" in sql
    # 11 inserted values plus the 10 values of the update clause.
    assert len(args) == 21
    assert args[10] is True and args[20] is True


def test_the_first_close_stores_a_transcript_and_reports_its_id():
    cxn = _Cxn()
    ticket = _ticket()

    transcript_id = asyncio.run(
        transcript_utils.capture_ticket_transcript(
            cxn, guild_id=111, channel=_Channel(), ticket=ticket
        )
    )

    assert transcript_id
    assert any(statement.startswith("INSERT INTO transcripts") for statement in cxn.sql)
    insert = next(args for statement, args in cxn.executed if statement.startswith("INSERT"))
    assert insert[1] == 111
    assert insert[2] == 99
    assert insert[3] == "ticket-0099"
    assert insert[4] == 7
    assert insert[5] == "Billing"
    assert insert[7] == 1


def test_a_reopened_ticket_updates_the_same_transcript_instead_of_copying_it():
    cxn = _Cxn(existing="abc123")
    ticket = _ticket(transcript_id="abc123")

    transcript_id = asyncio.run(
        transcript_utils.capture_ticket_transcript(
            cxn, guild_id=111, channel=_Channel(), ticket=ticket
        )
    )

    assert transcript_id == "abc123"
    assert cxn.executed and all(statement.startswith("UPDATE transcripts") for statement in cxn.sql)
    update = cxn.executed[0][1]
    assert update[0] == "abc123"
    assert update[4] == 1


def test_a_stale_transcript_id_falls_back_to_a_new_transcript():
    cxn = _Cxn(existing=None)
    ticket = _ticket(transcript_id="deleted")

    transcript_id = asyncio.run(
        transcript_utils.capture_ticket_transcript(
            cxn, guild_id=111, channel=_Channel(), ticket=ticket
        )
    )

    assert transcript_id != "deleted"
    assert any(statement.startswith("INSERT INTO transcripts") for statement in cxn.sql)


def test_the_auto_helper_does_nothing_when_the_setting_is_off():
    cxn = _Cxn()
    ticket = _ticket()

    asyncio.run(
        auto_capture_transcript(
            SimpleNamespace(cxn=cxn), 111, _Channel(), ticket, _cfg()
        )
    )

    assert cxn.executed == []
    assert "transcript_id" not in ticket


def test_the_auto_helper_records_the_transcript_on_the_ticket():
    cxn = _Cxn()
    ticket = _ticket()

    asyncio.run(
        auto_capture_transcript(
            SimpleNamespace(cxn=cxn), 111, _Channel(), ticket, _cfg(auto_transcript=True)
        )
    )

    assert ticket["transcript_id"]
    assert any(statement.startswith("INSERT INTO transcripts") for statement in cxn.sql)


def test_a_failed_transcript_never_escapes_the_close_path():
    ticket = _ticket()

    asyncio.run(
        auto_capture_transcript(
            SimpleNamespace(cxn=_Cxn(fail=True)),
            111,
            _Channel(),
            ticket,
            _cfg(auto_transcript=True),
        )
    )

    assert "transcript_id" not in ticket


def test_the_dashboard_saves_and_returns_the_toggle():
    patches = [
        mock.patch.object(dashboard_routes, "_guild_resource_ids", lambda guild_id: ({"5"}, {"9"})),
        mock.patch.object(dashboard_routes, "_get_runtime_server_config", lambda guild_id: {}),
        mock.patch.object(
            dashboard_routes,
            "_load_blacklist_manager",
            lambda: mock.Mock(get_guild_entry=lambda guild_id: None),
        ),
        mock.patch.object(dashboard_routes, "run_on_bot_loop", _close_awaitable),
    ]
    for patch in patches:
        patch.start()
    from utils.tickets import utils as ticket_utils

    previous = dict(ticket_utils._ticket_configs)
    ticket_utils._ticket_configs.clear()
    try:
        client = app.test_client()
        with client.session_transaction() as session:
            session["user"] = {"id": "42", "username": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "csrf"
            session["managed_guild_ids"] = ["111"]
            session["managed_guilds_at"] = time.time()

        response = client.post(
            "/api/guild/111/config/server",
            json={"tickets": {"auto_transcript": True}},
            headers={"X-CSRF-Token": "csrf"},
        )
        assert response.status_code == 200
        assert ticket_utils.get_ticket_config(111).auto_transcript is True

        read_back = client.get("/api/guild/111/tickets")
        assert read_back.status_code == 200
        assert read_back.get_json()["config"]["auto_transcript"] is True

        rejected = client.post(
            "/api/guild/111/config/server",
            json={"tickets": {"auto_transcript": "yes"}},
            headers={"X-CSRF-Token": "csrf"},
        )
        assert rejected.status_code == 400
    finally:
        ticket_utils._ticket_configs.clear()
        ticket_utils._ticket_configs.update(previous)
        for patch in patches:
            patch.stop()


def _close_awaitable(awaitable, timeout=8):
    if hasattr(awaitable, "close"):
        awaitable.close()
    return None
