from __future__ import annotations

import json
import socket
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import supervisor_control  # noqa: E402


def test_request_restart_round_trips_over_a_unix_socket(monkeypatch, tmp_path):
    path = tmp_path / "supervisor.sock"
    received = {}

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(path))
    server.listen(1)

    def serve():
        connection, _ = server.accept()
        with connection:
            data = b""
            while b"\n" not in data:
                data += connection.recv(8192)
            received.update(json.loads(data.split(b"\n", 1)[0].decode("utf-8")))
            connection.sendall(b'{"ok":true,"accepted":true}\n')

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    monkeypatch.setenv(supervisor_control.CONTROL_SOCKET_ENV, str(path))
    try:
        response = supervisor_control.request_restart(reason="test", delay=1.5)
    finally:
        server.close()
        thread.join(timeout=2)

    assert response == {"ok": True, "accepted": True}
    assert received == {"command": "restart", "reason": "test", "delay": 1.5}


def test_a_missing_control_socket_is_an_explicit_error(monkeypatch):
    monkeypatch.delenv(supervisor_control.CONTROL_SOCKET_ENV, raising=False)

    with pytest.raises(RuntimeError) as error:
        supervisor_control.request_restart()

    assert "NIKO_SUPERVISOR_CONTROL_SOCKET" in str(error.value)
