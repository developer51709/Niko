"""Small, dependency-free protocol shared by the supervisor and its child.

The supervisor must stay importable without Discord, Flask, or any cog code.  A
child gets one inherited socket descriptor and reports newline-delimited JSON
events on it.  The supervisor never infers readiness from log text: the child
sends explicit lifecycle events instead.

Part 1 uses this module from the fake-child harness.  Part 2 will use the same
reporter from the real bot child.
"""

from __future__ import annotations

import ctypes
import json
import os
import signal
import socket
import sys
import threading
import time

PROTOCOL_VERSION = 1

#: Environment variable containing the inherited child-to-supervisor socket.
CONTROL_FD_ENV = "NIKO_SUPERVISOR_CONTROL_FD"

#: Environment marker set on supervised children.
SUPERVISED_ENV = "NIKO_SUPERVISED"

#: Public port is exposed for diagnostics; it is not a port the child may bind.
PUBLIC_PORT_ENV = "NIKO_SUPERVISOR_PUBLIC_PORT"

#: Authenticated local control socket the child uses to ask the supervisor for
#: a restart.  It is deliberately separate from the inherited lifecycle fd: the
#: updater runs on a Flask worker thread and only needs a short request/response.
CONTROL_SOCKET_ENV = "NIKO_SUPERVISOR_CONTROL_SOCKET"


def is_supervised() -> bool:
    return (os.environ.get(SUPERVISED_ENV) or "").strip() == "1"


def control_socket_path() -> str | None:
    value = (os.environ.get(CONTROL_SOCKET_ENV) or "").strip()
    return value or None

#: Signals used by the test/harness child for Linux parent-death handling.
_PARENT_DEATH_SIGNAL = signal.SIGUSR1


class ChildReporter:
    """Write lifecycle events to the supervisor over one inherited socket.

    Construction happens in the child, after ``exec``.  The reporter owns the
    inherited descriptor for the rest of the child's life.  A broken control
    channel must not crash the child's HTTP path, so send failures are swallowed
    after the first one; the supervisor treats a closed channel as a child
    failure and will replace it.
    """

    def __init__(self, fd: int) -> None:
        self._fd = int(fd)
        self._socket = socket.socket(fileno=self._fd)
        self._file = self._socket.makefile("w", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()
        self._closed = False

    @classmethod
    def from_environment(cls) -> "ChildReporter":
        raw = (os.environ.get(CONTROL_FD_ENV) or "").strip()
        if not raw:
            raise RuntimeError(f"{CONTROL_FD_ENV} is not set; this process is not supervised")
        try:
            fd = int(raw)
        except ValueError as exc:
            raise RuntimeError(f"{CONTROL_FD_ENV} is not an integer") from exc
        return cls(fd)

    def send(self, event: str, **fields) -> bool:
        """Send one event. Returns False once the supervisor has gone away."""

        payload = {
            "protocol": PROTOCOL_VERSION,
            "event": event,
            "pid": os.getpid(),
            "at": time.time(),
            **fields,
        }
        line = json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n"
        with self._lock:
            if self._closed:
                return False
            try:
                self._file.write(line)
                self._file.flush()
                return True
            except (BrokenPipeError, ConnectionError, OSError):
                self._closed = True
                return False

    def heartbeat(self) -> bool:
        return self.send("heartbeat")

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            try:
                self._file.close()
            except OSError:
                pass
            try:
                self._socket.close()
            except OSError:
                pass


def install_parent_death_signal() -> bool:
    """Kill the child process group if the Linux parent dies unexpectedly.

    This is intentionally a harness/child helper, not supervisor logic.  The
    child is started in its own session, so it is the leader of the process
    group.  If the supervisor receives ``SIGKILL`` it cannot clean up its
    children; asking Linux to deliver a signal to the child lets the child kill
    its own group, including any leaked descendants.

    Returns False on platforms without ``prctl`` rather than making the child
    unusable there.
    """

    if not sys.platform.startswith("linux"):
        return False

    def _parent_died(_signum, _frame) -> None:
        try:
            os.killpg(os.getpgrp(), signal.SIGKILL)
        except OSError:
            os._exit(1)

    try:
        signal.signal(_PARENT_DEATH_SIGNAL, _parent_died)
        libc = ctypes.CDLL(None, use_errno=True)
        # PR_SET_PDEATHSIG == 1
        if libc.prctl(1, _PARENT_DEATH_SIGNAL, 0, 0, 0) != 0:
            return False
    except (AttributeError, OSError):
        return False
    return True
