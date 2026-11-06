"""Dashboard child: the Flask app without the Discord gateway.

The supervisor runs this process next to ``bot.py`` so a dashboard restart and a
bot restart cannot take each other down.  This child owns public HTTP: the app,
static assets, auth, SEO pages, and the owner console.  Routes that read the
live bot are forwarded to the bot child's loopback API by :mod:`web_bridge`,
which keeps the full application and its webapp coupling where it already lives.

That forwarding bridge is deliberately narrow and temporary: it is the seam
recorded in Part 4A of the supervisor design review.  Moving those routes onto a
state mirror/RPC contract is the next step; until then this child never imports
Discord, never opens a database pool, and never runs a cog.
"""

from __future__ import annotations

import os
import signal
import sys
import threading
import time
from pathlib import Path

# The supervisor starts this file directly; make ``src`` importable the same way
# ``python -m bot`` would.
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from utils import logging as bot_logging  # noqa: E402  (installs the console)
from werkzeug.serving import make_server  # noqa: E402

from web_bridge import BotBridge, BotRoute  # noqa: E402
from webapp import app as flask_app  # noqa: E402
from webapp import configure_bot  # noqa: E402


def _report(reporter, event: str, **fields) -> None:
    if reporter is not None:
        reporter.send(event, **fields)


def _heartbeat_loop(reporter) -> None:
    while True:
        time.sleep(3.0)
        if not reporter.heartbeat():
            return


def main() -> int:
    reporter = None
    if (os.environ.get("NIKO_SUPERVISED") or "").strip() == "1":
        from supervisor_protocol import ChildReporter, install_parent_death_signal

        reporter = ChildReporter.from_environment()
        install_parent_death_signal()
        _report(reporter, "process_started")

    # No bot object: this process serves the dashboard shell, auth and static
    # assets, and forwards anything that needs a live gateway.  Routes that
    # require it already answer a structured 503 when it is absent.
    configure_bot(None)
    bridge = BotBridge(flask_app, BotRoute())

    server = make_server("127.0.0.1", 0, bridge, threaded=True)
    port = int(server.server_port)
    thread = threading.Thread(target=server.serve_forever, name="web-child", daemon=True)
    thread.start()

    _report(reporter, "api_listening", host="127.0.0.1", port=port)
    bot_logging.info("Startup", f"Dashboard child listening on 127.0.0.1:{port}")
    _report(reporter, "ready", checks={"api": True, "gateway": False})

    if reporter is not None:
        threading.Thread(
            target=_heartbeat_loop, args=(reporter,), name="heartbeat", daemon=True
        ).start()

    stopping = threading.Event()

    def _stop(_signum=None, _frame=None) -> None:
        stopping.set()

    for signum in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(signum, _stop)
        except (ValueError, OSError):
            pass

    while not stopping.wait(0.5):
        pass

    _report(reporter, "draining", reason="signal")
    bot_logging.info("Shutdown", "Dashboard child stopping.")
    server.shutdown()
    server.server_close()
    _report(reporter, "stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
