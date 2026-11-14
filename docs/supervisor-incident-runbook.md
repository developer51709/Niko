# Supervisor Incident Runbook

How to find out what a supervised deployment is doing and what to do when it is
not serving. The supervisor owns the public port; the bot runs as its child.

## Where to look

| What | Where |
| --- | --- |
| Status file (atomic JSON) | `data/run/supervisor.json` (`--status-file`) |
| Control socket (`0600`) | `data/run/supervisor.sock` (`--control-socket`) |
| Snapshot file lock | `data/run/supervisor.lock` (`--lock-file`) |
| Restore point for a bot update | `data/updates/pending.json` |
| Update result and backups | `data/updates/last.json`, `data/updates/backups/<run>/` |
| Logs | Supervisor stderr; child lines pass through unchanged in the bot's console style |

`/health` is the supervisor's own liveness. `/ready` is the active child's
readiness and returns `503` with a reason. `/supervisor/status` only exists when
started with `--status-public`; otherwise use the status file or the control
socket. Its `children` map names `db`, `web` and `bot`; `child` stays the primary
(dashboard) child for older readers.

Control commands are `ping`, `status`, and `restart` (with optional `delay` and
`reason`). Example:

```bash
python3 - <<'PY'
import json, socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.connect("data/run/supervisor.sock")
    s.sendall(b'{"command": "status"}\n')
    print(json.dumps(json.loads(s.makefile().readline()), indent=2))
PY
```

## Triage

| Symptom | Check | Action |
| --- | --- | --- |
| `/health` 200, `/ready` 503 | status `child.state`, `child.last_error`, `child.readiness`, `last_error` | Wait one restart if `starting`; otherwise fix what the readiness checks name. The child is replaced after the startup timeout. |
| `/health` not answering | Is the supervisor process alive? status file fresh? | Start it again. If it exits immediately it logs why (port in use, lock held). |
| `children.db` not ready, or the bot reports `database pool is not attached` | `children.db.state`, `children.db.last_error` | The database child could not open its pool: MongoDB is unreachable when `NIKO_STRICT_DB` is set, or `create_pool` is still retrying. Fix the connection; the bot child retries the port over the control socket and recovers by itself. |
| Bot commands fail with `database child did not answer` | `children.db.ready`, then `data/run/logs/db/` (WARNING and above) | Restart only the database child (`{"command": "restart", "child": "db"}`); the bot child re-resolves its port and does not restart. |
| `state: "failed"` | `last_error`, `consecutive_failures`, history `child_exited` entries | Fix the cause, then send control `restart`; `failed` means the restart budget stopped the loop. |
| Child restarts in a loop | history timestamps, `returncode`, `last_stop_reason` | Look for a crash on boot or a readiness failure. Roll back the last bot update if it started then. A child that never reached ready backs off to five minutes instead of every 30s, so a repeated loop is a persistent boot failure, not a transient crash. |
| `last_error` names `Cloudflare throttle (error code: 1015)` or `Discord login blocked` | `WEBSHARE_API_KEY` set? Webshare list fetching? the bot child's `ProxyManager` lines | Discord banned the host's shared egress IP at the edge. The bot retries login through Webshare in-process; if no proxy is usable, fix the Webshare key/plan. Direct egress is probed every 10 minutes and the proxy is dropped once it answers. Do not remove the proxy or restart faster: the block follows the IP, not the process. |
| Child is `draining` and never exits | `last_stop_reason`, elapsed time | The supervisor escalates SIGTERM to SIGKILL after `--shutdown-timeout`; a repeated hang is a shutdown bug. |
| `/ready` detail `sqlite (NIKO_STRICT_DB requires mongodb)` | `MONGODB_URL`, MongoDB reachability, database name | Restore MongoDB. Do not unset `NIKO_STRICT_DB` on a production instance unless you accept serving from local SQLite. |
| Startup error mentions `refusing to fall back to SQLite` | Same as above | Same as above; the child intentionally refuses to start. |
| Update says the bot area was rolled back | `last_error`, history `rollback_applied`, `data/updates/last.json` | The last-good files are already restored and a replacement child is booting. Fix the release before applying again. |
| History `rollback_failed` | The recorded error, `pending.json.failed-*`, backups | Restore the named files from `data/updates/backups/<run>/` by hand, then control `restart`. Nothing outside `--update-root` is ever touched. |
| `pending_update` present while serving | history `update_confirmed` missing | The child is serving without confirming the release. Check why the ready event was not processed; the restore point is retired once a child reports ready. |
| Second update refused | Response says `An update is already being applied.` | Wait for the running update; do not retry in parallel. |
| Two supervisors | Second exits with a port/lock/control-socket error | Expected: it fails closed so only one process owns the public port and the child. |

## Last-good rollback behaviour

- The updater writes `data/updates/pending.json` just before asking for a
  supervised restart, listing each changed file and the run's backup directory.
- If the replacement child never becomes ready, the supervisor restores those
  files, removes files the update added, drops restored bytecode, records
  `rollback_applied`, renames the record to `pending.json.rolledback-<ts>`, and
  starts the last-good child.
- If the child becomes ready, the record is renamed
  `pending.json.confirmed-<ts>` and history records `update_confirmed`.
- A record containing an absolute path or `..` is refused and recorded as
  `rollback_failed`; inspect it before retrying.

Backups are kept. Delete old `data/updates/backups/<run>/` directories manually
once a release is confirmed, or disk use grows with every update.

## Reverting the supervisor

The non-supervised path is still supported:

1. Set the start command back to `python3 src/bot.py`.
2. Leave `NIKO_SUPERVISED` unset — the supervisor sets it for its child; it is
   not an operator setting.
3. Restart the service. No code revert is required; `utils.runtime.handoff` and the
   existing update path still handle bot-core restarts in direct mode.

If the last bot update is suspect, restore `data/updates/backups/<run>/` over
the tree (or use the pending record above) before switching the start command.
