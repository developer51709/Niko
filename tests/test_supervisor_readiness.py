import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import supervisor_readiness
from utils import interaction_endpoint


class Pool:
    db_type = "sqlite"

    async def fetchval(self, query, *args):
        return 1


class Shard:
    def is_closed(self):
        return False


class Bot:
    def __init__(self, **overrides):
        self.cxn = Pool()
        self.shards = {0: Shard()}
        self.shard_count = 1
        self.cog_status = [
            {"name": "cogs.system", "state": "loaded"},
            {"name": "cogs.admin", "state": "loaded"},
            {"name": "cogs.utility", "state": "loaded"},
        ]
        self.startup_errors = []
        self.startup_step_errors = {}
        self.__dict__.update(overrides)

    def is_ready(self):
        return True


@pytest.fixture(autouse=True)
def _public_key(monkeypatch):
    monkeypatch.setattr(interaction_endpoint, "public_key_configured", lambda: True)


def run(bot):
    return asyncio.run(supervisor_readiness.evaluate(bot))


def test_ready_requires_database_gateway_and_critical_cogs():
    result = run(Bot())

    assert result["state"] == "ready"
    assert result["ready"] is True
    assert result["checks"]["database"]["ok"] is True
    assert result["checks"]["gateway"]["ok"] is True


def test_missing_database_is_not_ready():
    result = run(Bot(cxn=None))

    assert result["state"] == "not_ready"
    assert any("database" in reason for reason in result["reasons"])


def test_a_failed_critical_cog_is_not_ready():
    bot = Bot()
    bot.cog_status[0] = {"name": "cogs.system", "state": "failed", "reason": "ImportError"}

    result = run(bot)

    assert result["state"] == "not_ready"
    assert any("cogs.system" in reason for reason in result["critical"])


def test_an_optional_startup_failure_degrades_but_does_not_block():
    bot = Bot(startup_step_errors={"write_bot_stats": "OSError: disk full"})

    result = run(bot)

    assert result["state"] == "degraded"
    assert result["ready"] is True
    assert any("write_bot_stats" in reason for reason in result["reasons"])


def test_a_critical_startup_failure_is_not_ready():
    bot = Bot(startup_step_errors={"load_cogs": "RuntimeError: broken"})

    result = run(bot)

    assert result["state"] == "not_ready"
    assert any("load_cogs" in reason for reason in result["critical"])


def test_closed_gateway_shard_is_not_ready():
    class ClosedShard:
        def is_closed(self):
            return True

    result = run(Bot(shards={0: ClosedShard()}))

    assert result["state"] == "not_ready"
    assert any("shard" in reason for reason in result["critical"])
