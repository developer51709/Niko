"""An applied update must be the code that answers, with no restart.

Dropping a module from ``sys.modules`` is not enough on its own: ``from utils
import maintenance`` resolves through the attribute the package holds, so a
purged module that is still reachable that way kept answering requests with the
previous build. That is how a pulled maintenance-snapshot change could sit on
disk while the dashboard still listed commands the old way.
"""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import updates  # noqa: E402


def _write(package: Path, name: str, body: str) -> None:
    (package / name).write_text(body, encoding="utf-8")


def test_purge_makes_a_from_import_read_the_new_file(tmp_path, monkeypatch):
    package = tmp_path / "purgetest"
    package.mkdir()
    _write(package, "__init__.py", "")
    # The new body is deliberately a different length: the bytecode cache is
    # keyed on (mtime second, size), and a same-second same-size rewrite would
    # reload from the old .pyc rather than from disk.
    _write(package, "child.py", "VALUE = 'old'\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setitem(sys.modules, "purgetest", importlib.import_module("purgetest"))

    first = importlib.import_module("purgetest.child")
    assert first.VALUE == "old"

    _write(package, "child.py", "VALUE = 'the-new-build'\n")
    assert "purgetest.child" in updates._purge(["purgetest.child"])

    from purgetest import child as second

    assert second is not first
    assert second.VALUE == "the-new-build"


def test_a_purged_module_that_is_still_imported_elsewhere_is_left_alone(tmp_path, monkeypatch):
    """Only the attribute pointing at the purged module is dropped."""
    package = tmp_path / "purgetest2"
    package.mkdir()
    _write(package, "__init__.py", "")
    _write(package, "sibling.py", "VALUE = 'sibling'\n")
    _write(package, "target.py", "VALUE = 'old'\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    sibling = importlib.import_module("purgetest2.sibling")
    target = importlib.import_module("purgetest2.target")

    updates._purge(["purgetest2.target"])

    from purgetest2 import sibling as again, target as reloaded

    assert again is sibling
    assert reloaded is not target
