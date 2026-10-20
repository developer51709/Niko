# Niko Premium Is Here — Real AI Image Moderation, Plus a Legal Update

- Date: 2026-10-20
- Tags: premium, moderation, billing, dashboard, legal, added

Some things are worth doing properly. Niko Premium is a $15/month server subscription that puts every image posted in your server in front of fal.ai's NSFW model and deletes the ones that should never have been posted. Everything else — the scam image filter, bot profile customization, economy, leveling, tickets, giveaways, and the rest — stays free, exactly as it is today. This same release ships a legal update: a stricter, owner-verified data-removal process, protected moderation records, and a formal route for court-ordered requests.

## Highlights

### A Filter You Can Actually Trust 🛡️
The old NSFW filter was a coin flip. The new one asks fal.ai's imageutils/nsfw model about every image attachment and removes anything above the confidence threshold, with a moderation log entry naming the member, the file, and the score. It runs the moment an image is posted, not minutes later.

### Nothing Else Changed 🙌
Premium is an addition, not a paywall. Economy, leveling, tickets, giveaways, reminders, the social notifier, bot profile customization, and the scam image filter are all still free for every server. The NSFW image filter is the one existing feature that moved — and it never worked reliably before.

### Checkout Without the Guesswork 💳
One monthly price per server, paid through OxaPay's white-label checkout. Crypto is live today; card support is coming next, and it stays visibly unavailable until it genuinely works.

### Gift a Month to a Server You Love 💝
Any member of a server can gift it a month of premium. The owner gets a DM that says who sent it and when the term ends — no invoice, no mystery charge, no guessing.

### No Surprise Expiries ⏳
Three days before a term ends, the owner gets a DM with a one-click renewal link. If nobody renews, premium simply pauses — nothing is auto-charged, and your server settings and history stay exactly where they were.

### A Legal Update With Teeth 🔐
The same release rebuilds data removal. Signed-in members can request deletion of their account data or a server they own, including after Niko is removed if they were the owner at the time. Moderation and safety records are preserved, and court-ordered requests go directly to the bot owner through the formal legal process described on the data-removal page.

## Changes

### added
- Niko Premium — $15 USD per server per month, renewing monthly
- `/premium status`, `/premium upgrade`, and `/premium gift` right inside Discord
- Real AI image moderation powered by fal.ai's `imageutils/nsfw` model, with a configurable confidence threshold
- A new `/billing` page for premium subscriptions and donations
- Crypto payments via OxaPay's white-label checkout
- Gift premium to any server you are a member of, with an automatic DM to its owner
- Renewal reminder DMs three days before a term ends, so owners can renew in time
- An owner-only Billing tab in the staff workspace for recent payments, active subscriptions, revenue totals, and billing follow-ups
- Refreshed Terms of Service and Privacy Policy covering premium payments, crypto checkout, gifts, refunds, and data removal
- A new `/data-removal` page where signed-in members can request account or server deletion, with owner verification and a written policy
- Owner-only review queue in the staff workspace for data removal requests, with an automatic scoped deletion that preserves moderation records
- A formal legal request process for court-ordered release of preserved safety records, handled confidentially by the bot owner

### improved
- `/donate` and older donation links now share the premium checkout flow
- The Moderation tab shows premium state up front and links straight to checkout when the image filter is locked
- Enabling the NSFW image filter without premium now explains the upgrade instead of silently doing nothing

### fixed
- The NSFW image filter actually detects and removes NSFW images now — the previous implementation was unreliable and missed most of them
- Repeated payment callbacks can no longer extend a subscription twice
- Renewing early adds the new month to the remaining term instead of shortening it
