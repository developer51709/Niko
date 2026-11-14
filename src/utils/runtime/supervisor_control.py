"""Small client for the supervisor's authenticated local control socket.

This module is used by the update path from a Flask worker thread.  It must not
import Discord or Flask: a request is one JSON line to a Unix socket and one JSON
line back.
"""

from __future__ import annotations

import json
import os
import socket

from supervisor_protocol import CONTROL_SOCKET_ENV, SUPERVISED_ENV


def is_supervised() -> bool:
    return (os.environ.get(SUPERVISED_ENV) or "").strip() == "1"


def socket_path() -> str | None:
    value = (os.environ.get(CONTROL_SOCKET_ENV) or "").strip()
    return value or None


def request(command: str, *, timeout: float = 5.0, **fields):
    """Send one control command and return its decoded response.

    Raises ``RuntimeError`` when this process is not supervised or no control
    socket is configured; callers use that to keep the direct-run fallback
    explicit instead of silently pretending a restart was requested.
    """
    path = socket_path()
    if not path:
        raise RuntimeError(f"{CONTROL_SOCKET_ENV} is not set; this process is not supervised")

    payload = {"command": command, **fields}
    body = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.settimeout(timeout)
        client.connect(path)
        client.sendall(body)
        # The supervisor answers one line and closes the connection.  ``read``
        # is used instead of ``makefile`` so a short response still returns.
        chunks = bytearray()
        while b"\n" not in chunks and len(chunks) < 64 * 1024:
            chunk = client.recv(8192)
            if not chunk:
                break
            chunks.extend(chunk)
    finally:
        client.close()

    if not chunks:
        raise RuntimeError("the supervisor closed the control socket without an answer")
    try:
        response = json.loads(chunks.split(b"\n", 1)[0].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("the supervisor returned an invalid control response") from exc
    if not isinstance(response, dict):
        raise RuntimeError("the supervisor returned a non-object control response")
    return response


def request_restart(
    reason: str = "control restart",
    delay: float = 2.0,
    child: str | list[str] | None = None,
) -> dict:
    """Ask the supervisor to stop one child (or every child) after ``delay``.

    The delay leaves time for the HTTP update response to flush.  The supervisor
    answers immediately; stopping happens in its own task.  ``child`` names the
    target(s) when the deployment runs the dashboard, the bot and the database
    separately: a webapp update restarts only ``web``, a bot update ``bot`` and
    the database child that serves its new database code.
    """
    fields: dict = {"reason": reason, "delay": max(0.0, float(delay))}
    if child:
        fields["child"] = child
    response = request("restart", **fields)
    if not response.get("ok"):
        raise RuntimeError(str(response.get("error") or "the supervisor refused the restart"))
    return response
