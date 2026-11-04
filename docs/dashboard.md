# Dashboard maintenance guide

The dashboard is a React + Vite frontend backed by the Flask API that runs
inside the Discord bot process. It is deliberately small: the UI has a typed
API client, a single page router, and a shared stylesheet instead of a large
component framework. That makes manual edits predictable for future
contributors.

## Architecture

```text
Discord bot process
  ├─ Discord gateway / cogs
  └─ Flask API + static file server :5000
       └─ src/website/dist  ← npm run build

web/src  ← edit this source, never generated dist files
```

The `Run the bot` workflow is the source of truth. The bot starts the web server
through `src/api_server.py`. Do not create a second website workflow.

## Frontend conventions

- Keep API response types in `web/src/types.ts`.
- Keep fetch functions in `web/src/api.ts`; use `credentials: "same-origin"`.
- Use relative URLs so the same build works in Replit preview and deployment.
- Keep user-visible loading, empty, and error states explicit.
- Use the tokens at the top of `web/src/styles.css` instead of scattering new
  colors through components.
- Build after changes. The Python server serves `src/website/dist`, not
  TypeScript source files.

## Backend conventions

- Flask app entrypoint: `src/webapp/__init__.py`; shared app setup and helpers live in `src/webapp/server.py` and its sibling modules (`auth.py`, `database.py`, `discord_api.py`, `staff.py`, `guilds.py`, `social.py`); focused Flask routes live in `src/webapp/routes/*_routes.py`.
- Personal (account-level) routes read the signed-in user only: `/api/me/...` with `@require_auth`. Anything that is the same in every server — the economy, achievements, leaderboard privacy — belongs here, never behind a server.
- Private guild routes must check the user’s Discord permissions on the server.
- Return JSON errors for API failures; do not silently write malformed config.
- Avoid long-running work in request handlers.
- Keep static fallback routing after API and authentication routes.
- The API runs in a daemon thread so a bot shutdown still terminates the web
  server.

## Dashboard on a subdomain

`SUBDOMAIN_ROUTING=true` moves the dashboard onto `dash.<your domain>`:
`https://dash.example.com/staff` is `https://example.com/dashboard/staff`, and
`https://dash.example.com/` is the dashboard home. It is off by default, so
nothing changes until it is switched on, and the apex keeps serving the long
form at the same time — the same build answers both.

The mapping lives in `SUBDOMAIN_SECTIONS` (`src/webapp/config.py`) and is keyed
by the host's first label, so `dash.example.com` and `dash.staging.example.com`
both work: point a wildcard DNS record and a matching certificate at the service
and there is nothing per-domain to configure.

How the two halves meet:

- `config.subdomain_prefix(host)` turns the host into the apex path it stands
  in for. `render_site_shell` uses it to describe the page in its apex form
  (copy, canonical URL) and to inject `window.__NIKO_SHELL__` into the shell —
  the one thing the built bundle cannot work out on its own.
- The client (`web/src/router.ts`) adds the prefix to every path it reads
  (`currentPath`) and strips it from every path it writes (`navigate`,
  `publicPath`, `DiscordSignIn`'s `next`), so links and guards stay written in
  the apex form everywhere else in the code.
- A request that already carries the long form on a section host
  (`/dashboard/staff`) is 301'd to the short one, which is what keeps old links
  and pasted URLs working.
- A section host serves only its own subtree, so the few links that leave the
  dashboard (`siteHref`) point at the site's own origin rather than pushing a
  path this host cannot render.
- The other direction is `config.section_origins`: the apex shell carries each
  section's origin (`{"/dashboard": "https://dash.example.com"}`) in
  `window.__NIKO_SHELL__.sections`, so a link *into* the dashboard — the public
  header's Dashboard button (`router.dashboardHref`) — goes to the short form
  on the section host instead of the long form on the apex. It is empty while
  the switch is off or `PUBLIC_URL` is unset, and the link stays relative.
- Hosts under the site's own domain that are *not* a section
  (`config.unknown_subdomain`) are not the site: they answer with HTTP 404 and
  the subdomain variant of the 404 page, which links out to the real site with
  absolute URLs. Their static files and `/api/`, `/auth/` endpoints still work,
  because the page itself has to load. Which hosts count as "the site's" comes
  from `PUBLIC_URL`; without it nothing is claimed and an unused subdomain
  serves the normal site.
- Signing in works from either host. `/auth/login` names the site's one
  registered callback — `DISCORD_REDIRECT_URI` if it is set, otherwise
  `PUBLIC_URL` + `/auth/callback` while routing is on (`runtime.redirect_uri`)
  — because Discord refuses a callback it does not know, and `dash.` is not one
  of them. The shared session cookie carries the OAuth state across the hop, and
  `/auth/callback` then sends the visitor back to the section host they started
  from, with the path in that host's short form (`config.public_path`). The
  `next=` a sign-in was given is stored in its apex form first
  (`config.apex_path`), since a section host writes it short: `/staff` on
  `dash.` has to come back as `/dashboard/staff`.
- A sign-in can only finish on the address that started it, because the OAuth
  state is a cookie on that host. When the callback names a different *site*
  (a preview host signing in against the real site's callback, say),
  `/auth/login` hands the visitor to the callback's own address — but only when
  that address is the site itself, which `PUBLIC_URL` names. Anything else is a
  misconfiguration and is not followed.
- A failed return explains itself: the login line and the failure both name the
  address the sign-in started on and the one it came back to
  (`/?error=…&from=…&to=…`, shown under the sign-in notice), and the server logs
  the pair with the cookie's domain and `Secure` flag. "The link expired" alone
  never has to be the whole story again.
- Sessions are shared when `PUBLIC_URL` names the apex (it usually does):
  `config.session_cookie_domain` then puts the session cookie on `.<domain>`, so
  a sign-in on the apex is valid on the subdomain and the other way round.
  Without `PUBLIC_URL` each host keeps its own host-only session — the
  subdomain still signs in, it just does not share the apex's. If the OAuth app
  checks redirect URIs exactly, add `https://dash.<domain>/auth/callback` to it
  as well.

## Missing pages

`pageFromPath` returns `not-found` for anything it does not recognise (`/` stays
the home page), and `NotFoundPage` has two variants:

- **page** — a host the site serves, with a path that is not a page. It renders
  inside the normal header and footer, because the navigation around it works.
- **subdomain** — a host that serves no site at all. Every relative link there
  would land back on the same 404, so it stands alone and links out to the real
  site with absolute URLs (`siteOrigin`, injected by the server).

The server picks the variant, not the client: it knows which hosts belong to the
site, and answers those with a 404 status. A path on a *used* host stays a 200 —
the server cannot see the client's route table (the status endpoint has no Flask
route, for one), so the page variant is chosen in the browser.

## Reloading a tab after a build

The shell is read from `src/website/dist` on every request and names the build
it was served from (`src/webapp/site_build.py`, injected as
`window.__NIKO_SHELL__.build`). A tab that is already open keeps the bundle it
loaded, so `UpdatePrompt` compares that name with `/api/site/build` every twenty
seconds while the tab is visible — the notice appears on its own, without
waiting for the visitor to switch back to it — and offers a reload when the
site has moved on. A hidden tab drops to a slow poll (its timers are throttled
anyway) and checks immediately on focus, on `pageshow` and when the connection
comes back.

It can only fire for a tab that is genuinely behind: the name is Vite's hashed
entry script, so it changes with any bundle change and — importantly — does not
change for a Python-only update or a rebuild that touched nothing the bundle
imports. Dismissing it silences that one build (kept in `sessionStorage`); the
next build that lands offers the reload again. There is nothing to configure.

## Common change recipes

### Add a public page

Add a `Page` value and a branch in `App`, add the page component, then add
navigation links and a footer link. Use `navigate()` for internal navigation.

### Add a dashboard setting

Decide the scope first. Server settings live in the guild area
(`/dashboard/<guild>/<section>`, `/api/guild/<id>/...`, permission gated);
account-level views live in the personal area opened from **My overview**
(`/dashboard` and `/dashboard/me/<tab>`, `/api/me/...`, no server needed).

Then add the backend validation and persistence first, type the
response/request in `web/src/types.ts`, add the fetch function to
`web/src/api.ts`, fetch it in the matching dashboard section component, and
render a controlled input. Save only the allowed fields and show confirmation
or failure feedback. If a view is already global (the economy and achievements
are), keep it personal: a server-scoped endpoint would imply a per-server value
that does not exist.

### Verify a release locally

```bash
npm run typecheck
npm run build
python3 -m py_compile src/api_server.py src/webapp/*.py src/webapp/routes/*.py src/website/__init__.py src/bot.py
```Then start `Run the bot`, check `/api/health`, and open the preview. If the
preview is blank, check workflow logs before changing frontend code.
