"""The public force-update entry point.

Beta triggers this route on the supervisor itself, not on the dashboard child:
that is what makes it usable while the dashboard is down.  The update still runs
in the bot child, which is the only process that owns the modules.
"""

from __future__ import annotations

import time
from pathlib import Path

SECRET = "test-force-update-token"


def test_force_update_is_hidden_without_a_configured_token(supervisor):
    handle = supervisor("normal", env={"BETA_UPDATE_TOKEN": ""})
    handle.wait_ready()

    response = handle.request(
        "/supervisor/update",
        method="POST",
        json={"areas": ["website"]},
        headers={"X-Update-Token": SECRET},
    )
    assert response.status_code == 404


def test_force_update_rejects_a_wrong_token(supervisor):
    handle = supervisor("normal", env={"BETA_UPDATE_TOKEN": SECRET})
    handle.wait_ready()

    response = handle.request(
        "/supervisor/update",
        method="POST",
        json={"areas": ["website"]},
        headers={"X-Update-Token": f"{SECRET}-wrong"},
    )
    assert response.status_code == 404


def test_force_update_forwards_to_the_bot_child(supervisor):
    handle = supervisor("normal", env={"BETA_UPDATE_TOKEN": SECRET})
    handle.wait_ready()

    response = handle.request(
        "/supervisor/update",
        method="POST",
        json={"areas": ["website", "cogs"]},
        headers={"X-Update-Token": SECRET},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["areas"] == ["website", "cogs"]
    assert payload["supervisor_token"] is True


def test_force_update_works_when_the_dashboard_child_is_down(supervisor, tmp_path):
    """The recovery property: a dead web child cannot hide the supervisor route."""
    missing_web = Path(tmp_path) / "missing_web_child.py"
    handle = supervisor(
        args=["--split-web", "--web-child", str(missing_web)],
        env={"BETA_UPDATE_TOKEN": SECRET},
    )
    handle.wait_status(
        lambda payload: bool(
            (payload.get("children", {}).get("bot") or {}).get("ready")
        ),
        timeout=15,
    )
    # The primary web child cannot be ready, so /ready stays 503; the force route
    # is independent of it.
    assert handle.request("/ready").status_code == 503

    response = handle.request(
        "/supervisor/update",
        method="POST",
        json={"areas": ["website"]},
        headers={"X-Update-Token": SECRET},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json()["areas"] == ["website"]


def test_force_update_reports_a_bot_that_is_not_ready(supervisor):
    handle = supervisor(
        "hang-before-api",
        env={"BETA_UPDATE_TOKEN": SECRET},
        startup_timeout=30,
        heartbeat_timeout=30,
    )
    # The child has reported process_started but has no API port yet.
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if handle.status()["children"]["bot"].get("state") == "starting":
            break
        time.sleep(0.05)
    response = handle.request(
        "/supervisor/update",
        method="POST",
        json={"areas": ["website"]},
        headers={"X-Update-Token": SECRET},
    )
    assert response.status_code == 503
    assert "not ready" in response.json()["error"]
