"""Persistent honeypot hits, IP bans, autoban settings, and API rate windows.

The decoy routes used to keep their hit history in this process. That history
vanished on restart, and a crawler probing from many addresses grew the map for
no lasting benefit. The developer API did the same for its per-IP request
timestamps. Both now live in the same database, with only a small cache of
active bans and the current settings kept in memory.

MongoDB is used when ``MONGODB_URL`` is configured (the production path). The
local development and test path is a JSON file under ``DATA_DIR``. MongoDB
collections are created implicitly:

    honeypot_hits   one document per source address, with counters and last hit
    honeypot_bans   one document per banned address
    honeypot_meta   the singleton autoban settings
    api_windows     one fixed-window counter per API source address

Hits are aggregated per address instead of being appended one row per request,
so a crawl cannot make the collection grow with every path it tries. The owner
page still sees the count, the first and last hit, the last path and host, and
the user agent.
"""

from __future__ import annotations

import ipaddress
import json
import logging
import os
import threading
import time
from math import ceil
from typing import Any

from . import config

log = logging.getLogger("Security")

DEFAULT_SETTINGS: dict[str, Any] = {
    "enabled": False,
    "threshold": 20,
    "window_seconds": 300,
    "cooldown_seconds": 86400,
}

#: Keep hit rows long enough to be useful, but not forever.
HIT_RETENTION_SECONDS = 90 * 86400

#: The owner page never asks for more than this many rows at once.
MAX_HITS_PER_PAGE = 500

_MAX_PATH = 500
_MAX_HOST = 200
_MAX_USER_AGENT = 300
_MAX_REASON = 500
_MAX_ACTOR = 100

_STATE_TTL_SECONDS = 10.0
_RETRY_AFTER_ERROR = 30.0
_WINDOW_RETENTION_SECONDS = 3600.0

_LOCK = threading.RLock()
_BACKEND = None
_BACKEND_KEY: tuple[str, str] | None = None
_CLIENT = None

_loaded = False
_state_at = 0.0
_last_load_attempt = 0.0
_bans: dict[str, dict] = {}
_settings: dict[str, Any] = dict(DEFAULT_SETTINGS)
_last_error_log = 0.0
_last_hit_prune = 0.0
_last_window_prune = 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Storage backends
# ──────────────────────────────────────────────────────────────────────────────
def _mongo_url() -> str:
    return (os.environ.get("MONGODB_URL") or "").strip()


def _mongo_database() -> str:
    base = (os.environ.get("MONGODB_DATABASE") or "").strip() or "discord_bot"
    return f"{base}_security"


class _MongoStore:
    name = "mongodb"

    def __init__(self, client) -> None:
        self.db = client[_mongo_database()]
        self.hits = self.db["honeypot_hits"]
        self.bans = self.db["honeypot_bans"]
        self.meta = self.db["honeypot_meta"]
        self.windows = self.db["api_windows"]
        try:
            self.hits.create_index("last_seen")
            self.windows.create_index("seen")
        except Exception:
            # A read-only account can still serve and record; the indexes only
            # keep the owner page and pruning fast.
            pass

    @staticmethod
    def _row(document: dict | None) -> dict | None:
        if not document:
            return None
        row = dict(document)
        row.pop("_id", None)
        return row

    def get_hit(self, ip: str) -> dict | None:
        return self._row(self.hits.find_one({"_id": ip}))

    def put_hit(self, ip: str, hit: dict) -> None:
        self.hits.replace_one({"_id": ip}, {**hit, "_id": ip}, upsert=True)

    def list_hits(self, limit: int) -> list[dict]:
        rows = self.hits.find({}).sort("last_seen", -1).limit(limit)
        return [row for document in rows if (row := self._row(document))]

    def count_addresses(self) -> int:
        return int(self.hits.count_documents({}))

    def total_hits(self) -> int:
        rows = list(
            self.hits.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$hits"}}}
            ])
        )
        return int(rows[0].get("total") or 0) if rows else 0

    def delete_hits_before(self, cutoff: float) -> None:
        self.hits.delete_many({"last_seen": {"$lt": cutoff}})

    def get_ban(self, ip: str) -> dict | None:
        return self._row(self.bans.find_one({"_id": ip}))

    def put_ban(self, ip: str, ban: dict) -> None:
        self.bans.replace_one({"_id": ip}, {**ban, "_id": ip}, upsert=True)

    def delete_ban(self, ip: str) -> None:
        self.bans.delete_one({"_id": ip})

    def list_bans(self) -> list[dict]:
        return [row for document in self.bans.find({}) if (row := self._row(document))]

    def get_settings(self) -> dict:
        return self._row(self.meta.find_one({"_id": "autoban"})) or {}

    def save_settings(self, settings: dict) -> None:
        self.meta.replace_one(
            {"_id": "autoban"}, {**settings, "_id": "autoban"}, upsert=True
        )

    def get_window(self, ip: str) -> dict | None:
        return self._row(self.windows.find_one({"_id": ip}))

    def put_window(self, ip: str, window: dict) -> None:
        self.windows.replace_one({"_id": ip}, {**window, "_id": ip}, upsert=True)

    def delete_windows_before(self, cutoff: float) -> None:
        self.windows.delete_many({"seen": {"$lt": cutoff}})


class _FileStore:
    """The local fallback: one JSON document in ``DATA_DIR``."""

    name = "files"

    def __init__(self) -> None:
        self.path = os.path.join(config.DATA_DIR, "honeypot_security.json")

    @staticmethod
    def _empty() -> dict:
        return {"hits": {}, "bans": {}, "settings": {}, "windows": {}}

    def _read(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, ValueError):
            document = {}
        if not isinstance(document, dict):
            document = {}
        result = self._empty()
        for key in result:
            value = document.get(key)
            if isinstance(value, dict):
                result[key] = value
        return result

    def _write(self, document: dict) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        temporary = f"{self.path}.tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(document, handle, separators=(",", ":"))
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, self.path)

    def get_hit(self, ip: str) -> dict | None:
        hit = self._read()["hits"].get(ip)
        return dict(hit) if isinstance(hit, dict) else None

    def put_hit(self, ip: str, hit: dict) -> None:
        document = self._read()
        document["hits"][ip] = dict(hit)
        self._write(document)

    def list_hits(self, limit: int) -> list[dict]:
        hits = [dict(row) for row in self._read()["hits"].values() if isinstance(row, dict)]
        hits.sort(key=lambda row: float(row.get("last_seen") or 0), reverse=True)
        return hits[:limit]

    def count_addresses(self) -> int:
        return len(self._read()["hits"])

    def total_hits(self) -> int:
        return sum(
            int(row.get("hits") or 0)
            for row in self._read()["hits"].values()
            if isinstance(row, dict)
        )

    def delete_hits_before(self, cutoff: float) -> None:
        document = self._read()
        stale = [
            ip
            for ip, row in document["hits"].items()
            if isinstance(row, dict) and float(row.get("last_seen") or 0) < cutoff
        ]
        if stale:
            for ip in stale:
                document["hits"].pop(ip, None)
            self._write(document)

    def get_ban(self, ip: str) -> dict | None:
        ban = self._read()["bans"].get(ip)
        return dict(ban) if isinstance(ban, dict) else None

    def put_ban(self, ip: str, ban: dict) -> None:
        document = self._read()
        document["bans"][ip] = dict(ban)
        self._write(document)

    def delete_ban(self, ip: str) -> None:
        document = self._read()
        if document["bans"].pop(ip, None) is not None:
            self._write(document)

    def list_bans(self) -> list[dict]:
        return [dict(row) for row in self._read()["bans"].values() if isinstance(row, dict)]

    def get_settings(self) -> dict:
        settings = self._read()["settings"]
        return dict(settings) if isinstance(settings, dict) else {}

    def save_settings(self, settings: dict) -> None:
        document = self._read()
        document["settings"] = dict(settings)
        self._write(document)

    def get_window(self, ip: str) -> dict | None:
        row = self._read()["windows"].get(ip)
        return dict(row) if isinstance(row, dict) else None

    def put_window(self, ip: str, window: dict) -> None:
        document = self._read()
        document["windows"][ip] = dict(window)
        self._write(document)

    def delete_windows_before(self, cutoff: float) -> None:
        document = self._read()
        stale = [
            ip
            for ip, row in document["windows"].items()
            if isinstance(row, dict) and float(row.get("seen") or 0) < cutoff
        ]
        if stale:
            for ip in stale:
                document["windows"].pop(ip, None)
            self._write(document)


def _connect() -> _MongoStore:
    global _CLIENT
    from pymongo import MongoClient

    _CLIENT = MongoClient(
        _mongo_url(),
        appname="niko-security",
        serverSelectionTimeoutMS=1500,
        connectTimeoutMS=1500,
        socketTimeoutMS=5000,
        maxPoolSize=5,
    )
    return _MongoStore(_CLIENT)


def _backend():
    global _BACKEND, _BACKEND_KEY
    url = _mongo_url()
    key = (url, _mongo_database() if url else "")
    with _LOCK:
        if _BACKEND is not None and _BACKEND_KEY == key:
            return _BACKEND
        _BACKEND = _connect() if url else _FileStore()
        _BACKEND_KEY = key
        return _BACKEND


def reset() -> None:
    """Drop the cached backend and state. Used after tests change ``DATA_DIR``."""
    global _BACKEND, _BACKEND_KEY, _CLIENT, _loaded, _state_at
    global _last_load_attempt, _settings, _last_error_log, _last_hit_prune
    global _last_window_prune
    with _LOCK:
        client, _CLIENT = _CLIENT, None
        _BACKEND = None
        _BACKEND_KEY = None
        _loaded = False
        _state_at = 0.0
        _last_load_attempt = 0.0
        _bans.clear()
        _settings = dict(DEFAULT_SETTINGS)
        _last_error_log = 0.0
        _last_hit_prune = 0.0
        _last_window_prune = 0.0
    if client is not None:
        try:
            client.close()
        except Exception:
            pass


def backend_name() -> str:
    return _backend().name


# ──────────────────────────────────────────────────────────────────────────────
# Addresses and settings
# ──────────────────────────────────────────────────────────────────────────────
def normalise_ip(raw: Any) -> str:
    """Canonical IPv4/IPv6 text, or ``""`` when the value is not an address."""
    value = str(raw or "").strip()
    if not value or value.lower() == "unknown":
        return ""
    if value.startswith("[") and "]" in value:
        value = value[1 : value.index("]")]
    elif value.count(":") == 1 and "." in value:
        host, _, port = value.partition(":")
        if port.isdigit():
            value = host
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return ""


def _is_public(ip: str) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )


def is_bannable(ip: str) -> bool:
    """Only external addresses may be banned.

    Loopback (``127.0.0.1``/``::1``), private ranges, link-local and reserved
    addresses belong to the deployment or the local network. Banning one would
    either lock out the owner's own traffic or have no effect on the internet,
    so both manual bans and autobans refuse them.
    """
    return _is_public(normalise_ip(ip))


def _coerce_settings(raw: dict) -> dict:
    settings = dict(DEFAULT_SETTINGS)
    for key in ("threshold", "window_seconds", "cooldown_seconds"):
        try:
            settings[key] = int(raw.get(key, settings[key]))
        except (TypeError, ValueError):
            pass
    settings["enabled"] = bool(raw.get("enabled", settings["enabled"]))
    return settings


def validate_settings(raw: dict) -> dict:
    """The autoban settings from an owner request, with bounds applied."""
    if not isinstance(raw, dict):
        raise ValueError("Send the autoban settings as a JSON object.")
    settings = _coerce_settings(raw)
    if not 2 <= settings["threshold"] <= 10000:
        raise ValueError("The threshold must be between 2 and 10,000 hits.")
    if not 30 <= settings["window_seconds"] <= 86400:
        raise ValueError("The counting window must be between 30 seconds and 24 hours.")
    if not 60 <= settings["cooldown_seconds"] <= 2592000:
        raise ValueError("The cooldown must be between 1 minute and 30 days.")
    return settings


def _expired(ban: dict, now: float) -> bool:
    expires_at = ban.get("expires_at")
    try:
        return bool(expires_at) and float(expires_at) <= now
    except (TypeError, ValueError):
        return False


def _warn(message: str, exc: Exception | None = None) -> None:
    global _last_error_log
    now = time.monotonic()
    if now - _last_error_log < 60:
        return
    _last_error_log = now
    if exc is None:
        log.warning("%s", message)
    else:
        log.warning("%s: %s", message, exc)


# ──────────────────────────────────────────────────────────────────────────────
# In-process cache of active bans and settings
# ──────────────────────────────────────────────────────────────────────────────
def _load_state(store, *, force: bool = False) -> None:
    global _loaded, _state_at, _last_load_attempt, _settings
    with _LOCK:
        now_mono = time.monotonic()
        if not force:
            if _loaded and now_mono - _state_at < _STATE_TTL_SECONDS:
                return
            if now_mono - _last_load_attempt < _RETRY_AFTER_ERROR:
                return
        _last_load_attempt = now_mono

        now = time.time()
        bans: dict[str, dict] = {}
        for row in store.list_bans():
            ip = normalise_ip(row.get("ip"))
            if not ip or _expired(row, now):
                continue
            if not _is_public(ip):
                # An old manual ban of loopback or a private address must not
                # survive a deployment: those addresses are internal and the
                # owner may be reaching the site through one of them.
                try:
                    store.delete_ban(ip)
                except Exception:
                    pass
                continue
            bans[ip] = row
        _settings = _coerce_settings(store.get_settings())
        _bans.clear()
        _bans.update(bans)
        _loaded = True
        _state_at = now_mono


def settings() -> dict:
    try:
        _load_state(_backend())
    except Exception as exc:
        _warn("Could not read the autoban settings", exc)
    return dict(_settings)


def active_ban(ip: str) -> dict | None:
    """The active ban for an address, from the cache (one database read)."""
    address = normalise_ip(ip)
    if not address or not _is_public(address):
        return None
    try:
        _load_state(_backend())
    except Exception as exc:
        _warn("Could not read the IP ban list", exc)
    with _LOCK:
        ban = _bans.get(address)
        if ban is None:
            return None
        if _expired(ban, time.time()):
            _bans.pop(address, None)
            return None
        return dict(ban)


def is_banned(ip: str) -> bool:
    return active_ban(ip) is not None


# ──────────────────────────────────────────────────────────────────────────────
# Honeypot hits and autoban
# ──────────────────────────────────────────────────────────────────────────────
def _prune_hits(store, now: float) -> None:
    global _last_hit_prune
    if now - _last_hit_prune < 3600:
        return
    _last_hit_prune = now
    try:
        store.delete_hits_before(now - HIT_RETENTION_SECONDS)
    except Exception:
        pass


def record_hit(
    *,
    ip: str,
    path: str,
    host: str = "",
    method: str = "GET",
    user_agent: str = "",
    now: float | None = None,
) -> dict:
    """Persist one honeypot hit, aggregating it under the source address.

    Returns ``{"hit": ..., "ban": ...}``. ``ban`` is set when this hit crossed
    the autoban threshold and created a ban. The hit is always written before a
    ban is considered, so the owner page can explain why the address was banned.
    """
    address = normalise_ip(ip) or "unknown"
    moment = float(now if now is not None else time.time())
    with _LOCK:
        store = _backend()
        try:
            _load_state(store)
        except Exception as exc:
            _warn("Could not read security settings while recording a hit", exc)

        stored = store.get_hit(address) or {}
        current_settings = dict(_settings)
        window_seconds = max(30, int(current_settings.get("window_seconds") or 300))
        window_start = float(stored.get("window_start") or moment)
        window_hits = int(stored.get("window_hits") or 0)
        if moment - window_start >= window_seconds:
            window_start = moment
            window_hits = 0
        window_hits += 1

        hit = {
            "ip": address,
            "hits": int(stored.get("hits") or 0) + 1,
            "first_seen": float(stored.get("first_seen") or moment),
            "last_seen": moment,
            "last_path": str(path or "")[:_MAX_PATH],
            "last_host": str(host or "")[:_MAX_HOST],
            "last_method": str(method or "GET")[:16].upper(),
            "last_user_agent": str(user_agent or "")[:_MAX_USER_AGENT],
            "window_start": window_start,
            "window_hits": window_hits,
        }
        store.put_hit(address, hit)
        _prune_hits(store, moment)

        created = None
        if (
            current_settings.get("enabled")
            and is_bannable(address)
            and window_hits >= int(current_settings.get("threshold") or 0)
        ):
            existing = store.get_ban(address)
            if existing is None or _expired(existing, moment):
                created = {
                    "ip": address,
                    "reason": (
                        f"Autoban: {window_hits} honeypot hits in "
                        f"{window_seconds} seconds."
                    ),
                    "created_at": moment,
                    "created_by": "autoban",
                    "expires_at": moment
                    + max(60, int(current_settings.get("cooldown_seconds") or 86400)),
                    "source": "autoban",
                }
                store.put_ban(address, created)
                _bans[address] = created
        return {"hit": hit, "ban": created}


def ban_ip(
    ip: str,
    *,
    reason: str = "",
    actor: str = "",
    source: str = "manual",
    expires_at: float | None = None,
) -> dict:
    """Ban an address in the database and make it effective immediately."""
    address = normalise_ip(ip)
    if not address:
        raise ValueError("Enter a valid IPv4 or IPv6 address.")
    if not _is_public(address):
        raise ValueError("Loopback and internal addresses cannot be banned.")
    now = time.time()
    ban = {
        "ip": address,
        "reason": str(reason or "").strip()[:_MAX_REASON] or "Banned by the owner.",
        "created_at": now,
        "created_by": str(actor or "")[:_MAX_ACTOR] or "owner",
        "expires_at": expires_at,
        "source": source,
    }
    with _LOCK:
        _backend().put_ban(address, ban)
        _bans[address] = ban
    return ban


def unban_ip(ip: str) -> bool:
    address = normalise_ip(ip)
    if not address:
        raise ValueError("Enter a valid IPv4 or IPv6 address.")
    # Removing a stale internal-IP ban is always allowed; only creating one is
    # refused. This lets an old row be cleaned up through the same endpoint.
    with _LOCK:
        _backend().delete_ban(address)
        _bans.pop(address, None)
    return True


def update_settings(raw: dict) -> dict:
    settings = validate_settings(raw)
    with _LOCK:
        _backend().save_settings(settings)
        global _settings, _state_at
        _settings = dict(settings)
        _state_at = time.monotonic()
    return dict(settings)


def snapshot(limit: int = 250) -> dict:
    """The owner page payload: hits, active bans, and the guard settings."""
    limit = max(1, min(int(limit or 250), MAX_HITS_PER_PAGE))
    try:
        store = _backend()
        _load_state(store, force=True)
        hits = store.list_hits(limit)
        now = time.time()
        with _LOCK:
            for address, ban in list(_bans.items()):
                if _expired(ban, now):
                    _bans.pop(address, None)
                    try:
                        store.delete_ban(address)
                    except Exception:
                        pass
            bans = [dict(row) for row in _bans.values()]
            current_settings = dict(_settings)
        banned = {row["ip"] for row in bans}
        for hit in hits:
            hit["bannable"] = is_bannable(hit.get("ip") or "")
            hit["banned"] = hit.get("ip") in banned
            hit["ban"] = next(
                (row for row in bans if row.get("ip") == hit.get("ip")), None
            )
        bans.sort(key=lambda row: float(row.get("created_at") or 0), reverse=True)
        return {
            "hits": hits,
            "bans": bans,
            "settings": current_settings,
            "totals": {
                "hits": store.total_hits(),
                "addresses": store.count_addresses(),
                "bans": len(bans),
            },
            "storage": store.name,
            "error": None,
        }
    except Exception as exc:
        _warn("Could not read the honeypot security store", exc)
        return {
            "hits": [],
            "bans": [],
            "settings": dict(_settings),
            "totals": {"hits": 0, "addresses": 0, "bans": 0},
            "storage": "unavailable",
            "error": "The security store could not be read.",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Developer API rate windows
# ──────────────────────────────────────────────────────────────────────────────
def api_rate_limit(ip: str, *, limit: int, window: float) -> dict:
    """Consume one slot in an address's fixed window, stored in the database.

    The API used to keep a deque of every request timestamp for every address.
    A crawler rotating addresses grew that map; this keeps one counter row per
    address, and a failure to reach the store fails open so a database outage
    does not take the whole API down.
    """
    global _last_window_prune
    address = normalise_ip(ip) or "unknown"
    now = time.time()
    try:
        with _LOCK:
            store = _backend()
            row = store.get_window(address) or {}
            start = float(row.get("start") or now)
            hits = int(row.get("hits") or 0)
            if now - start >= window:
                start = now
                hits = 0
            if hits >= limit:
                retry_after = max(1, int(ceil((start + window) - now)))
                return {
                    "limit": limit,
                    "remaining": 0,
                    "reset": int(now) + retry_after,
                    "retry_after": retry_after,
                    "blocked": True,
                }
            hits += 1
            store.put_window(address, {"start": start, "hits": hits, "seen": now})
            if now - _last_window_prune >= 3600:
                _last_window_prune = now
                try:
                    store.delete_windows_before(now - _WINDOW_RETENTION_SECONDS)
                except Exception:
                    pass
            resets_in = max(1, int(ceil((start + window) - now)))
            return {
                "limit": limit,
                "remaining": max(0, limit - hits),
                "reset": int(now) + resets_in,
                "retry_after": None,
                "blocked": False,
            }
    except Exception as exc:
        _warn("Could not record an API rate window", exc)
        return {
            "limit": limit,
            "remaining": max(0, limit - 1),
            "reset": int(now + window),
            "retry_after": None,
            "blocked": False,
        }
