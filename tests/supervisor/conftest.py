from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import psutil
import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR = ROOT / "src" / "supervisor.py"
FAKE_CHILD = ROOT / "tests" / "supervisor" / "fake_child.py"


class SupervisorHandle:
    def __init__(
        self,
        process: subprocess.Popen,
        run_dir: Path,
        status_path: Path,
        control_path: Path,
        lock_path: Path,
        args: list[str],
    ) -> None:
        self.process = process
        self.run_dir = run_dir
        self.status_path = status_path
        self.control_path = control_path
        self.lock_path = lock_path
        self.args = args
        self.port: int | None = None

    @property
    def pid(self) -> int:
        return int(self.process.pid)

    def url(self, path: str) -> str:
        if self.port is None:
            raise AssertionError("supervisor public port is not known yet")
        return f"http://127.0.0.1:{self.port}{path}"

    def request(self, path: str, **kwargs):
        kwargs.setdefault("timeout", 5)
        return requests.request(kwargs.pop("method", "GET"), self.url(path), **kwargs)

    def status(self) -> dict[str, Any]:
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def wait_status(
        self,
        predicate: Callable[[dict[str, Any]], bool] | None = None,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise AssertionError(
                    f"supervisor exited early with code {self.process.returncode}"
                )
            try:
                payload = self.status()
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                last_error = exc
            else:
                if self.port is None:
                    self.port = int(payload["public_port"])
                if predicate is None or predicate(payload):
                    return payload
            time.sleep(0.025)
        raise AssertionError(f"status condition not met within {timeout}s: {last_error}")

    def wait_ready(self, timeout: float = 10.0) -> dict[str, Any]:
        def ready(payload: dict[str, Any]) -> bool:
            return payload.get("state") in {"active", "degraded"} and bool(payload.get("ready"))

        payload = self.wait_status(ready, timeout=timeout)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                response = self.request("/ready")
            except requests.RequestException:
                time.sleep(0.025)
                continue
            if response.status_code == 200:
                return payload
            time.sleep(0.025)
        raise AssertionError("public /ready did not become ready")

    def control(self, command: str, timeout: float = 5.0, **fields: Any) -> dict[str, Any]:
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
        if not data:
            raise AssertionError(f"control socket returned no response for {command!r}")
        return json.loads(data.split(b"\n", 1)[0].decode("utf-8"))

    def wait_for_child(self, timeout: float = 10.0) -> dict[str, Any]:
        return self.wait_status(
            lambda payload: bool(payload.get("child")),
            timeout=timeout,
        )

    def wait_for_new_child(self, old_pid: int, timeout: float = 10.0) -> dict[str, Any]:
        return self.wait_status(
            lambda payload: bool(payload.get("child"))
            and payload["child"].get("pid") != old_pid,
            timeout=timeout,
        )

    def descendants(self) -> list[psutil.Process]:
        try:
            return psutil.Process(self.pid).children(recursive=True)
        except psutil.Error:
            return []

    def stop(self, timeout: float = 10.0) -> int | None:
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        return self.process.returncode

    def duplicate(self) -> subprocess.CompletedProcess:
        second_args = list(self.args)
        # The duplicate uses the same lock and control socket, but a different
        # status path so a partial startup cannot overwrite the live status.
        second_status = self.run_dir / "duplicate-status.json"
        index = second_args.index("--status-file")
        second_args[index + 1] = str(second_status)
        return subprocess.run(
            second_args,
            cwd=str(ROOT),
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )


@pytest.fixture
def supervisor(tmp_path: Path):
    handles: list[SupervisorHandle] = []

    def start(
        mode: str = "normal",
        *,
        startup_timeout: float = 5.0,
        heartbeat_timeout: float = 2.0,
        ready_grace: float = 0.0,
        shutdown_timeout: float = 0.5,
        backoff_initial: float = 0.01,
        backoff_max: float = 0.05,
        reset_after: float = 5.0,
        max_restarts: int = 0,
        env: dict[str, str] | None = None,
        args: list[str] | None = None,
    ) -> SupervisorHandle:
        run_dir = tmp_path / f"run-{uuid.uuid4().hex[:10]}"
        run_dir.mkdir()
        status_path = run_dir / "supervisor.json"
        control_path = run_dir / "supervisor.sock"
        lock_path = run_dir / "supervisor.lock"
        command = [
            sys.executable,
            str(SUPERVISOR),
            "--port",
            "0",
            "--child",
            str(FAKE_CHILD),
            # These harnesses describe the combined child; tests that exercise
            # split mode append their own --split-web, which wins.  The
            # database child is opt-in for the same reason: the fake children
            # have no pool, and a real one would need a real database.
            "--no-split-web",
            "--no-split-db",
            "--status-file",
            str(status_path),
            "--control-socket",
            str(control_path),
            "--lock-file",
            str(lock_path),
            "--startup-timeout",
            str(startup_timeout),
            "--heartbeat-timeout",
            str(heartbeat_timeout),
            "--ready-grace",
            str(ready_grace),
            "--shutdown-timeout",
            str(shutdown_timeout),
            "--restart-backoff-initial",
            str(backoff_initial),
            "--restart-backoff-max",
            str(backoff_max),
            "--restart-reset-after",
            str(reset_after),
            "--max-restarts",
            str(max_restarts),
            # Keep last-good rollback state inside this test's own run directory:
            # a real pending update in the checkout must never be restored by a
            # test supervisor.
            "--pending-update-file",
            str(run_dir / "pending-update.json"),
            "--update-root",
            str(run_dir),
            "--log-level",
            "WARNING",
            *(args or []),
        ]
        child_env = os.environ.copy()
        child_env["FAKE_CHILD_MODE"] = mode
        for key, value in (env or {}).items():
            child_env[str(key)] = str(value)
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            env=child_env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        handle = SupervisorHandle(process, run_dir, status_path, control_path, lock_path, command)
        handles.append(handle)
        try:
            handle.wait_status(lambda payload: bool(payload.get("public_port")), timeout=10)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    if handle.request("/health").status_code == 200:
                        break
                except requests.RequestException:
                    pass
                if process.poll() is not None:
                    raise AssertionError(
                        f"supervisor exited during startup with code {process.returncode}"
                    )
                time.sleep(0.025)
            else:
                raise AssertionError("supervisor /health did not become available")
        except Exception:
            handle.stop()
            raise
        return handle

    yield start

    for handle in handles:
        handle.stop()
