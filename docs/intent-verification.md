# Discord Intent Verification Guide — Niko Bot

This document contains every piece of information needed to complete Discord's
**Bot Verification** and **Privileged Intent** review forms.

---

## Bot Overview

| Field | Value |
|---|---|
| **Bot name** | Niko |
| **Purpose** | Multi-feature Discord companion — AI chat, economy, leveling, moderation, music, and community tools |
| **Audience** | General Discord communities (any server that invites the bot) |
| **Support server** | https://discord.gg/3JFbm2wfNk |
| **Privacy Policy URL** | Use `/legal privacy` in-bot, or link to your hosted copy of `docs/privacy-policy.md` |
| **Terms of Service URL** | Use `/legal terms` in-bot, or link to your hosted copy of `docs/terms-of-service.md` |

---

## Privileged Intents Used

### 1. Message Content Intent (`message_content`)

**Why it is required:**

Niko reads message content for the following features, none of which can work
without access to the raw text of messages:

| Feature | How message content is used |
|---|---|
| **AI chat** | User messages that contain "niko", a @mention, or the bot prefix are forwarded to an LLM to generate a conversational reply |
| **AI prefix commands** (`!ai <text>`) | The text after the prefix is extracted from the message and sent to the LLM |
| **AutoMod** | Messages are scanned for spam patterns, banned words, excessive mentions, and external links according to per-server configuration |
| **Highlights** | Messages are scanned for keywords registered by users; matching messages trigger a DM notification |
| **Snipe** | The content of the most recently deleted or edited message in a channel is temporarily cached (cleared on restart) so users can retrieve it with `!snipe` |
| **Leveling (XP)** | The presence of any message in a guild channel increments the author's XP; the content itself is not stored |
| **AFK detection** | Messages are scanned for @mentions of AFK users to send a notification |
| **UwU lock** | Messages in UwU-locked channels are deleted and re-sent in uwu-fied form |
| **Tags** | Messages starting with a configured tag trigger are matched by prefix |
| **Prefix commands** | All text-based (prefix) commands require reading message content to parse the command and arguments |

**Is message content stored permanently?**

No, with two narrow exceptions:
- **AI conversation history**: the last 3 message exchanges per user are kept in
  `memory.json` to give the LLM short-term context. Users can erase this with
  `/clearhistory`.
- **Snipe cache**: one deleted/edited message per channel is held in memory and
  cleared every time the bot restarts.

---

### 2. Server Members Intent (`members`)

**Why it is required:**

| Feature | How member data is used |
|---|---|
| **Welcome / onboarding** | `on_member_join` fires the welcome message, agreement gate, and role menu |
| **Leveling role rewards** | When a user reaches a configured level, their Member object is fetched to assign the reward role |
| **Economy commands** | Balance lookups, leaderboards, and rob/give commands resolve Member objects |
| **Birthday announcements** | The daily birthday task iterates guild members to check who has a birthday today |
| **Giveaway requirements** | Join requirements (account age, server age, booster status) are checked against the Member object |
| **Anti-raid / raid detection** | `on_member_join` is used to track join velocity for raid protection; join timestamps are compared |
| **Moderation** | Kick, ban, timeout, and warning commands operate on Member objects |
| **Member count display** | `!serverinfo` and the now-playing card display guild member counts |
| **Highlights DM** | The highlights listener needs to resolve the member who set the keyword to send them a DM |

**Is member data stored permanently?**

Only User IDs are stored, as keys in JSON files, to associate per-user data
(economy balance, XP, reminders, warnings, etc.) with the correct person.
No usernames, display names, avatars, or join metadata are stored.

---

### 3. Presence Intent (`presences`)

**Why it is required:**

| Feature | How presence data is used |
|---|---|
| **`!userinfo`** | Displays a member's current online/offline/DND status |
| **Member list accuracy** | Some member-count calculations use presence data to distinguish online from offline members |

**Is presence data stored permanently?**

No. Presence data is read in real time and is never written to disk.

---

## Data Storage Summary

This table covers every file or database where user/server data is persisted.

| File / DB | What is stored | Who can delete it |
|---|---|---|
| `memory.json` | AI conversation history (last 3 turns), long-term memory notes, favorability scores — keyed by User ID | User via `/clearhistory`; bot owner manually |
| `data/economy_data/{user_id}.json` | Coin balance, bank balance, inventory, job, XP, level, transaction log | Bot owner manually |
| `data/levels.json` | Per-guild, per-user XP and level | Server admin via `!levelconfig resetuser`; bot owner manually |
| `data/warnings.json` | Per-guild warning records (User ID + reason + timestamp) | Server admin via `!clearwarnings`; bot owner manually |
| `data/reminders.json` | User ID + reminder text + trigger timestamp | User via `!reminder remove` |
| `data/highlights.json` | User ID + keyword list | User via `!highlight remove` / `!highlight clear` |
| `data/birthdays.json` | User ID + MM-DD birthday | User via `!birthday remove` |
| `data/polls.json` | Poll question, options, vote counts, voter IDs | Server admin; bot owner manually |
| `data/suggestions.json` | Suggestion text, author User ID, vote counts | Server admin |
| `data/starboard.json` | Original message ID → starboard message ID mapping | Bot owner manually |
| `data/tags.json` | Guild ID + tag name + content + author User ID | Tag author or server admin via `!tag delete` |
| `data/mod_config.json` | Per-guild moderation settings (no user data) | Server admin |
| `data/ticket_config.json` | Per-guild ticket settings (no user data) | Server admin |
| `data/database.db` | Giveaway entries: prize, end time, host User ID; participant User IDs | Bot owner manually |

---

## Third-Party Services

| Service | Data sent | Purpose | Their privacy policy |
|---|---|---|---|
| **OpenAI API** | User message text + short anonymised channel context (≤3 prior messages) | AI reply generation | https://openai.com/policies/privacy-policy |
| **Lavalink nodes** | Search queries and stream URLs | Music playback | Varies by node operator |
| **Last.fm API** | Artist/track names | Autoplay similar tracks | https://www.last.fm/legal/privacy |

---

## Privacy Policy & Terms of Service (in-bot)

Niko ships `/legal privacy` and `/legal terms` slash commands that display the
full Privacy Policy and Terms of Service directly in Discord (ephemeral, visible
only to the requesting user). These are trilingual (EN / DE / ES).

If Discord's verification form requires a **public URL**, host the text from
`src/cogs/legal/cog.py` (the `privacy_body` and `terms_body` strings for the
`"en"` locale) on any public page (GitHub Gist, a simple website, etc.) and
submit that URL.

---

## Sample Verification Form Answers

### "Describe why your bot needs the Message Content privileged intent."

> Niko uses message content for several core features: (1) **AI chat** —
> messages mentioning the bot's name, pinging it, or using its prefix are read
> to generate a conversational AI reply; (2) **AutoMod** — message text is
> scanned for spam patterns, bad words, and link filters configured per server;
> (3) **Highlights** — messages are scanned for user-registered keywords to
> send DM notifications; (4) **Snipe** — the last deleted/edited message per
> channel is briefly cached; (5) **Leveling** — the presence of a message
> awards XP (content is not stored); (6) **Prefix commands** — all text
> commands require reading the message to parse the command name and arguments.
> Without this intent, none of these features can function.

### "Describe why your bot needs the Server Members privileged intent."

> Niko needs the Server Members intent for: (1) **Welcome & onboarding** —
> `on_member_join` triggers welcome messages and the agreement gate;
> (2) **Leveling role rewards** — member objects are fetched to assign roles on
> level-up; (3) **Giveaway requirements** — join age and booster status are
> checked on the member object; (4) **Birthday announcements** — the daily task
> iterates members to find today's birthdays; (5) **Anti-raid** — join events
> are tracked to detect unusual join velocity; (6) **Moderation** — kick, ban,
> and timeout commands require resolving member objects.

### "Describe why your bot needs the Presence privileged intent."

> Niko reads presence data to display a member's current online/offline/DND
> status in the `!userinfo` command. Presence data is never stored and is only
> read at the moment the command is invoked.

---

## Checklist Before Submitting Verification

- [ ] Privacy Policy URL is publicly accessible
- [ ] Terms of Service URL is publicly accessible
- [ ] `/legal privacy` and `/legal terms` commands work in your test server
- [ ] Bot description on the Discord Developer Portal accurately describes all features
- [ ] Support server link is valid and the bot is present there
- [ ] All three privileged intents are enabled in the Developer Portal → Bot settings
- [ ] Bot does not use message content for any purpose not listed above
