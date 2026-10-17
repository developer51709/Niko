"""Automated anti-abuse detection for rapid AI and command requests."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque

from discord.ext import commands

from utils.blacklist_manager import BlacklistManager


class AbuseRateLimit(commands.CheckFailure):
    """Raised when a command request triggers automated anti-abuse action."""

    def __init__(self, result: dict):
        self.result = result
        super().__init__("Automated abuse rate limit triggered.")


def strike_notice(result: dict) -> str:
    strikes = int(result.get("strikes", 0))
    if result.get("permanent"):
        return f"Automated anti-abuse: this request exceeded the spam limit. Strike {strikes}/3 — you are now permanently blacklisted."
    expires_at = result.get("expires_at")
    duration = "temporarily"
    if expires_at:
        expiry = datetime.fromtimestamp(expires_at, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        duration = f"until {expiry}"
    return f"Automated anti-abuse: this request exceeded the spam limit. Strike {strikes}/3 — access is suspended {duration}. Further strikes lead to a longer suspension, then a permanent blacklist."


# A short burst limit; the existing per-command cooldowns remain the primary
# user-facing throttle, while this catches repeated attempts to bypass them.
WINDOW_SECONDS = 10.0
MAX_REQUESTS_PER_WINDOW = 8

_requests: dict[int, Deque[float]] = defaultdict(deque)
_locks: dict[int, asyncio.Lock] = {}


def _get_lock(user_id: int) -> asyncio.Lock:
    return _locks.setdefault(user_id, asyncio.Lock())


async def record_request(user_id: int, *, reason: str) -> dict:
    """Return abuse status; the ninth request in 10 seconds earns a strike."""
    async with _get_lock(user_id):
        manager = BlacklistManager()
        await manager._ensure_loaded()
        if manager.get_user_entry(user_id):
            return {"abuse": False, "strikes": 0, "blacklisted": True, "permanent": False, "expires_at": None}

        now = time.monotonic()
        timestamps = _requests[user_id]
        while timestamps and timestamps[0] <= now - WINDOW_SECONDS:
            timestamps.popleft()
        timestamps.append(now)

        # Prune idle users to keep memory bounded.
        if len(_requests) > 4096:
            for inactive_user_id, events in list(_requests.items()):
                if not events or events[-1] <= now - WINDOW_SECONDS:
                    _requests.pop(inactive_user_id, None)
                    _locks.pop(inactive_user_id, None)

        if len(timestamps) <= MAX_REQUESTS_PER_WINDOW:
            return {"abuse": False, "strikes": 0, "blacklisted": False, "permanent": False, "expires_at": None}

        result = await BlacklistManager().register_abuse_strike(user_id, reason=reason)
        # Start a fresh window so continued spamming doesn't create dozens of
        # punishments from one continuous burst; users accrue a later strike
        # only after they resume and exceed the threshold again.
        timestamps.clear()
        return {"abuse": True, **result}
