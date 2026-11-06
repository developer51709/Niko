"""The heartbeat clock the watchdog measures and the events that feed it."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from supervisor import Child, Options, Supervisor  # noqa: E402


class _Proc:
    pid = 4242


def _supervisor(tmp_path: Path) -> Supervisor:
    options = Options(
        status_file=tmp_path / "supervisor.json",
        control_socket=tmp_path / "supervisor.sock",
        lock_file=tmp_path / "supervisor.lock",
        pending_update_file=tmp_path / "pending.json",
        update_root=tmp_path,
    )
    return Supervisor(options)


def _child(supervisor: Supervisor) -> Child:
    child = Child(
        proc=_Proc(),  # type: ignore[arg-type]
        reader=None,  # type: ignore[arg-type]
        writer=None,  # type: ignore[arg-type]
        started_at=time.monotonic(),
        name="bot",
    )
    supervisor._children["bot"] = child
    return child


def test_default_timeouts_tolerate_a_slow_shared_host():
    """Render's shared CPU can stall a child for seconds at a time.

    A 12s heartbeat window replaced a bot that had just come online, and the
    60s startup window replaced healthy cold boots, so both defaults must stay
    generous enough for a slow shared host.
    """
    options = Options()

    assert options.startup_timeout >= 600.0
    assert options.heartbeat_timeout >= 45.0
    assert options.ready_grace >= 900.0


def test_a_ready_event_refreshes_the_heartbeat_clock(tmp_path):
    """A child that reports ready after a startup stall is not killed at once.

    Render's cold start blocks the bot's event loop for longer than the
    heartbeat window, so the last heartbeat is already stale when ``ready``
    arrives.  The watchdog must measure from the ready event, otherwise the
    kill/restart loop repeats forever.
    """
    supervisor = _supervisor(tmp_path)
    child = _child(supervisor)
    child.last_heartbeat = time.monotonic() - 90

    asyncio.run(supervisor._handle_child_event(child, {"event": "ready"}))

    assert child.ready is True
    assert child.last_heartbeat == child.last_event_at
    assert time.monotonic() - child.last_heartbeat < 1
