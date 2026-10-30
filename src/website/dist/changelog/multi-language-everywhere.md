# Niko Now Speaks German and Spanish — Everywhere

- Date: 2026-10-29
- Tags: languages, localization, commands, website, dashboard, added

Niko is trilingual. Command help lines, replies, the help menu, and the website's command reference now exist in English, German, and Spanish, and Discord itself receives translated slash command and option descriptions so each member sees the `/` picker in their own language. Every cog keeps its wording in a `locales` folder next to the code, which makes adding the next language a translation job rather than a refactor.

## Highlights

### Three Languages, One Bot
Set your server's language and Niko answers in it: replies, panels, error messages, the help menu, and every command's help line. English stays the default, and a missing translation falls back to it instead of empty text.

### Discord's Command List Follows the Member
Slash command descriptions, subcommand descriptions, and argument hints are sent to Discord in all three languages, so the `/` picker speaks each member's Discord client language. Context menus rename themselves as well.

### The Website Follows the Visitor
The commands page reads the browser's language and renders every command and argument description in it, from the same catalogue the bot uses, so the site and Discord can never drift apart.

### Wording Lives Beside the Code
Every cog is a package with a `locales/en.json`, `de.json`, and `es.json`, one shape for all of them. Command text lives in a `commands` namespace keyed by the command path Discord shows, so a translator edits JSON instead of reading Python.

## Changes

### added
- Every cog ships a `locales` folder with `en.json`, `de.json`, and `es.json` using one consistent package layout
- Command help lines, short descriptions, and argument text moved out of Python into each cog's `commands` namespace
- German and Spanish wording for every command description and documented argument across the bot
- Discord receives `name_localizations` and `description_localizations` for slash commands, subcommands, and options, via `utils/command_localization.py`
- Localized context menu names such as *Übersetzen* and *Rollenspiel*
- `/api/commands` now serves `{ en, de, es }` maps for command descriptions and arguments
- A Languages & Localization guide covering what is translated and how Niko picks a language

### improved
- The help menu reads the same catalogue as the website, including each command's summary line
- The commands page renders argument descriptions in the visitor's language instead of the raw parameter name
- The startup command fingerprint includes translations, so editing a `locales` file triggers a sync instead of being skipped as "no command changes"
- Translations are clamped to Discord's 32/100 character limits per field, so one long line cannot fail an entire command sync
- The owner `.sync` command applies localizations too, covering commands added by a cog reload

### fixed
- Hybrid subcommands no longer send their serialized help map to Discord as the description — the readable English line is used instead
- Options declared without `@app_commands.describe` no longer show discord.py's empty placeholder in Discord's UI
- Command descriptions in Discord, the help menu, and the website now come from one source, so they cannot disagree
