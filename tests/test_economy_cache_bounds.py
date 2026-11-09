"""The economy account cache is bounded.

A loaded account is ~15 KB in memory (transaction log, inventory, achievements,
season baselines), and the cache used to keep every member who had ever run an
economy command — plus a startup step that pre-loaded the whole table. It is now
an LRU of the accounts commands are working with, with an idle window so an
account in play is never dropped, a ceiling so a busy afternoon cannot undo the
cap, and no startup pre-load at all.
"""

import asyncio
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cogs.economy import cog as economy  # noqa: E402
from cogs.economy.data import _default_user, _migrate_user  # noqa: E402
from events.startup import economy as startup  # noqa: E402


def _cog(monkeypatch) -> economy.EconomyCog:
    """An economy cog without __init__ (which needs a bot and starts a task)."""

    async def load(bot, user_id):
        return _migrate_user(_default_user())

    async def save(bot, user_id, data):
        return None

    monkeypatch.setattr(economy, "_get_user_from_db", load)
    monkeypatch.setattr(economy, "_save_user_to_db", save)
    cog = economy.EconomyCog.__new__(economy.EconomyCog)
    cog.bot = SimpleNamespace()
    cog.economy_data = {}
    cog._account_used = {}
    return cog


def test_the_shipped_limits_bound_the_cache():
    assert 0 < economy.ACCOUNT_CACHE_LIMIT <= economy.ACCOUNT_CACHE_MAX
    # ~15 KB per account, so the ceiling is the memory ceiling.
    assert economy.ACCOUNT_CACHE_MAX * 15 * 1024 <= 32 * 1024 * 1024


def test_running_the_same_account_twice_keeps_one_entry(monkeypatch):
    cog = _cog(monkeypatch)
    asyncio.run(cog.get_user_economy_data(7))
    asyncio.run(cog.get_user_economy_data(7))
    assert list(cog.economy_data) == ["7"]


def test_a_burst_of_members_cannot_grow_the_cache_past_its_ceiling(monkeypatch):
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_LIMIT", 3)
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_MAX", 6)
    cog = _cog(monkeypatch)

    for user_id in range(1, 12):
        asyncio.run(cog.get_user_economy_data(user_id))

    assert len(cog.economy_data) == 6


def test_idle_accounts_are_trimmed_back_to_the_target(monkeypatch):
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_LIMIT", 3)
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_MAX", 6)
    cog = _cog(monkeypatch)
    cog.economy_data = {str(user_id): {} for user_id in range(5)}
    cog._account_used = {str(user_id): 0.0 for user_id in range(5)}

    cog._trim_account_cache(time.time())

    # Oldest first, so the last three survive.
    assert list(cog.economy_data) == ["2", "3", "4"]
    assert set(cog._account_used) == {"2", "3", "4"}


def test_an_account_still_in_use_is_not_the_one_evicted(monkeypatch):
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_LIMIT", 3)
    monkeypatch.setattr(economy, "ACCOUNT_CACHE_MAX", 6)
    cog = _cog(monkeypatch)
    cog.economy_data = {str(user_id): {} for user_id in range(4)}
    cog._account_used = {str(user_id): 0.0 for user_id in range(4)}

    # Account 0 is loaded again, which moves it to the most-recently-used end.
    cog.economy_data.pop("0")
    cog.economy_data["0"] = {}
    cog._account_used["0"] = time.time()

    cog._trim_account_cache(time.time())

    assert "0" in cog.economy_data
    assert "1" not in cog.economy_data
    assert len(cog.economy_data) == 3


def test_startup_does_not_load_the_whole_economy_table():
    class Cxn:
        async def fetch(self, *args, **kwargs):
            raise AssertionError("startup must not read economy_users")

    cog = SimpleNamespace(economy_data={"1": {"balance": 5}}, _account_used={"1": 1.0})
    bot = SimpleNamespace(get_cog=lambda name: cog, cxn=Cxn())

    asyncio.run(startup.preload_economy_cache(bot))

    assert cog.economy_data == {}
    assert cog._account_used == {}
