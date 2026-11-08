"""Rank cards must never move a whole table through the bot to find a rank.

The rank shown on the balance/profile and level cards used to be computed by
fetching every economy account (or every row in the guild) and sorting it in
Python.  That put a copy of the table in the bot's memory at the same moment the
card was rendering, which is enough to get a healthy child killed under memory
pressure and replaced by the supervisor.  These tests pin the replacement: one
counting query, and no unbounded fetch.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.economy.cog import EconomyCog  # noqa: E402
from cogs.leveling.cog import Leveling  # noqa: E402


class CountingPool:
    """A database pool that records queries and refuses unbounded reads."""

    def __init__(self, *, higher: int = 0, value: int = 0, fail: bool = False) -> None:
        self.higher = higher
        self.value = value
        self.fail = fail
        self.queries: list[tuple[str, str, tuple]] = []

    async def fetchval(self, query: str, *args):
        self.queries.append(("fetchval", " ".join(query.split()), args))
        if self.fail:
            raise RuntimeError("database unavailable")
        return self.higher

    async def fetch(self, query: str, *args):  # pragma: no cover - asserted unused
        self.queries.append(("fetch", " ".join(query.split()), args))
        raise AssertionError(f"rank card issued a row fetch: {query}")

    async def fetchrow(self, query: str, *args):  # pragma: no cover
        self.queries.append(("fetchrow", " ".join(query.split()), args))
        raise AssertionError(f"rank card issued a row fetch: {query}")


def _economy(pool: CountingPool) -> EconomyCog:
    return SimpleNamespace(bot=SimpleNamespace(cxn=pool))  # type: ignore[return-value]


def _leveling(pool: CountingPool) -> Leveling:
    return SimpleNamespace(bot=SimpleNamespace(cxn=pool))  # type: ignore[return-value]


def test_net_worth_rank_is_a_single_count():
    pool = CountingPool(higher=41)

    rank = asyncio.run(EconomyCog._net_rank(_economy(pool), 12_345))

    assert rank == 42
    assert [kind for kind, _, _ in pool.queries] == ["fetchval"]
    query, args = pool.queries[0][1:]
    assert "COUNT(*)" in query and "net_worth >" in query
    assert args == (12_345,)


def test_net_worth_rank_failure_costs_the_card_its_rank_only():
    pool = CountingPool(fail=True)

    assert asyncio.run(EconomyCog._net_rank(_economy(pool), 5)) is None


def test_guild_level_rank_is_a_single_count():
    pool = CountingPool(higher=6)

    rank = asyncio.run(Leveling._get_user_rank(_leveling(pool), 99, 12, 340))

    assert rank == 7
    assert [kind for kind, _, _ in pool.queries] == ["fetchval"]
    query, args = pool.queries[0][1:]
    assert "COUNT(*)" in query and "level >" in query
    assert args == (99, 12, 340)


def test_guild_level_rank_falls_back_to_first():
    pool = CountingPool(fail=True)

    assert asyncio.run(Leveling._get_user_rank(_leveling(pool), 99, 0, 0)) == 1
