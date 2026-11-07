"""The schema module updates against the live pool, and unknown areas are safe.

``src/events/startup/database.py`` is the one startup file whose work can be
repeated: ``init_database`` creates tables with ``IF NOT EXISTS``, adds only
missing columns and re-runs the idempotent migrations. Importing the new file and
calling it applies the change without a restart.

The plan half of this file pins the bug that made the events area fail: a beta
build that does not publish an area used to read as "every file here was
deleted", so the update removed ``src/events/on_*.py`` and then failed to import
them (``ModuleNotFoundError: No module named 'events.on_message'``).
"""

import asyncio
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils import handoff  # noqa: E402
from webapp import runtime, updates  # noqa: E402


@pytest.fixture
def bot_loop():
    """A running bot loop with the API pointed at its bot, as in production."""
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    bot = SimpleNamespace(loop=loop)
    previous = runtime._discord_bot
    runtime.configure_bot(bot)
    try:
        yield bot, loop
    finally:
        runtime._discord_bot = previous
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5)


# ── Plan: an area beta does not publish ──────────────────────────────────────
def test_an_unpublished_area_is_not_offered_as_deletions(monkeypatch):
    # Beta is running a build from before the split, so its manifest has no
    # "events" or "database" area at all.
    monkeypatch.setattr(
        updates,
        "beta_manifest",
        lambda force=False: {"generated_at": 0, "areas": {"bot": {"files": {}}}},
    )

    plan = updates.plan(["events", "database"])

    assert plan["ok"] is True
    for name in ("events", "database"):
        assert plan["areas"][name]["available"] is False
        assert plan["areas"][name]["changed"] == 0
        assert plan["areas"][name]["files"] == []
    assert plan["total_changed"] == 0


def test_a_published_area_with_no_files_still_reports_removals(monkeypatch):
    # The opposite case: beta does publish the area and has nothing in it, so the
    # local files really were deleted there.
    monkeypatch.setattr(
        updates,
        "beta_manifest",
        lambda force=False: {"generated_at": 0, "areas": {"events": {"files": {}}}},
    )

    plan = updates.plan(["events"])

    assert plan["areas"]["events"]["available"] is True
    assert plan["areas"]["events"]["changed"] == 3
    assert {change["status"] for change in plan["areas"]["events"]["files"]} == {"removed"}


# ── The schema module ────────────────────────────────────────────────────────
def test_the_schema_area_owns_only_the_database_module():
    assert updates.area_for_path("src/events/startup/database.py") == "database"
    assert updates.area_files("database") == ["src/events/startup/database.py"]
    order = list(updates.AREA_ORDER)
    assert order.index("utils") < order.index("database") < order.index("webapp")


def test_the_bot_area_ships_the_database_child_script():
    """The child is the server half of the database API, so it travels with it.

    ``src/database/remote.py`` is the client the bot uses and ``src/db_child.py``
    is what serves it.  Shipping one without the other would leave the deployed
    child answering a contract its own bot no longer speaks.
    """
    assert updates.area_for_path("src/db_child.py") == "bot"
    assert "src/db_child.py" in updates.area_files("bot")


def test_the_schema_cannot_be_applied_without_a_running_bot():
    with pytest.raises(RuntimeError):
        updates.reload_database(None)


def test_a_schema_module_that_cannot_import_leaves_the_old_one_running(monkeypatch):
    import events.startup.database as before

    def refuse(name, *args, **kwargs):
        raise ImportError("broken")

    monkeypatch.setattr(updates.importlib, "import_module", refuse)

    with pytest.raises(ImportError):
        updates.reload_database(object())

    assert sys.modules[updates.SCHEMA_MODULE] is before


def test_a_beta_that_deleted_the_schema_file_is_refused_plainly(monkeypatch, tmp_path):
    monkeypatch.setattr(updates, "SCHEMA_MODULE", "schema_gone")
    monkeypatch.setattr(updates, "ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="was removed on beta"):
        updates.reload_database(object())


def test_re_importing_the_schema_refreshes_the_package_reexport():
    package = sys.modules.get("events.startup")
    if package is None:
        import events.startup  # noqa: F401

        package = sys.modules["events.startup"]
    package.init_database = lambda bot: None

    module, init = updates._import_schema_module()

    assert module.init_database is init
    assert package.init_database is init


def test_a_live_apply_reimports_and_reruns_the_new_schema(monkeypatch, tmp_path, bot_loop):
    bot, loop = bot_loop
    package = tmp_path / "schema_pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    marker = tmp_path / "runs.txt"
    module = package / "schema.py"

    def publish(version: str) -> None:
        module.write_text(
            (
                "import asyncio\n"
                "async def init_database(bot):\n"
                "    with open(MARKER, 'a') as handle:\n"
                "        handle.write(VERSION + ' ' + str(id(asyncio.get_running_loop())) + '\\n')\n"
            )
            .replace("MARKER", repr(str(marker)))
            .replace("VERSION", repr(version))
        )

    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(updates, "SCHEMA_MODULE", "schema_pkg.schema")
    # The module lives in a temp package here, not under the repo's src/.
    monkeypatch.setattr(updates, "_module_source", lambda name: module)

    publish("first")
    updates.reload_database(bot)
    # The update that just landed is what runs next — no stale module, no restart.
    publish("second")
    updates.reload_database(bot)

    runs = marker.read_text().splitlines()
    assert [line.split(" ")[0] for line in runs] == ["first", "second"]
    # Both ran on the bot loop, not on the dashboard's thread.
    assert {line.split(" ")[1] for line in runs} == {str(id(loop))}


def test_applying_only_the_database_area_runs_the_schema_and_does_not_restart(monkeypatch):
    change = {"path": "src/events/startup/database.py", "status": "modified", "bytes": 10, "sha": "sha"}
    monkeypatch.setattr(updates, "plan", lambda areas=None: {
        "ok": True,
        "configured": True,
        "beta": "https://beta.example",
        "areas": {"database": {"label": "Database schema", "changed": 1, "bytes": 10, "files": [change]}},
        "total_changed": 1,
        "total_bytes": 10,
    })
    monkeypatch.setattr(updates, "_stage_area", lambda name, files, run_id: {"written": 1, "removed": 0, "backup": "x"})
    monkeypatch.setattr(updates, "_record", lambda run: None)
    ran = []
    monkeypatch.setattr(updates, "reload_database", lambda bot: ran.append(bot) or {})
    scheduled = []
    monkeypatch.setattr(handoff, "schedule", lambda *args, **kwargs: scheduled.append(True))

    bot = object()
    result = updates.apply(["database"], bot)

    assert result["ok"] is True
    assert result["areas"]["database"]["strategy"] == "re-ran the database schema setup"
    assert ran == [bot]
    assert scheduled == []
