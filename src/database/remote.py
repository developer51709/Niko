"""Client handle on the supervised database child.

The database lives in its own process (``src/db_child.py``) so a bot restart
never closes the pool and the dashboard never needs one.  This module is what
the bot process attaches to ``bot.cxn``: it speaks the same pool API the call
sites already use, over a token-authenticated loopback connection.

Two APIs are exposed:

* The legacy SQL surface (``execute``/``fetch``/``fetchrow``/``fetchval``/
  ``fetchone``).  It keeps working on SQLite and MongoDB exactly as it did
  in-process, which is what the deprecation window requires.
* A JSON document surface (:meth:`RemotePool.documents`) for new code that
  wants documents rather than SQL strings.  It requires MongoDB; on SQLite the
  legacy SQL API remains available until SQLite support is removed.

``collection()`` is kept for the handful of modules that use native Mongo
helpers, and returns a proxy with the small motor subset they need.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import aiohttp

from database import Row

#: The supervisor's per-run loopback credential.  Only supervised children get
#: it, and the database child refuses every request without it.
TOKEN_ENV = "NIKO_INTERNAL_TOKEN"
TOKEN_HEADER = "X-Internal-Token"

#: Startup hint for the database child's loopback port.
PORT_ENV = "NIKO_DB_API_PORT"

#: How long a single database call may take before the child is considered
#: unreachable.  Reads and writes are local; anything slower is a stall.
REQUEST_TIMEOUT = 120.0


class DatabaseUnavailable(RuntimeError):
    """The database child could not be reached."""


class DatabaseRequestError(RuntimeError):
    """The database child answered with an error."""


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, (set, frozenset)):
        return list(value)
    return str(value)


class DatabaseRoute:
    """Where the database child listens, asked cheaply and cached.

    The supervisor knows the port because the child reports it when it binds,
    so this asks over the local control socket instead of guessing.  A failed
    call drops the cache: a restarted child has a new port.
    """

    def __init__(self, env_port: int | None = None) -> None:
        self._port = env_port
        self._at = time.monotonic() if env_port else 0.0
        self._env_used = env_port is not None

    def invalidate(self) -> None:
        self._port = None
        self._at = 0.0

    def port(self) -> int | None:
        now = time.monotonic()
        if self._port is not None and now - self._at < 1.0:
            return self._port
        env_port = (os.environ.get(PORT_ENV) or "").strip()
        if env_port.isdigit() and not self._env_used:
            self._port = int(env_port)
            self._env_used = True
            self._at = now
            return self._port
        try:
            from utils import supervisor_control

            response = supervisor_control.request("route", timeout=2.0)
        except Exception:
            return None
        port = response.get("db_api_port") if isinstance(response, dict) else None
        if isinstance(port, int) and 1 <= port <= 65535:
            self._port = port
            self._at = now
            return port
        return None


class RemotePool:
    """The bot-side pool API, backed by the database child."""

    def __init__(
        self,
        route: DatabaseRoute,
        token: str,
        backend: str,
        *,
        database_name: str | None = None,
        root: "RemotePool | None" = None,
    ) -> None:
        self._route = route
        self._token = token
        self.db_type = backend
        self._database = database_name
        self._root = root or self
        self._session: aiohttp.ClientSession | None = None
        self._client = RemoteClient(self)

    # ── transport ──────────────────────────────────────────────────────
    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    total=REQUEST_TIMEOUT, connect=3.0, sock_read=REQUEST_TIMEOUT
                )
            )
        return self._session

    async def _call(self, method: str, path: str, payload: dict | None) -> dict:
        root = self._root
        body = None
        headers = {TOKEN_HEADER: self._token}
        if payload is not None:
            body = json.dumps(payload, default=_json_default).encode("utf-8")
            headers["Content-Type"] = "application/json"
        # A restarted database child has a new port, so a connection that was
        # refused (nothing was sent) is retried once with a fresh route.
        last_error: Exception | None = None
        for attempt in range(2):
            port = self._route.port()
            if port is None:
                last_error = DatabaseUnavailable(
                    "the database child is not listening"
                )
                if attempt:
                    break
                await asyncio.sleep(0.05)
                continue
            url = f"http://127.0.0.1:{port}{path}"
            try:
                async with root._ensure_session().request(
                    method, url, data=body, headers=headers
                ) as response:
                    data = await response.json(content_type=None)
            except aiohttp.ClientConnectorError as exc:
                # Nothing was sent: the cached port is stale after a child
                # replacement, so resolving the route again is safe.
                last_error = DatabaseUnavailable(
                    f"the database child is not accepting connections: {exc}"
                )
                self._route.invalidate()
                continue
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as exc:
                # The request may have reached the child; retrying a write here
                # could apply it twice, so report the failure instead.
                self._route.invalidate()
                raise DatabaseUnavailable(
                    f"the database child did not answer: {type(exc).__name__}: {exc}"
                ) from exc
            if not isinstance(data, dict):
                raise DatabaseRequestError(
                    "the database child returned an invalid response"
                )
            if response.status != 200 or not data.get("ok"):
                raise DatabaseRequestError(
                    str(data.get("error") or f"database request failed ({response.status})")
                )
            data.pop("ok", None)
            return data
        raise last_error or DatabaseUnavailable("the database child is not reachable")

    async def _request(self, path: str, payload: dict | None) -> dict:
        if self._database:
            payload = {**(payload or {}), "database": self._database}
        return await self._call("POST", path, payload)

    # ── legacy SQL surface ─────────────────────────────────────────────
    async def _sql(self, op: str, query: str, args: tuple) -> dict:
        return await self._request(
            "/db/query", {"op": op, "query": query, "args": list(args)}
        )

    async def execute(self, query: str, *args) -> None:
        await self._sql("execute", query, args)

    async def fetch(self, query: str, *args) -> list[Row]:
        data = await self._sql("fetch", query, args)
        return [Row(row) for row in data.get("rows") or ()]

    async def fetchrow(self, query: str, *args) -> Row | None:
        data = await self._sql("fetchrow", query, args)
        row = data.get("row")
        return Row(row) if isinstance(row, dict) else None

    async def fetchone(self, query: str, *args) -> Row | None:
        return await self.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        data = await self._sql("fetchval", query, args)
        return data.get("value")

    async def ping(self) -> dict:
        data = await self._call("GET", "/db/health", None)
        return {"ok": True, "backend": data.get("backend")}

    async def close(self) -> None:
        session = self._root._session
        self._root._session = None
        if session is not None and not session.closed:
            await session.close()

    # ── native document helpers ────────────────────────────────────────
    def collection(self, name: str) -> "RemoteCollection":
        if self.db_type != "mongodb":
            raise RuntimeError(
                f"direct collection access requires MongoDB (this pool uses {self.db_type})"
            )
        return RemoteCollection(self, name)

    def database(self, name: str) -> "RemotePool":
        """A pool for another database on the same backend and child."""
        if self.db_type != "mongodb":
            raise RuntimeError(
                f"named databases require MongoDB (this pool uses {self.db_type})"
            )
        return RemotePool(
            self._route,
            self._token,
            self.db_type,
            database_name=name,
            root=self._root,
        )

    def documents(self, name: str) -> "RemoteDocuments":
        return RemoteDocuments(self, name)

    @property
    def client(self) -> "RemoteClient":
        return self._client


class RemoteClient:
    """Stand-in for the motor client, for clients that only want a ping."""

    def __init__(self, pool: RemotePool) -> None:
        self._pool = pool
        self.admin = RemoteAdmin(pool)


class RemoteAdmin:
    def __init__(self, pool: RemotePool) -> None:
        self._pool = pool

    async def command(self, name: str, *args, **kwargs):
        if str(name).lower() != "ping":
            raise DatabaseRequestError(
                f"the database child does not expose admin command {name!r}"
            )
        return await self._pool.ping()


@dataclass
class WriteResult:
    """The pymongo result fields the codebase reads."""

    acknowledged: bool = True
    inserted_id: Any = None
    matched_count: int = 0
    modified_count: int = 0
    upserted_id: Any = None
    deleted_count: int = 0


class RemoteCursor:
    def __init__(
        self,
        collection: "RemoteCollection",
        filter_doc: dict | None,
        projection: Any = None,
    ) -> None:
        self._collection = collection
        self._filter = filter_doc or {}
        self._projection = projection
        self._sort: list[list[Any]] = []
        self._limit: int | None = None
        self._skip: int | None = None
        self._docs: list[dict] | None = None

    def sort(self, key_or_list, direction: int | None = None) -> "RemoteCursor":
        if isinstance(key_or_list, str):
            self._sort.append([key_or_list, 1 if direction is None else int(direction)])
        else:
            for key, order in key_or_list:
                self._sort.append([key, int(order)])
        return self

    def limit(self, count: int) -> "RemoteCursor":
        self._limit = int(count)
        return self

    def skip(self, count: int) -> "RemoteCursor":
        self._skip = int(count)
        return self

    async def to_list(self, length: int | None = None) -> list[dict]:
        options: dict[str, Any] = {}
        if self._sort:
            options["sort"] = self._sort
        if self._limit is not None:
            options["limit"] = self._limit
        if self._skip is not None:
            options["skip"] = self._skip
        data = await self._collection._op(
            "find", [self._filter, self._projection, options]
        )
        return list(data.get("documents") or ())

    def __aiter__(self) -> "RemoteCursor":
        return self

    async def __anext__(self) -> dict:
        if self._docs is None:
            self._docs = await self.to_list()
        if not self._docs:
            raise StopAsyncIteration
        return self._docs.pop(0)


class RemoteCollection:
    """The subset of a motor collection this codebase uses."""

    def __init__(self, pool: RemotePool, name: str) -> None:
        self._pool = pool
        self._name = name

    async def _op(self, op: str, args: list) -> dict:
        return await self._pool._request(
            "/db/collection",
            {"collection": self._name, "op": op, "args": args},
        )

    def find(self, filter_doc: dict | None = None, projection: Any = None) -> RemoteCursor:
        return RemoteCursor(self, filter_doc, projection)

    async def find_one(self, filter_doc: dict | None = None, projection: Any = None):
        data = await self._op("find_one", [filter_doc or {}, projection])
        document = data.get("document")
        return document if isinstance(document, dict) else None

    async def insert_one(self, document: dict) -> WriteResult:
        data = await self._op("insert_one", [document])
        return WriteResult(inserted_id=data.get("inserted_id"))

    async def replace_one(
        self, filter_doc: dict, replacement: dict, upsert: bool = False
    ) -> WriteResult:
        data = await self._op("replace_one", [filter_doc, replacement, bool(upsert)])
        return WriteResult(
            matched_count=int(data.get("matched_count") or 0),
            modified_count=int(data.get("modified_count") or 0),
            upserted_id=data.get("upserted_id"),
        )

    async def update_one(
        self, filter_doc: dict, update: dict, upsert: bool = False
    ) -> WriteResult:
        data = await self._op("update_one", [filter_doc, update, bool(upsert)])
        return WriteResult(
            matched_count=int(data.get("matched_count") or 0),
            modified_count=int(data.get("modified_count") or 0),
            upserted_id=data.get("upserted_id"),
        )

    async def delete_one(self, filter_doc: dict) -> WriteResult:
        data = await self._op("delete_one", [filter_doc])
        return WriteResult(deleted_count=int(data.get("deleted_count") or 0))

    async def delete_many(self, filter_doc: dict) -> WriteResult:
        data = await self._op("delete_many", [filter_doc])
        return WriteResult(deleted_count=int(data.get("deleted_count") or 0))

    async def count_documents(self, filter_doc: dict) -> int:
        data = await self._op("count_documents", [filter_doc])
        return int(data.get("count") or 0)

    async def create_index(self, keys, **options) -> str:
        data = await self._op("create_index", [keys, options])
        return str(data.get("name") or "")


class RemoteDocuments:
    """JSON document reads and writes for one collection.

    This is the modern surface: callers pass and receive plain JSON documents
    instead of SQL.  It is MongoDB-backed, because the document API is the
    replacement for the SQL translation layer.
    """

    def __init__(self, pool: RemotePool, name: str) -> None:
        self._pool = pool
        self._name = name

    async def _call(self, action: str, payload: dict) -> dict:
        payload = {"collection": self._name, **payload}
        return await self._pool._request(f"/db/json/{action}", payload)

    async def read(
        self,
        filter_doc: dict | None = None,
        *,
        projection: Any = None,
        sort: list | None = None,
        limit: int | None = None,
        skip: int | None = None,
    ) -> list[dict]:
        payload: dict[str, Any] = {"filter": filter_doc or {}}
        if projection is not None:
            payload["projection"] = projection
        if sort:
            payload["sort"] = sort
        if limit is not None:
            payload["limit"] = int(limit)
        if skip is not None:
            payload["skip"] = int(skip)
        data = await self._call("read", payload)
        return list(data.get("documents") or ())

    async def read_one(
        self, filter_doc: dict, projection: Any = None
    ) -> dict | None:
        payload: dict[str, Any] = {"filter": filter_doc or {}}
        if projection is not None:
            payload["projection"] = projection
        data = await self._call("read_one", payload)
        document = data.get("document")
        return document if isinstance(document, dict) else None

    async def write(
        self, document: dict, *, key: str | None = None
    ) -> dict:
        """Create or replace one document, keyed by ``_id`` or ``document[key]``."""
        payload: dict[str, Any] = {"document": document}
        if key:
            payload["key"] = key
        return await self._call("write", payload)

    async def update(
        self, filter_doc: dict, update: dict, *, upsert: bool = False
    ) -> dict:
        return await self._call(
            "update",
            {"filter": filter_doc or {}, "update": update, "upsert": bool(upsert)},
        )

    async def delete(self, filter_doc: dict, *, many: bool = False) -> int:
        data = await self._call(
            "delete", {"filter": filter_doc or {}, "many": bool(many)}
        )
        return int(data.get("deleted_count") or 0)

    async def count(self, filter_doc: dict | None = None) -> int:
        data = await self._call("count", {"filter": filter_doc or {}})
        return int(data.get("count") or 0)


async def connect_remote_pool(
    *,
    attempts: int = 60,
    delay: float = 0.5,
) -> RemotePool:
    """Attach to the database child, waiting for it to finish its own start.

    The child connects to MongoDB (with its own retries) before it reports
    ready, so a bot child that boots first waits here instead of failing its
    readiness check and being restarted against a database that is still
    coming up.
    """
    token = (os.environ.get(TOKEN_ENV) or "").strip()
    if not token:
        raise DatabaseUnavailable(
            f"{TOKEN_ENV} is not set; the bot child cannot authenticate to the database child"
        )
    env_port = (os.environ.get(PORT_ENV) or "").strip()
    route = DatabaseRoute(int(env_port) if env_port.isdigit() else None)
    last_error: Exception | None = None
    probe = RemotePool(route, token, "unknown")
    try:
        for _ in range(max(1, attempts)):
            try:
                health = await probe.ping()
            except (DatabaseUnavailable, DatabaseRequestError) as exc:
                last_error = exc
                route.invalidate()
                await asyncio.sleep(delay)
                continue
            backend = str(health.get("backend") or "")
            if not backend:
                last_error = DatabaseRequestError(
                    "the database child did not report a backend"
                )
                await asyncio.sleep(delay)
                continue
            return RemotePool(route, token, backend)
    finally:
        await probe.close()
    raise DatabaseUnavailable(
        f"the database child did not become reachable: {type(last_error).__name__}: {last_error}"
    )
