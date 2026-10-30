### Privacy Policy

**Effective date:** 2026-10-30

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
• **Global analytics (anonymous)** — bot-wide usage counters, kept so that updates can target what servers actually use: a daily count per command name, how each command was invoked (slash command, prefix command, or right-click/context command), the Discord language each server is set to, the number of distinct servers that used Niko that day, and the daily total of servers and members. Only aggregate numbers are stored — no message content, no user ID, no server or channel ID, and nothing traceable to a server or a person. The counters are kept for the last 90 days plus all-time totals, are visible only to Niko staff, and are used solely to decide which features, fixes, and language translations to build and release next. Global analytics data is anonymous and is never seen, published, shared, or sold to any third-party company or individual.
• **Scam-image filter (experimental)** — when a member reports a message through the right-click scam report, the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so similar images can be detected and removed automatically. Nothing is stored for servers without the filter enabled.
• **Premium image moderation** — on a server with an active premium subscription, the URL of each image attachment posted in that server is sent to fal.ai's NSFW model so it can be scored. Niko stores the verdict (confidence score, file name, and moderation action), not the image itself. Nothing is sent for servers without premium.
• **Payments** — premium subscriptions and donations are processed by OxaPay. We store the order reference, the OxaPay payment reference, the Discord user and server the payment belongs to, the amount and currency, the chosen crypto asset, the deposit address shown at checkout, and the payment status and timestamps. Niko never receives or stores card numbers, bank details, wallet private keys, or seed phrases. Payment records are kept for accounting, fraud prevention, refund handling, and billing support, including after a subscription ends.

**2. How we use it**
All data is used exclusively to run Niko's features within Discord, and the anonymous global analytics are used only to prioritise the next updates. We never sell, share, or transfer your data to third parties.

**3. Storage & security**
Data is stored by the server hosting Niko in a database — SQLite or MongoDB, depending on how that deployment is configured. Some smaller stores are kept as JSON files alongside it. No external analytics service is used; the anonymous usage counters described above are kept by Niko itself.

**4. Data retention**
Economy, leveling, and configuration data persist until you or a server admin removes it. Daily server activity totals are retained as aggregates. AI conversation history is capped at your last 3 exchanges and is automatically overwritten. You may erase your own AI memory at any time with `/clearhistory`.

**5. Your rights & data removal**
You may request deletion of your account data or of a server you own through the data removal form: https://niko.sryze.cc/data-removal. You must sign in with Discord so ownership can be confirmed. A server request remains available after Niko is removed if you were the owner at the time. Every request is reviewed before deletion.

Moderation and safety records are preserved on purpose: bot-level blacklists, warnings, mutes, moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image reports. A deletion request never lifts a restriction, restores access, or erases evidence of abuse.

If a law requires deletion of a preserved safety record, send a formal legal request directly to the bot owner through https://sorenthedev.indevs.in. It must include a court record or a signed legal document and the contact details of an official legal representative so authenticity can be verified. These matters are handled personally and confidentially. Submitting an ordinary request does not override this process.

**6. Third-party services**
When the AI feature is enabled, your message and a short anonymised context are sent to the configured AI provider to generate a reply; that provider's own privacy policy also applies (for OpenAI: https://openai.com/policies/privacy-policy). Premium image moderation sends image URLs to fal.ai (https://fal.ai/privacy), and payments are processed by OxaPay (https://oxapay.com/privacy). Other features may contact their respective services (for example social platforms for the notifier, or Google Translate for translations); only the minimum data needed for the feature is shared. Niko does not sell or rent personal data and does not use it for advertising.

**7. Payments and billing support**
Payment records are retained after a subscription ends so that billing questions, duplicate charges, refunds, and financial records can be handled accurately. You can request information about, or deletion of, the personal data attached to a payment by using the support server and quoting the server ID and order reference; records we are required to keep for accounting or fraud prevention may be retained for as long as the law requires.

**8. Changes**
Material changes to this policy will be announced in the support server and reflected on this page. Continued use of Niko after a change constitutes acceptance.

-# Questions? Join the support server: https://niko.sryze.cc/discord
