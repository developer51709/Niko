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
The scan lives in `src/webapp/status.py`.

Dashboard routes have folders too, under their own page ids: `dashboard`,
`staff`, `staff-email`, `staff-email-reports`, `billing`, `gift`, `transcript`,
`application`, `appeal`, `email-report`, `team-application`. Record routes
(`docs-detail`, `team-member`, `changelog-detail`) have none: their title comes
from the record the server rendered.
