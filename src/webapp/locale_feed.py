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

The bot's own wording travels the same way. Every cog keeps its strings in
``src/<package>/locales/<lang>.json``, and the manifest lists those catalogues
too (``bot_pages``). Beta serves them at
``/api/locales/bot/<package>/<lang>.json``; production fetches the ones whose
hash it has not seen and hands the whole set to :mod:`utils.locales` as a live
overlay, which every ``msg()`` lookup reads. A bot reply written on beta is
therefore shown by the running process — no cog reload, no deploy, no restart.

Beta itself reads its own files, never a feed of its own, so the same timer also
watches those files: :func:`utils.locales.refresh_from_disk` notices a catalogue
saved on this instance and moves the revision every live table re-resolves on.
Both halves therefore pick up a translation within seconds, which is what the
website's per-request file reads have always done.

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

import asyncio
import hashlib
import logging
import os
import re
import threading
import time
from pathlib import Path

import requests

#: The website's per-page catalogue folders (``web/src/locales/<page>``, with
#: subfolders of their own once a page has sub pages).
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

#: A bot catalogue is named after the package that owns it (``cogs.music``),
#: which :func:`webapp.status.bot_catalogue_name` produces from its folder.
_BOT_NAME = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+){0,4}$")

_lock = threading.Lock()
_beta: dict = {"manifest": None, "at": 0.0, "error": None, "stale": False, "refreshing": False}
_local: dict = {"snapshot": None, "at": 0.0}
_catalogues: dict[tuple[str, str, str], dict] = {}

#: Bot catalogue bytes fetched from beta, keyed by (package, language, hash).
_bot_files: dict[tuple[str, str, str], dict] = {}
_bot: dict = {
    "packages": 0,
    "files": 0,
    "fetched": 0,
    "reused": 0,
    #: The catalogues the running bot is actually serving, so a failed fetch can
    #: keep its last good copy instead of falling back to English.
    "applied": {},
    "applied_at": 0.0,
    "error": None,
    "refreshing": False,
}

#: The background poller is started once per process (:func:`start_sync_loop`).
_loop: dict = {"started": False}

#: Key in the existing ``sync_state`` key/value table. The owner's manual mode
#: is a property of this deployment, so it lives in the database rather than on
#: a disk production does not have.
_AUTO_SYNC_KEY = "locale_auto_sync"

#: The owner's choice, read once at startup and kept in step by the dashboard.
_settings = {"auto": True, "loaded": False}

log = logging.getLogger(__name__)


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
            english, _ = status.site_catalogue(folder, "en")
            if not english:
                continue
            english_keys = set(status._leaf_keys(english))
            entry: dict = {"keys": len(english_keys), "langs": {}}
            for code in status.site_page_languages(folder):
                if not _LANGUAGE.match(code):
                    continue
                # A page split into subfolders is one catalogue to the site, so
                # the count and the hash cover every file that carries its copy.
                catalogue, raw = status.site_catalogue(folder, code)
                if not catalogue:
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
        # Per-catalogue detail for the bot half of the feed: the coverage rows
        # above are what the status page draws, while these hashes are what a
        # production instance needs to fetch only the files that changed.
        "bot_pages": status.bot_catalogues(force=force),
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

    bot_pages: dict[str, dict] = {}
    raw_bot_pages = snapshot.get("bot_pages")
    if isinstance(raw_bot_pages, dict):
        for name, entry in raw_bot_pages.items():
            if not isinstance(name, str) or not _BOT_NAME.match(name) or not isinstance(entry, dict):
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
            if "en" in clean:
                bot_pages[name] = {"keys": keys, "langs": clean}

    return {
        "languages": languages,
        "pages": pages,
        "bot": bot,
        "bot_pages": bot_pages,
        "generated_at": int(snapshot.get("generated_at") or 0),
    }


def _pull(pull_bot: bool = True) -> None:
    """Fetch beta's manifest once, keeping the old one if the call fails.

    ``pull_bot`` is false when the caller is about to refresh the bot's overlay
    itself (the owner pressed Sync): spawning the background pass there would
    race with the synchronous one and report a half-finished state.
    """
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
        # The bot's overlay is refreshed off the request path: a page asking for
        # its copy must never wait for a hundred catalogue files.
        if pull_bot:
            _sync_bot_async()
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


def _refresh(force: bool = False, pull_bot: bool = True) -> None:
    """Keep beta's manifest warm without ever making a page wait for beta.

    The first read of a process has to block — the site has nothing to show yet —
    but every read after that is refreshed on a daemon thread, so a slow beta can
    never add its latency to ``/api/status`` or to a page load.
    """
    if not BETA_INSTANCE_URL:
        return
    # Manual mode: only an explicit sync (``force=True``) may contact beta.
    # Without this, opening any page still refreshed the feed in the background.
    if not force and not auto_sync_enabled():
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
                threading.Thread(target=_pull, args=(pull_bot,), daemon=True, name="locale-feed").start()
            return
    _pull(pull_bot)


# ──────────────────────────────────────────────────────────────────────────────
# Bot catalogues
# ──────────────────────────────────────────────────────────────────────────────
def local_bot_catalogue(name: str, language: str) -> dict | None:
    """One bot catalogue from this instance's own ``locales`` folder.

    This is what beta answers a production instance with; it never consults a
    feed of its own, so a deployment pointed at itself cannot recurse.
    """
    if not _BOT_NAME.match(name or "") or not _LANGUAGE.match(language or ""):
        return None
    strings, raw = _status().bot_catalogue(name, language)
    if not strings:
        return None
    return {"strings": strings, "hash": _digest(raw), "origin": "build"}


def _fetch_bot_catalogue(name: str, code: str) -> dict | None:
    """One bot catalogue over the wire, or ``None`` when beta could not serve it."""
    try:
        response = requests.get(
            f"{BETA_INSTANCE_URL}/api/locales/bot/{name}/{code}.json",
            timeout=(2.0, FEED_TIMEOUT),
            headers={"Accept": "application/json", "User-Agent": "niko-locale-feed"},
        )
        if response.status_code != 200:
            raise ValueError(f"beta answered {response.status_code}")
        payload = response.json()
    except Exception:
        return None
    return payload if isinstance(payload, dict) and payload else None


def _bot_overlay(document: dict, previous: dict) -> tuple[dict[str, dict[str, dict]], int, int]:
    """Every bot catalogue the given manifest advertises, fetching new hashes.

    A catalogue already fetched for this hash is reused, so a translation pass
    over one cog costs one file per language, not the whole bot. A language beta
    no longer lists is simply absent from the result, which is how a removed
    translation stops being served.

    A file that cannot be fetched keeps the copy already in use for that
    catalogue: one dropped request must not pull a live server back to English
    while the rest of the pass succeeds. Returns the catalogues, how many files
    were downloaded, and how many fell back.
    """
    built: dict[str, dict[str, dict]] = {}
    fetched = 0
    reused = 0
    for name, entry in (document.get("bot_pages") or {}).items():
        for code, info in entry.get("langs", {}).items():
            digest = info.get("hash")
            if not digest:
                continue
            key = (name, code, digest)
            with _lock:
                catalogue = _bot_files.get(key)
            if catalogue is None:
                catalogue = _fetch_bot_catalogue(name, code)
                if catalogue is None:
                    catalogue = (previous.get(name) or {}).get(code)
                    if not isinstance(catalogue, dict) or not catalogue:
                        continue
                    reused += 1
                else:
                    with _lock:
                        if len(_bot_files) > 512:
                            _bot_files.clear()
                        _bot_files[key] = catalogue
                    fetched += 1
            built.setdefault(name, {})[code] = catalogue
    return built, fetched, reused


def apply_bot_catalogues(document: dict | None = None) -> dict:
    """Give the running bot beta's wording, without touching its files.

    The overlay lives in :mod:`utils.locales` and every ``load_locales`` table
    reads through it, so a translation written on beta is used by the next reply
    rather than the next deploy. When beta is unreachable the overlay is left
    alone: a network blip must not roll the bot back to English mid-conversation.
    """
    with _lock:
        if _bot.get("refreshing"):
            return dict(_bot)
        _bot["refreshing"] = True
    try:
        document = document if document is not None else manifest(pull_bot=False)
        source = (document or {}).get("source") or {}
        if source.get("mode") != "beta" or not document.get("bot_pages"):
            # No feed: drop any stale overlay so the bot serves its own files.
            error = None if not BETA_INSTANCE_URL else source.get("error")
            try:
                from utils.locales import apply_overlay

                apply_overlay({})
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            with _lock:
                _bot.update({
                    "packages": 0,
                    "files": 0,
                    "fetched": 0,
                    "reused": 0,
                    "applied": {},
                    "error": error,
                    "applied_at": time.time(),
                })
            return dict(_bot)

        with _lock:
            previous = dict(_bot["applied"])
        built, fetched, reused = _bot_overlay(document, previous)
        if not built:
            # Beta answered with nothing usable. Keep exactly what the bot is
            # already serving rather than swapping in an empty overlay.
            with _lock:
                _bot.update({"error": source.get("error") or "no bot catalogues could be read", "applied_at": time.time()})
            return dict(_bot)

        try:
            from utils.locales import apply_overlay

            apply_overlay(built)
            error = source.get("error")
        except Exception as exc:
            # Never let a bad overlay reach the bot: keep serving what it has.
            error = f"{type(exc).__name__}: {exc}"
            with _lock:
                _bot.update({"error": error, "applied_at": time.time()})
            return dict(_bot)
        with _lock:
            _bot.update({
                "packages": len(built),
                "files": sum(len(langs) for langs in built.values()),
                "fetched": fetched,
                "reused": reused,
                "applied": built,
                "error": error,
                "applied_at": time.time(),
            })
        return dict(_bot)
    finally:
        with _lock:
            _bot["refreshing"] = False


def _sync_bot_async() -> None:
    """Refresh the bot overlay on a daemon thread, never on the caller's."""
    if not BETA_INSTANCE_URL:
        return
    with _lock:
        if _bot.get("refreshing"):
            return
    threading.Thread(target=apply_bot_catalogues, name="locale-bot-sync", daemon=True).start()


def bot_sync_state() -> dict:
    """What the last bot-catalogue sync did, for the owner's locale page."""
    with _lock:
        return {
            "packages": _bot["packages"],
            "files": _bot["files"],
            "fetched": _bot["fetched"],
            "reused": _bot["reused"],
            "error": _bot["error"],
            "applied_at": int(_bot["applied_at"]) or None,
        }


def _watch_local_files() -> None:
    """Pick up catalogues edited on this instance, without a restart.

    Beta reads its own files rather than a feed — a deployment pointed at
    itself would recurse — so a translation saved there has to reach the running
    cog some other way. The tables a cog captured re-resolve when
    :func:`utils.locales.refresh_from_disk` sees a new mtime, which is what this
    thread does on the same cadence as the website's own manifest.
    """
    from utils.locales import refresh_from_disk

    while True:
        try:
            refresh_from_disk()
        except Exception:
            # A watcher must never take the bot down with it.
            pass
        time.sleep(FEED_TTL)


def auto_sync_enabled() -> bool:
    """Whether the background poller may read beta without being asked."""
    return bool(_settings["auto"])


async def load_settings(bot) -> bool:
    """Read the owner's automatic-sync choice from the database.

    ``loaded`` stays false when the table is not ready yet: this can run before
    the startup schema pass on a fresh process, and the feed thread retries the
    read rather than silently running automatic until the next restart.
    """
    pool = getattr(bot, "cxn", None)
    if pool is None:
        # No database means no stored choice; stop the startup retry rather
        # than delaying the first poll forever.
        _settings["loaded"] = True
        return bool(_settings["auto"])
    try:
        stored = await pool.fetchval(
            "SELECT value FROM sync_state WHERE key = $1", _AUTO_SYNC_KEY
        )
    except Exception as exc:
        log.warning("Could not read the automatic locale sync setting: %s", exc)
        return bool(_settings["auto"])
    auto = True
    if stored is not None:
        auto = str(stored).strip().lower() in {"1", "true", "yes", "on"}
    _settings["auto"] = auto
    _settings["loaded"] = True
    return auto


async def set_auto_sync(enabled: bool, actor=None, bot=None) -> bool:
    """Store automatic syncing on or off; the poller reads the new value next."""
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The database is not available.")

    # Delete-then-insert: both database backends accept those statements, and
    # the default (no row) is automatic sync, so only manual mode needs a row.
    await pool.execute("DELETE FROM sync_state WHERE key = $1", _AUTO_SYNC_KEY)
    if not enabled:
        await pool.execute(
            "INSERT INTO sync_state (key, value) VALUES ($1, $2)", _AUTO_SYNC_KEY, "0"
        )
    _settings["auto"] = bool(enabled)
    _settings["loaded"] = True
    log.info("Automatic locale sync turned %s by %s", "on" if enabled else "off", actor)
    return bool(enabled)


def _load_settings_at_start(bot) -> None:
    """Wait for the first database read before the poller can fire.

    The API (and this thread) starts before the startup schema pass, so the
    ``sync_state`` table can still be a moment away. Retry inside a short
    deadline instead of treating that as "automatic": a process restarted in
    manual mode must not poll beta just because it booted quickly.
    """
    if bot is None:
        return
    loop = getattr(bot, "loop", None)
    if loop is None or loop.is_closed():
        return
    deadline = time.monotonic() + 20.0
    last_error = None
    while time.monotonic() < deadline:
        try:
            # This runs on the feed thread, never the event loop, so waiting for
            # the coroutine cannot block the loop it needs to execute on.
            asyncio.run_coroutine_threadsafe(load_settings(bot), loop).result(timeout=5)
        except Exception as exc:
            last_error = exc
        if _settings["loaded"]:
            return
        time.sleep(0.5)
    if last_error is not None:
        log.warning("Could not read the automatic locale sync setting: %s", last_error)


def start_sync_loop(bot=None) -> None:
    """Keep a running bot's wording current, on a timer.

    Two sources, one loop each: this instance's own files (a translator saving
    ``fr.json`` on beta) and beta's feed (production reading beta). Either way a
    cog that captured its tables at import serves the new wording on its next
    reply — no restart, no deploy.

    The beta half honours the owner's automatic-sync choice; manual mode leaves
    that loop idle until :func:`sync` is called by the page's Sync now button.
    """
    with _lock:
        if _loop["started"]:
            return
        _loop["started"] = True

    threading.Thread(target=_watch_local_files, name="locale-files", daemon=True).start()
    if not BETA_INSTANCE_URL:
        return

    def run() -> None:
        _load_settings_at_start(bot)
        while True:
            try:
                _refresh()
            except Exception:
                # The feed records its own errors; the loop only has to survive.
                pass
            time.sleep(FEED_TTL)

    threading.Thread(target=run, name="locale-sync", daemon=True).start()


def _merged_languages(local: dict, beta: dict) -> list[dict]:
    # Beta's labels only fill the gaps. A feed running older code names a
    # language it has no entry for by upper-casing its code ("RU", "ZH"), and
    # that placeholder must not replace the real name this deploy knows — which
    # is the common case, because a new language reaches beta's files before
    # beta's label table has been deployed.
    labels = {row["code"]: row["label"] for row in beta["languages"]}
    labels.update({row["code"]: row["label"] for row in local["languages"]})
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
    The bot's overlay is refreshed here as well, synchronously: the owner pressed
    the button expecting the running bot to be on beta's copy when it returns.
    """
    document = manifest(force=True, pull_bot=False)
    # A background pass may already be downloading catalogues. Wait for it to
    # finish (bounded) so the page the owner gets back describes what the bot
    # is actually serving, instead of the state from before their click.
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        with _lock:
            if not _bot.get("refreshing"):
                break
        time.sleep(0.05)
    apply_bot_catalogues(document)
    return manifest(pull_bot=False)


def manifest(force: bool = False, pull_bot: bool = True) -> dict:
    """The catalogue manifest the live site should use, beta first.

    ``source`` travels with it so the status page can say whether it is looking
    at beta's working copy or at the deployed build, and how old the reading is.
    """
    local = local_snapshot()
    _refresh(force=force, pull_bot=pull_bot)

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
        "bot_pages": beta.get("bot_pages") or local.get("bot_pages") or {},
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
    folder = SITE_LOCALES / page

    with _lock:
        cached = _catalogues.get((page, language, digest))
    if cached is not None:
        return {"strings": cached, "hash": digest, "origin": "cache"}

    # The build may already hold exactly these files; then no HTTP is needed even
    # on a feed-enabled instance.
    local_entry = local_snapshot()["pages"].get(page, {}).get("langs", {}).get(language)
    if local_entry is not None and local_entry["hash"] == digest:
        strings, _ = _status().site_catalogue(folder, language)
        if strings:
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

    strings, raw = _status().site_catalogue(folder, language)
    if strings:
        # The hash of what is actually being served, not the one beta advertised:
        # an ETag that claims beta's content for a build file would earn a wrong
        # 304 the moment beta comes back.
        return {
            "strings": strings,
            "hash": local_entry["hash"] if local_entry else _digest(raw),
            "origin": "build",
        }
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Status
# ──────────────────────────────────────────────────────────────────────────────
def _covered(entries: dict, code: str) -> int:
    """How many of one language's keys a family of catalogues covers."""
    return sum(entry["langs"].get(code, {}).get("translated", 0) for entry in entries.values())


def _finished(entries: dict, code: str) -> int:
    """How many catalogues of a family a language has translated completely."""
    return sum(
        1
        for entry in entries.values()
        if entry["keys"] and entry["langs"].get(code, {}).get("translated", 0) >= entry["keys"]
    )


def coverage_rows(document: dict, include_bot: bool = False) -> list[dict]:
    """Coverage counted from whichever manifest the site is using.

    The public status page keeps the two catalogue families apart, one block
    each, so it reads the website rows alone. The owner's coverage card wants
    the single figure a translator works towards, so it asks for the merged
    totals and still gets each family's finished counts alongside them.
    """
    status = _status()
    pages = document["pages"]
    bot_pages = document.get("bot_pages") or {}
    total = sum(entry["keys"] for entry in pages.values())
    if include_bot:
        total += sum(entry["keys"] for entry in bot_pages.values())
    rows = []
    for language in document["languages"]:
        code = language["code"]
        translated = _covered(pages, code)
        extra = {"pages": len(pages), "complete_pages": _finished(pages, code)}
        if include_bot:
            translated += _covered(bot_pages, code)
            extra["bot"] = len(bot_pages)
            extra["complete_bot"] = _finished(bot_pages, code)
        row = status._coverage_row(code, translated, total, extra=extra)
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
            # Beta supplies the figures, but the names come from the merged
            # language list, so both halves of the page call each language the
            # same thing instead of showing one in English and one endonym.
            names = {row["code"]: row["label"] for row in document["languages"]}
            payload["bot"] = [
                dict(row, label=names.get(row["code"], row.get("label") or row["code"].upper()))
                for row in document["bot"]
            ]
        # When beta scanned its own files, not when this payload was built: the
        # page's "Scanned at" line should describe the catalogues it is showing.
        payload["scanned_at"] = document["generated_at"] or int(time.time())
    payload["source"] = source
    return payload
