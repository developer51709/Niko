"""Part 4: the dashboard and the bot run as independent children.

These tests use the fake child for both roles.  It reports the same lifecycle
protocol and serves HTTP with an ``X-Fake-Child`` header, so the proxy can be
asked which child answered without a real Discord token.
"""

from __future__ import annotations

import json
import os
import signal
import time
from pathlib import Path

FAKE_CHILD = Path(__file__).resolve().parent / "fake_child.py"
SPLIT_ARGS = ["--split-web", "--web-child", str(FAKE_CHILD)]


def _both_ready(payload: dict) -> bool:
    children = payload.get("children") or {}
    return bool(children) and all(item.get("ready") for item in children.values())


def test_both_children_boot_and_the_public_port_uses_the_dashboard(supervisor):
    handle = supervisor(args=SPLIT_ARGS)
    status = handle.wait_status(_both_ready, timeout=20)

    assert status["split_web"] is True
    assert set(status["children"]) == {"web", "bot"}
    assert status["children"]["web"]["primary"] is True
    assert status["child"]["name"] == "web"

    public = handle.request("/")
    assert public.headers.get("X-Fake-Child") == "web"
    # Interactions skip the dashboard and reach the gateway child directly.
    interaction = handle.request("/api/discord/interactions")
    assert interaction.headers.get("X-Fake-Child") == "bot"

    assert handle.request("/health").status_code == 200
    assert handle.request("/ready").status_code == 200


def test_restarting_the_dashboard_leaves_the_bot_untouched(supervisor):
    handle = supervisor(args=SPLIT_ARGS)
    status = handle.wait_status(_both_ready, timeout=20)
    web_pid = status["children"]["web"]["pid"]
    bot_pid = status["children"]["bot"]["pid"]

    answer = handle.control("restart", child="web", delay=0.0, reason="dashboard update")
    assert answer["ok"] is True
    assert answer["children"] == ["web"]

    replaced = handle.wait_status(
        lambda payload: payload["children"]["web"].get("pid") not in (None, web_pid)
        and payload["children"]["web"].get("ready"),
        timeout=20,
    )
    assert replaced["children"]["bot"]["pid"] == bot_pid
    assert replaced["children"]["bot"]["ready"] is True


def test_a_bot_crash_leaves_the_dashboard_ready(supervisor):
    handle = supervisor(args=SPLIT_ARGS)
    status = handle.wait_status(_both_ready, timeout=20)
    web_pid = status["children"]["web"]["pid"]
    bot_pid = status["children"]["bot"]["pid"]

    os.kill(bot_pid, signal.SIGKILL)

    restarted = handle.wait_status(
        lambda payload: payload["children"]["bot"].get("pid") not in (None, bot_pid)
        and payload["children"]["bot"].get("ready"),
        timeout=20,
    )
    assert restarted["children"]["web"]["pid"] == web_pid
    assert restarted["children"]["web"]["ready"] is True
    # The dashboard is the public surface, so the service stays ready while the
    # bot child is replaced.
    assert handle.request("/ready").status_code == 200
    assert handle.request("/").headers.get("X-Fake-Child") == "web"


def test_database_child_runs_beside_the_bot_and_reports_its_port(supervisor):
    """The bot child gets the database child's loopback port, and restarts of
    one never touch the other."""
    handle = supervisor(
        args=["--no-split-web", "--split-db", "--db-child", str(FAKE_CHILD)]
    )
    status = handle.wait_status(_both_ready, timeout=20)

    assert set(status["children"]) == {"db", "bot"}
    assert status["children"]["db"]["primary"] is False
    assert status["children"]["bot"]["primary"] is True

    route = handle.control("route")
    assert route["split_db"] is True
    assert route["db_api_port"] == status["children"]["db"]["api_port"]

    db_pid = status["children"]["db"]["pid"]
    bot_pid = status["children"]["bot"]["pid"]
    answer = handle.control("restart", child="db", delay=0.0, reason="database test")
    assert answer["ok"] is True
    assert answer["children"] == ["db"]

    replaced = handle.wait_status(
        lambda payload: payload["children"]["db"].get("pid") not in (None, db_pid)
        and payload["children"]["db"].get("ready"),
        timeout=20,
    )
    assert replaced["children"]["bot"]["pid"] == bot_pid
    # The control route follows the replaced child, not the old port.
    assert handle.control("route")["db_api_port"] == replaced["children"]["db"]["api_port"]


def test_supervisor_lines_are_written_to_the_shared_console(supervisor):
    handle = supervisor(args=SPLIT_ARGS)
    handle.wait_status(_both_ready, timeout=20)

    store = handle.run_dir / "logs"
    deadline = time.monotonic() + 10
    entries: list[dict] = []
    while time.monotonic() < deadline:
        try:
            entries = [
                json.loads(line)
                for path in store.glob("*/*.jsonl")
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except FileNotFoundError:
            entries = []
        if any(entry.get("process") == "supervisor" for entry in entries):
            break
        time.sleep(0.05)

    supervisor_lines = [entry for entry in entries if entry.get("process") == "supervisor"]
    assert supervisor_lines, "the supervisor wrote nothing to the shared console"
    assert all("line" in entry and "level" in entry for entry in supervisor_lines)
    # Child stdout is not duplicated: its structured records are the only copy.
    assert not any(
        str(entry.get("line", "")).startswith("[child:")
        for entry in supervisor_lines
    )
