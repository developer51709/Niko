"""Part 3 drill: a strict deployment whose MongoDB is down never falls back.

This runs the real ``database.create_pool`` inside a supervised harness child.
The connector is replaced (no network, no external database), so the assertion
is about this repository's behaviour: no SQLite file is created, readiness stays
down, and the supervisor stops the restart loop once its budget is spent.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRICT_CHILD = ROOT / "tests" / "supervisor" / "strict_db_child.py"


def test_strict_database_refuses_to_create_sqlite_when_mongodb_is_down(
    supervisor, tmp_path
):
    db_path = tmp_path / "database.db"
    handle = supervisor(
        "normal",
        max_restarts=1,
        backoff_initial=0.1,
        backoff_max=0.1,
        env={
            "MONGODB_URL": "mongodb://127.0.0.1:1",
            "NIKO_STRICT_DB": "1",
        },
        args=[
            "--child",
            str(STRICT_CHILD),
            "--child-arg",
            str(db_path),
        ],
    )

    status = handle.wait_status(lambda payload: payload["state"] == "failed", timeout=20)

    assert not db_path.exists(), "strict mode created a local SQLite database"
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 503
    assert status["consecutive_failures"] >= 1
    assert status["last_error"]

    not_ready = [
        item for item in status["history"] if item["event"] == "child_not_ready"
    ]
    assert not_ready, status["history"]
    assert "NIKO_STRICT_DB" in not_ready[-1]["reason"]
    assert not any(item["event"] == "child_ready" for item in status["history"])
