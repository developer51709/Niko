# Supervisor Runtime Migration — Design Review

> **Status:** Temporary design review and delivery plan. Part 1's isolated supervisor harness is implemented in `src/supervisor.py`, and Part 2's supervised real-child mode, readiness, and updater integration are implemented behind `NIKO_SUPERVISED=1`; default production runtime behavior is unchanged. A real-token managed preview has exercised gateway readiness, proxy traffic, control restarts, crash recovery, Discord OAuth, the staff guild directory, guild settings, and live slash commands. The beta-feed cold update and rollback are now exercised end to end on one machine against a loopback feed (`tests/supervisor/test_beta_update_gate.py`), so no second host is needed for that gate, and killing the child at every boot stage is covered (`tests/supervisor/test_boot_stage_kills.py`). What remains before rollout is one confirmation run on a real production-like staging instance and recording it in the runbook. See [`supervisor-part-1.md`](supervisor-part-1.md) and [`supervisor-part-2.md`](supervisor-part-2.md).
> **Date:** 2026-11-06
> **Purpose:** Give the team a concrete architecture, a failure inventory, and a gated multi-part plan before any major runtime changes.
> **Audience:** Bot, webapp, and deployment maintainers.

---

## 1. Executive recommendation

A supervisor is worth building for **reliability and operational control**, not as a magic replacement for hot reload.

The recommended target is:

1. A small, stable **supervisor** process becomes the Render service's main process. It owns the public `PORT`, the health endpoint, the control socket, and child lifecycle.
2. The existing bot + Flask application becomes a **child process**. It keeps almost all current code and still owns the gateway, cogs, database pools, and dashboard.
3. The supervisor reverse-proxies public HTTP to the active child. This keeps the public site and update/control plane answering while a child restarts, and allows a maintenance/health response when no child is ready.
4. Updates are coordinated through the supervisor. The existing updater may stage files, but restart decisions move to the supervisor in supervised mode.
5. **Warm standby** (loading a replacement child before cutover) is a separate, optional part. It is the only part that can materially reduce bot command downtime, and it requires an explicit lifecycle audit of cogs and background tasks.

**Do not make warm standby the first deliverable.** It has the highest chance of duplicate writes, duplicate Discord work, and confusing rollback behavior. Start with a supervised cold restart, prove it, then decide whether warm standby is worth the complexity.

**Do not move `src/bot.py` just to have a new entry point.** The supervisor can be added as `src/supervisor.py` while the child remains `src/bot.py`. Renaming the entry point adds update-system, probe, test, and documentation churn without improving uptime. If the entry point is moved later, it should be a deliberate, separate change.

---

## 2. Goals and non-goals

### Goals

- Keep Render from recreating the deployment when only the bot child restarts.
- Keep the public HTTP endpoint and health/control plane available when the bot child crashes or is being replaced.
- Make bot restarts observable, bounded, recoverable, and (optionally) prewarmed.
- Preserve the existing update areas and file-backed update workflow.
- Retain a non-supervised fallback so local development and unusual hosts still work.
- Ensure only one Discord gateway session and one authoritative writer exist at a time.

### Non-goals

- Preserving live Python objects across process replacement. A new interpreter cannot inherit cogs, event loop tasks, or database connections.
- Eliminating Discord reconnect time. A new gateway session still has to log in, identify, and receive `READY`.
- Making Render's own deploys or host failures invisible. The supervisor cannot prevent a platform-level restart or an ephemeral disk wipe.
- Horizontal bot scaling. Discord's gateway session model and the current SQLite/Mongo writers make a single active bot the safe default.
- Rewriting the dashboard into a separate web service in the first part.

---

## 3. Current baseline

### 3.1 Runtime shape

- `src/bot.py` is the single process.
- It imports the bot, API server, events, and startup code.
- It creates the bot and begins the API before Discord login:
  - `src/bot.py` calls `handoff.adopt(bot)` or `api_server.start_api_server(bot)`.
  - `api_server.py` starts Flask on a daemon thread with `make_server`.
- It then logs in, initializes the database, loads every extension, preloads caches, and calls `bot.connect()`.
- `events/startup/loader.py` records cog outcomes in `bot.cog_status` but catches per-cog failures; the process can become ready with failed cogs.
- `events/on_ready.py` records startup-step errors on the bot but still returns cleanly; `bot.is_ready()` is not a complete readiness signal.
- `webapp/runtime.py` stores the live bot in a module-global and provides `run_on_bot_loop()` for Flask routes. This is the main coupling that prevents a clean web/bot split.

### 3.2 Current update/restart behavior

- `webapp/updates.py` stages files from beta into the live deployment and applies area by area.
- Cog, utility, webapp, database, events, and startup-writer changes are applied in-process.
- `utils/handoff.py` handles the bot-core area by duplicating the listening socket and `execve`-ing a new image. The PID stays the same, so Render sees no exit and the port stays bound.
- A bot-core update therefore still rebuilds the entire interpreter and reloads every cog.
- `webapp/updates.py` probes `src/bot.py` in a throwaway interpreter with `NIKO_IMPORT_PROBE` before restarting.
- `tests/test_process_restart.py` explicitly asserts that the handoff does not use subprocesses and has no candidate/parent architecture. Those tests will need to be updated deliberately, not silently bypassed.

### 3.3 Deployment facts that shape the design

- No `render.yaml`, `Procfile`, or `Dockerfile` is present in the repository. The Render start command and health-check path are external configuration and must be updated as part of rollout.
- The bot can fall back from MongoDB to SQLite in `database.create_pool()` if MongoDB is configured but unreachable. This is safe for one process and dangerous for two concurrent children.
- SQLite uses `data/database.db` with WAL mode. Two children must not be allowed to write it concurrently.
- Several cogs start background loops as soon as they load. Examples include music/Lavalink rescanning, status panels, economy ticks, notifier polling, donations polling, reminders, giveaways, birthdays, automod, premium lifecycle, server stats, and leveling voice XP.
- `utils/interaction_endpoint.py` can serve Discord interactions over HTTP. The public endpoint must have exactly one active owner.
- The owner live-log page reads an in-memory buffer in the child process. A candidate child's logs are not visible through the active child unless the supervisor forwards or stores them.
- The frontend does not currently use WebSockets or server-sent events, so an HTTP reverse proxy can be HTTP-only for the first part.

---

## 4. Target architecture

### 4.1 Roles

```text
Render web service
└─ supervisor.py                 stable PID, public PORT, health, control, proxy
   └─ bot child (src/bot.py)      Flask API on loopback + gateway + cogs
```

Future optional split:

```text
Render web service
└─ supervisor.py
   ├─ web/API process             Flask dashboard, public traffic, no gateway
   └─ bot child                   gateway + cogs, internal control only
```

The first target is the single-child model. It keeps the existing Flask/bot coupling and avoids a large `webapp.runtime` rewrite.

### 4.2 Supervisor responsibilities

- Bind `0.0.0.0:$PORT` immediately.
- Serve:
  - `GET /health` — supervisor liveness. Return 200 while the supervisor can manage children, even if the bot is not ready.
  - `GET /ready` — active-child readiness. Return 200 only when the active child meets the readiness contract; 503 otherwise.
  - `GET /supervisor/status` — detailed JSON; protect or bind it only to a local/admin path if exposed publicly.
- Proxy every other request to the active child's loopback port.
- Spawn the child with an explicit environment and working directory.
- Monitor exit, heartbeat, readiness, memory, and restart count.
- Forward signals and own shutdown.
- Keep a small status file (`data/run/supervisor.json`) updated atomically.
- Expose a local control socket for the updater and operators.

The supervisor must not import `discord`, `webapp`, or cog modules. It should import only the standard library plus the chosen HTTP proxy library (`aiohttp` is already a dependency, but the proxy choice is an explicit decision).

### 4.3 Child responsibilities

- Run the existing bot boot path.
- Bind Flask to `127.0.0.1:$NIKO_CHILD_PORT`, never the public port.
- Report lifecycle events to the supervisor over an inherited pipe or Unix socket.
- Run the existing update code, but ask the supervisor to perform supervised restarts.
- Support a `NIKO_LIFECYCLE=active|warm` mode once warm standby is implemented.
- Exit cleanly on SIGTERM after draining.

### 4.4 Public HTTP proxy

The supervisor should own the public port because Render's health check must remain answerable while the child is down. The proxy must preserve:

- `Host` and `X-Forwarded-Host` (the app uses `X-Forwarded-Host` for subdomain routing).
- `X-Forwarded-Proto` and `X-Forwarded-For`.
- Request and response headers, including multiple `Set-Cookie` values.
- Request bodies, multipart uploads, file downloads, `Range`, `If-None-Match`, and conditional responses.
- Redirects and absolute URLs built by Flask from the public host.
- Compression and caching headers.
- Client disconnects and long-running request cancellation.

There are no WebSocket or SSE endpoints in the current webapp, but the proxy should reject or explicitly handle an upgrade request rather than silently corrupting it.

If a production-grade proxy is not acceptable inside the supervisor, the fallback is Unix FD inheritance: the supervisor holds the listening socket and passes it to the child, and the child serves it directly. That is closer to the current handoff, but the supervisor then cannot answer `/health` while the child is booting. The team should choose one explicitly; do not mix both models casually.

### 4.5 Why not a separate web process immediately?

A separate web process gives the best HTTP availability, but the Flask routes currently read the live bot through `webapp.runtime.configure_bot()` and `run_on_bot_loop()`. Splitting web and bot means replacing those in-process calls with RPC, shared database reads, or a control protocol. That is a major API refactor, not a supervisor detail.

Keep it as a later option if measurements show that a proxy plus maintenance response is not enough.

---

## 5. Lifecycle and readiness contract

### 5.1 Supervisor states

```text
starting → active → draining → restarting → active
                    ↘ failed
```

Plus `degraded` for an active child that is serving HTTP but failing non-critical readiness checks, and `stopped` for an intentional shutdown.

Every state transition must be logged with a monotonic timestamp and the child PID.

### 5.2 Child boot stages reported to the supervisor

1. `process_started` — Python is running.
2. `api_listening` — Flask is bound to the internal port.
3. `db_ready` — the shared pool exists and answers a ping; migrations have completed.
4. `cogs_loaded` — extension loading has finished, with loaded/maintenance/failed counts.
5. `gateway_ready` — all shards are ready and `on_ready` has completed.
6. `ready` — all critical checks pass.
7. `draining` — no new work accepted; in-flight work allowed to finish.
8. `stopped` — clean exit.

The child should use a reliable framed protocol (newline-delimited JSON is sufficient) over an inherited pipe or a Unix socket. Do not parse human log lines to infer readiness.

### 5.3 Readiness policy

A child is **ready** only when:

- The internal API is listening.
- The database pool exists, answers a ping, and reports its backend (`sqlite` or `mongodb`).
- Every critical cog is loaded or intentionally in maintenance. Critical cogs should be an explicit manifest, not “whatever happened to load.”
- No critical startup step failed. `bot.startup_errors` and `bot.last_startup_error` must be checked.
- The gateway reports all expected shards ready.
- The interaction endpoint has a public key or is intentionally disabled.
- The supervisor has received a heartbeat within the configured window.

A child with non-critical cog failures can be marked `degraded` and still receive traffic. The status page and supervisor status should expose the failures.

### 5.4 Heartbeat and hang detection

- Child sends a heartbeat every 2–5 seconds.
- Supervisor restarts after a configurable missed-heartbeat window.
- Heartbeat must be sent from the bot event loop, not a separate thread that can survive a dead loop.
- The supervisor should also check HTTP `/health` on the child with a short timeout, but the heartbeat is the primary hang signal.
- Restart storms are bounded by exponential backoff and a circuit breaker.

---

## 6. Update and cutover protocols

### 6.1 Cold restart (first supervised implementation)

1. The updater stages and validates files.
2. It records the update run and requests a supervised restart over the control socket.
3. It returns the HTTP response before the child is stopped. The supervisor may wait for the response to drain, or the updater may specify a delayed restart; the supervisor must be the one that kills the child.
4. The old child receives SIGTERM; it stops accepting new work, flushes analytics, closes the gateway and database, and exits within `shutdown_timeout`.
5. The supervisor starts a new child with the same environment and an internal port.
6. The child reports `api_listening`; the supervisor can route HTTP to it immediately so the site comes back before cogs are ready.
7. The child reports `ready`; `/ready` flips to 200.
8. If the child fails before readiness, the supervisor records the failure, restores the last-known-good files if a rollback was requested, and starts a replacement.

The expected downtime is the child's import + API bind time for HTTP, and full boot for commands. This is deliberate: cold restart alone does not reduce command downtime.

### 6.2 Warm standby (optional part)

Warm standby is the only design here that removes cog loading from the cutover critical path.

1. The supervisor starts a **candidate** child with `NIKO_LIFECYCLE=warm`.
2. The candidate imports modules, logs into Discord (REST only), opens the database, and loads cogs, but does **not** call `bot.connect()`.
3. The candidate reports `candidate_ready` when its API, database, and cogs are loaded and its side effects are suppressed.
4. The supervisor keeps the old child serving public traffic.
5. At cutover:
   - The candidate is promoted to active;
   - the old child is told to stop accepting new work and close its gateway;
   - the candidate calls `bot.connect()` and reports `gateway_ready`;
   - the proxy switches to the candidate's API;
   - the old child exits after the drain window.
6. If the candidate fails before promotion, the old child keeps serving and the candidate is killed.
7. If the candidate fails after promotion, the supervisor must have a tested rollback: stop the candidate, restore the last-good files if needed, and start a replacement from the last-good snapshot.

Warm standby does **not** preserve cogs or state. It creates a second set of cogs ahead of time. It must not run two Discord gateway sessions at once, and it must not let two children act as authoritative writers.

### 6.3 Candidate side-effect rules

A warm candidate must not:

- Connect to Discord's gateway.
- Run `on_ready` or the startup writers (`bot_stats.json`, `commands.json`).
- Edit status panels or send startup/status messages.
- Start command-tree sync or emoji sync.
- Run background loops that write to the database, call Discord, or consume external services.
- Connect to Lavalink, open voice connections, or create players.
- Start broadcast/analytics flush jobs.
- Accept public interactions.

The candidate may:

- Import modules and compile bytecode.
- Create the bot object and log in over REST to get application information.
- Open the database if the backend supports safe concurrent readers.
- Preload read-only caches only if cache invalidation at promotion is understood.
- Bind its internal API port.

This requires a `lifecycle` gate in the child and an audit of every cog's `__init__`, `cog_load`, and task-loop start. The audit is not optional.

---

## 7. Data ownership and singleton rules

The supervisor must enforce a single **active writer** at all times.

### Database

- **SQLite:** warm standby is unsafe. WAL allows concurrent readers, but two active processes writing `data/database.db` can produce lock errors and unpredictable behavior. Warm standby must be disabled automatically when the pool type is SQLite. Cold restart is allowed only after the old child has exited and its pool is closed.
- **MongoDB:** concurrent readers are safe, but concurrent writers and duplicate background jobs are not. Candidate writes must be suppressed until promotion.
- **Fallback:** `database.create_pool()` currently falls back to SQLite after MongoDB failures. In supervised production mode, add a strict mode (`REQUIRE_MONGODB=1` or similar) that refuses to start rather than silently switching an ephemeral instance to an empty local database. A candidate must never start on a different backend than the active child.

### Local files

`data/` contains bot stats, command data, legacy migration files, update backups, developer applications/screenshots, and other state. The active child is the only process allowed to write authoritative files. Candidate writers must be gated by lifecycle state. Atomic writes are already used in some places; that should become a rule for every `data/*.json` writer touched by the supervisor work.

### Discord

- One gateway session per shard.
- One owner of the HTTP interactions endpoint.
- One command-tree sync owner. The fingerprint check in `events/startup/sync.py` prevents unnecessary syncs but does not make concurrent candidates safe.
- One owner of status-panel edits, Lavalink rescanning, music players, and voice connections.

### Web sessions

Set a stable `SESSION_SECRET` in production. If it is unset, Flask generates a random secret at import; every child restart then invalidates sessions. That is especially visible once restarts are frequent. Verify `PUBLIC_URL` and `DISCORD_REDIRECT_URI` remain stable across both children.

---

## 8. Breaking-point register

> Severity is relative to the production bot. "Mitigation" is the design requirement, not a claim that it is already implemented.

### Process and supervisor lifecycle

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| S-01 | Supervisor crashes | Render restarts the service; all children die | Keep supervisor tiny and dependency-light; no bot imports; fast startup; external health check | Kill supervisor; Render recovers; supervisor starts one child |
| S-02 | Child crash loop | Restart storm, Discord rate limits, noisy logs | Exponential backoff, max attempts, circuit breaker, alerting; do not restart faster than boot time | Simulate immediate child exit loop |
| S-03 | Orphaned child after supervisor death | Two bot processes may start; port/DB conflict | Child requests `PR_SET_PDEATHSIG` on Linux; start child in its own process group; supervisor reaps; kill group on shutdown | `kill -9` supervisor; verify child exits |
| S-04 | Zombie child | PID/resource leak | `waitpid`/`poll` every child; never leave completed children unreaped | Long-running restart test |
| S-05 | Supervisor receives SIGTERM | Abrupt child kill, lost analytics | Forward SIGTERM, drain child, bounded timeout, then SIGKILL; flush supervisor state | Render stop simulation |
| S-06 | Child ignores SIGTERM | Hung shutdown | Two-stage stop: SIGTERM, grace period, SIGKILL; log which stage was used | Fake child ignores SIGTERM |
| S-07 | Stale PID/lock/socket after crash | New supervisor refuses to start or talks to nothing | Use `flock`/PID validation, not just file existence; bind a Unix socket and probe it; clean stale files only after ownership check | Kill and restart repeatedly |
| S-08 | Two supervisors run | Both try to own port/control; two bot children | OS port binding plus a file lock; fail closed if another live supervisor exists | Start second supervisor |
| S-09 | Port already in use | Supervisor cannot serve; Render fails | Fail fast with a clear message; do not spawn child; check public and internal ports | Occupy port before start |
| S-10 | Internal port collision | Candidate cannot bind | Ask the OS for a free loopback port and pass it to the child; never hardcode `PORT+1` | Start repeated candidates |
| S-11 | Wrong cwd/env in child | Imports, data paths, tokens fail | Supervisor sets explicit cwd, sanitized environment, and removes stale `NIKO_RESTART_FD`/handoff markers | Boot from a different cwd |
| S-12 | FD leak | Long-running memory/handle exhaustion | `close_fds=True`, pass only required descriptors, close pipe ends in both processes | Repeated restart FD count test |
| S-13 | Supervisor update deployed in-place | The stable layer becomes part of the update problem | Exclude supervisor from beta update areas; update it only by normal deploy; version it explicitly | Manifest inspection |
| S-14 | Clock/timezone changes | Timeout and uptime errors | Use `time.monotonic()` for supervision; UTC for logs/status | Time-change test |
| S-15 | Child cannot report readiness because pipe broke | Supervisor waits or kills a healthy child | Treat control-channel failure as child failure; timeout and restart; include stderr diagnostics | Close child event pipe |
| S-16 | Child blocks writing stdout/stderr because the supervisor is not draining it | Bot hangs during boot or under log load | Drain child output continuously on separate threads/tasks; never use an unbounded in-memory buffer; capture to bounded/rotating storage | Flood child logs during boot |

### HTTP, proxy, and Render

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| H-01 | Render health check points at the child | Child restart causes Render to restart the service | Point Render at supervisor `/health`; keep `/ready` separate | Dashboard/API config review |
| H-02 | `/health` returns 200 while bot is dead | Silent outage; no platform recovery | `/health` is supervisor liveness; `/ready` and external alerts cover bot readiness | Kill child; `/health` 200, `/ready` 503 |
| H-03 | Proxy loses `Host`/`X-Forwarded-Host` | Subdomain routing, OAuth redirects, absolute links break | Set/overwrite forwarded headers from the public request; never trust client-supplied forwarded headers | Subdomain + auth tests |
| H-04 | Proxy mishandles cookies | Sign-in/session failures | Pass all `Set-Cookie` values unchanged; preserve domain/path/secure/samesite; stable `SESSION_SECRET` | Login, CSRF, subdomain session tests |
| H-05 | Proxy breaks uploads/downloads/range | Broadcast uploads, developer screenshots, transcript downloads fail | Stream request/response bodies; preserve `Content-Length`, `Content-Type`, `Range`, `If-*`, 206 responses | Multipart and range tests |
| H-06 | Proxy times out long operations | Update/apply, exports, slow Discord calls fail | Per-route or generous configurable timeout; do not impose a short global timeout | Long request test |
| H-07 | In-flight request is killed at cutover | Lost response, duplicate POST | Drain old child; route new requests to active; retry only idempotent GETs; document non-idempotent behavior | Cutover under load |
| H-08 | Update response is cut off by restart | Owner sees a failed update though files applied | Supervisor delays child stop until response drains; update status persisted outside child memory | Apply bot area from UI |
| H-09 | Proxy is a bottleneck | Higher latency / dropped requests | Benchmark with expected concurrency; keep proxy code minimal; consider FD pass-through if proxy overhead is high | Load test |
| H-10 | Proxy adds a new SSRF/header-smuggling surface | Security issue | Bind child to loopback; normalize headers; reject ambiguous `Content-Length`/`Transfer-Encoding`; use a maintained proxy implementation | Security review |
| H-11 | Static assets or compression break | Broken dashboard | Pass `Accept-Encoding`, `Content-Encoding`, cache headers; test HTML/CSS/JS and conditional requests | Browser smoke test |
| H-12 | Interaction endpoint has two owners | Duplicate handling / invalid signatures | Proxy `/api/discord/interactions` to exactly one active child; candidate does not accept public interactions until promoted | Dual-child interaction test |
| H-13 | OAuth callback uses wrong origin | Sign-in fails | Preserve `PUBLIC_URL`/`DISCORD_REDIRECT_URI`; test callback through proxy | Sign-in end-to-end |

### Bot, gateway, cogs, and warm standby

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| B-01 | Two gateway sessions connect | Discord disconnects one; event flapping; duplicate commands | Only active child calls `bot.connect()`; candidate stops before connect; explicit old-close → new-connect ordering | Gateway session test |
| B-02 | Candidate connects before old closes | Session takeover/flapping | Cutover state machine; supervisor owns the sequence; old must acknowledge `gateway_closed` | Chaos cutover test |
| B-03 | Candidate gateway connect fails after old closed | Bot offline; rollback needed | Bounded retry, keep candidate logs, restore last-good files, start replacement; measure and document the rollback gap | Simulate invalid token/network |
| B-04 | `bot.is_ready()` is treated as full readiness | Commands/cogs unavailable while status says ready | Use explicit readiness stages, critical-cog manifest, `startup_errors`, shard readiness | Fault injection with one failed cog |
| B-05 | Startup step fails but `on_ready` returns | Degraded bot marked healthy | Record and expose startup errors; fail readiness for critical steps; allow degraded for non-critical | Inject each startup-step failure |
| B-06 | Cog load failure is swallowed | Missing commands; user-visible gaps | Critical-cog manifest; fail readiness or mark degraded; preserve `cog_status` details | Remove/broke a cog module |
| B-07 | Warm candidate runs background tasks | Duplicate writes, duplicate Discord messages, rate limits | Global lifecycle gate; audit every `cog_load`/task start; no candidate tasks before promotion | Warm child observation period |
| B-08 | Warm candidate starts Lavalink/music | Duplicate nodes/players; rate limits; voice state confusion | Lifecycle gate around node rescan, player creation, voice connections; only active child connects | Music cog warm test |
| B-09 | Warm candidate writes status panels | Duplicate edits; API rate limits | No `on_ready`/status refresh until promoted; candidate must not own stored panels | Panel DB inspection |
| B-10 | Warm candidate runs command/emoji sync | Discord command sync quota/rate-limit risk | Only active child runs sync; fingerprint check is not a concurrency guard | Mock sync calls |
| B-11 | Warm candidate starts analytics/donation/notifier loops | Duplicate DB rows or external posts | Lifecycle gate or do not load those cogs until promotion | Warm run with network/DB mocks |
| B-12 | Warm candidate overwrites `bot_stats.json`/`commands.json` | Version/command metadata flips before cutover | Gate writers until promotion; run writers once after promotion | Warm candidate file checks |
| B-13 | Candidate caches are stale at promotion | Wrong config/language/AI settings | Reload mutable caches after promotion or use cache versions/leases | Update config during warm boot |
| B-14 | Voice/music state is lost at cutover | Active players disconnect | Document as expected; add state persistence/reconnect only as a separate feature | Voice player cutover test |
| B-15 | In-flight commands/interactions are lost | User sees failure | Drain window; interaction response budget; route new interactions to candidate after readiness | Cutover under command load |
| B-16 | Shard coverage is incomplete | Some guilds offline while "ready" | Readiness waits for all expected shards; expose per-shard status | Shard fault injection |
| B-17 | Public interactions arrive during gateway gap | 3-second deadline missed | Keep proxy/API up, prewarm cogs, switch interaction ownership promptly; document residual window | Interaction load during cutover |
| B-18 | Background jobs are canceled on restart | Lost broadcasts/flushes | Drain/await known jobs or make jobs durable; at minimum preserve current behavior and document | Kill during broadcast |

### Database and local state

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| D-01 | Two SQLite writers | `database is locked`, corruption risk, lost writes | Disable warm standby for SQLite; stop old pool before new opens; never run two active children | SQLite two-process test |
| D-02 | Mongo failure silently falls back to SQLite | Empty database on a fresh instance; split-brain data | Strict backend mode in supervised production; fail readiness instead of fallback | Simulate Mongo outage |
| D-03 | Candidate runs migrations while old child uses old schema | Old child breaks mid-update | Expand/contract migrations only; advisory migration lock; defer destructive changes; test old code against new schema | Migration compatibility tests |
| D-04 | Two children write local JSON | Torn/lost state | Single authoritative writer; candidate gates all writes; atomic replace for every file | Warm candidate file diff test |
| D-05 | Analytics flush is duplicated or lost | Bad charts/lost counters | Only active child flushes; drain on shutdown; idempotent aggregation if possible | Active/candidate analytics test |
| D-06 | Session secret changes | All dashboard sessions invalidated on every restart | Require stable `SESSION_SECRET` in production | Restart then reuse session |
| D-07 | Update backups/status are child-local | Rollback/status lost when child dies | Store update run/status/backups in stable `data/updates`; supervisor reads them; avoid in-memory-only state | Kill child during update |
| D-08 | Concurrent update runs | Files/areas overwrite each other | Supervisor-level update lock plus existing updater lock; persist active run | Two simultaneous apply requests |
| D-09 | Local disk is ephemeral | Pulled files vanish on Render restart | Document clearly; deploy for durability; never treat supervisor as persistence | Platform restart |

### Update system and migration mechanics

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| U-01 | Updater and supervisor both restart | Double restart, lost response | Single owner: in supervised mode the updater requests; supervisor performs; disable `handoff.schedule` | Apply bot area |
| U-02 | Update progress lives in child memory | Progress disappears during restart | Persist run state; supervisor exposes status; UI tolerates 503 during handoff | Apply while polling |
| U-03 | Bot area still points at old entrypoint | New runtime never receives code | Update `AREAS["bot"]` paths, `_probe_bot`, `utils.handoff` target, docs/tests together | Manifest path test |
| U-04 | Supervisor is included in beta manifest | Updating it requires the platform restart it was meant to avoid | Explicit exclusion from all areas; keep it stable | `area_files` inspection |
| U-05 | Candidate starts on partially applied files | Import/runtime failure | Stage and validate the complete area before supervisor restart; probe in a clean interpreter; never start candidate mid-stage | Fault injection during staging |
| U-06 | Rollback after old child exits needs old code | No old process to fall back to | Keep changed-file backups and a last-good release marker; supervisor can restore files and start a fresh child | Force candidate failure after old exit |
| U-07 | New probe inherits supervisor/child env | Probe starts a bot or connects | Sanitize `NIKO_*` env; `NIKO_IMPORT_PROBE` exits after imports; probe with no public port | Probe env test |
| U-08 | Candidate updates its own supervisor control code | Protocol mismatch | Supervisor protocol versioned; candidate and supervisor negotiate; supervisor rejects unknown commands | Version skew test |
| U-09 | Update runs while warm candidate exists | Candidate holds old code while files change | Updates are serialized through supervisor; no update while a candidate is booting; abort candidate first | Concurrent update/candidate test |
| U-10 | Existing restart tests are bypassed | Regression in non-supervised/local mode | Keep a handoff fallback; update tests to cover both modes; do not delete the old path | Two-mode test suite |

### Logging, observability, and security

| ID | Breaking point | Impact | Required mitigation | Verification |
| --- | --- | --- | --- | --- |
| O-01 | Child logs are lost or mixed | Hard diagnosis | Supervisor forwards stdout/stderr with PID/role prefix; per-child log files; candidate logs retained | Restart/candidate log test |
| O-02 | Owner live-log page only sees one child | Missing candidate/crash evidence | Expose supervisor/child log source; keep per-child buffers; do not pretend prewarm logs are active | UI check |
| O-03 | No restart history | Cannot diagnose crash loops | Persist state, exit code, boot duration, restart count, readiness failure reason | Restart after forced crash |
| O-04 | Health is green while bot is degraded | Silent user impact | Separate `/health`, `/ready`, `/status`; alert on readiness, failed critical cogs, missed heartbeats | Fault injection |
| O-05 | Control socket is world-writable | Local privilege/restart attack | `0600` socket, local-only path, peer credential check, no TCP control endpoint | Permission test |
| O-06 | Proxy trusts spoofed forwarded headers | Host/session/origin confusion | Overwrite forwarded headers at the supervisor; never pass client-supplied values through | Header spoof test |
| O-07 | Secrets appear in logs/status | Credential exposure | Redact tokens, cookies, DSNs; pass env without logging values; log child PID/version only | Log scan |
| O-08 | Internal API is exposed publicly | Bypasses proxy/security | Bind child to `127.0.0.1`; firewall/container network review; no public internal port | Port scan |
| O-09 | Two children share a rotating log file | Interleaved/corrupt logs, rotation races | Give each child a role/pid-specific log file, or set `LOG_TO_FILE=false` and let the supervisor own log capture | Concurrent candidate/active log test |

---

## 9. Multi-part delivery plan

This work is intentionally split into separately reviewable, separately testable parts. A part is not “mostly done” and then followed by the next one: its gate must pass and be signed off first. Later parts may be prototyped behind flags, but they must not change production behavior until their gate is complete.

**Part 1 is the stop point for the first review.** It implements the supervisor as an isolated process harness with a fake child. It does not modify `src/bot.py`, the Flask app, the update paths, or production. That lets the team test process supervision, health, proxy behavior, IPC, and failure handling without risking the live bot.

**Part 2 is the first part allowed to integrate the real bot.** It introduces cold supervised restarts. It does not include warm standby or the web/bot split.

### Part map

| Part | Scope | Production behavior | Gate before the next part |
| --- | --- | --- | --- |
| 0 | Baseline, decisions, ADR | None | Baseline report and design sign-off |
| 1 | Supervisor-only design and fake-child harness | None | Supervisor unit/process/proxy tests pass; design approved |
| 2 | Real bot under supervisor; cold restart; update integration | Staging only | Full staging E2E with a test bot + tunnel; crash/restart/update tests pass |
| 3 | Incident recovery and hardening | Canary behind flags | Fault-injection suite, rollback drill, 24-hour soak pass |
| 4 | Split web/dashboard and bot into separate children | Canary behind flags | Independent-failure and independent-update E2E pass |
| 5 | Optional warm standby / hot-reload work | Disabled by default | Cog lifecycle audit and duplicate-side-effect soak pass |
| 6 | Production launch and stabilization | Production default | Full acceptance suite, 72-hour soak, rollback drill signed off |

### Change-control rules

- Every part gets its own implementation note or ADR with: files changed, flags introduced, test evidence, known gaps, rollback command, and reviewer approval.
- New runtime behavior is behind a flag until its gate passes. Suggested flags: `NIKO_SUPERVISED`, `NIKO_SPLIT_WEB`, `NIKO_WARM_STANDBY`.
- A failed gate is fixed in the same part. Do not “carry it forward” into a later part unless the risk is explicitly accepted in writing.
- The supervisor itself is never included in the beta update areas. It changes only through a normal deploy, with its own review.
- The existing non-supervised start command remains a supported fallback until Part 6 is complete.
- Test evidence is attached to the part review: commands run, durations, logs, health/status snapshots, and any skipped tests with a reason.

### Part 0 — Baseline and decisions (no runtime changes)

**Write scope**

- Instrument and record current boot phases: process import, API listening, DB ready, cogs loaded, gateway ready.
- Measure current bot-core update downtime and crash-recovery time.
- Confirm production database backend, memory headroom, Render health-check configuration, and whether `SESSION_SECRET` is stable.
- Decide proxy vs FD inheritance; decide whether warm standby is a real requirement; decide whether the web/bot split is required for the product's availability target.
- Record the decision and rejected alternatives in an ADR.

**Do not do in this part**

- No changes to `src/bot.py`, `api_server.py`, `webapp/`, or the updater.
- No new production dependencies.

**Gate evidence**

- Baseline report with real timings from staging or production-like infrastructure.
- Signed-off ADR covering the open decisions in section 12.
- Explicit go/no-go for Parts 4 and 5.

### Part 1 — Supervisor-only design and fake-child harness

**Goal:** prove the supervisor shell before touching the bot.

**Write scope**

- `src/supervisor.py` with public port ownership, `/health`, `/ready`, status file, child spawn/signal/restart logic, loopback proxy, and local control socket.
- A fake child used only by tests: it implements the same lifecycle protocol and can be told to boot, hang, crash, fail readiness, ignore SIGTERM, or leak a child process.
- `tests/supervisor/` covering state transitions, readiness, restart backoff, proxy passthrough, control-socket security, process-group cleanup, and log capture.
- A design note documenting the child protocol and the exact proxy/FD choice.
- Deployment documentation describing the future start command, but **do not change the current production start command**.

**Do not do in this part**

- Do not import `discord`, cogs, or `webapp` in the supervisor.
- Do not modify `src/bot.py` or `src/api_server.py`.
- Do not change the update system or Render configuration yet.
- Do not install a real bot token for these tests; the fake child is sufficient.

**Required tests**

- Supervisor starts with an ephemeral public port and an ephemeral child port.
- `/health` stays up while the fake child is stopped, hung, or restarting.
- `/ready` reflects fake-child readiness and returns 503 when appropriate.
- Proxy preserves host, forwarded headers, cookies, redirects, multipart bodies, file downloads, and `Range` requests.
- SIGTERM drains the child; SIGKILL and timeout paths clean up the process group.
- 100 fake-child restarts produce no zombie processes, FD leaks, or port conflicts.
- A second supervisor cannot steal the port/control socket.
- Control socket is `0600` and rejects an unprivileged/unauthorized client.
- Child stdout/stderr is drained under a log flood.

**Gate**

- Supervisor harness suite passes locally and in CI without Discord, a tunnel, or a database.
- Reviewer signs off that the supervisor is safe to integrate with the real child.
- **Stop here for the first design review.** Do not begin Part 2 until this gate is accepted.

### Part 2 — Real bot under supervisor, cold restart only

**Goal:** replace only the process boundary, not the bot architecture.

**Write scope**

- Child mode in `src/bot.py` / `src/api_server.py`: loopback internal port, lifecycle events, heartbeat, clean shutdown, and no `handoff.schedule()` when supervised.
- Supervisor child launch from the stable entry point; keep `src/bot.py` as the child entry point.
- Public HTTP through the supervisor proxy; `/health` and `/ready` separated.
- Updater integration for the bot area: stage, validate, ask the supervisor to restart, persist update state, and return the update response before the child stops.
- Readiness checks for DB, critical cogs, gateway shards, and startup errors.
- Keep non-supervised mode working exactly as today.
- Update `tests/test_process_restart.py` so supervised mode has explicit coverage while the old in-place handoff guarantees remain tested for non-supervised mode.

**Do not do in this part**

- No warm candidate, no second bot child.
- No web/bot process split.
- No production rollout; staging only.

**Required tests**

- Unit tests from Part 1 continue to pass.
- Staging E2E with a dedicated test bot, test guild, and Cloudflare tunnel (section 10).
- Kill the child at each boot stage; supervisor recovers and the dashboard proxy returns a bounded error/maintenance response.
- Apply a bot-area update from the dashboard; verify one restart, a complete response, the new code active, and a working slash command afterward.
- Force a failed update/probe and verify rollback and last-good startup.
- Verify no Render service restart is needed for a child restart.
- Verify non-supervised `python src/bot.py` still works.

**Gate**

- Part 2 E2E suite passes with a real test token and tunnel, not only mocks.
- Crash, restart, cold update, failed update, and rollback scenarios are all recorded in the runbook.
- **Still no production rollout.** Begin Part 3 only after this evidence is reviewed.

### Part 3 — Incident recovery and hardening

**Goal:** make failures observable, bounded, and recoverable before changing the process topology again.

**Write scope**

- Strict database backend mode; fail instead of silently falling back from MongoDB to SQLite in supervised production.
- Critical-cog manifest and degraded-state reporting.
- Heartbeat hang detection and restart circuit breaker.
- Supervisor/child log forwarding, status API, and restart history.
- Rollback that restores changed files and starts a last-good child when the old process is already gone.
- Startup/shutdown drains for known background work.
- Full chaos suite and incident runbook.

**Do not do in this part**

- No web/bot split.
- No warm standby.
- No removal of the non-supervised fallback.

**Required tests**

- Every scenario in the section 10 fault-injection matrix.
- Kill supervisor, child, and tunnel at each critical stage.
- Mongo outage, SQLite lock, disk-full simulation, malformed beta manifest, and duplicate update requests.
- 24-hour staging soak with dashboard polling, commands, and periodic restarts.
- Verify no duplicate gateway sessions, command syncs, analytics rows, panel edits, or local-file writes.

**Gate**

- All P0 recovery tests pass; no unexplained duplicate side effects.
- Recovery times are within the agreed target and visible in `/status`/logs.
- Production canary may begin only after this gate, with supervisor enabled behind a flag and warm standby still off.

### Part 4 — Split web/dashboard and bot into separate children

**Goal:** make the dashboard and gateway independently restartable, and therefore independently available.

**4A — Design/RPC contract (gate before code)**

- Define exactly which routes and actions need live bot state.
- Replace `webapp.runtime` in-process access with a versioned local control RPC (or a documented read-only/shared-state model).
- Decide which child owns the Discord HTTP interactions endpoint and how the supervisor routes it.
- Define independent readiness: web-ready and bot-ready; `/ready` must not mark the dashboard down just because the bot is restarting.
- Define update ownership: web-only updates restart web; bot-only updates restart bot; shared `utils`/`config` changes get a coordinated rolling policy.
- Define log/update-state ownership so the web child never reads bot memory.
- Produce a separate design review for this part. Do not implement until it is accepted.

**4B — Implementation**

- Supervisor runs two children: `web` (Flask/static/auth/dashboard/update UI) and `bot` (gateway/cogs/DB writers/control endpoint).
- Public routing: supervisor routes dashboard/static/auth to web and admin/control paths only to authorized endpoints. Prefer routing the Discord interaction endpoint directly to the bot child so a web-child failure does not stop slash commands; if web forwards instead, it must meet the 3-second interaction deadline and is tested while web is healthy.
- Bot-dependent dashboard routes return a structured `503` with bot state when the bot child is down.
- Independent update paths and version-skew handling.
- Per-child logging, readiness, restart policy, and resource limits.

**Required tests**

- Kill the web child: bot stays connected, slash commands still work, dashboard reconnects.
- Kill the bot child: dashboard/static/auth stay up; bot-dependent pages show degraded state; interactions behave as designed.
- Apply a web-only update: bot stays online and no commands are interrupted.
- Apply a bot-only update: dashboard stays available and reports bot restart progress.
- Apply a shared-code update: coordinated restart works, or the version-skew guard blocks it safely.
- Full E2E with test token + tunnel, including OAuth login, interactions, uploads/downloads, and update UI.

**Gate**

- Independent-failure and independent-update acceptance tests pass.
- No dual gateway session, duplicate command sync, or split-brain writer in any test.
- If this gate cannot be met without a large webapp rewrite, stop and keep the combined child; document the accepted limitation.

### Part 5 — Optional warm standby / hot reload work

**Goal:** reduce bot command downtime only if the measured benefit justifies the side-effect risk.

**Prerequisites**

- Parts 1–4 complete and stable.
- Cog lifecycle audit complete.
- Production uses MongoDB, or SQLite is explicitly excluded from warm mode.
- Memory headroom for a second bot child measured.
- Candidate side effects covered by tests.

**Write scope**

- `NIKO_LIFECYCLE=warm` support and lifecycle gates for writers, Discord actions, Lavalink/music, background loops, caches, and public interactions.
- Candidate prepare/promote/abort protocol and proxy switch.
- Candidate failure/rollback tests.

**Gate**

- Warm observation window shows no duplicate external side effects.
- Bot update keeps HTTP available and reduces command downtime to gateway connect/cutover.
- Candidate failure before promotion leaves the active child untouched; post-promotion failure has a tested recovery path.
- If the gate fails, leave warm standby disabled and keep the cold/split design. This part is not a launch blocker.

### Part 6 — Production launch and stabilization

**Write scope**

- Production start command and health-check configuration switch to the supervisor.
- Canary one instance, then the fleet if multiple instances exist.
- Monitoring/alerting on `/ready`, restart count, failed critical cogs, proxy errors, memory, and update failures.
- Runbook for on-call: rollback to direct bot start, rollback files, disable split, disable warm standby.
- 72-hour production soak and post-launch review.

**Gate**

- Full acceptance suite passes against a production-like staging environment with real token/tunnel.
- Rollback drill passes from every enabled flag.
- 72-hour soak has no unexplained restarts, duplicate side effects, or readiness flaps.
- Owner and reviewer sign-off.

**Launch rule:** do not enable a later part merely because it is written. Each flag defaults to off and is enabled only by its gate.

---

## 10. Test strategy and full E2E coverage

Testing is a release gate, not a follow-up. Each part has a test deliverable; a part cannot be signed off on “it starts locally.” The highest-risk paths must be exercised with a real Discord test application, a real public tunnel, and a real database, because that is where proxy, OAuth, interaction, gateway, and process-lifecycle bugs actually appear.

### 10.1 Test levels

| Level | What it covers | Runs in CI | Runs for release gate |
| --- | --- | --- | --- |
| L0 — Unit | State machines, parsers, readiness policy, config, header normalization, rollback file logic | Yes | Yes |
| L1 — Process/component | Supervisor with a fake child; signals; ports; control socket; proxy; process groups; log drain | Yes | Yes |
| L2 — Integration | Real Flask app, real DB, real updater, no Discord gateway where avoidable | Yes, with test DB | Yes |
| L3 — Full E2E | Real bot token, test guild, public tunnel, dashboard/OAuth, slash commands, interactions, updates, restarts | No by default | Yes, never skipped |
| L4 — Chaos/soak | Kills, hangs, network/DB failures, repeated restarts, 24-hour run | Nightly/optional | Yes for the relevant part |
| L5 — Production canary | Real deployment, feature flags, smoke commands, rollback drill | No | Yes before default enablement |

### 10.2 Test environments and fixtures

**Environment A — Local fake-child harness (Parts 1, 3)**

- No Discord token, no tunnel, no production data.
- `tests/supervisor/fake_child.py` implements the same lifecycle protocol as the real child and can simulate boot stages, hangs, crashes, bad readiness, ignored SIGTERM, and child processes that outlive their parent.
- Uses an ephemeral public port and ephemeral loopback child port.
- This is the first reviewable test target and must run without external services.

**Environment B — Staging/test Discord (Parts 2, 4, 5)**

- Dedicated Discord application and bot token, separate from production.
- Dedicated test guild, test channels, and test roles. Do not point tests at a production guild.
- Test database: a separate MongoDB database or a disposable SQLite file. Never use production data.
- The bot is invited only to the test guild and has the minimum intents/scopes needed for the tests.
- Commands that send messages or modify state are scoped to test channels and cleaned up by the fixture.

**Environment C — Public tunnel (Parts 2–4)**

- A Cloudflare tunnel exposes the supervisor's public test port to Discord and the test browser.
- Quick tunnel is acceptable for short-lived test runs; a named tunnel is preferred when a stable `PUBLIC_URL`/OAuth redirect is needed across runs.
- The tunnel URL is test configuration, not a secret, but it is temporary and must not be hardcoded.
- The Discord application's interactions endpoint and OAuth redirect URL are updated to the tunnel URL for the run, then restored.
- If the tunnel is unavailable, E2E tests fail with a clear setup error; they do not silently skip and count as a pass.

**Environment D — Production canary (Part 6)**

- Real deployment, supervisor flag enabled, split/warm flags still off unless their gates passed.
- Smoke tests only: health/readiness, dashboard login, one harmless slash command, one update poll, one controlled child restart.
- No destructive test commands, no test data in production.

### 10.3 Test tooling and package setup

The existing suite uses pytest (`tests/test_process_restart.py`), but pytest is not pinned in `requirements.txt`. Add a development-only dependency file rather than putting test tooling in the production image:

```text
requirements-dev.txt
  pytest
  pytest-asyncio
  pytest-timeout
  pytest-cov
```

Install for local/staging verification with:

```bash
python3 -m pip install -r requirements-dev.txt
```

Use the existing `psutil`, `requests`, `aiohttp`, and `flask` dependencies for process, HTTP, and proxy tests. Do not add a test framework that duplicates them. `cloudflared` is a test-environment binary, not a Python production dependency; install it in the test runner image or developer machine and record its version in the test evidence.

Add `pytest.ini` (or equivalent) with markers so local and CI runs are intentional:

```ini
[pytest]
markers =
    e2e: requires a real test bot and public tunnel
    requires_discord: requires TEST_DISCORD_TOKEN and a test guild
    requires_tunnel: requires a public tunnel URL
    chaos: destructive process/network fault injection
    slow: long-running soak or repeated-restart test
```

Planned test layout:

```text
tests/
  supervisor/          # fake child, supervisor state, proxy, signals
  integration/         # real Flask/app + test DB, no gateway where possible
  e2e/                 # real test bot, tunnel, dashboard, interactions
  chaos/              # kills, hangs, network/DB faults, soak
  conftest.py          # temp ports, temp dirs, process cleanup, test DB fixtures
```

### 10.4 Test secrets and temporary bot token handling

The test token is a real credential even if it is temporary. Treat it accordingly:

- Use a dedicated test application/token. Never reuse the production token.
- Put test values in `.env.local` or the workspace test environment. Never commit them, paste them into a test file, or print them in logs.
- Required keys: `TEST_DISCORD_TOKEN`, `TEST_GUILD_ID`, `TEST_CHANNEL_ID`, `TEST_PUBLIC_URL`, and a test `TEST_DB_URL`/`TEST_DB_PATH` if applicable.
- Use the platform's environment settings rather than asking for the token in chat. The token can be revoked immediately after the test campaign.
- Tests must redact the token, cookies, DSNs, and authorization headers from output.
- Restrict the test bot to the test guild. Do not enable privileged intents unless the feature under test requires them.
- Keep test commands idempotent and tagged so cleanup can remove test messages and temporary state.

### 10.5 Cloudflare tunnel test runbook

The tunnel is needed for full E2E because Discord must reach the interaction endpoint and the OAuth redirect must come back to the test dashboard.

1. Start the supervisor on an isolated test port with a disposable test database.
2. Start `cloudflared` against the supervisor's public port:

   ```bash
   cloudflared tunnel --url http://127.0.0.1:$TEST_SUPERVISOR_PORT
   ```

3. Capture the generated HTTPS URL and set `TEST_PUBLIC_URL` plus the Discord test application's interaction endpoint to `<url>/api/discord/interactions`.
4. Set the OAuth redirect URL to the test callback under the tunnel URL and update `DISCORD_REDIRECT_URI`/`PUBLIC_URL` in the test child environment.
5. Wait for DNS/tunnel readiness before starting E2E tests; fail fast if the public `/health` is not reachable.
6. Register the test command tree in the test guild only.
7. Tear down the tunnel, child, test database, and test command registrations. Revoke the temporary token at the end of the campaign.

Known limitation: a quick tunnel URL changes per run. Tests must read it from the environment; they must not embed it. A named tunnel is preferable if OAuth consent screens or Discord endpoint settings are painful to update repeatedly.

### 10.6 Full E2E scenarios

| Part | Scenario | Assertions |
| --- | --- | --- |
| 1 | Fake child boots, becomes ready, and serves through supervisor | `/health` 200, `/ready` 200, proxy body/headers correct, status file correct |
| 2 | Real bot boots under supervisor | Gateway ready, critical cogs loaded, dashboard reachable through public port |
| 2 | Dashboard OAuth login through tunnel | Redirect, callback, cookie/session, protected page all work |
| 2 | Slash command and HTTP interaction | Command reaches the bot; interaction endpoint returns a valid response before deadline |
| 2 | Kill child during boot | `/health` stays 200, `/ready` 503, supervisor restarts, site recovers, no orphan |
| 2 | Kill child while idle | Same, plus command works after recovery |
| 2 | Bot-area update from dashboard | One supervised restart, update response completes, new code active, command works |
| 2 | Failed probe/update | Old child remains, update reports failure, no partial file state |
| 2 | Rollback after a bad child | Last-good files restored, replacement child ready, command works |
| 3 | Hang without process exit | Heartbeat/HTTP timeout restarts; `/ready` reflects degraded state |
| 3 | Mongo unavailable | Strict mode fails readiness; no silent SQLite fallback |
| 3 | SQLite lock / disk-full simulation | Bounded error, no corruption, recovery after resource returns |
| 3 | Malformed beta manifest / duplicate update | Update refused/serialized; no double apply |
| 3 | Cloudflare tunnel drop | Dashboard returns bounded error; tunnel reconnect restores; bot gateway unaffected |
| 3 | Supervisor SIGKILL | Child is cleaned up; supervisor restart spawns exactly one new child |
| 4 | Kill web child | Bot stays connected; command still works; dashboard reconnects |
| 4 | Kill bot child | Dashboard/static/auth stay up; bot-dependent routes show structured 503 |
| 4 | Web-only update | Bot stays online; no command interruption; dashboard returns |
| 4 | Bot-only update | Dashboard stays available; bot restart progress visible |
| 4 | Shared-code/version-skew test | Coordinated restart or safe refusal; no incompatible route behavior |
| 5 | Warm candidate observation | No duplicate gateway, writes, messages, panel edits, Lavalink tasks, or command syncs |
| 5 | Candidate failure pre/post promotion | Old child untouched pre-promotion; tested recovery post-promotion |
| 6 | Production canary smoke | Health, readiness, login, one command, one controlled restart, no alerts |

### 10.7 Fault-injection matrix

| Scenario | Applies to | Expected behavior | Required evidence |
| --- | --- | --- | --- |
| Child exits immediately | 1–4 | Bounded backoff, alert, supervisor healthy, no tight restart loop | Restart timestamps, exit codes, `/status` |
| Child hangs but API answers | 2–4 | Heartbeat timeout restarts child; `/ready` 503 | Heartbeat/status timeline |
| Child hangs and API hangs | 2–4 | Process/HTTP timeout restarts child; no orphan | Supervisor logs, PID list |
| Kill at each boot stage | 2–4 | Recovery from import, API, DB, cogs, gateway stages; no half-written state | Per-stage test results |
| Candidate import fails | 5 | Old child keeps serving; candidate killed; update reports failure | Candidate logs, old-child health |
| Candidate cogs fail | 5 | Readiness fails or degrades per manifest; no cutover on critical failure | Cog status, gate decision |
| Two gateway sessions attempted | 2–5 | Test fails; only one active session; no flapping | Gateway/session assertions |
| Mongo unavailable | 2–4 | Strict mode refuses start/candidate; no SQLite fallback in production | Readiness/status, DB type |
| SQLite selected with warm mode | 5 | Warm standby refuses; cold restart only | Startup error, config assertion |
| Supervisor SIGTERM | 1–4 | Child drains, flushes, exits; supervisor exits cleanly | Logs, exit codes, elapsed time |
| Supervisor SIGKILL | 1–4 | Child dies via parent-death/process group; exactly one replacement on restart | PID/process tree snapshots |
| Port conflict | 1–2 | Supervisor fails fast with a clear log; no child spawn | Startup log, exit code |
| Stale control socket | 1–2 | New supervisor validates ownership and takes over safely | Socket/pid evidence |
| Two supervisors | 1–2 | Second fails closed; one public port owner | Process logs |
| Proxy upstream down | 1–3 | `/health` 200, `/ready` 503, bounded error/maintenance response | HTTP status/body |
| Tunnel disconnected | 2–4 | Public requests fail predictably; bot gateway unaffected; reconnect restores | Tunnel logs, bot status |
| Update during candidate boot | 5 | Serialized/aborted; no file race | Update run state |
| Duplicate update requests | 3 | One run wins; second refused/queued; no double restart | Update IDs, status |
| Old child killed during warm boot | 5 | Candidate aborts; supervisor starts cold child | Cutover state, logs |
| Rollback after cutover | 2–5 | Last-good files restored; replacement ready; gap measured | Rollback log, readiness timeline |
| Disk full during update | 2–3 | Staging fails before partial apply; old child untouched | Error, file hashes |
| Malformed/partial beta payload | 2–3 | Probe/staging rejects; no child restart | Update response, file hashes |
| Log flood | 1–3 | Supervisor drains output; child does not block; bounded retention | Log rate, process health |
| Bad network to Discord | 2–5 | Bounded connect retries; readiness fails; old child/rollback policy applies | Gateway logs, readiness |

### 10.8 Release-gate acceptance criteria

**Part 1**

- All supervisor harness tests pass without Discord, tunnel, or database.
- 100 fake-child restarts with no zombie/FD/port leak.
- Proxy and control-socket security tests pass.
- Reviewer signs the supervisor design and test evidence.

**Part 2**

- Full E2E with real test token and tunnel passes; no skipped P0 E2E tests.
- Cold restart, bot update, failed update, rollback, and interaction tests pass.
- `/health` remains 200 during every child restart; `/ready` behaves correctly.
- Non-supervised mode remains green.

**Part 3**

- Entire fault-injection matrix passes for enabled behavior.
- 24-hour staging soak passes with no unexplained restarts or duplicate side effects.
- Rollback drill and supervisor-kill drill pass.

**Part 4**

- Independent web/bot crash and update tests pass.
- No dual gateway, split-brain writer, or duplicate command sync in any run.
- Version-skew/shared-code test passes or safely refuses.

**Part 5**

- Warm observation window has zero duplicate side effects.
- Candidate pre/post-promotion failure tests pass.
- If the gate fails, the feature stays disabled; it is not a launch blocker.

**Part 6**

- Production-like staging acceptance suite passes.
- Rollback from every enabled flag passes.
- 72-hour production soak has no unexplained restart, duplicate side effect, or readiness flap.

Coverage expectations: 100% of supervisor states, state transitions, and documented control commands; at least 90% branch coverage for the supervisor module; every P0 row in the fault-injection matrix mapped to a named automated test. Coverage is not a substitute for the real-token/tunnel E2E gate.

> A skipped `requires_discord`, `requires_tunnel`, or `e2e` test is **not** a pass for a release gate. It is a blocked test that must be run before production enablement.

### 10.9 Test execution sequence

1. Install development dependencies: `python3 -m pip install -r requirements-dev.txt`.
2. Run fast tests: `pytest -m "not e2e and not chaos and not slow and not requires_discord and not requires_tunnel"`.
3. Run supervisor/process tests with the fake child: `pytest tests/supervisor -m "not e2e"`.
4. Start the staging test bot, disposable DB, supervisor, and Cloudflare tunnel.
5. Run the full E2E suite: `pytest -m "e2e"` with `TEST_DISCORD_TOKEN`, `TEST_GUILD_ID`, `TEST_CHANNEL_ID`, and `TEST_PUBLIC_URL` set in the test environment.
6. Run chaos/soak: `pytest -m "chaos or slow"` against staging, not production.
7. Capture evidence: command, commit, environment, timestamps, pass/fail counts, logs, `/status`, and rollback timing.
8. Tear down the tunnel, test child, test DB, and test command registrations; revoke the temporary token.

### 10.10 Load and soak tests

- Proxy throughput/latency under dashboard polling and static asset load.
- Repeated restarts (100+) with no FD/process/memory leak.
- Full-day soak with candidate observation disabled and enabled.
- Memory measurement for two children plus proxy.
- Verify no duplicate analytics rows, command syncs, panel edits, or external posts.

---

## 11. Rollout, flags, and rollback

### 11.1 Rollout sequence by part

| Stage | What is enabled | Where | Required gate |
| --- | --- | --- | --- |
| A | Part 1 supervisor harness only | Local/CI | Harness tests and design review |
| B | Supervisor + combined child, cold restart | Staging | Part 2 E2E |
| C | Supervisor + combined child | Production canary, flag on | Part 3 chaos/soak |
| D | Split web/bot children | Staging, then canary | Part 4 independent-failure tests |
| E | Warm standby | Staging only, disabled by default | Part 5 observation/soak |
| F | Supervisor default | Production | Part 6 acceptance + 72-hour soak |

No stage automatically enables the next. Production stays on the current direct start command until stage C's gate is signed off.

### 11.2 Flags and safe defaults

- `NIKO_SUPERVISED` — supervisor-managed child lifecycle. Default: off until Part 2 staging gate.
- `NIKO_SUPERVISOR_PROXY` — proxy vs FD mode, if both are retained. Default: whichever the ADR chooses.
- `NIKO_SPLIT_WEB` — separate web and bot children. Default: off until Part 4B gate.
- `NIKO_WARM_STANDBY` — candidate prewarm. Default: off; requires MongoDB and the lifecycle audit.
- `NIKO_STRICT_DB` — refuse silent Mongo → SQLite fallback. Default: off in local/dev, on in supervised staging/production.

Flags must be readable in `/status` and logs without exposing secrets. An invalid/partial flag combination fails closed with a clear error rather than starting a half-split topology.

### 11.3 Rollback by part

**Part 1**

- No production impact. Delete the harness branch or leave it unreferenced.

**Part 2**

- Switch the start command back to `python3 src/bot.py`.
- Keep `utils.handoff` and the existing update path intact.
- Disable `NIKO_SUPERVISED`; no code revert required.

**Part 3**

- Disable strict DB only if the backend is known-good; otherwise fail closed rather than fall back.
- Restore last-good update files and start the previous child.
- Disable supervisor canary and return to direct start if recovery is not bounded.

**Part 4**

- Disable `NIKO_SPLIT_WEB` and return to the combined child.
- If the web child is unhealthy, route to a maintenance response rather than a partially functional dashboard.
- Keep the bot child online while the web child is repaired or rolled back.

**Part 5**

- Disable `NIKO_WARM_STANDBY`; fall back to cold supervised restart or split-child restart.
- Kill any candidate and verify no orphaned tasks/players/connections before re-enabling.

**Part 6**

- Restore the prior start command/health path from the deployment dashboard.
- Keep the previous release files and update backups available until the soak is accepted.

### 11.4 Production prerequisites

- Stable `SESSION_SECRET`.
- Explicit health-check path owned by the supervisor.
- Confirmed database backend and strict fallback policy.
- Memory headroom for the proxy and, if enabled, a second child.
- Documented single-instance assumption.
- Monitoring/alerting on `/ready`, restart count, failed critical cogs, proxy errors, update failures, and memory.
- On-call runbook with the exact rollback command for every flag.
- Test evidence attached to the release review, including the real-token/tunnel E2E run.

---

## 12. Open decisions for reviewers

1. **Proxy vs FD inheritance:** Is an in-supervisor HTTP proxy acceptable, or do we prefer the smaller FD-passing design and accept a health-check gap during child boot?
2. **Web/bot split requirement:** Is a fully available dashboard during a bot restart a hard requirement, or is a structured 503/maintenance response acceptable? This decides whether Part 4 is mandatory or optional.
3. **Warm standby:** Is the cog lifecycle audit worth the reduction in command downtime, or is cold restart plus hot reload sufficient? This decides whether Part 5 is funded at all.
4. **Critical cogs:** Which cogs are required for readiness, and which are allowed to degrade?
5. **Database policy:** Is production guaranteed to use MongoDB, or must SQLite remain a supported supervised mode?
6. **Update ownership:** Should update orchestration stay in the Flask child, or move to a supervisor-owned control endpoint? This affects whether an update survives a dead child.
7. **Entry point:** Keep `src/bot.py` as the child, or introduce a new runtime entry point and update every path/probe/test together?
8. **Rollback durability:** Are file backups sufficient, or do we need versioned releases on persistent storage?
9. **Test ownership:** Who owns the temporary Discord test application/token, the test guild, and the Cloudflare tunnel? How long is the token valid, and who revokes it after the campaign?
10. **E2E gating:** Which E2E tests are mandatory for every release versus only for supervisor/process changes? The plan assumes every release touching the supervisor, child lifecycle, proxy, or update path must run the real-token/tunnel suite.
11. **Interaction ownership after split:** Does the web child forward Discord interactions to the bot child, or does the supervisor route the interaction path directly to the bot? A forwarding proxy that fails at the 3-second deadline is worse than direct routing.
12. **Shared-code updates after split:** Which files are web-only, bot-only, or shared? A shared `utils`/`config` change needs a coordinated restart policy or a version-skew guard.

---

## 13. First reviewable slice — stop after Part 1

The first implementation should be **Part 0 + Part 1 only**. Do not modify the bot, updater, or production start command in this slice.

### Concrete deliverables

1. `src/supervisor.py` that owns an ephemeral public port, serves `/health` and `/ready`, and proxies to a fake child.
2. A fake child under `tests/supervisor/` implementing the lifecycle protocol with deliberate boot/hang/crash/fail modes.
3. Control socket and status file with permission checks, restart backoff, process-group cleanup, and log draining.
4. `tests/supervisor/` tests for state transitions, proxy passthrough, signals, restarts, security, and resource cleanup.
5. A short supervisor protocol/design note and a runbook for running the harness.
6. A test evidence report: commands, pass counts, restart count, leak checks, and any known gaps.

### What is intentionally absent

- No `src/bot.py` changes.
- No `api_server.py` changes.
- No updater changes.
- No Render start-command change.
- No warm standby, split children, or real Discord token.

### Part 1 acceptance

- The harness suite passes locally and in CI with no external services.
- `/health` survives fake-child death; `/ready` correctly reports not-ready.
- 100 restarts produce no zombies, FD leaks, or port conflicts.
- Proxy behavior is verified for headers, cookies, redirects, uploads, downloads, and errors.
- The design note is approved by the maintainers.

**Stop here for review.** Only after that approval does Part 2 begin with the real bot, real staging E2E, temporary bot token, and Cloudflare tunnel. This sequence gives the team a tested supervisor shell before any production runtime behavior changes, while keeping the later architecture work — including the web/bot split and optional warm standby — explicitly planned and gated.
