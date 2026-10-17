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

- Flask app entrypoint: `src/webapp/__init__.py`; shared app setup: `src/webapp/server.py`; focused Flask routes live in `src/webapp/*_routes.py`.
- Personal (account-level) routes read the signed-in user only: `/api/me/...` with `@require_auth`. Anything that is the same in every server — the economy, achievements, leaderboard privacy — belongs here, never behind a server.
- Private guild routes must check the user’s Discord permissions on the server.
- Return JSON errors for API failures; do not silently write malformed config.
- Avoid long-running work in request handlers.
- Keep static fallback routing after API and authentication routes.
- The API runs in a daemon thread so a bot shutdown still terminates the web
  server.

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
python3 -m py_compile src/api_server.py src/webapp/*.py src/website/__init__.py src/bot.py
```Then start `Run the bot`, check `/api/health`, and open the preview. If the
preview is blank, check workflow logs before changing frontend code.
