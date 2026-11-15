# Premium: Longer Terms, Lower Monthly Prices

- Date: 2026-11-15
- Tags: premium, billing, pricing, sale, added, improved

Niko Premium can now be bought for one, three, six or twelve months, and a longer term costs less per month. A configured sale window can take a percentage off a server's first term. Whatever the page shows, the amount is worked out on the server from the chosen term — the page can pick a length, never a price.

## Highlights

### Pay for the Term You Want
The subscription page now offers 1, 3, 6 and 12 months — $15, $39, $72 and $132, or $13, $12 and $11 a month as the term gets longer. Gifts are priced from the same ladder, so a twelve-month gift finally costs less than twelve monthly payments.

### A Sale, Not a Permanent Discount
A sale window configured on the server takes a percentage off a server's first term and shows the date it ends. Renewals stay at list price, so a campaign never quietly becomes the new normal.

### The Server Decides the Amount
Checkout quotes the term price itself and records what the term would have cost beside what was charged, so a discounted payment is never mistaken for a mispriced one in the owner billing tab.

## Changes

### added
- 1, 3, 6 and 12-month premium terms at $15 / $39 / $72 / $132, with the per-month saving shown
- Gifts priced from the same term ladder instead of a flat monthly multiple
- A time-windowed sale (`PREMIUM_SALE`) that takes a percentage off a first term only

### improved
- Payments keep the list price beside the charged amount, so billing history shows discounts
- Premium prices in the bot's own embeds come from the plan constant instead of a hardcoded fallback
- The per-user staff grant is now beta access (`.staff beta`), separate from the paid server subscription
