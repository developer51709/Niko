"""Start the dashboard API alongside the Discord bot.

Keeping this in a tiny module makes the process boundary obvious and makes the
server startup easy to change without touching Discord event handling.

The server object is kept rather than hidden inside ``app.run`` because the
owner's update page needs two things a blocking ``app.run`` cannot offer: the
Flask app must be replaceable while the socket keeps accepting (an API update),
and the listening socket must survive a restart of the process (a bot update) by
being inherited instead of rebound — see :mod:`utils.handoff`.
"""

from __future__ import annotations

import logging
import os
import threading

from werkzeug.serving import make_server


class _QuietSuccessfulRequests(logging.Filter):
    """Hide routine 2xx/3xx access lines without hiding request failures."""

    def filter(self, record: logging.LogRecord) -> bool:
        for value in getattr(record, "args", ()) if isinstance(getattr(record, "args", ()), tuple) else ():
            try:
                status = int(value)
            except (TypeError, ValueError):
                continue
            return status >= 400
        return True


#: The live werkzeug server; ``None`` before startup and after a handoff.
_server = None
_thread: threading.Thread | None = None
_lock = threading.Lock()


def _flask_app():
    from webapp import app

    return app


def start_api_server(
    bot=None,
    fd: int | None = None,
    port: int | None = None,
    host: str = "0.0.0.0",
) -> threading.Thread:
    """Serve Flask on a daemon thread.

    ``fd`` is the listening socket this process inherited from the image it
    replaced (an in-place restart, see :mod:`utils.handoff`). Using it means the
    new image accepts connections on the same socket with no gap and no
    rebinding: the port is never unbound, so nothing can race to rebind it.

    ``port`` and ``host`` exist for tests and for the supervised child, which
    binds an ephemeral loopback port behind the supervisor's proxy.  A direct
    process keeps the historical ``PORT`` / ``0.0.0.0`` behaviour.
    """
    from webapp import configure_bot, locale_feed

    configure_bot(bot)
    # Bot wording is refreshed from beta on a timer as well as on demand: the bot
    # answers Discord messages whether or not anyone has the dashboard open.
    try:
        locale_feed.start_sync_loop(bot)
    except TypeError:
        # A bot-core update can start this server against the previous image's
        # feed, which takes no bot argument; its default still runs the loop.
        locale_feed.start_sync_loop()

    port = int(os.environ.get("PORT", "5000") if port is None else port)
    server = make_server(host, port, _flask_app(), threaded=True, fd=fd)

    def serve() -> None:
        # Flask/Werkzeug logs every successful request at INFO. The dashboard
        # polls /api/health regularly, so filter routine access lines while
        # retaining 4xx/5xx request failures and server errors.
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.INFO)
        if not any(isinstance(item, _QuietSuccessfulRequests) for item in werkzeug_logger.filters):
            werkzeug_logger.addFilter(_QuietSuccessfulRequests())
        server.serve_forever()

    global _server, _thread
    with _lock:
        _server = server
        _thread = threading.Thread(target=serve, name="niko-api", daemon=True)
        _thread.start()
    if fd is not None:
        # The stdlib module, not the project's ``utils.logging`` wrapper: this
        # file also builds the werkzeug filter below. Two positional strings on
        # stdlib ``logging.info`` are a format string and its arguments, which is
        # how this line used to raise "not all arguments converted" inside the
        # logging handler instead of logging anything.
        logging.getLogger("Startup").info(
            "Dashboard API adopted the listening socket from the predecessor."
        )
    return _thread


def stop_api_server(timeout: float = 5.0) -> None:
    """Stop the daemon server. Intended for tests and clean supervised shutdown."""
    global _server, _thread
    with _lock:
        server, thread = _server, _thread
        _server = None
        _thread = None
    if server is not None:
        server.shutdown()
        server.server_close()
    if thread is not None and thread is not threading.current_thread():
        thread.join(timeout=timeout)


def replace_app(app) -> None:
    """Swap the WSGI application under the running server.

    Werkzeug reads ``server.app`` for every request, so this changes every route
    at once. Open keep-alive connections finish their current response on the app
    they started with and pick up the new one on the next request.
    """
    with _lock:
        if _server is None:
            raise RuntimeError("The dashboard API is not serving.")
        _server.app = app


def serving() -> bool:
    """Whether this process is answering HTTP right now."""
    with _lock:
        return _server is not None


def listening_socket_fd() -> int:
    """A duplicate of the listening socket, safe to pass to a child process."""
    with _lock:
        if _server is None:
            raise RuntimeError("The dashboard API is not serving.")
        return os.dup(_server.socket.fileno())


def listening_port() -> int:
    with _lock:
        if _server is None:
            return int(os.environ.get("PORT", "5000"))
        # Werkzeug sets ``server_port`` to the port actually bound, including
        # when the caller asked for port 0 and the kernel chose one.
        return int(getattr(_server, "server_port", None) or _server.port)
