"""Public URLs for the generated loading-card GIFs.

Discord's media proxy caches remote images by URL, so a redesigned placeholder
served from the same path can keep showing the old animation long after the
GIF is regenerated. Every URL built here carries a short hash of the GIF's
bytes (``?hash=<8 hex>``), so a new design is a new URL and the stale cache
entry is never reused.

The hash is read from the copy in this checkout, so it always matches the file
that was deployed with the bot. Flask serves the built site from
``src/website/dist``, and the generators write that mirror alongside
``web/public``; the served copy is preferred and the source is the fallback.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# ``<repo>/src/website/dist``: the build Flask serves; and ``<repo>/web/public``:
# the source folder the generators write before mirroring into the build.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SERVED_ASSETS = _REPO_ROOT / "src" / "website" / "dist" / "assets" / "loading-cards"
_PUBLIC_ASSETS = _REPO_ROOT / "web" / "public" / "assets" / "loading-cards"

_HASH_LENGTH = 8
# Keyed by the file's stat signature so a regenerated GIF picks up a new hash
# without waiting for a restart.
_HASHES: dict[tuple[Path, int, int], str] = {}


def short_asset_hash(path: Path) -> str:
    """The first 8 hex characters of *path*'s SHA-256, or ``""`` if unreadable."""
    try:
        stat = path.stat()
    except OSError:
        return ""

    key = (path, stat.st_mtime_ns, stat.st_size)
    cached = _HASHES.get(key)
    if cached is not None:
        return cached

    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:_HASH_LENGTH]
    except OSError:
        digest = ""
    _HASHES[key] = digest
    return digest


def loading_card_path(relative: str) -> Path:
    """The generated GIF at *relative*, preferring the copy the site serves."""
    relative = relative.lstrip("/")
    for folder in (_SERVED_ASSETS, _PUBLIC_ASSETS):
        candidate = folder / relative
        if candidate.is_file():
            return candidate
    return _PUBLIC_ASSETS / relative


def loading_card_url(base: str, file_name: str) -> str:
    """``{base}/{file_name}`` with a short content hash appended.

    *base* is the URL the site serves the loading-cards folder at, and
    *file_name* may include a sub-folder (``economy/balance.gif``). When the GIF
    is missing from this checkout the URL is returned unchanged, so a
    deployment without the public assets still renders a message.
    """
    relative = file_name.lstrip("/")
    url = f"{base.rstrip('/')}/{relative}"
    digest = short_asset_hash(loading_card_path(relative))
    return f"{url}?hash={digest}" if digest else url
