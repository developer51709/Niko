"""Persistence for the developer portal.

The portal used to keep everything in JSON files under ``data/``: the access
roster, API keys, the usage log, appeals, reviewed applications, verification
screenshots, and the pepper that key hashes are mixed with. Production runs
without a persistent disk, so every one of those disappeared on the next
deploy — and a new pepper silently invalidated every issued key.

With ``MONGODB_URL`` configured, this module stores the same data in MongoDB,
in its own database beside the bot's (default ``<MONGODB_DATABASE>_developer_portal``,
e.g. ``discord_bot_developer_portal``). The music and error-report stores do the
same thing, which keeps the portal's collections out of the primary database.
Without ``MONGODB_URL`` the historical files are used, so local development and
the test suite need no server. The first MongoDB read imports the files it
finds: a deployment that upgrades keeps the grants, keys and screenshots it
already had.

The web application is synchronous, so this talks to MongoDB through the
synchronous driver that ``motor`` already depends on, instead of scheduling
every portal call onto the bot's event loop.
"""

from __future__ import annotations

import json
import os
import secrets
import threading
import time

from utils import logging

from .. import config

#: The only documents the portal persists wholesale. The values are the file
#: names used before MongoDB, which are still read for the one-time import.
_DOCUMENT_FILES = {
    "portal": "developer_portal.json",
    "applications": "developer_applications.json",
}

_DOCUMENT_ID = "document"
_PEPPER_ID = "api_key_pepper"
_SECRET_FILE = "developer_api_secret"
_SCREENSHOT_DIR = "developer_application_screenshots"

#: Content type → file extension for the local backend. The bytes themselves
#: are already checked by ``applications.detect_image_type``.
_IMAGE_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}

#: Cross-process writes are rare (the bot child owns the portal), so a short
#: cache is enough to keep a burst of requests from reading the same document
#: once per call while still noticing another process's change quickly.
_MONGO_CACHE_TTL = 1.0

_LOCK = threading.RLock()
_BACKEND = None
_BACKEND_KEY: tuple[str, str] | None = None
_CLIENT = None
_MONGO_CACHE: dict[str, tuple[float, dict]] = {}
_FILE_CACHE: dict[str, tuple[tuple[int, int] | None, dict]] = {}
_PEPPER_CACHE: bytes | None = None
_logged_database: str | None = None


def _mongo_url() -> str:
    return (os.environ.get("MONGODB_URL") or "").strip()


def _mongo_database() -> str:
    base = (os.environ.get("MONGODB_DATABASE") or "").strip() or "discord_bot"
    return f"{base}_developer_portal"


class _FileBackend:
    """The historical JSON files; used when MongoDB is not configured."""

    name = "files"

    def _document_path(self, kind: str) -> str:
        return os.path.join(config.DATA_DIR, _DOCUMENT_FILES[kind])

    def load_document(self, kind: str) -> dict:
        path = self._document_path(kind)
        try:
            stat = os.stat(path)
            stamp: tuple[int, int] | None = (stat.st_mtime_ns, stat.st_size)
        except OSError:
            stamp = None
        with _LOCK:
            cached = _FILE_CACHE.get(kind)
            # The first call must load even when the file does not exist yet.
            if cached is not None and cached[0] == stamp:
                return cached[1]
        document: dict = {}
        if stamp is not None:
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    document = loaded
            except (OSError, ValueError):
                document = {}
        with _LOCK:
            _FILE_CACHE[kind] = (stamp, document)
        return document

    def save_document(self, kind: str, document: dict) -> None:
        path = self._document_path(kind)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temporary = f"{path}.tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2)
        os.replace(temporary, path)
        if kind == "applications":
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
        try:
            stat = os.stat(path)
            stamp: tuple[int, int] | None = (stat.st_mtime_ns, stat.st_size)
        except OSError:
            stamp = None
        with _LOCK:
            _FILE_CACHE[kind] = (stamp, document)

    def load_secret(self) -> bytes | None:
        path = os.path.join(config.DATA_DIR, _SECRET_FILE)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                value = handle.read().strip()
        except OSError:
            return None
        return value.encode("utf-8") if value else None

    def save_secret(self, value: bytes) -> bytes:
        """Create the pepper file, or return the one another process created."""
        path = os.path.join(config.DATA_DIR, _SECRET_FILE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            with open(path, "r", encoding="utf-8") as handle:
                existing = handle.read().strip()
            if existing:
                return existing.encode("utf-8")
            # An empty leftover cannot hash anything; fill it in instead of
            # returning an empty pepper that every key would share.
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(value.decode("utf-8"))
            return value
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value.decode("utf-8"))
        return value

    def save_screenshot(self, application_id: str, raw: bytes, content_type: str) -> dict:
        extension = _IMAGE_EXTENSIONS[content_type]
        directory = os.path.join(config.DATA_DIR, _SCREENSHOT_DIR)
        os.makedirs(directory, exist_ok=True)
        for name in os.listdir(directory):
            if name.startswith(f"{application_id}."):
                try:
                    os.remove(os.path.join(directory, name))
                except OSError:
                    pass
        filename = f"{application_id}.{extension}"
        path = os.path.join(directory, filename)
        with open(path, "wb") as handle:
            handle.write(raw)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        return {
            "path": os.path.join(_SCREENSHOT_DIR, filename),
            "content_type": content_type,
            "size": len(raw),
            "uploaded_at": time.time(),
        }

    def load_screenshot(self, application_id: str) -> tuple[bytes, str] | None:
        directory = os.path.join(config.DATA_DIR, _SCREENSHOT_DIR)
        for content_type, extension in _IMAGE_EXTENSIONS.items():
            path = os.path.join(directory, f"{application_id}.{extension}")
            try:
                with open(path, "rb") as handle:
                    return handle.read(), content_type
            except OSError:
                continue
        return None

    def delete_screenshot(self, application_id: str) -> None:
        directory = os.path.join(config.DATA_DIR, _SCREENSHOT_DIR)
        if not os.path.isdir(directory):
            return
        for name in os.listdir(directory):
            if name.startswith(f"{application_id}."):
                try:
                    os.remove(os.path.join(directory, name))
                except OSError:
                    pass


class _MongoBackend:
    """The portal's own database, separate from the bot's primary database."""

    name = "mongodb"

    def __init__(self, client, database: str) -> None:
        global _logged_database
        self.database = database
        self.db = client[database]
        self.documents = self.db["portal"]
        self.applications = self.db["applications"]
        self.screenshots = self.db["screenshots"]
        self.meta = self.db["meta"]
        if _logged_database != database:
            _logged_database = database
            logging.success(
                "DeveloperAPI",
                f"Developer portal database ready ({database}).",
            )

    def _collection(self, kind: str):
        return self.documents if kind == "portal" else self.applications

    def load_document(self, kind: str) -> dict:
        collection = self._collection(kind)
        row = collection.find_one({"_id": _DOCUMENT_ID})
        if row is None:
            document = _read_legacy_document(kind)
            self._write_document(collection, document)
            if kind == "applications":
                self._import_legacy_screenshots(document)
            return document
        document = row.get(_DOCUMENT_ID)
        return document if isinstance(document, dict) else {}

    def _write_document(self, collection, document: dict) -> None:
        collection.replace_one(
            {"_id": _DOCUMENT_ID},
            {"_id": _DOCUMENT_ID, _DOCUMENT_ID: document},
            upsert=True,
        )

    def save_document(self, kind: str, document: dict) -> None:
        self._write_document(self._collection(kind), document)

    def _import_legacy_screenshots(self, document: dict) -> None:
        """Copy the screenshots the old JSON store referenced into MongoDB."""
        applications = document.get("applications")
        if not isinstance(applications, dict):
            return
        for application_id, application in applications.items():
            if not isinstance(application, dict):
                continue
            shot = application.get("screenshot")
            if not isinstance(shot, dict) or not shot.get("path"):
                continue
            path = os.path.join(config.DATA_DIR, str(shot["path"]))
            try:
                with open(path, "rb") as handle:
                    raw = handle.read()
            except OSError:
                continue
            self._save_screenshot(
                str(application_id),
                raw,
                str(shot.get("content_type") or "image/png"),
                shot.get("uploaded_at"),
            )

    def load_secret(self) -> bytes | None:
        row = self.meta.find_one({"_id": _PEPPER_ID})
        if row is None:
            legacy = _FileBackend().load_secret()
            if legacy:
                return self.save_secret(legacy)
            return None
        value = str(row.get("value") or "").strip()
        return value.encode("utf-8") if value else None

    def save_secret(self, value: bytes) -> bytes:
        # ``$setOnInsert`` makes the first process to get here win; every other
        # one reads that value back instead of writing its own pepper.
        self.meta.update_one(
            {"_id": _PEPPER_ID},
            {"$setOnInsert": {"value": value.decode("utf-8")}},
            upsert=True,
        )
        row = self.meta.find_one({"_id": _PEPPER_ID}) or {}
        return str(row.get("value") or value.decode("utf-8")).encode("utf-8")

    def _save_screenshot(
        self,
        application_id: str,
        raw: bytes,
        content_type: str,
        uploaded_at: float | None = None,
    ) -> dict:
        from bson.binary import Binary

        uploaded = float(uploaded_at or time.time())
        self.screenshots.replace_one(
            {"_id": application_id},
            {
                "_id": application_id,
                "content_type": content_type,
                "size": len(raw),
                "uploaded_at": uploaded,
                "data": Binary(raw),
            },
            upsert=True,
        )
        return {
            "content_type": content_type,
            "size": len(raw),
            "uploaded_at": uploaded,
        }

    def save_screenshot(self, application_id: str, raw: bytes, content_type: str) -> dict:
        return self._save_screenshot(application_id, raw, content_type)

    def load_screenshot(self, application_id: str) -> tuple[bytes, str] | None:
        row = self.screenshots.find_one({"_id": application_id})
        if row is None:
            return None
        data = row.get("data")
        if not data:
            return None
        return bytes(data), str(row.get("content_type") or "application/octet-stream")

    def delete_screenshot(self, application_id: str) -> None:
        self.screenshots.delete_one({"_id": application_id})


def _read_legacy_document(kind: str) -> dict:
    path = os.path.join(config.DATA_DIR, _DOCUMENT_FILES[kind])
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return {}
    return document if isinstance(document, dict) else {}


def _connect() -> _MongoBackend:
    global _CLIENT
    from pymongo import MongoClient

    database = _mongo_database()
    _CLIENT = MongoClient(
        _mongo_url(),
        appname="niko-developer-portal",
        # A portal request should answer quickly even while MongoDB is
        # unreachable; failing loudly is better than serving a stale empty
        # roster that would reject every key.
        serverSelectionTimeoutMS=1500,
        connectTimeoutMS=1500,
        socketTimeoutMS=5000,
        maxPoolSize=5,
    )
    return _MongoBackend(_CLIENT, database)


def _backend():
    global _BACKEND, _BACKEND_KEY
    url = _mongo_url()
    key = (url, _mongo_database() if url else "")
    with _LOCK:
        if _BACKEND is not None and _BACKEND_KEY == key:
            return _BACKEND
        # Constructing a client does not connect yet, so holding the lock here
        # costs nothing and stops two first requests from opening two clients.
        _BACKEND = _connect() if url else _FileBackend()
        _BACKEND_KEY = key
        return _BACKEND


def reset() -> None:
    """Drop the cached backend, documents, pepper, and client."""
    global _BACKEND, _BACKEND_KEY, _CLIENT, _PEPPER_CACHE
    with _LOCK:
        _BACKEND = None
        _BACKEND_KEY = None
        _MONGO_CACHE.clear()
        _FILE_CACHE.clear()
        _PEPPER_CACHE = None
        client, _CLIENT = _CLIENT, None
    if client is not None:
        try:
            client.close()
        except Exception:
            pass


def backend_name() -> str:
    return _backend().name


def load_document(kind: str) -> dict:
    if kind not in _DOCUMENT_FILES:
        raise ValueError(f"unknown developer portal document: {kind!r}")
    backend = _backend()
    if backend.name == "mongodb":
        with _LOCK:
            cached = _MONGO_CACHE.get(kind)
            if cached is not None and time.monotonic() - cached[0] < _MONGO_CACHE_TTL:
                return cached[1]
    document = backend.load_document(kind)
    if backend.name == "mongodb":
        with _LOCK:
            _MONGO_CACHE[kind] = (time.monotonic(), document)
    return document


def save_document(kind: str, document: dict) -> None:
    if kind not in _DOCUMENT_FILES:
        raise ValueError(f"unknown developer portal document: {kind!r}")
    backend = _backend()
    backend.save_document(kind, document)
    if backend.name == "mongodb":
        with _LOCK:
            _MONGO_CACHE[kind] = (time.monotonic(), document)


def key_pepper() -> bytes:
    """The stable secret mixed into key hashes.

    An environment variable wins so a deployment can manage it like the other
    application secrets. Otherwise the value is generated once and stored
    beside the portal data, so restarting on a host without a persistent disk
    no longer invalidates every issued key.
    """
    global _PEPPER_CACHE
    configured = (os.environ.get("DEVELOPER_API_KEY_PEPPER") or "").strip()
    if configured:
        return configured.encode("utf-8")
    with _LOCK:
        if _PEPPER_CACHE is not None:
            return _PEPPER_CACHE
    backend = _backend()
    stored = backend.load_secret()
    if not stored:
        stored = backend.save_secret(secrets.token_urlsafe(48).encode("utf-8"))
    with _LOCK:
        _PEPPER_CACHE = stored
    return stored


def save_screenshot(application_id: str, raw: bytes, content_type: str) -> dict:
    return _backend().save_screenshot(application_id, raw, content_type)


def load_screenshot(application_id: str) -> tuple[bytes, str] | None:
    return _backend().load_screenshot(application_id)


def delete_screenshot(application_id: str) -> None:
    _backend().delete_screenshot(application_id)
