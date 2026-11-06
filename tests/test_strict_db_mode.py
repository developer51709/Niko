"""Part 3: strict database backend mode.

A supervised production instance must never silently start on an empty local
SQLite file because MongoDB was unreachable. ``NIKO_STRICT_DB=1`` turns that
fallback into a startup failure, and readiness treats a non-Mongo pool as fatal.
Non-strict deployments keep the existing fallback.
"""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
import supervisor_readiness  # noqa: E402


@pytest.fixture(autouse=True)
def clean_pool(monkeypatch):
    monkeypatch.setattr(database, "_shared_pool", None, raising=False)
    yield


def test_strict_mode_refuses_sqlite_without_a_mongodb_url(monkeypatch, tmp_path):
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.setenv("NIKO_STRICT_DB", "1")

    with pytest.raises(RuntimeError, match="MONGODB_URL"):
        asyncio.run(database.create_pool(str(tmp_path / "database.db")))


def test_default_mode_still_falls_back_to_sqlite(monkeypatch, tmp_path):
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.delenv("NIKO_STRICT_DB", raising=False)

    pool = asyncio.run(database.create_pool(str(tmp_path / "database.db")))
    try:
        assert pool.db_type == "sqlite"
    finally:
        asyncio.run(pool._db.close())


def test_strict_mode_does_not_fall_back_when_mongodb_is_unreachable(monkeypatch, tmp_path):
    monkeypatch.setenv("MONGODB_URL", "mongodb://127.0.0.1:1")
    monkeypatch.setenv("NIKO_STRICT_DB", "1")

    def failing_client(*args, **kwargs):
        raise RuntimeError("mongo down")

    fake = types.ModuleType("motor.motor_asyncio")
    fake.AsyncIOMotorClient = failing_client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "motor", types.ModuleType("motor"))
    monkeypatch.setitem(sys.modules, "motor.motor_asyncio", fake)
    # The retry loop is about behaviour, not about waiting six seconds.
    monkeypatch.setattr(
        database,
        "asyncio",
        types.SimpleNamespace(sleep=lambda _seconds: asyncio.sleep(0)),
    )

    with pytest.raises(RuntimeError, match="refusing to fall back"):
        asyncio.run(database.create_pool(str(tmp_path / "database.db")))
    assert not (tmp_path / "database.db").exists()


def test_readiness_fails_on_sqlite_while_strict(monkeypatch):
    monkeypatch.setenv("NIKO_STRICT_DB", "1")

    class Pool:
        db_type = "sqlite"

    bot = types.SimpleNamespace(cxn=Pool())
    ok, detail = asyncio.run(supervisor_readiness._ping_database(bot))

    assert ok is False
    assert "NIKO_STRICT_DB" in detail


def test_readiness_accepts_sqlite_when_not_strict(monkeypatch):
    monkeypatch.delenv("NIKO_STRICT_DB", raising=False)

    class Pool:
        db_type = "sqlite"

        async def fetchval(self, _query):
            return 1

    bot = types.SimpleNamespace(cxn=Pool())
    ok, detail = asyncio.run(supervisor_readiness._ping_database(bot))

    assert ok is True
    assert detail == "sqlite"
