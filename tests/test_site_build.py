"""The site build's identity, and the reload notice that depends on it."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, config, site_build  # noqa: E402

SHELL = """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8" /><title>Niko</title></head>
  <body><div id="root"></div><script type="module" src="{entry}"></script></body>
</html>
"""


def _dist(root: Path, entry: str = "/assets/index-AAAA1111.js") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "index.html").write_text(SHELL.format(entry=entry), encoding="utf-8")
    return root


def _build(tmp_path: Path, monkeypatch, entry: str = "/assets/index-AAAA1111.js") -> str:
    monkeypatch.setattr(config, "WEB_DIST_DIR", str(_dist(tmp_path, entry)))
    return site_build.build_id()


def test_the_build_is_the_hashed_entry_script(tmp_path, monkeypatch):
    assert _build(tmp_path, monkeypatch) == "/assets/index-AAAA1111.js"


def test_a_new_bundle_is_a_new_build(tmp_path, monkeypatch):
    dist = _dist(tmp_path)
    monkeypatch.setattr(config, "WEB_DIST_DIR", str(dist))

    first = site_build.build_id()
    # A rebuild rewrites the shell and points at new assets; the name follows.
    _dist(tmp_path, "/assets/index-BBBB2222.js")
    second = site_build.build_id()

    assert first == "/assets/index-AAAA1111.js"
    assert second == "/assets/index-BBBB2222.js"
    assert first != second


def test_a_missing_build_has_no_name(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "WEB_DIST_DIR", str(tmp_path / "absent"))

    assert site_build.build_id() == ""


def test_a_shell_without_a_bundle_is_not_named(tmp_path, monkeypatch):
    # Nothing to compare, so an open tab must not be told it is out of date.
    assert _build(tmp_path, monkeypatch, entry="/assets/other.js") == ""


def test_the_endpoint_answers_with_the_served_build(tmp_path, monkeypatch):
    entry = _build(tmp_path, monkeypatch)

    response = app.test_client().get("/api/site/build")

    assert response.status_code == 200
    assert response.get_json() == {"build": entry}


def test_the_shell_carries_the_build_it_was_served_from():
    response = app.test_client().get("/", headers={"Accept": "text/html"})
    body = response.get_data(as_text=True)

    # The page compares this with /api/site/build; both read the same file, so a
    # fresh page can never look stale to itself.
    marker = body.split("window.__NIKO_SHELL__=", 1)[1].split("</script>", 1)[0]
    assert json.loads(marker)["build"] == site_build.build_id()


def test_the_dashboard_shell_is_the_injected_one():
    # /dashboard used to serve the file on disk, which carries no build id, so a
    # tab parked on it would never have been offered the reload.
    response = app.test_client().get("/dashboard", headers={"Accept": "text/html"})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "window.__NIKO_SHELL__=" in body
    assert json.loads(body.split("window.__NIKO_SHELL__=", 1)[1].split("</script>", 1)[0])["build"] == site_build.build_id()
