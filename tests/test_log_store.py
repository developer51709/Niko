"""The owner log archive: per-process, per-level buffers, cursors, rotation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from log_store import LogArchive, LogStore, store_from_environment  # noqa: E402


def _write(
    archive: LogArchive,
    text: str,
    *,
    process: str = "bot",
    level: str = "INFO",
    at: float | None = None,
) -> None:
    archive.append(level=level, logger="Startup", line=text, process=process, at=at)


def _texts(payload: dict) -> list[str]:
    return [line["line"] for line in payload["lines"]]


# ── The archive ────────────────────────────────────────────────────────────


def test_each_process_gets_its_own_file_and_buffer(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    _write(archive, "bot line", process="bot")
    _write(archive, "web line", process="web")
    _write(archive, "db line", process="db", level="ERROR")

    assert (tmp_path / "logs" / "bot" / "INFO.jsonl").exists()
    assert (tmp_path / "logs" / "web" / "INFO.jsonl").exists()
    assert (tmp_path / "logs" / "db" / "ERROR.jsonl").exists()
    bot_file = (tmp_path / "logs" / "bot" / "INFO.jsonl").read_text(encoding="utf-8")
    assert "bot line" in bot_file and "web line" not in bot_file

    only_bot = archive.snapshot(processes="bot", min_level="DEBUG")
    assert _texts(only_bot) == ["bot line"]
    assert all(line["process"] == "bot" for line in only_bot["lines"])

    only_errors = archive.snapshot(processes="db", min_level="ERROR")
    assert _texts(only_errors) == ["db line"]


def test_an_all_processes_view_merges_by_time(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    _write(archive, "older", process="web", at=100.0)
    _write(archive, "newer", process="bot", at=200.0)
    _write(archive, "middle", process="db", at=150.0)

    payload = archive.snapshot(processes="all", min_level="DEBUG")
    assert _texts(payload) == ["older", "middle", "newer"]
    assert [line["process"] for line in payload["lines"]] == ["web", "db", "bot"]


def test_levels_are_separate_files_and_the_level_selects_a_minimum(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    _write(archive, "debug", level="DEBUG")
    _write(archive, "info", level="INFO")
    _write(archive, "success", level="SUCCESS")
    _write(archive, "warning", level="WARNING")
    _write(archive, "error", level="ERROR")
    _write(archive, "critical", level="CRITICAL")

    levels = sorted(path.name for path in (tmp_path / "logs" / "bot").glob("*.jsonl"))
    assert levels == [
        "CRITICAL.jsonl",
        "DEBUG.jsonl",
        "ERROR.jsonl",
        "INFO.jsonl",
        "SUCCESS.jsonl",
        "WARNING.jsonl",
    ]

    # A warning view reads the warning, error and critical buffers only: a
    # DEBUG flood can never push those lines out of their own files.
    assert _texts(archive.snapshot(min_level="WARNING")) == ["warning", "error", "critical"]
    assert _texts(archive.snapshot(min_level="ERROR")) == ["error", "critical"]
    assert _texts(archive.snapshot(min_level="DEBUG")) == [
        "debug",
        "info",
        "success",
        "warning",
        "error",
        "critical",
    ]


def test_the_composite_cursor_only_returns_new_lines_across_restarts(tmp_path):
    root = tmp_path / "logs"
    archive = LogArchive(root)
    _write(archive, "first", at=100.0)
    first = archive.snapshot(min_level="DEBUG")
    assert _texts(first) == ["first"]
    assert isinstance(first["next"], str) and first["next"]
    assert first["next"] == first["head"]
    assert first["has_more"] is False
    # The id names the buffer and its byte offset, so two processes can never
    # hand the page the same key.
    assert first["lines"][0]["id"].startswith("bot/INFO:")

    _write(archive, "second", process="web", at=200.0)
    second = LogArchive(root).snapshot(min_level="DEBUG", since=first["next"])
    assert _texts(second) == ["second"]
    assert second["reset"] is False
    assert second["lines"][0]["id"].startswith("web/INFO:")

    # A cursor from another archive directory is stale even when its offsets
    # would fit, and the page is told to start over.
    other = LogArchive(tmp_path / "other")
    _write(other, "elsewhere")
    stale = other.snapshot(min_level="DEBUG", since=second["next"])
    assert stale["reset"] is True
    assert _texts(stale) == ["elsewhere"]


def test_a_legacy_numeric_cursor_resets_once_then_continues(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    _write(archive, "line")

    # A tab loaded before the archive sent a single byte offset: it is told to
    # clear once, then its retry with 0 reads the current tail without looping.
    assert archive.snapshot(min_level="DEBUG", since="123")["reset"] is True
    again = archive.snapshot(min_level="DEBUG", since="0")
    assert again["reset"] is False
    assert _texts(again) == ["line"]


def test_a_cursor_can_skip_lines_but_a_batch_advances_only_what_it_read(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    for index in range(5):
        _write(archive, f"line {index}", at=100.0 + index)

    page = archive.snapshot(min_level="INFO", limit=2)
    assert _texts(page) == ["line 0", "line 1"]
    assert page["has_more"] is True

    rest = archive.snapshot(min_level="INFO", since=page["next"], limit=10)
    assert _texts(rest) == ["line 2", "line 3", "line 4"]
    assert rest["has_more"] is False
    assert rest["next"] == rest["head"]


def test_rotation_resets_only_the_rotated_level_buffer(tmp_path):
    archive = LogArchive(tmp_path / "logs", max_bytes=64 * 1024, backups=2)
    _write(archive, "important", level="ERROR")
    payload = "x" * 900
    for index in range(120):
        _write(archive, f"{index:03d} {payload}", level="INFO")

    assert (tmp_path / "logs" / "bot" / "INFO.jsonl.1").exists()
    assert not (tmp_path / "logs" / "bot" / "ERROR.jsonl.1").exists()

    # The cursor for the rotated INFO stream points past the end of the new
    # file, so the page is told to reset; the ERROR stream is unaffected.
    stale = archive.snapshot(
        min_level="DEBUG",
        since=f"v1|{archive.token}|bot/ERROR=0;bot/INFO=999999999",
    )
    assert stale["reset"] is True
    assert "important" in _texts(stale)

    current = archive.snapshot(min_level="ERROR")
    assert current["reset"] is False
    assert _texts(current) == ["important"]


def test_a_process_name_cannot_escape_the_archive(tmp_path):
    archive = LogArchive(tmp_path / "logs")
    _write(archive, "sneaky", process="../../etc")

    assert (tmp_path / "logs" / "etc" / "INFO.jsonl").exists()
    assert not (tmp_path / "etc").exists()
    assert archive.processes() == ["etc"]


def test_two_processes_append_concurrently_without_losing_lines(tmp_path):
    root = tmp_path / "logs"
    code = (
        "import sys; sys.path.insert(0, %r)\n"
        "from log_store import LogArchive\n"
        "archive = LogArchive(%r)\n"
        "for index in range(40):\n"
        "    archive.append(level='INFO', logger='Worker', line=f'%s-{index}', process='%s')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    for name in ("bot", "web"):
        subprocess.run(
            [sys.executable, "-c", code % (str(ROOT / "src"), str(root), name, name)],
            check=True,
            env=env,
            cwd=str(ROOT),
        )

    snapshot = LogArchive(root).snapshot(min_level="DEBUG", limit=5000)
    assert len(snapshot["lines"]) == 80
    for name in ("bot", "web"):
        texts = [line["line"] for line in snapshot["lines"] if line["process"] == name]
        assert texts == [f"{name}-{index}" for index in range(40)]
    assert snapshot["next"] == snapshot["head"]


def test_the_environment_selects_the_archive(tmp_path, monkeypatch):
    root = tmp_path / "logs"
    monkeypatch.setenv("NIKO_LOG_STORE", str(root))
    monkeypatch.setenv("NIKO_LOG_STORE_BYTES", "131072")

    archive = store_from_environment()
    assert isinstance(archive, LogArchive)
    assert archive.root == root
    assert archive.max_bytes == 131072

    archive.append(level="ERROR", logger="supervisor", line="boom", process="supervisor")
    line = LogArchive(root).snapshot(processes="supervisor", min_level="ERROR")["lines"][0]
    assert line["process"] == "supervisor"
    assert line["level"] == "ERROR"

    monkeypatch.delenv("NIKO_LOG_STORE")
    assert store_from_environment() is None


# ── The single stream underneath every buffer ──────────────────────────────


def test_cursor_reads_only_new_lines_and_survives_a_new_store_instance(tmp_path):
    path = tmp_path / "INFO.jsonl"
    store = LogStore(path)
    _entry(store, "first")

    first = store.snapshot(0)
    assert [line["line"] for line in first["lines"]] == ["first"]
    assert first["next"] == first["head"]

    _entry(store, "second")
    second = store.snapshot(first["next"])
    assert [line["line"] for line in second["lines"]] == ["second"]
    assert second["lines"][0]["id"] > first["lines"][0]["id"]

    # A replaced process opens its own store over the same file.  The byte
    # cursor still points at the right place, which is what lets the owner page
    # keep its history across a child restart.
    reopened = LogStore(path)
    third = reopened.snapshot(second["next"])
    assert third["lines"] == []
    assert third["next"] == second["next"]
    assert third["token"] == store.token


def test_rotation_keeps_a_backup_and_tells_a_stale_cursor_to_reset(tmp_path):
    path = tmp_path / "INFO.jsonl"
    store = LogStore(path, max_bytes=64 * 1024, backups=2)
    payload = "x" * 900
    for index in range(120):
        _entry(store, f"{index:03d} {payload}")

    assert (tmp_path / "INFO.jsonl.1").exists()
    backup = json.loads((tmp_path / "INFO.jsonl.1").read_text().splitlines()[0])
    assert backup["line"].startswith("000 ")

    # A cursor past the end belongs to the file that was rotated away.  The
    # page clears on this flag and starts again from the new file's first line;
    # like the in-memory buffer, the response may still carry the current tail.
    stale = store.snapshot(10**9)
    assert stale["reset"] is True
    assert stale["head"] < 10**9

    current = store.snapshot(0, limit=5000)
    assert current["lines"]
    assert current["lines"][-1]["line"].startswith("119 ")


def _entry(store: LogStore, text: str, process: str = "bot") -> None:
    store.append(level="INFO", logger="Startup", line=text, process=process)
