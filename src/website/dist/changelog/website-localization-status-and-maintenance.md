# The Site Learns Languages

- Date: 2026-11-03
- Version: 2.27.0
- Tags: localization, website, dashboard, status, maintenance, added

Every public page and every dashboard screen now draws its copy from a per-page locale catalogue, so translating the site is a translation job instead of a search through components. This is the first and largest part of that pass — 28 catalogues and 2,955 strings are in place, with the German, Spanish and French files following page by page. Alongside it: a public `/status` page, and an owner-only maintenance mode that pauses cogs and single commands from the dashboard.

## Highlights

### One Catalogue per Page
`web/src/locales/<page>/en.json` holds every heading, button, empty state, error and screen-reader string a page renders, and components ask for it with `useStrings("<page>")`. A page with no translation falls back to English, and a missing key falls back to its English string, so a half-translated page never shows raw keys. The chrome the header and footers share lives once, in `shared/`.

### A Language Picker, Not Just Files
The owner devtools panel has a **Site language** picker on its Page tab. It switches the site for that browser, remembers the choice in `localStorage`, and leaves Discord replies on each guild's own locale. The tab title is re-stamped from the page's catalogue after every client-side navigation, so a translated page does not keep an English title in the window.

### A Public Status Page
`/status` reads a new `/api/status` payload: online state and latency, uptime, servers and members, the command count, every cog with its state and its own command count, per-shard guilds and latency, host metrics, and how much of the bot's wording each language has translated. Shards that have not finished connecting read **Starting** instead of a five-second latency, and a paused cog shows as maintenance rather than as an error.

### Maintenance Mode, Owner Only
The owner can pause a whole cog or a single command from the dashboard's maintenance tab, with an optional reason shown to anyone who tries to use it. The gate runs before a command's own checks: a paused cog answers with the maintenance notice on slash, prefix, and user/message context-menu commands alike, leaves its cooldowns and usage counters untouched, and does not push members toward the abuse limit. State is written to the database, so a restart keeps every switch where you left it.

## Changes

### added
- `web/src/locales/` — one catalogue per page plus the shared chrome, 28 catalogues and 2,955 English strings
- `web/src/i18n` — `useStrings(page)`, `t(key, values)` interpolation, and English fallback per language and per key
- A public `/status` page with a verdict card, live metrics, cog and shard cards, host stats and locale coverage
- `/api/status`: one payload for the bot's state, cogs, shards, host, and the string coverage of both sides of the project
- Owner maintenance mode — `utils/maintenance`, a dashboard tab, `/api/staff/maintenance`, and the `maintenance_targets` table
- Per-cog startup outcomes — loaded, maintenance, disabled, failed, each with a label and a reason — recorded on the bot for the status page
- `MAINTENANCE = True` and `DNL = True` with a `*_REASON` let a module announce its own state; those rows stay read-only in the dashboard
- German, Spanish and French files for the shared chrome, plus the landing page in all four languages

### improved
- The status page's cogs and shards are laid out as glass cards, single column on phones
- A shard reports `starting`, with no latency, until its first heartbeat arrives
- The status page, the landing page and the commands page count commands the same way — 323 today, subcommands and context menus included
- Maintenance also covers context menus and the AI's name replies, not only slash and prefix commands
- Number emojis (0–9) redrawn from Phosphor's digits, on the same grid and stroke weight as the rest of the icon set
- `/avatar` shows a user's global banner and their server banner as two labelled galleries, read from the REST user instead of the gateway cache
- The leveling panel's headings and navigation use Niko's own emojis instead of unicode glyphs
- Page titles follow the route and the chosen site language instead of staying on the landing page's title
- **Dashboard translation is not finished** — this update is the first part of it and the most complex: the catalogues, the picker and the coverage readout are in place, while the staff workspace's remaining admin tabs, the owner devtools and the render lab are still English and follow in later updates.

### fixed
- A paused cog still answering its user and message context menus
- Group commands (`/sticker`, `/stage`, `/soundboard`, `/premium`, `/boosterrole`) listed as having no cog in the maintenance tab
- A shard that was still connecting showing roughly 5,000 ms of latency instead of a starting state
- The status page's command count disagreeing with the landing page and the commands page

### migrated
- Page copy moved out of components into `web/src/locales/<page>/en.json`; docs articles, changelog entries and the legal documents stay authored content, not catalogue entries
- `load_locales` and the tests now expect `fr.json` beside every `en.json`, `de.json` and `es.json`

## Chart data

```json
{
  "type": "metrics",
  "title": "Release At a Glance",
  "data": [
    {
      "label": "Catalogues",
      "value": "28",
      "detail": "pages plus the shared chrome",
      "color": "#4a7fb5"
    },
    {
      "label": "Site strings",
      "value": "2,955",
      "detail": "English copy now in JSON",
      "color": "#66866f"
    },
    {
      "label": "Bot strings",
      "value": "3,904",
      "detail": "already in four languages",
      "color": "#d96545"
    }
  ]
}
```
