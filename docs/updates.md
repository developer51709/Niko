# Updates without a deploy

Production normally moves forward by deploying a new build from git, which costs
the whole process: the gateway reconnects, every cog reloads, and the dashboard
is unreachable while it happens. Most changes do not need that. This page
describes the owner-triggered update system that applies only the part that
changed, and the two owner pages that drive it.

Both pages live in the staff workspace — **Locales** and **Updates** — and are
visible to the bot owner only.

## Configuration

| Variable | Where | What it does |
| --- | --- | --- |
| `BETA_INSTANCE_URL` | production | Origin of the beta instance, e.g. `https://beta.example.com`. Powers the live translation feed *and* the update feed. |
| `BETA_UPDATE_TOKEN` | both instances | Shared secret. Beta only serves its source files to a caller with the same value, and production's supervisor accepts the same value on its force-update route. Without it, both answer 404. |
| `PRODUCTION_INSTANCE_URL` | beta | Origin of the production instance, for the recovery push. Without it, beta's `/api/updates/push` is unavailable. |
| `LOCALE_FEED_TTL` | production | Seconds before the translation manifest is re-read (default 15). |

Generate a token once and set it on both sides:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Nothing else is needed: no SSH, no deploy key, no git checkout on the production
machine.

## The locale page

**Staff settings → Locales** shows the merged catalogue set the live site is
using: every language, its coverage, whether the figures come from beta or from
this build, and how old the reading is. Coverage counts the site's page
catalogues and the bot's cog catalogues together, so a language's percentage
describes the whole product rather than one half of it.

The catalogue card has two collapsible sections, both closed until opened —
**Bot locales**, one card per cog package, and **Website locales**, one card per
page. Each card carries a small overview (key count, languages finished, overall
bar) and folds open into that catalogue's per-language coverage, because a
translation pass usually touches one family and then the other. **Sync now**
forces a re-read instead of waiting for the next poll.

A language appears as soon as one page has a file for it, so a translator can
add `it.json` on beta and see it in the picker on production without a deploy.
The same numbers are on the public `/status` page, which labels its section
**Live from beta** when the feed is answering.

Bot wording is part of the same feed. Beta publishes each cog's catalogues at
`/api/locales/bot/<package>/<lang>.json`, production fetches the ones it has not
seen yet, and `utils.locales` serves them as a live overlay — so a reply rewritten
on beta appears in Discord without reloading a cog or restarting the bot. The
poller runs every `LOCALE_FEED_TTL` seconds, and **Sync now** applies the same
pass synchronously. The *Running bot* fact on the page says how many catalogue
files the bot is currently serving from beta.

## The update page

**Staff settings → Updates** compares beta's files with this deployment's, area
by area, and applies what is selected, in the order below:

| Area | What it covers | How it is applied |
| --- | --- | --- |
| Shared modules | new `src/config/**` files and `src/config/links.py` | Written before anything is reloaded, because a module an area imports has to exist first. Existing config files keep this deployment's own ids and copy, and a file beta dropped is never deleted — except `links.py`, which always carries the production URLs and is replaced in full. A pending module is added to any run, whether or not the owner ticked it. |
| Website build | `src/website/dist/**` | Files replaced in place. Flask serves that folder from disk, so the next request is the new site. Nothing restarts. |
| Cog extensions | `src/cogs/**` | The changed `cogs.<package>` modules are dropped from `sys.modules` (clearing the cached import) and only the affected extensions are reloaded. |
| Utilities | `src/utils/**` | Changed `utils.*` modules are purged, every loaded extension is reloaded on top of them, and the dashboard app is rebuilt. |
| Database schema | `src/events/startup/database.py` | The module is re-imported and its `init_database` run again on the live pool: `CREATE TABLE IF NOT EXISTS`, missing columns and the idempotent migrations. The process keeps running. |
| API & dashboard | `src/webapp/**` | `webapp.*` is re-imported and the new Flask app is swapped into the running server (`server.app`). The listening socket, its thread and in-flight connections stay up. The swap is checked before it is reported: the new app must be the one on the server and must answer `/api/health`. |
| Gateway events | `src/events/on_*.py` | The modules are purged from `sys.modules`, re-imported, and the handler names `bot.py`'s callbacks look up are rebound onto the new functions. The next message runs the new code; nothing restarts. |
| Startup writers | `src/events/startup/writers.py` | The writers and the banner that reads their version are re-imported, `events.startup`'s exports are refreshed, and the ready handler is rebound. The writers then run once so `bot_stats.json` and `commands.json` are current. No restart and no cog reload. |
| Bot core | `src/bot.py`, `src/api_server.py`, the remaining `src/events/startup/**`, `src/database/**`, `src/db_child.py` | The process replaces its own image in place, keeping its PID and listening socket; see below. In the split layout the supervisor restarts the database child beside it, so the new `src/database/` client and the `src/db_child.py` that serves it change together. |

The API rebuild is transactional. The modules the running app was built from
are snapshotted before `webapp.*` is dropped; if the new copy fails to import,
they are put back and the area is rolled back, so the page reports the error
while the site keeps answering on the old code. An API update never leaves a
process whose modules were purged and whose route imports now read a file that
does not load. The updater reloads its own module at the end of such a run for
the same reason: `src/webapp/updates.py` is part of the area it replaces, and it
is the one module that cannot be re-imported while it is executing.

The gateway event modules get the same treatment without a reload of anything else.
`bot.py` registers its Discord callbacks as closures over module-level names
(`handle_ready`, `handle_message`) and reads that name from its own globals on
every dispatch, so an event update purges `events.on_message` / `events.on_ready`,
re-imports them from the new files, and rebinds every global that pointed at the
old functions — including any other callable a host module imported from them.
The gateway connection, the cogs and the dashboard are untouched; the very next
message is handled by the new code. Module-level state in those modules (per-channel
reply locks, the AI concurrency semaphore) starts again at its declared value,
which is why they are limits and not counters. An event module that fails to
import is put back from the old module object, so a bad pull cannot leave the
gateway without its handler.

The schema module and the startup writers are the exceptions in the startup
chain. `events/startup/database.py` is re-imported and its `init_database` called
again against the running pool, so a new table, a new column or a backfill is
live immediately: the function is written for exactly that — tables are `IF NOT
EXISTS`, migrations add only what is missing, and the pool is opened only when
there is none. The music and error-report databases are skipped on the second
run because their own `init` returns early once ready. `events/startup/writers.py`
is imported by `events.on_ready` and called on every READY, so it can be
re-imported and the ready handler rebound without a restart; the updater runs
the writers once so the exported stats and command data are current immediately
(keeping the process uptime marker intact, since no restart happened). The rest
of `src/events/startup/**` still ships with the bot core: it runs once at boot,
so reloading it would change nothing until a restart.

An area beta's build does not publish (an older deployment, or one without the
feature) is reported as *not published*, never as “every file here was deleted”.
That distinction matters: an update pulled from a beta build without the gateway
events area used to offer to delete this deployment's `src/events/on_*.py`, and
the reload then failed with `ModuleNotFoundError: No module named
'events.on_message'`.

Two smaller things are what make the new code the code that actually answers:

- **The compiled copy of a replaced file is deleted** (`__pycache__/*.pyc`).
  `importlib.invalidate_caches()` refreshes the finders, not a bytecode file
  whose recorded source stamp still matches; a module that arrives with the same
  size and timestamp would otherwise import from the previous build until the
  process restarted.
- **A swap that does not take effect is a failure, not a success.** After
  `replace_app`, the updater checks that the server holds the new app and that it
  answers `/api/health`; if either is false, the old app and the old modules go
  back and the area is rolled back — so "applied" always means "live now".

Every replaced file is hashed against beta's manifest before it is written, and
copied to `data/updates/backups/<run>/` first. A failed download or a failed
reload restores that area from the backup and reports the error on the page; the
last run is kept in `data/updates/last.json`.

### The bot-core restart

Python cannot replace its own code, so `src/bot.py` needs a new interpreter.
Handing the process over to a *child* is not good enough on a hosted service: the
parent has to exit for the child to take the port, and a supervisor (Render,
Railway, a systemd unit) treats that exit as a crash — it recreates the instance,
throws away the files the update just wrote and leaves the dashboard down for the
whole boot. So the process replaces its own image instead:

1. The running process duplicates its listening socket, marks the descriptor
   inheritable and passes it as `NIKO_RESTART_FD`. **The port never closes**: the
   kernel keeps the socket bound and listening across the exec, so connections
   queue instead of being refused.
2. `os.execve` keeps the PID. Nothing the host watches exits, so no restart of
   the service is triggered and the written files stay on disk.
3. The new image adopts the socket as soon as its imports finish, before cogs
   load and before the gateway connects, so the site is answering again in about
   a second. If the descriptor cannot be adopted it binds the port normally
   rather than coming up without a site.

The exec closes the old image's gateway connection with it, so the two images
never hold a Discord session at once, and the new one logs in again. Commands are
unanswered for the few seconds the boot takes; HTTP is not interrupted. The
gateway is not closed explicitly beforehand: `bot.close()` returns the running
`asyncio.run`, and interpreter shutdown does not wait for the daemon thread that
is about to exec — the process could exit before the image is replaced.

Because the bot area is the only one with no rollback (the running code is gone),
the update *proves* the new files first: every Python file has to compile, and
`src/bot.py` is run in a throwaway interpreter that stops right after its imports.
If either check fails the area is rolled back and reported as failed, and nothing
restarts — the old process keeps serving with its own code. The run is also
refused when this process owns no listening socket, since there would be nothing
for the site to come back on.

The restart code itself lives in `src/utils/runtime/handoff.py`, which ships with the
Utilities area, so it is re-imported from disk before the bot core is applied:
a process that has been up since before the in-place restart still holds the
previous successor handoff in memory, and restarting with that would hand the
port to a child — the exact failure the in-place restart exists to avoid. If the
file on disk is that copy too, the area is refused with a message saying to
apply Utilities first (ticking both areas in one run does it in the right order)
rather than failing with an `AttributeError` from the stale module.

## Forcing an update from beta (recovery)

The update page lives on production, so it is unreachable when production's
dashboard is down. The supervisor owns the public port independently of the
dashboard child and accepts a token-authenticated push on
`POST /supervisor/update`. Beta also wraps it in `POST /api/updates/push`, so the
owner can trigger it from the instance that is still up:

```bash
# On beta: ask production to pull and apply the selected areas.
curl -fsS -X POST https://beta.example.com/api/updates/push \
  -H "X-Update-Token: $BETA_UPDATE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"areas": ["website", "webapp"]}'

# Directly against production's supervisor when beta's dashboard is also down.
curl -fsS -X POST https://niko.example.com/supervisor/update \
  -H "X-Update-Token: $BETA_UPDATE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"areas": ["website", "webapp"]}'
```

Omit `areas` to let production apply every area that differs, which is the same
choice the owner page offers. The production supervisor reads
`BETA_UPDATE_TOKEN` from its process environment or from `src/.env` (the file the
bot child already uses).

What the recovery path guarantees — and what it does not:

- It works while the **dashboard** child is down or crash-looping. The supervisor
  answers on its own socket and forwards the request to the bot child, which runs
  the existing updater.
- It needs the **bot** child healthy enough to report ready. If the gateway child
  is down too, production answers `503`; the supervisor's crash/backoff and
  last-good rollback are the path back from there.
- The files still come from `BETA_INSTANCE_URL` over TLS and are hash-checked
  against beta's manifest. The pushed request cannot name a different host or
  supply code, so the token grants "apply now", not arbitrary execution.
- A missing or wrong token answers `404`, exactly like an instance that does not
  have the feature, so the route is not discoverable.

## Limits worth knowing

- A **new page** still needs a deploy: the feed can add strings and languages,
  not routes or components.
- Python modules the bot core imported at startup (`utils.runtime.gateway`, `utils.analytics`,
  …) keep their loaded copy until a bot-core restart, even if a utilities update
  rewrote the file. The page reports what it reloaded. Gateway event modules are
  the exception: their handlers are rebound, so a change to `src/events/on_message.py`
  is live on the next message; the schema module's `init_database` is re-run so
  a new table or column exists immediately; and the startup writers are
  re-imported and run so their exported data is current. Any other startup module
  still waits for a restart.
- A website update replaces files, it does not rebuild them. Beta must have run
  its own build (the `dist/` folder is in the manifest) before production pulls
  it.
- `src/config/**` mostly never *replaces* anything: it holds the guild ids and
  status copy a deployment was configured with. A **new** config module does
  travel, because code that imports it would otherwise fail its reload with
  `ModuleNotFoundError`. `src/config/links.py` is the exception: it always
  contains the production URLs (beta reads `PUBLIC_URL` from its environment),
  so its changes are pulled in full rather than requiring a manual GitHub pull
  and a deployment restart. This is the Shared modules area, and it applies
  first in every run.
- Updates are pulled on demand by the owner; nothing polls beta and applies
  changes by itself. The authenticated beta push is the one exception, and it
  only tells production to run the same pull now.
- A visitor who already has the site open is not sent a new bundle. Their tab
  keeps the one it loaded and is offered a reload by the update notice — the
  build name in the shell against `/api/site/build`, see "Reloading a tab after
  a build" in `docs/dashboard.md`. Only a change to the bundle triggers it; a
  server-only update is picked up by the next request without a reload.
- The bot-core restart replaces the process image, so it needs a Unix host.
  Under the supervisor the bot child is restarted in place; when Niko is run
  directly as `python3 src/bot.py`, the in-place handoff does the same job.
  `data/updates/handoff.json` records the pid, port and state
  (`restarting` / `restarted` / `failed`) if you need to trace one. Nothing is
  written to that file for any other area.
- A restart runs the new code from disk, but it cannot make it survive the
  container being recreated: on a host with an ephemeral filesystem (Render) the
  files pulled from beta are still lost the next time the service deploys or is
  restarted by the platform. Deploy for durability; the in-place restart is what
  lets an urgent bot fix land without waiting for one.
