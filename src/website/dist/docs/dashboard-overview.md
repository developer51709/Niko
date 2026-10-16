# Dashboard Overview

The Niko web dashboard provides a visual interface for configuring your server settings and for following your own Niko profile.

## Accessing the Dashboard

Visit `/dashboard` and authenticate with Discord. You land on **My overview**, your personal area; your servers are one tab away.

## Personal tabs

These belong to your Discord account, so they look the same in every server:

### Overview (`/dashboard`)
- Your profile snapshot: net worth, wallet, vault, level and job
- Daily streak, achievements unlocked, total earned and global economy rank
- A quick list of your servers
- The **leaderboard privacy** toggle, the only economy setting there is

### Economy (`/dashboard/me/economy`)
- Wallet, vault and net worth with your global rank
- Level, job, bank tier, daily streak, totals and shifts worked
- Recent ledger activity
- top.gg vote streak, multipliers and the listing link

### Achievements (`/dashboard/me/achievements`)
- Every badge with its progress bar, reward and unlock state
- Coins earned from badges and what is still on the table

Personal tabs read `/api/me/...` endpoints and never need a server to be selected.

## Server sections

Select a server from **My servers** to manage that server. These sections are permission gated and read `/api/guild/<id>/...` endpoints:

### Server Overview
- Server statistics
- Quick settings access
- Recent activity

### Leveling
- Level settings
- XP configuration
- Level role management

### Moderation
- Moderation settings
- AutoMod configuration
- Log channel setup

### AI
- AI personality settings
- AI enable/disable
- Response configuration

### Notifications
- Follow YouTube, Twitch, Twitter/X, TikTok, Bluesky and Reddit accounts per server
- Per-account announcement channel, ping role and custom message
- Send a test notification, pause or resume one account, or switch the whole server off
- Health badges show how many checks failed and when each account was last checked

Learn more in the [Social Media Notifier guide](/docs/social-notifier).

## Staff applications and customization

- **Staff applications:** Build role-specific application forms, share public openings with your members, and review or decide on submissions. Learn more in the [Staff Applications guide](/docs/dashboard-staff-applications).
- **Customization:** Preview and update Niko’s display name, bio, avatar, banner, font, and name colors for the selected server. See the [Server Profile Customization guide](/docs/dashboard-customization).

## Using the Dashboard

1. **Start with My overview** to see your own profile and economy numbers
2. **Open My servers** and pick a server when you want to change its settings
3. **Navigate sections** using the sidebar or tabs
4. **Configure settings** with visual controls, then save the sections that need saving

## Features

### Visual Configuration
- Toggle switches for enabling/disabling features
- Dropdowns for selecting options
- Input fields for custom values
- Channel selectors for setting channels

### Saving changes
Dashboard settings are validated before they are saved. Some sections, including profile customization, require you to select **Save changes** to apply your edits; follow the confirmation or error message shown after saving.

### Permission Gating
Some settings require administrator permissions to change. Your personal tabs never do — they only read your own account.

## Tips

1. **Economy is global**: wallet, vault, level and badges follow your account everywhere, so look for them under My overview
2. **Use both interfaces**: Dashboard and Discord commands both work
3. **Check permissions**: Make sure you have admin perms for server changes
4. **Test changes**: Verify settings work as expected
