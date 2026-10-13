# Global Economy Leaderboard & Privacy

- Date: 2026-10-13
- Tags: economy, leaderboard, privacy, dashboard

The café rich list is now a paginated global leaderboard, ranked by net worth, with a dashboard privacy control that lets members protect their identity without leaving the rankings.

## Highlights

### A Live, Paginated Rich List
Browse global economy standings a page at a time, with stable ranks and net-worth totals across the full leaderboard.

### Choose Your Visibility
Members can make their leaderboard profile private from the dashboard. Private profiles remain ranked, while their identity is shown only to the account owner, official Niko staff, and people who share a guild with them.

### Efficient Page Loading
Leaderboard pages are fetched with bounded database-side pagination, keeping requests focused on the requested slice of rankings.

## Changes

### added
- Public global economy leaderboard with net-worth rankings and previous/next pagination
- Dashboard economy privacy preference for hiding a member’s identity on the public leaderboard
- Privacy-aware identity visibility for account owners, official Niko staff, and mutual-guild members

### improved
- Leaderboard loading uses bounded database-side pagination and retains global rank numbers between pages
- The Discord leaderboard command links directly to the public café rich list and explains its privacy behavior
