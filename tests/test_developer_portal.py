"""Developer API access, key scopes, and website-only data routes."""

import asyncio
import hashlib
import hmac
import io
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, auth, developer_applications, developer_portal, developer_webhooks, staff  # noqa: E402
from webapp import api_errors  # noqa: E402
from webapp.routes import developer_routes, public_routes  # noqa: E402

OWNER = "900"


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(developer_portal.config, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(developer_portal, "_STORE", None)
    monkeypatch.setattr(developer_portal, "_STORE_STAMP", None)
    monkeypatch.setattr(developer_portal, "is_owner_id", lambda user_id: str(user_id) == OWNER)
    monkeypatch.setattr(staff, "is_owner_id", lambda user_id: str(user_id) == OWNER)
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)
    monkeypatch.setattr(developer_portal, "_IP_HITS", {})
    monkeypatch.setattr(developer_portal, "_KEY_HITS", {})
    return tmp_path


def stub_leaderboard(monkeypatch):
    monkeypatch.setattr(
        developer_routes,
        "get_runtime_leaderboard_page",
        lambda offset, page_size: ([{"user_id": "42", "net_worth": 100, "leaderboard_private": 0}], 1),
    )
    monkeypatch.setattr(developer_routes, "_resolve_leaderboard_identities", lambda _ids: {})


def signed_in_client(user_id, csrf="test-csrf"):
    client = app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"id": str(user_id)}
        session["access_token"] = "test-token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = csrf
    return client


def grant(user_id="42", scopes=("economy:read", "levels:read")):
    developer_portal.grant_access(user_id, list(scopes), actor_id=OWNER)


def accepted_key(user_id="42", scopes=("economy:read",), name="migration"):
    if not developer_portal.developer_access(user_id)["policy_accepted"]:
        developer_portal.accept_policy(user_id)
    return developer_portal.create_key(user_id, name, list(scopes))[1]


def test_policy_must_be_accepted_before_the_first_key(store):
    grant()

    assert developer_portal.developer_access("42")["policy_accepted"] is False
    with pytest.raises(PermissionError, match="guidelines"):
        developer_portal.create_key("42", "migration", ["economy:read"])

    developer_portal.accept_policy("42")
    key, raw = developer_portal.create_key("42", "migration", ["economy:read"])

    assert key["scopes"] == ["economy:read"]
    assert raw.startswith("niko_dev_")
    assert raw not in str(store / "developer_portal.json")


def test_a_key_cannot_include_a_scope_that_was_not_granted(store):
    grant(scopes=("economy:read",))

    with pytest.raises(PermissionError, match="not been granted"):
        accepted_key(scopes=("economy:read", "blacklist:read"))


def test_revoked_and_narrowed_keys_stop_working(store):
    grant(scopes=("economy:read", "levels:read"))
    raw = accepted_key(scopes=("economy:read", "levels:read"))

    authenticated = developer_portal.authenticate(raw)
    assert authenticated is not None
    assert authenticated["scopes"] == ["economy:read", "levels:read"]

    developer_portal.grant_access("42", ["levels:read"], actor_id=OWNER)
    narrowed = developer_portal.authenticate(raw)
    assert narrowed is not None
    assert narrowed["scopes"] == ["levels:read"]

    developer_portal.revoke_key("42", narrowed["key"]["id"])
    assert developer_portal.authenticate(raw) is None


def test_api_key_requires_the_matching_scope(store, monkeypatch):
    monkeypatch.setattr(
        developer_routes,
        "get_runtime_leaderboard_page",
        lambda offset, page_size: ([{"user_id": "42", "net_worth": 100, "leaderboard_private": 0}], 1),
    )
    monkeypatch.setattr(developer_routes, "_resolve_leaderboard_identities", lambda _ids: {})
    grant(scopes=("economy:read", "levels:read"))
    economy_key = accepted_key(scopes=("economy:read",), name="economy")
    levels_key = accepted_key(scopes=("levels:read",), name="levels")

    client = app.test_client()
    assert client.get("/api/v1/economy/leaderboard").status_code == 401
    assert client.get(
        "/api/v1/economy/leaderboard",
        headers={"Authorization": f"Bearer {levels_key}"},
    ).status_code == 403

    response = client.get(
        "/v1/economy/leaderboard",
        headers={"Authorization": f"Bearer {economy_key}"},
    )
    assert response.status_code == 200
    assert response.get_json()["entries"][0]["net_worth"] == 100
    assert response.headers["X-Niko-Scopes"] == "economy:read"


def test_website_data_routes_reject_direct_clients_but_allow_the_site(store, monkeypatch):
    monkeypatch.setattr(
        public_routes,
        "get_runtime_leaderboard_page",
        lambda offset, page_size: ([], 0),
    )
    monkeypatch.setattr(public_routes, "_resolve_leaderboard_identities", lambda _ids: {})

    client = app.test_client()
    assert client.get("/api/economy/leaderboard").status_code == 401
    same_origin = client.get(
        "/api/economy/leaderboard",
        headers={"Sec-Fetch-Site": "same-origin"},
    )
    assert same_origin.status_code == 200
    assert same_origin.get_json()["entries"] == []


def test_external_api_rate_limits_per_ip_and_recovers(store, monkeypatch):
    monkeypatch.setattr(developer_portal, "IP_RATE_LIMIT", 1)
    monkeypatch.setattr(developer_portal, "IP_RATE_WINDOW", 0.2)
    client = app.test_client()

    first = client.get("/api/v1/economy/leaderboard")
    blocked = client.get("/api/v1/economy/leaderboard")

    assert first.status_code == 401
    assert first.headers["X-RateLimit-Limit"] == "1"
    assert first.headers["X-RateLimit-Remaining"] == "0"
    assert blocked.status_code == 429
    assert blocked.get_json()["code"] == "RATE_LIMITED"
    assert blocked.get_json()["retry_after"] >= 1
    assert blocked.headers["X-Error-Code"] == "RATE_LIMITED"
    assert int(blocked.headers["Retry-After"]) >= 1

    time.sleep(0.25)
    recovered = client.get("/api/v1/economy/leaderboard")
    assert recovered.status_code == 401
    assert recovered.get_json()["code"] == "AUTH_KEY_REQUIRED"


def test_sustained_key_traffic_suspends_and_revokes_every_key(store, monkeypatch):
    stub_leaderboard(monkeypatch)
    monkeypatch.setattr(developer_portal, "KEY_RATE_LIMIT", 2)
    grant(scopes=("economy:read",))
    raw = accepted_key(scopes=("economy:read",), name="primary")
    other = accepted_key(scopes=("economy:read",), name="secondary")
    client = app.test_client()

    assert client.get(
        "/api/v1/economy/leaderboard", headers={"Authorization": f"Bearer {raw}"}
    ).status_code == 200
    suspended = client.get(
        "/api/v1/economy/leaderboard", headers={"Authorization": f"Bearer {raw}"}
    )

    assert suspended.status_code == 403
    assert suspended.get_json()["code"] == "ACCESS_SUSPENDED"
    access = developer_portal.developer_access("42")
    assert access["suspended"] is True
    assert access["enabled"] is False
    assert access["suspension"]["trigger"] == "sustained_request_rate"
    assert developer_portal.authenticate(raw) is None
    assert developer_portal.authenticate(raw, allow_suspended=True)["suspended"] is True
    stored = developer_portal._load()["keys"]
    assert len(stored) == 2
    assert all(key.get("revoked_at") for key in stored.values())
    assert all(key.get("revoked_reason") == "developer_suspended" for key in stored.values())
    assert other.startswith("niko_dev_")


def test_suspended_developer_keeps_read_only_status_but_cannot_manage_keys(store):
    grant(scopes=("economy:read",))
    accepted_key(scopes=("economy:read",))
    developer_portal.suspend_developer(
        "42",
        reason="Automated abuse detection: test threshold.",
        trigger="error_scanning",
        metadata={"errors": 80},
    )
    client = signed_in_client("42")

    status = client.get("/api/developer/me")
    assert status.status_code == 200
    assert status.get_json()["access"]["suspended"] is True
    assert status.get_json()["suspension"]["trigger"] == "error_scanning"

    blocked = client.get("/api/developer/keys")
    assert blocked.status_code == 403
    assert blocked.get_json()["code"] == "ACCESS_SUSPENDED"

    create = client.post(
        "/api/developer/keys",
        json={"name": "retry", "scopes": ["economy:read"]},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert create.status_code == 403
    assert create.get_json()["code"] == "ACCESS_SUSPENDED"
    with pytest.raises(PermissionError, match="suspended"):
        developer_portal.create_key("42", "retry", ["economy:read"])


def test_a_denied_appeal_keeps_the_suspension_and_cannot_be_reopened(store):
    grant(scopes=("economy:read",))
    accepted_key(scopes=("economy:read",))
    suspension = developer_portal.suspend_developer(
        "42",
        reason="Automated abuse detection: test threshold.",
        trigger="sustained_request_rate",
    )

    appeal = developer_portal.submit_appeal("42", "This was a one-off migration and the limiter is fixed.")
    assert appeal["status"] == "pending"
    assert developer_portal.appeal_for_user("42")["id"] == appeal["id"]
    with pytest.raises(ValueError, match="already under review"):
        developer_portal.submit_appeal("42", "Second appeal")

    decided = developer_portal.review_appeal(appeal["id"], "denied", note="No limiter added.", actor_id=OWNER)
    assert decided["status"] == "denied"
    assert developer_portal.suspension_for_user("42")["id"] == suspension["id"]
    assert developer_portal.developer_access("42")["enabled"] is False
    with pytest.raises(ValueError, match="already denied"):
        developer_portal.submit_appeal("42", "Third appeal")


def test_approved_appeal_restores_portal_access_but_not_revoked_keys(store):
    grant(scopes=("economy:read",))
    raw = accepted_key(scopes=("economy:read",))
    developer_portal.suspend_developer(
        "42",
        reason="Automated abuse detection: test threshold.",
        trigger="error_scanning",
    )
    appeal = developer_portal.submit_appeal("42", "The failing loop was a bad deploy and is reverted.")

    decided = developer_portal.review_appeal(appeal["id"], "approved", note="Limiter confirmed", actor_id=OWNER)

    assert decided["status"] == "approved"
    access = developer_portal.developer_access("42")
    assert access["suspended"] is False
    assert access["enabled"] is True
    assert access["suspension"] is None
    assert developer_portal.suspension_for_user("42") is None
    assert developer_portal.authenticate(raw) is None
    replacement, replacement_raw = developer_portal.create_key("42", "replacement", ["economy:read"])
    assert replacement["prefix"] == replacement_raw[:18]


def test_owner_reviews_an_appeal_through_the_portal_api(store):
    grant(scopes=("economy:read",))
    accepted_key(scopes=("economy:read",))
    developer_portal.suspend_developer(
        "42",
        reason="Automated abuse detection: test threshold.",
        trigger="sustained_request_rate",
    )
    appeal = developer_portal.submit_appeal("42", "Limiter is now shared across workers.")
    owner = signed_in_client(OWNER)

    queue = owner.get("/api/developer/appeals")
    assert queue.status_code == 200
    assert queue.get_json()["appeals"][0]["id"] == appeal["id"]

    response = owner.post(
        f"/api/developer/appeals/{appeal['id']}/review",
        json={"status": "approved", "note": "Confirmed."},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert response.status_code == 200
    assert response.get_json()["appeal"]["status"] == "approved"
    assert response.get_json()["access"]["enabled"] is True


def test_api_errors_use_stable_codes_and_report_references(store, monkeypatch):
    client = app.test_client()

    unauthorised = client.get("/api/v1/economy/leaderboard")
    assert unauthorised.status_code == 401
    assert unauthorised.get_json()["code"] == "AUTH_KEY_REQUIRED"
    assert unauthorised.headers["X-Error-Code"] == "AUTH_KEY_REQUIRED"

    missing = client.get("/api/v1/does-not-exist")
    assert missing.status_code == 404
    assert missing.get_json()["code"] == "NOT_FOUND"

    wrong_method = client.post("/api/v1/economy/leaderboard")
    assert wrong_method.status_code == 405
    assert wrong_method.get_json()["code"] == "METHOD_NOT_ALLOWED"

    monkeypatch.setattr("webapp.error_reporting.record_api_error", lambda *args, **kwargs: "ABC123")
    with app.app_context():
        reported = api_errors.error_response(
            "INTERNAL_SERVER_ERROR", "An unexpected server error occurred.", 500, report=True
        )
    assert reported.status_code == 500
    assert reported.get_json()["code"] == "INTERNAL_SERVER_ERROR"
    assert reported.get_json()["report_code"] == "ABC123"
    assert reported.headers["X-Error-Report"] == "ABC123"


PNG = b"\x89PNG\r\n\x1a\n" + b"verification-image"


@pytest.fixture
def application_store(store, monkeypatch):
    monkeypatch.setattr(developer_applications.config, "DATA_DIR", str(store))
    monkeypatch.setattr(developer_applications, "_STORE", None)
    monkeypatch.setattr(developer_applications, "_STORE_STAMP", None)
    monkeypatch.setattr(developer_applications, "_MEMBERSHIP_CACHE", {})
    monkeypatch.setattr(developer_applications, "_runtime_bot", lambda: None)
    monkeypatch.setattr(developer_applications, "shared_guild_count", lambda _app: 0)
    monkeypatch.setattr(
        developer_portal,
        "resolve_identity",
        lambda user_id: {
            "username": f"user-{user_id}",
            "display_name": f"User {user_id}",
            "avatar_url": None,
        },
    )
    return store


def submit_application(client, *, bot_id="1545846783253545081", scopes="warns:read"):
    return client.post(
        "/api/developer/applications",
        data={
            "name": "Aeris",
            "description": "A moderation bridge for partnered communities.",
            "bot_user_id": bot_id,
            "scopes": scopes,
            "screenshot": (io.BytesIO(PNG), "application.png"),
        },
        headers={"X-CSRF-Token": "test-csrf"},
        content_type="multipart/form-data",
    )


def test_application_registration_review_and_app_bound_key(application_store, monkeypatch):
    grant(scopes=("warns:read", "warns:write"))
    developer_portal.accept_policy("42")
    developer = signed_in_client("42")

    submitted = submit_application(developer)
    assert submitted.status_code == 201
    application = submitted.get_json()["application"]
    app_id = application["id"]
    assert application["status"] == "pending"
    assert application["screenshot"]["url"].endswith(f"/{app_id}/screenshot")
    assert (application_store / "developer_application_screenshots" / f"{app_id}.png").is_file()

    duplicate = submit_application(developer)
    assert duplicate.status_code == 409
    assert duplicate.get_json()["code"] == "APPLICATION_EXISTS"

    assert developer.get("/api/developer/applications/review").status_code == 403
    owner = signed_in_client(OWNER)
    queue = owner.get("/api/developer/applications/review")
    assert queue.status_code == 200
    assert queue.get_json()["applications"][0]["status"] == "pending"

    reviewed = owner.post(
        f"/api/developer/applications/{app_id}/review",
        json={"status": "approved", "scopes": ["warns:read"], "note": "Screenshot matches."},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert reviewed.status_code == 200
    assert reviewed.get_json()["application"]["status"] == "approved"
    assert reviewed.get_json()["application"]["approved_scopes"] == ["warns:read"]

    created = developer.post(
        "/api/developer/keys",
        json={"name": "warn sync", "scopes": ["warns:read"], "application_id": app_id},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert created.status_code == 201
    secret = created.get_json()["secret"]
    authenticated = developer_portal.authenticate(secret)
    assert authenticated["application"]["id"] == app_id
    assert authenticated["scopes"] == ["warns:read"]

    outside_app = developer.post(
        "/api/developer/keys",
        json={"name": "too broad", "scopes": ["warns:write"], "application_id": app_id},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert outside_app.status_code == 403


def test_restricted_scopes_cannot_be_self_requested(application_store):
    grant(scopes=("warns:read", "blacklist:read"))
    developer_portal.accept_policy("42")

    response = submit_application(signed_in_client("42"), scopes="blacklist:read")

    assert response.status_code == 400
    assert response.get_json()["code"] == "INVALID_APPLICATION"
    assert "special" in response.get_json()["error"].lower()


def test_denied_application_can_be_resubmitted_and_owner_only_is_enforced(application_store):
    grant(scopes=("warns:read",))
    developer_portal.accept_policy("42")
    developer = signed_in_client("42")
    app_id = submit_application(developer).get_json()["application"]["id"]
    owner = signed_in_client(OWNER)

    denied = owner.post(
        f"/api/developer/applications/{app_id}/review",
        json={"status": "denied", "note": "The profile menu is not visible."},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert denied.status_code == 200
    assert denied.get_json()["application"]["status"] == "denied"

    resubmitted = submit_application(developer)
    assert resubmitted.status_code == 201
    assert resubmitted.get_json()["application"]["id"] == app_id
    assert resubmitted.get_json()["application"]["status"] == "pending"

    non_owner = developer.post(
        f"/api/developer/applications/{app_id}/review",
        json={"status": "approved", "scopes": ["warns:read"]},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert non_owner.status_code == 403


def test_warn_api_uses_shared_guild_rule_and_emits_write_results(application_store, monkeypatch):
    grant(scopes=("warns:read", "warns:write"))
    developer_portal.accept_policy("42")
    developer = signed_in_client("42")
    app_id = submit_application(developer, scopes="warns:read").get_json()["application"]["id"]
    owner = signed_in_client(OWNER)
    owner.post(
        f"/api/developer/applications/{app_id}/review",
        json={"status": "approved", "scopes": ["warns:read", "warns:write"]},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    secret = developer.post(
        "/api/developer/keys",
        json={"name": "warn sync", "scopes": ["warns:read", "warns:write"], "application_id": app_id},
        headers={"X-CSRF-Token": "test-csrf"},
    ).get_json()["secret"]

    warn = {
        "id": 77,
        "guild_id": "123456789012345678",
        "user_id": "555",
        "moderator_id": "999",
        "reason": "Spam",
        "created_at": "2026-11-05T00:00:00+00:00",
    }

    class FakeWarns:
        def list_warnings(self, guild_id, *, user_id=None, offset=0, limit=100):
            return [warn], 1

        def add_warn(self, guild_id, user_id, moderator_id, reason):
            return {**warn, "reason": reason, "moderator_id": str(moderator_id)}

        def delete_warning(self, guild_id, warn_id):
            return warn if warn_id == 77 else None

        def clear_warnings(self, guild_id, user_id):
            return 2

    class FakeBot:
        def get_cog(self, name):
            return FakeWarns()

    monkeypatch.setattr(developer_routes, "_discord_bot", FakeBot())
    monkeypatch.setattr(developer_routes, "_guild", lambda _guild_id: object())
    monkeypatch.setattr(developer_routes, "run_on_bot_loop", lambda value, **_kwargs: value)
    monkeypatch.setattr(
        developer_applications,
        "application_in_guild",
        lambda _app, guild_id: str(guild_id) == "123456789012345678",
    )

    headers = {"Authorization": f"Bearer {secret}"}
    listed = app.test_client().get("/api/v1/guilds/123456789012345678/warns", headers=headers)
    assert listed.status_code == 200
    assert listed.get_json()["warns"][0]["id"] == 77

    created = app.test_client().post(
        "/api/v1/guilds/123456789012345678/members/555/warns",
        json={"reason": "Repeated spam"},
        headers={**headers, "Content-Type": "application/json"},
    )
    assert created.status_code == 201
    assert created.get_json()["warn"]["reason"] == "Repeated spam"

    deleted = app.test_client().delete("/api/v1/guilds/123456789012345678/warns/77", headers=headers)
    assert deleted.status_code == 200

    cleared = app.test_client().delete("/api/v1/guilds/123456789012345678/members/555/warns", headers=headers)
    assert cleared.status_code == 200
    assert cleared.get_json()["cleared"] == 2

    wrong_guild = app.test_client().get("/api/v1/guilds/999999999999999999/warns", headers=headers)
    assert wrong_guild.status_code == 404
    assert wrong_guild.get_json()["code"] == "GUILD_NOT_SHARED"


def test_blacklist_write_requires_an_app_bound_trusted_scope(application_store, monkeypatch):
    grant(scopes=("warns:read", "blacklist:write"))
    developer_portal.accept_policy("42")
    developer = signed_in_client("42")
    app_id = submit_application(developer, scopes="warns:read").get_json()["application"]["id"]
    owner = signed_in_client(OWNER)
    owner.post(
        f"/api/developer/applications/{app_id}/review",
        json={"status": "approved", "scopes": ["blacklist:write"]},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    secret = developer.post(
        "/api/developer/keys",
        json={"name": "trusted blacklist", "scopes": ["blacklist:write"], "application_id": app_id},
        headers={"X-CSRF-Token": "test-csrf"},
    ).get_json()["secret"]

    class FakeManager:
        def add_user(self, user_id, *, reason, added_by, expires_at):
            assert user_id == 1052690741874401360
            assert reason == "Confirmed scam reports"
            assert added_by == 1545846783253545081
            return True

    monkeypatch.setattr(developer_routes, "_load_blacklist_manager", lambda: FakeManager())
    monkeypatch.setattr(developer_routes, "run_on_bot_loop", lambda value, **_kwargs: value)

    response = app.test_client().post(
        "/api/v1/blacklist",
        json={"type": "user", "action": "add", "id": "1052690741874401360", "reason": "Confirmed scam reports"},
        headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.get_json()["changed"] is True

    with pytest.raises(PermissionError, match="reviewed application"):
        developer_portal.create_key("42", "generic blacklist", ["blacklist:write"])


def test_webhook_configuration_requires_https_public_urls_and_keeps_the_secret(application_store):
    grant(scopes=("warns:read",))
    developer_portal.accept_policy("42")
    app_id = submit_application(signed_in_client("42")).get_json()["application"]["id"]
    developer_applications.review_application(
        app_id,
        "approved",
        scopes=["warns:read"],
        actor_id=OWNER,
        allowed_scopes=list(developer_portal.ALL_SCOPES),
    )

    first = developer_applications.configure_webhook(
        app_id,
        "42",
        url="https://93.184.216.34/niko/events",
        enabled=True,
        events=["warn.created", "warns.cleared"],
    )
    assert first["enabled"] is True
    assert first["events"] == ["warn.created", "warns.cleared"]
    assert first["secret"]

    second = developer_applications.configure_webhook(
        app_id,
        "42",
        url="https://93.184.216.34/niko/events",
        enabled=False,
        events=["warn.deleted"],
    )
    assert second["secret"] == first["secret"]
    assert second["enabled"] is False

    with pytest.raises(ValueError, match="HTTPS"):
        developer_applications.configure_webhook(app_id, "42", url="http://example.com", enabled=True, events=["warn.created"])
    with pytest.raises(ValueError, match="public"):
        developer_applications.configure_webhook(app_id, "42", url="https://127.0.0.1/niko", enabled=True, events=["warn.created"])


def test_generic_keys_cannot_use_restricted_or_warn_scopes(store):
    grant(scopes=("economy:read", "blacklist:read", "warns:read"))
    developer_portal.accept_policy("42")

    with pytest.raises(PermissionError, match="reviewed application"):
        developer_portal.create_key("42", "too broad", ["blacklist:read"])
    with pytest.raises(PermissionError, match="app-bound"):
        developer_portal.create_key("42", "warn sync", ["warns:read"])


def test_webhook_events_are_signed_selected_and_guild_filtered(application_store, monkeypatch):
    app_id = "app-1"
    record = {
        "id": app_id,
        "owner_id": "42",
        "status": "approved",
        "approved_scopes": ["warns:read"],
        "webhook": {
            "url": "https://example.com/niko",
            "enabled": True,
            "events": ["warn.created"],
            "secret": "test-secret",
        },
    }
    monkeypatch.setattr(developer_applications, "approved_applications", lambda: [record])
    monkeypatch.setattr(developer_portal, "developer_access", lambda _user_id: {"enabled": True, "scopes": ["warns:read"]})

    async def shared(_app, guild_id):
        return str(guild_id) == "123"

    monkeypatch.setattr(developer_applications, "application_in_guild_async", shared)
    delivered = []

    async def capture(application_id, payload, *, attempts=3):
        delivered.append((application_id, payload))
        return True

    monkeypatch.setattr(developer_webhooks, "_deliver", capture)

    async def dispatch():
        await developer_webhooks.dispatch_guild_event_async("warn.created", "123", {"warn": {"id": 1}})
        await developer_webhooks.dispatch_guild_event_async("warn.created", "999", {"warn": {"id": 2}})
        await developer_webhooks.dispatch_guild_event_async("warn.deleted", "123", {"warn": {"id": 3}})
        await asyncio.sleep(0)

    asyncio.run(dispatch())
    assert len(delivered) == 1
    assert delivered[0][1]["guild_id"] == "123"

    monkeypatch.setattr(developer_portal, "developer_access", lambda _user_id: {"enabled": True, "scopes": []})
    asyncio.run(dispatch())
    assert len(delivered) == 1
    assert delivered[0][1]["type"] == "warn.created"
    assert delivered[0][1]["application_id"] == app_id

    body = '{"hello":"world"}'
    expected = hmac.new(b"test-secret", b"123." + body.encode(), hashlib.sha256).hexdigest()
    assert developer_webhooks._signature("test-secret", 123, body) == expected


def test_owner_access_is_implicit_and_full(store):
    access = developer_portal.developer_access(OWNER)

    assert access["enabled"] is True
    assert access["is_owner"] is True
    assert access["policy_accepted"] is True
    assert access["scopes"] == list(developer_portal.ALL_SCOPES)


def test_portal_blocks_key_creation_until_the_guidelines_are_accepted(store):
    grant(scopes=("economy:read",))
    client = signed_in_client("42")
    payload = {"name": "migration", "scopes": ["economy:read"]}

    blocked = client.post("/api/developer/keys", json=payload, headers={"X-CSRF-Token": "test-csrf"})
    assert blocked.status_code == 403
    assert "guidelines" in blocked.get_json()["error"]

    agreed = client.post("/api/developer/agree", headers={"X-CSRF-Token": "test-csrf"})
    assert agreed.status_code == 200
    assert agreed.get_json()["access"]["policy_accepted"] is True

    created = client.post("/api/developer/keys", json=payload, headers={"X-CSRF-Token": "test-csrf"})
    assert created.status_code == 201
    secret = created.get_json()["secret"]
    assert secret.startswith("niko_dev_")

    listed = client.get("/api/developer/keys").get_json()["keys"]
    assert len(listed) == 1
    assert listed[0]["prefix"] == secret[:18]
    assert "hash" not in listed[0]


def test_only_the_owner_can_manage_developer_access(store):
    owner = signed_in_client(OWNER)
    grant_response = owner.put(
        "/api/developer/access/42",
        json={"scopes": ["economy:read"], "notes": "Economy migration"},
        headers={"X-CSRF-Token": "test-csrf"},
    )
    assert grant_response.status_code == 200
    assert grant_response.get_json()["access"]["scopes"] == ["economy:read"]

    roster = owner.get("/api/developer/access")
    assert roster.status_code == 200
    assert roster.get_json()["developers"][0]["user_id"] == "42"

    developer = signed_in_client("42")
    assert developer.get("/api/developer/access").status_code == 403
    assert developer.get("/api/developer/me").get_json()["access"]["enabled"] is True
