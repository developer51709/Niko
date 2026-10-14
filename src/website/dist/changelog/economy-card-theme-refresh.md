# Economy & Leveling Cards Match the Website Theme

- Date: 2026-10-14
- Tags: economy, leveling, theme, cards, dashboard

Every rendered economy and leveling image now uses the same graphite, steel and sage palette as the website and dashboard, retiring the warm café styling that outlived the site theme change.

## Highlights

### One Palette Everywhere
Balance, reward, leaderboard, shop, inventory, coinflip, blackjack and level cards are drawn from the website's own theme tokens, so a card finally looks like a panel of the dashboard.

### The Café Look Is Gone
The espresso gradients, gold borders, coffee-cup placeholder avatar and café banner are replaced by a near-black graphite canvas with a steel accent and sage for money earned.

### Discord Views Followed
Economy and shop containers now use the same brand accent as every other Niko view instead of their own café brown, so commands and cards match again.

## Changes

### improved
- Economy, gambling and leveling image cards use the website theme palette: graphite surfaces, a steel accent for numerals, sage for money earned and a muted red for losses
- Card banners read “NIKO ECONOMY” and “NIKO LEVELING”, and the placeholder avatar is a neutral profile mark
- Server-configured level card colours still take precedence over the defaults

### fixed
- The card palettes could drift from the site theme unnoticed; a test now pins every card colour to the stylesheet tokens
