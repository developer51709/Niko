# Emoji assets

The folder is split by ownership, so a generation run cannot silently replace
art another source owns:

| Folder | Owner | Used for |
| --- | --- | --- |
| `badges/` | `scripts/build-badge-art.mjs` | Niko role badges, Discord profile badges, account-age and boosting tiers |
| `manual/` | hand-maintained | art with no generation script: status dots, HypeSquad, Connect Four, legacy icons, downloads |
| `review/` | pending review | old generated art with no clean With Icons equivalent (see `review/README.md`) |
| `seasonal/default/` | `scripts/build-emoji-icons.mjs` | the generic With Icons outline set |
| `seasonal/christmas/` | `scripts/build-emoji-icons.mjs` | `*_christmas` variants |
| `seasonal/halloween/` | `scripts/build-emoji-icons.mjs` | `*_halloween` variants |
| `seasonal/valentine/` | `scripts/build-emoji-icons.mjs` | `*_valentine` variants |

The sync resolves a name in this order: active seasonal variant, generic
default, badge art, manual art, review art. A missing file is downloaded into
`manual/`, never into a generated folder.

The seasonal choice is date-based (`src/utils/emoji_seasons.py`). Variants are
separate uploaded application emojis, not replacements, so returning to the
generic set is just a config lookup and does not change any emoji ids.
