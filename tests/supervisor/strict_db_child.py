"""Harness child: the real database bootstrap under ``NIKO_STRICT_DB``.

MongoDB is simulated as unreachable by replacing the connector, so no network
or external database is involved. The point is the production code path: the
child must fail instead of creating a local SQLite file, and the supervisor must
stop restarting it once the budget is spent.
"""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import database  # noqa: E402
from supervisor_protocol import ChildReporter, install_parent_death_signal  # noqa: E402


def _install_unreachable_motor() -> None:
    module = types.ModuleType("motor.motor_asyncio")

    def down(*_args, **_kwargs):
        raise RuntimeError("simulated MongoDB outage")

    module.AsyncIOMotorClient = down  # type: ignore[attr-defined]
    sys.modules["motor"] = types.ModuleType("motor")
    sys.modules["motor.motor_asyncio"] = module


async def _main() -> int:
    reporter = ChildReporter.from_environment()
    install_parent_death_signal()
    reporter.send("process_started")

    _install_unreachable_motor()
    # The three retry sleeps are not what this drill is about.
    database.asyncio = types.SimpleNamespace(sleep=lambda _seconds: asyncio.sleep(0))

    try:
        await database.create_pool(sys.argv[1])
    except Exception as exc:
        reporter.send("error", reason=f"{type(exc).__name__}: {exc}")
        reporter.send("stopped")
        reporter.close()
        return 1

    reporter.send("ready", reason="strict database unexpectedly succeeded")
    reporter.send("stopped")
    reporter.close()
    return 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
