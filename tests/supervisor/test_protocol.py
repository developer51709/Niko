from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from supervisor_protocol import ChildReporter, PROTOCOL_VERSION  # noqa: E402


def test_reporter_writes_one_json_object_per_line():
    parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    reporter = ChildReporter(child.fileno())
    try:
        assert reporter.send("process_started", mode="unit") is True
        assert reporter.heartbeat() is True

        stream = parent.makefile("r", encoding="utf-8")
        first = json.loads(stream.readline())
        second = json.loads(stream.readline())
        assert first["protocol"] == PROTOCOL_VERSION
        assert first["event"] == "process_started"
        assert first["mode"] == "unit"
        assert first["pid"] == os.getpid()
        assert second["event"] == "heartbeat"
    finally:
        reporter.close()
        parent.close()


def test_reporter_requires_the_supervisor_control_fd():
    from supervisor_protocol import CONTROL_FD_ENV

    old = os.environ.pop(CONTROL_FD_ENV, None)
    try:
        with pytest.raises(RuntimeError, match=CONTROL_FD_ENV):
            ChildReporter.from_environment()
    finally:
        if old is not None:
            os.environ[CONTROL_FD_ENV] = old
