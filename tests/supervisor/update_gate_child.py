"""Part 2 gate harness: a supervised child that can run a real bot-area update.

It serves the production Flask API on a loopback port and reports readiness
exactly like the real child. A JSON command in ``NIKO_UPDATE_GATE_DIR`` runs
``webapp.updates.apply`` inside this process — the same place the dashboard's
owner route runs it — and writes the result back, so the gate can drive the
real updater through a real supervisor without a second host.

After a bot-area update the updater asks the supervisor to restart this child.
The next boot imports the files the update wrote, and its boot record carries
the ``UPDATE_GATE_MARKER`` those files define, which is how the test proves the
new core is the one now serving.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import api_server  # noqa: E402
from supervisor_protocol import ChildReporter, install_parent_death_signal  # noqa: E402

COMMAND_POLL = 0.1


def _gate_dir() -> Path | None:
    raw = (os.environ.get("NIKO_UPDATE_GATE_DIR") or "").strip()
    return Path(raw) if raw else None


def _write_json(path: Path, payload: dict) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, default=str, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _boot_record(directory: Path, port: int) -> None:
    _write_json(
        directory / f"boot-{os.getpid()}.json",
        {
            "pid": os.getpid(),
            "api_port": port,
            "marker": getattr(api_server, "UPDATE_GATE_MARKER", ""),
            "at": time.time(),
        },
    )


async def _watch_commands(directory: Path, draining: asyncio.Event) -> None:
    """Run one ``updates.apply`` per distinct command id, writing the result."""
    handled: set[str] = set()
    while not draining.is_set():
        path = directory / "command.json"
        try:
            command = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            await asyncio.sleep(COMMAND_POLL)
            continue
        identifier = str(command.get("id") or "")
        if not identifier or identifier in handled:
            await asyncio.sleep(COMMAND_POLL)
            continue
        handled.add(identifier)
        areas = command.get("areas") or ["bot"]
        try:
            # Imported here so the module is read from the files the update
            # writes, exactly as the owner route reads it.
            from webapp import updates

            result = await asyncio.to_thread(updates.apply, areas)
            payload = {"id": identifier, "ok": bool(result.get("ok")), "result": result}
        except BaseException as exc:  # noqa: BLE001 - reported to the test
            payload = {"id": identifier, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
        _write_json(directory / f"result-{identifier}.json", payload)


async def _main() -> None:
    reporter = ChildReporter.from_environment()
    install_parent_death_signal()
    reporter.send("process_started")

    api_server.start_api_server(None, host="127.0.0.1", port=0)
    port = api_server.listening_port()
    reporter.send("api_listening", host="127.0.0.1", port=port)
    reporter.send("db_ready", backend="harness")
    reporter.send("cogs_loaded", total=0, failed=0)
    reporter.send("gateway_ready", shard_count=1, ready_shards=1)
    reporter.send("ready", reason="update gate harness ready")

    gate = _gate_dir()
    if gate is not None:
        _boot_record(gate, port)

    draining = asyncio.Event()
    loop = asyncio.get_running_loop()

    def stop() -> None:
        if not draining.is_set():
            reporter.send("draining", reason="SIGTERM")
            draining.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop)
        except NotImplementedError:
            pass

    async def heartbeat() -> None:
        while not draining.is_set():
            await asyncio.sleep(0.5)
            if not reporter.heartbeat():
                return

    heartbeat_task = asyncio.create_task(heartbeat(), name="gate-heartbeat")
    watcher_task = (
        asyncio.create_task(_watch_commands(gate, draining), name="gate-commands")
        if gate is not None
        else None
    )
    try:
        await draining.wait()
    finally:
        # Let an in-flight apply finish writing its result before the process
        # exits; a supervised restart is requested mid-run and arrives shortly
        # after the response, so this is normally immediate.
        if watcher_task is not None:
            try:
                await asyncio.wait_for(watcher_task, timeout=20)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                watcher_task.cancel()
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        api_server.stop_api_server()
        reporter.send("stopped")
        reporter.close()


if __name__ == "__main__":
    asyncio.run(_main())
