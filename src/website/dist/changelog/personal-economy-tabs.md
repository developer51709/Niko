# Economy & Achievements Move to Your Profile

- Date: 2026-10-14
- Tags: dashboard, economy, achievements, fixed

The dashboard's economy and achievements views now sit under My overview as personal tabs, because the Niko economy is one account-wide balance rather than something a server owns, and My servers finally separates the servers Niko is already in from the ones you can add it to.

## Highlights

### Tabs On Your Profile, Not a Server
My overview now has Overview at /dashboard, Economy at /dashboard/me/economy and Achievements at /dashboard/me/achievements, all reading your global account: wallet, vault, level, job, global rank, recent ledger activity and your top.gg vote streak.

### Nothing Server-Shaped Left
The economy has no per-server settings to manage, so the only control that remains is the leaderboard privacy toggle on the personal Overview tab, and the server sidebar keeps just the sections that really do belong to a server.

### My Servers Lists Your Servers
The My servers tab showed every server as “Ready to add” whenever the dashboard process had no live gateway cache of Niko's guilds; it now also trusts the guild list Niko records at startup.

## Changes

### improved
- Economy and Achievements are now personal tabs under My overview instead of server sections, since the economy is global per Discord account
- The Economy tab shows global rank, worth, streaks and recent ledger activity, and rewards no longer require selecting a server to read
- The Achievements tab keeps every badge, its progress bar, its unlock state and the coins it paid
- Server sidebars list only sections that configure that server, and economy reads through /api/me/economy and /api/me/achievements

### fixed
- My servers listed installed servers under “Add Niko to a server” because guild install state came only from the live gateway cache, which is empty on a standby instance or before the gateway's first sync; the dashboard now falls back to the guild list Niko writes at startup
