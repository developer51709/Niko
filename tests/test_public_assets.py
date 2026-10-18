"""Regression checks for public assets referenced by the dashboard."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from webapp import app  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"


def _spotify_path(source: Path) -> str:
    root = ET.fromstring(source.read_text())
    path = root.find(f"{SVG_NS}path")
    assert path is not None, f"{source} has no Spotify glyph"
    data = path.attrib.get("d", "")
    assert data.startswith("M12 0C"), f"{source} has a malformed Spotify glyph"
    assert '""' not in data
    return data


def test_spotify_profile_logo_is_valid_and_served():
    """A broken path attribute made the profile card show a broken image."""
    source = ROOT / "web" / "public" / "spotify.svg"
    assert _spotify_path(source)

    response = app.test_client().get("/spotify.svg")
    assert response.status_code == 200
    assert response.mimetype == "image/svg+xml"
    served = ET.fromstring(response.get_data())
    assert served.find(f"{SVG_NS}path") is not None
