"""Temporary IP-bound API keys and staff login sessions issued over MCP."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import mcp_keys  # noqa: E402
from webapp import app, auth, config, mcp_server, test_access  # noqa: E402
from webapp.developer import portal  # noqa: E402
from webapp.developer import store as portal_store  # noqa: E402

OWNER = "1052690741874401360"


@pytest.fixture(autouse=True)
def isolated_access(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.delenv("DEVELOPER_API_KEY_PEPPER", raising=False)
    monkeypatch.setattr(mcp_keys, "LOCAL_PATH", str(tmp_path / "mcp_keys.db"))
    monkeypatch.setattr(mcp_keys, "_LOCAL_READY", False)
    monkeypatch.setattr(test_access, "OWNER_IDS", {int(OWNER)})
    monkeypatch.setattr(portal, "is_owner_id", lambda user_id: str(user_id) == OWNER)
    monkeypatch.setattr(auth, "_current_user_blacklist_entry", lambda: None)
    portal_store.reset()
    yield
    portal_store.reset()
    monkeypatch.setattr(mcp_keys, "_LOCAL_READY", False)


def _tool_call(client, arguments):
    owner_key = mcp_keys.local_rotate("owner", "Owner")["key"]
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "niko_create_test_access", "arguments": arguments},
        },
        headers={"Authorization": f"Bearer {owner_key}"},
    )
    assert response.status_code == 200
    result = response.get_json()["result"]
    if result["isError"]:
        raise AssertionError(result["content"][0]["text"])
    return json.loads(result["content"][0]["text"])


def _login(client, login_url, remote_addr="127.0.0.1"):
    parsed = urlsplit(login_url)
    target = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    return client.get(
        target,
        base_url="https://localhost",
        environ_base={"REMOTE_ADDR": remote_addr},
    )


def test_mcp_exposes_test_access_tool():
    owner_key = mcp_keys.local_rotate("owner", "Owner")["key"]
    response = app.test_client().post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Authorization": f"Bearer {owner_key}"},
    )

    tools = {tool["name"]: tool for tool in response.get_json()["result"]["tools"]}
    tool = tools["niko_create_test_access"]
    assert tool["inputSchema"]["required"] == ["kind", "ip"]
    assert tool["inputSchema"]["properties"]["kind"]["enum"] == ["api_key", "session"]


def test_session_login_uses_the_requested_staff_role_and_is_ip_bound():
    client = app.test_client()
    issued = _tool_call(
        client,
        {
            "kind": "session",
            "ip": "127.0.0.1",
            "role": "support",
            "ttl_seconds": 300,
            "next": "/dashboard/staff",
        },
    )

    denied = _login(client, issued["login_url"], remote_addr="198.51.100.8")
    assert denied.status_code == 403
    assert "different IP" in denied.get_json()["error"]

    signed_in = _login(client, issued["login_url"])
    assert signed_in.status_code == 302
    assert signed_in.headers["Location"].endswith("/dashboard/staff")

    status = client.get("/auth/status", base_url="https://localhost").get_json()
    assert status["authenticated"] is True
    assert status["owner"] is False

    # The staff API reads the same test role, so a support session cannot open
    # the owner-only MCP configuration page.
    assert client.get("/api/staff/mcp", base_url="https://localhost").status_code == 403


def test_owner_session_can_open_owner_only_pages():
    client = app.test_client()
    issued = _tool_call(
        client,
        {
            "kind": "session",
            "ip": "127.0.0.1",
            "role": "owner",
            "ttl_seconds": 300,
            "next": "/dashboard/staff",
        },
    )

    assert _login(client, issued["login_url"]).status_code == 302
    assert client.get("/api/staff/mcp", base_url="https://localhost").status_code == 200


def test_api_key_is_bound_to_the_address_and_expires():
    client = app.test_client()
    issued = _tool_call(
        client,
        {
            "kind": "api_key",
            "ip": "127.0.0.1",
            "scopes": ["economy:read", "users:read"],
            "ttl_seconds": 300,
            "name": "staff-page test",
        },
    )
    raw_key = issued["key"]
    assert raw_key.startswith("niko_dev_")
    assert issued["scopes"] == ["economy:read", "users:read"]

    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        authenticated = portal.authenticate(raw_key)
    assert authenticated is not None
    assert authenticated["scopes"] == ["economy:read", "users:read"]
    assert authenticated["key"]["test"] is True
    assert authenticated["key"]["ip"] == "127.0.0.1"
    assert authenticated["key"]["expires_at"] > time.time()

    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "198.51.100.9"}):
        assert portal.authenticate(raw_key) is None

    with portal._LOCK:
        document = portal._load()
        document["keys"][authenticated["key"]["id"]]["expires_at"] = time.time() - 1
        portal._save(document)
    with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        assert portal.authenticate(raw_key) is None


def test_api_key_uses_the_forwarded_client_address_from_the_supervisor():
    client = app.test_client()
    issued = _tool_call(
        client,
        {
            "kind": "api_key",
            "ip": "203.0.113.5",
            "scopes": ["economy:read"],
            "ttl_seconds": 300,
        },
    )

    with app.test_request_context(
        "/",
        headers={"X-Forwarded-For": "203.0.113.5"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    ):
        assert portal.authenticate(issued["key"]) is not None

    with app.test_request_context(
        "/",
        headers={"X-Forwarded-For": "203.0.113.6"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    ):
        assert portal.authenticate(issued["key"]) is None


def test_test_access_rejects_invalid_inputs():
    client = app.test_client()

    for arguments in (
        {"kind": "session", "ip": "not-an-ip", "role": "support"},
        {"kind": "session", "ip": "127.0.0.1", "role": "not-a-role"},
        {"kind": "api_key", "ip": "127.0.0.1", "scopes": []},
        {"kind": "api_key", "ip": "127.0.0.1", "scopes": ["not:a:scope"]},
        {"kind": "session", "ip": "127.0.0.1", "role": "support", "ttl_seconds": 10},
    ):
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "niko_create_test_access",
                    "arguments": arguments,
                },
            },
            headers={"Authorization": f"Bearer {mcp_keys.local_rotate()['key']}"},
        )
        result = response.get_json()["result"]
        assert result["isError"] is True


def test_expired_test_session_does_not_fall_back_to_a_normal_login():
    client = app.test_client()
    with client.session_transaction() as flask_session:
        flask_session["user"] = {"id": OWNER}
        flask_session[test_access.SESSION_KEY] = {
            "kind": "session",
            "role": "owner",
            "ip": "127.0.0.1",
            "expires_at": time.time() - 1,
            "user_id": OWNER,
        }

    # The first request clears the stale test marker and its user identity.
    response = client.get(
        "/auth/status",
        base_url="https://localhost",
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert response.get_json()["authenticated"] is False
