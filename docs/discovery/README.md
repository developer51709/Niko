# Discovery listing

Copy-and-paste copy for Niko's bot discovery listing, one file per language, and the
card artwork each listing embeds. The listing is localised, so each language is a
self-contained description rather than a translation note on the English one.

| Language | Description | Card |
|---|---|---|
| English | [`en.md`](en.md) | <https://niko.sryze.cc/assets/discovery/en.png> |
| German | [`de.md`](de.md) | <https://niko.sryze.cc/assets/discovery/de.png> |
| Spanish | [`es.md`](es.md) | <https://niko.sryze.cc/assets/discovery/es.png> |
| French | [`fr.md`](fr.md) | <https://niko.sryze.cc/assets/discovery/fr.png> |

## Publishing a description

1. Open the bot's listing in the developer portal and find the application description
   section.
2. Add the language, then paste the whole file — image line included — into the
   extended description field. Do not paste the file name or the table above.
3. Keep the trailing link list: the invite, dashboard, support server, and docs links are
   the only way from the listing into the product.

Two fields are filled in separately from these files:

- **Summary.** Capped at 200 characters by Discord and shown in search results, so it
  stays a single short sentence rather than a shortened copy of the description.
- **Media.** The portal's carousel takes up to five images or videos, and Discord does not
  document inline markdown images in the description itself. Where the card does not
  render inline, add its URL from the table above as the first carousel image — the file
  is the same either way.

Discord does not publish a maximum length for the extended description. The copy here
stays around 2,500 characters so the page reads as an introduction rather than a manual,
and it avoids emoji to match the bot's own command and help wording.

## The cards

`web/public/assets/discovery/<lang>.png` is the source file, mirrored into the committed
website build at `src/website/dist/assets/discovery/` so the running bot serves the URL
above before the next full build. Both copies are generated, never hand-edited:

```bash
python3 scripts/generate_discovery_cards.py
```

`npm run build` runs the same script through the package's `prebuild` hook, so a build
always refreshes the cards. The headline, tagline, three feature rows, and language label
live in `CARD_COPY` in that script; change the artwork and the description together, or
the listing will promise something the card does not show.

Keep the artwork generic: no server counts, no member totals, nothing that goes stale
between builds. The cards use the dashboard's own tokens from `web/src/styles.css` — the
near-black canvas, hairline rules, and the single sage accent — with no glows, noise, or
illustration, so the image supports the listing instead of competing with it.

Each card is a rounded rectangle saved as RGBA with transparent corners, so it can sit on
Discord's dark or light message background without a painted box around it. Do not flatten
the files to JPEG or composite them onto a background: that puts the corners back.
