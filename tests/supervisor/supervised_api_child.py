"""Part 2 harness: a supervised child around the real Flask API server.

It has no Discord gateway, but it exercises the production API module, the
inherited lifecycle socket, the ephemeral loopback bind, and the supervisor's
reverse proxy.  The real bot uses the same ``api_server.start_api_server`` call
with ``host="127.0.0.1"`` and ``port=0``.
"""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import api_server  # noqa: E402
from supervisor_protocol import ChildReporter, install_parent_death_signal  # noqa: E402


async def _main() -> None:
    reporter = ChildReporter.from_environment()
    install_parent_death_signal()
    reporter.send("process_started")

    api_server.start_api_server(None, host="127.0.0.1", port=0)
    port = api_server.listening_port()
    reporter.send("api_listening", host="127.0.0.1", port=port)
    reporter.send("db_ready", backend="harness")
    reporter.send("cogs_loaded", total=0, failed=0)
    reporter.send("gateway_ready", shard_count=1, ready_shards=1)
    reporter.send("ready", reason="harness API ready")

    draining = asyncio.Event()
    loop = asyncio.get_running_loop()

    def stop() -> None:
        if not draining.is_set():
            reporter.send("draining", reason="SIGTERM")
            draining.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop)
        except NotImplementedError:
            pass

    async def heartbeat() -> None:
        while not draining.is_set():
            await asyncio.sleep(0.5)
            if not reporter.heartbeat():
                return

    heartbeat_task = asyncio.create_task(heartbeat(), name="harness-heartbeat")
    try:
        await draining.wait()
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        api_server.stop_api_server()
        reporter.send("stopped")
        reporter.close()


if __name__ == "__main__":
    asyncio.run(_main())
