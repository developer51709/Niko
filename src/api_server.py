"""Start the dashboard API alongside the Discord bot.

Keeping this in a tiny module makes the process boundary obvious and makes the
server startup easy to change without touching Discord event handling.
"""

from __future__ import annotations

import os
import threading


def start_api_server(bot=None) -> threading.Thread:
    """Start Flask in a daemon thread and return the thread for diagnostics."""
    from website import app, configure_bot

    configure_bot(bot)

    port = int(os.environ.get("PORT", "5000"))

    def serve() -> None:
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, threaded=True)

    thread = threading.Thread(target=serve, name="niko-api", daemon=True)
    thread.start()
    return thread