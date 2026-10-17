# Niko web app

This directory is the source for Niko's React/Vite website. The Python bot serves
the compiled files from `src/website/dist`, so the dashboard and API share one
origin and one Replit workflow.

## Local workflow

From the repository root:

```bash
npm run dev       # Vite development server on port 5000
npm run build     # compile to src/website/dist
npm run typecheck # strict TypeScript check
```

The bot workflow uses the compiled build. Run `npm run build` after changing the
web app, then restart **Run the bot**. For a fast design loop, use `npm run dev`
instead; Vite is configured for Replit's proxied preview.

## Where to make changes

- `web/src/App.tsx` — pages, dashboard sections, and API calls.
- `web/src/api.ts` — the typed client for the bot API.
- `web/src/types.ts` — response shapes shared by the UI.
- `web/src/styles.css` — all visual tokens and responsive styles.
- `web/vite.config.ts` — dev server and production output.

Routes are intentionally kept in one small page router so adding a new public
page does not require a routing dependency. Use `navigate("/path")` for internal
links to keep the app feeling instant.

## Adding a dashboard field

1. Add the field to `web/src/types.ts`.
2. Add or update the endpoint in `src/website.py`.
3. Fetch it in `DashboardSection`.
4. Render it in the relevant view in `web/src/App.tsx`.
5. Run `npm run typecheck && npm run build`.

Never put Discord tokens, provider keys, or client secrets in this directory.