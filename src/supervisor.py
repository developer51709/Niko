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
import hmac
import importlib.util
import json
import logging
import os
import secrets
import shutil
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

from console_format import ConsoleFormatter
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
    #: Where the updater records the files a supervised restart is about to
    #: boot, and the root those paths are relative to.
    pending_update_file: Path = ROOT / "data" / "updates" / "pending.json"
    update_root: Path = ROOT
    #: When true (the default), the supervisor runs the dashboard in its own
    #: child process and the bot in another.  The dashboard child is the public
    #: one.  Set ``NIKO_SPLIT_WEB=0`` or pass ``--no-split-web`` to run the old
    #: combined child instead.
    split_web: bool = True
    web_child_script: Path = ROOT / "src" / "web_child.py"
    #: When true, the database runs in its own child too.  It defaults to the
    #: split layout; the combined fallback keeps the historical in-process pool.
    split_db: bool = True
    db_child_script: Path = ROOT / "src" / "db_child.py"
    #: Shared console store the owner's logs page reads.  Supervised processes
    #: append to it so a restart no longer starts an empty console.  ``None``
    #: keeps it beside the status file, which is what isolates test instances.
    log_store: Path | None = None
    log_store_bytes: int = 5 * 1024 * 1024
    log_store_backups: int = 3
    log_level: str = "INFO"

    def child_specs(self) -> list["ChildSpec"]:
        bot = ChildSpec(
            name="bot",
            script=self.child_script,
            args=list(self.child_args),
            primary=not self.split_web,
        )
        children: list[ChildSpec] = []
        if self.split_db:
            # The database starts first: the bot child waits for its port so a
            # restart never races the pool it is about to use.
            children.append(ChildSpec(name="db", script=self.db_child_script))
        if self.split_web:
            children.append(ChildSpec(name="web", script=self.web_child_script, primary=True))
        children.append(bot)
        return children


@dataclass
class ChildSpec:
    """One process the supervisor owns.

    ``primary`` marks the child that owns public traffic; its readiness is the
    service's readiness.  In split mode the web child is primary and the bot
    child is restarted without touching it.  In the combined fallback mode the
    bot child is both the gateway and the dashboard, so it is primary.
    """

    name: str
    script: Path
    args: list[str] = field(default_factory=list)
    primary: bool = False


@dataclass
class ChildSlot:
    """Per-child bookkeeping that outlives each individual process."""

    spec: ChildSpec
    state: str = "starting"
    restarts: int = 0
    failures: int = 0
    last_error: str | None = None
    last_stop_reason: str | None = None
    restart_requested: bool = False


@dataclass
class Child:
    proc: asyncio.subprocess.Process
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    started_at: float
    name: str = "bot"
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

        self._log_store_path = Path(
            options.log_store or (options.status_file.parent / "logs")
        )
        self._log_store: Any = None
        self._log_handler: logging.Handler | None = None
        self._specs = options.child_specs()
        self._slots: dict[str, ChildSlot] = {
            spec.name: ChildSlot(spec=spec) for spec in self._specs
        }
        self._children: dict[str, Child] = {}
        self._history: list[dict[str, Any]] = []
        self._lock_fd: int | None = None
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._control_server: asyncio.AbstractServer | None = None
        self._session: aiohttp.ClientSession | None = None
        #: Only the supervisor and its children know this value.  It is what
        #: makes the loopback-only update entry point unusable by anything else
        #: on the host, including a reverse-proxied public request.
        self._internal_token = secrets.token_urlsafe(32)
        self._supervise_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()
        self._restart_signal = asyncio.Event()
        self._restart_pending = False
        self._stopping = False
        self._shutdown_future: asyncio.Task | None = None
        self._startup_done = False

    # ── Children ──────────────────────────────────────────────────────────

    @property
    def _child(self) -> Child | None:
        """The primary child: the one public traffic is proxied to."""
        for slot in self._slots.values():
            if slot.spec.primary:
                return self._children.get(slot.spec.name)
        return None

    def _child_named(self, name: str | None) -> Child | None:
        if name is None:
            return None
        return self._children.get(name)

    @property
    def _bot_child(self) -> Child | None:
        return self._children.get("bot")

    def _slot_of(self, child: Child) -> ChildSlot:
        return self._slots[child.name]

    def _refresh_state(self) -> None:
        """Derive supervisor state from the children.

        Readiness is the primary child's: the public surface is what Render's
        health check cares about.  A bot child that is still booting must not
        make the platform restart a service whose dashboard is answering.
        """
        if self._stopping:
            self.state = "stopped"
            self.ready = False
            return
        primary = self._primary_slot()
        primary_ready = bool(
            primary is not None
            and self._children.get(primary.spec.name) is not None
            and self._children[primary.spec.name].ready
        )
        states = {
            slot.spec.name: self._children.get(slot.spec.name)
            for slot in self._slots.values()
        }
        ready_children = [child for child in states.values() if child is not None and child.ready]
        if primary_ready:
            others_ready = all(
                child is not None and child.ready
                for name, child in states.items()
                if name != (primary.spec.name if primary is not None else None)
            )
            self.state = "active" if others_ready else "degraded"
            self.ready = True
            return
        if ready_children:
            self.state = "degraded"
            self.ready = False
            return
        if all(slot.state == "failed" for slot in self._slots.values()):
            self.state = "failed"
        elif any(slot.state == "draining" for slot in self._slots.values()):
            self.state = "draining"
        elif any(child is not None for child in states.values()):
            self.state = "starting"
        else:
            self.state = "restarting"
        self.ready = False

    def _primary_slot(self) -> ChildSlot | None:
        for slot in self._slots.values():
            if slot.spec.primary:
                return slot
        return next(iter(self._slots.values()), None)

    # ── Public server and status ──────────────────────────────────────────

    async def run(self) -> None:
        try:
            self._prepare_paths()
            self._install_log_store()
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
        children = list(self._children.values())
        for child in children:
            await self._terminate_child(child, "supervisor shutdown")
        if self._supervise_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._supervise_task
        for child in list(self._children.values()):
            await self._cleanup_child(child)
        # A draining/stopped event from the child must not overwrite the final
        # supervisor state during an intentional shutdown.
        self.state = "stopped"
        self.ready = False
        await self._cleanup_resources()
        self._write_status()
        LOG.info("supervisor stopped")

    def _install_log_store(self) -> None:
        """Mirror the supervisor's own log records into its process buffer."""
        try:
            from log_store import LogArchive

            self._log_store = LogArchive(
                self._log_store_path,
                max_bytes=self.options.log_store_bytes,
                backups=self.options.log_store_backups,
            )
        except Exception as error:
            self._log_store = None
            LOG.warning("owner log archive unavailable: %s", error)
            return

        store = self._log_store

        class _StoreHandler(logging.Handler):
            def __init__(self) -> None:
                super().__init__(level=logging.NOTSET)
                # Same rendering as the terminal (and as the bot's own store
                # lines), so the owner's logs page shows one consistent style.
                self.setFormatter(ConsoleFormatter())

            def emit(self, record: logging.LogRecord) -> None:
                try:
                    store.append(
                        level=record.levelname,
                        logger=record.name,
                        line=self.format(record),
                        process="supervisor",
                        at=record.created,
                    )
                except Exception:
                    pass

        self._log_handler = _StoreHandler()
        logging.getLogger().addHandler(self._log_handler)

    def _remove_log_handler(self) -> None:
        if self._log_handler is not None:
            logging.getLogger().removeHandler(self._log_handler)
            self._log_handler = None

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
        # Recovery path: beta can force an update over the supervisor's own
        # public listener even when the dashboard child is down.  It is hidden
        # (404) unless BETA_UPDATE_TOKEN is configured.
        app.router.add_post("/supervisor/update", self._force_update)
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

    async def _force_update(self, request: web.Request) -> web.Response:
        """Run a beta-initiated update without relying on the dashboard child.

        The update itself still runs in the bot child (it owns the modules and
        the Discord connection), but the supervisor answers on its own public
        socket, so a crashed or crash-looping dashboard child cannot lock the
        owner out of the recovery path.  ``BETA_UPDATE_TOKEN`` is the shared
        secret beta already uses; no new trust relationship is introduced.
        """
        expected = (os.environ.get("BETA_UPDATE_TOKEN") or "").strip()
        supplied = request.headers.get("X-Update-Token", "")
        # Bytes, not str: a non-ASCII header must fail auth like any other wrong
        # token instead of raising inside compare_digest.
        if not expected or not hmac.compare_digest(
            supplied.encode("utf-8", "replace"), expected.encode("utf-8", "replace")
        ):
            # Same response as an unconfigured instance: a caller cannot probe
            # whether this deployment has the recovery path enabled.
            raise web.HTTPNotFound()

        if request.content_length is not None and request.content_length > 16 * 1024:
            return web.json_response({"error": "request body is too large"}, status=413)
        raw = await request.read()
        if len(raw) > 16 * 1024:
            return web.json_response({"error": "request body is too large"}, status=413)
        try:
            body = json.loads(raw) if raw else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return web.json_response({"error": "expected a JSON object"}, status=400)
        if not isinstance(body, dict):
            return web.json_response({"error": "expected a JSON object"}, status=400)
        areas = body.get("areas")
        if areas is not None and (
            not isinstance(areas, list)
            or not all(isinstance(name, str) for name in areas)
        ):
            return web.json_response(
                {"error": "areas must be a list of area names"}, status=400
            )

        if self._stopping:
            return web.json_response({"error": "supervisor is shutting down"}, status=503)
        child = self._bot_child
        if (
            child is None
            or child.api_port is None
            or child.exit_event.is_set()
            or not child.ready
        ):
            return web.json_response(
                {
                    "error": "the bot child is not ready; no update can run",
                    "retry_after": 5,
                },
                status=503,
                headers={"Retry-After": "5"},
            )
        session = self._session
        if session is None:
            return web.json_response({"error": "supervisor is starting"}, status=503)

        LOG.warning(
            "forced update requested by beta (areas=%s)",
            ",".join(areas) if areas else "all",
        )
        payload = {"areas": areas} if areas is not None else {}
        try:
            # Applying a bot-core change downloads every file it needs before
            # requesting a restart, so the read side is deliberately generous.
            timeout = aiohttp.ClientTimeout(total=900.0, connect=5.0, sock_read=900.0)
            async with session.post(
                f"http://127.0.0.1:{child.api_port}/api/updates/force",
                json=payload,
                headers={
                    "X-Supervisor-Token": self._internal_token,
                    "Accept": "application/json",
                },
                timeout=timeout,
            ) as response:
                data = await response.json(content_type=None)
                status = response.status
        except asyncio.TimeoutError:
            return web.json_response(
                {
                    "error": "the bot child did not finish the update within 15 "
                    "minutes; it may still be running"
                },
                status=504,
            )
        except Exception as exc:
            LOG.warning("forced update could not reach the bot child: %s", exc)
            return web.json_response(
                {"error": "the bot child did not answer the update request"},
                status=502,
            )
        if not isinstance(data, dict):
            return web.json_response(
                {"error": "the bot child returned an invalid update response"},
                status=502,
            )
        return web.json_response(data, status=status)

    # ── Child supervision ─────────────────────────────────────────────────

    async def _supervise(self) -> None:
        """Supervise every child concurrently.

        Each child owns its restart budget, readiness and exit history, so a
        dashboard restart never stops the gateway and a bot crash never takes
        the dashboard down with it.
        """
        try:
            await asyncio.gather(
                *(
                    asyncio.create_task(
                        self._supervise_child(slot),
                        name=f"supervise-{slot.spec.name}",
                    )
                    for slot in self._slots.values()
                )
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            LOG.exception("supervision loop crashed")
            self.last_error = "supervision loop crashed; see supervisor logs"
            self.state = "failed"
            self._write_status()

    async def _supervise_child(self, slot: ChildSlot) -> None:
        name = slot.spec.name
        try:
            while not self._shutdown_event.is_set():
                child = self._children.get(name)
                if child is None:
                    if slot.state == "failed" and not slot.restart_requested:
                        await self._wait_for_wake()
                        if self._shutdown_event.is_set():
                            break
                    if slot.restart_requested:
                        slot.restart_requested = False
                        slot.failures = 0
                    slot.state = "starting"
                    self._refresh_state()
                    self._record("child_starting", child=name)
                    self._write_status()
                    try:
                        await self._start_child(slot)
                    except Exception as exc:
                        slot.restarts += 1
                        slot.failures += 1
                        slot.state = "restarting"
                        slot.last_error = (
                            f"{name} spawn failed: {type(exc).__name__}: {exc}"
                        )
                        self.last_error = slot.last_error
                        LOG.error("%s", slot.last_error)
                        self._record("spawn_failed", child=name, error=slot.last_error)
                        self._refresh_state()
                        self._write_status()
                        if not self._allow_restart(slot):
                            slot.state = "failed"
                            self._refresh_state()
                            self._write_status()
                            await self._wait_for_wake()
                        else:
                            await self._backoff(slot)
                        continue
                    self._refresh_state()
                    self._write_status()
                    continue

                await child.exit_event.wait()
                await self._cleanup_child(child)
                if self._shutdown_event.is_set():
                    break

                # An update's bot that never became ready is the one case we can
                # repair without the app's help: the updater recorded what it
                # replaced, so restore those files before booting again.  A
                # dashboard child carries no bot area and is not a rollback
                # trigger.
                if name == "bot" and child.ready_at is None and not child.restart_requested:
                    self._rollback_pending_update()

                if child.restart_requested:
                    slot.last_stop_reason = child.stop_reason or "control restart"
                    slot.failures = 0
                    slot.state = "restarting"
                    self.last_stop_reason = slot.last_stop_reason
                    self._refresh_state()
                    self._record("child_restarting", child=name, reason=slot.last_stop_reason)
                    self._write_status()
                    continue

                slot.restarts += 1
                slot.failures += 1
                slot.last_error = (
                    f"{name} exited with code {child.returncode}"
                    + (f" ({child.stop_reason})" if child.stop_reason else "")
                )
                slot.last_stop_reason = child.stop_reason or "child exit"
                slot.state = "restarting"
                self.restart_count += 1
                self.consecutive_failures = slot.failures
                self.last_error = slot.last_error
                self.last_stop_reason = slot.last_stop_reason
                self._refresh_state()
                self._record(
                    "child_exited",
                    child=name,
                    returncode=child.returncode,
                    restart_count=slot.restarts,
                    reason=child.stop_reason,
                )
                self._write_status()
                if not self._allow_restart(slot):
                    slot.state = "failed"
                    slot.last_error = (
                        f"{name} restart limit reached after {slot.failures} failures"
                    )
                    self.last_error = slot.last_error
                    self._record("child_failed", child=name, error=slot.last_error)
                    self._refresh_state()
                    self._write_status()
                    await self._wait_for_wake()
                    continue
                await self._backoff(slot)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOG.exception("supervision loop for %s crashed", name)
            slot.state = "failed"
            slot.last_error = f"{name} supervision loop crashed"
            self.last_error = slot.last_error
            self._refresh_state()
            self._write_status()

    async def _await_sibling_port(self, name: str, timeout: float) -> int | None:
        """Wait briefly for a sibling child to report its loopback port.

        Children start concurrently, and the bot needs the database child's
        port before it can attach its pool.  The port is also discoverable over
        the control socket afterwards, so a timeout here only means "ask the
        supervisor later" rather than a failure.
        """
        deadline = time.monotonic() + max(0.0, timeout)
        while not self._shutdown_event.is_set():
            child = self._children.get(name)
            if child is not None and child.api_port:
                return child.api_port
            if time.monotonic() >= deadline:
                return None
            await asyncio.sleep(0.05)
        return None

    async def _start_child(self, slot: ChildSlot) -> None:
        if self._shutdown_event.is_set():
            return
        if slot.spec.name == "bot" and self.options.split_db:
            await self._await_sibling_port(
                "db", min(15.0, self.options.startup_timeout / 2)
            )
        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        parent_sock.setblocking(False)
        child_sock.set_inheritable(True)
        env = self._child_environment(child_sock.fileno(), slot)
        command = [
            sys.executable,
            "-u",
            str(slot.spec.script),
            *slot.spec.args,
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
            name=slot.spec.name,
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
        self._children[child.name] = child
        slot.state = "process_started"
        self._record("child_started", child=child.name, pid=child.pid)
        LOG.info("child %s started pid=%s", child.name, child.pid)
        self._write_status()

    def _child_environment(
        self,
        control_fd: int,
        slot: ChildSlot | None = None,
    ) -> dict[str, str]:
        slot = slot or self._primary_slot()
        assert slot is not None
        env = dict(os.environ)
        for key in (
            "NIKO_RESTART_FD",
            "NIKO_HANDOFF_ROLE",
            "NIKO_CHILD_PORT",
            "NIKO_IMPORT_PROBE",
            "NIKO_CHILD_NAME",
            "NIKO_WEB_ROLE",
            "NIKO_INTERNAL_TOKEN",
            "NIKO_BOT_API_PORT",
            "NIKO_DB_API_PORT",
            "NIKO_SPLIT_WEB",
            "NIKO_SPLIT_DB",
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
                "NIKO_CHILD_NAME": slot.spec.name,
                CONTROL_FD_ENV: str(control_fd),
                CONTROL_SOCKET_ENV: str(self.options.control_socket.resolve()),
                PUBLIC_PORT_ENV: str(self.public_port or self.options.public_port),
                "NIKO_SPLIT_WEB": "1" if self.options.split_web else "0",
                "NIKO_SPLIT_DB": "1" if self.options.split_db else "0",
                "NIKO_LOG_STORE": str(self._log_store_path.resolve()),
                "NIKO_LOG_STORE_BYTES": str(self.options.log_store_bytes),
                "NIKO_LOG_STORE_BACKUPS": str(self.options.log_store_backups),
                "PYTHONUNBUFFERED": "1",
            }
        )
        if slot.spec.name in {"bot", "db"}:
            # Only the children that answer loopback calls need the supervisor's
            # credential: the bot runs updates and reads the database, the
            # database child serves it.  The dashboard child never gets it.
            env["NIKO_INTERNAL_TOKEN"] = self._internal_token
        if slot.spec.name == "bot" and self.options.split_db:
            db = self._children.get("db")
            if db is not None and db.api_port:
                env["NIKO_DB_API_PORT"] = str(db.api_port)
        if slot.spec.name == "web":
            # The dashboard child forwards live-bot routes to the bot child's
            # loopback API.  It has no gateway of its own.
            env["NIKO_WEB_ROLE"] = "1"
            bot = self._children.get("bot")
            if bot is not None and bot.api_port:
                env["NIKO_BOT_API_PORT"] = str(bot.api_port)
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
            self._slot_of(child).state = "draining"
        elif event in {"ready", "degraded"}:
            child.ready = True
            child.ready_at = time.monotonic()
            child.state = event
            child.readiness = payload.get("checks") if isinstance(payload.get("checks"), dict) else None
            self._slot_of(child).state = event
            self._record(
                "child_ready",
                child=child.name,
                state=event,
                reasons=payload.get("reasons") or [],
            )
            # The release the pending update delivered is now serving, so it is
            # no longer a rollback candidate.  Only the bot child carries the
            # bot area; a dashboard child becoming ready says nothing about it.
            if child.name == "bot":
                self._confirm_pending_update()
        elif event in {"readiness_failed", "error"}:
            reason = str(payload.get("reason") or payload.get("message") or event)
            child.last_error = reason
            child.readiness = payload.get("checks") if isinstance(payload.get("checks"), dict) else None
            child.ready = False
            self._slot_of(child).last_error = reason
            self.last_error = reason
            self._record("child_not_ready", child=child.name, reason=reason)
            self._refresh_state()
            await self._terminate_child(child, "readiness failed")
            return
        elif event == "stopped":
            child.state = "stopped"
            child.ready = False
            self._slot_of(child).state = "stopped"
        else:
            LOG.debug("unknown child event: %s", event)
            return

        self._record(f"child_{event}", child=child.name, state=child.state)
        self._refresh_state()
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
                slot = self._slot_of(child)
                if (
                    child.ready_at is not None
                    and now - child.ready_at >= self.options.restart_reset_after
                    and slot.failures
                ):
                    slot.failures = 0
                    self.consecutive_failures = 0
                    self._record("failure_counter_reset", child=child.name)
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
            # An operator-initiated shutdown is expected, not a fault.
            emit = LOG.info if reason == "supervisor shutdown" else LOG.warning
            emit("stopping child pid=%s: %s", child.pid, reason)
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
        if self._children.get(child.name) is child:
            self._children.pop(child.name, None)
        slot = self._slots.get(child.name)
        if slot is not None and slot.state not in {"failed", "restarting"}:
            slot.state = "stopped"
        self._refresh_state()
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
                    self._log_child_line(line)
                if len(buffer) >= 64 * 1024:
                    self._log_child_line(bytes(buffer), truncated=True)
                    buffer.clear()
            if buffer:
                self._log_child_line(bytes(buffer))
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError):
            pass

    def _log_child_line(
        self,
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
        # The child already rendered its own console line in the bot's style
        # (clock, level, module); re-prefixing it would stack a second
        # timestamp on top.  Pass it through untouched, like the bot's own
        # terminal output.  The child writes its records to the shared store
        # itself, so this line is terminal-only.
        print(f"{text}{suffix}", file=sys.stderr, flush=True)

    async def _backoff(self, slot: ChildSlot | None = None) -> None:
        failures = slot.failures if slot is not None else self.consecutive_failures
        exponent = max(0, failures - 1)
        delay = min(
            self.options.restart_backoff_initial * (2**exponent),
            self.options.restart_backoff_max,
        )
        self._record(
            "restart_backoff",
            child=slot.spec.name if slot is not None else None,
            seconds=round(delay, 3),
        )
        await self._wait_for_wake(delay)

    def _allow_restart(self, slot: ChildSlot | None = None) -> bool:
        limit = self.options.max_restarts
        failures = slot.failures if slot is not None else self.consecutive_failures
        return limit <= 0 or failures <= limit

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
        if command == "route":
            bot = self._bot_child
            db = self._children.get("db")
            return {
                "ok": True,
                "split_web": self.options.split_web,
                "split_db": self.options.split_db,
                "bot_api_port": bot.api_port if bot is not None else None,
                "db_api_port": db.api_port if db is not None else None,
            }
        if command == "restart":
            if self._stopping:
                return {"ok": False, "error": "supervisor is shutting down"}
            try:
                delay = max(0.0, float(payload.get("delay", 0.0) or 0.0))
            except (TypeError, ValueError):
                return {"ok": False, "error": "delay must be a number"}
            reason = str(payload.get("reason") or "control restart")
            targets = self._restart_targets(payload.get("child") or payload.get("target"))
            if targets is None:
                return {
                    "ok": False,
                    "error": f"unknown child: {payload.get('child') or payload.get('target')}",
                }
            self._request_restart(delay, reason, targets)
            child = self._child
            return {
                "ok": True,
                "accepted": True,
                "delay": delay,
                "children": [slot.spec.name for slot in targets],
                "child_pid": child.pid if child else None,
            }
        if command == "shutdown":
            asyncio.create_task(self.shutdown())
            return {"ok": True, "accepted": True}
        return {"ok": False, "error": f"unknown control command: {command or '<empty>'}"}

    def _restart_targets(self, target: Any) -> list[ChildSlot] | None:
        """Resolve a control restart target: ``None``/``all`` means every child."""
        if target in (None, "", "all", "*"):
            return list(self._slots.values())
        names = [str(target)] if isinstance(target, str) else [str(item) for item in target]
        selected: list[ChildSlot] = []
        for name in names:
            slot = self._slots.get(name)
            if slot is None:
                return None
            selected.append(slot)
        return selected

    def _request_restart(
        self,
        delay: float,
        reason: str,
        targets: list[ChildSlot] | None = None,
    ) -> None:
        slots = list(targets) if targets is not None else list(self._slots.values())

        async def request_after_delay() -> None:
            if delay:
                await asyncio.sleep(delay)
            if self._shutdown_event.is_set():
                return
            wake = False
            for slot in slots:
                child = self._children.get(slot.spec.name)
                if child is None:
                    slot.restart_requested = True
                    wake = True
                    continue
                child.restart_requested = True
                child.stop_reason = reason
                await self._terminate_child(child, reason)
            if wake:
                self._restart_signal.set()

        asyncio.create_task(request_after_delay(), name="control-restart")

    # ── Reverse proxy ─────────────────────────────────────────────────────

    async def _proxy(self, request: web.Request) -> web.StreamResponse:
        # Discord interactions must reach the gateway child directly: they are
        # signed for that process's application key and carry a hard deadline.
        # Everything else belongs to the primary (dashboard) child.
        child = self._child
        if request.path.startswith("/api/discord/interactions"):
            child = self._bot_child or self._child
        if (
            self._stopping
            or child is None
            or child.api_port is None
            or child.exit_event.is_set()
        ):
            name = child.name if child is not None else "child"
            return self._unavailable(f"{name} child is not serving")

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
            self.last_error = f"proxy error ({child.name}): {type(exc).__name__}: {exc}"
            self._record("proxy_error", child=child.name, error=self.last_error)
            self._write_status()
            return self._unavailable(f"{child.name} child request failed")

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
        if child.state == "draining":
            return False, "child is draining"
        if not child.ready:
            return False, f"{child.name} child state: {child.state}"
        if time.monotonic() - child.last_heartbeat > self.options.heartbeat_timeout:
            return False, "child heartbeat is stale"
        return True, "ready"

    def _child_summary(self, child: Child | None = None) -> dict[str, Any] | None:
        child = self._child if child is None else child
        if child is None:
            return None
        return {
            "name": child.name,
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

    def _children_summary(self) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        for name, slot in self._slots.items():
            child = self._children.get(name)
            summary[name] = {
                "primary": slot.spec.primary,
                "state": child.state if child is not None else slot.state,
                "ready": bool(child is not None and child.ready),
                "restarts": slot.restarts,
                "consecutive_failures": slot.failures,
                "last_error": (child.last_error if child is not None else slot.last_error),
                "pid": child.pid if child is not None else None,
                "api_port": child.api_port if child is not None else None,
            }
        return summary

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
            "split_web": self.options.split_web,
            "split_db": self.options.split_db,
            "child": self._child_summary(),
            "children": self._children_summary(),
            "restart_count": self.restart_count,
            "child_starts": self.child_starts,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "last_stop_reason": self.last_stop_reason,
            "pending_update": self._pending_summary(),
            "history": list(self._history),
        }

    # ── Last-good rollback ────────────────────────────────────────────────

    def _pending_update(self) -> dict[str, Any] | None:
        try:
            payload = json.loads(self.options.pending_update_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None

    def _pending_summary(self) -> dict[str, Any] | None:
        pending = self._pending_update()
        if pending is None:
            return None
        return {
            "run_id": pending.get("run_id"),
            "area": pending.get("area"),
            "requested_at": pending.get("requested_at"),
            "changes": len(pending.get("changes") or ()),
        }

    def _retire_pending_update(self, suffix: str) -> None:
        path = self.options.pending_update_file
        if not path.exists():
            return
        target = path.with_name(f"{path.name}.{suffix}-{int(time.time())}")
        with contextlib.suppress(OSError):
            path.replace(target)

    def _confirm_pending_update(self) -> None:
        pending = self._pending_update()
        if pending is None:
            return
        self._record("update_confirmed", run=pending.get("run_id"), area=pending.get("area"))
        self._retire_pending_update("confirmed")

    def _update_path(self, relative: str) -> Path | None:
        """Resolve an updater path, refusing anything outside the update root."""
        if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            return None
        root = self.options.update_root.resolve()
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return None
        return candidate

    def _forget_bytecode(self, target: Path) -> None:
        """A restored source must not keep importing the failed release's .pyc."""
        if target.suffix != ".py":
            return
        try:
            cached = Path(importlib.util.cache_from_source(str(target)))
        except (NotImplementedError, ValueError):
            return
        with contextlib.suppress(OSError):
            cached.unlink()

    def _rollback_pending_update(self) -> bool:
        """Restore the files an update replaced, after its child failed to boot.

        The updater writes ``pending.json`` just before asking for a supervised
        restart.  If the replacement never becomes ready, this copies the run's
        backups back (and removes files the update had added), then lets the
        supervision loop start a last-good child.  Everything is a plain file
        operation, so the supervisor still imports no application code.
        """
        pending = self._pending_update()
        if pending is None:
            return False
        run_id = pending.get("run_id")
        backup_dir = str(pending.get("backup_dir") or "")
        restored = 0
        removed = 0
        try:
            for change in pending.get("changes") or ():
                if not isinstance(change, dict):
                    continue
                relative = str(change.get("path") or "")
                target = self._update_path(relative)
                backup = self._update_path(f"{backup_dir}/{relative}") if backup_dir else None
                if target is None or backup is None:
                    raise ValueError(f"unsafe path in pending update: {relative!r}")
                if backup.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup, target)
                    self._forget_bytecode(target)
                    restored += 1
                elif str(change.get("status") or "") == "added" and target.is_file():
                    target.unlink()
                    self._forget_bytecode(target)
                    removed += 1
        except Exception as exc:
            self.last_error = f"last-good rollback failed: {type(exc).__name__}: {exc}"
            LOG.error("%s", self.last_error)
            self._record("rollback_failed", run=run_id, error=self.last_error)
            self._retire_pending_update("failed")
            self._write_status()
            return False

        self.last_error = f"update {run_id} did not boot; restored the last-good files"
        self.last_stop_reason = f"rolled back update {run_id}"
        self._record(
            "rollback_applied",
            run=run_id,
            area=pending.get("area"),
            restored=restored,
            removed=removed,
        )
        LOG.warning(
            "rolled back update %s: %s file(s) restored, %s added file(s) removed",
            run_id,
            restored,
            removed,
        )
        self._retire_pending_update("rolledback")
        self._write_status()
        return True

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
        self._remove_log_handler()
        if self._log_store is not None:
            with contextlib.suppress(Exception):
                self._log_store.close()
            self._log_store = None
        if self._startup_done:
            self._write_status()


def parse_args(argv: list[str] | None = None) -> Options:
    parser = argparse.ArgumentParser(description="Supervise the Niko bot child process.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "5000")))
    parser.add_argument("--child", type=Path, default=ROOT / "src" / "bot.py")
    parser.add_argument("--child-arg", action="append", default=[])
    split_default = (os.environ.get("NIKO_SPLIT_WEB") or "").strip().lower()
    parser.add_argument(
        "--split-web",
        dest="split_web",
        action="store_true",
        default=split_default not in {"0", "false", "no", "off"},
        help="run the dashboard and the bot as separate children (default)",
    )
    parser.add_argument(
        "--no-split-web",
        dest="split_web",
        action="store_false",
        help="run the bot and dashboard in one child (fallback)",
    )
    parser.add_argument("--web-child", type=Path, default=ROOT / "src" / "web_child.py")
    parser.add_argument(
        "--split-db",
        dest="split_db",
        action="store_true",
        default=None,
        help="run the database in its own child (default: follow --split-web)",
    )
    parser.add_argument(
        "--no-split-db",
        dest="split_db",
        action="store_false",
        help="keep the database pool inside the bot child (combined fallback)",
    )
    parser.add_argument("--db-child", type=Path, default=ROOT / "src" / "db_child.py")
    parser.add_argument("--log-store", type=Path, default=None)
    parser.add_argument("--log-store-bytes", type=int, default=5 * 1024 * 1024)
    parser.add_argument("--log-store-backups", type=int, default=3)
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
    parser.add_argument(
        "--pending-update-file",
        type=Path,
        default=ROOT / "data" / "updates" / "pending.json",
    )
    parser.add_argument("--update-root", type=Path, default=ROOT)
    parser.add_argument("--status-public", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)
    split_db = args.split_db
    if split_db is None:
        env_value = (os.environ.get("NIKO_SPLIT_DB") or "").strip().lower()
        if env_value in {"0", "false", "no", "off"}:
            split_db = False
        elif env_value in {"1", "true", "yes", "on"}:
            split_db = True
        else:
            split_db = args.split_web
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
        pending_update_file=args.pending_update_file,
        update_root=args.update_root,
        split_web=args.split_web,
        web_child_script=args.web_child,
        split_db=split_db,
        db_child_script=args.db_child,
        log_store=args.log_store,
        log_store_bytes=args.log_store_bytes,
        log_store_backups=args.log_store_backups,
        status_public=args.status_public,
        log_level=args.log_level,
    )


def _load_shared_env() -> None:
    """Read ``src/.env`` the way the bot child does.

    The force-update endpoint needs ``BETA_UPDATE_TOKEN`` in the supervisor's own
    environment.  Hosted deployments set it in the process environment, while a
    self-hosted install follows the setup guide and keeps it in ``src/.env``;
    loading that file keeps both arrangements working without exporting the
    secret a second time.
    """
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv(ROOT / "src" / ".env")


def main(argv: list[str] | None = None) -> int:
    _load_shared_env()
    options = parse_args(argv)
    level = getattr(logging, str(options.log_level).upper(), logging.INFO)
    # Same formatter as the bot, so supervised output and the bot's own lines
    # line up in one console.  The root logger captures everything so the
    # shared console store keeps DEBUG/INFO history the terminal was configured
    # to hide, exactly like the application's own logger; only the stream
    # handler is filtered.
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(ConsoleFormatter())
    console.setLevel(level)
    logging.basicConfig(level=logging.DEBUG, handlers=[console])
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
