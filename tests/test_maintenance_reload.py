"""A dashboard-only update must not need a bot restart to show its data.

The updater writes ``src/utils`` before it rebuilds the dashboard, and the
rebuild only re-imports ``webapp.*``. ``from utils import maintenance`` resolves
through the package attribute, so the rebuilt route keeps the module the process
imported at startup unless it re-reads the file itself.
"""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp.routes import maintenance_routes  # noqa: E402


def _package(tmp_path, name):
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    return package


def test_the_route_re_reads_a_module_that_was_purged_under_it(tmp_path, monkeypatch):
    package = _package(tmp_path, "staletarget")
    child = package / "child.py"
    # A different length on rewrite: the bytecode cache is keyed on mtime second
    # and size, so a same-second same-size edit would load the stale .pyc.
    child.write_text("VALUE = 'old'\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))

    module = importlib.import_module("staletarget.child")
    assert module.VALUE == "old"

    # What the updater used to leave behind: gone from sys.modules, still the
    # attribute on the package, which is what ``from … import …`` reads.
    del sys.modules["staletarget.child"]
    monkeypatch.setattr(maintenance_routes, "maintenance", module)
    monkeypatch.setattr(maintenance_routes, "_refreshed", False)

    child.write_text("VALUE = 'the-new-build'\n", encoding="utf-8")
    state = maintenance_routes._state()

    assert state is module
    assert state.VALUE == "the-new-build"
    assert sys.modules["staletarget.child"] is module


def test_the_route_re_reads_once_per_build(monkeypatch):
    calls = []

    class _Module:
        __name__ = "staleroute.double"

    monkeypatch.setattr(maintenance_routes, "maintenance", _Module())
    monkeypatch.setattr(maintenance_routes, "_refreshed", False)
    monkeypatch.setattr(
        maintenance_routes.importlib,
        "reload",
        lambda module: calls.append(module) or module,
    )

    maintenance_routes._state()
    maintenance_routes._state()

    assert len(calls) == 1
