# Website & dashboard locale catalogues

One folder per page, named after the `Page` value in `web/src/router.ts`:

```
locales/
  shared/        chrome every page renders (navigation)
    en.json
    de.json
    es.json
    fr.json
  status/        the /status page
    en.json
  home/          the landing page
    en.json
```

`en.json` is the source copy and holds every string the page renders itself:
headings, buttons, empty states, error text, form labels, and screen-reader
copy. Add `de.json`, `es.json`, or `fr.json` beside it as that page is
translated; a missing language falls back to English, and a missing key falls
back to the English string, so a half-translated page never shows raw keys.

Long-form content is not catalogue copy and stays where it is authored: doc
articles (`web/src/data/docs`), changelog entries, the legal documents in
`LegalPage.tsx`, and the data-removal policy block. Their page chrome is in the
catalogue; the prose itself is content, like a doc article.

Read strings through `useStrings("<page>")` from `web/src/i18n`:

```tsx
const { t } = useStrings("status");
<h1>{t("title")}</h1>
```

`shared/` is consulted after the page's own catalogue, so a page can word a
shared string its own way without duplicating every navigation label.

## Trying a translation

The owner devtools panel (bottom-left **Dev** button) has a **Site language**
picker on its **Page** tab. It switches the site's language for that browser
only, remembers the choice in `localStorage`, and leaves Discord replies alone —
they keep following each guild's locale.

## Coverage

`/status` counts these catalogues: each language's translated leaf keys against
`en`, summed across every folder present. A page without a folder is not counted,
so the figure only ever describes copy that actually exists. The page line counts
a page as done only when its file covers every key its `en.json` has, so a
translation that stopped halfway stays partial instead of passing for finished.
The scan lives in `src/webapp/status.py`; the merge with a live feed is in
`src/webapp/locale_feed.py`.

## Live feed from beta

A translation pass is written over days on the beta instance, and waiting for a
deploy to show it — or for `/status` to stop reporting yesterday's coverage — is
the wrong shape for that work. Set `BETA_INSTANCE_URL` to the beta origin on the
production instance and it reads beta's files directly:

```
BETA_INSTANCE_URL=https://beta.example.com
```

No restart, no git pull. Production re-reads beta's manifest every 15 seconds
(`LOCALE_FEED_TTL`) and fetches a page's catalogue the first time someone opens
that page, so new strings and new languages appear as they are written. `/status`
reports the merged coverage and says where it came from — a **Live from beta**
chip, or **From this build** when the feed is off or unreachable.

Three endpoints make this work, all served by every instance:

| Endpoint | Who reads it | What it returns |
| --- | --- | --- |
| `/api/locales/source.json` | the other instance's feed | this instance's own files: page key counts, a hash per language file, and the bot's coverage |
| `/api/locales/index.json` | the browser | the merged manifest: languages, pages, hashes used to cache each file |
| `/api/locales/<page>/<lang>.json` | the browser | one catalogue, beta's copy first, with an `ETag` |

What the feed will not do:

- **It cannot add a page.** A page beta has and this build does not is ignored;
  there is no route for it. A new *language* works because it is just another
  catalogue file.
- **It cannot blank a page.** A catalogue that fails validation, a timeout, or a
  broken beta response falls back to the files in this deployment.
- **It cannot slow a page down.** Only the first read after a process starts
  waits for beta; later reads refresh on a background thread. A beta that goes
  away leaves the last good manifest in place, marked stale on `/status`.

When beta is not configured, everything behaves exactly as before: the bundled
catalogues and the local scan.

Dashboard routes have folders too, under their own page ids: `dashboard`,
`staff`, `staff-email`, `staff-email-reports`, `billing`, `gift`, `transcript`,
`application`, `appeal`, `email-report`, `team-application`. Record routes
(`docs-detail`, `team-member`, `changelog-detail`) have none: their title comes
from the record the server rendered.
