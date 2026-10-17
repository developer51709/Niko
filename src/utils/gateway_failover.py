"""Reversible gateway gate for preloaded production and standby bots."""

from __future__ import annotations

import asyncio


class GatewayHandoff:
    """Run one bot's gateway only while it owns the active role.

    discord.py's public ``close`` also closes the HTTP client and permanently
    marks the bot closed. A handoff ends only the current ``connect`` cycle,
    closes each shard connection, and leaves the authenticated HTTP client and
    loaded cogs available for the next activation.
    """

    def __init__(self, bot, *, active: bool = False):
        self.bot = bot
        self.active = asyncio.Event()
        self.connected = asyncio.Event()
        self.stopping = False
        self.refresh_caches_on_ready = False
        self._cycle: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        if active:
            self.active.set()

    def mark_connected(self) -> None:
        """Signal that this owner completed its first gateway-ready work."""
        self.connected.set()

    async def run(self) -> None:
        """Wait for ownership and run gateway connect cycles."""
        while not self.stopping:
            if not self.active.is_set():
                await self.active.wait()
                continue
            self._cycle = asyncio.create_task(self.bot.connect(reconnect=True))
            try:
                await self._cycle
            except asyncio.CancelledError:
                if self.stopping:
                    raise
                if self.active.is_set():
                    raise
            except Exception:
                if self.active.is_set() and not self.stopping:
                    raise
            finally:
                self._cycle = None
            if not self.active.is_set() and not self.stopping:
                continue
            if not self.stopping:
                await asyncio.sleep(1)

    async def activate(self) -> None:
        """Claim the gateway after the previous owner has relinquished it."""
        async with self._lock:
            if self.stopping:
                raise RuntimeError("Gateway controller is shutting down.")
            self.connected.clear()
            self.refresh_caches_on_ready = True
            self.active.set()

    async def relinquish(self) -> bool:
        """Disconnect shards and wait until this process no longer owns them."""
        async with self._lock:
            self.active.clear()
            cycle = self._cycle
            if cycle is not None and not cycle.done() and asyncio.current_task() is not cycle:
                cycle.cancel()
                try:
                    await asyncio.wait_for(asyncio.gather(cycle, return_exceptions=True), timeout=10)
                except asyncio.TimeoutError as exc:
                    raise RuntimeError("Gateway supervisor did not stop within 10 seconds.") from exc
            shards = getattr(self.bot, "_AutoShardedClient__shards", {})
            if shards:
                await asyncio.gather(*(shard.close() for shard in tuple(shards.values())))
                shards.clear()
            return bool(cycle is not None and cycle.done() and cycle.cancelled())

    async def shutdown(self) -> None:
        """Stop the supervisor and close any owned shards without closing HTTP."""
        self.stopping = True
        await self.relinquish()
