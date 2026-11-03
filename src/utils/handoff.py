"""Move a running deployment to a successor process without dropping the gateway.

Python cannot replace its own code: a changed ``bot.py`` or startup chain needs
a new interpreter. The old way is to stop the process and start it again, which
takes the gateway offline for the whole boot and makes the dashboard unreachable.

This module does it in the other order.

1. The current process (``main``) has already written the new files. It
   duplicates its listening socket and starts ``src/bot.py`` with that socket
   inherited, plus a one-run token.
2. The successor (``candidate``) imports the new code, starts its dashboard on
   the inherited socket — so the site never stops answering, and either process
   can serve a request for the moment — loads its cogs and connects the gateway.
3. Once its gateway is ready the candidate calls ``/api/handoff/ready`` on the
   main process. The main process stops accepting, closes its gateway and exits,
   leaving the candidate with the socket, the gateway session and every cog.
4. The candidate starts answering commands only after that acknowledgement, so a
   command is never handled twice during the short overlap.

If the candidate never becomes ready, the main process is untouched: it keeps
serving and running, and the owner sees the failure on the update page. Files
that were written stay on disk, so a retry (or a normal deploy) picks them up.
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ROLE = (os.environ.get("NIKO_HANDOFF_ROLE") or "").strip()
INHERITED_FD = os.environ.get("NIKO_HANDOFF_FD")
MAIN_PORT = int(os.environ.get("NIKO_HANDOFF_MAIN_PORT") or os.environ.get("PORT") or 5000)

_token = (os.environ.get("NIKO_HANDOFF_TOKEN") or "").strip()
_active = ROLE != "candidate"
_stage = {"candidate": None, "ready_at": None}


def is_candidate() -> bool:
    return ROLE == "candidate"


def inherited_fd() -> int | None:
    """The listening socket the predecessor handed over, if this is a successor."""
    return int(INHERITED_FD) if INHERITED_FD else None


def token() -> str:
    return _token


def commands_allowed() -> bool:
    """False in a successor until the predecessor has let go."""
    return _active


def activate() -> None:
    global _active
    if _active:
        return
    _active = True
    _stage["ready_at"] = time.time()
    logging.info("Handoff", "Successor is answering commands; the predecessor has stepped down.")


def schedule(bot, delay: float = 2.0) -> None:
    """Start the successor after the response that asked for it has been sent."""
    threading.Thread(target=_delayed_start, args=(bot, delay), name="niko-handoff", daemon=True).start()


def _delayed_start(bot, delay: float) -> None:
    time.sleep(max(0.0, delay))
    try:
        start(bot)
    except Exception as exc:
        logging.error("Handoff", f"Could not start the successor process: {exc}")
        _remember({"state": "failed", "error": f"{type(exc).__name__}: {exc}", "at": int(time.time())})


def start(bot) -> dict:
    """Spawn the successor with this process's listening socket."""
    import api_server

    fd = api_server.listening_socket_fd()
    port = api_server.listening_port()
    global _token
    _token = secrets.token_hex(16)

    environment = dict(os.environ)
    environment.update({
        "NIKO_HANDOFF_ROLE": "candidate",
        "NIKO_HANDOFF_TOKEN": _token,
        "NIKO_HANDOFF_FD": str(fd),
        "NIKO_HANDOFF_MAIN_PORT": str(port),
        "NIKO_HANDOFF_MAIN_PID": str(os.getpid()),
    })

    logging.info("Handoff", f"Starting a successor process on the inherited socket (port {port}).")
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "src" / "bot.py")],
        cwd=str(ROOT),
        env=environment,
        pass_fds=(fd,),
        close_fds=True,
    )
    # The parent no longer needs its duplicate; the child owns its own now.
    os.close(fd)

    record = {
        "state": "started",
        "pid": process.pid,
        "port": port,
        "at": int(time.time()),
    }
    _remember(record)
    _stage["candidate"] = record
    return record


def announce(timeout: float = 25.0) -> bool:
    """Tell the predecessor we are ready and wait for its acknowledgement."""
    import requests

    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{MAIN_PORT}/api/handoff/ready"
    while time.time() < deadline:
        try:
            response = requests.post(
                url,
                headers={"X-Handoff-Token": _token},
                json={"pid": os.getpid()},
                timeout=2.0,
            )
            if response.ok and response.json().get("handoff") is True:
                # The predecessor closes its gateway and exits immediately after
                # answering; a beat later this process owns the session.
                time.sleep(0.8)
                _remember({"state": "promoted", "at": int(time.time())})
                return True
        except Exception:
            # Either the predecessor is gone or the request landed on this very
            # process (both share the socket), which answers ``handoff: false``.
            pass
        time.sleep(0.4)
    return False


def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def become_successor(bot, timeout: float = 25.0) -> None:
    """Successor side, once the new code is fully loaded and online.

    The listening socket is adopted here rather than at process start: until the
    cogs, database and gateway are ready there is nothing useful to serve, and
    sharing the socket early would send half of production's traffic to a
    half-started process.
    """
    import api_server

    fd = inherited_fd()
    if fd is None:
        logging.error("Handoff", "This process was started as a successor without a socket; starting a normal server.")
        api_server.start_api_server(bot)
    else:
        try:
            api_server.start_api_server(bot, fd=fd)
            logging.info("Handoff", "Successor is serving HTTP on the inherited socket.")
        except Exception as exc:
            # Never announce a successor that cannot serve: the predecessor would
            # retire and leave the site without an API.
            logging.error("Handoff", f"Could not adopt the inherited socket ({exc}); leaving the predecessor in charge.")
            os._exit(1)

    if announce(timeout=timeout):
        activate()
        return

    main_pid = int(os.environ.get("NIKO_HANDOFF_MAIN_PID") or 0)
    if _alive(main_pid):
        logging.error("Handoff", "The predecessor never acknowledged and is still running; exiting this successor.")
        os._exit(1)
    logging.warning("Handoff", "The predecessor is gone; this successor is taking over unacknowledged.")
    activate()
    _remember({"state": "promoted-unacknowledged", "at": int(time.time())})


def complete(bot) -> None:
    """The predecessor's side: let go of Discord, then of the socket, then exit.

    The gateway goes first so the successor can start answering commands, but
    the HTTP server stays up a little longer: the successor retries its ready
    call, and a reply that never reached it would otherwise cost the site its
    API when this process retires.
    """
    time.sleep(0.2)
    try:
        from webapp.runtime import run_on_bot_loop

        run_on_bot_loop(bot.close(), timeout=15)
        logging.info("Handoff", "Closed this process's gateway connection.")
    except Exception as exc:
        logging.warning("Handoff", f"Could not close the gateway cleanly: {exc}")

    time.sleep(1.2)
    try:
        import api_server

        api_server.stop_serving()
        logging.info("Handoff", "Stopped accepting HTTP; the successor owns the socket.")
    except Exception as exc:
        logging.warning("Handoff", f"Could not stop the API server: {exc}")
    time.sleep(0.2)
    logging.info("Handoff", "Retiring this process; the successor is live.")
    os._exit(0)


def _remember(record: dict) -> None:
    """A small file so the successor (and the owner) can see what happened."""
    try:
        path = ROOT / "data" / "updates" / "handoff.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, indent=2), encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        pass


def last() -> dict | None:
    try:
        return json.loads((ROOT / "data" / "updates" / "handoff.json").read_text(encoding="utf-8"))
    except Exception:
        return None
