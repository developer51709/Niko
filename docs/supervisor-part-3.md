# Supervisor Part 3 — Incident Recovery and Hardening

> **Status:** Implemented behind `NIKO_SUPERVISED=1`, staging only. Part 3 makes
> the supervised runtime fail closed, recover from a release that cannot boot,
> and expose enough history to diagnose an incident. It does not change the
> process topology (no split web child, no warm standby) and leaves the
> non-supervised `python3 src/bot.py` path untouched.
>
> **Date:** 2026-11-06

## 1. Strict database backend

A supervised production instance must never start on an empty local SQLite file
because MongoDB was briefly unreachable: every guild would look reset, and the
next successful boot would write to a different database.

- `NIKO_STRICT_DB=1` makes `database.create_pool()` refuse SQLite entirely: a
  missing `MONGODB_URL` raises immediately, and three failed MongoDB attempts
  raise instead of falling back. The error names the reason, so the supervisor
  log and readiness cause are actionable.
- `supervisor_readiness._ping_database()` independently fails readiness when the
  attached pool is not MongoDB under the same flag, which covers a pool created
  before the flag was set or replaced by a hot-reloaded module.
- Default stays off, so local development and non-supervised deployments keep
  the existing fallback. The flag is documented in `env.example`.

With strict mode on and MongoDB down, the child reports the failure and exits;
the supervisor's restart budget (section 3) bounds the loop instead of
restarting forever, and `/ready` stays 503 because no child is ready.

## 2. Last-good rollback after a failed post-update boot

The update flow already refuses a bot core that cannot import, before asking the
supervisor to restart. The remaining risk was a release that imports cleanly but
dies during real boot (a missing runtime file, a bad environment assumption).
The process is gone by then, so the updater cannot repair it.

Now:

1. Immediately before requesting the supervised restart, the updater writes
   `data/updates/pending.json` with the run id, the area, the run's backup
   directory, and every changed file with its status.
2. The supervisor reads that file itself — it still imports no application code
   — and when a child that never became ready exits, it restores each file from
   the run's backup, deletes files the update had added, and drops the restored
   source's bytecode so a stale `.pyc` cannot shadow it.
3. The restore is recorded in history as `rollback_applied` (with the run id,
   restored and removed counts) and the pending record is retired as
   `pending.json.rolledback-<timestamp>`. The supervision loop then boots the
   last-good files.
4. When a child does become ready (or degraded), the pending record is retired
   as `pending.json.confirmed-<timestamp>` and history records
   `update_confirmed`. A release that boots is never rolled back later.
5. A pending record with an absolute path, `..`, or a target outside
   `--update-root` is refused: history records `rollback_failed` with the
   reason, the record is retired, and nothing outside the tree is touched.

The status file exposes `pending_update` (`run_id`, `area`, `requested_at`,
`changes`) so the owner can see an unconfirmed restart. The rollback applies
once per pending record; a failure is not retried in a loop.

Rollback is deliberately limited to the bot area. It is the only area whose
apply path ends in a supervised restart; every other area rolls back in-process
where the old code is still running.

## 3. Restarts stay bounded

Part 1/2 already provide exponential backoff, a consecutive-failure counter, a
counter reset after the child has been ready for `--restart-reset-after`, and
`--max-restarts`. Part 3 relies on those for strict-database outages and failed
releases:

- a child that dies before readiness increments the failure counter;
- the counter is reset after a child stays ready, so one bad release does not
  exhaust the budget forever;
- `--max-restarts` (off by default) stops the loop in `state: failed` and waits
  for a control `restart` instead of restarting forever. Supervised production
  should set it.

## 4. Hostile update inputs

These branches already existed and are now covered by named tests:

- a malformed beta manifest is reported and `plan` returns no areas;
- a manifest that is not JSON is reported the same way;
- a downloaded file whose hash does not match is refused before it is written;
- a full disk during staging restores the previous file and fails the run;
- a second update request while one is running is refused with
  `An update is already being applied.`

## 5. Evidence

```text
PYTHONPATH=src .venv/bin/python -m pytest tests/supervisor \
  tests/test_process_restart.py tests/test_supervisor_readiness.py \
  tests/test_supervisor_control.py tests/test_supervised_updates.py \
  tests/test_api_server_supervised.py tests/test_update_chaos.py \
  tests/test_strict_db_mode.py tests/test_sqlite_concurrency.py \
  -q --timeout=240
→ 76 passed in 93.89s
```

New coverage in this part:

- `tests/supervisor/test_last_good_rollback.py` — restore on failed boot,
  confirm on ready, refusal of an unsafe path, and removal of an added file;
- `tests/test_strict_db_mode.py` — strict refusal without MongoDB, strict
  refusal when MongoDB is unreachable, the unchanged non-strict fallback, and
  both readiness outcomes;
- `tests/test_update_chaos.py` — malformed/non-JSON manifest, tampered
  download, disk-full restore, duplicate run;
- `tests/test_supervised_updates.py` — the restore point is written before the
  restart request and cleared when the request is rejected;
- `tests/supervisor/test_strict_db_integration.py` — the real `create_pool`
  path inside a supervised child: no SQLite file, readiness 503, and `state:
  failed` once the restart budget is spent;
- `tests/supervisor/test_single_writer.py` — five supervised restarts with a
  concurrent-child sample every 20 ms, one startup effect per boot, no orphan;
- `tests/supervisor/test_soak_local.py` — 30 seconds of continuous `/health`
  and proxied `/api/health` polling with a restart every 6 seconds
  (`4 restarts, 0 health failures, 0 API failures, FDs 12→13, RSS +460 KiB`);
- `tests/test_sqlite_concurrency.py` — a held write lock makes the pool's write
  fail with `database is locked` instead of silently succeeding;
- `tests/supervisor/test_supervised_api.py` — stalled-upstream bounded 503,
  and supervisor SIGKILL taking the real Flask child with it.

## 6. Local substitutes for unavailable infrastructure

The staging drills in the design review assume a public host, a tunnel, a real
Discord token, and 24 hours. None of those are available here. Each was
replaced with the closest local equivalent, and the gap is stated rather than
waved away.

| Staging drill | Local substitute | Proves | Does not prove |
| --- | --- | --- | --- |
| 24-hour soak | 30-second soak against the real supervisor and the real Flask child, polling `/health` and `/api/health` continuously with a restart every 6 seconds (`test_soak_local.py`) | No hang under steady proxied traffic and repeated restarts; FDs and RSS stay flat (12→13 FDs, +460 KiB) | Multi-hour drift, memory pressure, real Discord traffic |
| Duplicate-side-effect audit | Five supervised restarts while sampling the process tree every 20 ms; every boot appends exactly one line to a startup-effect log (`test_single_writer.py`) | At most one child is ever alive; each boot's startup effect runs once; no orphan survives the supervisor | Discord messages, analytics rows, panel edits — those need a real bot |
| Tunnel disconnected / upstream wedged | `SIGSTOP` the real child, then request through the proxy with `--proxy-timeout 1` (`test_supervised_api.py`) | A stalled upstream gets a bounded maintenance 503; `/health` and `/ready` stay usable | External DNS, TLS, or tunnel-edge behaviour |
| Mongo unavailable with strict mode | Supervised harness child running the real `create_pool` with an unreachable connector (`test_strict_db_integration.py`) | No SQLite file is created, readiness stays 503, the restart budget ends in `state: failed` | Real network timeouts, SRV/auth failures, multi-node elections |
| SQLite selected / two writers | A second connection holds `BEGIN IMMEDIATE` while the pool writes (`test_sqlite_concurrency.py`) | The second write fails loudly with `database is locked` | Behaviour of two full bot processes (explicitly forbidden) |
| Supervisor SIGKILL | Kill the supervisor with the real Flask child running (`test_supervised_api.py`) | The child dies with its parent; no orphan is left behind | Recovery on a platform that restarts the service |
| Supervisor SIGTERM | Existing `test_sigterm_stops_the_child_and_writes_a_stopped_status` | Child drains, supervisor exits 0, status records `stopped` | Platform shutdown grace-window differences |

Still not locally verifiable:

- user-initiated slash commands during or after a restart (needs Discord; the
  same restart path was confirmed manually on the live preview);
- background-job drains on shutdown (needs the cog lifecycle audit reserved for
  a later part);
- the 24-hour soak and the real staging drills listed above.

## 7. Remaining Part 3 gate

What is left genuinely needs infrastructure that is not in this workspace:

- The full 24-hour soak, and the parts of the duplicate-side-effect audit that
  only a real bot can produce (Discord messages, analytics rows, command syncs,
  panel edits).
- User-initiated slash commands during and after a restart.
- Startup/shutdown drains for background jobs that write during shutdown; that
  needs the cog lifecycle audit the design review reserves for a later part, so
  it is intentionally not claimed here.
- One confirmation run of the Part 2 cold update and rollback on the
  production-like instance, which the local gate in Part 2 mirrors.

Production now starts through the supervisor (`python3 src/supervisor.py`); the
direct `python3 src/bot.py` command remains a local-debug fallback and warns
when used. See [`supervisor-incident-runbook.md`](supervisor-incident-runbook.md)
for what to check when the supervised runtime misbehaves.
