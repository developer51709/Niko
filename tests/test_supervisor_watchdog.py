"""The heartbeat clock the watchdog measures and the events that feed it."""

from __future__ import annotations

import asyncio
import contextlib
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from supervisor import Child, Options, Supervisor  # noqa: E402


class _Proc:
    def __init__(self, pid: int = 4242, returncode: int | None = None) -> None:
        self.pid = pid
        self.returncode = returncode


def _supervisor(tmp_path: Path, **options) -> Supervisor:
    settings = dict(
        status_file=tmp_path / "supervisor.json",
        control_socket=tmp_path / "supervisor.sock",
        lock_file=tmp_path / "supervisor.lock",
        pending_update_file=tmp_path / "pending.json",
        update_root=tmp_path,
    )
    settings.update(options)
    return Supervisor(Options(**settings))


def _child(supervisor: Supervisor, proc: _Proc | None = None) -> Child:
    child = Child(
        proc=proc or _Proc(),  # type: ignore[arg-type]
        reader=None,  # type: ignore[arg-type]
        writer=None,  # type: ignore[arg-type]
        started_at=time.monotonic(),
        name="bot",
    )
    supervisor._children["bot"] = child
    return child


def _live_proc() -> _Proc:
    """A process that really exists: this interpreter."""
    return _Proc(pid=os.getpid())


def _run_watchdog(supervisor: Supervisor, child: Child, seconds: float) -> list[str]:
    """Run the watchdog for a moment, returning the stops it ordered."""
    stops: list[str] = []

    async def fake_terminate(target: Child, reason: str) -> None:
        stops.append(reason)

    supervisor._terminate_child = fake_terminate  # type: ignore[method-assign]

    async def drive() -> None:
        task = asyncio.create_task(supervisor._watchdog(child))
        await asyncio.sleep(seconds)
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    asyncio.run(drive())
    return stops


def test_default_timeouts_tolerate_a_slow_shared_host():
    """Render's shared CPU can stall a child for seconds at a time.

    A 12s heartbeat window replaced a bot that had just come online, and the
    60s startup window replaced healthy cold boots, so both defaults must stay
    generous enough for a slow shared host.
    """
    options = Options()

    assert options.startup_timeout >= 600.0
    assert options.heartbeat_timeout >= 300.0
    assert options.ready_grace >= 900.0
    # The kill window is derived from the report window unless it is spelled
    # out, so the two cannot drift apart in a deployment that tunes only one.
    assert options.stall_timeout == 0.0


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


def test_a_live_child_past_its_heartbeat_window_is_not_stopped(tmp_path):
    """A missed heartbeat must never be read as a closed process.

    A shared container can stop scheduling the child for minutes while the
    process is perfectly healthy.  The supervisor may report the stall, but
    only the process being gone may end it -- so a live pid is left alone even
    though the clock says the heartbeat is late.
    """
    supervisor = _supervisor(
        tmp_path, heartbeat_timeout=0.2, stall_timeout=600.0, ready_grace=0.0
    )
    child = _child(supervisor, _live_proc())
    child.ready = True
    child.ready_at = time.monotonic()
    child.last_heartbeat = time.monotonic() - 30

    stops = _run_watchdog(supervisor, child, 0.6)

    assert stops == []
    assert child.stalled is True
    assert "still running" in (child.last_error or "")


def test_a_resumed_heartbeat_clears_the_stall(tmp_path):
    supervisor = _supervisor(
        tmp_path, heartbeat_timeout=0.2, stall_timeout=600.0, ready_grace=0.0
    )
    child = _child(supervisor, _live_proc())
    child.ready = True
    child.ready_at = time.monotonic()
    child.last_heartbeat = time.monotonic() - 30

    _run_watchdog(supervisor, child, 0.4)
    assert child.stalled is True

    asyncio.run(supervisor._handle_child_event(child, {"event": "heartbeat"}))

    assert child.stalled is False
    assert time.monotonic() - child.last_heartbeat < 1


def test_a_child_whose_process_is_gone_is_never_stopped(tmp_path):
    """An exited process needs no signal; its exit code is the report."""
    supervisor = _supervisor(tmp_path, heartbeat_timeout=0.2, ready_grace=0.0)
    child = _child(supervisor, _Proc(returncode=7))
    child.ready = True
    child.ready_at = time.monotonic()
    child.last_heartbeat = time.monotonic() - 30

    assert _run_watchdog(supervisor, child, 0.5) == []
    assert child.stalled is False


def test_a_still_alive_child_is_replaced_only_after_the_stall_window(tmp_path):
    """A hang is silence for the whole window, not one late heartbeat."""
    supervisor = _supervisor(
        tmp_path, heartbeat_timeout=0.2, stall_timeout=0.6, ready_grace=0.0
    )
    child = _child(supervisor, _live_proc())
    child.ready = True
    child.ready_at = time.monotonic()
    child.last_heartbeat = time.monotonic() - 30

    stops = _run_watchdog(supervisor, child, 1.2)

    assert stops == ["heartbeat stalled"]
    assert "hung" in (supervisor.last_error or "")
