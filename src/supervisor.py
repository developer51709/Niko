"""Own the public port and supervise one bot child process.

This is the Part 1 supervisor shell.  It deliberately knows nothing about
Discord, Flask, cogs, or the updater.  A child talks to it through an inherited
newline-delimited JSON socket, and the supervisor owns:

* the public HTTP port and ``/health``/``/ready``;
* the loopback HTTP reverse proxy to the active child;
* spawning, heartbeats, restart backoff, signals, and process-group cleanup;
* an authenticated local control socket and an atomically written status file.

Run it with no arguments to use ``PORT`` and ``src/bot.py``.  The fake-child
harness passes an explicit ``--child`` path and test timeouts.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import fcntl
import json
import logging
import os
import signal
import socket
import stat
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import aiohttp
from aiohttp import web
from multidict import CIMultiDict

from supervisor_protocol import (
    CONTROL_FD_ENV,
    CONTROL_SOCKET_ENV,
    PROTOCOL_VERSION,
    PUBLIC_PORT_ENV,
    SUPERVISED_ENV,
)

ROOT = Path(__file__).resolve().parents[1]
LOG = logging.getLogger("supervisor")

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}
# These are overwritten at the trust boundary, never copied from the client.
FORWARDED_HEADERS = {
    "x-forwarded-for",
    "x-forwarded-host",
    "x-forwarded-port",
    "x-forwarded-proto",
}


@dataclass
class Options:
    public_host: str = "0.0.0.0"
    public_port: int = 5000
    child_script: Path = ROOT / "src" / "bot.py"
    child_args: list[str] = field(default_factory=list)
    status_file: Path = ROOT / "data" / "run" / "supervisor.json"
    control_socket: Path = ROOT / "data" / "run" / "supervisor.sock"
    lock_file: Path = ROOT / "data" / "run" / "supervisor.lock"
    startup_timeout: float = 60.0
    heartbeat_timeout: float = 12.0
    shutdown_timeout: float = 8.0
    restart_backoff_initial: float = 1.0
    restart_backoff_max: float = 30.0
    restart_reset_after: float = 60.0
    max_restarts: int = 0
    proxy_timeout: float = 300.0
    status_public: bool = False
    log_level: str = "INFO"


@dataclass
class Child:
    proc: asyncio.subprocess.Process
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    started_at: float
    api_port: int | None = None
    state: str = "process_started"
    ready: bool = False
    ready_at: float | None = None
    last_heartbeat: float = 0.0
    last_event_at: float = 0.0
    last_error: str | None = None
    readiness: dict[str, Any] | None = None
    returncode: int | None = None
    restart_requested: bool = False
    stop_reason: str | None = None
    stop_task: asyncio.Task | None = None
    monitor_task: asyncio.Task | None = None
    watchdog_task: asyncio.Task | None = None
    stdout_task: asyncio.Task | None = None
    stderr_task: asyncio.Task | None = None
    wait_task: asyncio.Task | None = None
    exit_event: asyncio.Event = field(default_factory=asyncio.Event)

    @property
    def pid(self) -> int:
        return int(self.proc.pid)


class Supervisor:
    def __init__(self, options: Options) -> None:
        self.options = options
        self.state = "starting"
        self.ready = False
        self.public_port: int | None = None
        self.started_at = time.time()
        self.started_monotonic = time.monotonic()
        self.last_error: str | None = None
        self.restart_count = 0
        self.child_starts = 0
        self.consecutive_failures = 0
        self.last_stop_reason: str | None = None

        self._child: Child | None = None
        self._history: list[dict[str, Any]] = []
        self._lock_fd: int | None = None
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._control_server: asyncio.AbstractServer | None = None
        self._session: aiohttp.ClientSession | None = None
        self._supervise_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        self._restart_signal = asyncio.Event()
        self._restart_pending = False
        self._stopping = False
        self._shutdown_future: asyncio.Task | None = None
        self._startup_done = False

    # ── Public server and status ──────────────────────────────────────────

    async def run(self) -> None:
        try:
            self._prepare_paths()
            self._acquire_lock()
            self._remove_stale_socket()
            self._install_signal_handlers()
            await self._start_public_server()
            await self._start_control_server()
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    total=None,
                    connect=5.0,
                    sock_read=self.options.proxy_timeout,
                )
            )
            self.state = "starting"
            self._record("supervisor_started", public_port=self.public_port)
            self._write_status()
            self._startup_done = True
            self._supervise_task = asyncio.create_task(self._supervise(), name="supervise")
            await self._shutdown_event.wait()
            await self.shutdown()
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            LOG.exception("supervisor failed to start")
            await self._cleanup_resources()
            raise
        finally:
            if not self._stopping:
                self._shutdown_event.set()
                await self._cleanup_resources()

    async def shutdown(self) -> None:
        """Request one clean shutdown; repeated calls await the same work."""
        if self._shutdown_future is None:
            self._shutdown_event.set()
            self._shutdown_future = asyncio.create_task(
                self._shutdown_impl(), name="shutdown"
            )
        await asyncio.shield(self._shutdown_future)

    async def _shutdown_impl(self) -> None:
        if self._stopping:
            return
        self._stopping = True
        self.ready = False
        self.state = "stopped"
        self._shutdown_event.set()
        self._restart_signal.set()
        # Wake the supervision loop's child wait before waiting for that loop.
        # Awaiting the loop first would deadlock while it waits for an exit that
        # only this shutdown path can trigger.
        child = self._child
        if child is not None:
            await self._terminate_child(child, "supervisor shutdown")
        if self._supervise_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._supervise_task
        child = self._child
        if child is not None:
            await self._cleanup_child(child)
        # A draining/stopped event from the child must not overwrite the final
        # supervisor state during an intentional shutdown.
        self.state = "stopped"
        self.ready = False
        await self._cleanup_resources()
        self._write_status()
        LOG.info("supervisor stopped")

    def _prepare_paths(self) -> None:
        for path in (
            self.options.status_file.parent,
            self.options.control_socket.parent,
            self.options.lock_file.parent,
        ):
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._secure_run_dir(self.options.control_socket.parent)

    @staticmethod
    def _secure_run_dir(path: Path) -> None:
        try:
            mode = stat.S_IMODE(path.stat().st_mode)
            if mode & 0o077:
                path.chmod(0o700)
        except OSError:
            pass

    def _acquire_lock(self) -> None:
        path = self.options.lock_file
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(fd)
            raise RuntimeError(f"another supervisor owns {path}") from exc
        os.write(fd, f"{os.getpid()}\n".encode("ascii"))
        os.fsync(fd)
        self._lock_fd = fd

    def _remove_stale_socket(self) -> None:
        path = self.options.control_socket
        if not path.exists() and not path.is_socket():
            return
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            probe.settimeout(0.2)
            probe.connect(str(path))
        except OSError:
            with contextlib.suppress(FileNotFoundError):
                path.unlink()
        else:
            raise RuntimeError(f"another supervisor is listening on {path}")
        finally:
            probe.close()

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()
        for signum in (signal.SIGTERM, signal.SIGINT):
            with contextlib.suppress(NotImplementedError, RuntimeError):
                loop.add_signal_handler(
                    signum,
                    lambda: asyncio.create_task(self.shutdown()),
                )

    async def _start_public_server(self) -> None:
        app = web.Application(client_max_size=1024**3)
        app.router.add_get("/health", self._health)
        app.router.add_get("/ready", self._ready)
        app.router.add_get("/supervisor/status", self._public_status)
        app.router.add_route("*", "/{tail:.*}", self._proxy)

        self._runner = web.AppRunner(app, access_log=None)
        await self._runner.setup()
        self._site = web.TCPSite(
            self._runner,
            host=self.options.public_host,
            port=self.options.public_port,
        )
        await self._site.start()
        server = self._site._server
        if server is None or not server.sockets:
            raise RuntimeError("public server did not expose a listening socket")
        self.public_port = int(server.sockets[0].getsockname()[1])
        LOG.info("public server listening on %s:%s", self.options.public_host, self.public_port)

    async def _start_control_server(self) -> None:
        path = self.options.control_socket
        self._control_server = await asyncio.start_unix_server(
            self._handle_control,
            path=str(path),
            limit=64 * 1024,
        )
        os.chmod(path, 0o600)
        LOG.info("control socket listening on %s", path)

    async def _health(self, _request: web.Request) -> web.Response:
        return web.json_response(
            {
                "status": "ok",
                "state": self.state,
                "pid": os.getpid(),
                "uptime_seconds": round(time.monotonic() - self.started_monotonic, 3),
            }
        )

    async def _ready(self, _request: web.Request) -> web.Response:
        ready, reason = self._readiness()
        body = {
            "ready": ready,
            "state": self.state,
            "reason": reason,
            "child": self._child_summary(),
        }
        return web.json_response(body, status=200 if ready else 503)

    async def _public_status(self, request: web.Request) -> web.Response:
        # The detailed status is available over the authenticated local control
        # socket.  The public endpoint is opt-in and off by default; enabling it
        # is an explicit deployment decision.
        if not self.options.status_public:
            raise web.HTTPNotFound()
        return web.json_response(self._status_snapshot())

    # ── Child supervision ─────────────────────────────────────────────────

    async def _supervise(self) -> None:
        try:
            while not self._shutdown_event.is_set():
                if self._child is None:
                    if self.state == "failed" and not self._restart_signal.is_set():
                        await self._wait_for_wake()
                        if self._shutdown_event.is_set():
                            break
                    if self._restart_signal.is_set():
                        self._restart_signal.clear()
                    if self._restart_pending:
                        self._restart_pending = False
                        self.consecutive_failures = 0
                    try:
                        await self._start_child()
                    except Exception as exc:
                        self.restart_count += 1
                        self.consecutive_failures += 1
                        self.last_error = f"spawn failed: {type(exc).__name__}: {exc}"
                        LOG.error("%s", self.last_error)
                        self._record("spawn_failed", error=self.last_error)
                        if not self._allow_restart():
                            self.state = "failed"
                            self._write_status()
                            await self._wait_for_wake()
                        else:
                            self.state = "restarting"
                            self._write_status()
                            await self._backoff()
                        continue
                    continue

                child = self._child
                await child.exit_event.wait()
                await self._cleanup_child(child)
                if self._shutdown_event.is_set():
                    break

                if child.restart_requested:
                    self.last_stop_reason = child.stop_reason or "control restart"
                    self.consecutive_failures = 0
                    self.state = "restarting"
                    self.ready = False
                    self._record("child_restarting", reason=self.last_stop_reason)
                    self._write_status()
                    continue

                self.restart_count += 1
                self.consecutive_failures += 1
                self.last_error = (
                    f"child exited with code {child.returncode}"
                    + (f" ({child.stop_reason})" if child.stop_reason else "")
                )
                self.last_stop_reason = child.stop_reason or "child exit"
                self.state = "restarting"
                self.ready = False
                self._record(
                    "child_exited",
                    returncode=child.returncode,
                    restart_count=self.restart_count,
                    reason=child.stop_reason,
                )
                self._write_status()
                if not self._allow_restart():
                    self.state = "failed"
                    self.last_error = (
                        f"restart limit reached after {self.consecutive_failures} failures"
                    )
                    self._write_status()
                    await self._wait_for_wake()
                    continue
                await self._backoff()
        except asyncio.CancelledError:
            raise
        except Exception:
            LOG.exception("supervision loop crashed")
            self.state = "failed"
            self.last_error = "supervision loop crashed; see supervisor logs"
            self._write_status()

    async def _start_child(self) -> None:
        if self._shutdown_event.is_set():
            return
        self.state = "starting"
        self.ready = False
        self._record("child_starting")
        self._write_status()

        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        parent_sock.setblocking(False)
        child_sock.set_inheritable(True)
        env = self._child_environment(child_sock.fileno())
        command = [
            sys.executable,
            "-u",
            str(self.options.child_script),
            *self.options.child_args,
        ]
        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(ROOT),
                env=env,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
                pass_fds=(child_sock.fileno(),),
            )
            reader, writer = await asyncio.open_connection(sock=parent_sock, limit=64 * 1024)
        except Exception:
            parent_sock.close()
            child_sock.close()
            if proc is not None and proc.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
                with contextlib.suppress(Exception):
                    await proc.wait()
            raise
        finally:
            with contextlib.suppress(OSError):
                child_sock.close()

        started = time.monotonic()
        child = Child(
            proc=proc,
            reader=reader,
            writer=writer,
            started_at=started,
            last_heartbeat=started,
            last_event_at=started,
        )
        self.child_starts += 1
        child.monitor_task = asyncio.create_task(
            self._monitor_child(child), name=f"child-monitor-{proc.pid}"
        )
        child.watchdog_task = asyncio.create_task(
            self._watchdog(child), name=f"child-watchdog-{proc.pid}"
        )
        child.stdout_task = asyncio.create_task(
            self._drain_stream(child, proc.stdout, "stdout"), name=f"child-stdout-{proc.pid}"
        )
        child.stderr_task = asyncio.create_task(
            self._drain_stream(child, proc.stderr, "stderr"), name=f"child-stderr-{proc.pid}"
        )
        child.wait_task = asyncio.create_task(
            self._wait_child(child), name=f"child-wait-{proc.pid}"
        )
        self._child = child
        self._record("child_started", pid=child.pid)
        LOG.info("child started pid=%s", child.pid)
        self._write_status()

    def _child_environment(self, control_fd: int) -> dict[str, str]:
        env = dict(os.environ)
        for key in (
            "NIKO_RESTART_FD",
            "NIKO_HANDOFF_ROLE",
            "NIKO_CHILD_PORT",
            "NIKO_IMPORT_PROBE",
            CONTROL_FD_ENV,
            CONTROL_SOCKET_ENV,
            PUBLIC_PORT_ENV,
            SUPERVISED_ENV,
        ):
            env.pop(key, None)
        # A supervised child must never bind the public port by accident.  The
        # real child binds an ephemeral loopback port and reports it in its
        # api_listening event.
        env.pop("PORT", None)
        env.update(
            {
                SUPERVISED_ENV: "1",
                CONTROL_FD_ENV: str(control_fd),
                CONTROL_SOCKET_ENV: str(self.options.control_socket.resolve()),
                PUBLIC_PORT_ENV: str(self.public_port or self.options.public_port),
                "PYTHONUNBUFFERED": "1",
            }
        )
        return env

    async def _wait_child(self, child: Child) -> None:
        try:
            child.returncode = await child.proc.wait()
        finally:
            child.exit_event.set()

    async def _monitor_child(self, child: Child) -> None:
        try:
            while True:
                raw = await child.reader.readline()
                if not raw:
                    break
                if len(raw) > 64 * 1024:
                    self.last_error = "child control event exceeded 64 KiB"
                    await self._terminate_child(child, "oversized control event")
                    return
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self.last_error = "child sent malformed lifecycle JSON"
                    LOG.warning("%s", self.last_error)
                    continue
                if not isinstance(payload, dict):
                    continue
                await self._handle_child_event(child, payload)
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError, ValueError) as exc:
            self.last_error = f"child control channel lost: {type(exc).__name__}: {exc}"
            LOG.warning("%s", self.last_error)
        finally:
            if not child.exit_event.is_set() and not self._stopping:
                # A silent control channel is a child failure, not a healthy
                # child we should wait on forever.
                await self._terminate_child(child, "control channel closed")

    async def _handle_child_event(self, child: Child, payload: dict[str, Any]) -> None:
        event = str(payload.get("event") or "")
        child.last_event_at = time.monotonic()
        if event == "heartbeat":
            child.last_heartbeat = child.last_event_at
            return
        if event == "state":
            event = str(payload.get("state") or "")
        if not event:
            return

        if event == "process_started":
            child.state = event
            child.last_heartbeat = child.last_event_at
        elif event == "api_listening":
            try:
                port = int(payload.get("port"))
            except (TypeError, ValueError):
                self.last_error = "child reported an invalid api port"
                await self._terminate_child(child, "invalid api port")
                return
            if not 1 <= port <= 65535:
                self.last_error = f"child reported invalid api port {port}"
                await self._terminate_child(child, "invalid api port")
                return
            child.api_port = port
            child.state = event
            LOG.info("child pid=%s api listening on 127.0.0.1:%s", child.pid, port)
        elif event in {"db_ready", "cogs_loaded", "gateway_ready"}:
            child.state = event
        elif event == "draining":
            child.state = "draining"
            child.ready = False
            self.ready = False
            self.state = "draining"
        elif event in {"ready", "degraded"}:
            child.ready = True
            child.ready_at = time.monotonic()
            child.state = event
            child.readiness = payload.get("checks") if isinstance(payload.get("checks"), dict) else None
            self.state = "active" if event == "ready" else "degraded"
            self.ready = True
            self._record("child_ready", state=event, reasons=payload.get("reasons") or [])
        elif event in {"readiness_failed", "error"}:
            reason = str(payload.get("reason") or payload.get("message") or event)
            child.last_error = reason
            child.readiness = payload.get("checks") if isinstance(payload.get("checks"), dict) else None
            child.ready = False
            self.ready = False
            self.last_error = reason
            self._record("child_not_ready", reason=reason)
            await self._terminate_child(child, "readiness failed")
            return
        elif event == "stopped":
            child.state = "stopped"
            child.ready = False
            self.ready = False
        else:
            LOG.debug("unknown child event: %s", event)
            return

        self._record(f"child_{event}", state=child.state)
        self._write_status()

    async def _watchdog(self, child: Child) -> None:
        interval = max(0.05, min(0.25, self.options.heartbeat_timeout / 4.0))
        while not child.exit_event.is_set():
            await asyncio.sleep(interval)
            if child.exit_event.is_set():
                return
            now = time.monotonic()
            if child.ready:
                if now - child.last_heartbeat > self.options.heartbeat_timeout:
                    self.last_error = (
                        f"child heartbeat missed by {now - child.last_heartbeat:.2f}s"
                    )
                    LOG.warning("%s", self.last_error)
                    await self._terminate_child(child, "heartbeat timeout")
                    return
                if (
                    child.ready_at is not None
                    and now - child.ready_at >= self.options.restart_reset_after
                    and self.consecutive_failures
                ):
                    self.consecutive_failures = 0
                    self._record("failure_counter_reset")
            elif child.ready_at is None and now - child.started_at > self.options.startup_timeout:
                # A child that has already been ready is not still starting.
                # Its draining/restarting `ready=False` must not be reported as
                # a startup timeout based on a start time from long ago.
                self.last_error = f"child did not become ready within {self.options.startup_timeout:.2f}s"
                LOG.warning("%s", self.last_error)
                await self._terminate_child(child, "startup timeout")
                return

    async def _terminate_child(self, child: Child, reason: str) -> None:
        if child.stop_task is None:
            child.stop_task = asyncio.create_task(
                self._terminate_child_impl(child, reason),
                name=f"child-stop-{child.pid}",
            )
        await asyncio.shield(child.stop_task)

    async def _terminate_child_impl(self, child: Child, reason: str) -> None:
        if child.stop_reason is None:
            child.stop_reason = reason
        if child.proc.returncode is None:
            LOG.warning("stopping child pid=%s: %s", child.pid, reason)
            self._kill_group(child, signal.SIGTERM)
            try:
                await asyncio.wait_for(child.exit_event.wait(), timeout=self.options.shutdown_timeout)
            except asyncio.TimeoutError:
                LOG.warning("child pid=%s ignored SIGTERM; sending SIGKILL", child.pid)
                self._kill_group(child, signal.SIGKILL)
                with contextlib.suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(child.exit_event.wait(), timeout=5.0)
        # Kill any child descendants that outlived their group leader.  This is
        # safe when the group is empty (ESRCH) and is the reason the child is
        # started in its own session.
        self._kill_group(child, signal.SIGKILL)

    def _kill_group(self, child: Child, signum: int) -> None:
        try:
            os.killpg(child.pid, signum)
        except (ProcessLookupError, PermissionError):
            pass

    async def _cleanup_child(self, child: Child) -> None:
        if self._child is child:
            self._child = None
        self.ready = False
        for task in (child.monitor_task, child.watchdog_task):
            if task is not None:
                task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.gather(
                *(task for task in (child.monitor_task, child.watchdog_task) if task is not None),
                return_exceptions=True,
            )
        with contextlib.suppress(Exception):
            child.writer.close()
            await child.writer.wait_closed()
        for task in (child.stdout_task, child.stderr_task):
            if task is not None:
                with contextlib.suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(task, timeout=2.0)
                if not task.done():
                    task.cancel()
        if child.returncode is None and child.proc.returncode is not None:
            child.returncode = child.proc.returncode
        self._record(
            "child_stopped",
            pid=child.pid,
            returncode=child.returncode,
            reason=child.stop_reason,
        )
        self._write_status()

    async def _drain_stream(
        self,
        child: Child,
        stream: asyncio.StreamReader | None,
        stream_name: str,
    ) -> None:
        if stream is None:
            return
        buffer = bytearray()
        try:
            while True:
                chunk = await stream.read(8192)
                if not chunk:
                    break
                buffer.extend(chunk)
                while True:
                    newline = buffer.find(b"\n")
                    if newline < 0:
                        break
                    line = bytes(buffer[:newline])
                    del buffer[: newline + 1]
                    self._log_child_line(child, stream_name, line)
                if len(buffer) >= 64 * 1024:
                    self._log_child_line(child, stream_name, bytes(buffer), truncated=True)
                    buffer.clear()
            if buffer:
                self._log_child_line(child, stream_name, bytes(buffer))
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError):
            pass

    def _log_child_line(
        self,
        child: Child,
        stream_name: str,
        line: bytes,
        *,
        truncated: bool = False,
    ) -> None:
        text = line.decode("utf-8", errors="replace").rstrip("\r")
        # Keep child output useful but bounded; the supervisor must never hold an
        # unbounded in-memory log buffer.
        if len(text) > 4096:
            text = text[:4096] + "…[truncated]"
        suffix = " [line truncated]" if truncated else ""
        LOG.info("[child:%s:%s] %s%s", child.pid, stream_name, text, suffix)

    async def _backoff(self) -> None:
        exponent = max(0, self.consecutive_failures - 1)
        delay = min(
            self.options.restart_backoff_initial * (2**exponent),
            self.options.restart_backoff_max,
        )
        self._record("restart_backoff", seconds=round(delay, 3))
        await self._wait_for_wake(delay)

    def _allow_restart(self) -> bool:
        limit = self.options.max_restarts
        return limit <= 0 or self.consecutive_failures <= limit

    async def _wait_for_wake(self, timeout: float | None = None) -> None:
        shutdown_task = asyncio.create_task(self._shutdown_event.wait())
        restart_task = asyncio.create_task(self._restart_signal.wait())
        try:
            done, _ = await asyncio.wait(
                {shutdown_task, restart_task},
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if restart_task in done:
                self._restart_signal.clear()
        finally:
            shutdown_task.cancel()
            restart_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(shutdown_task, restart_task, return_exceptions=True)

    # ── Control socket ────────────────────────────────────────────────────

    async def _handle_control(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        response: dict[str, Any]
        try:
            if not self._peer_allowed(writer):
                response = {"ok": False, "error": "control peer is not authorized"}
            else:
                raw = await asyncio.wait_for(reader.readline(), timeout=5.0)
                if len(raw) > 8192:
                    response = {"ok": False, "error": "control request too large"}
                else:
                    try:
                        payload = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        response = {"ok": False, "error": "invalid JSON control request"}
                    else:
                        response = await self._dispatch_control(payload)
        except asyncio.TimeoutError:
            response = {"ok": False, "error": "control request timed out"}
        except ValueError:
            response = {"ok": False, "error": "control request too large"}
        except (ConnectionError, OSError) as exc:
            response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        except Exception as exc:
            LOG.exception("control request failed")
            response = {"ok": False, "error": f"control request failed: {type(exc).__name__}"}
        try:
            writer.write((json.dumps(response, separators=(",", ":")) + "\n").encode("utf-8"))
            await writer.drain()
        except (ConnectionError, OSError):
            pass
        finally:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

    def _peer_allowed(self, writer: asyncio.StreamWriter) -> bool:
        sock = writer.get_extra_info("socket")
        if sock is None or not hasattr(socket, "SO_PEERCRED"):
            # The filesystem mode (0600) still protects platforms without peer
            # credentials.  Linux gets the stronger check.
            return True
        try:
            raw = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            _pid, uid, _gid = struct.unpack("3i", raw)
        except (AttributeError, OSError):
            return True
        return uid == os.geteuid()

    async def _dispatch_control(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {"ok": False, "error": "control request must be an object"}
        command = str(payload.get("command") or "").strip().lower()
        if command == "ping":
            return {"ok": True, "pong": True, "protocol": PROTOCOL_VERSION}
        if command == "status":
            return {"ok": True, "status": self._status_snapshot()}
        if command == "restart":
            if self._stopping:
                return {"ok": False, "error": "supervisor is shutting down"}
            try:
                delay = max(0.0, float(payload.get("delay", 0.0) or 0.0))
            except (TypeError, ValueError):
                return {"ok": False, "error": "delay must be a number"}
            reason = str(payload.get("reason") or "control restart")
            self._request_restart(delay, reason)
            return {
                "ok": True,
                "accepted": True,
                "delay": delay,
                "child_pid": self._child.pid if self._child else None,
            }
        if command == "shutdown":
            asyncio.create_task(self.shutdown())
            return {"ok": True, "accepted": True}
        return {"ok": False, "error": f"unknown control command: {command or '<empty>'}"}

    def _request_restart(self, delay: float, reason: str) -> None:
        async def request_after_delay() -> None:
            if delay:
                await asyncio.sleep(delay)
            if self._shutdown_event.is_set():
                return
            child = self._child
            if child is None:
                self._restart_pending = True
                self._restart_signal.set()
                return
            child.restart_requested = True
            child.stop_reason = reason
            await self._terminate_child(child, reason)

        asyncio.create_task(request_after_delay(), name="control-restart")

    # ── Reverse proxy ─────────────────────────────────────────────────────

    async def _proxy(self, request: web.Request) -> web.StreamResponse:
        child = self._child
        if (
            self._stopping
            or child is None
            or child.api_port is None
            or child.exit_event.is_set()
        ):
            return self._unavailable("bot child is not serving")

        if request.headers.get("Upgrade"):
            return web.json_response(
                {"error": "protocol upgrades are not supported by the supervisor proxy"},
                status=501,
            )
        if request.headers.get("Transfer-Encoding") and request.headers.get("Content-Length"):
            return web.json_response(
                {"error": "ambiguous request framing"},
                status=400,
            )

        headers = self._proxy_request_headers(request)
        target = f"http://127.0.0.1:{child.api_port}{request.raw_path}"
        has_body = request.can_read_body
        data = request.content.iter_chunked(64 * 1024) if has_body else None
        timeout = aiohttp.ClientTimeout(total=None, connect=5.0, sock_read=self.options.proxy_timeout)
        try:
            assert self._session is not None
            async with self._session.request(
                request.method,
                target,
                headers=headers,
                data=data,
                allow_redirects=False,
                timeout=timeout,
            ) as upstream:
                response = web.StreamResponse(
                    status=upstream.status,
                    reason=upstream.reason,
                    headers=self._proxy_response_headers(upstream.headers),
                )
                await response.prepare(request)
                if request.method != "HEAD":
                    async for chunk in upstream.content.iter_chunked(64 * 1024):
                        await response.write(chunk)
                await response.write_eof()
                return response
        except asyncio.CancelledError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionError, OSError) as exc:
            self.last_error = f"proxy error: {type(exc).__name__}: {exc}"
            self._record("proxy_error", error=self.last_error)
            self._write_status()
            return self._unavailable("bot child request failed")

    def _proxy_request_headers(self, request: web.Request) -> dict[str, str]:
        connection_tokens = {
            token.strip().lower()
            for token in (request.headers.get("Connection") or "").split(",")
            if token.strip()
        }
        headers: dict[str, str] = {}
        for key, value in request.headers.items():
            lower = key.lower()
            if lower in HOP_BY_HOP or lower in connection_tokens or lower in FORWARDED_HEADERS:
                continue
            if lower in {"host", "expect"}:
                continue
            headers[key] = value
        forwarded_host = request.host
        headers["Host"] = forwarded_host
        headers["X-Forwarded-Host"] = forwarded_host
        headers["X-Forwarded-Proto"] = request.scheme
        headers["X-Forwarded-For"] = request.remote or ""
        headers["X-Forwarded-Port"] = str(self.public_port or self.options.public_port)
        return headers

    @staticmethod
    def _proxy_response_headers(headers: Any) -> CIMultiDict:
        connection_tokens = {
            token.strip().lower()
            for token in (headers.get("Connection") or "").split(",")
            if token.strip()
        }
        result = CIMultiDict()
        for key, value in headers.items():
            lower = key.lower()
            if lower in HOP_BY_HOP or lower in connection_tokens:
                continue
            result.add(key, value)
        return result

    @staticmethod
    def _unavailable(reason: str) -> web.Response:
        return web.json_response(
            {
                "error": "service unavailable",
                "reason": reason,
                "retry_after": 1,
            },
            status=503,
            headers={"Retry-After": "1"},
        )

    # ── Status and helpers ────────────────────────────────────────────────

    def _readiness(self) -> tuple[bool, str]:
        child = self._child
        if self._stopping:
            return False, "supervisor is shutting down"
        if child is None:
            return False, "no child running"
        if child.exit_event.is_set():
            return False, "child has exited"
        if child.api_port is None:
            return False, "child api is not listening"
        if child.state == "draining" or self.state == "draining":
            return False, "child is draining"
        if not child.ready:
            return False, f"child state: {child.state}"
        if time.monotonic() - child.last_heartbeat > self.options.heartbeat_timeout:
            return False, "child heartbeat is stale"
        return True, "ready"

    def _child_summary(self) -> dict[str, Any] | None:
        child = self._child
        if child is None:
            return None
        return {
            "pid": child.pid,
            "state": child.state,
            "ready": child.ready,
            "api_port": child.api_port,
            "started_at": child.started_at,
            "last_heartbeat": child.last_heartbeat,
            "last_error": child.last_error,
            "readiness": child.readiness,
            "returncode": child.returncode,
        }

    def _status_snapshot(self) -> dict[str, Any]:
        return {
            "protocol": PROTOCOL_VERSION,
            "supervisor_pid": os.getpid(),
            "state": self.state,
            "ready": self.ready and self._readiness()[0],
            "public_port": self.public_port,
            "control_socket": str(self.options.control_socket),
            "started_at": self.started_at,
            "uptime_seconds": round(time.monotonic() - self.started_monotonic, 3),
            "child": self._child_summary(),
            "restart_count": self.restart_count,
            "child_starts": self.child_starts,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "last_stop_reason": self.last_stop_reason,
            "history": list(self._history),
        }

    def _record(self, event: str, **fields: Any) -> None:
        item = {
            "at": time.time(),
            "event": event,
            **fields,
        }
        self._history.append(item)
        del self._history[:-50]

    def _write_status(self) -> None:
        path = self.options.status_file
        payload = self._status_snapshot()
        try:
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            os.chmod(temporary, 0o600)
            os.replace(temporary, path)
        except OSError as exc:
            LOG.warning("could not write supervisor status: %s", exc)

    async def _cleanup_resources(self) -> None:
        self._shutdown_event.set()
        self._restart_signal.set()
        if self._supervise_task is not None and not self._supervise_task.done():
            self._supervise_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._supervise_task
        if self._control_server is not None:
            self._control_server.close()
            with contextlib.suppress(Exception):
                await self._control_server.wait_closed()
            self._control_server = None
        if self._runner is not None:
            with contextlib.suppress(Exception):
                await self._runner.cleanup()
            self._runner = None
        if self._session is not None:
            with contextlib.suppress(Exception):
                await self._session.close()
            self._session = None
        with contextlib.suppress(FileNotFoundError):
            self.options.control_socket.unlink()
        if self._lock_fd is not None:
            with contextlib.suppress(OSError):
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            with contextlib.suppress(OSError):
                os.close(self._lock_fd)
            self._lock_fd = None
        if self._startup_done:
            self._write_status()


def parse_args(argv: list[str] | None = None) -> Options:
    parser = argparse.ArgumentParser(description="Supervise the Niko bot child process.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "5000")))
    parser.add_argument("--child", type=Path, default=ROOT / "src" / "bot.py")
    parser.add_argument("--child-arg", action="append", default=[])
    parser.add_argument("--status-file", type=Path, default=ROOT / "data" / "run" / "supervisor.json")
    parser.add_argument("--control-socket", type=Path, default=ROOT / "data" / "run" / "supervisor.sock")
    parser.add_argument("--lock-file", type=Path, default=ROOT / "data" / "run" / "supervisor.lock")
    parser.add_argument("--startup-timeout", type=float, default=60.0)
    parser.add_argument("--heartbeat-timeout", type=float, default=12.0)
    parser.add_argument("--shutdown-timeout", type=float, default=8.0)
    parser.add_argument("--restart-backoff-initial", type=float, default=1.0)
    parser.add_argument("--restart-backoff-max", type=float, default=30.0)
    parser.add_argument("--restart-reset-after", type=float, default=60.0)
    parser.add_argument("--max-restarts", type=int, default=0)
    parser.add_argument("--proxy-timeout", type=float, default=300.0)
    parser.add_argument("--status-public", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)
    return Options(
        public_host=args.host,
        public_port=args.port,
        child_script=args.child,
        child_args=list(args.child_arg),
        status_file=args.status_file,
        control_socket=args.control_socket,
        lock_file=args.lock_file,
        startup_timeout=args.startup_timeout,
        heartbeat_timeout=args.heartbeat_timeout,
        shutdown_timeout=args.shutdown_timeout,
        restart_backoff_initial=args.restart_backoff_initial,
        restart_backoff_max=args.restart_backoff_max,
        restart_reset_after=args.restart_reset_after,
        max_restarts=args.max_restarts,
        proxy_timeout=args.proxy_timeout,
        status_public=args.status_public,
        log_level=args.log_level,
    )


def main(argv: list[str] | None = None) -> int:
    options = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, str(options.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s supervisor: %(message)s",
        stream=sys.stderr,
    )
    supervisor = Supervisor(options)
    try:
        asyncio.run(supervisor.run())
    except KeyboardInterrupt:
        return 0
    except RuntimeError as exc:
        print(f"supervisor: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"supervisor: could not start: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
