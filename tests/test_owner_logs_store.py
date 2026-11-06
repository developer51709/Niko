"""The owner console reads the per-process archive, so restarts and supervision show up."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from log_store import LogArchive  # noqa: E402


def test_the_owner_console_prefers_the_archive(tmp_path, monkeypatch):
    from webapp.routes import log_routes

    root = tmp_path / "logs"
    LogArchive(root).append(
        level="INFO",
        logger="supervisor",
        line="child web started pid=123",
        process="supervisor",
    )
    monkeypatch.setenv("NIKO_LOG_STORE", str(root))
    monkeypatch.setattr(log_routes, "_shared_store", None)

    archive = log_routes._log_buffer()
    assert isinstance(archive, LogArchive)
    snapshot = archive.snapshot(since="", processes="all", min_level="DEBUG")
    assert snapshot["lines"][0]["process"] == "supervisor"
    assert snapshot["lines"][0]["line"] == "child web started pid=123"
    # The response shape is the one the page already understands.
    for key in ("lines", "head", "next", "first", "token", "truncated", "reset", "has_more"):
        assert key in snapshot
    json.dumps(snapshot)


def test_the_archive_serves_one_process_and_level_at_a_time(tmp_path, monkeypatch):
    from webapp.routes import log_routes

    root = tmp_path / "logs"
    archive = LogArchive(root)
    archive.append(level="DEBUG", logger="bot", line="noisy debug", process="bot")
    archive.append(level="ERROR", logger="bot", line="bot failed", process="bot")
    archive.append(level="ERROR", logger="db", line="database failed", process="db")
    monkeypatch.setenv("NIKO_LOG_STORE", str(root))
    monkeypatch.setattr(log_routes, "_shared_store", None)

    # A bot, ERROR-and-above view reads only that process's error buffer.
    errors = log_routes._log_buffer().snapshot(
        since="", processes="bot", min_level="ERROR"
    )
    assert [line["line"] for line in errors["lines"]] == ["bot failed"]

    bot = log_routes._log_buffer().snapshot(since="", processes="bot", min_level="DEBUG")
    assert [line["line"] for line in bot["lines"]] == ["noisy debug", "bot failed"]


def test_the_route_selects_a_process_and_a_minimum_level():
    from webapp import server
    from webapp.routes import log_routes

    with server.app.test_request_context("/api/owner/logs?process=DB&level=all"):
        assert log_routes._process_arg() == "db"
        assert log_routes._level_arg() == "DEBUG"

    with server.app.test_request_context("/api/owner/logs?process=dashboard&level=warning"):
        assert log_routes._process_arg() == "web"
        assert log_routes._level_arg() == "WARNING"

    with server.app.test_request_context("/api/owner/logs"):
        assert log_routes._process_arg() == "all"
        assert log_routes._level_arg() == "DEBUG"


def test_the_owner_console_falls_back_to_the_process_buffer(tmp_path, monkeypatch):
    from webapp.routes import log_routes

    monkeypatch.delenv("NIKO_LOG_STORE", raising=False)
    monkeypatch.setattr(log_routes, "_shared_store", None)

    buffer = log_routes._log_buffer()
    # A direct (non-supervised) run still serves the in-process ring.
    assert buffer is not None
    assert hasattr(buffer, "snapshot")


def test_the_in_memory_ring_answers_in_the_archive_shape():
    from webapp.routes import log_routes

    class Ring:
        def snapshot(self, since=0, limit=2000):
            entries = [
                {"id": 1, "at": 1.0, "level": "INFO", "logger": "bot", "line": "debug", "process": "bot"},
                {"id": 2, "at": 2.0, "level": "ERROR", "logger": "bot", "line": "failed", "process": "bot"},
            ]
            return {
                "lines": [entry for entry in entries if entry["id"] > since][:limit],
                "head": 2,
                "next": 2,
                "first": 1,
                "token": "abc",
                "capacity": 5000,
                "noise_capacity": 2000,
                "truncated": False,
                "reset": False,
            }

    payload = log_routes._memory_snapshot(Ring(), "", 2000, "bot", "ERROR")
    assert [line["line"] for line in payload["lines"]] == ["failed"]
    assert payload["lines"][0]["id"] == "memory:2"
    assert payload["next"] == "memory:2" and payload["head"] == "memory:2"
    assert payload["has_more"] is False
    assert payload["capacity"] == 5000
