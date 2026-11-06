"""Part 3: hostile update inputs must fail closed and leave files intact.

Covers the fault-injection rows that do not need a live instance: a malformed
beta manifest, a tampered download, a full disk while staging, and a second
update request while one is already running.
"""

from __future__ import annotations

import errno
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import updates  # noqa: E402


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    monkeypatch.setattr(updates, "_manifest_cache", {"at": 0.0, "document": None, "error": None})
    updates._progress_reset()
    yield
    updates._progress_reset()


class _Response:
    status_code = 200

    def __init__(self, payload=None, content: bytes = b"") -> None:
        self._payload = payload
        self.content = content

    def json(self):
        return self._payload


def _configured(monkeypatch):
    monkeypatch.setattr(updates, "beta_base", lambda: "http://beta.test")
    monkeypatch.setattr(updates, "token", lambda: "shared-secret")


def test_a_malformed_manifest_is_reported_not_applied(monkeypatch):
    _configured(monkeypatch)
    monkeypatch.setattr(updates.requests, "get", lambda *args, **kwargs: _Response({"areas": "broken"}))

    assert updates.beta_manifest(force=True) is None
    plan = updates.plan(["bot"])

    assert plan["ok"] is False
    assert "file list" in plan["error"]
    assert plan["areas"] == {}


def test_a_manifest_that_is_not_json_is_reported(monkeypatch):
    _configured(monkeypatch)

    class Broken(_Response):
        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr(updates.requests, "get", lambda *args, **kwargs: Broken())

    assert updates.beta_manifest(force=True) is None
    assert updates.manifest_error()
    assert updates.plan(["bot"])["ok"] is False


def test_a_tampered_download_is_rejected(monkeypatch):
    _configured(monkeypatch)
    monkeypatch.setattr(
        updates.requests,
        "get",
        lambda *args, **kwargs: _Response(content=b"tampered"),
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        updates._download("src/bot.py", "0" * 40)


def test_a_full_disk_while_staging_restores_the_previous_file(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    target = repo / "src" / "bot.py"
    target.write_text("OLD_RELEASE = True\n", encoding="utf-8")

    monkeypatch.setattr(updates, "ROOT", repo)
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(updates, "_download", lambda relative, expected: b"NEW_RELEASE = True\n")
    monkeypatch.setattr(
        updates,
        "_write",
        lambda relative, body: (_ for _ in ()).throw(OSError(errno.ENOSPC, "No space left on device")),
    )

    with pytest.raises(OSError, match="No space left"):
        updates._stage_area(
            "bot",
            [{"path": "src/bot.py", "status": "modified", "sha": "x", "bytes": 12}],
            "run-disk-full",
        )

    assert target.read_text(encoding="utf-8") == "OLD_RELEASE = True\n"


def test_a_second_update_is_refused_while_one_is_running(monkeypatch):
    monkeypatch.setattr(
        updates,
        "plan",
        lambda areas=None: {
            "ok": True,
            "configured": True,
            "beta": "http://beta.test",
            "areas": {},
            "total_changed": 0,
            "total_bytes": 0,
            "running": True,
            "last": None,
        },
    )
    updates._running["active"] = True

    result = updates.apply(["bot"])

    assert result["ok"] is False
    assert "already being applied" in result["error"]
