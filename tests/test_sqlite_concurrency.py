"""Part 3 drill: a second SQLite writer fails loudly instead of corrupting state.

The design forbids two active SQLite writers. Without a real second child this
verifies the underlying guarantee: while another connection holds a write lock,
a write through the pool raises instead of silently succeeding.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import aiosqlite
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402


@pytest.fixture(autouse=True)
def clean_pool(monkeypatch):
    monkeypatch.setattr(database, "_shared_pool", None, raising=False)


def test_a_locked_database_makes_the_second_writer_fail(monkeypatch, tmp_path):
    # Never let a developer's or CI environment point this at a real MongoDB:
    # the drill is specifically the SQLite write path.
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.delenv("NIKO_STRICT_DB", raising=False)
    db_path = tmp_path / "database.db"

    async def scenario():
        pool = await database.create_pool(str(db_path))
        assert pool.db_type == "sqlite"
        holder = await aiosqlite.connect(db_path)
        try:
            await pool.execute(
                "CREATE TABLE IF NOT EXISTS probe (id INTEGER PRIMARY KEY, value TEXT)"
            )
            await holder.execute("BEGIN IMMEDIATE")
            await holder.execute("INSERT INTO probe (value) VALUES ('held')")
            try:
                await asyncio.wait_for(
                    pool.execute("INSERT INTO probe (value) VALUES ('blocked')"),
                    timeout=10,
                )
            except Exception as exc:  # noqa: BLE001 - the error is the assertion
                return type(exc).__name__, str(exc)
            raise AssertionError("a second writer succeeded while the database was locked")
        finally:
            await holder.rollback()
            await holder.close()
            await pool._db.close()

    name, message = asyncio.run(scenario())

    assert name in {"OperationalError", "DatabaseError"}, name
    assert "lock" in message.lower(), message
