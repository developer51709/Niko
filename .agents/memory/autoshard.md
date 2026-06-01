---
name: AutoShardedBot switch
description: bot.py now uses AutoShardedBot; key structural decisions for the sharding refactor
---

## Rule
`bot.py` instantiates `commands.AutoShardedBot` with an optional `SHARD_COUNT` env var:
```python
_shard_count = int(os.getenv("SHARD_COUNT", "0")) or None
bot = commands.AutoShardedBot(command_prefix=dynamic_prefix, intents=intents, shard_count=_shard_count)
```
Setting `shard_count=None` tells Discord to auto-determine the optimal shard count.

## Supporting utils extracted from bot.py
- `utils/gateway.py` — `patch_identify(device)` spoofs IDENTIFY payload
- `utils/blacklist.py` — `check_message_blacklist(msg)` and `check_interaction_blacklist(interaction)`
- `utils/ai/reply.py` — `generate_reply(...)` dispatcher + `AI_ENABLED`, `AI_MODE`, `ANSWER_REPLYS` constants
- `utils/prefix_manager.py` — `dynamic_prefix(bot, message)` callable

## Event files
- `events/on_ready.py` — `handle_ready(bot)` (DB init, cog load, status, banner, stats export)
- `events/on_message.py` — `handle_message(bot, msg)` (prefix dispatch, AI trigger, blacklist gate)

**Why:** Keeping bot.py thin (< 60 lines) makes it easy to add environment-level sharding config without digging through business logic.
