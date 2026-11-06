"""The dashboard child forwards live-bot routes and degrades when the bot is down."""

from __future__ import annotations

import json
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from werkzeug.test import Client  # noqa: E402
from werkzeug.wrappers import Response  # noqa: E402

from web_bridge import BotBridge, BotRoute, should_forward  # noqa: E402


class _Upstream(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _format, *_args):
        pass

    def do_GET(self):
        parts = urlsplit(self.path)
        if parts.path == "/api/status":
            body = json.dumps(
                {
                    "from": "bot",
                    "query": parts.query,
                    "cookie": self.headers.get("Cookie"),
                    "proto": self.headers.get("X-Forwarded-Proto"),
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Set-Cookie", "a=1; Path=/")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()


def _local_app(environ, start_response):
    body = f"local:{environ.get('PATH_INFO')}".encode()
    start_response(
        "200 OK",
        [("Content-Type", "text/plain"), ("Content-Length", str(len(body)))],
    )
    return [body]


def _closed_port() -> int:
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def _serve_upstream():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Upstream)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, int(server.server_address[1])


def test_only_live_bot_api_paths_are_forwarded():
    assert should_forward("/api/status") is True
    assert should_forward("/api/discord/interactions") is True
    assert should_forward("/api/owner/logs") is False
    assert should_forward("/api/updates/force") is False
    assert should_forward("/api/updates/push") is False
    assert should_forward("/api/health") is False
    assert should_forward("/dashboard") is False
    assert should_forward("/assets/app.js") is False


def test_a_restarted_bot_route_is_not_pinned_to_the_startup_port(monkeypatch):
    asked = []

    def route(command, timeout):
        asked.append(command)
        return {"bot_api_port": 6001}

    monkeypatch.setattr("utils.supervisor_control.request", route)
    bot_route = BotRoute(env_port=6000)

    assert bot_route.port() == 6000
    bot_route.invalidate()
    assert bot_route.port() == 6001
    assert asked == ["route"]


def test_forwarded_request_keeps_the_path_headers_and_cookies():
    server, port = _serve_upstream()
    try:
        client = Client(BotBridge(_local_app, BotRoute(env_port=port)), Response)
        client.set_cookie("session", "abc")
        response = client.get(
            "/api/status?view=all",
            headers={"X-Forwarded-Proto": "https"},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert payload == {
            "from": "bot",
            "query": "view=all",
            "cookie": "session=abc",
            "proto": "https",
        }
        assert response.headers.get("Set-Cookie") == "a=1; Path=/"
    finally:
        server.shutdown()
        server.server_close()


def test_local_paths_do_not_reach_the_bot():
    server, port = _serve_upstream()
    try:
        client = Client(BotBridge(_local_app, BotRoute(env_port=port)), Response)
        response = client.get("/api/owner/logs")
        assert response.status_code == 200
        assert response.get_data(as_text=True) == "local:/api/owner/logs"
        assert client.get("/").get_data(as_text=True) == "local:/"
    finally:
        server.shutdown()
        server.server_close()


def test_a_bot_that_is_not_serving_gets_a_bounded_503():
    client = Client(BotBridge(_local_app, BotRoute(env_port=_closed_port())), Response)
    response = client.get("/api/status")
    assert response.status_code == 503
    assert response.headers.get("Retry-After") == "1"
    payload = response.get_json()
    assert payload["error"] == "service unavailable"
    assert payload["reason"] == "the bot child is not serving"
    # The dashboard shell still answers while the bot child is down.
    assert client.get("/").status_code == 200
