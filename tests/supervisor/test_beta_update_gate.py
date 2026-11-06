"""Part 2 gate, run without a second host.

A production-like instance needs an origin to pull from. Instead of a separate
machine, this test copies the tree into ``tmp_path`` and runs the **real**
supervisor, a **real** supervised child serving the production Flask app, and
the **real** updater against a loopback HTTP server that speaks beta's update
feed contract (``/api/updates/manifest.json`` and ``/api/updates/file``,
``X-Update-Token`` checked, 404 otherwise).

That covers the gate's two outstanding scenarios end to end:

* a cold bot-area update is discovered over the feed, staged, import-probed,
  and applied through one supervised restart, after which the new child boots
  with the marker the update wrote;
* a bot core that cannot import is rejected by the probe and rolled back while
  the old child keeps serving, leaving a tree whose next boot still imports.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from webapp import updates  # noqa: E402

GATE_CHILD = "tests/supervisor/update_gate_child.py"
MARKER = "beta-bot-core-marker"
BROKEN_IMPORT = "import update_gate_missing_module_xyz  # deliberate broken update"


# ──────────────────────────────────────────────────────────────────────────────
# The local stand-in for beta
# ──────────────────────────────────────────────────────────────────────────────
class BetaFeed:
    """A loopback server that publishes this checkout's bot area, beta-style."""

    def __init__(self, stage: Path, overrides: dict[str, bytes], token: str) -> None:
        self.stage = stage
        self.overrides = dict(overrides)
        self.token = token
        self.pulls: list[str] = []
        self.document = self._manifest()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.port = int(self.server.server_address[1])
        self.thread = threading.Thread(
            target=self.server.serve_forever, name="beta-feed", daemon=True
        )
        self.thread.start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def _manifest(self) -> dict:
        files: dict[str, dict] = {}
        for relative in updates._files("bot", root=self.stage):  # noqa: SLF001 - feeds the real contract
            body = self.overrides.get(relative)
            if body is None:
                body = (self.stage / relative).read_bytes()
            files[relative] = {"sha": hashlib.sha1(body).hexdigest(), "size": len(body)}
        return {"generated_at": int(time.time()), "areas": {"bot": {"files": files}}}

    def publish(self, relative: str, body: bytes) -> None:
        """Change beta's copy of one file and re-publish its manifest."""
        self.overrides[relative] = body
        self.document = self._manifest()

    def body(self, relative: str) -> bytes | None:
        published = self.document["areas"]["bot"]["files"]
        if relative not in published:
            return None
        if relative in self.overrides:
            return self.overrides[relative]
        return (self.stage / relative).read_bytes()

    def _handler(self):
        feed = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args) -> None:  # keep pytest output readable
                pass

            def _not_found(self) -> None:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _json(self, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:
                parts = urlsplit(self.path)
                feed.pulls.append(parts.path)
                if self.headers.get("X-Update-Token") != feed.token:
                    self._not_found()
                    return
                if parts.path == "/api/updates/manifest.json":
                    self._json(feed.document)
                    return
                if parts.path == "/api/updates/file":
                    relative = (parse_qs(parts.query).get("path") or [""])[0]
                    body = feed.body(relative)
                    if body is None:
                        self._not_found()
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                self._not_found()

        return Handler

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


# ──────────────────────────────────────────────────────────────────────────────
# The staged instance
# ──────────────────────────────────────────────────────────────────────────────
def _stage_tree(destination: Path) -> Path:
    def ignore(directory, names):
        skipped = set()
        for name in names:
            if (
                name in {"__pycache__", "dist", "node_modules"}
                or name.startswith(".")
                or name.endswith(".pyc")
            ):
                skipped.add(name)
        return skipped

    shutil.copytree(ROOT / "src", destination / "src", ignore=ignore)
    shutil.copytree(
        ROOT / "tests" / "supervisor",
        destination / "tests" / "supervisor",
        ignore=ignore,
    )
    (destination / "data").mkdir()
    return destination


class GateSupervisor:
    def __init__(
        self, stage: Path, gate_dir: Path, feed: BetaFeed, token: str
    ) -> None:
        self.stage = stage
        self.run_dir = stage / "run"
        self.run_dir.mkdir()
        self.status_path = self.run_dir / "supervisor.json"
        self.control_path = self.run_dir / "supervisor.sock"
        self.log_path = self.run_dir / "supervisor.log"
        self.port: int | None = None
        env = os.environ.copy()
        env.update(
            {
                "BETA_INSTANCE_URL": feed.url,
                "BETA_UPDATE_TOKEN": token,
                "NIKO_UPDATE_GATE_DIR": str(gate_dir),
                "NIKO_SUPERVISED_RESTART_DELAY": "1.0",
            }
        )
        command = [
            sys.executable,
            str(stage / "src" / "supervisor.py"),
            "--port",
            "0",
            "--child",
            str(stage / GATE_CHILD),
            # The gate drives one stage child; split mode has its own suite.
            "--no-split-web",
            "--status-file",
            str(self.status_path),
            "--control-socket",
            str(self.control_path),
            "--lock-file",
            str(self.run_dir / "supervisor.lock"),
            "--startup-timeout",
            "60",
            "--heartbeat-timeout",
            "20",
            "--shutdown-timeout",
            "10",
            "--log-level",
            "WARNING",
        ]
        self.log = self.log_path.open("wb")
        self.process = subprocess.Popen(
            command,
            cwd=str(stage),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=self.log,
            stderr=subprocess.STDOUT,
        )

    # ── reading it ────────────────────────────────────────────────────────────
    def status(self) -> dict:
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def url(self, path: str) -> str:
        if self.port is None:
            raise AssertionError("supervisor public port is not known yet")
        return f"http://127.0.0.1:{self.port}{path}"

    def request(self, path: str, **kwargs):
        kwargs.setdefault("timeout", 10)
        return requests.get(self.url(path), **kwargs)

    def log_tail(self, limit: int = 40) -> str:
        try:
            lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return ""
        return "\n".join(lines[-limit:])

    def wait(self, predicate, timeout: float = 60.0) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise AssertionError(
                    "supervisor exited with code "
                    f"{self.process.returncode}\n{self.log_tail()}"
                )
            try:
                payload = self.status()
            except (FileNotFoundError, json.JSONDecodeError):
                time.sleep(0.05)
                continue
            self.port = int(payload["public_port"])
            if predicate(payload):
                return payload
            time.sleep(0.05)
        raise AssertionError(f"condition not met within {timeout}s\n{self.log_tail()}")

    def wait_ready(self, timeout: float = 90.0) -> dict:
        payload = self.wait(
            lambda item: bool(item.get("ready"))
            and item.get("state") in {"active", "degraded"},
            timeout=timeout,
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if self.request("/ready").status_code == 200:
                    return payload
            except requests.RequestException:
                pass
            time.sleep(0.05)
        raise AssertionError(f"/ready never became 200\n{self.log_tail()}")

    def wait_new_child(self, old_pid: int, timeout: float = 90.0) -> dict:
        return self.wait(
            lambda item: bool(item.get("child")) and item["child"].get("pid") != old_pid,
            timeout=timeout,
        )

    def control(self, command: str, timeout: float = 10.0, **fields) -> dict:
        payload = {"command": command, **fields}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            client.connect(str(self.control_path))
            client.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            data = b""
            while b"\n" not in data:
                chunk = client.recv(65536)
                if not chunk:
                    break
                data += chunk
        return json.loads(data.split(b"\n", 1)[0].decode("utf-8"))

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.log.close()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _run_update(gate_dir: Path, identifier: str, areas: list[str], timeout: float = 180.0) -> dict:
    """Ask the supervised child to run the real updater, then read its result."""
    (gate_dir / "command.json").write_text(
        json.dumps({"id": identifier, "areas": areas}), encoding="utf-8"
    )
    result_path = gate_dir / f"result-{identifier}.json"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            return json.loads(result_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(0.1)
    raise AssertionError(f"the child never wrote {result_path}")


def _boot_for(gate_dir: Path, pid: int) -> dict:
    path = gate_dir / f"boot-{pid}.json"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            time.sleep(0.05)
    raise AssertionError(f"child {pid} left no boot record")


def _probe(stage: Path) -> subprocess.CompletedProcess:
    """The updater's own import gate, run against the staged tree."""
    environment = {
        name: value
        for name, value in os.environ.items()
        if not name.startswith(updates.PROCESS_ENV_MARKERS)
    }
    environment[updates.PROBE_ENV] = "1"
    return subprocess.run(
        [sys.executable, str(stage / "src" / "bot.py")],
        cwd=str(stage),
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )


@pytest.fixture
def gate(tmp_path: Path):
    """A staged tree, a beta stand-in, and a real supervisor over a real child."""
    stage = _stage_tree(tmp_path / "stage")
    gate_dir = tmp_path / "gate"
    gate_dir.mkdir()
    token = secrets.token_hex(8)
    feed = BetaFeed(stage, {}, token)
    supervisor = GateSupervisor(stage, gate_dir, feed, token)
    try:
        supervisor.wait_ready(timeout=120)
        yield stage, gate_dir, feed, supervisor
    finally:
        supervisor.stop()
        feed.close()


# ──────────────────────────────────────────────────────────────────────────────
# Gate scenario 1 — a real cold bot-area update through the supervisor
# ──────────────────────────────────────────────────────────────────────────────
def test_bot_area_update_is_pulled_staged_and_supervised(gate):
    stage, gate_dir, feed, supervisor = gate
    first = supervisor.status()["child"]
    assert first["ready"] is True
    baseline = _boot_for(gate_dir, first["pid"])
    assert baseline["api_port"] == first["api_port"]
    assert baseline["marker"] == ""

    # Beta's copy of one bot-core file carries a marker only the new code has.
    original = (stage / "src" / "api_server.py").read_bytes()
    feed.publish(
        "src/api_server.py", original + f'\n\nUPDATE_GATE_MARKER = "{MARKER}"\n'.encode("utf-8")
    )

    # A caller without the shared secret must not read the feed.
    assert requests.get(feed.url + "/api/updates/manifest.json", timeout=5).status_code == 404

    response = _run_update(gate_dir, "cold", ["bot"])
    assert response["ok"] is True, response
    outcome = response["result"]["areas"]["bot"]
    assert outcome["ok"] is True, outcome
    assert outcome["strategy"] == "requesting a supervised restart"
    assert outcome["changed"] == 1, outcome
    assert "/api/updates/manifest.json" in feed.pulls
    assert "/api/updates/file" in feed.pulls

    # The run is persisted before the child is asked to restart.
    last = json.loads((stage / "data" / "updates" / "last.json").read_text(encoding="utf-8"))
    assert last["supervised_restart"] is True
    assert last["areas"]["bot"]["ok"] is True
    assert last["handoff"] is False

    # The replaced file was backed up and the new one is what is on disk.
    backup = stage / "data" / "updates" / "backups" / last["id"] / "src" / "api_server.py"
    assert backup.read_bytes() == original
    assert MARKER in (stage / "src" / "api_server.py").read_text(encoding="utf-8")

    # One restart, and the new child booted the files the update wrote.
    second = supervisor.wait_new_child(first["pid"], timeout=120)
    supervisor.wait_ready(timeout=120)
    final = supervisor.status()
    assert final["child_starts"] == 2
    assert final["child"]["pid"] == second["child"]["pid"]
    assert _boot_for(gate_dir, final["child"]["pid"])["marker"] == MARKER
    health = supervisor.request("/api/health")
    assert health.status_code == 200
    assert health.json()["ok"] is True


# ──────────────────────────────────────────────────────────────────────────────
# Gate scenario 2 — a bot core that cannot import is rolled back
# ──────────────────────────────────────────────────────────────────────────────
def test_unimportable_bot_core_is_rolled_back_and_the_old_child_keeps_serving(gate):
    stage, gate_dir, feed, supervisor = gate
    before = supervisor.status()
    first = before["child"]
    original_bot = (stage / "src" / "bot.py").read_bytes()
    original_api = (stage / "src" / "api_server.py").read_bytes()

    lines = original_bot.splitlines(keepends=True)
    lines.insert(1, (BROKEN_IMPORT + "\n").encode("utf-8"))
    feed.publish("src/bot.py", b"".join(lines))

    response = _run_update(gate_dir, "broken", ["bot"])
    assert response["ok"] is False, response
    outcome = response["result"]["areas"]["bot"]
    assert outcome["rolled_back"] is True, outcome
    assert "cannot import" in outcome["error"], outcome

    # The staged file was restored byte for byte, and nothing else moved.
    assert (stage / "src" / "bot.py").read_bytes() == original_bot
    assert (stage / "src" / "api_server.py").read_bytes() == original_api
    assert "/api/updates/file" in feed.pulls

    # No restart was requested: the same child still serves.
    after = supervisor.status()
    assert after["child"]["pid"] == first["pid"]
    assert after["child_starts"] == before["child_starts"]
    assert supervisor.request("/ready").status_code == 200
    assert supervisor.request("/api/health").status_code == 200

    # And the tree left behind is one the next boot can import.
    result = _probe(stage)
    assert result.returncode == 0, result.stderr

    # A restart on the rolled-back tree still comes up ready.
    accepted = supervisor.control("restart", delay=0.1, reason="post-rollback boot")
    assert accepted["ok"] is True
    supervisor.wait_new_child(first["pid"], timeout=120)
    supervisor.wait_ready(timeout=120)
    assert supervisor.request("/api/health").status_code == 200
