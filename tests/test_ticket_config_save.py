"""Ticket config writes from a synchronous caller stay on the bot's loop.

The shared database pool's HTTP session belongs to the bot loop, so writing it
from a fresh loop in Flask's thread fails inside aiohttp with "Timeout context
manager should be used inside a task". The sync path hands the write over.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.tickets import utils as ticket_utils  # noqa: E402
from utils.tickets.config import TicketConfig  # noqa: E402


def test_update_ticket_config_without_a_loop_schedules_the_write_on_the_bot_loop(monkeypatch):
    import webapp.runtime as runtime

    scheduled = []
    monkeypatch.setattr(runtime, "schedule_on_bot_loop", scheduled.append)

    cfg = TicketConfig(guild_id=321)
    ticket_utils.update_ticket_config(321, cfg)

    assert ticket_utils.get_ticket_config(321) is cfg
    assert len(scheduled) == 1
    scheduled[0].close()


def test_update_ticket_config_keeps_the_cache_when_no_bot_loop_exists(monkeypatch):
    import webapp.runtime as runtime

    def no_bot(_coro):
        raise RuntimeError("The Discord bot is not running.")

    monkeypatch.setattr(runtime, "schedule_on_bot_loop", no_bot)

    cfg = TicketConfig(guild_id=654)
    ticket_utils.update_ticket_config(654, cfg)

    assert ticket_utils.get_ticket_config(654) is cfg
