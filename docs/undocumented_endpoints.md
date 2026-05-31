# Undocumented & Lightly-Documented Discord Endpoints
> Research for Niko Bot — cross-referenced against discord.py 2.7.1 + current bot codebase.
> "Undocumented" = not in official Discord developer docs or buried in beta/preview sections.
> All HTTP client methods listed are confirmed present in `discord.http.HTTPClient`.

---

## 1. Voice Channel Status  ⭐ highest visual impact
**`bot.http.edit_voice_channel_status(channel_id, status)`**

Sets a custom text line visible to every member in the voice channel list — like a "now playing" ticker or mood setter. Almost no bots use this.

```python
# Raw call (discord.py wraps it):
await bot.http.edit_voice_channel_status(channel_id, status="☕ lo-fi beats · chill mode")
# Clear it:
await bot.http.edit_voice_channel_status(channel_id, status=None)
```

**Use cases for Niko:**
- Music cog: auto-set to current song title + artist when a track starts
- VoiceMaster: set status when a temp channel is created ("🎮 Gaming", "📖 Study")
- Clear on disconnect / channel empty

**Permissions needed:** `MANAGE_CHANNELS` or user is in the channel.
**Discord docs:** Not in stable docs — preview/beta only.

---

## 2. Native Discord Polls  ⭐ aesthetic upgrade over button polls
**`discord.Poll` — `bot.http.end_poll(channel_id, message_id)` — `bot.http.get_poll_answer_voters(...)`**

Discord renders these natively with progress bars, emoji answers, and a distinct poll card UI. Vastly cleaner than Niko's current button-based polls. The bot currently hand-rolls polls with `PollView` buttons and JSON storage.

```python
poll = discord.Poll(
    question="best café drink? ☕",
    duration=datetime.timedelta(hours=24),
    multiple=False,
)
poll.add_answer(text="espresso", emoji="☕")
poll.add_answer(text="matcha latte", emoji="🍵")
poll.add_answer(text="hot cocoa", emoji="🍫")

msg = await channel.send(poll=poll)

# End early:
await bot.http.end_poll(channel_id, message_id)

# Get who voted for answer 1:
voters = await bot.http.get_poll_answer_voters(channel_id, message_id, answer_id=1)
```

**Gateway events (already in discord.py):**
```python
@bot.event
async def on_poll_vote_add(payload: discord.RawPollVoteActionEvent): ...
@bot.event
async def on_poll_vote_remove(payload: discord.RawPollVoteActionEvent): ...
```

**Note:** Can coexist alongside the existing custom poll system — native polls for slash commands, custom polls for prefix commands.

---

## 3. Soundboard Integration  ⭐ unique voice channel feature
**`bot.http.send_soundboard_sound(channel_id, sound_id, source_guild_id)`**
**`bot.http.get_soundboard_sounds(guild_id)` / `bot.http.get_soundboard_default_sounds()`**
**`bot.http.create_soundboard_sound(guild_id, ...)` / `bot.http.delete_soundboard_sound(guild_id, sound_id)`**

The bot can play sounds in voice channels and manage the guild soundboard. Almost no non-music bots do this.

```python
# Get guild soundboard sounds:
sounds = await bot.http.get_soundboard_sounds(guild_id)

# Play a sound (bot must be in the VC):
await bot.http.send_soundboard_sound(
    channel_id=vc.id,
    sound_id=sound["sound_id"],
    source_guild_id=guild_id,  # None for default sounds
)

# Get Discord's default sounds (free for everyone):
defaults = await bot.http.get_soundboard_default_sounds()
```

**Gateway event — detect when ANY user plays a soundboard sound:**
```python
@bot.event
async def on_voice_channel_effect(payload):  # VOICE_CHANNEL_EFFECT_SEND
    # payload.sound_id, payload.channel_id, payload.user_id
    ...
```

**Use cases for Niko:**
- `/soundboard play <name>` — slash command to play a guild sound
- Auto-play café ambiance sound when a VoiceMaster channel is created
- Reaction sound when giveaway ends

---

## 4. Components v2 — Advanced Layout (unused by bot)  ⭐ aesthetic differentiation
**`discord.ui.Section` · `discord.ui.MediaGallery` · `discord.ui.Thumbnail` · `discord.ui.UnfurledMediaItem` · `discord.ui.File`**

The bot already uses `LayoutView`, `Container`, `TextDisplay`, `ActionRow`, and `Separator` — but misses these more powerful layout primitives that almost no public bots use.

### Section — content + accessory side-by-side
```python
section = discord.ui.Section(
    discord.ui.TextDisplay("### ☕ Your Café Card\nLevel 12 · Barista"),
    accessory=discord.ui.Thumbnail(
        discord.ui.UnfurledMediaItem(url=user.display_avatar.url)
    ),
)
container = discord.ui.Container(section, accent_colour=discord.Color.from_str("#c8a882"))
view = discord.ui.LayoutView()
view.add_item(container)
await ctx.send(view=view)
```

### MediaGallery — multi-image grid in one message
```python
gallery = discord.ui.MediaGallery(
    discord.ui.MediaGalleryItem(discord.ui.UnfurledMediaItem(url=img1)),
    discord.ui.MediaGalleryItem(discord.ui.UnfurledMediaItem(url=img2)),
    discord.ui.MediaGalleryItem(discord.ui.UnfurledMediaItem(url=img3)),
)
view = discord.ui.LayoutView()
view.add_item(discord.ui.Container(gallery))
await ctx.send(view=view)
```

**Use cases for Niko:**
- Economy card: Section with user avatar thumbnail + stats text side-by-side (no PIL needed)
- Casino / blackjack: MediaGallery for card images
- Profile command: Section layout instead of embed
- Image generation results: MediaGallery for multiple outputs

---

## 5. Burst / Super Reactions  (lightly documented)
**Raw HTTP — not a named method, needs `Route`**

Nitro users can send "burst" reactions that animate across the screen. Bots can send them too — the server doesn't check for Nitro on bot accounts.

```python
from discord.http import Route

async def burst_react(bot, channel_id: int, message_id: int, emoji: str):
    """emoji: 'name:id' for custom, or URL-encoded unicode like '%E2%98%95'"""
    route = Route(
        "PUT",
        "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
        channel_id=channel_id,
        message_id=message_id,
        emoji=emoji,
    )
    await bot.http.request(route, params={"burst": "true"})
```

**Use cases for Niko:**
- React with burst ☕ on giveaway winners
- Special burst reaction for milestone messages (level up, economy achievement)
- Easter egg: burst react when someone types "niko" 100 times

---

## 6. Voice State Editing  (lightly documented)
**`bot.http.edit_my_voice_state(guild_id, ...)` / `bot.http.edit_voice_state(guild_id, user_id, ...)`**

Allows bots to raise their hand, suppress themselves, or become a speaker on a Stage channel — and to move or suppress other users.

```python
# Make bot a speaker on a Stage:
await bot.http.edit_my_voice_state(
    guild_id,
    channel_id=stage_channel_id,
    suppress=False,
    request_to_speak_timestamp=datetime.datetime.utcnow().isoformat(),
)

# Suppress a user (move them to audience):
await bot.http.edit_voice_state(guild_id, user_id, suppress=True)
```

**Use cases for Niko:**
- Stage channel hosting — bot auto-becomes speaker when invited
- VoiceMaster: suppress bots moved into managed channels

---

## 7. Forum Thread Tags  (lightly documented)
**`bot.http.start_thread_in_forum(channel_id, ..., applied_tags=[tag_id])`**
**Thread search: `GET /channels/{channel_id}/threads/search?query=...` (no discord.py wrapper — use Route)**

```python
# Create a forum post with tags applied:
await bot.http.start_thread_in_forum(
    channel_id=forum_id,
    name="☕ Weekly Café Vibes",
    auto_archive_duration=1440,
    applied_tags=[tag_id_1, tag_id_2],
    content="this week's theme is lo-fi rain ☕🌧️",
)

# Thread search (undocumented — no official discord.py method):
from discord.http import Route
route = Route("GET", "/channels/{channel_id}/threads/search",
              channel_id=forum_id)
results = await bot.http.request(route, params={"query": "café", "limit": 25})
```

**Use cases for Niko:**
- Ticket system: auto-apply tags ("Open", "Billing", "Technical") on forum-based tickets
- Suggestion system: auto-tag suggestions by category
- `/forum search` command for searching threads

---

## 8. Message Forwarding  (very new, almost no bots support it)
**Raw HTTP — `message_reference.type = 1`**

Discord added native message forwarding in 2024. Type 0 = reply (existing), Type 1 = forward. No discord.py helper yet — needs raw Route.

```python
from discord.http import Route

async def forward_message(bot, target_channel_id: int, source_channel_id: int, message_id: int):
    route = Route("POST", "/channels/{channel_id}/messages", channel_id=target_channel_id)
    payload = {
        "message_reference": {
            "type": 1,
            "message_id": str(message_id),
            "channel_id": str(source_channel_id),
        }
    }
    return await bot.http.request(route, json=payload)
```

**Use cases for Niko:**
- Starboard: forward starred messages instead of reposting content
- Mod tools: forward reported messages to a mod channel
- Announcements: forward from one channel to another

---

## 9. SKUs & Entitlements  (documented but barely used by bots)
**`bot.http.get_skus(app_id)` · `bot.http.get_entitlements(app_id, ...)` · `bot.http.consume_entitlement(app_id, entitlement_id)`**

Discord's native premium feature system. Create SKUs in the Developer Portal, check entitlements in code, and gate features behind one-time purchases or subscriptions — all handled by Discord, no Stripe needed.

```python
# Check if a user has bought a premium feature:
entitlements = await bot.http.get_entitlements(
    application_id=bot.application_id,
    user_id=user.id,
    exclude_ended=True,
)
has_premium = any(e["sku_id"] == PREMIUM_SKU_ID for e in entitlements)

# Consume a one-time entitlement after use:
await bot.http.consume_entitlement(bot.application_id, entitlement_id)
```

**Gateway event:**
```python
@bot.event
async def on_entitlement_create(entitlement: discord.Entitlement): ...
```

**Use cases for Niko:**
- Premium AI personality / longer memory
- Premium economy features (higher daily limits, exclusive jobs)
- Premium image generation (HD, custom styles)

---

## 10. Role Connections / Linked Roles  (very few bots implement this)
**`PUT /users/@me/applications/{app_id}/role-connection`**

Lets Niko push metadata about a user (their level, economy rank, streak) to Discord, which admins can then use to gate roles automatically via Discord's native "Linked Roles" system.

```python
from discord.http import Route

async def update_role_connection(bot, user_access_token: str, metadata: dict):
    """Called with a user's OAuth token, not the bot token."""
    # metadata keys must match what's registered in the Developer Portal
    route = Route("PUT", "/users/@me/applications/{app_id}/role-connection",
                  app_id=bot.application_id)
    payload = {
        "platform_name": "Niko Café",
        "platform_username": metadata.get("username"),
        "metadata": {
            "economy_level": str(metadata.get("level", 0)),  # type: INTEGER_GREATER_THAN_OR_EQUAL
            "daily_streak":  str(metadata.get("streak", 0)),
        }
    }
    # Use user token, not bot token:
    headers = {"Authorization": f"Bearer {user_access_token}"}
    async with bot.http._HTTPClient__session.put(
        f"https://discord.com/api/v10/users/@me/applications/{bot.application_id}/role-connection",
        json=payload, headers=headers
    ) as resp:
        return await resp.json()
```

**Use cases for Niko:**
- "Barista" role unlocked when economy level ≥ 10
- "Regular" role unlocked when daily streak ≥ 7
- "VIP" role unlocked when net worth ≥ 10,000

---

## 11. GUILD_SYNC Gateway Opcode  (undocumented — op 12)
Not exposed via discord.py's public API. Allows requesting presence/member data for specific guilds without `members` intent workarounds.

```python
import discord.gateway as gateway

async def guild_sync(ws, guild_ids: list[int]):
    """Send the undocumented GUILD_SYNC op (12) to force member presence refresh."""
    await ws.send_as_json({
        "op": gateway.DiscordWebSocket.GUILD_SYNC,
        "d": [str(g) for g in guild_ids],
    })
```

**Caution:** Undocumented — behaviour may change without notice. Rate-limited by Discord.

---

## 12. Autocomplete on Slash Commands  (documented but barely used in this bot)
Only 3 commands in the bot use autocomplete. Massive UX improvement for any command with many options.

```python
@app_commands.command()
async def play(self, interaction: discord.Interaction, query: str):
    ...

@play.autocomplete("query")
async def play_autocomplete(self, interaction: discord.Interaction, current: str):
    # Return up to 25 choices
    results = await search_tracks(current)
    return [
        app_commands.Choice(name=r["title"][:100], value=r["url"])
        for r in results[:25]
    ]
```

**High-value targets for Niko:**
- `/economy shop buy` — autocomplete item names
- `/job apply` — autocomplete job list
- `/ai personality` — autocomplete personality names
- `/emoji` commands — autocomplete server emoji names

---

## 13. Context Menus  (documented but underused)
Right-click on a message or user → Niko action. Creates a whole category of features with zero command typing required.

```python
@app_commands.context_menu(name="☕ Ask Niko")
async def ask_niko_context(interaction: discord.Interaction, message: discord.Message):
    """Right-click a message → ask Niko to respond to it."""
    reply = generate_reply(interaction.user.id, interaction.guild, message.content, ...)
    await interaction.response.send_message(reply, ephemeral=True)

@app_commands.context_menu(name="📊 User Stats")
async def user_stats_context(interaction: discord.Interaction, user: discord.Member):
    """Right-click a user → show their economy/level card."""
    ...
```

---

## Priority Implementation Order (recommended)

| Priority | Feature | Impact | Effort |
|----------|---------|--------|--------|
| 🔴 High | Voice Channel Status (auto-set from music cog) | Visual, unique | Low |
| 🔴 High | Components v2 Section + Thumbnail (replace embed cards) | Aesthetic | Medium |
| 🔴 High | Native Discord Polls (replace button polls) | Clean UI | Low |
| 🟡 Med | Soundboard integration | Fun, unique | Medium |
| 🟡 Med | Burst reactions (giveaway/milestone moments) | Flair | Low |
| 🟡 Med | Autocomplete on shop/job/emoji commands | UX | Low |
| 🟡 Med | Context menus (Ask Niko, User Stats) | Discoverability | Low |
| 🟢 Low | Message Forwarding (starboard upgrade) | Utility | Low |
| 🟢 Low | Forum Thread Tags + Search | Power users | Medium |
| 🟢 Low | SKUs + Entitlements (premium tier) | Monetization | High |
| 🟢 Low | Role Connections / Linked Roles | Community | High |
| 🟢 Low | GUILD_SYNC opcode | Internal | Low |
