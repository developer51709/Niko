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
| `BETA_UPDATE_TOKEN` | both instances | Shared secret. Beta only serves its source files to a caller with the same value. Without it, `/api/updates/*` answers 404. |
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
by area, and applies what is selected:

| Area | What it covers | How it is applied |
| --- | --- | --- |
| Website build | `src/website/dist/**` | Files replaced in place. Flask serves that folder from disk, so the next request is the new site. Nothing restarts. |
| Cog extensions | `src/cogs/**` | The changed `cogs.<package>` modules are dropped from `sys.modules` (clearing the cached import) and only the affected extensions are reloaded. |
| Utilities | `src/utils/**` | Changed `utils.*` modules are purged, every loaded extension is reloaded on top of them, and the dashboard app is rebuilt. |
| API & dashboard | `src/webapp/**` | `webapp.*` is re-imported and the new Flask app is swapped into the running server (`server.app`). The listening socket, its thread and in-flight connections stay up. |
| Bot core | `src/bot.py`, `src/api_server.py`, `src/events/**`, `src/database/**` | A successor process is started on the inherited listening socket; see below. |

The API rebuild is transactional. The modules the running app was built from
are snapshotted before `webapp.*` is dropped; if the new copy fails to import,
they are put back and the area is rolled back, so the page reports the error
while the site keeps answering on the old code. An API update never leaves a
process whose modules were purged and whose route imports now read a file that
does not load. The updater reloads its own module at the end of such a run for
the same reason: `src/webapp/updates.py` is part of the area it replaces, and it
is the one module that cannot be re-imported while it is executing.

Every replaced file is hashed against beta's manifest before it is written, and
copied to `data/updates/backups/<run>/` first. A failed download or a failed
reload restores that area from the backup and reports the error on the page; the
last run is kept in `data/updates/last.json`.

### The bot-core handoff

Python cannot replace its own code, so `src/bot.py` needs a new interpreter. The
handoff keeps both the site and the gateway up while that happens:

1. The running process duplicates its listening socket and starts
   `src/bot.py` with that socket inherited as an open file descriptor — no
   rebinding and no gap — plus a one-run token and `NIKO_HANDOFF_ROLE=candidate`.
2. The successor imports the new code, serves the API on the *same* socket — so
   the site keeps answering during the overlap — loads its cogs and connects the
   gateway.
3. When its gateway is ready, the successor posts to
   `/api/handoff/ready` on the predecessor. The predecessor stops accepting,
   closes its gateway and exits; the successor keeps the socket, the session and
   the cogs.
4. The successor starts answering commands only after that acknowledgement, so
   no command is handled twice. Expect one to two seconds where commands are not
   answered; HTTP is never down.

If the successor never becomes ready, the predecessor stays exactly as it was
and the page reports the failure. Files that were already written stay on disk,
so a retry or a normal deploy picks them up.

The handoff is local to one machine: the successor must be able to inherit a
file descriptor, so this is for a single-process deployment (the normal
`python3 src/bot.py` layout), not for a container that is recreated per release.

## Limits worth knowing

- A **new page** still needs a deploy: the feed can add strings and languages,
  not routes or components.
- Python modules the bot core imported at startup (`utils.gateway`, `utils.analytics`,
  …) keep their loaded copy until a bot-core handoff, even if a utilities update
  rewrote the file. The page reports what it reloaded.
- A website update replaces files, it does not rebuild them. Beta must have run
  its own build (the `dist/` folder is in the manifest) before production pulls
  it.
- `src/config/**` never travels: it holds the guild ids, links and status copy a
  deployment was configured with. A bot-core update deliberately leaves it
  alone, so beta cannot repoint production's links.
- Updates are pulled on demand by the owner; nothing polls beta and applies
  changes by itself.
- The handoff replaces the running process, so the supervisor that started it
  must not restart it on a clean exit. `data/updates/handoff.json` records the
  successor's pid and state if you need to trace one.
