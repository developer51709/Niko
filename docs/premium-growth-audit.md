# Premium audit and upgrade strategy

_Status: the term ladder (§5.1), the sale window (§5.2), and the truth-pass items (F7, F8, F6) are implemented. The perk bundle (§3–§4) and the win-back offer (§5.3) are still proposals. Where this document cites `utils/premium_manager.py`, that class now lives in `utils/premium.py` as `BetaAccess`._

Scope: the guild subscription that lives in `src/utils/premium.py`, its checkout in
`src/webapp/routes/premium_routes.py`, the Discord surface in `src/cogs/premium/cog.py`,
and the two billing pages in `web/src/pages/`. Related but separate: one-off donations
(`src/utils/donations.py`, `web/src/pages/BillingPage.tsx?token=…`) and the older
user-level grant table behind `src/utils/premium_manager.py`.

---

## 1. What premium is today

| Item | Current value | Where it is defined |
|---|---|---|
| Plan | One tier, `premium_monthly` | `premium.PREMIUM_PLAN` |
| Price | $15.00 USD / server / month | `premium.PREMIUM_PRICE_CENTS` |
| Term | 30 days, manual renewal, no auto-charge | `premium.PREMIUM_MONTH_DAYS` |
| Renewal reminder | DM 3 days before expiry, once per term | `premium.PREMIUM_REMINDER_DAYS`, `reminder_due()` |
| Grace period | None — expiry is authoritative | `premium.PREMIUM_GRACE_DAYS = 0` |
| Perks | One: AI image moderation (fal.ai NSFW) | `premium.PERKS` |
| Payment | Crypto only via OxaPay white-label; card shown disabled | `payment_configured()`, `plan.methods` |
| Gift terms | 1 / 3 / 6 / 12 months, membership-based | `GIFT_MONTH_OPTIONS` |
| Gift pricing | Exact multiple of the monthly price (no multi-month saving) | `_create_checkout()` |
| Entitlement checks | AutoMod image filter toggle; AI error reports (user-level) | `cogs/automod/cog.py::_premium_active`, `cogs/system/error_handler.py` |
| Enforcement surface | `POST /api/guild/<id>/config/automod` returns **402** with `upgrade_url` | `webapp/routes/dashboard_routes.py` |
| Owner visibility | Billing tab: payments, subscriptions, revenue, expiry count | `/api/staff/billing` |

The strategy statement in the docs is explicit and worth protecting:
_premium is an addition, not a paywall_ (`web/src/content/docs/premium-overview.mdx`).
Every recommendation below is additive under that rule.

---

## 2. Audit findings

Ordered by how much they cost conversion or trust today.

**F1 — A single perk cannot carry $15.**
`PERKS` holds one entry, and it is the most expensive thing in the product to run
(one fal.ai call per image, up to two images per message). The billing page also appends
"renewal reminder" as a bullet, which is an operational courtesy, not a benefit. A
community owner comparing $15 against free is comparing one API feature against nothing.

**F2 — Multi-month terms exist for gifts but not for the subscription.**
`/api/premium/checkout` hardcodes `months=1`; only `/billing/gift` offers term choice.
The predictable, higher-intent buyer (the server's own owner) is the one who cannot
prepay. Prepaying also removes the two churn points per year the reminder DM creates.

**F3 — Multi-month purchases have no incentive.**
`_create_checkout()` charges `PREMIUM_PRICE_CENTS * months` exactly. A 12-month gift
costs 12 × $15 with zero saving, while carrying all the gifter's risk forward. There is
no `TERM_PRICES` table anywhere.

**F4 — There is no discount, coupon, or sale mechanism at all.**
No code path reads a percentage, a promo code, or a date window. Every price is
`price_cents * months`. Any seasonal sale therefore needs a small, deliberate change —
see §5.

**F5 — Lapsed servers are dropped silently.**
`expire_lapsed()` marks the row and the loop logs it; the only owner contact is the
pre-expiry reminder. No win-back exists, even though the loop already has the exact list
of guilds that just lapsed and the owner ID to reach them.

**F6 — Two unrelated things are called "premium".**
`utils/premium_manager.py` maintains a separate `premium_users` table (user-level grants)
used only to unlock AI-assisted error reports. It shares a name with the $15 product and
appears in staff tooling. This will confuse support, not customers, but it should be
renamed (`staff_plus`, `beta_access`) before more perks are attached to either concept.

**F7 — `auto_renew` is stored as `1` but nothing auto-renews.**
`subscription_view()` exposes `auto_renew` to the dashboard and bot embeds while the
product is deliberately manual. Either implement it or stop returning it.

**F8 — Price is hardcoded as a fallback in the Discord cog.**
`premium/cog.py` uses `int(row.get('price_cents') or 1500)` in two embeds instead of
`PREMIUM_PRICE_CENTS`. A price change would make the status card lie.

**F9 — The upgrade moment is under-built at the exact place intent peaks.**
The 402 at the NSFW toggle already returns `upgrade_url`, which is the right in-context
prompt. But that page opens with no preselected explanation of what the owner was doing,
no gift option, and no term choice. Same for `/premium status` → "Upgrade this server".

**F10 — No funnel data.**
`premium_payments` already stores `created_at` and `paid_at`, so checkout conversion is
derivable per day without new columns. It is not surfaced anywhere; the staff tab shows
totals only. Without that, price and perk changes cannot be judged.

**F11 — Reminder reach depends on one DM.**
If the owner has DMs closed the reminder is marked sent anyway (correctly — noted in the
code). The guild's other managers never hear about it. A single fallback post in the
server's configured log channel would recover most of that loss.

---

## 3. Perks that cost nothing to run

The constraint is _no new marginal cost_: no new paid API calls, no new storage tier,
no new hosted service. Each candidate below uses infrastructure that already exists in
this repo, so the only cost is engineering time. Effort is S (hours), M (a day or two),
L (a week+).

### A. Identity and cosmetics — highest perceived value per hour

| Perk | Why it is free | Where it lands | Effort |
|---|---|---|---|
| White-label ticket transcripts: server logo, accent colour, footer line, optional "Powered by Niko" removal | Reuses `utils/tickets/transcripts.py` and the existing `panel_color` config; rendering is local CPU | ticket panel settings + transcript renderer | M |
| Card themes for rank / economy / profile cards (accent colour + a few background presets) | `utils/image/*` already render with the server's colour; assets are local | `level_card.py`, `economy_card.py` | M |
| "Premium server" badge on `/serverinfo`, profile cards and transcript headers | Pure rendering; badge pipeline already exists (`cogs/info/_badges.py`, `member_badges`) | `_server.py`, transcript header | S |
| Server-wide accent colour for all Niko panels | `accent_colour=` is already a parameter everywhere (see `cogs/premium/cog.py::ACCENT`) | config + a helper that resolves it | S |
| Custom panel footer/branding line on tickets and logging embeds | Text from config | tickets + logging | S |

Why this group first: every one of these is visible to **every member** of the server,
not just the admins who buy it. That is free advertising inside the product, and it is
what makes a server _look_ upgraded — the strongest word-of-mouth lever available.

### B. Raise existing hard caps (never lower the free ones)

Free keeps today's cap; premium gets a bigger one. Nothing is taken away. Verified caps
that already exist:

| Feature | Free cap today | Premium suggestion |
|---|---|---|
| Tags | `MAX_TAGS_PER_GUILD = 500` (`cogs/utility/tags.py`) | 2,000 |
| Sticky messages | `MAX_STICKIES_PER_GUILD = 50` (`cogs/utility/sticky.py`) | 200 |
| Highlight keywords | `MAX_KEYWORDS = 25` (`cogs/utility/highlights.py`) | 100 |
| Social feed follows | `MAX_FOLLOWS_PER_GUILD` / `_PER_PLATFORM` (`cogs/notifier/cog.py`) | +50% (note: adds polling work, not money) |
| Blocked words | `MAX_BLOCKED_WORDS = 1000` (`cogs/moderation/utils.py`) | 4,000 |
| Music queue per play | `_MAX_TRACKS_PER_PLAY = 50` (`cogs/music/cog.py`) | 200 (bandwidth only) |

This is the cheapest perk category in the repo: one `cap()` helper that takes
`premium: bool`, applied at the six call sites above.

### C. Dashboard insight — data already stored, just not shown

| Perk | Why it is free | Effort |
|---|---|---|
| 90-day / 365-day activity trends instead of the current short window | `events/startup/database.py` already keeps daily aggregate counters | S–M |
| CSV / JSON export of moderation cases, members, and activity | Read-only query + serialisation | S |
| Weekly owner digest DM: joins/leaves, top commands, cases opened, ticket load | Reuses the counters and the existing DM helper in the premium cog | M |
| Moderation insight: repeat offenders and case clustering | Existing case tables, local computation | M |

The weekly digest is the single best **retention** perk on this list: it gives the owner a
reason to open the dashboard every week, which is exactly where upgrades happen.

### D. Automation and safety nets

| Perk | Why it is free | Effort |
|---|---|---|
| Scheduled announcements / recurring posts | A row + the existing task loop | M |
| Server settings backup, restore, and clone to another server | Config rows already exist as one document per guild | M |
| Bulk import of blocked words / tags from a file | Existing parse + insert path | S |
| Larger automod exemption lists | Same table, more rows | S |

### E. Recognition (no runtime cost, small labour cost)

| Perk | Note |
|---|---|
| Premium role and coloured name in the support server | Pure Discord role; **staff time** is the real cost |
| Priority queue in support tickets | Labour, not money — cap it ("same-day first reply") so it stays honest |
| Listing in a "Premium servers" showcase | Marketing asset, zero runtime cost |
| Early access to new features | Only pick features without per-use cost; see §8 |

---

## 4. The package to launch

One perk at $15 invites the question "is AI moderation worth $15 to me?". Seven that all
work on the free tier's own infrastructure invite "which of these do I want first?".

1. White-label transcripts (A)
2. Card themes + premium badge (A)
3. Limit boosts: tags, stickies, highlights, blocked words (B)
4. Weekly owner digest (C)
5. 90-day analytics + CSV export (C)
6. Settings backup / clone (D)
7. Early access (E)

None of these adds a paid call. The only genuinely expensive perk stays what premium
already sells: AI image moderation. That reframes the price from "one API feature" to
"the professional tier of a bot you already use", without touching the free tier.

Copy rule for every perk above: describe it as **included with premium**, never as
"locked" or "unavailable on the free plan". The docs already use that voice.

---

## 5. Pricing, terms, and seasonal discounts

All of this is free to run — it is arithmetic and a date, not a service.

### 5.1 Multi-month terms for the subscription

Today only gifts get terms (F2) and terms save nothing (F3). Suggested ladder
(illustrative — pick from your own numbers):

| Term | Price | Per month | Saving vs monthly |
|---|---|---|---|
| 1 month | $15.00 | $15.00 | — |
| 3 months | $39.00 | $13.00 | 13% |
| 6 months | $72.00 | $12.00 | 20% |
| 12 months | $132.00 | $11.00 | 27% |

Implementation, smallest possible diff:

1. `utils/premium.py`: add `TERM_PRICES_CENTS` and a pure `term_price_cents(months)` /
   `term_saving_cents(months)`. Pure functions keep the existing
   `tests/test_premium_subscriptions.py` style: no database needed.
2. `premium_routes.py::_create_checkout`: replace
   `amount_cents = billing.PREMIUM_PRICE_CENTS * int(months)` with
   `billing.term_price_cents(months)` and validate `months` against the new whitelist for
   **both** purchase and gift. The amount must stay server-derived — the existing test
   `test_checkout_ignores_a_client_supplied_price` already enforces that, and must keep
   passing.
3. `/api/premium/plans`: return `terms: [{months, price_cents, price_label,
   per_month_cents, saving_cents}]` so both billing pages render from one source.
4. `BillingPage.tsx`: add the term picker that `GiftPremiumPage.tsx` already has
   (`billing-presets` markup), and show the monthly equivalent under the total.
5. `GiftPremiumPage.tsx`: swap `perMonthCents * months` for the same `terms` payload, so
   gifts and subscriptions can never disagree.

### 5.2 A seasonal sale window

Two short windows a year is enough; more trains people to wait.

| Window | Example | Discount |
|---|---|---|
| Winter / new-year | 20 Dec – 3 Jan | 25% off a first term |
| Project anniversary or a milestone (e.g. servers served) | 7 days | 20% off a first term |

Constraints that keep it honest:

- **First term per guild only**, so renewals are never discounted into a permanent price cut.
- **Apply to the term price**, not the monthly price, so a 12-month sale does not undercut
  the 12-month ladder permanently.
- **One row of config**, not a code path per campaign.

Implementation: a `SALE` record with `percent`, `starts_at`, `ends_at`, `first_term_only`,
resolved by a pure `active_sale(now)` function (unit-testable like `reminder_due()`).
`/api/premium/plans` returns a `discount` block (or `null`); checkout recomputes it
server-side at the moment of payment, so a stale page cannot buy at an expired price.

Accounting: `record_payment()` should store both the **list** amount and the charged
amount. Add `list_cents` (and optionally `promo`) to `premium_payments` via the migration
block in `src/events/startup/database.py`; keep `amount_cents` as what was actually
charged, so `billing_totals()` stays true revenue. Keep `premium_subscriptions.price_cents`
as the **list** monthly price so `/premium status` and staff tooling keep meaning.

### 5.3 Win-back for lapsed servers (F5)

`expire_lapsed()` already returns exactly the guilds that just lapsed. One DM per guild,
sent once, with a signed link reusing the helper in `src/utils/donations.py`:

- 40% off one month, valid 14 days, only for a guild whose term ended 7–30 days ago.
- Never repeats for the same guild (one extra timestamp field, or reuse a `notes`-style
  column if you prefer no migration).
- Tone: "your AI filter is paused; here is a lower price if you want it back" — factual,
  no urgency framing.

### 5.4 Donation → premium conversion

Donors already pay you voluntarily. A donation of $15 or more could become one month of
premium for a server the donor chooses. Zero new money, and it converts your warmest
audience into trial users.

Cheapest version first: the owner billing tab already has a manual grant endpoint
(`/api/staff/billing/subscriptions/<guild_id>`, `action=grant`). Record the donation track
ID in the billing note and use the existing path — no code. Automate only if the volume
justifies it.

### 5.5 Payment friction

The largest conversion loss is probably not price: it is that the only working method is
crypto, for an audience of Discord community admins. That is a provider/integration
question (OxaPay card processing), not a perk, and it is the one item here that may cost
money to enable. Verify the fee structure before promising it; do not turn the disabled
"Card" button into a date until the provider is confirmed.

---

## 6. Upgrading without pressure

The zero-cost rules that keep this feeling like an offer rather than a toll:

1. **The free tier stays complete.** No feature is removed, degraded, rate-limited down, or
   made read-only to create an upsell. This is already the project's stated position; keep
   it true as perks are added.
2. **One prompt per moment of intent.** The 402 at the NSFW toggle, `/premium status`, and
   `/billing` are the right places. Do not add a fourth.
3. **No marketing DMs.** Only transactional DMs: expiry reminder, win-back to the owner,
   gift notice. Contacting members who do not own a server about premium is both annoying
   and a policy risk.
4. **Dismissible and remembered.** Any in-dashboard mention is closable and stays closed.
5. **Dates, not countdowns.** "Sale ends 3 January" is honest. A ticking clock on the plan
   page is manufactured scarcity; do not add one.
6. **Say what returns to list price.** After a sale, the page must state the normal price
   plainly — the current copy already does this well ("$15 / month — cancel by simply not
   renewing").
7. **A grace period instead of a hard stop.** `PREMIUM_GRACE_DAYS = 0` today. Three days
   costs a few fal.ai calls and prevents the "it broke the day it expired" story that makes
   communities distrust paid bot features. It is also the cheapest trust purchase available.
8. **Gift is the low-pressure path.** Gifting already exists, is membership-based, and lets
   a member support a server without owning it. Put a "gift this server premium" secondary
   link in the 402 dialog and add a "copy gift link" button on the gift page — the most
   natural spread vector the product has.

Two more low-effort, high-signal additions in the same spirit:

- **Cost transparency.** One line on the billing page: what the $15 covers (moderation API,
   hosting, domain). It converts because it justifies the number instead of pressuring.
- **Reminder fallback.** If the owner DM fails, post the reminder once in the guild's
  configured log channel so the other managers see it (F11).

---

## 7. What to measure

No new analytics service is needed; `premium_payments` is already a funnel.

| Metric | How |
|---|---|
| Checkout conversion | `paid_at IS NOT NULL` ÷ all rows, per day/week |
| Term mix | Group paid rows by `months` before and after terms launch |
| Reminder → renewal | Guilds reminded vs guilds renewed within 72h |
| Churn after expiry | Guilds marked expired that never return within 30 days |
| Gift vs purchase | `kind` split; gift is the community-led channel |
| Upgrade intent | Count 402 responses and `/billing` views (one counter each) |
| ARPU / MRR | `billing_totals()` already sums paid cents; divide by active terms |

Add the two counters (402 hit, billing view) only — everything else is a query over
existing tables. Without these, neither the perk bundle nor the sale can be evaluated
rather than argued about.

---

## 8. Sequencing

1. **Truth pass (S):** hide or implement `auto_renew` (F7), replace the `or 1500`
   fallbacks with `PREMIUM_PRICE_CENTS` (F8), rename the user-level grant concept (F6).
2. **Terms + sale config (S–M):** `TERM_PRICES_CENTS`, `active_sale()`, plans payload,
   term pickers on both pages, `list_cents` migration. Fully unit-testable.
3. **Win-back + reminder fallback (S):** both hang off the existing lifecycle loop.
4. **Perk bundle (M):** cosmetics first (A), then caps (B), then digest/analytics (C).
5. **Re-measure** before the first sale window; pick the discount from the term mix rather
   than from a hunch.

---

## 9. Deliberately excluded

Anything with a per-use bill attached, because "free to implement" must not become
"expensive to run":

- Extra AI chat quota, larger AI memory, more image generation (per-token / per-image cost).
- Free or extended NSFW filtering — that is the paid thing, and it is the one perk whose
  cost scales with success.
- Music bandwidth or 24/7 playback if the Lavalink node is metered.
- Email digests (unless an existing provider is already paid for), SMS, push.
- "Unlimited everything" — it makes the free tier look deliberately hobbled.

A **trial** is attractive but is not free: seven days of image filtering spends real fal.ai
credits. If it is tried, cap it (e.g. 200 images) and budget it explicitly rather than
folding it into this list.

---

## 10. Open questions

- Is OxaPay's card processing available, and at what fee? This is likely bigger than any
  perk in §3.
- Does the Lavalink deployment have metered egress? If yes, music limits move from "free"
  to "costs money" and should drop out of §3B.
- Should premium ever follow the payer rather than the server? Today it follows the server
  (and the Terms say so); changing that is a policy decision, not a perk.
- Is the win-back DM acceptable under the support server's own conduct rules, and should it
  be opt-out-able by the owner?
