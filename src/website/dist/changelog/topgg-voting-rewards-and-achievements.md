# top.gg Voting Rewards & Café Achievements

- Date: 2026-10-14
- Tags: economy, voting, achievements, dashboard, streaks

Voting for Niko on top.gg now pays coins and builds a streak that boosts your daily and work earnings, with a new set of badges to collect. Both the café standings and every badge are visible in two new dashboard tabs.

## Highlights

### Rewarded Votes
Every counted top.gg vote credits coins and sends you a thank-you DM. Weekend votes pay double, and repeated webhook deliveries never pay out twice.

### Streaks That Pay Off
Vote every 12 hours to build a streak of up to ten steps, raising your vote payout to 2.0x and your daily and work earnings to 1.5x. Missing a day restarts the streak, and the vote card in Discord and the dashboard both show where you stand.

### Twenty-One Badges to Chase
The café now tracks twenty-one achievements across work, banking, streaks, spending and voting. Each one pays its reward automatically the moment it unlocks, and the new Achievements tab shows progress bars for every badge you are still working on.

## Changes

### added
- top.gg vote webhook that credits coins, tracks streaks and sends a thank-you DM
- Streak multipliers for vote payouts and for daily and work earnings, with weekend vote doubling
- Seven voting badges covering total votes and vote streaks, plus fourteen existing café badges shown with progress and rewards
- Economy tab in the dashboard with wallet, vault, level, global and server ranks, recent ledger activity and the vote card
- Achievements tab in the dashboard listing locked and unlocked badges with progress bars
- `/vote` command with the listing link, streak status and current multipliers

### improved
- Economy accounts persist their vote counters, so streaks survive restarts on both SQLite and MongoDB deployments
- Existing databases gain the vote counter columns automatically on startup
