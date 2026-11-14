"""Forward live-bot API calls from the dashboard child to the bot child.

The split dashboard runs Flask without a gateway.  Routes that read the live bot
object cannot be answered there yet, so those requests are handed to the bot
child's loopback API, which runs the same Flask app with the bot attached.

This module is the Part 4A seam: stdlib only, no Flask import, so it can be
tested without building the application.  Moving these routes onto a state
mirror/RPC contract replaces it without changing the supervisor.
"""

from __future__ import annotations

import http.client
import json
import os
import socket
import time

#: Requests the dashboard child answers itself.  Everything else under
#: ``/api/`` needs the live bot object and is forwarded.  The owner console is
#: local so it stays readable while the bot child restarts, and health/config
#: are local because they do not depend on Discord being connected.
LOCAL_API_PATHS = (
    "/api/owner/logs",
    "/api/health",
    "/api/config",
    "/api/emojis",
    "/api/site/build",
    # The update feed and the beta push/recovery routes read files and env, not
    # the bot.  Keeping them in the dashboard child means beta can still serve
    # source files while its own bot child restarts, and the supervisor's
    # loopback-only force route is never reachable through the bridge.
    "/api/updates",
    # Only the bot child answers the Discord relay, and only for the supervisor's
    # per-run credential.  The dashboard child answers this path itself (with a
    # 403 for anyone who does not hold the credential) so a public request can
    # never reach the bot's egress through the bridge.
    "/api/internal",
)

#: Public pages that read the live bot's database instead of anything the
#: dashboard child owns. The challenge page is the browser half of web
#: verification: it looks up, answers and consumes the challenge row and then
#: applies the roles, so it must run where the bot and its pool do. The bare
#: ``/verify`` page is deliberately *not* forwarded — it is the always-on ad
#: entry, and it has to keep answering while the bot child restarts.
FORWARDED_PUBLIC_PREFIX = "/verify/"

#: The staff README card is drawn from the live roster: the staff rows, the
#: gateway presence behind its status, and the member's avatar. The dashboard
#: child has none of those — it was rendering every member except the seeded
#: owner as "This profile is not public right now." — so the card is rendered
#: where the data lives. The bot's own ``/bot/card.svg`` is deliberately not
#: forwarded: it reads ``bot_stats.json`` and has to survive the same restart.
STAFF_CARD_PREFIX = "/staff/"
STAFF_CARD_SUFFIX = "/card.svg"

#: Headers that describe one hop rather than the request or its response.
HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def should_forward(path: str) -> bool:
    if path.startswith(FORWARDED_PUBLIC_PREFIX):
        # A challenge token is always in the path, so the prefix matches every
        # form, image and submission and never the entry page, at ``/verify``
        # or its trailing-slash alias.
        return path.rstrip("/") != "/verify"
    if path.startswith(STAFF_CARD_PREFIX) and path.endswith(STAFF_CARD_SUFFIX):
        return True
    if not path.startswith("/api/"):
        return False
    return not any(
        path == prefix or path.startswith(prefix + "/") for prefix in LOCAL_API_PATHS
    )


class BotRoute:
    """Where the bot child's loopback API is, asked cheaply and cached.

    The supervisor knows the port because the bot child reports it when its API
    binds, so the dashboard asks over the local control socket instead of
    guessing.  A restarted bot child gets a new port; any failed forward drops
    the cache.
    """

    def __init__(self, env_port: int | None = None) -> None:
        self._port = env_port
        self._at = time.monotonic() if env_port else 0.0
        self._sock = None
        # The environment is a startup hint only. After a failed forward the
        # bot child may have a new port, and re-reading the stale hint would
        # keep the dashboard pointed at the old one forever.
        self._env_used = env_port is not None

    def invalidate(self) -> None:
        self._port = None
        self._at = 0.0
        self._sock = None

    def port(self) -> int | None:
        now = time.monotonic()
        if self._port is not None and now - self._at < 1.0:
            return self._port
        env_port = (os.environ.get("NIKO_BOT_API_PORT") or "").strip()
        if env_port.isdigit() and not self._env_used:
            self._port = int(env_port)
            self._env_used = True
            self._at = now
            return self._port
        try:
            from utils.runtime import supervisor_control

            response = supervisor_control.request("route", timeout=2.0)
        except Exception:
            return None
        port = response.get("bot_api_port") if isinstance(response, dict) else None
        if isinstance(port, int) and 1 <= port <= 65535:
            self._port = port
            self._at = now
            return port
        return None


class BotBridge:
    """WSGI middleware that forwards live-bot API calls to the bot child."""

    def __init__(self, application, route: BotRoute) -> None:
        self.application = application
        self.route = route

    def __call__(self, environ, start_response):
        if not should_forward(environ.get("PATH_INFO") or ""):
            return self.application(environ, start_response)

        port = self.route.port()
        if port is None:
            return unavailable(start_response, "the bot child is not serving")

        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query = environ.get("QUERY_STRING", "")
        target = path + (f"?{query}" if query else "")

        headers = {}
        for key, value in environ.items():
            if not key.startswith("HTTP_"):
                continue
            header = key[5:].replace("_", "-").title()
            if header.lower() in HOP_BY_HOP:
                continue
            headers[header] = value
        if environ.get("CONTENT_TYPE"):
            headers["Content-Type"] = environ["CONTENT_TYPE"]
        headers["X-Forwarded-Host"] = (
            environ.get("HTTP_X_FORWARDED_HOST") or environ.get("HTTP_HOST", "")
        )
        headers["X-Forwarded-Proto"] = (
            environ.get("HTTP_X_FORWARDED_PROTO") or environ.get("wsgi.url_scheme", "http")
        )
        # This process is the bot child's peer, so the member's own address has
        # to travel with the request: the web captcha refuses proxies and VPNs
        # by client IP, and a loopback peer would read as a private address that
        # is always allowed. The chain stays left-to-right, so the original
        # client is still first.
        peer = (environ.get("REMOTE_ADDR") or "").strip()
        if peer:
            chain = (headers.get("X-Forwarded-For") or "").strip()
            headers["X-Forwarded-For"] = f"{chain}, {peer}" if chain else peer

        body = None
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        if length:
            body = environ["wsgi.input"].read(length)

        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=300)
        try:
            connection.request(method, target, body=body, headers=headers)
            upstream = connection.getresponse()
            payload = upstream.read()
        except (ConnectionError, OSError, socket.timeout):
            self.route.invalidate()
            return unavailable(start_response, "the bot child is not serving")
        finally:
            connection.close()

        response_headers = [
            (key, value)
            for key, value in upstream.getheaders()
            if key.lower() not in HOP_BY_HOP
        ]
        start_response(f"{upstream.status} {upstream.reason}", response_headers)
        return [payload]


def unavailable(start_response, reason: str):
    body = json.dumps(
        {"error": "service unavailable", "reason": reason, "retry_after": 1}
    ).encode("utf-8")
    start_response(
        "503 Service Unavailable",
        [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Retry-After", "1"),
        ],
    )
    return [body]
