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

Add the backend validation and persistence first, type the response/request,
fetch it in `DashboardSection`, and render a controlled input. Save only the
allowed fields and show confirmation or failure feedback.

### Verify a release locally

```bash
npm run typecheck
npm run build
python3 -m py_compile src/api_server.py src/website.py src/bot.py
```

Then restart `Run the bot`, check `/api/health`, and open the preview. If the
preview is blank, check workflow logs before changing frontend code.