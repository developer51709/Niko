"""The locale feed reads the owner's sync setting before Discord's login.

Discord's client hands out a sentinel for ``loop`` until it logs in; every
attribute on it raises AttributeError ("loop attribute cannot be accessed in
non-async contexts").  The feed thread starts before that login, so probing the
sentinel used to crash the thread on the deployed Python.
"""

from __future__ import annotations

import asyncio
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class _LoopSentinel:
    def __getattr__(self, name: str) -> None:
        raise AttributeError(
            "loop attribute cannot be accessed in non-async contexts. "
            "Consider using either an asynchronous main function and passing it "
            "to asyncio.run or using asynchronous initialisation hooks such as "
            "Client.setup_hook"
        )


def test_the_pre_login_sentinel_is_not_a_loop():
    from webapp import locale_feed

    bot = SimpleNamespace(loop=_LoopSentinel(), cxn=object())
    # No attribute on the sentinel may be touched: it raises for all of them.
    assert locale_feed._bot_loop(bot) is None
    loop = asyncio.new_event_loop()
    try:
        assert locale_feed._bot_loop(bot, loop) is loop
    finally:
        loop.close()


def test_the_setting_is_read_on_the_loop_the_api_server_passes(monkeypatch):
    from webapp import locale_feed

    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, name="test-bot-loop", daemon=True)
    thread.start()
    called: list[bool] = []

    async def fake_load(bot):
        called.append(True)
        locale_feed._settings["loaded"] = True
        return True

    monkeypatch.setattr(locale_feed, "load_settings", fake_load)
    locale_feed._settings["loaded"] = False
    try:
        # The bot still carries the sentinel: the explicit loop is what the API
        # server obtained from get_running_loop().
        locale_feed._load_settings_at_start(
            SimpleNamespace(loop=_LoopSentinel(), cxn=object()), loop
        )
        assert called == [True]
        assert locale_feed._settings["loaded"] is True
    finally:
        locale_feed._settings["loaded"] = False
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=2)
        loop.close()
