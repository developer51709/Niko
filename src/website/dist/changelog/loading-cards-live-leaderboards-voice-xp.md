# Faster Cards, Live Server Leaderboards & Voice XP

- Date: 2026-10-26
- Tags: economy, leveling, spotify, website, dashboard, added

Image cards no longer leave you staring at a spinner: economy, leveling, and Spotify commands open with an animated card-shaped placeholder and edit it into the finished render. The leveling leaderboard moved to a live page at /levels/<server id>, servers can exclude channels from XP and opt into passive voice XP, and the support server got clearer panels and a rules page that prints all twenty rules in one message.

## Highlights

### The Wait Now Looks Like the Card
Balance, daily, work, shop, inventory, rank, and Spotify all show a looping GIF placeholder in the exact shape of the card being rendered, then swap it in place. The placeholder comes from the website, so it appears instantly and costs no upload.

### A Leaderboard That Actually Moves
Every server gets a public board at `/levels/<server id>` that re-reads the XP table while it is open. Rows animate when members climb past each other, pages are handled on the server, and a server Niko has left gets an honest unknown-server page.

### XP Only Where You Want It
Exclude text or voice channels from XP, whitelist them again later, and turn on passive voice XP from the leveling panel, the commands, or the dashboard. Ticket channels are always excluded, and AFK channels never award voice XP.

### Support Panels That Answer First
The rules panel prints all twenty rules in the message instead of behind four buttons, important links and 'not ours to fix' reports live in private cards, and onboarding and ticket panels explain exactly where to ask for help.

## Changes

### added
- Animated loading cards for balance, reward, shop, inventory, and rank renders, plus the Spotify now-playing card
- A public per-server leveling leaderboard at `/levels/<server id>` with live polling, rank-movement animation, pagination, and an unknown-server state
- `GET /api/levels/<guild id>` — a paginated, public leveling endpoint that only serves guilds Niko is still in
- `/leveling config exclude` and `/leveling config include` for text and voice channels
- `/leveling config voicexp` for opt-in passive voice XP, with AFK channels skipped automatically
- A Channels & Voice section in the leveling panel and a matching Channels & voice card set in the dashboard
- A dedicated Spotify now-playing image card with album art, track details, and a live progress bar
- Loading card generators under `scripts/` and the generated GIFs in the public website assets
- Regression tests for the Spotify card, the guild leaderboard API, and the loading-card assets

### improved
- Economy, leveling, and Spotify commands render into the same message as the placeholder, so a slow avatar or cover fetch no longer leaves a bare thinking state or a duplicate card
- Level-up messages, level roles, cooldowns, and multipliers now share one XP-award path for messages and voice ticks
- `/leveling leaderboard` links to the live web board instead of rendering paginated images, and the old leaderboard renderer is gone
- Help categories are consolidated into Community and Moderation so merged cogs stop producing a long, sparse category list
- Support server onboarding and ticket panels explain where to ask, what to include, and which problems belong to Discord
- The support rules panel shows every rule at once and keeps links and out-of-scope reports in ephemeral cards
- Blackjack suit glyphs are drawn from smooth vector outlines and cached per size and colour
- The support report channel is renamed to #scam-reports while keeping its stored channel ID and history
- Forum guidelines are pinned before archiving so the post actually appears in the pinned list
- Excluded channels and the voice XP toggle are persisted in SQLite and MongoDB and exposed through the leveling config API

### fixed
- Rounded economy and Spotify cards keep their transparent corners instead of filling them with a dark rectangle
- An archived community-help guidelines post is fetched and deleted on refresh instead of leaving stale posts behind
- `.starboard` opens the main help command again instead of its own sparse command list
- Empty section accessories use a non-empty text display, which Discord accepts
- The legacy SVG card routes, helpers, and renderer are removed with their no-longer-used imports
