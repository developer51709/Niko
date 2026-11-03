"""Live translation feed, pulled from the beta instance.

Production ships the website and the bot's wording at build time, so a page's
copy is only as new as the last deploy. A translation pass is written over days
on the beta instance — languages appearing file by file — and the live site
should be able to show what beta has without waiting for a release, a restart or
a git pull.

Beta answers one endpoint for this, ``/api/locales/source.json`` (see
:mod:`webapp.routes.public_routes`): a manifest of every page, the languages
that page has, and a content hash per file. That is all this module needs. The
manifest is re-read every :data:`FEED_TTL` seconds, and a catalogue is fetched
the first time a page asks for a hash it has not seen, so strings written on
beta reach the browser on the next navigation instead of the next deploy.

Three rules keep that safe on a live site:

- **The build is always the fallback.** If beta is not configured, is down, is
  slow, or answers with nonsense, the site keeps rendering the files it shipped
  with and ``source`` says why.
- **Translations cannot invent pages.** A page beta has and the build does not is
  ignored: there is no route for it, and no ``en.json`` to count keys against. A
  new *language* is fine, because a language is just another catalogue file.
- **English keeps the key list.** A translation fills keys in; it cannot rename
  the page or introduce a key the page does not render.

Set ``BETA_INSTANCE_URL`` to the beta origin (``https://beta.example.com``) on the
production instance to turn the feed on. Leave it empty and everything behaves
exactly as it did before, reading local files only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from pathlib import Path

import requests

#: The website's per-page catalogue folders (``web/src/locales/<page>``).
SITE_LOCALES = Path("web/src/locales")

#: Origin of the beta instance, e.g. ``https://beta.niko.sryze.cc``. Empty keeps
#: the feed off and the site on its own build. One variable names beta for every
#: feed that reads from it: translations here, and the owner's update page in
#: :mod:`webapp.updates`.
BETA_INSTANCE_URL = (os.environ.get("BETA_INSTANCE_URL") or "").strip().rstrip("/")

#: How long a beta manifest is reused, in seconds. This is the "realtime" knob:
#: the status page can be at most this far behind the files on beta.
FEED_TTL = max(3.0, float(os.environ.get("LOCALE_FEED_TTL") or 15))

#: How long one HTTP call to beta may take before the build takes over.
FEED_TIMEOUT = max(1.0, float(os.environ.get("LOCALE_FEED_TIMEOUT") or 4))

#: How long the local scan is reused. Reading every catalogue is cheap but not
#: free, and files on this instance only change on deploy.
LOCAL_TTL = 30.0

_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
_LANGUAGE = re.compile(r"^[a-z]{2}(?:-[a-z]{2})?$")

_lock = threading.Lock()
_beta: dict = {"manifest": None, "at": 0.0, "error": None, "stale": False, "refreshing": False}
_local: dict = {"snapshot": None, "at": 0.0}
_catalogues: dict[tuple[str, str, str], dict] = {}


# ──────────────────────────────────────────────────────────────────────────────
# Local scan
# ──────────────────────────────────────────────────────────────────────────────
def _status():
    """The scan helpers live in :mod:`webapp.status`.

    Imported here rather than at module scope because ``status`` imports this
    module to decorate its payload; one lazy import breaks the cycle without
    either module owning a copy of the leaf-key walk.
    """
    from . import status

    return status


def _digest(raw: bytes) -> str:
    return hashlib.sha1(raw).hexdigest()[:12]


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _order(codes) -> list[str]:
    """English first, then the rest alphabetically, so the site is stable."""
    rest = sorted(code for code in codes if code != "en")
    return ["en", *rest] if "en" in codes else rest


def local_snapshot(force: bool = False) -> dict:
    """This instance's own catalogues, in the shape beta publishes.

    ``pages[<page>].langs[<code>]`` carries the number of English keys the file
    covers and a hash of its bytes. Coverage is counted from those two numbers,
    so the status page and the files on disk can never disagree.
    """
    now = time.monotonic()
    with _lock:
        cached = _local["snapshot"]
        if cached is not None and not force and now - _local["at"] < LOCAL_TTL:
            return cached

    status = _status()
    labels: dict[str, str] = {}
    pages: dict[str, dict] = {}

    if SITE_LOCALES.is_dir():
        for folder in sorted(path for path in SITE_LOCALES.iterdir() if path.is_dir()):
            english_path = folder / "en.json"
            if not english_path.is_file():
                continue
            english = _read_json(english_path)
            if not isinstance(english, dict):
                continue
            english_keys = set(status._leaf_keys(english))
            entry: dict = {"keys": len(english_keys), "langs": {}}
            for path in sorted(folder.glob("*.json")):
                code = path.stem
                if not _LANGUAGE.match(code):
                    continue
                try:
                    raw = path.read_bytes()
                    catalogue = json.loads(raw)
                except Exception:
                    continue
                if not isinstance(catalogue, dict):
                    continue
                keys = set(status._leaf_keys(catalogue))
                translated = len(english_keys) if code == "en" else len(english_keys & keys)
                entry["langs"][code] = {"translated": translated, "hash": _digest(raw)}
                labels.setdefault(code, status.LANGUAGE_LABELS.get(code, code.upper()))
            pages[folder.name] = entry

    snapshot = {
        "languages": [{"code": code, "label": labels[code]} for code in _order(labels)],
        "pages": pages,
        "bot": status._bot_locale_status(),
        "generated_at": int(time.time()),
    }
    with _lock:
        _local.update({"snapshot": snapshot, "at": now})
    return snapshot


# ──────────────────────────────────────────────────────────────────────────────
# Beta
# ──────────────────────────────────────────────────────────────────────────────
def _validated(snapshot) -> dict | None:
    """Keep the parts of a beta snapshot the site can actually act on.

    Anything malformed is dropped rather than trusted: beta is another machine,
    and a half-written catalogue must not be able to blank a page.
    """
    if not isinstance(snapshot, dict):
        return None
    raw_pages = snapshot.get("pages")
    if not isinstance(raw_pages, dict):
        return None

    pages: dict[str, dict] = {}
    for name, entry in raw_pages.items():
        if not isinstance(name, str) or not _NAME.match(name) or not isinstance(entry, dict):
            continue
        keys = entry.get("keys")
        langs = entry.get("langs")
        if not isinstance(keys, int) or keys < 0 or not isinstance(langs, dict):
            continue
        clean: dict[str, dict] = {}
        for code, info in langs.items():
            if not isinstance(code, str) or not _LANGUAGE.match(code) or not isinstance(info, dict):
                continue
            digest = info.get("hash")
            translated = info.get("translated")
            if not isinstance(digest, str) or not digest:
                continue
            if not isinstance(translated, int) or translated < 0:
                translated = 0
            clean[code] = {"translated": min(translated, keys), "hash": digest[:40]}
        # A page with no English file has no key list to measure against.
        if "en" not in clean:
            continue
        pages[name] = {"keys": keys, "langs": clean}

    if not pages:
        return None

    languages: list[dict] = []
    for row in snapshot.get("languages") or []:
        if not isinstance(row, dict):
            continue
        code = row.get("code")
        if not isinstance(code, str) or not _LANGUAGE.match(code):
            continue
        label = row.get("label")
        languages.append({"code": code, "label": label if isinstance(label, str) and label else code.upper()})
    if not any(row["code"] == "en" for row in languages):
        languages.insert(0, {"code": "en", "label": "English"})

    bot = []
    for row in snapshot.get("bot") or []:
        if not isinstance(row, dict) or not isinstance(row.get("code"), str):
            continue
        if not isinstance(row.get("total"), int):
            continue
        bot.append(row)

    return {
        "languages": languages,
        "pages": pages,
        "bot": bot,
        "generated_at": int(snapshot.get("generated_at") or 0),
    }


def _pull() -> None:
    """Fetch beta's manifest once, keeping the old one if the call fails."""
    try:
        response = requests.get(
            f"{BETA_INSTANCE_URL}/api/locales/source.json",
            timeout=(2.0, FEED_TIMEOUT),
            headers={"Accept": "application/json", "User-Agent": "niko-locale-feed"},
        )
        if response.status_code != 200:
            raise ValueError(f"beta answered {response.status_code}")
        snapshot = _validated(response.json())
        if snapshot is None:
            raise ValueError("beta returned no usable catalogues")
        with _lock:
            _beta.update({"manifest": snapshot, "at": time.monotonic(), "error": None, "stale": False})
    except Exception as exc:
        # Keep the last good manifest and mark it stale: a translation the site
        # already fetched should not disappear because one poll timed out.
        with _lock:
            _beta.update({
                "at": time.monotonic(),
                "error": f"{type(exc).__name__}: {exc}",
                "stale": _beta["manifest"] is not None,
            })
    finally:
        with _lock:
            _beta["refreshing"] = False


def _refresh(force: bool = False) -> None:
    """Keep beta's manifest warm without ever making a page wait for beta.

    The first read of a process has to block — the site has nothing to show yet —
    but every read after that is refreshed on a daemon thread, so a slow beta can
    never add its latency to ``/api/status`` or to a page load.
    """
    if not BETA_INSTANCE_URL:
        return
    now = time.monotonic()
    with _lock:
        cached = _beta["manifest"] is not None
        fresh = cached and now - _beta["at"] < FEED_TTL
        if fresh and not force:
            return
        if cached and not force:
            if not _beta.get("refreshing"):
                _beta["refreshing"] = True
                threading.Thread(target=_pull, daemon=True, name="locale-feed").start()
            return
    _pull()


def _merged_languages(local: dict, beta: dict) -> list[dict]:
    labels = {row["code"]: row["label"] for row in local["languages"]}
    labels.update({row["code"]: row["label"] for row in beta["languages"]})
    # A language counts as available when either side has a file for it: that is
    # how a brand-new beta language reaches the picker before production builds.
    seen = set(labels)
    seen.update(code for page in beta["pages"].values() for code in page["langs"])
    seen.update(code for page in local["pages"].values() for code in page["langs"])
    return [{"code": code, "label": labels.get(code, code.upper())} for code in _order(seen)]


def sync() -> dict:
    """Re-read beta now instead of waiting for the TTL.

    The owner's locale page calls this after adding a language or landing a
    batch of translations, so the page it shows is the one beta has right now.
    """
    _refresh(force=True)
    return manifest(force=True)


def manifest(force: bool = False) -> dict:
    """The catalogue manifest the live site should use, beta first.

    ``source`` travels with it so the status page can say whether it is looking
    at beta's working copy or at the deployed build, and how old the reading is.
    """
    local = local_snapshot()
    _refresh(force=force)

    with _lock:
        beta = _beta["manifest"]
        error = _beta["error"]
        fetched_at = _beta["at"]
        stale = _beta["stale"]

    if beta is None:
        return {
            **local,
            "source": {
                "mode": "local",
                "origin": BETA_INSTANCE_URL or None,
                "error": error,
                "age_seconds": None,
                "stale": False,
            },
        }

    pages = dict(local["pages"])
    for name, entry in beta["pages"].items():
        # Only pages this build can render; beta cannot add a route.
        if name in pages:
            pages[name] = entry

    return {
        "languages": _merged_languages(local, beta),
        "pages": pages,
        "bot": beta["bot"] or local["bot"],
        "generated_at": beta["generated_at"] or local["generated_at"],
        "source": {
            "mode": "beta",
            "origin": BETA_INSTANCE_URL,
            "error": error,
            "age_seconds": max(0, int(time.monotonic() - fetched_at)) if fetched_at else None,
            "stale": stale,
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Catalogues
# ──────────────────────────────────────────────────────────────────────────────
def _remember(page: str, language: str, digest: str, catalogue: dict) -> None:
    with _lock:
        if len(_catalogues) > 512:
            _catalogues.clear()
        _catalogues[(page, language, digest)] = catalogue


def catalogue(page: str, language: str) -> dict | None:
    """One page's strings in one language, newest copy first.

    Returns a dict with ``strings`` (the catalogue), ``hash`` (what to put in an
    ETag) and ``origin`` — ``beta`` when it came over the wire, ``build`` when it
    came from this deployment, ``cache`` when an earlier request already had it.
    """
    if not _NAME.match(page) or not _LANGUAGE.match(language):
        return None

    document = manifest()
    entry = document["pages"].get(page)
    if entry is None:
        return None
    info = entry["langs"].get(language)
    if info is None:
        return None
    digest = info["hash"]
    local_path = SITE_LOCALES / page / f"{language}.json"

    with _lock:
        cached = _catalogues.get((page, language, digest))
    if cached is not None:
        return {"strings": cached, "hash": digest, "origin": "cache"}

    # The build may already hold exactly this file; then no HTTP is needed even
    # on a feed-enabled instance.
    local_entry = local_snapshot()["pages"].get(page, {}).get("langs", {}).get(language)
    if local_entry is not None and local_entry["hash"] == digest and local_path.is_file():
        strings = _read_json(local_path)
        if isinstance(strings, dict):
            _remember(page, language, digest, strings)
            return {"strings": strings, "hash": digest, "origin": "build"}

    if BETA_INSTANCE_URL and document["source"]["mode"] == "beta":
        try:
            response = requests.get(
                f"{BETA_INSTANCE_URL}/api/locales/{page}/{language}.json",
                timeout=(2.0, FEED_TIMEOUT),
                headers={"Accept": "application/json", "User-Agent": "niko-locale-feed"},
            )
            if response.status_code == 200:
                strings = response.json()
                if isinstance(strings, dict):
                    _remember(page, language, digest, strings)
                    return {"strings": strings, "hash": digest, "origin": "beta"}
        except Exception:
            # Fall through to the build: a slow beta must not slow the page down.
            pass

    strings = _read_json(local_path) if local_path.is_file() else None
    if isinstance(strings, dict):
        # The hash of what is actually being served, not the one beta advertised:
        # an ETag that claims beta's content for a build file would earn a wrong
        # 304 the moment beta comes back.
        return {
            "strings": strings,
            "hash": local_entry["hash"] if local_entry else digest,
            "origin": "build",
        }
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Status
# ──────────────────────────────────────────────────────────────────────────────
def coverage_rows(document: dict) -> list[dict]:
    """Website coverage, counted from whichever manifest the site is using."""
    status = _status()
    pages = document["pages"]
    total = sum(entry["keys"] for entry in pages.values())
    rows = []
    for language in document["languages"]:
        code = language["code"]
        translated = sum(entry["langs"].get(code, {}).get("translated", 0) for entry in pages.values())
        complete = sum(
            1
            for entry in pages.values()
            if entry["keys"] and entry["langs"].get(code, {}).get("translated", 0) >= entry["keys"]
        )
        row = status._coverage_row(
            code,
            translated,
            total,
            extra={"pages": len(pages), "complete_pages": complete},
        )
        row["label"] = language["label"]
        rows.append(row)
    return rows


def decorate(payload: dict) -> dict:
    """Point a locale status payload at the feed, without losing its cache."""
    document = manifest()
    source = document["source"]
    payload = dict(payload)
    payload["website"] = coverage_rows(document)
    payload["languages"] = [language["code"] for language in document["languages"]]
    if source["mode"] == "beta":
        if document["bot"]:
            payload["bot"] = document["bot"]
        # When beta scanned its own files, not when this payload was built: the
        # page's "Scanned at" line should describe the catalogues it is showing.
        payload["scanned_at"] = document["generated_at"] or int(time.time())
    payload["source"] = source
    return payload
