"""Incident publication, report timelines, and API maintenance targets."""

import asyncio
import sys
import time
from pathlib import Path

import aiosqlite
import pytest
from flask import Flask, jsonify

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import SQLitePool  # noqa: E402
from utils import error_reports, maintenance  # noqa: E402
from webapp import api_maintenance, app as flask_app  # noqa: E402
from webapp import status as status_source  # noqa: E402
from webapp.routes import maintenance_routes, team_routes  # noqa: E402

REPORT_SCHEMA = """
CREATE TABLE error_reports (
    code TEXT PRIMARY KEY,
    report TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

MAINTENANCE_SCHEMA = """
CREATE TABLE maintenance_targets (
    target TEXT PRIMARY KEY,
    reason TEXT,
    since REAL,
    added_by TEXT,
    report_code TEXT
)
"""


@pytest.fixture
def reports(monkeypatch):
    async def setup():
        connection = await aiosqlite.connect(":memory:")
        pool = SQLitePool(connection)
        await pool.execute(REPORT_SCHEMA)
        return connection, pool

    connection, pool = asyncio.run(setup())
    database = error_reports.ErrorReportDatabase()
    monkeypatch.setattr(database, "pool", pool)
    monkeypatch.setattr(error_reports, "_REPORT_CACHE", {})
    asyncio.run(database.ensure_status_columns())
    yield database
    asyncio.run(connection.close())


@pytest.fixture
def maintenance_store(monkeypatch):
    async def setup():
        connection = await aiosqlite.connect(":memory:")
        pool = SQLitePool(connection)
        await pool.execute(MAINTENANCE_SCHEMA)
        return connection, pool

    connection, pool = asyncio.run(setup())
    bot = type("Bot", (), {"cxn": pool, "cog_status": []})()
    monkeypatch.setattr(maintenance, "_cache", maintenance._empty())
    monkeypatch.setattr(maintenance, "_loaded", True)
    yield bot
    asyncio.run(connection.close())


def test_every_review_change_is_appended_to_the_report_timeline(reports):
    async def scenario():
        code, _ = await error_reports.save_error_report(ValueError("boom"), {"command": "ping"})
        await error_reports.set_error_report_status(code, "under_review", 42, "Ada")
        await error_reports.set_error_report_status(code, "resolved", 7, "Grace")
        return await error_reports.get_error_report_item(code)

    item = asyncio.run(scenario())
    events = item["incident_events"]
    assert [event["type"] for event in events] == ["created", "status", "status"]
    assert events[1]["from"] == "awaiting_review"
    assert events[1]["status"] == "under_review"
    assert events[1]["by_name"] == "Ada"
    assert events[2]["status"] == "resolved"


def test_only_owner_published_reports_become_public_incidents(reports):
    async def scenario():
        public_code, _ = await error_reports.save_error_report(RuntimeError("api exploded"), {"request": {"endpoint": "api_boom"}}, source="api")
        private_code, _ = await error_reports.save_error_report(PermissionError("no"), {"command": "ping"}, source="slash")
        await error_reports.set_error_report_incident(
            public_code,
            public_notice=True,
            severity="major",
            maintenance_enabled=True,
            maintenance_kind="api",
            maintenance_key="api_boom",
            staff_id=42,
            staff_name="Ada",
        )
        return public_code, private_code, await error_reports.list_public_incidents()

    public_code, private_code, incidents = asyncio.run(scenario())
    assert [incident["code"] for incident in incidents] == [public_code]
    assert private_code not in [incident["code"] for incident in incidents]
    incident = incidents[0]
    assert incident["severity"] == "major"
    assert incident["state"] == "investigating"
    assert incident["maintenance"] == {"kind": "api", "key": "api_boom", "label": "Boom API"}
    assert all("traceback" not in event and "by_name" not in event for event in incident["timeline"])
    # The report document still has its full traceback for staff.
    report = asyncio.run(error_reports.get_error_report_item(public_code))
    assert "RuntimeError" in report["report"]["exception"]["traceback"]


def test_permission_failures_are_classified_as_user_error(reports):
    async def scenario():
        code, _ = await error_reports.save_error_report(PermissionError("missing permission"), {"command": "ban"})
        return await error_reports.get_error_report(code)

    report = asyncio.run(scenario())
    assert report["classification"] == "user_error"


def test_api_maintenance_is_in_the_same_cache_and_snapshot(maintenance_store):
    async def scenario():
        bot = maintenance_store
        await maintenance.set_maintenance(
            "api", "api_boom", True, "The endpoint is down.", 42, bot, report_code="ABC123",
        )
        snapshot = maintenance.snapshot(
            bot,
            [{"endpoint": "api_boom", "path": "/api/boom", "methods": ["GET"]}],
        )
        return snapshot, maintenance.find_api_block("api_boom")

    snapshot, found = asyncio.run(scenario())
    api = snapshot["apis"][0]
    assert api["maintenance"] is True
    assert api["path"] == "/api/boom"
    assert api["report_code"] == "ABC123"
    assert found[0] == "api"
    assert found[2]["reason"] == "The endpoint is down."


def test_api_maintenance_gate_returns_a_stable_documented_envelope(monkeypatch):
    monkeypatch.setattr(
        maintenance,
        "find_api_block",
        lambda _endpoint, _path: (
            "api",
            "api_economy_leaderboard",
            {"reason": "Rebuilding the leaderboard cache", "since": 1762300000, "report_code": "ABC123"},
        ),
    )
    monkeypatch.setattr(api_maintenance, "_is_owner", lambda: False)
    monkeypatch.setattr(api_maintenance, "_current_staff_role", lambda: None)
    client = flask_app.test_client()

    response = client.get("/api/v1/economy/leaderboard")

    assert response.status_code == 503
    assert response.headers["Retry-After"] == "300"
    assert response.headers["X-Error-Code"] == "API_MAINTENANCE"
    assert response.headers["X-Error-Report"] == "ABC123"
    payload = response.get_json()
    assert payload["code"] == "API_MAINTENANCE"
    assert payload["docs"] == "/developers/maintenance"
    assert payload["maintenance"] == {
        "kind": "api",
        "key": "api_economy_leaderboard",
        "label": maintenance.api_label("api_economy_leaderboard"),
        "reason": "Rebuilding the leaderboard cache",
        "since": 1762300000,
    }
    assert payload["report_code"] == "ABC123"


def test_api_404_and_405_responses_are_json_with_stable_codes():
    client = flask_app.test_client()

    missing = client.get("/api/v1/does-not-exist")
    assert missing.status_code == 404
    assert missing.get_json()["code"] == "NOT_FOUND"

    wrong_method = client.post("/api/v1/economy/leaderboard")
    assert wrong_method.status_code == 405
    assert wrong_method.get_json()["code"] == "METHOD_NOT_ALLOWED"


def test_owner_can_publish_a_report_and_pause_its_api(monkeypatch, reports):
    async def add_maintenance_table():
        await reports.pool.execute(MAINTENANCE_SCHEMA)
        code, _ = await error_reports.save_error_report(
            RuntimeError("api exploded"),
            {"request": {"endpoint": "api_staff_error_reports"}},
            source="api",
        )
        return code

    code = asyncio.run(add_maintenance_table())
    bot = type("Bot", (), {"cxn": reports.pool, "commands": [], "tree": None, "cog_status": []})()
    monkeypatch.setattr(team_routes, "_discord_bot", bot)
    monkeypatch.setattr(team_routes, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))
    monkeypatch.setattr(team_routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(maintenance_routes, "_discord_bot", bot)
    monkeypatch.setattr(maintenance_routes, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))
    monkeypatch.setattr(maintenance_routes, "_current_staff_role", lambda: "owner")
    monkeypatch.setattr(maintenance, "_cache", maintenance._empty())
    monkeypatch.setattr(maintenance, "_loaded", True)

    client = flask_app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "42", "username": "tester", "global_name": "Tester"}
        session["access_token"] = "token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = "csrf"

    response = client.post(
        f"/api/staff/error-reports/{code}/incident",
        json={
            "public_notice": True,
            "severity": "critical",
            "maintenance": {"enabled": True, "kind": "api", "key": "api_staff_error_reports"},
        },
        headers={"X-CSRF-Token": "csrf"},
    )

    assert response.status_code == 200, response.get_json()
    item = response.get_json()["report"]
    assert item["public_notice"] is True
    assert item["severity"] == "critical"
    assert item["maintenance_kind"] == "api"
    assert item["maintenance_key"] == "api_staff_error_reports"
    assert maintenance.entry("api", "api_staff_error_reports")["report_code"] == code

    resumed = client.post(
        "/api/staff/maintenance",
        json={"kind": "api", "key": "api_staff_error_reports", "enabled": False},
        headers={"X-CSRF-Token": "csrf"},
    )
    assert resumed.status_code == 200, resumed.get_json()
    assert maintenance.entry("api", "api_staff_error_reports") is None
    report = asyncio.run(error_reports.get_error_report_item(code))
    assert report["maintenance_kind"] is None
    assert report["incident_events"][-1]["type"] == "maintenance"
    assert report["incident_events"][-1]["enabled"] is False


def test_non_owners_and_user_errors_cannot_create_public_incidents(monkeypatch, reports):
    async def save_user_error():
        code, _ = await error_reports.save_error_report(PermissionError("no"), {"command": "ban"}, source="slash")
        return code

    code = asyncio.run(save_user_error())
    bot = type("Bot", (), {"cxn": reports.pool, "commands": [], "tree": None, "cog_status": []})()
    monkeypatch.setattr(team_routes, "_discord_bot", bot)
    monkeypatch.setattr(team_routes, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))
    client = flask_app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": "42", "username": "tester", "global_name": "Tester"}
        session["access_token"] = "token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = "csrf"

    monkeypatch.setattr(team_routes, "_current_staff_role", lambda: "head_admin")
    denied = client.post(
        f"/api/staff/error-reports/{code}/incident",
        json={"public_notice": True},
        headers={"X-CSRF-Token": "csrf"},
    )
    assert denied.status_code == 403

    monkeypatch.setattr(team_routes, "_current_staff_role", lambda: "owner")
    refused = client.post(
        f"/api/staff/error-reports/{code}/incident",
        json={"public_notice": True},
        headers={"X-CSRF-Token": "csrf"},
    )
    assert refused.status_code == 409
    assert "user error" in refused.get_json()["error"].lower()


def test_status_payload_includes_api_and_command_maintenance(monkeypatch):
    bot = type("Bot", (), {
        "guilds": [],
        "shards": {},
        "shard_count": 1,
        "user": None,
        "start_time": None,
        "cog_status": [],
        "commands": [],
        "tree": None,
        "cogs": {},
        "latency": 0.05,
        "is_ready": lambda self: True,
        "get_cog": lambda self, name: None,
    })()
    monkeypatch.setattr(maintenance, "_cache", {
        "cogs": {},
        "commands": {"ping": {"reason": "Command fix", "since": 10, "by": "1", "report_code": "ABC123"}},
        "apis": {"api_boom": {"reason": "API fix", "since": 11, "by": "1", "report_code": "ABC123"}},
    })

    async def no_incidents(*args, **kwargs):
        return []

    monkeypatch.setattr(status_source, "list_public_incidents", no_incidents)
    payload = asyncio.run(status_source.bot_status(bot))

    assert payload["state"] == "maintenance"
    assert payload["api_maintenance"][0]["label"] == "Boom API"
    assert payload["command_maintenance"][0]["name"] == "ping"
    assert payload["command_maintenance"][0].get("incident_state") is None


def test_the_api_gate_answers_503_and_lets_the_owner_through(monkeypatch):
    test_app = Flask(__name__)
    test_app.secret_key = "test"

    @test_app.route("/api/boom")
    def api_boom():
        return jsonify({"ok": True})

    api_maintenance.register_api_maintenance(test_app)
    monkeypatch.setattr(maintenance, "_cache", {
        "cogs": {},
        "commands": {},
        "apis": {"api_boom": {"reason": "Paused", "since": 1, "by": "42", "report_code": "ABC123"}},
    })
    monkeypatch.setattr(api_maintenance, "_is_owner", lambda: False)
    monkeypatch.setattr(api_maintenance, "_current_staff_role", lambda: None)
    client = test_app.test_client()

    response = client.get("/api/boom")
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "300"
    assert response.get_json()["maintenance"]["label"] == "Boom API"

    monkeypatch.setattr(api_maintenance, "_is_owner", lambda: True)
    assert client.get("/api/boom").status_code == 200
