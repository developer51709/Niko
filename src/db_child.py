"""Database child: the one process that owns the database pool.

The dashboard and the bot are separate children; the database is now one too.
That keeps a bot restart from closing the pool, keeps the dashboard free of
database imports, and gives every database call one owner that can be
supervised, restarted, and inspected independently.

The child serves a token-authenticated loopback HTTP API, in two layers:

* **JSON documents** (``/db/json/*``) — the modern surface.  Each call reads or
  writes plain JSON documents in a collection, with no SQL string involved.
* **Legacy SQL** (``/db/query``) — ``execute``/``fetch``/``fetchrow``/
  ``fetchval``/``fetchone``, unchanged.  The SQLite backend is deprecated and
  scheduled for removal between December 1 and December 10, 2026, but callers
  keep working through this layer until then.

``/db/collection`` is the small native-motor subset (find/find_one/insert_one/
…) that a few modules use directly.  It lives beside the document API because
both are the same operations on the same collection.

Only the supervisor starts this process, and only the bot child talks to it:
the credential is the supervisor's per-run ``NIKO_INTERNAL_TOKEN``, and the
server binds an ephemeral loopback port.  The port is reported to the
supervisor in the ``api_listening`` event.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import hmac
import json
import os
import signal
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aiohttp import web  # noqa: E402

from utils import logging as bot_logging  # noqa: E402  (installs the console)
import database  # noqa: E402
from database import MongoPool  # noqa: E402

DATABASE_PATH = "data/database.db"
TOKEN_ENV = "NIKO_INTERNAL_TOKEN"
TOKEN_HEADER = "X-Internal-Token"

#: Broadcast media and transcripts are stored as text beside their row, so a
#: single write can be tens of megabytes.  The default aiohttp body limit of
#: 1 MiB would reject them.
MAX_BODY_BYTES = 64 * 1024 * 1024

SQL_OPS = ("execute", "fetch", "fetchrow", "fetchval", "fetchone")

POOL = web.AppKey("pool")
TOKEN = web.AppKey("token")
BASE_DATABASE = web.AppKey("base_database")
NAMED_POOLS = web.AppKey("named_pools")
STARTED_AT = web.AppKey("started_at")


class UnsupportedOperation(RuntimeError):
    """The request needs a backend or feature this child does not provide."""


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, (set, frozenset)):
        return list(value)
    return str(value)


def _response(payload: dict, status: int = 200) -> web.Response:
    body = json.dumps({"ok": True, **payload}, default=_json_default)
    return web.Response(
        text=body, status=status, content_type="application/json"
    )


def _error(message: str, status: int = 400) -> web.Response:
    return web.json_response({"ok": False, "error": message}, status=status)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _base_database() -> str:
    return os.getenv("MONGODB_DATABASE", "discord_bot")


def _pool_for(app: web.Application, name: str | None):
    """Resolve a database name to a pool, refusing unrelated databases."""
    pool = app[POOL]
    base = app[BASE_DATABASE]
    if not name or name == base:
        return pool
    _require(
        name.startswith(base + "_"),
        f"database {name!r} is not managed by this child",
    )
    if getattr(pool, "db_type", None) != "mongodb":
        raise UnsupportedOperation(
            "named databases require MongoDB; the legacy SQL API is still "
            f"available on {getattr(pool, 'db_type', 'unknown')}"
        )
    cache: dict[str, MongoPool] = app[NAMED_POOLS]
    if name not in cache:
        cache[name] = MongoPool(pool.client, name)
    return cache[name]


def _collection(pool, name: Any):
    _require(isinstance(name, str) and bool(name), "collection must be a name")
    if getattr(pool, "db_type", None) != "mongodb":
        raise UnsupportedOperation(
            "the JSON document API requires MongoDB; use /db/query for the "
            "legacy SQL API on SQLite"
        )
    return pool.collection(name)


async def _body(request: web.Request) -> dict:
    try:
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"request body is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")
    return payload


# ── legacy SQL ────────────────────────────────────────────────────────────


async def handle_query(request: web.Request) -> web.Response:
    payload = await _body(request)
    op = str(payload.get("op") or "")
    _require(op in SQL_OPS, f"unknown query operation: {op or '<empty>'}")
    query = payload.get("query")
    _require(isinstance(query, str) and bool(query.strip()), "query is required")
    args = payload.get("args") or []
    _require(isinstance(args, list), "args must be a list")

    pool = _pool_for(request.app, payload.get("database"))
    result = await getattr(pool, op)(query, *args)
    if op == "fetch":
        return _response({"rows": [dict(row) for row in result]})
    if op in ("fetchrow", "fetchone"):
        return _response({"row": dict(result) if result is not None else None})
    if op == "fetchval":
        return _response({"value": result})
    return _response({})


# ── native collection subset ──────────────────────────────────────────────


def _unpack(args: list, count: int, what: str, defaults: tuple = ()) -> list:
    _require(isinstance(args, list), "args must be a list")
    values = list(args[:count])
    values.extend(defaults[len(values):])
    _require(len(values) == count, f"{what} expects at most {count} arguments")
    return values


def _index_keys(keys):
    if isinstance(keys, str):
        return keys
    _require(isinstance(keys, list) and keys, "index keys must be a name or a list")
    out = []
    for item in keys:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            out.append((item[0], int(item[1])))
        else:
            out.append((item, 1))
    return out


async def _collection_op(collection, op: str, args: list) -> dict:
    if op == "find":
        filter_doc, projection, options = _unpack(
            args, 3, "find", defaults=(None, None, {})
        )
        cursor = collection.find(filter_doc or {}, projection)
        options = options or {}
        sort = options.get("sort") or []
        if sort:
            cursor = cursor.sort([(key, int(order)) for key, order in sort])
        if options.get("skip") is not None:
            cursor = cursor.skip(int(options["skip"]))
        if options.get("limit") is not None:
            cursor = cursor.limit(int(options["limit"]))
        documents = await cursor.to_list(length=None)
        return {"documents": [dict(document) for document in documents]}

    if op == "find_one":
        filter_doc, projection = _unpack(
            args, 2, "find_one", defaults=(None, None)
        )
        document = await collection.find_one(filter_doc or {}, projection)
        return {"document": dict(document) if document is not None else None}

    if op == "insert_one":
        (document,) = _unpack(args, 1, "insert_one")
        _require(isinstance(document, dict), "insert_one expects a document")
        result = await collection.insert_one(document)
        return {"inserted_id": getattr(result, "inserted_id", None)}

    if op in ("replace_one", "update_one"):
        filter_doc, change, upsert = _unpack(
            args, 3, op, defaults=(None, {}, False)
        )
        _require(isinstance(change, dict), f"{op} expects a document")
        method = getattr(collection, op)
        result = await method(filter_doc or {}, change, upsert=bool(upsert))
        return {
            "matched_count": int(getattr(result, "matched_count", 0) or 0),
            "modified_count": int(getattr(result, "modified_count", 0) or 0),
            "upserted_id": getattr(result, "upserted_id", None),
        }

    if op in ("delete_one", "delete_many"):
        (filter_doc,) = _unpack(args, 1, op, defaults=(None,))
        result = await getattr(collection, op)(filter_doc or {})
        return {"deleted_count": int(getattr(result, "deleted_count", 0) or 0)}

    if op == "count_documents":
        (filter_doc,) = _unpack(args, 1, "count_documents", defaults=(None,))
        return {"count": int(await collection.count_documents(filter_doc or {}))}

    if op == "create_index":
        keys, options = _unpack(args, 2, "create_index", defaults=(None, {}))
        _require(isinstance(options, dict), "create_index options must be an object")
        name = await collection.create_index(_index_keys(keys), **options)
        return {"name": name}

    raise ValueError(f"unknown collection operation: {op or '<empty>'}")


async def handle_collection(request: web.Request) -> web.Response:
    payload = await _body(request)
    pool = _pool_for(request.app, payload.get("database"))
    collection = _collection(pool, payload.get("collection"))
    args = payload.get("args") or []
    _require(isinstance(args, list), "args must be a list")
    result = await _collection_op(collection, str(payload.get("op") or ""), args)
    return _response(result)


# ── JSON documents ────────────────────────────────────────────────────────


async def handle_json_read(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    args: list[Any] = [payload.get("filter") or {}, payload.get("projection")]
    options: dict[str, Any] = {}
    for key in ("sort", "limit", "skip"):
        if payload.get(key) is not None:
            options[key] = payload[key]
    args.append(options)
    result = await _collection_op(collection, "find", args)
    return _response({"documents": result["documents"]})


async def handle_json_read_one(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    result = await _collection_op(
        collection, "find_one", [payload.get("filter") or {}, payload.get("projection")]
    )
    return _response({"document": result["document"]})


async def handle_json_write(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    document = payload.get("document")
    _require(isinstance(document, dict), "document must be an object")
    key = payload.get("key")
    key = str(key) if key is not None else None
    document_id = document.get("_id")
    if key:
        document_id = document.get(key)
    _require(document_id is not None, "document has no id; pass _id or key")

    # The id is the filter, never part of the replacement: Mongo rejects a
    # replacement whose _id disagrees with the filter, and an upsert fills it
    # in from there.
    replacement = {k: v for k, v in document.items() if k != "_id"}
    result = await collection.replace_one(
        {"_id": document_id}, replacement, upsert=True
    )
    return _response(
        {
            "id": document_id,
            "created": getattr(result, "upserted_id", None) is not None,
        }
    )


async def handle_json_update(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    update = payload.get("update")
    _require(isinstance(update, dict), "update must be an object")
    result = await collection.update_one(
        payload.get("filter") or {}, update, upsert=bool(payload.get("upsert"))
    )
    return _response(
        {
            "matched_count": int(getattr(result, "matched_count", 0) or 0),
            "modified_count": int(getattr(result, "modified_count", 0) or 0),
            "upserted_id": getattr(result, "upserted_id", None),
        }
    )


async def handle_json_delete(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    method = collection.delete_many if payload.get("many") else collection.delete_one
    result = await method(payload.get("filter") or {})
    return _response({"deleted_count": int(getattr(result, "deleted_count", 0) or 0)})


async def handle_json_count(request: web.Request) -> web.Response:
    payload = await _body(request)
    collection = _collection(
        _pool_for(request.app, payload.get("database")), payload.get("collection")
    )
    count = await collection.count_documents(payload.get("filter") or {})
    return _response({"count": int(count)})


# ── health ────────────────────────────────────────────────────────────────


async def handle_health(request: web.Request) -> web.Response:
    pool = request.app[POOL]
    return _response(
        {
            "backend": getattr(pool, "db_type", "unknown"),
            "uptime_seconds": round(time.monotonic() - request.app[STARTED_AT], 3),
        }
    )


@web.middleware
async def _guard(request: web.Request, handler):
    token = str(request.app.get(TOKEN) or "")
    provided = request.headers.get(TOKEN_HEADER) or ""
    authorized = bool(token) and bool(provided) and hmac.compare_digest(
        provided.encode("utf-8", "replace"), token.encode("utf-8")
    )
    if not authorized:
        return _error("unauthorized", status=401)
    try:
        return await handler(request)
    except web.HTTPException as exc:
        return _error(exc.reason or "request failed", status=exc.status)
    except UnsupportedOperation as exc:
        return _error(str(exc), status=400)
    except (ValueError, KeyError, TypeError, PermissionError) as exc:
        return _error(f"{type(exc).__name__}: {exc}", status=400)
    except Exception as exc:
        bot_logging.warning(
            "Database", f"{request.path} failed: {type(exc).__name__}: {exc}"
        )
        return _error(f"{type(exc).__name__}: {exc}", status=500)


def create_app(pool, token: str, *, base_database: str | None = None) -> web.Application:
    app = web.Application(middlewares=[_guard], client_max_size=MAX_BODY_BYTES)
    app[POOL] = pool
    app[TOKEN] = token
    app[BASE_DATABASE] = base_database or _base_database()
    app[NAMED_POOLS] = {}
    app[STARTED_AT] = time.monotonic()
    app.add_routes(
        [
            web.get("/db/health", handle_health),
            web.post("/db/query", handle_query),
            web.post("/db/collection", handle_collection),
            web.post("/db/json/read", handle_json_read),
            web.post("/db/json/read_one", handle_json_read_one),
            web.post("/db/json/write", handle_json_write),
            web.post("/db/json/update", handle_json_update),
            web.post("/db/json/delete", handle_json_delete),
            web.post("/db/json/count", handle_json_count),
        ]
    )
    return app


# ── process lifecycle ─────────────────────────────────────────────────────


def _report(reporter, event: str, **fields) -> None:
    if reporter is not None:
        reporter.send(event, **fields)


async def _heartbeat_loop(reporter, interval: float = 3.0) -> None:
    try:
        while True:
            await asyncio.sleep(interval)
            if not reporter.heartbeat():
                return
    except asyncio.CancelledError:
        raise


async def _serve(reporter) -> int:
    token = (os.environ.get(TOKEN_ENV) or "").strip()
    if not token:
        print(
            f"db_child: {TOKEN_ENV} is not set; refusing to start an unauthenticated database",
            file=sys.stderr,
        )
        return 2

    # Start the heartbeat before the pool: a cold MongoDB connect can take
    # longer than the supervisor's heartbeat timeout (three 6s attempts plus
    # backoff), and a starting child that never beats looks like a hung one.
    heartbeat = (
        asyncio.create_task(_heartbeat_loop(reporter), name="db-heartbeat")
        if reporter is not None
        else None
    )

    try:
        pool = await database.create_pool(DATABASE_PATH)
    except Exception as exc:
        reason = f"database is unavailable: {type(exc).__name__}: {exc}"
        bot_logging.error("Database", reason)
        _report(reporter, "readiness_failed", reason=reason)
        if heartbeat is not None:
            heartbeat.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await heartbeat
        return 1

    backend = getattr(pool, "db_type", "unknown")
    _report(reporter, "db_ready", backend=backend)

    app = create_app(pool, token)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = int(site._server.sockets[0].getsockname()[1])

    _report(reporter, "api_listening", host="127.0.0.1", port=port)
    bot_logging.success(
        "Database", f"Database child listening on 127.0.0.1:{port} ({backend})"
    )
    _report(reporter, "ready", checks={"database": True, "backend": backend})

    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(signum, stopping.set)
        except (NotImplementedError, RuntimeError):
            try:
                signal.signal(signum, lambda *_: loop.call_soon_threadsafe(stopping.set))
            except (ValueError, OSError):
                pass

    await stopping.wait()
    _report(reporter, "draining", reason="signal")
    if heartbeat is not None:
        heartbeat.cancel()
        try:
            await heartbeat
        except (asyncio.CancelledError, Exception):
            pass
    await runner.cleanup()
    bot_logging.info("Shutdown", "Database child stopped.")
    _report(reporter, "stopped")
    return 0


def main() -> int:
    reporter = None
    if (os.environ.get("NIKO_SUPERVISED") or "").strip() == "1":
        from supervisor_protocol import ChildReporter, install_parent_death_signal

        reporter = ChildReporter.from_environment()
        install_parent_death_signal()
        _report(reporter, "process_started")
    try:
        return asyncio.run(_serve(reporter))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
