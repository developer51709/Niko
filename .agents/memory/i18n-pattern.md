---
name: i18n make_msg vs make_flat_msg
description: When to use make_msg (personality-aware) vs make_flat_msg (flat lang dict) from utils/i18n.py
---

## Rule
- Use `make_msg(MESSAGES)` when the MESSAGES dict is `{personality: {lang: {key: str}}}` — all fun, ai, admin, info, leveling, music, social, and utility cogs use this layout.
- Use `make_flat_msg(MESSAGES)` when the MESSAGES dict is `{lang: {key: str}}` — moderation/_messages.py uses this layout.

## How to apply
In any cog module with a MESSAGES dict, replace the boilerplate `get_lang()` + `msg()` inline functions with a single line:
```python
from utils.i18n import make_msg   # or make_flat_msg
msg = make_msg(MESSAGES)
```
`make_msg` calls `get_personality(ctx)` and `get_lang(ctx)` internally with a 4-level fallback (personality+lang → personality+en → normal+lang → normal+en).

**Why:** 17+ cogs had near-identical copy-pasted get_lang()/msg() definitions — consolidating to utils/i18n.py eliminates the duplication.
