"""Start the dashboard API alongside the Discord bot.

Keeping this in a tiny module makes the process boundary obvious and makes the
server startup easy to change without touching Discord event handling.
"""

from __future__ import annotations

import logging
import os
import threading


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


def start_api_server(bot=None) -> threading.Thread:
    """Start Flask in a daemon thread and return the thread for diagnostics."""
    from webapp import app, configure_bot

    configure_bot(bot)

    port = int(os.environ.get("PORT", "5000"))

    def serve() -> None:
        # Flask/Werkzeug logs every successful request at INFO. The dashboard
        # polls /api/health regularly, so filter routine access lines while
        # retaining 4xx/5xx request failures and server errors.
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.INFO)
        if not any(isinstance(item, _QuietSuccessfulRequests) for item in werkzeug_logger.filters):
            werkzeug_logger.addFilter(_QuietSuccessfulRequests())
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

    thread = threading.Thread(target=serve, name="niko-api", daemon=True)
    thread.start()
    return thread