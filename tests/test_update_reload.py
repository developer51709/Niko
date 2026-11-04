"""Applying an API update in place, without a restart.

The owner's update page can replace ``src/webapp/**`` and rebuild the Flask app
under the running socket. Two things have to hold for that to be usable:

* a rebuild that fails must leave the API serving the code it started with, not
  a process whose modules have been dropped and whose lazy imports now execute a
  file that does not import, and
* the updater itself lives in the area it replaces, so it has to re-read its own
  file or the new update logic sits on disk until the next restart.
"""

import importlib
import importlib.util
import py_compile
import socket
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

import api_server
from webapp import updates


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def _health(port: int) -> dict:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=10) as response:
        return {"status": response.status, "body": response.read(64)}


def _unhealthy_app():
    """A stand-in ``webapp`` package whose API cannot answer a request."""
    from types import SimpleNamespace

    from flask import Flask

    app = Flask("unhealthy")

    @app.route("/api/health")
    def health():
        return {"ok": False}, 500

    return SimpleNamespace(app=app, configure_bot=lambda bot: None)


class ApiReloadTests(unittest.TestCase):
    def setUp(self):
        # A reload replaces the ``webapp.*`` modules for the whole process, so
        # the rest of the suite gets the ones it imported back afterwards.
        self.modules = updates._webapp_modules()
        self.port = _free_port()
        api_server.start_api_server(None, port=self.port)

    def tearDown(self):
        api_server.stop_serving()
        updates._restore_modules(self.modules)

    def test_a_rebuild_swaps_the_app_and_keeps_the_socket_serving(self):
        before = api_server._server.app
        server_module = sys.modules["webapp.server"]

        outcome = updates.reload_webapp(None)

        self.assertTrue(outcome["swapped"])
        self.assertGreater(outcome["routes"], 0)
        # A new app object answers on the same listening socket, and the new
        # route modules are the ones the server will import from now on.
        self.assertIsNot(api_server._server.app, before)
        self.assertIsNot(sys.modules["webapp.server"], server_module)
        self.assertEqual(_health(self.port)["status"], 200)

    def test_a_failed_rebuild_leaves_the_old_app_serving(self):
        before = api_server._server.app
        modules = updates._webapp_modules()
        server_module = modules["webapp.server"]

        # The new webapp file that does not import: the import is what fails.
        with patch("importlib.import_module", side_effect=ImportError("broken webapp")):
            with self.assertRaises(ImportError):
                updates.reload_webapp(None)

        # The server was never handed a new app, and the modules it answers with
        # are exactly the ones it started with — no half-purged state for a lazy
        # import inside a route to trip over.
        self.assertIs(api_server._server.app, before)
        self.assertIs(sys.modules["webapp.server"], server_module)
        self.assertIs(sys.modules["webapp"], modules["webapp"])
        self.assertEqual(_health(self.port)["status"], 200)

    def test_the_route_modules_are_importable_again_after_a_failed_rebuild(self):
        before = api_server._server.app

        with patch("importlib.import_module", side_effect=ImportError("broken webapp")):
            with self.assertRaises(ImportError):
                updates.reload_webapp(None)

        # A route module imported lazily after the failed rebuild is the module
        # the running app was built from, not a second execution of the bad file.
        self.assertIs(importlib.import_module("webapp.routes.owner_routes"), sys.modules["webapp.routes.owner_routes"])
        self.assertIs(api_server._server.app, before)


class UpdaterReloadTests(unittest.TestCase):
    def test_the_updater_reloads_its_own_file_and_keeps_its_state(self):
        module = sys.modules["webapp.updates"]
        lock, state, cache = updates._lock, updates._running, updates._manifest_cache

        self.assertTrue(updates.reload_updates_module())

        # Same module object, same live state: a run in flight keeps its progress
        # and the manifest it just fetched is not re-read.
        self.assertIs(sys.modules["webapp.updates"], module)
        self.assertIs(updates._lock, lock)
        self.assertIs(updates._running, state)
        self.assertIs(updates._manifest_cache, cache)

    def test_a_broken_updater_file_does_not_break_the_update_path(self):
        with patch("importlib.reload", side_effect=SyntaxError("broken updater")):
            self.assertFalse(updates.reload_updates_module())

        # The running module is untouched, so the page keeps working.
        self.assertIn("apply", dir(updates))


class TransactionalApiUpdateTests(unittest.TestCase):
    """An API update applied from the page ends with a serving API."""

    def test_a_webapp_run_finishes_its_result_and_reloads_the_updater(self):
        state, lock = updates._running, updates._lock
        assert not state["active"]
        fake_plan = {
            "ok": True,
            "configured": True,
            "areas": {"webapp": {"changed": 1, "files": [{"path": "src/webapp/server.py", "status": "modified", "sha": "x", "bytes": 1}]}},
        }
        with patch.object(updates, "plan", return_value=fake_plan), \
                patch.object(updates, "_stage_area", return_value={"written": 1, "removed": 0, "backup": ""}), \
                patch.object(updates, "_record"), \
                patch.object(updates, "reload_webapp", return_value={"swapped": True, "routes": 233}):
            result = updates.apply(["webapp"], None)

        # The apply frame survives the reload: the caller still gets its result.
        self.assertTrue(result["ok"])
        self.assertEqual(result["areas"]["webapp"]["strategy"], "rebuilt the dashboard app")
        # And the running updater is the same module, with the same live state.
        self.assertIs(updates._running, state)
        self.assertIs(updates._lock, lock)
        self.assertFalse(updates.progress()["active"])

    def test_a_utils_run_purges_the_changed_modules(self):
        # The plan lists change records, not bare paths. Reading ``path`` off
        # each one is what keeps the purge from being handed a dict.
        fake_plan = {
            "ok": True,
            "configured": True,
            "areas": {"utils": {"changed": 2, "files": [
                {"path": "src/utils/locales.py", "status": "modified", "sha": "x", "bytes": 1},
                {"path": "src/utils/ai/config.py", "status": "modified", "sha": "y", "bytes": 1},
            ]}},
        }
        purged = {}

        def record_purge(prefixes):
            purged["prefixes"] = list(prefixes)
            return list(prefixes)

        with patch.object(updates, "plan", return_value=fake_plan), \
                patch.object(updates, "_stage_area", return_value={"written": 2, "removed": 0, "backup": ""}), \
                patch.object(updates, "_purge", side_effect=record_purge), \
                patch.object(updates, "reload_extensions", return_value={"reloaded": []}), \
                patch.object(updates, "reload_webapp", return_value={"swapped": True, "routes": 1}), \
                patch.object(updates, "reload_updates_module", return_value=True), \
                patch.object(updates, "_record"):
            result = updates.apply(["utils"], object())

        self.assertTrue(result["ok"])
        self.assertEqual(purged["prefixes"], ["utils.ai", "utils.locales"])
        self.assertEqual(result["areas"]["utils"]["strategy"], "reloaded modules, extensions and the dashboard")

    def test_a_run_that_replaced_api_code_reloads_the_updater(self):
        source = (updates.ROOT / "src" / "webapp" / "updates.py").read_text(encoding="utf-8")

        self.assertIn('if any(name in results for name in ("utils", "webapp")):', source)
        # The call site (the last mention, after its own definition).
        call = source.rindex("reload_updates_module()")
        # It runs after the run is recorded and the result is built, because the
        # frame returning it must not read a module-level name whose value the
        # reload has just replaced.
        self.assertLess(source.index("    _record(run)"), call)
        self.assertLess(source.index("result = {**current"), call)
        self.assertLess(call, source.index("    return result"))


class SwapVerificationTests(unittest.TestCase):
    def setUp(self):
        self.modules = updates._webapp_modules()
        self.port = _free_port()
        api_server.start_api_server(None, port=self.port)

    def tearDown(self):
        api_server.stop_serving()
        updates._restore_modules(self.modules)

    def test_an_app_that_does_not_answer_is_rolled_back(self):
        # A rebuild can import cleanly and still be unable to serve a request;
        # reporting it as applied is how an API update looks like it needs a
        # restart.
        before_app = api_server._server.app

        with patch("importlib.import_module", return_value=_unhealthy_app()):
            with self.assertRaises(RuntimeError):
                updates.reload_webapp(None)

        self.assertIs(api_server._server.app, before_app)
        self.assertIs(sys.modules["webapp"], self.modules["webapp"])
        self.assertEqual(_health(self.port)["status"], 200)

    def test_a_swap_that_never_lands_is_rolled_back(self):
        before_app = api_server._server.app

        # A ``replace_app`` that silently does nothing must not be reported as a
        # successful update.
        with patch.object(api_server, "replace_app", lambda app: None):
            with self.assertRaises(RuntimeError):
                updates.reload_webapp(None)

        self.assertIs(api_server._server.app, before_app)
        self.assertIs(sys.modules["webapp"], self.modules["webapp"])
        self.assertEqual(_health(self.port)["status"], 200)


class BytecodeTests(unittest.TestCase):
    def test_replacing_a_module_drops_its_compiled_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "webapp" / "thing.py"
            source.parent.mkdir(parents=True)
            source.write_text("VALUE = 1\n", encoding="utf-8")
            py_compile.compile(str(source), doraise=True)
            cached = Path(importlib.util.cache_from_source(str(source)))
            self.assertTrue(cached.is_file())

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "DATA_DIR", root / "data" / "updates"), \
                    patch.object(updates, "_download", lambda relative, expected: b"VALUE = 2\n"):
                updates._stage_area("webapp", [{"path": "src/webapp/thing.py", "status": "modified", "sha": "x"}], "run")

            self.assertEqual(source.read_text(encoding="utf-8"), "VALUE = 2\n")
            # A compiled copy whose stamp still matches the file would keep the
            # old module importing until the process restarts.
            self.assertFalse(cached.is_file())
