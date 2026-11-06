"""The gateway event files update without a bot-core restart.

``src/events/on_message.py`` is called from a callback ``bot.py`` registered at
start-up; that callback reads the handler's name from bot.py's globals on every
dispatch, so re-importing the module and rebinding the name is enough for the next
message to run the new file. These checks pin that split: the event modules are
their own area, the startup writers and schema have their own areas, the rest of
the startup chain is not, and a broken event file leaves the running handler in
place.
"""

import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import handoff  # noqa: E402
from webapp import updates  # noqa: E402


def test_the_event_modules_are_their_own_area():
    assert updates.area_for_path("src/events/on_message.py") == "events"
    assert updates.area_for_path("src/events/on_ready.py") == "events"
    assert updates.area_for_path("src/events/__init__.py") == "events"


def test_the_remaining_startup_chain_stays_with_the_bot_core():
    # Apart from the schema and the ready-time writers, the startup chain runs
    # once at boot: re-importing it would change nothing until a restart, so it
    # must not be advertised as a live area.
    assert updates.area_for_path("src/events/startup/loader.py") == "bot"
    assert updates.area_for_path("src/events/startup/status.py") == "bot"
    assert updates.area_for_path("src/bot.py") == "bot"
    assert updates.area_for_path("src/events/startup/database.py") == "database"


def test_each_area_lists_only_the_files_it_owns():
    event_files = updates.area_files("events")
    bot_files = updates.area_files("bot")

    assert "src/events/on_message.py" in event_files
    assert not any(path.startswith("src/events/startup/") for path in event_files)

    assert "src/events/startup/loader.py" in bot_files
    assert "src/events/startup/database.py" not in bot_files
    assert "src/events/on_message.py" not in bot_files
    assert "src/bot.py" in bot_files

    assert updates.area_files("database") == ["src/events/startup/database.py"]


def test_events_apply_before_the_bot_core_so_a_restart_sees_them():
    order = list(updates.AREA_ORDER)
    assert order.index("events") < order.index("bot")
    # The schema has to exist before the code that reads those tables reloads.
    assert order.index("utils") < order.index("database") < order.index("webapp")


def test_an_event_update_rebinds_the_callbacks(monkeypatch):
    import events.on_message as before

    host = types.ModuleType("bot")
    host.handle_message = before.handle_message
    monkeypatch.setitem(sys.modules, "bot", host)

    result = updates.reload_events(["src/events/on_message.py"])

    assert result["reloaded"] == ["events.on_message"]
    assert result["failed"] == []
    assert result["rebound"] == ["events.on_message.handle_message"]
    fresh = sys.modules["events.on_message"]
    assert host.handle_message is fresh.handle_message
    assert host.handle_message is not before.handle_message


def test_applying_only_the_events_area_does_not_restart_the_process(monkeypatch):
    import events.on_message as before

    host = types.ModuleType("bot")
    host.handle_message = before.handle_message
    monkeypatch.setitem(sys.modules, "bot", host)

    change = {"path": "src/events/on_message.py", "status": "modified", "bytes": 10, "sha": "sha"}
    monkeypatch.setattr(updates, "plan", lambda areas=None: {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"events": {"label": "Gateway events", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    })
    monkeypatch.setattr(updates, "_stage_area", lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"})
    monkeypatch.setattr(updates, "_record", lambda run: None)
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(True))

    result = updates.apply(["events"], None)

    assert result["ok"] is True
    assert result["areas"]["events"]["strategy"] == "re-imported the gateway event handlers"
    assert result["areas"]["events"]["rebound"] == ["events.on_message.handle_message"]
    assert host.handle_message is sys.modules["events.on_message"].handle_message
    assert scheduled == []


def test_a_module_that_cannot_import_leaves_the_handler_alone(monkeypatch):
    import events.on_message as before

    monkeypatch.setattr(updates.importlib, "import_module", lambda name, *args, **kwargs: (_ for _ in ()).throw(ImportError("broken")))

    result = updates.reload_events(["src/events/on_message.py"])

    assert result["reloaded"] == []
    assert result["rebound"] == []
    assert result["failed"] and "ImportError" in result["failed"][0]
    # The process keeps running the module it already had.
    assert sys.modules["events.on_message"] is before


def test_a_rollback_re_imports_whatever_events_are_loaded():
    result = updates.reload_events(None)

    assert "events.on_message" in result["reloaded"]
    assert result["failed"] == []
