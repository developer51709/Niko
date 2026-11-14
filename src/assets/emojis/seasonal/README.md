# Seasonal emoji art

`default/` is the generic generated set (With Icons outline art). It is used
outside every holiday window.

`christmas/`, `halloween/` and `valentine/` hold the suffixed variants, for
example `heart_christmas.png`. The suffix is the config key: while the season
is active, `get_emoji("heart")` resolves to `heart_christmas`; outside the
window it resolves back to `heart`. All variants are uploaded once, so the
switch does not delete or re-upload Discord emojis.

The variants cover every general-purpose emoji: navigation, people, content,
utility, media controls, progression and the celebration rewards. State
indicators (ticks, crosses, warnings, locks), machine stats and per-event log
marks deliberately stay on the generic set so their colour is unambiguous all
year.

Season windows live in `src/utils/emoji_seasons.py` and are intentionally
short: Halloween Oct 1–Nov 2, Christmas Dec 1–Jan 6, Valentine Feb 1–15.

Regenerate everything with:

```bash
node scripts/build-emoji-icons.mjs
```
