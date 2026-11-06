"""A new shared module travels with the update that needs it.

``src/config`` is configured per deployment, so it is normally never overwritten
— but an update that ships code importing a *new* config module has to write that
module first, or the reload dies with ``ModuleNotFoundError`` and the area rolls
back. ``links.py`` is the exception: it only ever holds production URLs, so beta's
copy replaces it and a link change needs no manual deployment restart.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from webapp import updates


def _manifest(files_by_area: dict[str, dict[str, str]]) -> dict:
    return {
        "areas": {
            name: {"files": {path: {"sha": sha, "size": 12} for path, sha in files.items()}}
            for name, files in files_by_area.items()
        }
    }


class SharedModulePlanTests(unittest.TestCase):
    def test_config_belongs_to_an_additive_area_that_applies_first(self):
        self.assertEqual(updates.area_for_path("src/config/version.py"), "support")
        self.assertTrue(updates.AREAS["support"]["additive"])
        self.assertEqual(updates.AREA_ORDER[0], "support")

    def test_only_a_config_module_this_deployment_lacks_is_a_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "ids.py").write_text("GUILD = 1\n", encoding="utf-8")
            document = _manifest({"support": {
                "src/config/version.py": "a" * 40,
                "src/config/ids.py": "b" * 40,
            }})

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "beta_manifest", lambda force=False: document):
                planned = updates.plan(["support"])

        files = planned["areas"]["support"]["files"]
        # The module that exists here keeps this deployment's own values; the new
        # one has nothing to overwrite and has to arrive.
        self.assertEqual([entry["path"] for entry in files], ["src/config/version.py"])
        self.assertEqual(files[0]["status"], "added")

    def test_links_is_replaced_even_though_the_area_is_additive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "links.py").write_text("SITE = 'old'\n", encoding="utf-8")
            document = _manifest({"support": {
                "src/config/links.py": "a" * 40,
            }})

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "beta_manifest", lambda force=False: document):
                planned = updates.plan(["support"])

        files = planned["areas"]["support"]["files"]
        self.assertEqual([entry["path"] for entry in files], ["src/config/links.py"])
        self.assertEqual(files[0]["status"], "modified")

    def test_a_config_file_beta_dropped_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "links.py").write_text("SITE = 'x'\n", encoding="utf-8")
            document = _manifest({"support": {}})

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "beta_manifest", lambda force=False: document):
                planned = updates.plan(["support"])

        self.assertEqual(planned["areas"]["support"]["changed"], 0)


class SharedModuleApplyTests(unittest.TestCase):
    def test_a_selected_area_pulls_in_the_shared_module_it_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "ids.py").write_text("GUILD = 1\n", encoding="utf-8")
            (root / "src" / "webapp").mkdir(parents=True)
            (root / "src" / "webapp" / "x.py").write_text("OLD = 1\n", encoding="utf-8")
            document = _manifest({
                "support": {"src/config/version.py": "a" * 40},
                "webapp": {"src/webapp/x.py": "b" * 40},
            })
            order: list[str] = []

            def download(relative, expected):
                order.append(relative)
                return b"NEW = 2\n"

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "DATA_DIR", root / "data" / "updates"), \
                    patch.object(updates, "beta_manifest", lambda force=False: document), \
                    patch.object(updates, "_download", download), \
                    patch.object(updates, "reload_webapp", lambda bot: {"swapped": True, "routes": 1}), \
                    patch.object(updates, "reload_updates_module", lambda: True), \
                    patch.object(updates, "_record", lambda run: None):
                result = updates.apply(["webapp"], None)

            self.assertTrue((root / "src" / "config" / "version.py").is_file())
            self.assertEqual((root / "src" / "config" / "ids.py").read_text(encoding="utf-8"), "GUILD = 1\n")
            self.assertEqual((root / "src" / "webapp" / "x.py").read_text(encoding="utf-8"), "NEW = 2\n")

        # The new module is on disk before the area that imports it is rebuilt,
        # which is the whole point of the area ordering.
        self.assertEqual(order, ["src/config/version.py", "src/webapp/x.py"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["areas"]["support"]["strategy"], "added new shared modules")
        self.assertEqual(result["areas"]["webapp"]["strategy"], "rebuilt the dashboard app")

    def test_a_links_change_rides_along_with_another_area(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "links.py").write_text("SITE = 'old'\n", encoding="utf-8")
            (root / "src" / "webapp").mkdir(parents=True)
            (root / "src" / "webapp" / "x.py").write_text("OLD = 1\n", encoding="utf-8")
            document = _manifest({
                "support": {"src/config/links.py": "a" * 40},
                "webapp": {"src/webapp/x.py": "b" * 40},
            })
            bodies = {
                "src/config/links.py": b"SITE = 'https://niko.sryze.cc'\n",
                "src/webapp/x.py": b"NEW = 2\n",
            }
            order: list[str] = []

            def download(relative, expected):
                order.append(relative)
                return bodies[relative]

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "DATA_DIR", root / "data" / "updates"), \
                    patch.object(updates, "beta_manifest", lambda force=False: document), \
                    patch.object(updates, "_download", download), \
                    patch.object(updates, "reload_webapp", lambda bot: {"swapped": True, "routes": 1}), \
                    patch.object(updates, "reload_updates_module", lambda: True), \
                    patch.object(updates, "_record", lambda run: None):
                result = updates.apply(["webapp"], None)

            links = (root / "src" / "config" / "links.py").read_text(encoding="utf-8")

        # links.py is applied first even though the owner only selected webapp,
        # and the strategy reports a replacement rather than a new module.
        self.assertEqual(order, ["src/config/links.py", "src/webapp/x.py"])
        self.assertEqual(links, "SITE = 'https://niko.sryze.cc'\n")
        self.assertEqual(result["areas"]["support"]["strategy"], "updated shared modules")

    def test_a_deployment_that_has_every_config_keeps_support_out_of_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "config").mkdir(parents=True)
            (root / "src" / "config" / "version.py").write_text("VERSION = '2.27.0'\n", encoding="utf-8")
            (root / "src" / "webapp").mkdir(parents=True)
            (root / "src" / "webapp" / "x.py").write_text("OLD = 1\n", encoding="utf-8")
            document = _manifest({
                "support": {"src/config/version.py": "a" * 40},
                "webapp": {"src/webapp/x.py": "b" * 40},
            })

            with patch.object(updates, "ROOT", root), \
                    patch.object(updates, "DATA_DIR", root / "data" / "updates"), \
                    patch.object(updates, "beta_manifest", lambda force=False: document), \
                    patch.object(updates, "_download", lambda relative, expected: b"NEW = 2\n"), \
                    patch.object(updates, "reload_webapp", lambda bot: {"swapped": True, "routes": 1}), \
                    patch.object(updates, "reload_updates_module", lambda: True), \
                    patch.object(updates, "_record", lambda run: None):
                result = updates.apply(["webapp"], None)
                kept = (root / "src" / "config" / "version.py").read_text(encoding="utf-8")

        # Nothing to add means no extra row in the run, and the local config is
        # still this deployment's own copy.
        self.assertNotIn("support", result["areas"])
        self.assertEqual(kept, "VERSION = '2.27.0'\n")
        self.assertTrue(result["ok"])

    def test_selecting_nothing_still_writes_nothing(self):
        with patch.object(updates, "plan", return_value={"ok": True, "areas": {}}) as planned, \
                patch.object(updates, "_record", lambda run: None):
            result = updates.apply([], None)

        # No areas chosen means no run at all: the support area is not a way in.
        self.assertTrue(result["ok"])
        self.assertEqual(result["areas"], {})
        self.assertEqual(planned.call_args.args[0], [])
