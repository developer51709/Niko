# Honeypot decoy files

This package generates the files Niko's website serves on the paths credential
crawlers probe: `/.env`, its many `.bak`/`.old`/`.example` variants,
`/.aws/credentials`, `dump.sql`, PHP and YAML application configuration, agent
files such as `.mcp.json` and `CLAUDE.md`, and about 170 more.

**Nothing here is a real credential.** Every value is derived from one fixed
seed in [`values.py`](values.py), so the same string appears on every restart
and in every process, and anyone can reproduce it from this public source. A
decoy that happened to be a live key would be worse than serving a 404, so no
module in here reads the environment or imports the application's
configuration.

## Why it was added

Niko's deployment was being crawled continuously for secrets. Each scan looked
like this:

```
GET /.env                 404
GET /.env.local           404
GET /.env.production      404
GET /.aws/credentials     404
GET /.git/config          404
...
```

Two problems came out of that:

1. **The logs filled up.** Every probe produced an access-log line, and a
   single scan runs to a hundred-plus requests. The owner's live feed and the
   console stopped showing the bot's own output.
2. **A friendly note did not work.** The paths used to answer with a written
   notice explaining that there was nothing to find and where to report a
   vulnerability. The scans continued exactly as before.

The first version rejected IP bans because there are no real credentials to
protect here. The owner page now offers them as an operational tool instead:
repeated probes are recorded, and an address that keeps coming back can be
refused across the site. The middle ground is still to make the crawl
unrewarding and quiet:

- a scanner that finds a plausible `.env` will keep reading, keep downloading
  `dump.sql`, and keep trying the fake keys — all of which costs it time and
  yields nothing;
- every decoy answers `200`, and `utils/logging._QuietSuccessfulRequests`
  already drops successful access lines, so the per-path log flood disappears;
- each probe is aggregated in the database under its source address (count,
  first/last hit, last path and host, user agent), so the history survives a
  restart without keeping a request list in the web process;
- one compact line per probing address per minute records that it happened:

  ```
  Honeypot  Decoy files: 10.12.0.80 is probing the deployment (/.env) — serving fake credentials
  ```

The honest channel is unchanged: `/.well-known/security.txt` still points at
the GitHub advisory page and the support server, and this README, in the public
repository, says exactly what the files are. Anyone with the sense to look at
the source will see the trap in a minute; the crawlers that ignore it get the
time-wasting version.

## How it works

| File | Purpose |
| --- | --- |
| [`values.py`](values.py) | The single seed and every generated value: tokens, passwords, keys, service accounts. |
| [`env.py`](env.py) | The 20 `.env` variants and the Vim swap file. |
| [`configs.py`](configs.py) | Frontend bundles, JSON, PHP, YAML (Compose, Spring, Rails, k8s, litellm…) and CI files. |
| [`stores.py`](stores.py) | Credential stores, private keys, shell history, the SQL dump and the backup ZIP. |
| `../security.py` | Persistent hits, IP bans, autoban settings, and API rate windows. |
| `../routes/honeypot_routes.py` | The owner page's API: hits, bans, and autoban controls. |
| [`easter_eggs.py`](easter_eggs.py) | The rickroll frames and the host-to-animation mapping. |
| [`nyancat.py`](nyancat.py) | Port of klange/nyancat's terminal renderer: palette, crop and counter. |
| [`nyancat_frames.py`](nyancat_frames.py) | The vendored 12 × 64 × 64 Nyan Cat frames. |
| [`__init__.py`](__init__.py) | The path registry, `body_for()`, and the command-line entry point. |
| [`__main__.py`](__main__.py) | `python -m webapp.honeypot`. |

The files are **consistent on purpose**. The PostgreSQL password in `.env` is
the same one in `docker-compose.yml`, `.pgpass`, `credentials.json` and
`dump.sql`; the AWS key in `.env` opens `.aws/credentials`; the Discord token
appears in `.env`, `config.js` and `CLAUDE.md`. The site's own URL and the
shared staff addresses (`owner@`, `admin@`, `support@`, `support-lead@` on
`niko.sryze.cc`) are real too: they are public already, the donation site is
simply the public site, and a made-up address that bounces would only reveal
that the file is fake. A mismatch between two leaked
files is the fastest way to spot a decoy, so there are none. The `.env.backup`
family carries a *different*, older database password to suggest a rotation,
and `dump.sql` has real-looking rows (users, sessions, payments, API keys,
staff accounts) rather than a schema with no data.

Routes are registered in
[`../routes/security_decoy_routes.py`](../routes/security_decoy_routes.py):

- only paths the deployment genuinely does not serve are registered, so a real
  route or a file in the built site always wins;
- responses carry `Cache-Control: no-store` and `X-Robots-Tag: noindex,
  nofollow`, so the decoys do not end up in search results;
- the hit history lives in MongoDB (or the local JSON fallback), aggregated per
  address, not in the web process's memory;
- the log summary is throttled per `X-Forwarded-For` address, capped at 512
  tracked addresses.

Every decoy body is rendered once and cached, including the ~44 KB SQL dump and
the ZIP, so a scanner hammering these paths costs the deployment almost nothing.

## Easter eggs

Several decoys point at hosts under the public domain that the site does not
run: `db.`, `read.`, `cache.`, `nyan.`, `vault.` and `queue.` on
`niko.sryze.cc`. The wildcard DNS for the site sends them here, and instead of
the subdomain 404 a request to one is answered with a short ANSI animation in
the caller's terminal — a nyan cat from the data stores, a rickroll from the
secret store and the queue — followed by a card saying the host is a decoy. A
crawler that tries the fake PostgreSQL password gets a few seconds of
animation instead of a login prompt, and anything it writes down is noise.

`nyan.niko.sryze.cc` (and `nyancat.`) is the exception: it exists only as a
joke. It opens with the intro screen and an animated five-second countdown
(the port's version of upstream's telnet banner, including `press Ctrl+C to
stop`), then plays the animation until the visitor stops it. There is no
closing card and no decoy file behind it; every path on that host plays the
animation, even `/.env`. Ctrl+C closes the request, which ends the server-side
generator and frees its stream slot.

The nyan animation is the real one. [`nyancat_frames.py`](nyancat_frames.py)
vendors the twelve 64×64 frames from
[klange/nyancat](https://github.com/klange/nyancat) (the source of the Debian
`nyancat` package), and [`nyancat.py`](nyancat.py) ports its xterm-256 render
loop: the 40×23 crop of an 80×24 terminal, two spaces per pixel, 90 ms per
frame, and the `You have nyaned for N seconds!` counter. Upstream is a C
program and telnet server; this deployment is pure Python and ships updates as
Python files, so compiling and supervising a binary is not worth it for an
easter egg. The port runs in the same process as the dashboard and API and
draws the same picture. The upstream NCSA/UIUC licence is kept in
[`LICENSE-nyancat.txt`](LICENSE-nyancat.txt).

The host check runs before subdomain routing in
[`../routes/security_decoy_routes.py`](../routes/security_decoy_routes.py), so
the fake hosts win even though the site treats them as unused subdomains. At
most eight animations stream at once; anything past that gets only the closing
card, so a scanner cannot pin a thread per request. Decoy animations finish
after about five seconds with that card; the fun host runs until the client
disconnects. The cursor is hidden while a frame runs and restored at the end.
To watch one locally:

```bash
curl -H 'X-Forwarded-Host: vault.niko.sryze.cc' http://localhost:5173/
curl -H 'X-Forwarded-Host: nyan.niko.sryze.cc' http://localhost:5173/
curl -H 'X-Forwarded-Host: cache.niko.sryze.cc' http://localhost:5173/
```

## Inspecting it

```bash
PYTHONPATH=src python -m webapp.honeypot --list     # every decoy path
PYTHONPATH=src python -m webapp.honeypot .env       # print one, exactly as served
PYTHONPATH=src python -m webapp.honeypot dump.sql | less
```

To add a path, put a builder in the relevant module and register it in
`_files()` in [`__init__.py`](__init__.py). Run the tests afterwards:

```bash
pytest tests/test_security_decoy_routes.py
```

## Owner page and bans

The staff workspace's **Honeypot** tab lists the aggregated hits with the source
IP, last path and host, user agent, and first/last timestamps. The owner can ban
an address from there, with an optional reason, and unban it later. A ban is
checked before subdomain routing, so it applies to the website, every API and
auth route, and every subdomain, not just the decoy paths.

The same tab arms the autoban guard. The owner sets how many hits inside a
counting window trigger a ban and how long that ban lasts. Manual bans and
autobans both refuse loopback (`127.0.0.1`, `::1`), private, link-local, and
reserved addresses: those are internal, so banning one would either lock out
the deployment itself or have no effect on the internet. Bans are stored with
the hits; the request guard reads a small active-ban cache and does not query
the database on every page view.

## What it does not do

- It does not cover paths outside the registry. A scanner inventing a new
  filename still gets the SPA's 404 (and one access-log line).
- It does not record what a crawler does with the fake values; it only counts
  the probes per address.
- It never serves, reads or derives from a real secret.
