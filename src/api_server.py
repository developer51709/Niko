"""Start the dashboard API alongside the Discord bot.

Keeping this in a tiny module makes the process boundary obvious and makes the
server startup easy to change without touching Discord event handling.

The server object is kept rather than hidden inside ``app.run`` because the
owner's update page needs three things a blocking ``app.run`` cannot offer: the
Flask app must be replaceable while the socket keeps accepting (an API update),
the socket must be handable to a successor process (a bot update), and the
accept loop must be stoppable without killing the process.
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


def start_api_server(bot=None, fd: int | None = None, port: int | None = None) -> threading.Thread:
    """Serve Flask on a daemon thread.

    ``fd`` is an inherited listening socket from the process that is handing
    over. Using it means the successor accepts connections on the same socket,
    with no gap and no rebinding, while the predecessor stops accepting.

    ``port`` exists for diagnostics and tests; the process uses ``PORT``.
    """
    from webapp import configure_bot

    configure_bot(bot)

    port = int(port or os.environ.get("PORT", "5000"))
    server = make_server("0.0.0.0", port, _flask_app(), threaded=True, fd=fd)

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
        logging.info("Startup", "Dashboard API adopted the listening socket from the predecessor.")
    return _thread


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
        return int(_server.port)


def stop_serving() -> None:
    """Stop accepting and close this process's copy of the listening socket.

    A successor holding the same socket keeps the listener alive; the port is
    never unbound.
    """
    global _server
    with _lock:
        server = _server
        _server = None
    if server is None:
        return
    try:
        server.shutdown()
    except Exception:
        pass
    try:
        server.server_close()
    except Exception:
        pass
