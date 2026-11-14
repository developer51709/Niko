"""Owner MCP endpoint, database key storage, and direct deployment."""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import mcp_keys  # noqa: E402
from webapp import app, config, mcp_deploy, mcp_server, updates  # noqa: E402
from webapp.routes import mcp_routes  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_key_db(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_keys, "LOCAL_PATH", str(tmp_path / "mcp_keys.db"))
    monkeypatch.setattr(mcp_keys, "_LOCAL_READY", False)
    monkeypatch.delenv("MCP_API_KEY", raising=False)
    yield
    monkeypatch.setattr(mcp_keys, "_LOCAL_READY", False)


def _initialize(client, token: str):
    return client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def _owner_session(client, csrf="csrf-token"):
    with client.session_transaction() as session:
        session["user"] = {"id": "42", "username": "tester", "global_name": "Tester"}
        session["access_token"] = "token"
        session["token_exp"] = time.time() + 3600
        session["csrf_token"] = csrf


def test_mcp_ignores_environment_keys(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "env-only")
    monkeypatch.setenv("BETA_UPDATE_TOKEN", "beta-only")
    client = app.test_client()

    assert _initialize(client, "env-only").status_code == 401
    assert _initialize(client, "beta-only").status_code == 401


def test_mcp_requires_a_database_backed_key():
    client = app.test_client()
    assert client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"}).status_code == 401

    owner_key = mcp_keys.local_rotate()["key"]
    assert _initialize(client, "wrong").status_code == 401
    response = _initialize(client, owner_key)
    assert response.status_code == 200
    assert response.get_json()["result"]["serverInfo"]["name"] == "niko"
    assert response.headers["Mcp-Session-Id"]


def test_owner_key_is_stored_only_as_a_salted_pbkdf2_hash():
    generated = mcp_keys.local_rotate("42", "Tester")
    raw_key = generated["key"]
    assert raw_key.startswith(mcp_keys.KEY_PREFIX)
    assert len(raw_key) > 32

    with sqlite3.connect(mcp_keys.LOCAL_PATH) as connection:
        row = connection.execute(
            "SELECT key_prefix, key_hash, salt, iterations FROM mcp_api_key WHERE id = 'owner'"
        ).fetchone()

    assert row is not None
    prefix, stored_hash, salt, iterations = row
    assert stored_hash != raw_key
    assert len(stored_hash) == 64
    assert len(salt) == 32
    assert int(iterations) >= 100_000
    assert raw_key not in Path(mcp_keys.LOCAL_PATH).read_bytes().decode("latin-1")
    assert prefix in raw_key
    assert mcp_keys.local_verify(raw_key) is True
    assert mcp_keys.local_verify(raw_key + "x") is False


def test_rotation_invalidates_the_previous_key_immediately():
    old_key = mcp_keys.local_rotate()["key"]
    new_key = mcp_keys.local_rotate()["key"]

    client = app.test_client()
    assert _initialize(client, old_key).status_code == 401
    assert _initialize(client, new_key).status_code == 200


def test_mcp_lists_deployment_and_diagnostics_tools():
    owner_key = mcp_keys.local_rotate()["key"]
    response = app.test_client().post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        headers={"Authorization": f"Bearer {owner_key}"},
    )

    assert response.status_code == 200
    tools = {tool["name"] for tool in response.get_json()["result"]["tools"]}
    assert {
        "niko_status",
        "niko_logs",
        "niko_error_reports",
        "niko_set_error_report_status",
        "niko_incidents",
        "niko_update_incident",
        "niko_deploy",
    } <= tools


def test_mcp_subdomain_is_a_known_site_host(monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.example")
    monkeypatch.setenv("SUBDOMAIN_ROUTING", "true")
    monkeypatch.setenv("MCP_SUBDOMAIN", "mcp")

    assert config.is_mcp_host("mcp.niko.example") is True
    assert config.is_mcp_host("niko.example") is False


def test_mcp_host_root_is_the_landing_page(monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.example")
    response = app.test_client().get("/", base_url="https://mcp.niko.example")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "MCP Server." in response.get_data(as_text=True)


def test_mcp_origin_overrides_the_generated_host(monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.example")
    monkeypatch.setenv("MCP_ORIGIN", "https://automation.example")

    response = app.test_client().get("/api/staff/mcp")
    assert response.status_code == 401
    assert mcp_server.endpoint() == "https://automation.example/mcp"


def test_staff_mcp_metadata_is_owner_only(monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.example")
    owner_key = mcp_keys.local_rotate("42", "Tester")["key"]
    monkeypatch.setattr(mcp_routes, "_current_staff_role", lambda: "support")

    client = app.test_client()
    _owner_session(client)
    assert client.get("/api/staff/mcp").status_code == 403

    monkeypatch.setattr(mcp_routes, "_current_staff_role", lambda: "owner")
    response = client.get("/api/staff/mcp")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["configured"] is True
    assert payload["endpoint"] == "https://mcp.niko.example/mcp"
    assert payload["key"]["key_prefix"] in owner_key
    assert payload["key"]["algorithm"] == mcp_keys.ALGORITHM
    assert all("name" in tool for tool in payload["tools"])
    assert owner_key not in json.dumps(payload)


def test_staff_can_rotate_the_key_without_a_restart(monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://niko.example")
    monkeypatch.setattr(mcp_routes, "_current_staff_role", lambda: "owner")
    client = app.test_client()
    _owner_session(client)
    old_key = mcp_keys.local_rotate()["key"]

    assert client.post("/api/staff/mcp/key").status_code == 403
    response = client.post("/api/staff/mcp/key", headers={"X-CSRF-Token": "csrf-token"})
    assert response.status_code == 200
    generated = response.get_json()
    new_key = generated["key"]
    assert "no-store" in response.headers["Cache-Control"]
    assert new_key != old_key
    assert generated["key_prefix"] in new_key

    # The next request reads the replacement row; no process restart is needed.
    assert _initialize(client, old_key).status_code == 401
    assert _initialize(client, new_key).status_code == 200

    metadata = client.get("/api/staff/mcp").get_json()
    assert metadata["key"]["last_used_at"] is not None
    assert new_key not in json.dumps(metadata)


def test_direct_deploy_writes_a_website_file(monkeypatch, tmp_path):
    root = tmp_path
    (root / "src" / "website" / "dist").mkdir(parents=True)
    monkeypatch.setattr(updates, "ROOT", root)
    monkeypatch.setattr(updates, "DATA_DIR", root / "data" / "updates")

    result = mcp_deploy.apply_payloads([
        {"path": "src/website/dist/index.html", "content": "<h1>deployed</h1>"},
    ])

    assert result["ok"] is True
    assert result["areas"]["website"]["written"] == 1
    assert (root / "src" / "website" / "dist" / "index.html").read_text() == "<h1>deployed</h1>"
    assert updates.last_run()["source"] == "mcp"


def test_mcp_deploy_tool_uses_the_direct_path(monkeypatch, tmp_path):
    (tmp_path / "src" / "website" / "dist").mkdir(parents=True)
    monkeypatch.setattr(updates, "ROOT", tmp_path)
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "data" / "updates")
    owner_key = mcp_keys.local_rotate()["key"]

    response = app.test_client().post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "niko_deploy",
                "arguments": {
                    "files": [{"path": "src/website/dist/index.html", "content": "<p>mcp</p>"}],
                },
            },
        },
        headers={"Authorization": f"Bearer {owner_key}"},
    )

    result = response.get_json()["result"]
    assert result["isError"] is False
    payload = json.loads(result["content"][0]["text"])
    assert payload["ok"] is True
    assert (tmp_path / "src" / "website" / "dist" / "index.html").read_text() == "<p>mcp</p>"


def test_direct_deploy_refuses_paths_outside_the_update_areas():
    with pytest.raises(ValueError, match="outside the deployable areas"):
        mcp_deploy.apply_payloads([{"path": "README.md", "content": "no"}])


def test_direct_deploy_refuses_removing_an_additive_config_file(monkeypatch, tmp_path):
    config_file = tmp_path / "src" / "config" / "ids.py"
    config_file.parent.mkdir(parents=True)
    config_file.write_text("OWNER_IDS = {1}\n", encoding="utf-8")
    monkeypatch.setattr(updates, "ROOT", tmp_path)
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "data" / "updates")

    with pytest.raises(ValueError, match="additive area and cannot be removed"):
        mcp_deploy.apply_payloads([
            {"path": "src/config/ids.py", "status": "removed"},
        ])

    assert config_file.exists()


def _github_blob_sha(body: bytes) -> str:
    import hashlib

    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


class _GitHubResponse:
    def __init__(self, status_code=200, payload=None, content=b""):
        self.status_code = status_code
        self._payload = payload
        self.content = content

    def json(self):
        return self._payload


def test_the_mcp_tool_list_includes_commit_deployment():
    owner_key = mcp_keys.local_rotate()["key"]
    response = app.test_client().post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 50, "method": "tools/list"},
        headers={"Authorization": f"Bearer {owner_key}"},
    )

    tools = {tool["name"]: tool for tool in response.get_json()["result"]["tools"]}
    assert "niko_deploy_commit" in tools
    assert "commit SHA" in tools["niko_deploy_commit"]["description"]


def test_commit_deploy_fetches_files_instead_of_carrying_them_in_json(monkeypatch, tmp_path):
    body = b"<h1>from a commit</h1>\n"
    commit_sha = "a" * 40
    commit_payload = {
        "commit": {"message": "Update the landing page\n\nBody text"},
        "files": [{
            "filename": "src/website/dist/index.html",
            "status": "modified",
            "sha": _github_blob_sha(body),
        }],
    }
    calls = []

    def fake_github_get(url, *, headers=None):
        calls.append(url)
        if "/commits/" in url:
            return _GitHubResponse(payload=commit_payload)
        return _GitHubResponse(content=body)

    (tmp_path / "src" / "website" / "dist").mkdir(parents=True)
    monkeypatch.setattr(updates, "ROOT", tmp_path)
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "data" / "updates")
    monkeypatch.setattr(mcp_deploy, "_github_get", fake_github_get)

    result = mcp_deploy.apply_commit(commit_sha)

    assert result["ok"] is True
    assert result["commit"] == commit_sha
    assert result["commit_message"] == "Update the landing page"
    assert result["areas"]["website"]["written"] == 1
    assert (tmp_path / "src" / "website" / "dist" / "index.html").read_bytes() == body
    assert any("/commits/" in url for url in calls)
    assert any("raw.githubusercontent.com" in url for url in calls)


def test_commit_deploy_checks_the_blob_hash(monkeypatch, tmp_path):
    body = b"print('tampered')\n"
    commit_payload = {
        "commit": {"message": "Update a file"},
        "files": [{
            "filename": "src/website/dist/index.html",
            "status": "modified",
            "sha": "0" * 40,
        }],
    }

    def fake_github_get(url, *, headers=None):
        if "/commits/" in url:
            return _GitHubResponse(payload=commit_payload)
        return _GitHubResponse(content=body)

    (tmp_path / "src" / "website" / "dist").mkdir(parents=True)
    monkeypatch.setattr(updates, "ROOT", tmp_path)
    monkeypatch.setattr(updates, "DATA_DIR", tmp_path / "data" / "updates")
    monkeypatch.setattr(mcp_deploy, "_github_get", fake_github_get)

    with pytest.raises(RuntimeError, match="blob SHA"):
        mcp_deploy.apply_commit("b" * 40)

    assert not (tmp_path / "src" / "website" / "dist" / "index.html").exists()
