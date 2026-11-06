"""A controllable child for supervisor Part 1 tests.

It speaks the same newline-delimited JSON lifecycle protocol as the real child
will, and it serves a small HTTP surface through an ephemeral loopback port so
the supervisor proxy can be tested without Discord, Flask, or a database.

Modes are selected with ``FAKE_CHILD_MODE``:
    normal           become ready and serve until SIGTERM
    crash            exit before reporting process_started
    crash-after-api  report api_listening, then exit
    fail-readiness   bind the API and report readiness_failed
    hang-before-api  report process_started and never bind the API
    hang-after-ready become ready, then stop heartbeating but keep serving
    ignore-sigterm   become ready and ignore SIGTERM
    leak-child       become ready and spawn a grandchild that outlives boot

Additional test knobs:
    FAKE_CHILD_BOOT_DELAY       seconds before api_listening
    FAKE_CHILD_READY_DELAY      seconds between api_listening and ready
    FAKE_CHILD_EXIT_AFTER       seconds after ready before os._exit(1)
    FAKE_CHILD_HEARTBEAT        heartbeat interval in seconds
    FAKE_CHILD_CRASH_ONCE       marker path: first run crashes, later runs are normal
    FAKE_CHILD_LOG_FLOOD        write continuous large stdout lines
    FAKE_CHILD_STAGE_MARKER     directory: touch one file per lifecycle event sent
    FAKE_CHILD_STAGE_HOLD       stage name to stop at (after reporting it)
    FAKE_CHILD_STAGE_HOLD_ONCE  marker path: only the first child holds, later
                                runs boot normally, so recovery can be tested
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from supervisor_protocol import ChildReporter, install_parent_death_signal  # noqa: E402


class FakeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "fake-child/1"

    def log_message(self, _format: str, *_args) -> None:
        pass

    def _write_json(self, status: int, payload: dict, headers: list[tuple[str, str]] | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for key, value in headers or []:
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _read_body(self) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._write_json(200, {"ok": True})
            return
        if path == "/echo":
            self._write_json(
                200,
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": {key: value for key, value in self.headers.items()},
                    "body_length": 0,
                },
            )
            return
        if path == "/cookies":
            body = b"cookies"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Set-Cookie", "first=one; Path=/; HttpOnly")
            self.send_header("Set-Cookie", "second=two; Path=/; SameSite=Lax")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/landing")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/download":
            body = b"0123456789" * 4096
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/range":
            body = bytes(range(256)) * 4
            start, end = 10, 19
            range_header = self.headers.get("Range", "")
            if range_header.startswith("bytes="):
                try:
                    raw_start, raw_end = range_header[6:].split("-", 1)
                    start = int(raw_start)
                    end = int(raw_end) if raw_end else len(body) - 1
                except ValueError:
                    start, end = 0, len(body) - 1
            start = max(0, min(start, len(body) - 1))
            end = max(start, min(end, len(body) - 1))
            chunk = body[start : end + 1]
            self.send_response(206 if range_header else 200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Accept-Ranges", "bytes")
            if range_header:
                self.send_header("Content-Range", f"bytes {start}-{end}/{len(body)}")
            self.end_headers()
            self.wfile.write(chunk)
            return
        if path == "/slow":
            time.sleep(0.2)
            self._write_json(200, {"slept": True})
            return
        self._write_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        body = self._read_body()
        path = self.path.split("?", 1)[0]
        if path in {"/echo", "/upload"}:
            self._write_json(
                200,
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": {key: value for key, value in self.headers.items()},
                    "body_length": len(body),
                    "body": body.decode("utf-8", errors="replace")[:200],
                },
            )
            return
        self._write_json(404, {"error": "not found"})


class FakeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _run_server(server: FakeServer) -> None:
    server.serve_forever(poll_interval=0.05)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fake supervised child for supervisor tests.")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args(argv)

    mode = os.environ.get("FAKE_CHILD_MODE", "normal")
    reporter = ChildReporter.from_environment()
    install_parent_death_signal()
    stop = threading.Event()
    server: FakeServer | None = None
    server_thread: threading.Thread | None = None

    # Stage instrumentation: a test can wait for the exact event and then kill
    # the child there, and the hold keeps the first child parked at that stage
    # so the kill lands where the test intends.
    stage_marker = (os.environ.get("FAKE_CHILD_STAGE_MARKER") or "").strip()
    hold_stage = (os.environ.get("FAKE_CHILD_STAGE_HOLD") or "").strip()
    hold_marker = (os.environ.get("FAKE_CHILD_STAGE_HOLD_ONCE") or "").strip()
    holding = bool(hold_stage) and not (hold_marker and Path(hold_marker).exists())
    if holding and hold_marker:
        Path(hold_marker).write_text("held", encoding="utf-8")

    def stage(name: str) -> None:
        if stage_marker:
            directory = Path(stage_marker)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / name).touch()
        if holding and name == hold_stage:
            while not stop.wait(0.05):
                reporter.heartbeat()

    def stop_child(_signum=None, _frame=None) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, stop_child)
    signal.signal(signal.SIGINT, stop_child)
    if mode == "ignore-sigterm":
        signal.signal(signal.SIGTERM, lambda *_args: None)
        signal.signal(signal.SIGINT, lambda *_args: None)

    try:
        reporter.send("process_started", mode=mode)
        stage("process_started")

        marker = os.environ.get("FAKE_CHILD_CRASH_ONCE")
        if marker and not Path(marker).exists():
            Path(marker).write_text("crashed", encoding="utf-8")
            os._exit(7)

        if mode == "crash":
            os._exit(7)

        boot_delay = max(0.0, float(os.environ.get("FAKE_CHILD_BOOT_DELAY", "0")))
        if boot_delay and stop.wait(boot_delay):
            return 0

        if mode == "hang-before-api":
            while not stop.wait(0.1):
                reporter.heartbeat()
            return 0

        server = FakeServer(("127.0.0.1", args.port), FakeHandler)
        server_thread = threading.Thread(target=_run_server, args=(server,), name="fake-http", daemon=True)
        server_thread.start()
        port = int(server.server_address[1])
        reporter.send("api_listening", port=port)
        stage("api_listening")

        if mode == "crash-after-api":
            os._exit(9)

        if mode == "fail-readiness":
            reporter.send("readiness_failed", reason="forced by fake child")
            while not stop.wait(0.1):
                pass
            return 0

        ready_delay = max(0.0, float(os.environ.get("FAKE_CHILD_READY_DELAY", "0.01")))
        if ready_delay and stop.wait(ready_delay):
            return 0

        reporter.send("db_ready", backend="fake")
        stage("db_ready")
        reporter.send("cogs_loaded", loaded=1, failed=0)
        stage("cogs_loaded")
        reporter.send("gateway_ready", shards=1)
        stage("gateway_ready")
        reporter.send("ready", critical_checks=1)
        stage("ready")

        if mode == "hang-after-ready":
            # Keep serving HTTP, but stop sending heartbeats.  The supervisor's
            # heartbeat watchdog must replace this child.
            pass
        else:
            interval = max(0.02, float(os.environ.get("FAKE_CHILD_HEARTBEAT", "0.1")))

            def heartbeat_loop() -> None:
                while not stop.wait(interval):
                    reporter.heartbeat()

            threading.Thread(target=heartbeat_loop, name="fake-heartbeat", daemon=True).start()

        if os.environ.get("FAKE_CHILD_LOG_FLOOD"):
            def flood() -> None:
                line = "flood " + ("x" * 8192)
                while not stop.wait(0.001):
                    print(line, flush=True)

            threading.Thread(target=flood, name="fake-flood", daemon=True).start()

        if mode == "leak-child":
            grandchild = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            reporter.send("leaked_grandchild", pid=grandchild.pid)

        exit_after = float(os.environ.get("FAKE_CHILD_EXIT_AFTER", "0") or 0)
        if exit_after > 0:
            def exit_later() -> None:
                time.sleep(exit_after)
                os._exit(1)

            threading.Thread(target=exit_later, name="fake-exit", daemon=True).start()

        while not stop.wait(0.1):
            pass
        reporter.send("draining")
        if server is not None:
            server.shutdown()
            server.server_close()
        if server_thread is not None:
            server_thread.join(timeout=2.0)
        reporter.send("stopped")
        return 0
    finally:
        if server is not None:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
        reporter.close()


if __name__ == "__main__":
    raise SystemExit(main())
