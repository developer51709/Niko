---
name: Mixin cog pattern
description: How moderation and economy use plain mixin classes with discord.py Cog multiple inheritance
---

## Rule
Large cogs (moderation, economy) are split into mixin classes defined in `_*.py` or `commands/*.py` files. The main Cog class uses multiple inheritance to combine them:
```python
class Moderation(MembersMixin, MessagesMixin, ChannelsMixin, SettingsMixin, commands.Cog):
    def __init__(self, bot): self.bot = bot
    def utils(self): return self.bot.get_cog("ModerationUtils")
    def logger(self): return self.bot.get_cog("ServerLogger")
```

## How to apply
- Mixin classes are plain Python classes (no `commands.Cog` in their own MRO).
- All `@commands.hybrid_command` / `@commands.hybrid_group` decorators in mixins are picked up by discord.py when the Cog is registered.
- Mixin methods use `self.utils()`, `self.logger()`, `self.bot`, `self.get_user_economy_data()` etc — these resolve at runtime via the combined Cog instance.
- Each mixin file imports its needed helpers at the top (e.g. `from ._messages import msg, _cv2` for moderation, `from ..data import *` for economy).

**Why:** Moderation was 828 lines; economy was 937 lines. Splitting into ~150-200 line mixin files makes individual features easy to find and edit without touching unrelated code.
