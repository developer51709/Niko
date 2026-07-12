# Undocumented & Lightly-Documented Discord Endpoints
> Research for Niko Bot — cross-referenced against discord.py 2.7.1 + current bot codebase.
> ✅ = implemented in bot · 📋 = documented here, not yet wired up
> All HTTP client methods listed are confirmed present in `discord.http.HTTPClient`.

---

## ✅ 1. Voice Channel Status
**`bot.http.edit_voice_channel_status(status, *, channel_id)`**
**File:** `src/utils/discord_extras.py` → `set_voice_status()`
**Wired into:** `src/cogs/music/cog.py` — auto-sets on track start (`on_wavelink_track_start`), clears on disconnect/idle

Sets a custom text line visible to every member in the voice channel list — like a "now playing" ticker.
Signature: `edit_voice_channel_status(status: str | None, *, channel_id: int)` — status first, channel_id is keyword-only.
Almost no bots use this. Requires `MANAGE_CHANNELS` or being in the channel.

```python
# In discord_extras.py:
await bot.http.edit_voice_channel_status(status or "", channel_id=channel_id)
```

---

## ✅ 2. Native Discord Polls
**`discord.Poll` — `bot.http.end_poll()` — `bot.http.get_poll_answer_voters()`**
**File:** `src/utils/ai/actions.py` → `_do_create_poll()`

Discord renders these natively with progress bars and a distinct poll card. Replaced the AI-action's legacy emoji-reaction poll. Falls back to the old system if native polls are unsupported.

```python
poll = discord.Poll(question=question, duration=datetime.timedelta(hours=24), multiple=False)
for opt in options:
    poll.add_answer(text=opt[:55])
await channel.send(poll=poll)
```

**Gateway events available (not yet wired):**
```python
async def on_poll_vote_add(payload: discord.RawPollVoteActionEvent): ...
async def on_poll_vote_remove(payload: discord.RawPollVoteActionEvent): ...
```

---

## ✅ 3. Soundboard Integration
**`bot.http.send_soundboard_sound(channel_id, **payload)` — `get_soundboard_sounds(guild_id)` — `get_soundboard_default_sounds()`**
**File:** `src/cogs/fun/soundboard.py` — `/soundboard list`, `/soundboard play`, `/soundboard default`

Bot can list and play guild or Discord default sounds in any voice channel.
`send_soundboard_sound` takes `**kwargs` — pass `sound_id=` and optionally `source_guild_id=` (omit for default sounds).
`get_soundboard_sounds` returns `{"items": [...]}` dict; `get_soundboard_default_sounds` returns a plain list.

```python
await bot.http.send_soundboard_sound(channel_id, sound_id=sound_id, source_guild_id=guild_id)
```

---

## ✅ 4. Burst / Super Reactions
**Raw HTTP via `discord.http.Route`**
**File:** `src/utils/discord_extras.py` → `burst_react()`
**Wired into:** Giveaway winners (`⭐` on giveaway msg, `🎉` on announcement), Level-ups (`🎉`)
**Command:** `/burst <message_id> <emoji>` (in `src/cogs/system/nitro.py`)

Bot accounts can send burst/super reactions without Nitro. Animated burst effect across screen.

```python
route = Route("PUT", "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
              channel_id=..., message_id=..., emoji=url_encoded_emoji)
await bot.http.request(route, params={"burst": "true"})
```

---

## ✅ 5. Components v2 — Section + Thumbnail (Nitro aesthetic)
**`discord.ui.Section` · `discord.ui.Thumbnail` · `discord.ui.UnfurledMediaItem`**
**File:** `src/cogs/system/nitro.py` → `_user_profile_ctx()` context menu

User profile context menu uses `Section` + `Thumbnail` for a side-by-side avatar + stats card.
No image generation (PIL) needed — pure Discord layout.

```python
section = discord.ui.Section(
    discord.ui.TextDisplay(content="stats here"),
    accessory=discord.ui.Thumbnail(discord.ui.UnfurledMediaItem(url=avatar_url)),
)
view = discord.ui.LayoutView()
view.add_item(discord.ui.Container(section, accent_colour=discord.Colour(0xc8a882)))
```

---

## ✅ 6. Message Forwarding (Discord 2024 feature)
**Raw HTTP via `Route` — `message_reference.type = 1`**
**File:** `src/utils/discord_extras.py` → `forward_message()`
**Command:** `/forward <message_id> <destination>` (in `src/cogs/system/nitro.py`)

Native message forwarding. Type 0 = reply (existing), type 1 = forward (shows original in a frame).
No discord.py wrapper yet — must use raw Route.

```python
payload = {"message_reference": {"type": 1, "message_id": str(mid), "channel_id": str(src_id)}}
await bot.http.request(Route("POST", "/channels/{channel_id}/messages", channel_id=dest_id), json=payload)
```

---

## ✅ 7. Context Menus (Nitro-tier discoverability)
**`discord.app_commands.ContextMenu` — registered via `bot.tree.add_command()`**
**File:** `src/cogs/system/nitro.py` — `☕ Ask Niko` (message), `📊 User Profile` (user)

Right-click menus. Must be registered in cog `__init__` via `bot.tree.add_command()` and removed in `cog_unload()`.

```python
self._ctx_ask = app_commands.ContextMenu(name="☕ Ask Niko", callback=self._ask_niko_ctx)
self.bot.tree.add_command(self._ctx_ask)
# In cog_unload:
self.bot.tree.remove_command(self._ctx_ask.name, type=self._ctx_ask.type)
```

---

## ✅ 8. Sticker Management (Nitro-adjacent)
**`bot.http.get_all_guild_stickers(guild_id)` — `guild.fetch_sticker(id)` — `channel.send(stickers=[sticker])`**
**Commands:** `/sticker list`, `/sticker send` with autocomplete (in `src/cogs/system/nitro.py`)

Bots can list, send, and upload guild stickers. Sending requires a `discord.Sticker` object from `fetch_sticker()`.

---

## ✅ 9. Stage Channel Speaker
**`bot.http.edit_my_voice_state(guild_id, channel_id=..., suppress=False, request_to_speak_timestamp=...)`**
**File:** `src/utils/discord_extras.py` → `stage_become_speaker()`
**Command:** `/stage speak` (in `src/cogs/system/nitro.py`)

Makes the bot a speaker on a Stage channel. Must already be in the Stage. Sends both a request-to-speak timestamp and suppress=False simultaneously.

---

## ✅ 10. Voice Status Command
**`/vcstatus <text>` (in `src/cogs/system/nitro.py`)**

Manual override for the voice channel status. Useful for VoiceMaster channels. Wraps `set_voice_status()` from `discord_extras.py`.

---

## 📋 11. Poll Vote Gateway Events (not yet wired)
```python
@bot.event
async def on_poll_vote_add(payload: discord.RawPollVoteActionEvent):
    # payload.user_id, payload.channel_id, payload.message_id, payload.answer_id
    pass
```

---

## 📋 12. Forum Thread Tags + Search (not yet wired)
**`bot.http.start_thread_in_forum(channel_id, ..., applied_tags=[tag_id])`**
**Thread search (undocumented):**
```python
from discord.http import Route
route = Route("GET", "/channels/{channel_id}/threads/search", channel_id=forum_id)
results = await bot.http.request(route, params={"query": "café", "limit": 25})
```

---

## 📋 13. GUILD_SYNC Gateway Opcode (undocumented — op 12)
Not part of discord.py's public API. Forces member presence sync for specific guilds.
```python
await ws.send_as_json({"op": 12, "d": [str(guild_id)]})
```
**Caution:** Undocumented — rate-limited, may change without notice.

---

## 📋 14. Role Connections / Linked Roles
Push XP level / economy rank to Discord so admins can gate roles on it natively.
```python
# Requires user OAuth token (not bot token):
PUT /users/@me/applications/{app_id}/role-connection
{"platform_name": "Niko Café", "metadata": {"economy_level": "12", "daily_streak": "5"}}
```

---

## 📋 15. SKUs & Entitlements (monetization)
**`bot.http.get_skus(app_id)` · `bot.http.get_entitlements(app_id, ...)` · `bot.http.consume_entitlement(app_id, id)`**
Gate premium features behind Discord's native subscription system — no Stripe needed.
```python
entitlements = await bot.http.get_entitlements(application_id=bot.application_id, user_id=user.id)
has_premium = any(e["sku_id"] == PREMIUM_SKU_ID for e in entitlements)
```

---

## Nitro Features Bots Can Use (Summary)

| Feature | Status | Notes |
|---------|--------|-------|
| Burst/super reactions | ✅ Implemented | No Nitro needed for bots |
| Soundboard playback | ✅ Implemented | Guild + default sounds |
| Voice channel status | ✅ Implemented | Music auto-sets it |
| Animated emoji | ✅ Always available | `<a:name:id>` format |
| Application emoji | ✅ Already done | Works in all servers |
| External emoji | ✅ Requires permission | `use_external_emojis` |
| Sticker send/manage | ✅ Implemented | `/sticker` commands |
| Stage channel speaker | ✅ Implemented | `/stage speak` |
| Message forwarding | ✅ Implemented | `/forward` command |
| Context menus | ✅ Implemented | Right-click actions |
| Native polls | ✅ Implemented | AI action upgraded |
| Rich presence with images | ✅ Via activity | Already used |
| Profile banner | 📋 Possible | `edit_profile` with base64 |
| Role connections | 📋 Planned | Needs OAuth flow |
| SKUs/Entitlements | 📋 Planned | Premium tier support |
| 4000 char messages | ❌ Not available | Bots capped at 2000 |

---

## Implementation Locations

| Feature | File |
|---------|------|
| Burst react, VC status, forward, stage | `src/utils/discord_extras.py` |
| Soundboard commands | `src/cogs/fun/soundboard.py` |
| Context menus, stickers, VC status cmd, forward cmd | `src/cogs/system/nitro.py` |
| Native poll (AI action) | `src/utils/ai/actions.py` |
| Auto VC status on track start/end | `src/cogs/music/cog.py` |
| Burst react on giveaway win | `src/cogs/giveaway/cog.py` |
| Burst react on level up | `src/cogs/leveling/cog.py` |
