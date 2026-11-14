# Supervisor Part 2 — Real Child, Readiness, and Supervised Updates

> **Status:** Implemented behind `NIKO_SUPERVISED=1`. The default direct
> `python src/bot.py` path is unchanged, including the existing in-place
> `utils.runtime.handoff` fallback.
>
> A managed preview with a real Discord token is now running the supervisor as
> its entry point. It has been exercised for real gateway boot, MongoDB
> readiness, control restarts, crash recovery, proxy traffic, preview
> reachability, Discord OAuth, the staff guild directory, guild settings, and
> live slash commands. The bot-area update and rollback paths are now exercised
> end to end locally through a loopback beta feed, with no second host involved
> (see section 8), and every boot stage has a kill test (section 9). The
> remaining Part 2 gate is one confirmation run against a real production-like
> instance before rollout.

## 1. Runtime shape

```text
supervisor.py
├─ public 0.0.0.0:$PORT
│  ├─ /health, /ready
│  └─ proxy → 127.0.0.1:<ephemeral child port>
└─ child: python src/bot.py
   ├─ NIKO_SUPERVISED=1
   ├─ NIKO_SUPERVISOR_CONTROL_FD=<inherited lifecycle fd>
   ├─ NIKO_SUPERVISOR_CONTROL_SOCKET=<local control socket>
   ├─ Flask on 127.0.0.1:0
   └─ lifecycle JSON + bot-loop heartbeats
```

The child reports the port the kernel actually assigned. It never binds
`PORT`, `PORT + 1`, or a pre-bound port. `src/bot.py` remains the child entry
point.

## 2. Child behavior

- `process_started` is sent before startup work begins.
- A heartbeat task runs on the bot's own event loop, so a blocked loop is
  visible to the supervisor.
- The API server is started with `host="127.0.0.1"` and `port=0`; the actual
  port is sent in `api_listening`.
- `db_ready` and `cogs_loaded` are emitted after their startup steps.
- `gateway_ready` is emitted when Discord dispatches READY.
- `on_ready` waits for the full startup chain before reporting `ready`.
- SIGTERM sends `draining`, closes the bot, and the entrypoint sends `stopped`.
- A supervised child never calls `handoff.adopt()` or `handoff.schedule()`.

## 3. Readiness policy

`src/supervisor_readiness.py` checks:

1. **Database** — the pool exists and answers a ping (`SELECT 1` for SQLite,
   `admin.command("ping")` for MongoDB).
2. **Gateway** — `bot.is_ready()` is true, expected shards are present, and no
   listed shard is closed.
3. **Critical cogs** — default
   `cogs.system,cogs.admin,cogs.utility`, overridable with
   `NIKO_CRITICAL_COGS`. A missing or failed critical cog is fatal.
4. **Startup errors** — `init_database`, `load_cogs`, and
   `preload_economy_cache` are fatal; other startup steps only degrade the
   process. The critical list is overridable with
   `NIKO_CRITICAL_STARTUP_STEPS`.
5. **Interactions endpoint** — a missing public key degrades readiness because
   gateway-delivered interactions can still work.

A critical failure sends `readiness_failed` and the supervisor replaces the
child. A non-critical failure sends `degraded`; the supervisor keeps serving it
and exposes the checks in its status file.

## 4. Supervised bot updates

For the `bot` area the updater now:

1. stages and validates the files;
2. runs the throwaway import probe with all `NIKO_SUPERVISOR_*` and
   `NIKO_SUPERVISED` markers stripped;
3. confirms the API is serving;
4. persists `data/updates/last.json`;
5. asks the supervisor over the local control socket to restart the child, with
   a short delay (default 2 seconds, `NIKO_SUPERVISED_RESTART_DELAY`);
6. returns the HTTP response before the supervisor stops the child.

If the supervisor rejects the request, the bot-area files are restored and the
run is recorded as failed. A direct, non-supervised process still uses
`_inplace_handoff()` and `handoff.schedule()`.

## 5. Evidence collected locally

```text
.venv/bin/python -m pytest tests/supervisor \
  tests/test_process_restart.py tests/test_supervisor_readiness.py \
  tests/test_supervisor_control.py tests/test_supervised_updates.py \
  tests/test_api_server_supervised.py -q --timeout=120
→ 45 passed
```

The integration test starts the standalone supervisor with
`tests/supervisor/supervised_api_child.py`, which imports the **real**
`src/api_server.py` Flask app. It verifies:

- the child API binds an ephemeral loopback port;
- `/api/health` reaches the real Flask app through the supervisor proxy;
- a control-socket restart replaces the child cleanly and serves again.

Existing direct-mode restart tests remain green:

```text
.venv/bin/python -m pytest tests/test_process_restart.py -q --timeout=30
→ 13 passed
```

Additional affected suites:

```text
.venv/bin/python -m pytest tests/test_bot_card.py tests/test_handoff_logging.py \
  tests/test_multimodal_ai.py tests/test_update_events.py \
  tests/test_update_startup.py -q --timeout=60
→ 40 passed
```

## 6. Live preview evidence (2026-11-06)

The managed preview ran `python3 src/supervisor.py` with the real test bot and
MongoDB. The final preview is reachable on port `5173`.

Observed on the live child:

- `/health` and `/ready` returned `200`; `/ready` reported:
  `mongodb` database OK, five gateway shards OK, critical cogs OK, interactions
  endpoint OK, and no startup errors.
- `/api/health` and `/api/status` returned `200` through the supervisor proxy;
  `/api/status` reported `operational`, 25 loaded cogs, and five connected
  shards.
- A control-socket restart kept the supervisor PID unchanged, replaced the
  child PID, incremented `child_starts`, and returned `/ready` to `200`.
- During the restart, `/ready` returned `503` with `child is draining`,
  `child api is not listening`, and `child state: api_listening` before
  recovering.
- SIGKILLing the child kept `/health` at `200`, restarted it, and returned
  `/ready` to `200`; the supervisor recorded the crash and recovery in history.
- The real Flask app answered through the supervisor after both restarts.
- The preview URL was verified externally against the supervisor listener.
- `/auth/status` returned `oauth_available: true` through the proxy, and
  `/auth/login` on the external preview URL redirected to Discord's authorize
  endpoint with the preview callback and `identify guilds guilds.join` scopes.
- Manual browser verification passed: Discord OAuth sign-in completed, the staff
  guild directory page loaded, and guild settings loaded and worked through the
  supervisor proxy (confirmed by the project owner on 2026-11-06).
- Manual interaction verification passed: slash commands are fully functional in
  the test guild through the supervised child (confirmed by the project owner on
  2026-11-06).
- The preview runs a beta instance, so it correctly has no `BETA_INSTANCE_URL`.
  `BETA_UPDATE_TOKEN` is present for the beta feed’s read side, but the owner
  update feed needs `BETA_INSTANCE_URL` to discover changed files, and that value
  belongs only on an instance that pulls *from* beta. Its absence here is
  expected configuration, not a missing secret.

## 7. Status panel API probe fix

The staff status panel reported the API as down while the website and dashboard
API were serving normally.

**Cause.** `_collect_status` probed `http://127.0.0.1:$PORT/api/health`. Inside a
supervised child that is the wrong address twice over: `PORT` is the
supervisor’s public port and is removed from the child environment, and the
child’s Flask app binds an ephemeral loopback port reported in `api_listening`.
The probe therefore hit a port nothing was serving on and recorded a false
failure.

**Fix.** `_local_api_base()` in `src/cogs/staff/panels/status.py` now reads
`api_server.listening_port()`, which returns Werkzeug’s actual bound
`server_port` (including a kernel-assigned port after `port=0`). The historical
`$PORT` / `5000` lookup remains only as a fallback when no server is running.
The public website check still probes `PUBLIC_URL` independently, so the two
signals cannot mask each other.

**Regression coverage.** `tests/test_status_panel_music.py` adds
`test_local_api_probe_uses_the_actual_bound_port`, which pins
`api_server.listening_port` to `43210` and asserts the probe base, plus a source
assertion that `_collect_status` builds its URL through `_local_api_base()`.

```text
PYTHONPATH=src .venv/bin/python -m pytest tests/test_status_panel_music.py \
  tests/test_status_panel_translation_card.py tests/test_version_consistency.py \
  -q --timeout=60
→ 23 passed
```

After a control restart of the live child to load the fix, `/health`, `/ready`,
`/api/health`, and `/api/status` all returned `200` and `/ready` reported the
full startup chain green. Probing the child’s recorded loopback port directly
(`data/run/supervisor.json` → `child.api_port`) also returned `200` for
`/api/health` and `/api/status`, which is exactly the URL the panel now uses.

## 8. Bot-area update gate without a second host

`tests/supervisor/test_beta_update_gate.py` runs the update/rollback gate
entirely on one machine. It starts no second bot and opens no second gateway
session.

What stands in for production:

- a copy of the tree in pytest's `tmp_path`, so the working checkout is never
  touched;
- the real `src/supervisor.py` from that copy, with its working directory in the
  copy — real child spawn, public port, status file, control socket, watchdog;
- a real supervised child (`tests/supervisor/update_gate_child.py`) serving the
  production `api_server.py` Flask app on an ephemeral loopback port, which is
  the same call `src/bot.py` makes in supervised mode;
- the real updater (`webapp.updates.apply`) executed *inside* that child, where
  the dashboard's owner route runs it;
- a loopback HTTP server that speaks beta's feed contract
  (`/api/updates/manifest.json`, `/api/updates/file`, `X-Update-Token` checked,
  404 without it), publishing the copy's bot area plus a deliberate change.

**Scenario 1 — cold bot-area update.** Beta republishes `src/api_server.py` with
a marker constant. The updater pulls the manifest, downloads the file, backs up
what was there, writes the new copy, and the import probe runs `src/bot.py` and
exits 0. The updater asks the supervisor for a restart and returns; the
supervisor replaces the child exactly once (`child_starts` 1 → 2), and the new
child's boot record carries the marker, which proves the restarted process is
running the updated core. `/api/health` is 200 through the proxy. The test also
asserts `last.json` records `supervised_restart: true` with `handoff: false`, the
backup equals the previous file, and a request without the token gets 404.

**Scenario 2 — unimportable bot core.** Beta republishes `src/bot.py` with an
import that cannot resolve. Staging writes it, the probe fails, and the area is
restored byte for byte. The run is recorded as failed with `rolled_back: true`,
no restart is requested, the child PID and `child_starts` are unchanged, and
`/ready` and `/api/health` stay 200. A fresh probe on the rolled-back tree exits
0, and a controlled restart still comes up ready — the last-good state.

```text
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/supervisor/test_beta_update_gate.py -q --timeout=300
→ 2 passed in 13.34s

PYTHONPATH=src .venv/bin/python -m pytest tests/supervisor \
  tests/test_process_restart.py tests/test_supervisor_readiness.py \
  tests/test_supervisor_control.py tests/test_supervised_updates.py \
  tests/test_api_server_supervised.py -q --timeout=180
→ 47 passed in 35.33s
```

What it does not cover:

- a real `src/bot.py` child, which needs a Discord token and would open a second
gateway session. The harness child serves the same production Flask app, and the
real core is validated by the updater's own import probe, which is the pre-restart
gate that decides whether the child is replaced at all.
- a user-initiated slash command *after* the update. That was confirmed manually
on the live preview, whose child is replaced through the same supervised restart
path exercised here.

## 9. Boot-stage kill tests

`tests/supervisor/test_boot_stage_kills.py` kills the child at every lifecycle
event it reports — `process_started`, `api_listening`, `db_ready`,
`cogs_loaded`, `gateway_ready`, and `ready` — and proves recovery. Three knobs on
the fake child make the kill land deterministically: `FAKE_CHILD_STAGE_MARKER`
touches one file per event sent, `FAKE_CHILD_STAGE_HOLD` parks the child at a
named stage, and `FAKE_CHILD_STAGE_HOLD_ONCE` makes only the first child hold so
the replacement boots normally.

For every stage the test asserts:

- `/health` is 200 while the child is held and after the kill;
- `/ready` is 503 until the stage is `ready`, and 503 again while no child is
  ready;
- the proxy answers a bounded maintenance 503 —
  `{"error": "service unavailable", "retry_after": 1}` with `Retry-After: 1` —
  in under two seconds rather than hanging;
- the supervisor replaces the child, `/ready` returns to 200, the proxied route
  serves again, `child_starts` advances, and the killed PID is gone.

`tests/supervisor/test_supervised_api.py` repeats the kill against the real
Flask child: `/api/health` goes 200 → bounded 503 → 200 after recovery.

```text
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/supervisor/test_boot_stage_kills.py tests/supervisor/test_supervised_api.py \
  -q --timeout=180
→ 9 passed in 18.12s

PYTHONPATH=src .venv/bin/python -m pytest tests/supervisor \
  tests/test_process_restart.py tests/test_supervisor_readiness.py \
  tests/test_supervisor_control.py tests/test_supervised_updates.py \
  tests/test_api_server_supervised.py -q --timeout=180
→ 54 passed in 46.15s
```

### Remaining Part 2 gate

Still required before production rollout:

- One confirmation run of the cold update and rollback on a real production-like
  instance configured with both `BETA_INSTANCE_URL` and `BETA_UPDATE_TOKEN`
  before rollout. The preview is the beta instance itself, so it correctly has no
  `BETA_INSTANCE_URL`; the local gate above covers the same code paths.
- Recording that run in the staging runbook.
