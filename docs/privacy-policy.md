### Privacy Policy

**Effective date:** <t:1793491200:F> (2026-11-01)
**Updated by:** <@1052690741874401360>

This is the repository copy of the policy published at https://niko.sryze.cc/privacy.
Keep both in sync, along with `/legal privacy` in `src/cogs/legal/cog.py`.

Niko is a free, volunteer-run Discord bot. It is not a company, a registered business, a partnership, or any other legal entity: it is maintained by individuals in their personal capacity, in their own time. "Official instances" means the bot invited from https://niko.sryze.cc and everything served from that domain, including the dashboard, public leaderboards, support server, and web forms.

**1. Which instances this policy covers**

This policy describes how the official public Niko instances handle data. It does not describe every copy of the software, because we do not run them.

- **Official public instances.** All user data for these instances — account and server settings, economy and leveling records, AI memory, moderation and safety records, payment references, staff mail, and the anonymous usage counters — is stored in a **private MongoDB database** that we control. That database is not publicly reachable, is not shared with other bots or services, and is readable only with credentials held by the maintainers who operate Niko.
- **Private, beta, and self-hosted instances.** Niko's source is public, so anyone can run their own copy. Those deployments may use the **deprecated SQLite storage method** instead of MongoDB, may store data in JSON files or a different database, and may keep it on hardware we have never seen.
- **Self-hosted instances are outside our control.** We do not operate, host, administer, or have access to them, and we cannot read, export, correct, or delete anything they hold. We therefore **cannot handle data-removal requests, access requests, safety reports, or support requests about self-hosted, private, or beta instances**. Whoever runs such an instance is a separate controller: they decide what is collected, how long it is kept, how it is secured, and who can see it, and they are responsible for answering your requests and for their own legal obligations. Send any request about one of those instances to its operator, not to us.
- **How to tell which one you are using.** If the bot's profile, help command, or website links to niko.sryze.cc, you are on an official instance. If it points somewhere else, or was started by someone you know, treat its operator as the responsible party.

**2. What we collect**

We keep the categories below. Nothing else is collected for advertising, profiling, or resale.

• **Discord identifiers** — your user ID links your economy balance, XP and level, reminders, birthday, highlights, AI memory, roleplay blocks, AFK state, and warnings to you. Server and channel IDs keep each server's settings apart from every other server's.
• **Message content** — read in real time to answer AI mentions, run automod and the scam filter, serve snipe and highlight commands, and award XP. Content is not stored as a chat log; it is stored only in the narrow cases listed in the retention schedule below (AI memory, the snipe cache, ticket transcripts, and reported scam images).
• **Names and avatars you already show in Discord** — where a feature has to display a person (public leaderboards, staff profiles, server ownership records, ticket transcripts, giveaways, suggestions, and polls), the username, display name, and avatar URL are stored next to the record.
• **Server data** — server name, icon URL, owner ID, member count, and the per-server configuration for every feature an admin has touched.
• **Content you submit** — ticket transcripts, staff and team applications, appeals, reports, suggestions, polls, giveaways, birthdays, reminders, music playlists, and liked songs.
• **Presence, voice state, and activity** — presence and voice state are read while a feature needs them (member lists, music, VoiceMaster) and are not stored. Daily message, join, and leave totals are stored as aggregate counters for the dashboard, without message text and without member IDs.
• **Scam-image filter (experimental)** — when a member reports a message through the right-click scam report, the reported images and message context are sent to Niko staff for review. On confirmation, a perceptual hash (a compact numeric fingerprint) and a copy of the image are stored so similar images can be detected and removed automatically. Nothing is stored for servers without the filter enabled.
• **Premium image moderation** — on a server with an active premium subscription, the URL of each image attachment posted there is sent to fal.ai's NSFW model so it can be scored. Niko stores the verdict (confidence score, file name, and moderation action), never the image itself. Nothing is sent for servers without premium.
• **Payments** — premium subscriptions and donations are processed by OxaPay. We store the order reference, the OxaPay payment reference, the Discord user and server the payment belongs to, the amount and currency, the chosen crypto asset, the deposit address shown at checkout, and the payment status and timestamps. Niko never receives or stores card numbers, bank details, wallet private keys, or seed phrases.
• **Staff mail** — mail sent to a Niko address on our own domain, and our replies, are stored so the team can read and answer them from one mailbox.
• **Global analytics (anonymous)** — described in section 7.

**3. AI features and Groq**

Niko's AI replies, image understanding, and voice-message transcription run through **Groq**, an AI inference provider, and Groq is the AI provider used by the official Niko instances. Groq is not an advertiser, a data broker, or a commercial partner of the project.

- **What is sent.** When a member asks Niko to answer, Niko sends Groq the message being answered, the member's Discord username, the server name and member count, up to three recent turns of that member's AI conversation in that server, a short memory note, up to three recent channel messages used as context, a short excerpt of the message being replied to, and — when the member attached them — up to three image URLs or a transcription of their voice message.
- **Default models.** Chat runs on `openai/gpt-oss-20b`, image understanding on `qwen/qwen3.8-27b`, and transcription on `whisper-large-v3-turbo`. These defaults are configurable per deployment through the `GROQ_*` environment variables, so a self-hosted copy may use different models.
- **What Groq does with it.** Groq processes the request and returns a reply. Its handling of that request is governed by its own privacy policy and terms, which you should read alongside this one: https://groq.com/privacy-policy/. We do not control Groq's infrastructure and cannot delete data Groq keeps under its own policy.
- **What we do with it.** We use the reply to answer in Discord and store only the short conversation memory described in section 4. We do not use your messages to train models, we do not sell them, and we do not share them with any other AI provider.
- **How to avoid it.** AI features are per-server and can be turned off by an admin in the dashboard. A member can erase their own conversation memory at any time with `/clearhistory`, and can simply not mention the bot. With AI disabled, no message content is sent to Groq.

**4. Data retention policy**

Retention is deliberate, not incidental. Every category has a stated lifetime and a stated trigger. Where a fixed period is possible we use one; where a record exists to protect other people, we keep it for as long as that protection may be needed and say so plainly rather than promising a number we would not honour. Deleting a record removes the row from the live database immediately; a copy that sits inside a rotating backup ages out as that backup is replaced.

| Category | What it contains | Retention | What ends it early |
| --- | --- | --- | --- |
| Economy, leveling, and profile data | Balances, XP, jobs, inventories, achievements, streaks, leaderboard privacy flag | Until you delete your account data | Account deletion request |
| Server configuration | Automod, logging, tickets, starboard, leveling, welcome, suggestions, notifier, and every other per-server setting | While the server uses Niko | Server deletion request |
| AI conversation memory | Last 3 exchanges per member per server, plus a short memory note of a few hundred characters | Continuously overwritten | `/clearhistory`, account deletion, server deletion |
| Snipe cache | Last deleted or edited message per channel | In memory only; cleared on every restart | Next deletion in that channel, restart |
| Dashboard activity counters | Daily message, join, and leave totals per server — no text, no member IDs | While the server uses Niko | Server deletion request |
| Global analytics | Daily command and language counters, server and member totals | Last 90 days plus lifetime totals | Automatic daily sweep |
| Logging revert snapshots | The message state behind a "revert" button on a log entry | 30 days | Automatic hourly prune |
| Verification challenges | Pending alt-account verification state | Minutes | Solved or expired, then swept |
| Temporary blacklists and timeouts | Active restriction with an expiry date | Until the expiry date | Automatic deletion at expiry |
| Permanent blacklists, warnings, mutes, moderation cases, giveaway bans, abuse strikes, ticket transcripts, logging records | The evidence behind moderation decisions | No automatic expiry, while needed to protect communities | Formal legal process only |
| Scam-image reports and confirmed fingerprints | The report, perceptual hash, and stored image copy | No automatic expiry while useful for detection | Formal legal process only |
| Premium image moderation verdicts | Score, file name, and action — never the image | As long as the subscription record exists | Server deletion request |
| Payment and billing records | Order and payment references, payer and server IDs, amount, asset, deposit address, status | Long enough for accounting, tax, fraud prevention, refunds, and chargeback windows | Expiry of those obligations, then deletion or anonymisation |
| Data removal requests | What was requested, what was removed or preserved, when, and the reviewer | Kept as a compliance audit record | Not deleted |
| Staff and team applications | Submitted answers, role, and review decision | While reviewed, then as a recruitment record | Account deletion request |
| Birthdays, AFK state, reminders, roleplay blocks, giveaway entries, poll votes, music playlists and likes | The feature's own rows | Until you remove them or the feature ends | Account deletion request |
| Server ownership records | Server ID, owner ID, name, icon, and whether Niko is present | Kept after Niko is removed so the owner can still request deletion | Holds no member content |
| Staff mail | Mail to a Niko address and our replies | While needed to answer, audit, and hand over between staff roles | When no longer needed |
| Aggregated and anonymised data | Totals that cannot be traced to a person or server | No limit — no longer personal data | Not applicable |

**What ends retention early.** A completed account deletion request removes the personal and configuration data listed on the data removal page; a completed server request does the same for a server you own. `/clearhistory` erases your AI memory immediately. Turning off a feature stops new collection at once. A restart clears the snipe cache. Expiry dates delete temporary restrictions without anyone asking.

**What survives a deletion request, and why.** Moderation and safety records survive on purpose. They are the evidence that protects other communities: bot-level blacklists, warnings, mutes, moderation cases, logs and ticket transcripts, giveaway bans, abuse strikes, and scam-image reports. A deletion request never lifts a restriction, restores access, or erases evidence of abuse, and using one to try is a violation of the Terms of Service. Data removal requests themselves are kept as the audit trail described above.

**Legal holds.** If a record is needed for an active investigation, an appeal, a payment dispute, a chargeback, or actual or threatened legal proceedings, its retention is extended until the matter is closed — including records that would otherwise have expired. Once the hold ends, the normal schedule applies again.

**Backups.** Where the database operator takes backups, they serve disaster recovery only, are access-restricted in the same way as the live database, and are rotated. Deleted data ages out of them as they rotate; we cannot surgically edit a backup, so a record may exist in one briefly after you delete it.

**Instances we do not run.** This schedule describes official public instances only. Private, beta, and self-hosted deployments — including those still using the deprecated SQLite storage — set their own retention, and we cannot shorten, extend, enforce, or answer questions about it. Ask the operator of that instance.

**5. How we use it, and our legal bases**

All data is used to run the features a server has enabled, to keep communities safe (automod, scam detection, moderation cases, blacklist enforcement, appeals), to answer support and staff mail, to keep payment and accounting records accurate, to fix bugs, and to decide which commands, fixes, and translations to work on next. We never sell, share, or transfer your data to third parties for advertising or profiling.

Where European data-protection law applies, we rely on: performance of a contract or your request (running enabled features, answering your mail); our legitimate interests (protecting communities from scams and abuse, preventing fraud, securing and improving the service); compliance with legal obligations (accounting, tax, valid legal process); and consent where a feature asks for it. You may object to processing based on legitimate interests at any time, and we will stop unless we have an overriding legal ground — which, for preserved safety records, is usually the protection of other users.

**6. Storage and security**

Data for official public instances is stored by the server hosting Niko in a private MongoDB database we operate. Some auxiliary stores (for example the music library's playlists) live in a separate database on the same private infrastructure. Older or self-hosted deployments may use SQLite or JSON files, which Niko no longer uses for the official instances. No external analytics service is used; the anonymous usage counters described below are kept by Niko itself.

Access is limited to the maintainers who run Niko, through credentials that are not published and are rotated when someone leaves the team. Staff members see only the parts of the dashboard their role allows. Traffic between Niko, Discord, the database, and the providers below is encrypted in transit. Payment card data never reaches us. No system is perfectly secure: if a breach affects your data, we will announce it in the support server and, where the law requires it, notify the people affected and the relevant authority.

**7. Global analytics (anonymous)**

Niko keeps bot-wide usage statistics so that updates can be aimed at what communities actually use. What is counted is a daily total per command name, how each command was invoked (slash command, prefix command, or right-click/context command), the Discord language each server is set to, how many distinct servers used Niko that day, and the daily total of servers and members Niko is in. These are anonymous aggregate counters only: no message content, no user ID, no server or channel ID, and no individual person's activity is recorded, and a counter can never be traced back to a server or a person. The counters are kept for the last 90 days plus all-time totals, are visible only to Niko's staff, and are used solely to decide which features, fixes, and language translations to build and release next. Global analytics data is anonymous and is never seen, published, shared, or sold to any third-party company or individual.

**8. Your rights**

Subject to the preserved records described above, and to the law where you live, you can ask to see what Niko holds about you and receive a copy; to correct anything wrong (most profile and settings fields you can change yourself); to delete your account data or a server you own through the data removal form; to restrict or object to a particular use, such as having your identity shown on the public leaderboard, which has its own privacy toggle in the dashboard; to withdraw consent for any feature that asked for it, by turning the feature off; and to complain to your local data-protection authority. Every request is answered through the support server or the contact routes below, and we may ask you to prove control of the Discord account or server concerned so that nobody can delete somebody else's data.

**9. Data removal requests**

You may request deletion of your account data or of a server you own through the data removal form: https://niko.sryze.cc/data-removal. You must sign in with Discord so ownership can be confirmed. A server request remains available after Niko is removed if you were the owner at the time. Every request is reviewed before deletion runs, so that a request cannot be used to erase a safety record or escape a restriction, and requests are retained as a compliance audit record.

If a law requires deletion or release of a preserved safety record, send a formal legal request by email to the bot owner at owner@niko.sryze.cc. It must include a court record or a signed legal document and the contact details of an official legal representative so authenticity can be verified. These matters are handled personally and confidentially. Submitting an ordinary request does not override this process.

**10. Third-party services**

We share the minimum a feature needs, and only with the provider that feature uses:

- **Groq** — AI replies, image understanding, and voice transcription (see section 3), under https://groq.com/privacy-policy/.
- **fal.ai** — premium image moderation, which sends image URLs for scoring, under https://fal.ai/privacy. Never used on servers without premium.
- **OxaPay** — premium and donation payments, under https://oxapay.com/privacy.
- **Discord** — everything Niko does happens on Discord and is subject to Discord's own privacy policy.
- **Hosting and infrastructure providers** — the servers and database where the official instances run.
- **Google Translate** — only when a translation feature is used, and only the text being translated.

Niko does not sell or rent personal data, does not use it for advertising, and does not share it with data brokers.

**11. Payments and billing support**

Payment records are kept after a subscription ends so that billing questions, duplicate charges, refunds, chargeback windows, and financial records can be handled accurately. You can request information about, or deletion of, the personal data attached to a payment by using the support server and quoting the server ID and order reference; records we are required to keep for accounting, tax, or fraud prevention may be retained for as long as the law requires, and are then deleted or anonymised.

**12. Children and international transfers**

Niko is not directed at children. Discord requires users to be at least 13 years old, or older where local law sets a higher minimum, and Niko follows that rule; if we learn that a child below the applicable age has used an official instance, we will remove their data on request from a parent or guardian and may restrict the account's access to Niko. Niko's maintainers and providers may process data in countries other than yours, including the United States; where a transfer needs a legal safeguard, we rely on the provider's contractual protections and on the necessity of the transfer to deliver a feature you or your server asked for.

**13. Changes**

Material changes — a new provider, a new category of data, or a shorter or longer retention period — will be announced in the support server and reflected on this page, and the effective date at the top moves. Continued use of Niko after a change constitutes acceptance.

-# Questions? Join the support server: https://niko.sryze.cc/discord · Formal legal requests: owner@niko.sryze.cc
