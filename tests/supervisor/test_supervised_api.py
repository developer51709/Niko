from __future__ import annotations

import os
import signal
import time
from pathlib import Path

import psutil
import requests

ROOT = Path(__file__).resolve().parents[2]
API_CHILD = ROOT / "tests" / "supervisor" / "supervised_api_child.py"


def _start(supervisor, **overrides):
    return supervisor(
        "normal",
        startup_timeout=30.0,
        heartbeat_timeout=5.0,
        shutdown_timeout=5.0,
        args=["--child", str(API_CHILD)],
        **overrides,
    )


def test_real_flask_api_runs_on_loopback_behind_the_supervisor(supervisor, tmp_path):
    handle = _start(supervisor)
    payload = handle.wait_ready(timeout=35)

    assert handle.port is not None
    assert payload["child"]["api_port"] != handle.port

    # ``/health`` belongs to the supervisor itself; ``/api/health`` proves the
    # request reached the child's real Flask app through the proxy.
    response = handle.request("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["service"] == "niko-api"
    assert "static_build" in body


def test_supervised_restart_replaces_the_child_cleanly(supervisor):
    handle = _start(supervisor)
    first = handle.wait_ready(timeout=35)
    old_pid = first["child"]["pid"]

    accepted = handle.control("restart", delay=0.1, reason="test restart")
    assert accepted["ok"] is True

    second = handle.wait_for_new_child(old_pid, timeout=35)
    assert second["child"]["pid"] != old_pid
    handle.wait_ready(timeout=35)
    assert handle.request("/health").status_code == 200


def test_the_real_api_child_recovers_from_a_sigkill(supervisor):
    handle = _start(supervisor, backoff_initial=0.5, backoff_max=0.5)
    first = handle.wait_ready(timeout=35)
    old_pid = first["child"]["pid"]

    os.kill(old_pid, signal.SIGKILL)

    # The real child's Flask app has no replacement until the supervisor boots
    # one, so the proxy must answer a bounded 503 instead of hanging.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        started = time.monotonic()
        try:
            response = handle.request("/api/health", timeout=5)
        except requests.RequestException:
            time.sleep(0.05)
            continue
        if response.status_code == 503:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("the proxy never reported the missing real child")

    assert time.monotonic() - started < 2.0
    assert response.json()["retry_after"] == 1

    replacement = handle.wait_for_new_child(old_pid, timeout=35)
    assert replacement["child"]["pid"] != old_pid
    handle.wait_ready(timeout=35)
    recovered = handle.request("/api/health")
    assert recovered.status_code == 200
    assert recovered.json()["ok"] is True
    assert not psutil.pid_exists(old_pid)
