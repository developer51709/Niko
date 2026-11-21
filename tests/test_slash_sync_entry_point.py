"""The bulk sync has to keep Discord's Primary Entry Point command.

An app with an Activity owns a command Discord creates itself, and a bulk
overwrite that leaves it out is rejected with error code 50240. The startup
sync retries once with the registered entry point added to the payload.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discord.errors import HTTPException  # noqa: E402

from utils import command_ids  # noqa: E402


def _command(name, command_id, *, command_type=1):
    return SimpleNamespace(
        name=name,
        id=command_id,
        type=command_type,
        options=[],
        to_dict=lambda _tree=None: {"name": name, "type": command_type, "options": []},
    )


class _Cxn:
    def __init__(self, stored="{}"):
        self.stored = stored
        self.executed = []

    async def fetchval(self, _query, _key):
        return self.stored

    async def execute(self, _query, *args):
        self.executed.append(args)
        if len(args) >= 2:
            self.stored = args[1]


def _http_exception(code):
    return HTTPException(
        SimpleNamespace(status=400, reason="Bad Request"),
        {"code": code, "message": "bulk update"},
    )


class _Tree:
    def __init__(self, command, sync_error):
        self.command = command
        self.sync_error = sync_error
        self.fetched_times = 0

    def get_commands(self):
        return [self.command]

    def _get_all_commands(self, guild=None):
        return [self.command]

    async def sync(self):
        raise self.sync_error

    async def fetch_commands(self):
        self.fetched_times += 1
        return [self.command]


def _run(bot):
    import events.startup.sync as startup_sync

    original = startup_sync.apply_command_localizations
    startup_sync.apply_command_localizations = lambda _tree: None
    try:
        asyncio.run(startup_sync.run_slash_sync(bot))
    finally:
        startup_sync.apply_command_localizations = original


def _bot(tree):
    registered = []
    posted = []

    async def get_global_commands(_application_id):
        registered.append(True)
        return [
            {"id": "900", "type": 4, "name": "launch", "description": "Start the activity"},
            {"id": "42", "type": 1, "name": "setup", "description": ""},
        ]

    async def bulk_upsert_global_commands(_application_id, payload):
        posted.append(payload)
        return []

    return SimpleNamespace(
        application_id=7,
        tree=tree,
        cxn=_Cxn(),
        http=SimpleNamespace(
            get_global_commands=get_global_commands,
            bulk_upsert_global_commands=bulk_upsert_global_commands,
        ),
    ), registered, posted


def test_a_sync_refused_for_the_entry_point_is_retried_with_it():
    command_ids.remember({})
    tree = _Tree(_command("setup", 42), _http_exception(50240))
    bot, registered, posted = _bot(tree)

    _run(bot)

    assert registered == [True]
    assert [[row["name"] for row in payload] for payload in posted] == [
        ["setup", "launch"],
    ]
    assert command_ids.mention("setup") == "</setup:42>"


def test_other_sync_failures_are_not_retried():
    command_ids.remember({})
    tree = _Tree(_command("setup", 42), _http_exception(50035))
    bot, registered, posted = _bot(tree)

    _run(bot)

    assert registered == []
    assert posted == []
