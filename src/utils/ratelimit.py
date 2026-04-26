"""Async per-key rate limiter using a rolling window.

Use a single shared instance per logical surface (e.g. one limiter for
"channel sends", another for "role assignments") and call ``acquire(key)``
before performing the rate-limited operation.  ``acquire`` will sleep just
long enough so that no more than ``rate`` operations occur per ``per``
seconds for the supplied key, never dropping calls — it queues them.

The implementation uses a small deque of recent timestamps per key and a
per-key ``asyncio.Lock`` so concurrent callers for the same key are
serialised cleanly.  Idle keys are pruned automatically by ``acquire``
itself once their window has fully elapsed, so memory usage stays bounded
to the set of recently-active keys.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Hashable


class RateLimiter:
    __slots__ = ("rate", "per", "_timestamps", "_locks")

    def __init__(self, rate: int, per: float):
        if rate < 1:
            raise ValueError("rate must be >= 1")
        if per <= 0:
            raise ValueError("per must be > 0")
        self.rate: int = rate
        self.per: float = per
        self._timestamps: dict[Hashable, deque[float]] = {}
        self._locks: dict[Hashable, asyncio.Lock] = {}

    def _lock_for(self, key: Hashable) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def acquire(self, key: Hashable = "_global") -> None:
        lock = self._lock_for(key)
        async with lock:
            ts = self._timestamps.get(key)
            if ts is None:
                ts = deque()
                self._timestamps[key] = ts

            now = time.monotonic()
            cutoff = now - self.per
            while ts and ts[0] < cutoff:
                ts.popleft()

            if len(ts) >= self.rate:
                wait = ts[0] + self.per - now
                if wait > 0:
                    await asyncio.sleep(wait)
                    now = time.monotonic()
                    cutoff = now - self.per
                    while ts and ts[0] < cutoff:
                        ts.popleft()

            ts.append(time.monotonic())

            if not ts:
                self._timestamps.pop(key, None)
                self._locks.pop(key, None)


# ─────────────────────────────────────────────────────────────
#  Shared limiters used across the bot.
#
#  Discord's per-channel send limit is roughly 5 messages / 5 seconds for
#  bots; we stay comfortably below that to leave headroom for the bot's
#  other activity (commands, reactions, etc.).
# ─────────────────────────────────────────────────────────────

# One bucket per (guild_id, channel_id) — used by the logging cog.
log_channel_limiter = RateLimiter(rate=4, per=5.0)

# One bucket per guild — used for welcome messages and similar
# "join-time" channel sends so a raid can't spam the welcome channel.
welcome_limiter = RateLimiter(rate=3, per=5.0)

# One bucket per guild — used by autorole assignment so a join wave
# doesn't burn through the guild's role-edit budget.
role_assign_limiter = RateLimiter(rate=5, per=5.0)
