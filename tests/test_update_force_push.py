"""Beta-side push: telling production to apply an update while its site is down."""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import updates  # noqa: E402
from webapp.server import app as flask_app  # noqa: E402


class _Response:
    def __init__(self, status_code: int = 200, payload=None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {"ok": True}
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def test_push_requires_both_sides_to_be_configured(monkeypatch):
    monkeypatch.delenv("PRODUCTION_INSTANCE_URL", raising=False)
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")
    result = updates.push_to_production()
    assert result["ok"] is False
    assert "PRODUCTION_INSTANCE_URL" in result["error"]

    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "")
    result = updates.push_to_production()
    assert result["ok"] is False
    assert "BETA_UPDATE_TOKEN" in result["error"]


def test_push_posts_the_selected_areas_with_the_shared_token(monkeypatch):
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example/")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")
    seen: dict = {}

    def fake_post(url, **kwargs):
        seen["url"] = url
        seen.update(kwargs)
        return _Response(200, {"ok": True, "areas": {"website": {"changed": 2}}})

    monkeypatch.setattr(updates.requests, "post", fake_post)
    result = updates.push_to_production(["website", "cogs"])

    assert result["ok"] is True
    assert seen["url"] == "https://prod.example/supervisor/update"
    assert seen["headers"]["X-Update-Token"] == "shared"
    assert seen["json"] == {"areas": ["website", "cogs"]}
    assert seen["allow_redirects"] is False


def test_push_rejects_unknown_areas_before_calling_production(monkeypatch):
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")
    called = False

    def fake_post(*_args, **_kwargs):
        nonlocal called
        called = True
        return _Response()

    monkeypatch.setattr(updates.requests, "post", fake_post)
    result = updates.push_to_production(["not-an-area"])
    assert result["ok"] is False
    assert "Unknown areas" in result["error"]
    assert called is False


def test_push_reports_a_timeout_without_claiming_failure(monkeypatch):
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")

    def fake_post(*_args, **_kwargs):
        raise requests.Timeout("slow")

    monkeypatch.setattr(updates.requests, "post", fake_post)
    result = updates.push_to_production(["website"])
    assert result["ok"] is False
    assert result["sent"] is True
    assert "may still be running" in result["error"]


def test_push_reports_unreachable_production(monkeypatch):
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")

    def fake_post(*_args, **_kwargs):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(updates.requests, "post", fake_post)
    result = updates.push_to_production()
    assert result["ok"] is False
    assert "could not reach production" in result["error"]


def test_beta_push_route_requires_the_shared_token(monkeypatch):
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    client = flask_app.test_client()

    assert client.post("/api/updates/push", json={}).status_code == 404

    seen: dict = {}

    def fake_push(areas):
        seen["areas"] = areas
        return {"ok": True, "production": "https://prod.example"}

    monkeypatch.setattr(updates, "push_to_production", fake_push)
    response = client.post(
        "/api/updates/push",
        json={"areas": ["website"]},
        headers={"X-Update-Token": "shared"},
    )
    assert response.status_code == 200
    assert seen["areas"] == ["website"]


def test_internal_force_route_is_hidden_in_the_dashboard_child(monkeypatch):
    monkeypatch.setenv("NIKO_INTERNAL_TOKEN", "internal-secret")
    monkeypatch.setenv("NIKO_WEB_ROLE", "1")
    client = flask_app.test_client()
    response = client.post(
        "/api/updates/force",
        json={"areas": ["website"]},
        headers={"X-Supervisor-Token": "internal-secret"},
    )
    assert response.status_code == 404


def test_apply_refuses_a_second_run(monkeypatch):
    gate = updates._apply_gate
    gate.acquire()
    try:
        result = updates.apply(["website"])
    finally:
        gate.release()
    assert result["ok"] is False
    assert "already being applied" in result["error"]


def test_apply_gate_survives_the_module_reload_at_the_end_of_a_run(monkeypatch):
    """A utils/webapp update swaps this module's dict before the gate is released."""
    original = updates._apply_gate
    replacement = threading.Lock()

    def fake_locked(_areas, _bot=None):
        updates._apply_gate = replacement
        return {"ok": True}

    monkeypatch.setattr(updates, "_apply_locked", fake_locked)
    try:
        assert updates.apply(["website"]) == {"ok": True}
        # The lock that was acquired is free again, not the replacement.
        assert original.acquire(blocking=False) is True
        original.release()
    finally:
        updates._apply_gate = original


def test_push_relays_a_rejected_update(monkeypatch):
    monkeypatch.setenv("PRODUCTION_INSTANCE_URL", "https://prod.example")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "shared")
    monkeypatch.setattr(
        updates.requests,
        "post",
        lambda *_args, **_kwargs: _Response(
            409, {"ok": False, "error": "An update is already being applied."}
        ),
    )
    result = updates.push_to_production(["website"])
    assert result["ok"] is False
    assert result["status"] == 409
    assert result["result"]["error"]
