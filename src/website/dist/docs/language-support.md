# Languages & Localization

Niko ships in **English**, **German**, and **Spanish**. English is the default and the fallback: if a string has not been translated yet, the English wording is used instead of an empty reply.

## What is translated

- **Discord's command UI.** Slash command descriptions, subcommand descriptions, and option descriptions arrive in your members' own language. A member browsing `/` in a German Discord client sees German, even when the server itself is English.
- **Niko's own wording.** Command help lines, replies, panels, and error messages use the server's language.
- **The website.** The commands page at [/commands](/commands) follows the language of the browser that opens it.
- **The help menu.** `.help` and `/help` read the catalogue in the server's language, including the one-line summary under each command.

## How the language is chosen

Niko reads the **server's preferred locale** in Discord (Server Settings → Overview → Server Language). Any `de` locale picks German, any `es` locale picks Spanish, and everything else falls back to English, so a server only has to set its language once.

Slash command names stay in English so permissions, documentation, and moderation logs match; their descriptions are localized. Some context menus also rename themselves, for example *Translate* becomes *Übersetzen*.

## Keeping translations up to date

Translations live next to the code, not in a translation service: every cog has a `locales` folder with `en.json`, `de.json`, and `es.json`, and the command wording sits in the `commands` namespace of those files. A key that exists in English but not yet in German or Spanish is served in English, so a release never blocks on a translation.

If you spot a wrong or awkward translation, report it in the [support server](/support) with the command name and the language — the wording is a one-line edit in the matching JSON file.
