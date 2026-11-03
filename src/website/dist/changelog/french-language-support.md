# Niko Speaks French

- Date: 2026-10-30
- Version: 2.25.0
- Tags: languages, localization, french, commands, website, added

French is Niko's fourth language. Command help lines, replies, panels, error messages, the help menu and Discord's own slash command descriptions are translated across every cog, so a French server stops reading English. The wording lives in the same `locales` folder as the other three, which kept this a translation job rather than a refactor.

## Highlights

### The Fourth Language
Set the server's language in Discord and Niko answers in French: replies, panels, errors and the help menu all follow. Any French locale — `fr`, `fr-FR`, `fr-CA` — resolves to French, and English stays the fallback for a key no translation has reached yet.

### Discord's Command List Follows
Slash command descriptions, subcommand descriptions and argument hints are sent to Discord in French too, so a French client sees French in the `/` picker while a German client keeps German.

### Twenty-Four Cogs, One Shape
Every cog that already carried `en.json`, `de.json` and `es.json` now has `fr.json` beside them, with the wording in the same `commands` and `messages` namespaces, so the next language is again a translation job rather than a change to Python.

### The Website Follows the Visitor
The commands page reads the browser's language and renders the French description from the same catalogue the bot uses, so the site and Discord cannot drift apart on a command's wording.

## Changes

### added
- French (`fr`) as a shipped language in `utils/locales.py`
- `fr.json` for all 24 cogs that carry a locale folder
- French slash command, subcommand and option descriptions
- French help menu, per-command help lines and panel wording
- French AI action wording under `utils/ai/locales/fr.json`

### improved
- A key missing from French falls back to English instead of an empty reply
- Command descriptions stay in one place, so the bot and the website read the same French text

## Commits
- 7b5cca8 Added support for french
- 88513d1 Added french to the supported locales
