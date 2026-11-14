"""The startup data writers update without a bot-core restart.

``events.on_ready`` imports the writers through ``events.startup`` and calls them
on every READY. Re-importing the writers, refreshing that package's exports and
rebinding the ready handler therefore applies a writers change without restarting
the process or reloading a single cog.
"""

import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.runtime import handoff  # noqa: E402
from webapp import updates  # noqa: E402


def test_the_writers_are_their_own_area_and_apply_before_the_bot_core():
    assert updates.area_for_path("src/events/startup/writers.py") == "startup"
    assert updates.area_files("startup") == ["src/events/startup/writers.py"]
    assert "src/events/startup/writers.py" not in updates.area_files("bot")
    order = list(updates.AREA_ORDER)
    assert order.index("startup") < order.index("bot")


def test_reloading_the_writers_refreshes_the_package_and_ready_handler(monkeypatch):
    import events.on_ready as before
    import events.startup as package

    old_writer = package.write_bot_stats
    host = types.ModuleType("bot")
    host.handle_ready = before.handle_ready
    monkeypatch.setitem(sys.modules, "bot", host)

    result = updates.reload_startup_writers(None, run_writers=False)

    assert "events.startup.writers" in result["reloaded"]
    assert result["failed"] == []
    assert result["rebound"] == ["events.on_ready.handle_ready"]
    fresh = sys.modules["events.startup.writers"]
    assert package.write_bot_stats is fresh.write_bot_stats
    assert package.write_bot_stats is not old_writer
    assert host.handle_ready is sys.modules["events.on_ready"].handle_ready
    assert host.handle_ready is not before.handle_ready


def test_running_the_writers_keeps_the_process_uptime(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    stats = data / "bot_stats.json"
    stats.write_text(json.dumps({"uptime_since": "before", "version": "old"}), encoding="utf-8")

    def write_stats(_bot):
        stats.write_text(
            json.dumps({"uptime_since": "after-restart", "version": "new"}),
            encoding="utf-8",
        )

    module = types.SimpleNamespace(
        write_commands=lambda _bot: None,
        write_bot_stats=write_stats,
    )
    monkeypatch.setattr(updates, "ROOT", tmp_path)

    ran = updates._run_startup_writers(object(), module)

    assert ran == ["write_commands", "write_bot_stats"]
    payload = json.loads(stats.read_text(encoding="utf-8"))
    assert payload["uptime_since"] == "before"
    assert payload["version"] == "new"


def test_applying_only_the_startup_area_does_not_restart_the_process(monkeypatch):
    change = {
        "path": "src/events/startup/writers.py",
        "status": "modified",
        "bytes": 10,
        "sha": "sha",
    }
    monkeypatch.setattr(updates, "plan", lambda areas=None: {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"startup": {"label": "Startup writers", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    })
    monkeypatch.setattr(
        updates,
        "_stage_area",
        lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"},
    )
    monkeypatch.setattr(updates, "_record", lambda run: None)
    monkeypatch.setattr(
        updates,
        "reload_startup_writers",
        lambda bot, files: {
            "reloaded": ["events.startup.writers", "events.startup.banner"],
            "rebound": ["events.on_ready.handle_ready"],
            "failed": [],
        },
    )
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(True))

    result = updates.apply(["startup"], None)

    assert result["ok"] is True
    assert result["areas"]["startup"]["strategy"] == "re-imported the startup writers"
    assert result["areas"]["startup"]["rebound"] == ["events.on_ready.handle_ready"]
    assert scheduled == []
