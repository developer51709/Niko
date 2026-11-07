from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import handoff  # noqa: E402
from webapp import updates  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_update_data(monkeypatch, tmp_path):
    """Keep staging records out of the checkout's real ``data/updates``."""
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "updates")


def _plan():
    change = {"path": "src/bot.py", "status": "modified", "bytes": 10, "sha": "sha"}
    return {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"bot": {"label": "Bot core", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    }


def _prepare(monkeypatch):
    monkeypatch.setattr(updates, "plan", lambda areas=None: _plan())
    monkeypatch.setattr(
        updates,
        "_stage_area",
        lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"},
    )
    monkeypatch.setattr(updates, "_record", lambda run: None)
    monkeypatch.setattr(updates, "_probe_bot", lambda: None)
    monkeypatch.setitem(sys.modules, "api_server", SimpleNamespace(serving=lambda: True))
    monkeypatch.setattr(updates.supervisor_control, "is_supervised", lambda: True)
    monkeypatch.setattr(
        updates.supervisor_control,
        "socket_path",
        lambda: "/tmp/niko-supervisor.sock",
    )


def test_supervised_bot_update_requests_supervisor_restart(monkeypatch):
    _prepare(monkeypatch)
    requested = []
    monkeypatch.setattr(
        updates.supervisor_control,
        "request_restart",
        lambda **kwargs: requested.append(kwargs) or {"ok": True, "accepted": True},
    )
    monkeypatch.setattr(
        updates,
        "_inplace_handoff",
        lambda: (_ for _ in ()).throw(AssertionError("supervised update used handoff")),
    )
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(True))

    result = updates.apply(["bot"], object())

    assert result["ok"] is True
    assert result["areas"]["bot"]["strategy"] == "requesting a supervised restart"
    assert requested
    assert scheduled == []


def test_supervised_bot_update_records_the_last_good_restore_point(monkeypatch):
    _prepare(monkeypatch)
    seen = {}

    def restart(**kwargs):
        seen["pending"] = json.loads(
            (updates.DATA_DIR / "pending.json").read_text(encoding="utf-8")
        )
        return {"ok": True, "accepted": True}

    monkeypatch.setattr(updates.supervisor_control, "request_restart", restart)

    result = updates.apply(["bot"], object())

    assert result["ok"] is True
    pending = seen["pending"]
    assert pending["run_id"] == result["run"]
    assert pending["area"] == "bot"
    assert pending["backup_dir"] == f"data/updates/backups/{result['run']}"
    assert pending["changes"] == [{"path": "src/bot.py", "status": "modified"}]
    assert (updates.DATA_DIR / "pending.json").exists()


def _restart_targets_for(monkeypatch, *, split_web: str, split_db: str) -> list:
    """The ``child`` values a bot update sends, in the requested split layout."""
    _prepare(monkeypatch)
    monkeypatch.setenv("NIKO_SPLIT_WEB", split_web)
    monkeypatch.setenv("NIKO_SPLIT_DB", split_db)
    requested = []
    monkeypatch.setattr(
        updates.supervisor_control,
        "request_restart",
        lambda **kwargs: requested.append(kwargs) or {"ok": True, "accepted": True},
    )

    result = updates.apply(["bot"], object())

    assert result["ok"] is True
    assert requested, "a bot update must request a supervised restart"
    return [item.get("child") for item in requested]


def test_a_bot_update_restarts_the_database_child_beside_the_bot(monkeypatch):
    # The database child imported ``src/database/`` at its own boot, so it has
    # to be replaced with the bot or it keeps serving the old modules.
    assert _restart_targets_for(monkeypatch, split_web="1", split_db="1") == [
        ["bot", "db"]
    ]


def test_a_bot_update_leaves_the_split_database_alone_when_it_is_in_the_bot(monkeypatch):
    assert _restart_targets_for(monkeypatch, split_web="1", split_db="0") == ["bot"]


def test_a_bot_update_in_the_combined_layout_restarts_every_child(monkeypatch):
    # ``None`` is the supervisor's "all children", which is right when the bot
    # child is also the dashboard and the database.
    assert _restart_targets_for(monkeypatch, split_web="0", split_db="0") == [None]


def test_a_rejected_supervised_restart_clears_the_restore_point(monkeypatch):
    _prepare(monkeypatch)
    monkeypatch.setattr(
        updates.supervisor_control,
        "request_restart",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("control socket unavailable")),
    )
    monkeypatch.setattr(updates, "_restore_area", lambda name, files, run_id: None)

    result = updates.apply(["bot"], object())

    assert result["ok"] is False
    assert not (updates.DATA_DIR / "pending.json").exists()


def test_a_rejected_supervised_restart_rolls_the_bot_area_back(monkeypatch):
    _prepare(monkeypatch)
    rolled_back = []
    monkeypatch.setattr(
        updates.supervisor_control,
        "request_restart",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("control socket unavailable")),
    )
    monkeypatch.setattr(
        updates,
        "_restore_area",
        lambda name, files, run_id: rolled_back.append(name),
    )

    result = updates.apply(["bot"], object())

    assert result["ok"] is False
    assert result["areas"]["bot"]["rolled_back"] is True
    assert rolled_back == ["bot"]
