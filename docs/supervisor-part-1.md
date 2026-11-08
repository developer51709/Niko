# Supervisor Part 1 — Isolated Shell and Harness

> **Status:** Implemented behind the standalone `src/supervisor.py` entry point.
> Part 2 now adds the supervised real-child mode, readiness, and supervised bot
> updates; see [`supervisor-part-2.md`](supervisor-part-2.md). Production startup
> remains opt-in and the default direct `src/bot.py` path is unchanged.
>
> See [`supervisor-design-review.md`](supervisor-design-review.md) for the full
> multi-part plan. This note records the concrete Part 1 protocol and the
> evidence required before Part 2 integrates the real bot.

## 1. What exists

| File | Purpose |
| --- | --- |
| `src/supervisor.py` | Public HTTP server, proxy, child lifecycle, watchdog, control socket, status file, signal handling |
| `src/supervisor_protocol.py` | Dependency-free newline-JSON child protocol and Linux parent-death helper |
| `tests/supervisor/fake_child.py` | Controllable child with HTTP fixtures and failure modes |
| `tests/supervisor/conftest.py` | Subprocess fixture, status polling, control client, cleanup |
| `tests/supervisor/test_supervisor.py` | Lifecycle, proxy, security, crash, and leak tests |
| `requirements-dev.txt` | Development-only pytest tooling |
| `pytest.ini` | Test markers from the design review |

The supervisor imports only the standard library, `aiohttp`, and `multidict`. It
does not import `discord`, `webapp`, cogs, the database, or `src/bot.py`.

## 2. Runtime shape

```text
supervisor.py
├─ public HTTP server on 0.0.0.0:$PORT
│  ├─ GET /health                  supervisor liveness; always 200 while running
│  ├─ GET /ready                   child readiness; 200 or 503
│  ├─ GET /supervisor/status       opt-in only; 404 by default
│  └─ *                             reverse proxy to active child loopback API
├─ local Unix control socket       default data/run/supervisor.sock, mode 0600
├─ atomically replaced status file default data/run/supervisor.json
└─ one supervised child
   └─ inherits a socketpair FD and reports newline-delimited JSON
```

The public listener is started before the child. If the child is absent, hung,
restarting, or failed, `/health` still answers and `/ready` returns 503. The proxy
returns a bounded JSON 503 with `Retry-After` when there is no API target.

## 3. Child lifecycle protocol

### Transport

- The supervisor creates an `AF_UNIX` `socketpair`.
- The child end is passed through `pass_fds` and named by
  `NIKO_SUPERVISOR_CONTROL_FD`.
- The supervisor sets `NIKO_SUPERVISED=1` and
  `NIKO_SUPERVISOR_PUBLIC_PORT=<public port>`.
- The child must **not** bind the public port. In Part 2 it binds an ephemeral
  loopback port and reports it in `api_listening`.
- Messages are one JSON object per line, UTF-8, no embedded newlines.
- Every message includes `protocol`, `event`, `pid`, and `at`.
- The supervisor enforces a 64 KiB line limit. A malformed event is logged; an
  oversized event terminates the child.

### Events

| Event | Required fields | Meaning |
| --- | --- | --- |
| `process_started` | — | Python is running and the reporter is connected |
| `api_listening` | `port` | Loopback API is bound; proxy may use it |
| `db_ready` | optional `backend` | Database pool exists and answers |
| `cogs_loaded` | optional counts | Extension loading finished |
| `gateway_ready` | optional shard data | Gateway is ready |
| `ready` | — | All critical checks passed |
| `degraded` | optional `reason` | Serving, but a non-critical check failed |
| `readiness_failed` | `reason` | Critical readiness failure; supervisor replaces child |
| `draining` | — | Child is stopping deliberately |
| `stopped` | — | Child is about to exit cleanly |
| `heartbeat` | — | Sent every few seconds from the child event loop |
| `error` | `message` | Diagnostic error |

`state` is also accepted as an event name with a `state` field, so a future child
can send `{"event":"state","state":"ready"}` without changing the supervisor.

### Readiness policy in Part 1

The supervisor considers a child ready only when:

1. It is the current child and has not exited.
2. It reported a valid loopback `api_listening.port`.
3. It reported `ready`.
4. Its last heartbeat is within `--heartbeat-timeout`, once the `--ready-grace`
   settling window since the first `ready` has elapsed. A cold shared host
   finishes its startup chain after reporting ready and blocks the child's
   event loop for seconds at a time, so heartbeats are not expected during
   that window.

A child that has not reported `ready` is not expected to heartbeat at all:
startup failures normally exit the process, which the supervisor sees
immediately, and a boot that never finishes is bounded by `--startup-timeout`.

A missed heartbeat is a *stall report*, never a death certificate.  A container
sharing a throttled CPU can stop being scheduled for minutes while its process
is healthy, so the watchdog checks the child's pid before acting: a process
that is gone is reported by its exit code, and a process that is still running
is left alone unless it has sent nothing at all for `--stall-timeout` (by
default four times `--heartbeat-timeout`).  A heartbeat that resumes clears the
stall and the child keeps running.

The real bot will add database, critical-cog, startup-error, and shard checks in
Part 2; Part 1 proves the transport and state machine without those dependencies.

## 4. Supervisor state machine

```text
starting → active → restarting → starting → active
             ↘ degraded
             ↘ failed
             ↘ stopped
```

- Unexpected child exit increments `restart_count` and enters `restarting`.
- The supervisor applies exponential backoff:
  `min(initial * 2^(failures-1), max)`.
- A control-socket restart is deliberate: it terminates the child and starts a
  replacement without counting a crash or applying backoff.
- A missed heartbeat or startup timeout terminates the child with SIGTERM,
  waits `--shutdown-timeout`, then sends SIGKILL.
- The child runs in its own session/process group. Shutdown and restart use
  `killpg`, which also removes leaked descendants.
- `max_restarts > 0` opens a circuit breaker after that many consecutive
  failures. A control restart clears it.
- A child that stays ready for `--restart-reset-after` resets the consecutive
  failure count.

## 5. HTTP proxy decision

Part 1 uses an **aiohttp reverse proxy** rather than inherited-FD serving.

Why:

- The supervisor can answer `/health` while no child owns the API.
- The child can bind an ephemeral loopback port, so there is no hardcoded
  `PORT + 1` and no pre-bind race with another process.
- aiohttp already exists in the production dependency set.
- It gives us streaming request/response bodies and access to response headers
  needed for cookies, ranges, uploads, and downloads.

The proxy:

- Preserves `Host`, method, path, query string, and body.
- Overwrites `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-For`, and
  `X-Forwarded-Port`; client-supplied values are not trusted.
- Removes hop-by-hop headers and headers named by `Connection`.
- Preserves multiple `Set-Cookie` values, redirects, cache headers, content
  length, content type, `Range`, and `206` responses.
- Rejects `Upgrade` requests with 501 rather than corrupting a WebSocket-style
  connection. The current dashboard has no WebSocket or SSE endpoints.
- Rejects requests with both `Transfer-Encoding` and `Content-Length`.

The FD-inheritance option remains available as a future fallback if proxy
overhead or header behavior proves unacceptable. Do not mix both models without
an explicit decision.

## 6. Status file

`data/run/supervisor.json` is written atomically with `os.replace` and mode
`0600`. It includes:

- supervisor PID, state, readiness, public port, start time, uptime;
- control socket path;
- current child PID, state, readiness, loopback port, last heartbeat/error;
- restart count, child start count, consecutive failures, last stop reason;
- the last 50 lifecycle events.

It contains no environment secrets or authorization headers.

## 7. Control socket

Default: `data/run/supervisor.sock`, mode `0600`, under a `0700` run directory.
On Linux the supervisor checks `SO_PEERCRED` and rejects a different UID. A
one-line JSON request gets one-line JSON response.

Commands:

```json
{"command":"ping"}
{"command":"status"}
{"command":"restart","reason":"bot update","delay":0.25}
{"command":"shutdown"}
```

`restart` is accepted before the child is stopped, so a future updater can return
its HTTP response before the process disappears. `delay` defers the request for
callers that need a response drain window.

## 8. Running the harness

Install development dependencies once:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run only the isolated supervisor tests:

```bash
pytest tests/supervisor -q
```

The tests use ephemeral public and child ports, no Discord token, no tunnel, and
no database. To run a single fake child manually:

```bash
python3 src/supervisor.py \
  --port 0 \
  --child tests/supervisor/fake_child.py \
  --status-file /tmp/niko-supervisor.json \
  --control-socket /tmp/niko-supervisor.sock \
  --lock-file /tmp/niko-supervisor.lock \
  --startup-timeout 5 \
  --heartbeat-timeout 2 \
  --shutdown-timeout 0.5
```

Set `FAKE_CHILD_MODE` to `normal`, `crash`, `crash-after-api`, `fail-readiness`,
`hang-before-api`, `hang-after-ready`, `ignore-sigterm`, or `leak-child`.

## 9. Part 1 test evidence

The harness covers:

- separate `/health` and `/ready` behavior;
- public availability during child restart, startup hang, heartbeat loss, and
  crash;
- readiness 503 while no ready child exists;
- control-triggered restart and replacement;
- SIGTERM drain and SIGTERM-ignoring child escalation;
- supervisor SIGKILL with process-group cleanup;
- 100 crash/restart cycles with process/FD checks;
- proxy forwarding of host and spoofed-forwarding-header rejection;
- multiple cookies, redirects, downloads, range requests, and multipart uploads;
- 503 behavior when the child has no API;
- control socket mode, unknown-command rejection, and local-only status;
- second-supervisor fail-closed locking;
- child log-flood draining while `/health` stays responsive.

Run the suite after every supervisor change and attach the command, commit,
pass/fail count, and any skipped tests to the Part 1 review.

## 10. Known limitations and Part 2 handoff

- The real bot still has no supervised child mode. Part 2 must bind Flask to an
  ephemeral loopback port, report readiness, disable `handoff.schedule()` when
  supervised, and launch through this supervisor.
- Part 1 deliberately does not verify cogs, database, Discord, OAuth, the
  updater, or the interaction endpoint. Those are Part 2 gates.
- The proxy currently derives `X-Forwarded-Proto` from the direct connection.
  Part 2 must verify TLS-terminated public behavior or configure a trusted proxy
  scheme before OAuth is accepted.
- The status file is runtime state, not durable storage; `data/` is ephemeral on
  the hosted deployment.
- No production start command was changed. The non-supervised
  `python3 src/bot.py` path remains the fallback.
