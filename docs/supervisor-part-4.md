# Supervisor Part 4 — Split Dashboard and Bot Children

> **Status:** Default supervised mode since 2026-11-06. The supervisor starts
> the database (`src/db_child.py`), the dashboard (`src/web_child.py`) and the
> bot (`src/bot.py`) as separate children unless `--no-split-web` /
> `NIKO_SPLIT_WEB=0` is passed. The non-supervised `python3 src/bot.py` path is
> unchanged.
>
> **Date:** 2026-11-06

## 1. Topology

```text
supervisor.py            public PORT, /health, /ready, control socket, log archive
├─ db child              src/db_child.py      the one database pool; JSON documents + legacy SQL
├─ web child             src/web_child.py     Flask, static, auth, SEO, owner console
└─ bot child             src/bot.py           gateway, cogs, loopback API, database client
```

The supervisor keeps one supervision loop per child, and each has its own
readiness, heartbeat, restart budget (`--max-restarts`), backoff, exit history
and status entry. Killing or restarting either child cannot stop the other.

- Public traffic is proxied to the **web** child.
- `/api/discord/interactions` is proxied straight to the **bot** child, because
  the signature and the 3-second deadline belong to that process.
- `/ready` reflects the **web** child. A bot child that is booting or being
  replaced leaves the service ready: the dashboard is the public surface, and an
  unhealthy bot must not make the platform restart the whole service.

`GET /supervisor/status` (control socket, or the opt-in public endpoint) now has
a `children` map beside the existing `child` field, which stays the primary
(dashboard) child for older readers.

## 2. The 4A seam: live-bot routes are bridged

`web_child.py` has no bot object, no gateway and no database pool. The Flask
routes that read the live bot still live in the bot child, so `web_bridge.py`
forwards them over loopback:

- local to the dashboard child: `/api/owner/logs`, `/api/health`, `/api/config`,
  `/api/emojis`, `/api/site/build`;
- forwarded to the bot child: every other `/api/*` request;
- when the bot child is not serving, the browser gets a bounded
  `503 {"error": "service unavailable", "reason": "the bot child is not
  serving", "retry_after": 1}` with `Retry-After: 1`, while the dashboard shell,
  auth and static assets keep answering.

The web child asks the supervisor for the bot's port over the local control
socket (`route`), caches it for a second, and drops the cache on a failed
forward, so a replaced bot child is picked up without a restart.

This bridge is deliberately the **Part 4A contract**, not the final design: it
preserves every current route exactly, at the cost of running Flask in both
children. Replacing it with a state mirror/RPC contract (the design review's
Part 4 goal) removes Flask from the bot child and closes the version-skew window
described next.

## 2a. The dashboard child reaches Discord through the bot child

Splitting the processes also split the Discord egress. Before the split the
dashboard borrowed the bot's own HTTP client in-process, so its OAuth token
exchange, session refresh, user fetch and membership reads travelled with the
bot's `User-Agent` and, when failover had armed it, the Webshare proxy. In the
dashboard child there is no such client: `discord_request` fell back to a bare
`requests` call from the host's own address. On a host whose address Cloudflare
has banned for the Discord API that is every browser path to Discord failing —
sign-in included — while the bot keeps answering commands, which is exactly what
production saw.

`src/webapp/discord_api.py` therefore hands those calls to the bot child when it
has no bot of its own:

- `POST /api/internal/discord` on the bot child's loopback API
  (`webapp/routes/internal_routes.py`) takes `{method, url, kwargs}`, makes the
  call with `discord_request` where the bot lives, and returns the status,
  headers and base64 body;
- the route accepts only Discord API URLs, only the request options
  `discord_request` is called with, and only the supervisor's per-run
  `NIKO_RELAY_TOKEN` — so it is not a public relay even where the dashboard is
  reachable directly;
- that credential is minted for this hop alone and handed to the `bot` and `web`
  children only. `NIKO_INTERNAL_TOKEN`, which also opens updates and the database
  child, still never reaches the dashboard: one capability, one credential, and
  a dashboard that is reached by the public cannot borrow the bot's loopback API
  beyond making a Discord call;
- a process with no bot answers `503` instead of pretending to have egress, and
  `web_bridge.should_forward` keeps `/api/internal/*` out of the public bridge;
- a single-process deployment never relays: the bot is right there, and the
  local path is unchanged.

The dashboard still owns its cookies, sessions and routes; only the HTTP call
moves, which keeps the sign-in a redirect through the site and puts the OAuth
token exchange back on the egress the bot is already using.

## 2b. The database child

The pool used to live inside the bot because the bot was the entry point. Now
that the dashboard and the bot are separate, tying the database to either one is
only a limitation: restarting the bot closed the pool, and the dashboard could
never touch it. The pool moved to its own child.

`src/db_child.py` runs `database.create_pool()` once and serves a
loopback-only, token-authenticated HTTP API on an ephemeral port it reports in
`api_listening`:

- `POST /db/json/read`, `/read_one`, `/write`, `/update`, `/delete`, `/count` —
  the JSON document API. New code passes documents, not SQL. It requires
  MongoDB.
- `POST /db/query` — the legacy SQL surface (`execute`, `fetch`, `fetchrow`,
  `fetchval`, `fetchone`), unchanged for every existing call site. **SQLite
  keeps working here** until support is removed between December 1 and
  December 10, 2026.
- `POST /db/collection` — the small native-motor subset (`find`, `find_one`,
  `insert_one`, `replace_one`, `update_one`, `delete_one`, `delete_many`,
  `count_documents`, `create_index`) used by the modules that already speak
  MongoDB directly.

`database/remote.py` is the bot-side handle. It exposes the same pool API
(`db_type`, the SQL methods, `collection()`, `client.admin.command("ping")`), so
call sites did not change. It also adds `documents(name)` for the JSON API and
`database(name)` for the music and error-report databases on the same cluster.
The supervisor passes the child's port to the bot through `NIKO_DB_API_PORT`
and the control `route` command; a failed call drops the cached port and asks
again, so a replaced database child is picked up without a bot restart.

Only the bot and db children get `NIKO_INTERNAL_TOKEN`; the database child
refuses to start without it. The relay credential (§2a) is separate and is the
only secret the dashboard child shares with the bot child. Named databases are limited to the configured
`MONGODB_DATABASE` and its `_`-suffixed siblings.

The combined fallback (`--no-split-web`) keeps the historical in-process pool,
where there is no second process to coordinate with. `NIKO_SPLIT_DB=0` or
`--no-split-db` does the same in an otherwise split layout.

## 3. Update ownership

| Update area | What happens | Bot interrupted? | Dashboard interrupted? |
| --- | --- | --- | --- |
| `webapp` | The bot child rebuilds its Flask app in place; the supervisor restarts the `web` child | No | ~1 s |
| `website` | Static files are read from disk on the next request | No | No |
| `utils`, `cogs`, `events`, `startup` | Applied in place in the bot child | No | No |
| `database` (schema) | `init_database` runs again through the database child | No | No |
| `support`, `bot` (includes `src/database/` and `src/db_child.py`) | The bot child is replaced, and the `db` child with it so it loads the new database modules and child script; the `web` child keeps serving | Yes (restart) | No |

`utils.supervisor_control.request_restart()` takes a `child` target, so a bot
update names `bot` and a webapp update names `web`. A run that includes both
areas requests both, separately.

The bridge means the bot child still imports `webapp`; it is refreshed by the
in-process reload the update already performs, so the two children do not serve
different webapp code after a dashboard update.

## 4. The log archive

The owner's logs page used to read a ring buffer in whichever process rendered
it, so every restart started empty and supervisor output was invisible. A
single shared file fixed that but still had two leaks: a chatty process could
rotate lines another process had not read yet, and a DEBUG burst could rotate
the ERROR lines away.

`log_store.py` now keeps **one append-only buffer per process and level** under
`data/run/logs` (next to the supervisor status file, or the directory given to
`--log-store`):

```text
data/run/logs/
  supervisor/  DEBUG.jsonl  INFO.jsonl  WARNING.jsonl  …
  db/          DEBUG.jsonl  INFO.jsonl  WARNING.jsonl  …
  web/         DEBUG.jsonl  INFO.jsonl  WARNING.jsonl  …
  bot/         DEBUG.jsonl  INFO.jsonl  SUCCESS.jsonl  WARNING.jsonl  ERROR.jsonl …
```

Each leaf is an independent `LogStore` with its own lock, byte cursor, rotation
(5 MB, 3 backups by default) and backups; writing `bot/ERROR` can only rotate
`bot/ERROR.jsonl`. A process, level, logger or source only ever competes with
its own buffer. Every record still carries:

- `process`: `supervisor`, `db`, `web` (dashboard), or `bot`;
- `level`, `logger`, `source` (`main` / `pymongo` / `urllib3` / `wavelink`) and
  the ANSI-coloured `line`.

The supervisor renders its own lines with the bot's `ConsoleFormatter`, so the
terminal and the page show the same clock, level and module columns for both.
The supervisor does not duplicate child stdout: each child's own logging handler
is the single copy.

The page's cursor is a **composite of byte offsets**, one per leaf file in the
view, so it survives a child restart and even a supervisor restart. Because a
view spans files, the API accepts two filters and merges only the matching
leaves:

- `process=all|supervisor|db|web|bot`;
- `level=<minimum>` — a WARNING view reads `WARNING`, `ERROR` and `CRITICAL`,
  never DEBUG or INFO.

A cursor past the end of any selected leaf (rotation, or a fresh data
directory) is answered with `reset: true` and the page starts again. The page's
**Process** menu (all / supervisor / database / dashboard / bot) and **level**
menu now select those buffers; the noisy-library switches still hide
`pymongo` / `urllib3` / `wavelink` rows on the client. The locale copies explain
the archive.

## 5. Evidence

```text
PYTHONPATH=src .venv/bin/python -m pytest tests/supervisor \
  tests/test_process_restart.py tests/test_supervisor_readiness.py \
  tests/test_supervisor_control.py tests/test_supervised_updates.py \
  tests/test_api_server_supervised.py tests/test_update_chaos.py \
  tests/test_strict_db_mode.py tests/test_sqlite_concurrency.py \
  tests/test_log_store.py tests/test_owner_logs_store.py \
  -q --timeout=240
→ 91 passed
```

New coverage in this part:

- `tests/test_database_remote.py` — the database child over SQLite (legacy SQL,
  auth, document API refusal) and over an in-memory MongoDB stand-in (JSON
  documents, collection proxy, named databases);
- `tests/supervisor/test_split_children.py` — both children boot; the public
  port is the dashboard; interactions reach the bot child; restarting the
  dashboard leaves the bot PID untouched; killing the bot leaves the dashboard
  ready and `/ready` at 200; supervisor records reach the log archive;
- `tests/supervisor/test_split_real_web_child.py` — the real dashboard child
  under the supervisor next to a fake bot child: HTML locally, `/api/echo`
  forwarded, owner console local;
- `tests/supervisor/test_web_bridge.py` — the forward/local split, cookie and
  header passthrough, query preservation, and the bounded 503 when the bot is
  down;
- `tests/test_log_store.py` — per-process files, the minimum-level view,
  composite cursors across a new archive instance, rotation that resets only
  the rotated level buffer, path sanitisation, 80 concurrent writes, and
  environment selection;
- `tests/test_owner_logs_store.py` — the owner route reads the shared store when
  the supervisor provides one and still falls back to the in-process ring.

`tsc --noEmit` passes for the dashboard changes.

## 6. Known limitations

- The forwarding bridge is HTTP inside one host. It is not the final RPC
  contract, and it keeps Flask imported in the bot child; a Flask-module failure
  still affects the bot child even though the dashboard child keeps serving.
- A dashboard child that cannot boot after a webapp update is restarted by the
  supervisor but is **not** rolled back: the last-good restore point is recorded
  for the bot area only. Extending it to a second pending record is part of the
  RPC work.
- `/ready` intentionally ignores bot readiness. Render will not restart the
  service for a bot-only outage, so alerting must watch
  `children.bot.ready` in the status file.
- Login, uploads, and the update UI through the split have not been exercised
  against Discord from this workspace; the beta preview is the next place to
  run them.
- The log archive is local disk. It survives process and supervisor restarts,
  not a platform redeploy that wipes `data/`. Its bound is per leaf file, so a
  deployment that logs every level for every process holds up to
  `processes × levels × 5 MB × 4`.
