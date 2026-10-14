# Voting Rewards & Streaks

Voting for Niko on top.gg is the easiest way to top up your café balance. Every counted vote pays coins straight into your wallet, and voting regularly raises the rewards you earn across the economy.

## How to vote

1. Run `/vote` to open the vote card, which shows your current streak, your multipliers and the listing link.
2. Vote on top.gg — you can vote once every 12 hours.
3. Niko sends you a thank-you DM as soon as the vote is credited.

Voting does not need a specific server: the café economy is global, so your balance, streak and badges follow you everywhere.

## What a vote pays

| Vote | Reward |
| --- | --- |
| First vote | 500 coins |
| Every counted vote | 500 coins, plus the streak bonus below |
| Weekend vote | doubled |

## Streak multipliers

Consecutive votes build a streak — vote inside 24 hours of your last vote and the streak continues, miss a day and it restarts at one. The streak scales two things at once, up to ten steps:

- **Vote payout** — +10% per streak step, up to a 2.0x reward.
- **Daily & work earnings** — +5% per streak step, up to a 1.5x bonus on `/daily` and `/work`.

The streak caps at ten steps, but **total votes** keep counting toward the voting badges.

## Voting badges

Voting unlocks badges that are paid automatically when they are earned:

- **First Upvote** — vote once.
- **Vote Regular** — vote 10 times.
- **Ballot Stuffer** — vote 50 times.
- **Civic Legend** — vote 200 times.
- **Week of Votes** — keep a 7-vote streak.
- **Month of Votes** — keep a 30-vote streak.
- **Unbroken Voter** — keep a 100-vote streak.

## Checking your progress

- **Discord:** run `/vote` for your streak and multipliers at any time.
- **Dashboard:** open the selected server's **Economy** tab for your café standing (wallet, vault, ranks, recent activity and the vote card), and the **Achievements** tab for every badge, its progress bar and the coins it paid.

## Self-hosting

Vote rewards arrive through top.gg's webhook at `/api/topgg/webhook`. Set the `TOPGG_WEBHOOK_TOKEN` environment variable to the same authorization token you configure on the listing's webhook page; the endpoint stays closed until that token is set, and repeated deliveries inside the 12-hour window never pay out twice.
