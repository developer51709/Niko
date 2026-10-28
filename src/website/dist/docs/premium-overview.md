# Niko Premium

Niko Premium is an optional **$15 USD per month** subscription for a single server. It exists to pay for the moderation API, bot hosting, and the new domain — nothing that was free is moving behind it.

## What premium adds

**AI image moderation.** Every image attachment posted in the server is scored by fal.ai's imageutils/nsfw model. Images at or above the confidence threshold are deleted, the author is notified, and a moderation log entry records the member, the file, and the score.

**Tuning.** The filter has its own toggle in the Moderation tab and a configurable threshold (NSFW_THRESHOLD, 0.85 by default), so a community can decide how strict it wants to be.

The filter only runs while the server's subscription is active. A lapsed term pauses the calls; it never keeps spending API credits in the background.

## What stays free

Premium is an addition, not a paywall. Every other feature is free for every server, including:

- Economy, jobs, banking, shop, and gambling
- Leveling, rank cards, and role rewards
- Moderation, warnings, cases, logging, and lockdowns
- Tickets and Discord-styled transcripts
- Giveaways, polls, suggestions, starboard, tags, birthdays, and reminders
- The social notifier, music, VoiceMaster, and the AI companion
- **Bot profile customization** — name, avatar, banner, and profile cards
- The **scam image filter**

The only existing feature that moved into premium is the **NSFW image filter**, which did not work reliably before this update. It has been rebuilt on fal.ai's dedicated NSFW model and now actually detects and removes images.

## Subscribing

Open the billing page at /billing, or run:

```
/premium status
/premium upgrade
```

The checkout is one page with a glass card and a payment-method screen:

- **Crypto** — powered by OxaPay's white-label checkout. Niko shows the exact address, amount, network, QR code, and a countdown, then confirms automatically when the network settles the payment.
- **Card** — visible but disabled while it is being prepared. It will appear here first.

Premium is **monthly and manual**: there is no automatic charge on the card everyone forgot about. Three days before a term ends, the owner receives a DM with a renewal link. If nobody renews, premium pauses and the server's settings and history stay intact. Your own servers appear on the billing page; communities you only belong to belong on the gift page.

## Gifting premium

Gifting is its own checkout, not a checkbox on the subscription page. Any member of a server can send it premium:

```
/premium gift [server_id]
```

That opens **/billing/gift**, where you pick a server you are a member of and a length of **1, 3, 6, or 12 months**. The full price is quoted up front from the plan price, so the term is the only thing you choose.

Gifting needs server membership, not Manage Server, and the gifter pays. The server owner receives a DM naming the gifter and the date the new term ends. Gifts extend an active term instead of replacing it, so no paid days are lost.

## Donations

Niko is free to run for most servers, and donations cover the rest:

```
/donate [amount]
/donationstatus [track_id]
/donorinfo [member]
```

`/donate` opens **/billing** with a signed, short-lived link. The page offers $3, $5, $10, $25, and $50 presets as well as any amount from $1 to $10,000, and it shows how much has been raised so far. Paying in USDT, ETH, BTC, BNB, LTC, DOGE, TRX, or XMR works the same way as premium: you get an address, an exact amount, a QR code, and a 60-minute countdown.

Once the network confirms, you receive a DM receipt, the **Supporter** role in the support server, and the track ID stays usable with `/donationstatus`. Confirmations are credited exactly once, even if the payment provider retries the webhook or the bot restarts while a payment is in flight — unpaid invoices are re-checked from the database every 45 seconds.

## The owner view

Bot owners get a **Billing** tab in the staff workspace. It lists recent payments, active subscriptions, revenue totals, and renewal dates, with notes for billing follow-ups and manual grant/cancel controls for the rare case something goes wrong.

## Payments and policies

Payments are processed by OxaPay; Niko never sees or stores card numbers or wallet private keys. Subscriptions are digital services billed per server, and crypto transactions are irreversible once broadcast. The Terms of Service (/terms) and Privacy Policy (/privacy) describe what is stored, how refunds are handled, and the limits of what a volunteer-run project can promise.
