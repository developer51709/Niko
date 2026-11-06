"""The dashboard's bot identity: navbar config and favicon data.

The split dashboard child has no gateway, so its public config used to report a
null avatar and the favicon fell back to the build's static icon. These tests
pin the live-user path, the bot-child lookup, and the startup-file fallback.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import config as webapp_config  # noqa: E402
from webapp import runtime, social  # noqa: E402
from webapp.routes import public_routes  # noqa: E402
from webapp.server import app  # noqa: E402


def _user(**overrides):
    values = {
        "display_avatar": SimpleNamespace(url="https://cdn.discordapp.com/avatars/1/niko.png"),
        "name": "Niko",
        "display_name": "Niko",
        "discriminator": "0",
        "public_flags": SimpleNamespace(value=1 << 16),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_a_live_gateway_reads_the_identity_off_its_user(monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", SimpleNamespace(user=_user()))

    identity = runtime.public_bot_identity()

    assert identity["bot_avatar_url"] == "https://cdn.discordapp.com/avatars/1/niko.png"
    assert identity["bot_name"] == "Niko"
    assert identity["bot_display_name"] == "Niko"
    assert identity["bot_verified"] is True


def test_the_dashboard_child_asks_the_bot_child_for_the_identity(monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", None)
    monkeypatch.setattr(runtime, "_identity_cache", None)
    monkeypatch.setattr(runtime, "_identity_route", None)
    monkeypatch.setenv("NIKO_SUPERVISED", "1")
    monkeypatch.setitem(
        sys.modules,
        "web_bridge",
        SimpleNamespace(BotRoute=lambda: SimpleNamespace(port=lambda: 4567)),
    )

    seen = {}

    def fake_get(url, timeout):
        seen["url"] = url
        seen["timeout"] = timeout
        return SimpleNamespace(
            status_code=200,
            json=lambda: {
                "bot_avatar_url": "https://cdn.discordapp.com/avatars/2/niko.png",
                "bot_name": "Niko",
                "bot_verified": True,
            },
        )

    monkeypatch.setattr("requests.get", fake_get)

    identity = runtime.public_bot_identity()

    assert seen["url"] == "http://127.0.0.1:4567/api/config"
    assert identity["bot_avatar_url"].endswith("/2/niko.png")
    assert identity["bot_verified"] is True


def test_the_startup_record_is_the_fallback_while_the_bot_restarts(monkeypatch, tmp_path):
    stats = tmp_path / "bot_stats.json"
    stats.write_text(
        '{"bot_avatar_url": "https://cdn.discordapp.com/avatars/3/niko.png",'
        ' "bot_name": "Niko", "bot_display_name": "Niko"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(webapp_config, "BOT_STATS", str(stats))
    monkeypatch.setattr(runtime, "_discord_bot", None)
    monkeypatch.setattr(runtime, "_identity_cache", None)
    monkeypatch.setattr(runtime, "_identity_from_bot_child", lambda: {})

    identity = runtime.public_bot_identity()

    assert identity["bot_avatar_url"].endswith("/3/niko.png")
    assert identity["bot_name"] == "Niko"


def test_public_config_and_the_preview_avatar_use_that_identity(monkeypatch):
    identity = {
        "bot_avatar_url": "https://cdn.discordapp.com/avatars/4/niko.png",
        "bot_name": "Niko",
        "bot_display_name": "Niko",
        "bot_discriminator": "0",
        "bot_verified": True,
    }
    monkeypatch.setattr(runtime, "public_bot_identity", lambda: identity)
    monkeypatch.setattr(public_routes, "_discord_bot", None)

    response = app.test_client().get("/api/config")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["bot_avatar_url"] == identity["bot_avatar_url"]
    assert payload["bot_verified"] is True
    assert social._bot_avatar_url() == identity["bot_avatar_url"]
