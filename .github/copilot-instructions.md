# Repository guidance

## Build, test, and run

Run these commands from the repository root.

### Python bot

```bash
python -m pip install -r requirements.txt
python3 src/bot.py
python -m pytest
python -m pytest tests/test_transcript_rendering.py -v
python -m pytest tests/test_transcript_rendering.py::test_export_html_renders_custom_emoji_and_stickers -v
```

The final two commands run one test file and one test function, respectively.
For a quick backend syntax check, use:

```bash
python3 -m py_compile src/api_server.py src/webapp/*.py src/website/__init__.py src/bot.py
```

### Web app

```bash
npm run dev
npm run typecheck
npm run build
```

`npm run build` compiles `web/` into `src/website/dist/`, which the bot serves.
Edit the source under `web/`, not generated files under `src/website/dist/`.

## Architecture

- `src/bot.py` starts the Discord bot and the Flask API. Discord features are organized as `discord.py` cogs under `src/cogs/`; `src/events/startup/loader.py` discovers and loads them, while `src/events/on_ready.py` coordinates startup tasks.
- The Flask app is registered from `src/webapp/__init__.py`; shared setup and helpers live in `src/webapp/server.py`, with focused route modules alongside it. `src/api_server.py` runs Flask in a daemon thread in the bot process. Flask handlers that need live bot/cog state schedule work on the Discord event loop; the bot and dashboard should use the same persisted state.
- The React/Vite source is under `web/src/`. It is served on the same origin as the API from the compiled `src/website/dist/` build. The lightweight page router is in `web/src/router.ts`; internal navigation uses `navigate()` rather than adding a routing dependency.
- Bot persistence is accessed through the shared async pool in `src/database/` (`bot.cxn` in cogs). It supports SQLite and MongoDB behind the same interface; SQL uses `$1`, `$2`, … placeholders, and configured JSON columns are serialized/deserialized by the adapter. Keep new data access compatible with that abstraction instead of depending directly on a particular backend.

## Codebase conventions

- A cog is an extension with an async `setup(bot)` entry point. Keep Discord command/event behavior in cogs or the existing event/startup modules, and reuse shared helpers in `src/utils/` where appropriate.
- User-facing Discord responses use Components v2 (`discord.ui.LayoutView` and related layout items); shared pagination behavior is in `src/utils/paginator.py`.
- Dashboard API request and response types belong in `web/src/types.ts`, and fetch functions belong in `web/src/api.ts`. Use same-origin relative URLs. Keep guild authorization and input validation in Flask route handlers; UI checks are not an authorization boundary.
- For dashboard settings, validate and persist only permitted fields on the backend, then keep the API types and controlled UI inputs in sync. Return explicit JSON errors for API failures.
- Discord snowflake IDs must remain exact across the browser boundary; represent IDs as strings in frontend types rather than JavaScript numbers.
- When changing public API behavior, update the relevant route module, `web/src/api.ts`/`web/src/types.ts`, and `docs/api.md` together.
