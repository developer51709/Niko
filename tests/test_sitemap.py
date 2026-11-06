"""The server-generated sitemap and robots.txt."""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from webapp import app, config, social_preview  # noqa: E402

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def write_manifest(dist: Path, pages: dict) -> Path:
    path = dist / "social-pages.json"
    path.write_text(
        json.dumps({"site": "https://niko.sryze.cc", "pages": pages}),
        encoding="utf-8",
    )
    return path


def sitemap_locations(response) -> list[str]:
    root = ElementTree.fromstring(response.get_data(as_text=True))
    return [
        item.text or ""
        for item in root.findall(f"{{{SITEMAP_NS}}}url/{{{SITEMAP_NS}}}loc")
    ]


@pytest.fixture
def site(tmp_path, monkeypatch):
    monkeypatch.setenv("PUBLIC_URL", "https://public.example/")
    monkeypatch.setattr(config, "WEB_DIST_DIR", str(tmp_path))
    monkeypatch.setattr(
        social_preview,
        "_manifest_cache",
        {"path": None, "stamp": None, "pages": {}},
    )
    write_manifest(tmp_path, {
        "/": {"title": "Home"},
        "/commands": {"title": "Commands"},
        "/docs/new-guide": {"title": "New guide"},
        "/changelog/launch": {"title": "Launch"},
        "/dashboard": {"title": "Private dashboard"},
        "/levels": {"title": "Leaderboard template"},
        "/help/flagged-media": {"title": "Flagged media"},
        "/team/apply/support": {"title": "Application form"},
    })
    return tmp_path


def test_sitemap_lists_public_pages_and_skips_private_ones(site):
    response = app.test_client().get("/sitemap.xml")

    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert response.headers["Cache-Control"].startswith("public, max-age=")

    locations = sitemap_locations(response)
    assert "https://public.example/" in locations
    assert "https://public.example/donate" in locations
    assert "https://public.example/docs/new-guide" in locations
    assert "https://public.example/changelog/launch" in locations
    assert "https://public.example/dashboard" not in locations
    assert "https://public.example/levels" not in locations
    assert "https://public.example/help/flagged-media" not in locations
    assert "https://public.example/team/apply/support" not in locations


def test_sitemap_picks_up_a_new_manifest_entry_without_a_restart(site):
    client = app.test_client()
    assert "https://public.example/changelog/second-release" not in sitemap_locations(
        client.get("/sitemap.xml")
    )

    path = write_manifest(site, {
        "/": {"title": "Home"},
        "/changelog/second-release": {"title": "Second release"},
    })
    stamp = time.time_ns() + 1_000_000_000
    os.utime(path, ns=(stamp, stamp))

    assert "https://public.example/changelog/second-release" in sitemap_locations(
        client.get("/sitemap.xml")
    )


def test_sitemap_uses_the_manifest_build_time_as_lastmod(site):
    path = site / "social-pages.json"
    stamp = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc).timestamp()
    os.utime(path, (stamp, stamp))

    response = app.test_client().get("/sitemap.xml")

    assert "<lastmod>2026-01-02T03:04:05Z</lastmod>" in response.get_data(as_text=True)


def test_robots_points_at_the_canonical_sitemap_and_blocks_private_areas(site):
    response = app.test_client().get("/robots.txt")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert "User-agent: *" in body
    assert "Allow: /" in body
    assert "Sitemap: https://public.example/sitemap.xml" in body
    for path in ("/api/", "/auth/", "/dashboard", "/staff", "/transcript", "/report/", "/billing"):
        assert f"Disallow: {path}" in body


def test_robots_falls_back_to_the_site_origin_without_public_url(site, monkeypatch):
    monkeypatch.delenv("PUBLIC_URL", raising=False)

    body = app.test_client().get("/robots.txt").get_data(as_text=True)

    assert f"Sitemap: {social_preview.SITE_URL}/sitemap.xml" in body
