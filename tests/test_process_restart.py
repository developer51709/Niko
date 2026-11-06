"""A bot-core update must not close the dashboard's port or exit the process.

On a supervised host (Render, Railway, a systemd unit) the process exiting is the
failure this pins: the supervisor reads it as a crash, recreates the instance —
discarding the files the update just wrote — and the site is down for the whole
boot. So a bot-core update replaces the process image in place with ``execve``,
handing over the listening socket, and the PID never changes.
"""

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import api_server  # noqa: E402
from utils import handoff  # noqa: E402
from webapp import updates  # noqa: E402


@pytest.fixture(autouse=True)
def _restore_handoff():
    """Re-importing ``utils.handoff`` replaces both the module and the package
    attribute; put the pair back so each test sees the same module."""
    import utils

    module = utils.handoff
    try:
        yield
    finally:
        sys.modules["utils.handoff"] = module
        utils.handoff = module


# ── The restart itself ────────────────────────────────────────────────────────
def test_a_bot_update_replaces_the_image_instead_of_exiting():
    source = (ROOT / "src/utils/handoff.py").read_text(encoding="utf-8")

    # Exiting, or leaving a child behind in this process's place, is exactly what
    # makes a hosted deployment restart and drop the update.
    assert "os._exit" not in source
    assert "subprocess" not in source
    assert not hasattr(handoff, "complete")
    assert not hasattr(handoff, "is_candidate")


def test_restart_keeps_the_listening_socket_and_its_pid(monkeypatch):
    seen = {}
    monkeypatch.setattr(api_server, "listening_socket_fd", lambda: 9)
    monkeypatch.setattr(api_server, "listening_port", lambda: 10000)
    monkeypatch.setattr(handoff, "_remember", lambda record: seen.setdefault("records", []).append(record))
    monkeypatch.setattr(handoff.os, "set_inheritable", lambda fd, flag: seen.update({"fd": fd, "inheritable": flag}))

    def execve(path, argv, environment):
        seen["exec"] = {"path": path, "argv": argv, "env": environment}
        raise SystemExit(0)

    monkeypatch.setattr(handoff.os, "execve", execve)

    with pytest.raises(SystemExit):
        handoff.restart()

    # Inheritable is the whole trick: an ordinary descriptor is closed by exec and
    # the port would come up only after a rebind.
    assert seen["fd"] == 9
    assert seen["inheritable"] is True
    assert seen["exec"]["env"][handoff.INHERITED_FD_ENV] == "9"
    assert seen["exec"]["argv"][-1].endswith("bot.py")
    # The page reads this file to show what the restart did.
    assert [record["state"] for record in seen["records"]] == ["restarting"]


def test_a_process_without_an_inherited_socket_binds_the_port_normally(monkeypatch):
    monkeypatch.delenv(handoff.INHERITED_FD_ENV, raising=False)

    assert handoff.inherited_fd() is None
    assert handoff.adopt(None) is False


def test_a_socket_that_cannot_be_adopted_still_leaves_a_listening_site(monkeypatch):
    monkeypatch.setenv(handoff.INHERITED_FD_ENV, "9")
    monkeypatch.setattr(handoff, "_remember", lambda record: None)

    def refuse(bot=None, fd=None, port=None):
        raise OSError("bad descriptor")

    monkeypatch.setattr(api_server, "start_api_server", refuse)

    # False tells src/bot.py to bind the port itself.
    assert handoff.adopt(None) is False


# ── The preflight that keeps a broken bot core from being restarted onto ──────
def test_the_probe_never_inherits_the_restart_socket(monkeypatch):
    captured = {}

    def run(*args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setenv(handoff.INHERITED_FD_ENV, "9")
    monkeypatch.setattr(updates.subprocess, "run", run)

    updates._probe_bot()

    environment = captured["env"]
    assert handoff.INHERITED_FD_ENV not in environment
    assert environment["NIKO_IMPORT_PROBE"] == "1"
    assert captured["cwd"] == str(ROOT)


def test_the_probe_does_not_read_the_loaded_handoff_module(monkeypatch):
    # A process that booted before the in-place restart still holds the
    # predecessor's utils.handoff: it has no INHERITED_FD_ENV, and naming the
    # variable through it failed the whole bot-core update with AttributeError.
    monkeypatch.setitem(sys.modules, "utils.handoff", SimpleNamespace(schedule=lambda bot: None))
    monkeypatch.setenv("NIKO_RESTART_FD", "9")
    monkeypatch.setenv("NIKO_HANDOFF_ROLE", "successor")
    monkeypatch.setenv("NIKO_SUPERVISED", "1")
    monkeypatch.setenv("NIKO_SUPERVISOR_CONTROL_FD", "10")
    monkeypatch.setenv("NIKO_SUPERVISOR_CONTROL_SOCKET", "/tmp/supervisor.sock")
    monkeypatch.setenv("KEEP_ME", "1")
    captured = {}

    def run(*args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(updates.subprocess, "run", run)

    updates._probe_bot()

    environment = captured["env"]
    assert "NIKO_RESTART_FD" not in environment
    assert "NIKO_HANDOFF_ROLE" not in environment
    assert "NIKO_SUPERVISED" not in environment
    assert "NIKO_SUPERVISOR_CONTROL_FD" not in environment
    assert "NIKO_SUPERVISOR_CONTROL_SOCKET" not in environment
    assert environment["NIKO_IMPORT_PROBE"] == "1"
    assert environment["KEEP_ME"] == "1"


def test_the_restart_runs_the_handoff_from_disk_not_the_stale_one(monkeypatch):
    monkeypatch.setitem(sys.modules, "utils.handoff", SimpleNamespace(schedule=lambda bot: None))

    module = updates._inplace_handoff()

    assert module.INHERITED_FD_ENV == "NIKO_RESTART_FD"
    assert sys.modules["utils.handoff"] is module


def test_a_process_with_only_the_successor_handoff_is_told_what_to_do(monkeypatch, tmp_path):
    package = tmp_path / "old_handoff_pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "handoff.py").write_text("def schedule(bot, delay=2.0):\n    pass\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(updates, "HANDOFF_MODULE", "old_handoff_pkg.handoff")
    previous = SimpleNamespace(name="previous")
    monkeypatch.setitem(sys.modules, "old_handoff_pkg.handoff", previous)

    with pytest.raises(RuntimeError) as error:
        updates._inplace_handoff()

    assert "apply the Utilities area first" in str(error.value)
    # Nothing is left holding the copy that was just refused.
    assert sys.modules["old_handoff_pkg.handoff"] is previous
    assert sys.modules["old_handoff_pkg"].handoff is previous


def test_serving_falls_back_to_the_socket_on_an_older_api_server():
    def refuse():
        raise RuntimeError("The dashboard API is not serving.")

    assert updates._serving(SimpleNamespace(serving=lambda: True)) is True
    assert updates._serving(SimpleNamespace(serving=lambda: False)) is False

    # The module a process booted before serving() existed still knows whether
    # it holds the listener; the duplicate it hands out must not leak.
    fd = os.open(os.devnull, os.O_RDONLY)
    try:
        assert updates._serving(SimpleNamespace(listening_socket_fd=lambda: fd)) is True
        with pytest.raises(OSError):
            os.fstat(fd)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass

    assert updates._serving(SimpleNamespace(listening_socket_fd=refuse)) is False


def test_a_bot_area_update_schedules_the_in_place_restart(monkeypatch):
    change = {"path": "src/bot.py", "status": "modified", "bytes": 10, "sha": "sha"}
    monkeypatch.setattr(updates, "plan", lambda areas=None: {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"bot": {"label": "Bot core", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    })
    monkeypatch.setattr(updates, "_stage_area", lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"})
    monkeypatch.setattr(updates, "_record", lambda run: None)
    monkeypatch.setattr(updates, "_probe_bot", lambda: None)
    monkeypatch.setattr(updates, "_inplace_handoff", lambda: handoff)
    monkeypatch.setitem(sys.modules, "api_server", SimpleNamespace(serving=lambda: True))
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(args))

    result = updates.apply(["bot"], object())

    assert result["ok"] is True
    assert result["areas"]["bot"]["strategy"] == "restarting this process in place"
    assert scheduled == [()]


def test_a_bot_core_that_cannot_import_fails_the_area(monkeypatch):
    monkeypatch.setattr(
        updates.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1, stdout="", stderr="ImportError: No module named 'config.version'"
        ),
    )

    with pytest.raises(RuntimeError) as error:
        updates._probe_bot()

    assert "config.version" in str(error.value)


def test_a_bot_area_update_is_refused_when_nothing_is_serving(monkeypatch):
    change = {"path": "src/bot.py", "status": "modified", "bytes": 10, "sha": "sha"}
    monkeypatch.setattr(updates, "plan", lambda areas=None: {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"bot": {"label": "Bot core", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    })
    monkeypatch.setattr(updates, "_stage_area", lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"})
    monkeypatch.setattr(updates, "_record", lambda run: None)
    monkeypatch.setattr(updates, "_restore_area", lambda name, files, run_id: None)
    monkeypatch.setattr(updates, "_probe_bot", lambda: None)
    monkeypatch.setattr(updates, "_rebuild_after_rollback", lambda name, bot: None)
    monkeypatch.setattr(api_server, "serving", lambda: False)
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(True))

    result = updates.apply(["bot"], None)

    # Restarting onto a process with no socket would end with a site that cannot
    # come back, so the area fails and the running process is left alone.
    assert result["ok"] is False
    assert "not serving" in result["areas"]["bot"]["error"]
    assert scheduled == []


def test_a_python_file_that_cannot_compile_is_refused_before_it_is_written():
    with pytest.raises(ValueError):
        updates._python_check("src/bot.py", b"async def broken(:\n")

    # Valid source, and anything that is not Python, passes through untouched.
    updates._python_check("src/bot.py", b"VALUE = 1\n")
    updates._python_check("src/website/dist/index.html", b"<html></html>")
