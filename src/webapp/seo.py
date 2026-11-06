"""Search-engine discovery files generated from the current site build.

``robots.txt`` and ``sitemap.xml`` are served by the web application instead of
being copied into the built site. The sitemap is rebuilt from
``social-pages.json`` — the same manifest that supplies the per-page social
metadata — so a new documentation page or changelog entry appears as soon as
the site build is deployed, without a separate sitemap file to update.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from urllib.parse import quote
from xml.sax.saxutils import escape

from . import config, social_preview

SITEMAP_PATH = "/sitemap.xml"
ROBOTS_PATH = "/robots.txt"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

#: Public pages that are worth indexing even when the manifest is unavailable.
#: The manifest adds the documentation and changelog entries on top of these.
CORE_PUBLIC_PATHS = (
    "/",
    "/commands",
    "/team",
    "/team/apply",
    "/status",
    "/leaderboard",
    "/support",
    "/discord",
    "/discord/partnership",
    "/docs",
    "/developers",
    "/changelog",
    "/privacy",
    "/terms",
    "/data-removal",
    "/community",
    "/donate",
)

#: A route is never a sitemap entry, regardless of what a manifest contains.
#: ``/levels`` is the template for a server's own leaderboard, not a page.
EXCLUDED_PUBLIC_PATHS = frozenset({"/levels", "/render-lab-b7f3e91c"})

#: Match prefixes, not globs: robots prefixes cover everything below them.
ROBOTS_DISALLOW = (
    "/api/",
    "/auth/",
    "/health",
    "/dashboard",
    "/staff",
    "/transcript",
    "/report/",
    "/apply/",
    "/team/apply/",
    "/billing",
    "/help/flagged-media",
    "/render-lab-b7f3e91c",
)

#: A sitemap only changes when the build does, but keep deploy changes fresh.
CACHE_MAX_AGE = 300


def site_url() -> str:
    """The canonical origin, falling back to the site's own domain."""
    return (config.canonical_origin() or social_preview.SITE_URL).rstrip("/")


def _is_indexable(path: str) -> bool:
    if path in EXCLUDED_PUBLIC_PATHS:
        return False
    return not (
        path.startswith("/api/")
        or path.startswith("/auth/")
        or path.startswith("/dashboard")
        or path.startswith("/staff")
        or path.startswith("/transcript")
        or path.startswith("/report/")
        or path.startswith("/apply/")
        or path.startswith("/team/apply/")
        or path.startswith("/billing")
        or path.startswith("/help/")
    )


def public_paths(pages: dict) -> list[str]:
    """Every indexable public path in the manifest, plus the core pages.

    The manifest's keys are already canonical paths, but they are normalised
    again so a trailing slash or query string cannot produce a duplicate URL.
    """
    paths = set(CORE_PUBLIC_PATHS)
    for raw_path in pages:
        path = social_preview.route_key(str(raw_path))
        if _is_indexable(path):
            paths.add(path)
    return sorted(paths, key=lambda path: (path != "/", path))


def manifest_last_modified(dist_dir: str) -> str | None:
    """The build manifest's modification time as a sitemap ``lastmod``."""
    try:
        stamp = os.stat(os.path.join(dist_dir, social_preview.MANIFEST_NAME)).st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(stamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sitemap_xml(base_url: str, paths: list[str], last_modified: str | None = None) -> str:
    """Render a sitemap for *paths* under *base_url*."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<urlset xmlns="{SITEMAP_NAMESPACE}">',
    ]
    for path in paths:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(base_url + quote(path, safe='/'))}</loc>")
        if last_modified:
            lines.append(f"    <lastmod>{escape(last_modified)}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def robots_txt(base_url: str) -> str:
    """Render robots directives and point crawlers at the sitemap."""
    lines = ["User-agent: *", "Allow: /"]
    lines.extend(f"Disallow: {path}" for path in ROBOTS_DISALLOW)
    lines.extend(["", f"Sitemap: {base_url}{SITEMAP_PATH}", ""])
    return "\n".join(lines)


def current_sitemap() -> str:
    """The sitemap for the site build currently on disk."""
    paths = public_paths(social_preview.load_pages(config.WEB_DIST_DIR))
    return sitemap_xml(
        site_url(),
        paths,
        manifest_last_modified(config.WEB_DIST_DIR),
    )
