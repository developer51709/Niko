"""Part 2 gate: SIGKILL the child at every boot stage and prove recovery.

Each stage is the point where the supervisor has just been told that stage is
reached. The fake child is held there, so the kill lands deterministically, and
only the first child holds — the replacement boots normally. Throughout, the
supervisor's public socket must stay up, ``/ready`` must report the truth, and
the proxy must answer a bounded 503 rather than hang.
"""

from __future__ import annotations

import os
import signal
import time
from pathlib import Path

import psutil
import pytest

STAGES = (
    "process_started",
    "api_listening",
    "db_ready",
    "cogs_loaded",
    "gateway_ready",
    "ready",
)


def _wait_path(path: Path, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.01)
    raise AssertionError(f"the child never reported {path.name}")


@pytest.mark.parametrize("stage", STAGES)
def test_killing_the_child_at_a_boot_stage_recovers(supervisor, tmp_path, stage):
    marker_dir = tmp_path / f"stages-{stage}"
    hold_marker = tmp_path / f"held-{stage}"
    handle = supervisor(
        "normal",
        startup_timeout=20.0,
        heartbeat_timeout=5.0,
        shutdown_timeout=2.0,
        # A visible restart window: long enough to observe the bounded 503,
        # short enough that recovery stays quick.
        backoff_initial=1.0,
        backoff_max=1.0,
        env={
            "FAKE_CHILD_STAGE_MARKER": str(marker_dir),
            "FAKE_CHILD_STAGE_HOLD": stage,
            "FAKE_CHILD_STAGE_HOLD_ONCE": str(hold_marker),
        },
    )
    _wait_path(marker_dir / stage)
    first = handle.wait_for_child(timeout=15)
    old_pid = first["child"]["pid"]

    if stage == "ready":
        handle.wait_ready(timeout=20)
        assert handle.status()["child"]["ready"] is True
    else:
        assert handle.status()["child"]["ready"] is False

    # The public surface is up while the child has not finished booting.
    assert handle.request("/health").status_code == 200
    if stage == "ready":
        assert handle.request("/ready").status_code == 200
        assert handle.request("/echo").status_code == 200
    else:
        assert handle.request("/ready").status_code == 503
        if stage == "process_started":
            # Nothing is listening yet, so the proxy answers immediately.
            started = time.monotonic()
            response = handle.request("/echo", timeout=5)
            assert time.monotonic() - started < 2.0
            assert response.status_code == 503
            assert response.json()["retry_after"] == 1

    os.kill(old_pid, signal.SIGKILL)

    # While there is no child, the dashboard gets a bounded maintenance answer.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        started = time.monotonic()
        response = handle.request("/echo", timeout=5)
        elapsed = time.monotonic() - started
        if response.status_code == 503:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("the proxy never reported the missing child")

    assert elapsed < 2.0, f"the proxy took {elapsed:.2f}s without a child"
    assert response.json()["retry_after"] == 1
    assert response.json()["error"] == "service unavailable"
    assert handle.request("/ready").status_code == 503
    assert handle.request("/health").status_code == 200

    # The replacement boots normally (only the first child held) and serves.
    replacement = handle.wait_for_new_child(old_pid, timeout=20)
    assert replacement["child"]["pid"] != old_pid
    handle.wait_ready(timeout=20)
    final = handle.status()
    assert final["child_starts"] >= 2
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 200
    assert handle.request("/echo").status_code == 200
    assert not psutil.pid_exists(old_pid)
