"""Part 3: an update whose child never becomes ready is rolled back.

The updater writes ``pending.json`` just before asking for a supervised restart.
If that restart does not produce a ready child, the supervisor restores the
files from the run's backups and boots again from the last-good release. These
tests drive that with the fake child, so no Discord or real code is involved.
"""

from __future__ import annotations

import json
from pathlib import Path


def _repo(tmp_path: Path, content: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "bot.py").write_text(content, encoding="utf-8")
    return repo


def _pending(tmp_path: Path, repo: Path, changes: list[dict], backup: bytes | None = b"last good\n") -> Path:
    run = "run-test"
    backup_file = repo / "data" / "updates" / "backups" / run / "src" / "bot.py"
    if backup is not None:
        backup_file.parent.mkdir(parents=True)
        backup_file.write_bytes(backup)
    path = tmp_path / "pending.json"
    path.write_text(
        json.dumps(
            {
                "run_id": run,
                "area": "bot",
                "requested_at": 1,
                "backup_dir": f"data/updates/backups/{run}",
                "changes": changes,
            }
        ),
        encoding="utf-8",
    )
    return path


def _events(status: dict) -> list[str]:
    return [str(item.get("event")) for item in status.get("history") or ()]


def test_a_failed_boot_restores_the_last_good_files(supervisor, tmp_path):
    repo = _repo(tmp_path, "new release\n")
    pending = _pending(
        tmp_path,
        repo,
        [{"path": "src/bot.py", "status": "modified"}],
    )
    handle = supervisor(
        "crash-after-api",
        backoff_initial=0.1,
        backoff_max=0.1,
        max_restarts=2,
        args=[
            "--pending-update-file",
            str(pending),
            "--update-root",
            str(repo),
        ],
    )

    status = handle.wait_status(
        lambda payload: "rollback_applied" in _events(payload),
        timeout=15,
    )
    applied = next(
        item for item in status["history"] if item["event"] == "rollback_applied"
    )
    assert applied["run"] == "run-test"
    assert applied["restored"] == 1

    assert (repo / "src" / "bot.py").read_text(encoding="utf-8") == "last good\n"
    # The pending record is retired, so a second failure cannot restore again.
    assert not pending.exists()
    assert list(pending.parent.glob("pending.json.rolledback-*"))
    assert status["pending_update"] is None
    assert handle.request("/health").status_code == 200


def test_a_ready_child_confirms_the_pending_update(supervisor, tmp_path):
    repo = _repo(tmp_path, "new release\n")
    pending = _pending(
        tmp_path,
        repo,
        [{"path": "src/bot.py", "status": "modified"}],
    )
    handle = supervisor(
        "normal",
        args=[
            "--pending-update-file",
            str(pending),
            "--update-root",
            str(repo),
        ],
    )
    handle.wait_ready()

    status = handle.wait_status(
        lambda payload: "update_confirmed" in _events(payload),
        timeout=10,
    )
    assert (repo / "src" / "bot.py").read_text(encoding="utf-8") == "new release\n"
    assert not pending.exists()
    assert list(pending.parent.glob("pending.json.confirmed-*"))
    assert status["pending_update"] is None


def test_an_unsafe_pending_path_is_refused_not_restored(supervisor, tmp_path):
    repo = _repo(tmp_path, "new release\n")
    outside = tmp_path / "outside.txt"
    outside.write_text("untouched\n", encoding="utf-8")
    pending = _pending(
        tmp_path,
        repo,
        [{"path": "../outside.txt", "status": "modified"}],
    )
    handle = supervisor(
        "crash-after-api",
        backoff_initial=0.1,
        backoff_max=0.1,
        max_restarts=1,
        args=[
            "--pending-update-file",
            str(pending),
            "--update-root",
            str(repo),
        ],
    )

    status = handle.wait_status(
        lambda payload: "rollback_failed" in _events(payload),
        timeout=15,
    )
    event = next(item for item in status["history"] if item["event"] == "rollback_failed")
    assert "unsafe path" in event["error"]
    assert outside.read_text(encoding="utf-8") == "untouched\n"
    assert not pending.exists()
    assert list(pending.parent.glob("pending.json.failed-*"))


def test_a_pending_listing_an_added_file_removes_it_on_rollback(supervisor, tmp_path):
    repo = _repo(tmp_path, "new release\n")
    added = repo / "src" / "new_module.py"
    added.write_text("added by the update\n", encoding="utf-8")
    pending = _pending(
        tmp_path,
        repo,
        [{"path": "src/new_module.py", "status": "added"}],
        backup=None,
    )
    handle = supervisor(
        "crash-after-api",
        backoff_initial=0.1,
        backoff_max=0.1,
        max_restarts=1,
        args=[
            "--pending-update-file",
            str(pending),
            "--update-root",
            str(repo),
        ],
    )

    status = handle.wait_status(
        lambda payload: "rollback_applied" in _events(payload),
        timeout=15,
    )
    applied = next(
        item for item in status["history"] if item["event"] == "rollback_applied"
    )
    assert applied["removed"] == 1
    assert not added.exists()
