"""Persistent honeypot hits, autobans, and the global IP-ban guard."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, auth  # noqa: E402
from webapp import config as webapp_config, security  # noqa: E402
from webapp.routes import honeypot_routes  # noqa: E402


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(webapp_config, "DATA_DIR", str(tmp_path))
    monkeypatch.delenv("MONGODB_URL", raising=False)
    security.reset()
    yield tmp_path
    security.reset()


def test_hits_are_aggregated_and_survive_a_restart(store):
    first = security.record_hit(
        ip="198.51.100.7",
        path="/.env",
        host="niko.sryze.cc",
        method="GET",
        user_agent="scanner/1.0",
    )
    security.record_hit(ip="198.51.100.7", path="/dump.sql", host="dash.niko.sryze.cc")

    assert first["hit"]["hits"] == 1
    assert first["ban"] is None
    assert not security.is_banned("198.51.100.7")

    # A fresh process (and a fresh cache) reads the same row from the store.
    security.reset()
    snapshot = security.snapshot()
    assert snapshot["error"] is None
    assert snapshot["totals"]["hits"] == 2
    assert snapshot["totals"]["addresses"] == 1
    assert len(snapshot["hits"]) == 1
    hit = snapshot["hits"][0]
    assert hit["ip"] == "198.51.100.7"
    assert hit["hits"] == 2
    assert hit["last_path"] == "/dump.sql"
    assert hit["last_host"] == "dash.niko.sryze.cc"
    assert hit["banned"] is False


def test_autoban_creates_a_ban_after_the_threshold(store):
    security.update_settings({
        "enabled": True,
        "threshold": 2,
        "window_seconds": 300,
        "cooldown_seconds": 600,
    })

    assert security.record_hit(ip="8.8.8.8", path="/.env")["ban"] is None
    second = security.record_hit(ip="8.8.8.8", path="/.aws/credentials")

    assert second["ban"] is not None
    assert second["ban"]["source"] == "autoban"
    ban = security.active_ban("8.8.8.8")
    assert ban is not None
    assert ban["expires_at"] > 0

    # The next request is refused before Flask reaches a route.
    client = app.test_client()
    blocked = client.get("/", headers={"X-Forwarded-For": "8.8.8.8"})
    assert blocked.status_code == 403
    assert blocked.mimetype == "text/plain"

    api = client.get("/api/config", headers={"X-Forwarded-For": "8.8.8.8"})
    assert api.status_code == 403
    assert api.get_json()["code"] == "IP_BANNED"

    subdomain = client.get(
        "/dashboard",
        headers={
            "X-Forwarded-For": "8.8.8.8",
            "X-Forwarded-Host": "dash.niko.sryze.cc",
        },
    )
    assert subdomain.status_code == 403

    # A different address still reaches the site.
    allowed = client.get("/api/config", headers={"X-Forwarded-For": "1.1.1.1"})
    assert allowed.status_code == 200


def test_loopback_and_private_addresses_cannot_be_banned(store):
    with pytest.raises(ValueError, match="internal"):
        security.ban_ip("127.0.0.1", reason="local")
    with pytest.raises(ValueError, match="internal"):
        security.ban_ip("10.0.0.7", reason="private")
    assert security.active_ban("127.0.0.1") is None

    # A row written by an older build is ignored and removed on the next read.
    security._backend().put_ban("127.0.0.1", {
        "ip": "127.0.0.1",
        "reason": "old manual ban",
        "created_at": time.time(),
        "created_by": "900",
        "expires_at": None,
        "source": "manual",
    })
    security.reset()
    assert security.active_ban("127.0.0.1") is None
    # The owner page's full read removes the now-invalid row.
    security.snapshot()
    assert security._backend().get_ban("127.0.0.1") is None

    # Local traffic still reaches the site even while the guard is armed.
    security.update_settings({
        "enabled": True,
        "threshold": 2,
        "window_seconds": 300,
        "cooldown_seconds": 600,
    })
    for _ in range(3):
        security.record_hit(ip="127.0.0.1", path="/.env")
    assert security.active_ban("127.0.0.1") is None
    local = app.test_client().get("/api/config")
    assert local.status_code == 200


def test_manual_ban_and_unban(store):
    security.ban_ip("8.8.4.4", reason="Repeat probing", actor="900")
    assert security.is_banned("8.8.4.4")
    snapshot = security.snapshot()
    assert [row["ip"] for row in snapshot["bans"]] == ["8.8.4.4"]

    security.unban_ip("8.8.4.4")
    assert not security.is_banned("8.8.4.4")
    assert security.snapshot()["bans"] == []


def test_the_guard_is_off_by_default(store):
    for _ in range(30):
        security.record_hit(ip="8.8.8.8", path="/.env")
    assert not security.is_banned("8.8.8.8")
    assert security.settings()["enabled"] is False


def test_owner_api_lists_hits_and_saves_the_guard(store, monkeypatch):
    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "900"}
        session["access_token"] = "test-token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = "test-csrf"
    monkeypatch.setattr(honeypot_routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)

    security.record_hit(ip="8.8.4.4", path="/.env", host="niko.sryze.cc")
    listed = client.get("/api/owner/honeypot")
    assert listed.status_code == 200
    assert listed.get_json()["hits"][0]["ip"] == "8.8.4.4"

    saved = client.post(
        "/api/owner/honeypot/settings",
        headers={"X-CSRF-Token": "test-csrf"},
        json={
            "enabled": True,
            "threshold": 2,
            "window_seconds": 300,
            "cooldown_seconds": 600,
        },
    )
    assert saved.status_code == 200
    assert saved.get_json()["settings"]["enabled"] is True

    local = client.post(
        "/api/owner/honeypot/ban",
        headers={"X-CSRF-Token": "test-csrf"},
        json={"ip": "127.0.0.1", "reason": "test"},
    )
    assert local.status_code == 400
    assert "internal" in local.get_json()["error"].lower()

    banned = client.post(
        "/api/owner/honeypot/ban",
        headers={"X-CSRF-Token": "test-csrf"},
        json={"ip": "8.8.4.4", "reason": "test"},
    )
    assert banned.status_code == 200
    assert [row["ip"] for row in banned.get_json()["bans"]] == ["8.8.4.4"]
