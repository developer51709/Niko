"""Integration: the real dashboard child under the supervisor, next to a bot child.

The bot side is the fake child, so the test needs no Discord token.  It still
exercises the real entry point, the supervisor's child environment, the
forwarding bridge, and the owner console served locally.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAKE_CHILD = Path(__file__).resolve().parent / "fake_child.py"
WEB_CHILD = ROOT / "src" / "web_child.py"

SPLIT_ARGS = ["--split-web", "--web-child", str(WEB_CHILD)]


def _both_ready(payload: dict) -> bool:
    children = payload.get("children") or {}
    return bool(children) and all(item.get("ready") for item in children.values())


def test_the_real_dashboard_child_serves_pages_and_forwards_live_api(supervisor):
    handle = supervisor(
        args=SPLIT_ARGS,
        startup_timeout=60.0,
        heartbeat_timeout=15.0,
    )
    status = handle.wait_status(_both_ready, timeout=60)
    assert status["child"]["name"] == "web"
    assert status["children"]["web"]["primary"] is True

    shell = handle.request("/", timeout=15)
    assert shell.status_code == 200
    assert "<!doctype html" in shell.text.lower()
    # Answered by the dashboard child itself, not forwarded.
    assert not shell.headers.get("X-Fake-Child")

    # A live-bot route reaches the bot child's API.
    forwarded = handle.request("/api/echo", timeout=15)
    assert forwarded.headers.get("X-Fake-Child") == "bot"

    # The owner console stays local so it survives the bot restarting.
    console = handle.request("/api/owner/logs", timeout=15)
    assert console.status_code == 401
    assert not console.headers.get("X-Fake-Child")
