"""Restart the bot process in place, without giving up its listening socket.

Python cannot replace its own code, so a changed ``src/bot.py`` or startup chain
needs a new interpreter. Exiting and letting something start the process again is
what this module exists to avoid: a supervised service — Render, Railway, a
systemd unit — reads that exit as a crash or a stopped service and recreates the
instance, which throws away the files the update just wrote and leaves the
dashboard unreachable for the whole boot. On a deployment with an ephemeral
filesystem that is worse than not updating at all: the pull is lost and the same
deploy has to run again.

So the process replaces its own image instead of dying:

1. The live listening socket is duplicated and marked inheritable, and its
   descriptor is passed to the new image as ``NIKO_RESTART_FD``. The kernel keeps
   the socket bound and listening across ``execve``, so **the port never closes**
   and connections queue instead of being refused.
2. ``execve`` keeps the PID. A supervisor watching this process sees no exit, so
   nothing recreates the container and the files that were just written stay.
3. The new image adopts the socket as soon as its imports finish
   (:func:`adopt`), long before cogs load and the gateway connects, so the site is
   answering again in about a second.

The exec closes every other descriptor, which ends the gateway connection: the new
image logs in and reconnects while the site keeps answering. Closing the gateway
explicitly first is deliberately avoided — ``bot.close()`` makes the running
``asyncio.run`` return, and interpreter shutdown does not wait for this daemon
thread, so the process could exit before the exec that was supposed to replace it.
Commands go unanswered for the few seconds the boot takes; HTTP is not
interrupted.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

from utils import logging

ROOT = Path(__file__).resolve().parents[3]

#: Passed to the restarted image: the descriptor it must serve HTTP on.
INHERITED_FD_ENV = "NIKO_RESTART_FD"


def inherited_fd() -> int | None:
    """The listening socket the previous image left open, if this is a restart."""
    value = (os.environ.get(INHERITED_FD_ENV) or "").strip()
    try:
        return int(value) if value else None
    except ValueError:
        return None


def adopt(bot=None) -> bool:
    """Serve HTTP on the inherited socket, or say that there was none.

    Called by ``src/bot.py`` at startup, before the cogs load. Returning ``False``
    is not an error: the caller binds the port normally, so an update whose
    descriptor did not survive still comes back up with a listening site.
    """
    import api_server

    fd = inherited_fd()
    if fd is None:
        return False
    try:
        api_server.start_api_server(bot, fd=fd)
    except Exception as exc:
        logging.error("Handoff", f"Could not serve on the inherited socket ({exc}); binding the port again.")
        _remember({"state": "failed", "pid": os.getpid(), "error": f"{type(exc).__name__}: {exc}", "at": int(time.time())})
        return False
    _remember({
        "state": "restarted",
        "pid": os.getpid(),
        "port": api_server.listening_port(),
        "at": int(time.time()),
    })
    logging.info("Handoff", "Restarted in place; the dashboard socket never closed.")
    return True


def schedule(delay: float = 2.0) -> None:
    """Restart after the response that asked for it has been sent."""
    threading.Thread(target=_delayed_restart, args=(delay,), name="niko-handoff", daemon=True).start()


def _delayed_restart(delay: float) -> None:
    time.sleep(max(0.0, delay))
    try:
        restart()
    except Exception as exc:
        logging.error("Handoff", f"Could not restart this process: {exc}")


def restart() -> None:
    """Replace this process with a fresh image of ``src/bot.py``.

    Everything that can fail happens before the image is replaced, so a restart
    that cannot be prepared leaves the site and the bot exactly as they are. After
    a successful ``execve`` this function does not return; the running gateway
    connection ends with the old image and the new one logs in again.
    """
    import api_server

    fd = api_server.listening_socket_fd()
    # The kernel closes descriptors on exec unless they are inheritable; this is
    # the single line that keeps the port open across the restart.
    os.set_inheritable(fd, True)
    port = api_server.listening_port()

    environment = dict(os.environ)
    environment.pop(INHERITED_FD_ENV, None)
    environment.update({INHERITED_FD_ENV: str(fd)})

    record = {"state": "restarting", "pid": os.getpid(), "port": port, "at": int(time.time())}
    _remember(record)
    logging.info("Handoff", f"Restarting this process in place on the inherited socket (port {port}).")

    try:
        os.execve(sys.executable, [sys.executable, str(ROOT / "src" / "bot.py")], environment)
    except Exception as exc:
        # The port is still served by this process, so the site stays up; only
        # the new code waits for the next deploy.
        _remember({
            "state": "failed",
            "pid": os.getpid(),
            "port": port,
            "error": f"{type(exc).__name__}: {exc}",
            "at": int(time.time()),
        })
        raise


def _remember(record: dict) -> None:
    """A small file so the owner (and the next image) can see what happened."""
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
