"""The dashboard child reaches Discord through the bot child.

Since the supervisor split, the dashboard has no Discord client of its own. On a
host whose address Cloudflare has banned for the Discord API, every call it made
directly failed — the OAuth token exchange, the user fetch, session refreshes and
membership reads — while the bot kept answering over the egress its failover had
armed. These tests cover the relay that closes that gap: the bot child's
authenticated endpoint, the dashboard-side call, and a sign-in that completes in
a process with no bot object at all.
"""

import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests as req

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from werkzeug.serving import make_server  # noqa: E402

from webapp import app, config, discord_api, runtime  # noqa: E402
from webapp.routes import auth_routes, internal_routes  # noqa: E402
from web_bridge import should_forward  # noqa: E402


def _response(status=200, body=b'{"id": "1"}', reason="OK", content_type="application/json"):
    response = req.Response()
    response.status_code = status
    response.reason = reason
    response.headers.update({"Content-Type": content_type})
    response._content = body
    response.url = "https://discord.com/api/v10/users/@me"
    return response


@pytest.fixture
def run_token(monkeypatch):
    monkeypatch.setenv(internal_routes.TOKEN_ENV, "run-token")
    return "run-token"


@pytest.fixture
def bot_child(monkeypatch):
    """Serve the dashboard app the way the bot child does, over loopback.

    The relay endpoint refuses to answer in a process without a bot, and the
    dashboard-side caller only relays when it has none. Both are this process in
    a test, so the "bot child" side installs a stand-in bot for the duration of
    its own request, exactly like the child that owns the gateway.
    """
    calls = []

    def fake_discord_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return _response(body=b'{"id": "42", "username": "tester"}')

    monkeypatch.setattr(internal_routes, "discord_request", fake_discord_request)
    state = {"bot": object()}
    lock = threading.Lock()

    def as_bot_child(environ, start_response):
        with lock:
            previous = runtime._discord_bot
            runtime._discord_bot = state["bot"]
            try:
                return app(environ, start_response)
            finally:
                runtime._discord_bot = previous

    server = make_server("127.0.0.1", 0, as_bot_child, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield SimpleNamespace(port=server.server_port, calls=calls)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class _Route:
    def __init__(self, port):
        self._port = port
        self.invalidated = False

    def port(self):
        return self._port

    def invalidate(self):
        self.invalidated = True


def test_the_public_bridge_never_exposes_the_relay():
    """A public request must not be forwarded into the bot's egress."""
    assert should_forward("/api/internal/discord") is False


def test_the_relay_refuses_a_caller_without_the_run_credential(monkeypatch):
    monkeypatch.setenv(internal_routes.TOKEN_ENV, "run-token")
    monkeypatch.setattr(runtime, "_discord_bot", object())

    response = app.test_client().post(
        "/api/internal/discord",
        json={"method": "GET", "url": "https://discord.com/api/v10/users/@me"},
    )

    assert response.status_code == 403


def test_the_relay_refuses_a_public_process_with_no_bot(run_token, monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", None)

    response = app.test_client().post(
        "/api/internal/discord",
        headers={internal_routes.TOKEN_HEADER: run_token},
        json={"method": "GET", "url": "https://discord.com/api/v10/users/@me"},
    )

    assert response.status_code == 503


def test_the_relay_only_carries_discord_api_calls(run_token, monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", object())
    monkeypatch.setattr(
        internal_routes,
        "discord_request",
        lambda *args, **kwargs: pytest.fail("a non-Discord URL must never be relayed"),
    )

    response = app.test_client().post(
        "/api/internal/discord",
        headers={internal_routes.TOKEN_HEADER: run_token},
        json={"method": "GET", "url": "https://example.com/collect"},
    )

    assert response.status_code == 400


def test_the_dashboard_child_makes_the_call_in_the_bot_child(run_token, bot_child, monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", None)
    monkeypatch.setattr(discord_api, "_relay_route", _Route(bot_child.port))
    monkeypatch.setattr(
        discord_api.req, "get",
        lambda *args, **kwargs: pytest.fail(
            "the banned host must not be asked to reach Discord directly"
        ),
    )

    response = discord_api.discord_request(
        "POST",
        "https://discord.com/api/oauth2/token",
        data={"grant_type": "authorization_code", "code": "abc"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    assert response.status_code == 200
    assert response.json()["id"] == "42"
    method, url, kwargs = bot_child.calls[0]
    assert (method, url) == ("POST", "https://discord.com/api/oauth2/token")
    assert kwargs["data"] == {"grant_type": "authorization_code", "code": "abc"}
    assert kwargs["headers"] == {"Content-Type": "application/x-www-form-urlencoded"}


def test_a_blocked_answer_travels_back_untouched(run_token, bot_child, monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", None)
    monkeypatch.setattr(discord_api, "_relay_route", _Route(bot_child.port))
    monkeypatch.setattr(internal_routes, "discord_request", lambda *a, **k: _response(
        status=429,
        body=b'<html><div id="cf-error-details"><h1>Error 1015</h1></div></html>',
        reason="Too Many Requests",
        content_type="text/html",
    ))

    response = discord_api.discord_request("GET", "https://discord.com/api/v10/users/@me")

    # The dashboard reports Discord's own answer; it does not turn a block into
    # a dashboard error, because that is what the caller already handles.
    assert response.status_code == 429
    assert not response.ok
    assert "1015" in response.text


def test_the_internal_token_alone_does_not_enable_the_relay(monkeypatch):
    """Production shipped without a credential for the dashboard child.

    The supervisor used to hand `NIKO_INTERNAL_TOKEN` only to the bot and db
    children, so the web child silently took the direct path and every sign-in
    left the banned host — HTTP 429 from Cloudflare, with nothing in the log but
    the answer itself.  The relay needs its own credential; the internal one
    must not stand in for it.
    """
    monkeypatch.delenv(discord_api.RELAY_TOKEN_ENV, raising=False)
    monkeypatch.setenv("NIKO_INTERNAL_TOKEN", "bot-only-secret")
    monkeypatch.setattr(runtime, "_discord_bot", None)

    assert discord_api._relay_target() is None


def test_without_a_bot_child_the_call_is_still_made_directly(monkeypatch):
    monkeypatch.delenv(discord_api.RELAY_TOKEN_ENV, raising=False)
    monkeypatch.setattr(runtime, "_discord_bot", None)
    direct = _response(body=b'{"id": "7"}')
    monkeypatch.setattr(discord_api.req, "get", lambda *a, **k: direct)

    assert discord_api.discord_request("GET", "https://discord.com/api/v10/users/@me") is direct


def test_an_unreachable_bot_child_is_reported_as_an_unreachable_discord(run_token, monkeypatch):
    monkeypatch.setattr(runtime, "_discord_bot", None)
    route = _Route(9)  # nothing listens here
    monkeypatch.setattr(discord_api, "_relay_route", route)

    with pytest.raises(req.ConnectionError):
        discord_api.discord_request("GET", "https://discord.com/api/v10/users/@me")

    # A replaced bot child listens somewhere else; the cached port is dropped.
    assert route.invalidated is True


def test_a_sign_in_completes_in_a_process_with_no_bot(monkeypatch):
    """The OAuth callback is what was failing in production: it must relay."""
    monkeypatch.setenv("PUBLIC_URL", "https://niko.sryze.cc")
    monkeypatch.setenv("DISCORD_REDIRECT_URI", "https://niko.sryze.cc/auth/callback")
    monkeypatch.setattr(config, "DISCORD_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(runtime, "_discord_bot", None)

    seen = []

    def fake_relay(method, url, kwargs):
        seen.append((method, url, kwargs))
        if url.endswith("/oauth2/token"):
            return _response(body=(
                b'{"access_token": "member-token", "refresh_token": "refresh",'
                b' "expires_in": 604800, "scope": "identify guilds guilds.join"}'
            ))
        return _response(body=b'{"id": "42", "username": "tester"}')

    monkeypatch.setattr(discord_api, "_relay_discord_request", fake_relay)

    with app.test_client() as client:
        state = auth_routes._encode_oauth_state("/dashboard", "", "niko.sryze.cc")
        response = client.get(
            f"/auth/callback?code=abc&state={state}", base_url="https://niko.sryze.cc"
        )
        # The session has to survive the redirect: reading it back on the next
        # request is what proves the sign-in really completed.
        status = client.get("/auth/status", base_url="https://niko.sryze.cc")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert status.status_code == 200
    assert status.json["authenticated"] is True
    assert status.json["user"]["id"] == "42"
    # Both legs of the sign-in went to the bot child, not to Discord directly.
    assert [url for _, url, _ in seen] == [
        "https://discord.com/api/oauth2/token",
        "https://discord.com/api/v10/users/@me",
    ]
