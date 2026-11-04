# Languages & Localization

Niko ships in **English**, **German**, **Spanish**, **French**, **Russian**, **Japanese**, **Chinese**, **Hindi**, and **Arabic**. English is the default and the fallback: if a string has not been translated yet, the English wording is used instead of an empty reply.

The first four are complete. The other five are rolling out one catalogue at a time, so a panel, a command or a whole cog may still answer in English while its neighbours are translated. That is expected, not a bug — nothing is ever half-sentenced.

## What is translated

- **Discord's command UI.** Slash command descriptions, subcommand descriptions, and option descriptions arrive in your members' own language. A member browsing `/` in a German Discord client sees German, even when the server itself is English.
- **Niko's own wording.** Command help lines, replies, panels, and error messages use the server's language.
- **The website.** The commands page at [/commands](/commands) follows the language of the browser that opens it.
- **The help menu.** `.help` and `/help` read the catalogue in the server's language, including the one-line summary under each command.

## How the language is chosen

Niko reads the **server's preferred locale** in Discord (Server Settings → Overview → Server Language). Any `de` locale picks German, any `es` locale picks Spanish, any `fr` locale picks French, any `ru`, `ja`, `zh`, `hi` or `ar` locale picks that language, and everything else falls back to English, so a server only has to set its language once. A regional locale such as `fr-FR`, `zh-CN` or `es-419` counts as its base language.

Slash command names stay in English so permissions, documentation, and moderation logs match; their descriptions are localized. Some context menus also rename themselves, for example *Translate* becomes *Übersetzen*. Discord has no Arabic client locale, so in Arabic the bot's own wording is translated while the command descriptions stay in the language of the member's Discord client.

## Keeping translations up to date

Translations live next to the code, not in a translation service: every cog has a `locales` folder with one JSON file per language it has reached, and the command wording sits in the `commands` namespace of those files. `en.json` is the only file a cog must have; a language may arrive later, and a key that exists in English but not in another language is served in English, so a release never blocks on a translation.

Wording saved on the staging instance reaches the live bot and the live site within seconds, without a deploy or a restart — a translation is a file edit, not a release.

If you spot a wrong or awkward translation, report it in the [support server](/support) with the command name and the language — the wording is a one-line edit in the matching JSON file.
