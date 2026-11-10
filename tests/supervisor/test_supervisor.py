from __future__ import annotations

import asyncio
import os
import signal
import stat
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import psutil
import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from supervisor import Child, Options, Supervisor  # noqa: E402
from supervisor_protocol import CONTROL_SOCKET_ENV  # noqa: E402


def test_child_environment_carries_the_control_socket_path(tmp_path):
    options = Options(control_socket=tmp_path / "supervisor.sock")
    supervisor = Supervisor(options)

    env = supervisor._child_environment(9)

    assert env[CONTROL_SOCKET_ENV] == str(options.control_socket.resolve())
    assert env["NIKO_SUPERVISED"] == "1"
    assert "PORT" not in env


def _child(name: str, port: int | None, **fields) -> Child:
    return Child(
        proc=SimpleNamespace(pid=1),
        reader=None,
        writer=None,
        started_at=time.monotonic(),
        name=name,
        api_port=port,
        **fields,
    )


def test_a_child_that_is_being_replaced_does_not_lend_its_port(tmp_path):
    """An update restarts the bot and the database child in one request.

    The replacement bot boots while the old database child is still shutting
    down.  Handing it that port would attach the new bot to a child that is
    about to exit, and the update would be confirmed on a database that is
    already gone.
    """
    supervisor = Supervisor(
        Options(control_socket=tmp_path / "supervisor.sock", split_web=True, split_db=True)
    )
    db = _child("db", 4567)
    supervisor._children["db"] = db

    assert supervisor._live_api_port("db") == 4567

    # Marked before any target is stopped, so it is never offered again.
    db.restart_requested = True
    assert supervisor._live_api_port("db") is None

    db.restart_requested = False
    db.exit_event.set()
    assert supervisor._live_api_port("db") is None


def test_a_multi_child_restart_marks_every_target_before_stopping_any(tmp_path):
    async def scenario():
        supervisor = Supervisor(
            Options(control_socket=tmp_path / "supervisor.sock", split_web=True, split_db=True)
        )
        supervisor._children["bot"] = _child("bot", 1111)
        supervisor._children["db"] = _child("db", 2222)
        stopped = []

        async def fake_terminate(child, reason):
            # By the time the first child is stopped, the sibling must already
            # be marked as going away or a boot in between could use its port.
            stopped.append(child.name)
            assert all(instance.restart_requested for instance in supervisor._children.values())

        supervisor._terminate_child = fake_terminate  # type: ignore[method-assign]
        supervisor._request_restart(
            0.0,
            "update",
            [supervisor._slots["bot"], supervisor._slots["db"]],
        )
        await asyncio.sleep(0.05)
        return stopped

    assert asyncio.run(scenario()) == ["bot", "db"]


def test_a_booting_bot_does_not_inherit_a_dying_database_port(tmp_path):
    options = Options(
        control_socket=tmp_path / "supervisor.sock", split_web=True, split_db=True
    )
    supervisor = Supervisor(options)
    supervisor._children["db"] = _child("db", 4567, restart_requested=True)

    env = supervisor._child_environment(9, supervisor._slots["bot"])

    assert "NIKO_DB_API_PORT" not in env


def test_health_and_readiness_are_separate(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()

    health = handle.request("/health")
    ready = handle.request("/ready")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json()["ready"] is True

    status = handle.status()
    assert status["state"] == "active"
    assert status["child"]["ready"] is True
    assert status["child"]["api_port"]


def test_health_stays_available_while_the_child_restarts(supervisor):
    handle = supervisor(
        "normal",
        env={"FAKE_CHILD_BOOT_DELAY": "0.4"},
    )
    handle.wait_ready()
    old_pid = handle.status()["child"]["pid"]

    reply = handle.control("restart", reason="test restart")
    assert reply["ok"] is True

    handle.wait_status(
        lambda payload: payload["state"] == "starting"
        and (payload["child"] is None or not payload["child"]["ready"]),
        timeout=5,
    )
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 503

    new_status = handle.wait_for_new_child(old_pid, timeout=10)
    assert new_status["child"]["pid"] != old_pid
    handle.wait_ready()
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 200
    final_status = handle.status()
    assert final_status["child_starts"] >= 2
    # A draining long-running child must not be recorded as a startup timeout.
    assert final_status["last_error"] is None


def test_a_crash_is_restarted_without_losing_the_public_server(supervisor):
    marker = Path("/tmp") / f"niko-supervisor-crash-{os.getpid()}-{time.time_ns()}"
    marker.unlink(missing_ok=True)
    handle = supervisor(
        "normal",
        env={
            "FAKE_CHILD_CRASH_ONCE": str(marker),
            "FAKE_CHILD_READY_DELAY": "0.05",
        },
    )
    first = handle.wait_for_child(timeout=5)
    first_status = handle.wait_status(
        lambda payload: payload["child"] is None
        or payload["child"]["pid"] != first["child"]["pid"],
        timeout=10,
    )
    assert first_status["restart_count"] >= 1
    assert handle.request("/health").status_code == 200
    handle.wait_ready()
    assert handle.status()["child_starts"] >= 2
    marker.unlink(missing_ok=True)


def test_a_child_that_closes_its_channel_and_exits_is_not_killed(supervisor):
    """A shutting-down child closes its channel before its process is gone.

    A host that stops the container, or a deploy restart, sends SIGTERM to the
    children directly: the reporter closes, the child drains for a moment and
    the process exits.  Killing it on the closed channel blamed the supervisor
    for a process that was already leaving and charged the restart budget with
    a stop the supervisor never asked for.
    """
    handle = supervisor(
        "close-channel",
        shutdown_timeout=3.0,
        env={"FAKE_CHILD_CLOSE_EXIT_AFTER": "0.4"},
    )
    handle.wait_ready()
    old_pid = handle.status()["child"]["pid"]

    restarted = handle.wait_for_new_child(old_pid, timeout=10)
    assert restarted["child_starts"] >= 2
    final = handle.status()
    # The child exited by itself, so no stop reason may name the channel close
    # as a supervisor-initiated stop.
    assert final["last_stop_reason"] == "child exit"
    handle.wait_ready()


def test_a_child_that_keeps_running_without_a_channel_is_replaced(supervisor):
    """A live process with no lifecycle channel cannot be supervised."""
    close_once = Path("/tmp") / f"niko-supervisor-close-{os.getpid()}-{time.time_ns()}"
    close_once.unlink(missing_ok=True)
    handle = supervisor(
        "close-channel",
        shutdown_timeout=0.5,
        env={"FAKE_CHILD_CLOSE_ONCE": str(close_once)},
    )
    handle.wait_ready()
    old_pid = handle.status()["child"]["pid"]

    restarted = handle.wait_for_new_child(old_pid, timeout=10)
    assert restarted["child_starts"] >= 2
    assert handle.status()["last_stop_reason"] == "control channel closed"
    handle.wait_ready()
    close_once.unlink(missing_ok=True)


def test_health_stays_available_while_the_child_hangs_before_listening(supervisor):
    handle = supervisor(
        "hang-before-api",
        startup_timeout=0.5,
        heartbeat_timeout=2.0,
        backoff_initial=0.2,
        backoff_max=0.2,
    )
    status = handle.wait_for_child(timeout=5)
    assert status["child"]["ready"] is False
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 503

    handle.wait_status(lambda payload: payload["restart_count"] >= 1, timeout=5)
    assert handle.request("/health").status_code == 200


def test_readiness_failure_is_replaced_while_health_stays_up(supervisor):
    handle = supervisor(
        "fail-readiness",
        shutdown_timeout=0.2,
        backoff_initial=0.2,
        backoff_max=0.2,
    )
    handle.wait_for_child(timeout=5)
    status = handle.wait_status(lambda payload: payload["restart_count"] >= 1, timeout=8)
    assert status["last_error"]
    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 503


def test_heartbeat_timeout_replaces_a_hung_child(supervisor):
    handle = supervisor(
        "hang-after-ready",
        heartbeat_timeout=0.4,
        startup_timeout=3.0,
    )
    handle.wait_ready()
    first_pid = handle.status()["child"]["pid"]

    handle.wait_status(
        lambda payload: payload["restart_count"] >= 1,
        timeout=8,
    )
    assert handle.request("/health").status_code == 200
    new_status = handle.wait_status(
        lambda payload: bool(payload["child"]) and payload["child"]["pid"] != first_pid,
        timeout=8,
    )
    assert new_status["child_starts"] >= 2


def test_a_starting_child_is_not_expected_to_send_heartbeats(supervisor):
    """Boot is bounded by the startup window, not by the heartbeat clock.

    The child sends no heartbeats until it reports ready, and startup work can
    hold that back for minutes on a slow host.  A short heartbeat timeout must
    not replace it while it is still starting.
    """
    handle = supervisor(
        "normal",
        env={"FAKE_CHILD_READY_DELAY": "1.2"},
        heartbeat_timeout=0.3,
        startup_timeout=5.0,
    )
    payload = handle.wait_ready(timeout=10)

    assert payload["restart_count"] == 0
    assert payload["child_starts"] == 1


def test_a_ready_child_settles_for_the_grace_window_before_heartbeats_count(supervisor):
    """A slow host gets time to finish booting after its first ready.

    The child stops heartbeating as soon as it reports ready, which is what a
    throttled Render container looks like while its startup chain still runs.
    It must survive until the grace window expires, then be replaced.
    """
    handle = supervisor(
        "hang-after-ready",
        heartbeat_timeout=0.3,
        ready_grace=1.5,
        startup_timeout=5.0,
    )
    handle.wait_ready()
    first_pid = handle.status()["child"]["pid"]

    time.sleep(0.7)
    assert handle.status()["child"]["pid"] == first_pid
    assert handle.status()["restart_count"] == 0

    new_status = handle.wait_status(
        lambda payload: bool(payload["child"]) and payload["child"]["pid"] != first_pid,
        timeout=8,
    )
    assert new_status["restart_count"] >= 1


def test_ignore_sigterm_child_is_escalated_and_replaced(supervisor):
    handle = supervisor(
        "ignore-sigterm",
        shutdown_timeout=0.2,
    )
    handle.wait_ready()
    old_pid = handle.status()["child"]["pid"]
    started = time.monotonic()
    assert handle.control("restart")["ok"] is True
    handle.wait_for_new_child(old_pid, timeout=8)
    handle.wait_ready()
    assert time.monotonic() - started >= 0.2
    assert handle.status()["child_starts"] >= 2


def test_control_socket_is_private_and_rejects_unknown_commands(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()
    mode = stat.S_IMODE(handle.control_path.stat().st_mode)
    assert mode == 0o600

    ping = handle.control("ping")
    assert ping == {"ok": True, "pong": True, "protocol": 1}

    unknown = handle.control("not-a-command")
    assert unknown["ok"] is False
    assert "unknown control command" in unknown["error"]

    # Detailed status is local-control-only by default.
    assert handle.request("/supervisor/status").status_code == 404
    status = handle.control("status")
    assert status["ok"] is True
    assert status["status"]["state"] == "active"


def test_second_supervisor_fails_closed(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()

    duplicate = handle.duplicate()
    assert duplicate.returncode != 0
    assert "another supervisor owns" in duplicate.stderr
    assert handle.request("/health").status_code == 200


def test_proxy_forwards_hosts_and_overwrites_spoofed_forwarding_headers(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()

    response = handle.request(
        "/echo?mode=forwarded",
        headers={
            "Host": "public.example",
            "X-Forwarded-Host": "evil.example",
            "X-Forwarded-For": "203.0.113.9",
            "X-Forwarded-Proto": "https",
        },
    )
    assert response.status_code == 200
    assert response.json()["path"] == "/echo?mode=forwarded"
    echoed = response.json()["headers"]
    assert echoed["Host"] == "public.example"
    assert echoed["X-Forwarded-Host"] == "public.example"
    assert echoed["X-Forwarded-For"] == "127.0.0.1"
    assert echoed["X-Forwarded-Proto"] == "http"


def test_proxy_preserves_cookies_redirects_downloads_ranges_and_uploads(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()

    cookies = handle.request("/cookies")
    assert cookies.status_code == 200
    set_cookies = cookies.raw.headers.getlist("Set-Cookie")
    assert len(set_cookies) == 2
    assert any("first=one" in value for value in set_cookies)
    assert any("second=two" in value for value in set_cookies)

    redirect = handle.request("/redirect", allow_redirects=False)
    assert redirect.status_code == 302
    assert redirect.headers["Location"] == "/landing"

    download = handle.request("/download")
    assert download.status_code == 200
    assert len(download.content) == 40960
    assert download.headers["Content-Type"] == "application/octet-stream"

    ranged = handle.request("/range", headers={"Range": "bytes=10-19"})
    assert ranged.status_code == 206
    assert ranged.headers["Content-Range"] == "bytes 10-19/1024"
    assert len(ranged.content) == 10

    uploaded = handle.request(
        "/upload",
        method="POST",
        files={"file": ("hello.txt", b"hello supervisor", "text/plain")},
    )
    assert uploaded.status_code == 200
    body = uploaded.json()
    assert body["body_length"] > 0
    assert body["headers"]["Content-Type"].startswith("multipart/form-data; boundary=")


def test_proxy_returns_503_when_the_child_is_gone(supervisor):
    handle = supervisor(
        "normal",
        backoff_initial=0.5,
        backoff_max=0.5,
    )
    handle.wait_ready()
    child_pid = handle.status()["child"]["pid"]
    os.kill(child_pid, signal.SIGKILL)

    handle.wait_status(
        lambda payload: payload["child"] is None
        or payload["child"]["pid"] != child_pid,
        timeout=5,
    )
    response = handle.request("/echo")
    assert response.status_code == 503
    assert response.json()["retry_after"] == 1
    assert handle.request("/health").status_code == 200


def test_log_flood_is_drained_without_blocking_the_health_endpoint(supervisor):
    handle = supervisor("normal", env={"FAKE_CHILD_LOG_FLOOD": "1"})
    handle.wait_ready()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        assert handle.request("/health").status_code == 200
        time.sleep(0.05)


def test_sigterm_stops_the_child_and_writes_a_stopped_status(supervisor):
    handle = supervisor("normal")
    handle.wait_ready()
    child_pid = handle.status()["child"]["pid"]

    handle.process.send_signal(signal.SIGTERM)
    assert handle.process.wait(timeout=10) == 0
    assert not psutil.pid_exists(child_pid)

    final = handle.status()
    assert final["state"] == "stopped"
    assert final["child"] is None


def test_sigkill_supervisor_kills_the_whole_child_process_group(supervisor):
    handle = supervisor("leak-child")
    handle.wait_ready()
    child = psutil.Process(handle.status()["child"]["pid"])
    descendants = [child, *child.children(recursive=True)]
    assert descendants

    handle.process.kill()
    handle.process.wait(timeout=5)

    gone, alive = psutil.wait_procs(descendants, timeout=5)
    assert not alive, [process.pid for process in alive]
    assert gone


def test_one_hundred_restarts_do_not_leak_processes_or_descriptors(supervisor):
    handle = supervisor(
        "crash-after-api",
        startup_timeout=1.0,
        backoff_initial=0.001,
        backoff_max=0.002,
    )
    handle.wait_for_child(timeout=5)
    baseline_fds = psutil.Process(handle.pid).num_fds()

    status = handle.wait_status(
        lambda payload: payload.get("child_starts", 0) >= 100,
        timeout=30,
    )
    assert status["restart_count"] >= 99
    after_fds = psutil.Process(handle.pid).num_fds()
    assert after_fds <= baseline_fds + 12

    handle.stop()
    time.sleep(0.2)
    assert handle.descendants() == []


def test_a_child_that_never_boots_backs_off_far_longer_than_a_crash(tmp_path):
    """A boot that never reaches ready is not a transient crash.

    A blocked egress IP (Cloudflare 1015) or a rejected token fails the same way
    on every attempt, so restarting it on the crash schedule only repeats the
    failure, re-sends the blocked login and adds a frame per attempt to the log.
    """
    supervisor = Supervisor(
        Options(control_socket=tmp_path / "supervisor.sock", restart_backoff_max=30.0)
    )
    assert supervisor._restart_ceiling(never_ready=False) == 30.0
    assert supervisor._restart_ceiling(never_ready=True) == 300.0

    # Short test windows stay short: the ceiling is derived from the configured
    # one instead of being a fixed five minutes.
    quick = Supervisor(
        Options(control_socket=tmp_path / "quick.sock", restart_backoff_max=0.05)
    )
    assert quick._restart_ceiling(never_ready=True) == pytest.approx(0.5)

    # A ceiling someone raised above the cap is never lowered by this.
    generous = Supervisor(
        Options(control_socket=tmp_path / "generous.sock", restart_backoff_max=600.0)
    )
    assert generous._restart_ceiling(never_ready=True) == 600.0
