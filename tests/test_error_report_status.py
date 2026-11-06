"""Review states and deletion for the staff error reports page.

A report is triaged by any staff member but destroyed only by the owner and
Head Admins, and a database created before review states existed still has to
come up with its old rows in the default state.
"""

import asyncio
import json
import re
import sys
import time
from pathlib import Path

import aiosqlite
import pytest
from flask import Flask

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import SQLitePool  # noqa: E402
from utils import error_reports  # noqa: E402
from webapp import app  # noqa: E402
from webapp import error_reporting  # noqa: E402
from webapp.routes import team_routes as routes  # noqa: E402

LEGACY_SCHEMA = """
CREATE TABLE error_reports (
    code TEXT PRIMARY KEY,
    report TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

REPORT_BODY = (
    "Occurred (UTC):\n\n2026-01-01T00:00:00+00:00\n"
    "Exception\n\nType: ValueError\nMessage: boom"
)


@pytest.fixture
def legacy_reports(monkeypatch):
    """The report store as a database from before review states existed."""
    async def setup():
        connection = await aiosqlite.connect(":memory:")
        pool = SQLitePool(connection)
        await pool.execute(LEGACY_SCHEMA)
        await pool.execute(
            "INSERT INTO error_reports (code, report, created_at) VALUES ($1, $2, $3)",
            "ABC123",
            REPORT_BODY,
            "2026-01-01T00:00:00+00:00",
        )
        return connection, pool

    connection, pool = asyncio.run(setup())
    database = error_reports.ErrorReportDatabase()
    monkeypatch.setattr(database, "pool", pool)
    monkeypatch.setattr(error_reports, "_REPORT_CACHE", {})
    yield database
    asyncio.run(connection.close())


@pytest.fixture
def reports(legacy_reports):
    """The same store after startup has added the review columns."""
    asyncio.run(legacy_reports.ensure_status_columns())
    return legacy_reports


@pytest.fixture
def web(monkeypatch, reports):
    """The Flask app with a bot and a working loop, signed in as staff."""
    monkeypatch.setattr(routes, "_discord_bot", object())
    monkeypatch.setattr(routes, "run_on_bot_loop", lambda awaitable: asyncio.run(awaitable))

    def client(role):
        monkeypatch.setattr(routes, "_current_staff_role", lambda: role)
        flask = app.test_client()
        with flask.session_transaction() as session:
            session["user"] = {"id": "42", "username": "tester", "global_name": "Tester"}
            session["access_token"] = "token"
            session["token_exp"] = time.time() + 3600
            session["csrf_token"] = "csrf"
        return flask

    return client


def _stored(reports):
    row = asyncio.run(reports.pool.fetchrow(
        "SELECT status, status_by_name FROM error_reports WHERE code = $1", "ABC123"))
    return dict(row) if row is not None else None


def test_a_legacy_table_gains_the_review_columns(legacy_reports):
    columns = asyncio.run(legacy_reports.pool.fetch("PRAGMA table_info(error_reports)"))
    assert "status" not in {row["name"] for row in columns}

    asyncio.run(legacy_reports.ensure_status_columns())

    # An old report starts out waiting for its first review.
    assert _stored(legacy_reports) == {"status": "awaiting_review", "status_by_name": None}


def test_any_staff_role_can_move_a_report_between_review_states(web):
    client = web("support")
    response = client.post(
        "/api/staff/error-reports/abc123",
        json={"status": "under_review"},
        headers={"X-CSRF-Token": "csrf"},
    )

    assert response.status_code == 200
    assert response.get_json()["report"] == {
        "code": "ABC123",
        "status": "under_review",
        "status_by": "42",
        "status_by_name": "Tester",
        "status_at": response.get_json()["report"]["status_at"],
    }
    listed = asyncio.run(error_reports.list_error_reports())
    assert listed[0]["status"] == "under_review"
    assert listed[0]["status_by_name"] == "Tester"


def test_an_unknown_review_state_is_refused(web, reports):
    client = web("moderator")
    response = client.post(
        "/api/staff/error-reports/ABC123",
        json={"status": "closed"},
        headers={"X-CSRF-Token": "csrf"},
    )

    assert response.status_code == 400
    assert _stored(reports)["status"] == "awaiting_review"


def test_a_fix_moves_through_its_development_stages(reports):
    stages = ("fix_needed", "investigating_fix", "developing_fix", "testing_fix", "resolved")

    for stage in stages:
        result = asyncio.run(error_reports.set_error_report_status("ABC123", stage, 42, "Ada"))
        assert result["status"] == stage

    assert asyncio.run(error_reports.list_error_reports())[0]["status"] == "resolved"


def test_the_fix_workflow_matches_the_dashboard_dropdown():
    page = (ROOT / "web" / "src" / "pages" / "StaffDashboardPage.tsx").read_text(encoding="utf-8")
    block = re.search(r"const REPORT_STATUSES = \[(.*?)\n\];", page, re.S).group(1)
    options = re.findall(r'value: "([a-z_]+)"', block)

    # The server accepts exactly the states the dropdown offers, in the same
    # order, so a new stage cannot be added to one side only.
    assert options == list(error_reports.REPORT_STATUSES)
    assert options[3:6] == ["investigating_fix", "developing_fix", "testing_fix"]


def test_the_delete_prompt_is_the_dashboards_own_glass_dialog():
    page = (ROOT / "web" / "src" / "pages" / "StaffDashboardPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "web" / "src" / "styles.css").read_text(encoding="utf-8")
    dialog = (ROOT / "web" / "src" / "components" / "dashboard" / "ConfirmDialog.tsx").read_text(encoding="utf-8")

    # A browser prompt cannot wear the dashboard's glass, so deleting a report
    # asks in a portalled card instead.
    assert 'reports.confirmDelete' not in page
    delete_flow = page.split("const requestDeleteReport")[1].split("async function loadAppeals")[0]
    assert "window.confirm" not in delete_flow
    assert "<ConfirmDialog" in page
    assert 'title={t("reports.deleteTitle")}' in page
    assert "createPortal" in dialog
    assert 'role="alertdialog"' in dialog
    assert "confirm-dialog { display: grid" in styles and "backdrop-filter: blur(26px)" in styles

    # The row keeps its status pill on a phone, where the shared staff rule
    # hides pills, and the triage controls stack instead of overflowing.
    assert ".staff-report-row .staff-guild-status { grid-area: status; display: inline-flex" in styles
    assert ".staff-report-actions .button { width: 100%" in styles


def test_only_the_owner_and_head_admins_can_delete_a_report(web, reports):
    asyncio.run(reports.ensure_status_columns())

    # Lower staff can triage but not destroy the traceback.
    forbidden = web("moderator").delete(
        "/api/staff/error-reports/ABC123", headers={"X-CSRF-Token": "csrf"})
    assert forbidden.status_code == 403
    assert _stored(reports) is not None

    allowed = web("head_admin").delete(
        "/api/staff/error-reports/ABC123", headers={"X-CSRF-Token": "csrf"})
    assert allowed.status_code == 200
    assert allowed.get_json() == {"deleted": True, "code": "ABC123"}
    assert _stored(reports) is None

    # Deleting it again reports the report as already gone.
    again = web("owner").delete(
        "/api/staff/error-reports/ABC123", headers={"X-CSRF-Token": "csrf"})
    assert again.status_code == 404


def test_a_report_is_stored_as_versioned_json(reports):
    async def save():
        code, saved = await error_reports.save_error_report(
            ValueError("boom"),
            {
                "command": "ping Example",
                "user": {"id": "42", "name": "Ada"},
                "arguments": "(1, 'two')",
            },
            source="prefix",
        )
        row = await reports.pool.fetchrow(
            "SELECT report FROM error_reports WHERE code = $1", code
        )
        fetched = await error_reports.get_error_report(code)
        return code, saved, row, fetched

    code, saved, row, fetched = asyncio.run(save())
    stored = json.loads(row["report"])

    # The column contains JSON, not the old human-readable text.
    assert row["report"].lstrip().startswith("{")
    assert stored["version"] == error_reports.REPORT_VERSION
    assert stored["code"] == code
    assert stored["source"] == "prefix"
    assert stored["context"]["command"] == "ping Example"
    assert stored["exception"]["name"] == "ValueError"
    assert "ValueError: boom" in stored["exception"]["traceback"]
    assert fetched == saved
    assert fetched["code"] == code


def test_an_old_plain_text_report_is_read_as_structured_context(legacy_reports):
    report = asyncio.run(error_reports.get_error_report("ABC123"))

    assert report["version"] == 0
    assert report["source"] == "legacy"
    assert report["exception"]["name"] == "ValueError"
    assert report["exception"]["message"] == "boom"
    assert report["created_at"] == "2026-01-01T00:00:00+00:00"
    # The original text stays available instead of being thrown away.
    assert report["raw"] == REPORT_BODY


def test_web_and_api_failures_create_reports_with_redacted_requests(monkeypatch):
    captured = []

    def fake_persist(error, context, source, summary):
        captured.append({
            "error": error,
            "context": context,
            "source": source,
            "summary": summary,
        })
        return "WEB123"

    monkeypatch.setattr(error_reporting, "_persist", fake_persist)
    test_app = Flask(__name__)
    test_app.secret_key = "test"

    @test_app.route("/api/boom")
    def api_boom():
        raise RuntimeError("api exploded")

    @test_app.route("/boom")
    def website_boom():
        raise RuntimeError("website exploded")

    error_reporting.register_error_reporting(test_app)
    client = test_app.test_client()

    response = client.get("/api/boom?token=super-secret&guild_id=7")
    assert response.status_code == 500
    assert response.get_json()["report_code"] == "WEB123"
    assert response.headers["X-Error-Code"] == "INTERNAL_SERVER_ERROR"
    assert response.headers["X-Error-Report"] == "WEB123"
    api = captured[-1]
    assert api["source"] == "api"
    assert api["context"]["request"]["method"] == "GET"
    assert api["context"]["request"]["path"] == "/api/boom"
    assert api["context"]["request"]["query"]["token"] == "<redacted>"
    assert api["context"]["request"]["query"]["guild_id"] == ["7"]

    response = client.get("/boom", headers={"Accept": "text/html"})
    assert response.status_code == 500
    assert captured[-1]["source"] == "website"
    assert captured[-1]["context"]["request"]["path"] == "/boom"

    # A normal 404 is not an incident and must not create a report.
    before = len(captured)
    assert client.get("/does-not-exist").status_code == 404
    assert len(captured) == before


def test_getreport_prints_the_overview_in_the_current_channel():
    support = (ROOT / "src" / "cogs" / "staff" / "commands" / "support.py").read_text(encoding="utf-8")
    command = support.split("async def get_report")[1]

    # The command shows the headline card where staff asked for it; it no
    # longer DMs a file, which left the channel without the report code.
    assert "discord.File" not in command
    assert "io.BytesIO" not in command
    assert "ctx.author.send" not in command
    assert "ctx.send(view=view" in command


def test_request_redaction_strips_credentials_at_every_level():
    redacted = error_reporting._redact_value({
        "password": "hunter2",
        "csrf_token": "csrf-secret",
        "nested": {"access_token": "token-secret", "guild_id": "7"},
        "items": [{"client_secret": "secret"}, {"name": "visible"}],
    })

    assert redacted["password"] == "<redacted>"
    assert redacted["csrf_token"] == "<redacted>"
    assert redacted["nested"]["access_token"] == "<redacted>"
    assert redacted["nested"]["guild_id"] == "7"
    assert redacted["items"][0]["client_secret"] == "<redacted>"
    assert redacted["items"][1]["name"] == "visible"
