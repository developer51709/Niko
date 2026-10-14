### Privacy Policy

**Effective date:** 2026-10-01

This is the repository copy of the policy published at https://niko.sryze.cc/privacy.
Keep both in sync, along with `/legal privacy` in `src/cogs/legal/cog.py`.

**1. What we collect**
Niko stores only what is strictly necessary to provide its features:
• **User IDs** — to link economy balances, XP, reminders, birthdays, highlights, AI memory, and warnings to you.
• **Server IDs** — to keep per-server configuration (moderation, leveling, tickets, automod, etc.).
• **Message content** — read in real time for AI replies, automod, snipe, highlights, and leveling XP. It is not stored permanently, with three narrow exceptions: AI conversation history (last 3 exchanges, per user), the snipe cache (last deleted/edited message per channel, cleared on restart), and the experimental scam-image filter described below. The server dashboard also stores daily aggregate message, join, and leave counts; these aggregates contain no message text and no member IDs.
• **User presence & status** — read to support member-list and bot-status features; not stored.
• **Voice state** — used only during active music or VoiceMaster sessions; not stored.
• **Social notifier** — if a server follows social accounts, only the account name, platform, last-seen post ID, and target channel are stored.
• **Scam-image filter (experimental)** — when a member reports a message through the right-click scam report, the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so similar images can be detected and removed automatically. Nothing is stored for servers without the filter enabled.

**2. How we use it**
All data is used exclusively to run Niko's features within Discord. We never sell, share, or transfer your data to third parties.

**3. Storage & security**
Data is stored by the server hosting Niko in a database — SQLite or MongoDB, depending on how that deployment is configured. Some smaller stores are kept as JSON files alongside it. No external analytics service is used.

**4. Data retention**
Economy, leveling, and configuration data persist until you or a server admin removes it. Daily server activity totals are retained as aggregates. AI conversation history is capped at your last 3 exchanges and is automatically overwritten. You may erase your own AI memory at any time with `/clearhistory`.

**5. Your rights**
You may request deletion of all data associated with your User ID at any time by contacting the bot owner through the support server: https://niko.sryze.cc/discord

**6. Third-party services**
When the AI feature is enabled, your message and a short anonymised context are sent to the configured AI provider to generate a reply; that provider's own privacy policy also applies (for OpenAI: https://openai.com/policies/privacy-policy). Other features may contact their respective services (for example social platforms for the notifier, or Google Translate for translations); only the minimum data needed for the feature is shared.

**7. Changes**
Material changes to this policy will be announced in the support server and reflected on this page. Continued use of Niko after a change constitutes acceptance.

-# Questions? Join the support server: https://niko.sryze.cc/discord
