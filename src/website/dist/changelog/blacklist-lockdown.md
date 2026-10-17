# Blacklisting a Server Now Pauses Its Features Instead of Erasing Them

- Date: 2026-10-16
- Tags: blacklist, moderation, dashboard, starboard, polls, giveaways, added

Blacklisting a server used to be one opaque database write. It is now a reported sequence of steps — save the entry, pause social notifications, disable the starboard, lock open polls and giveaways, notify the owner — each announced as it runs in the staff dashboard, followed by a summary of what was paused, skipped, or could not be switched off. Everything saved comes back untouched if the appeal is approved, and every disabled feature stays disabled across a bot restart.

## Highlights

### You Can See Every Step Happening
The blacklist button walks through the six steps one request at a time, showing 'Saving to database…', 'Pausing social notifs…', 'Disabling starboard…', 'Disabling polls…', 'Disabling giveaways…' and 'Sending blacklist notification…' as progress toasts, then a success message and a summary panel grouped into paused, not in use, and needs attention.

### Paused, Not Erased
The starboard channel, open polls, active giveaways and the notifier switch are saved and switched off instead of deleted, so an approved appeal puts the server back exactly as it was. Only the social notifier stays off by design, because a server turns its own announcements back on in the dashboard.

### Off Means Off, Restart or Not
Every disabled feature lives in the database rather than in memory: a blacklisted server keeps its locked polls, frozen giveaways and cleared starboard channel through a restart, and it stops receiving official staff broadcasts until the blacklist is lifted.

## Changes

### added
- A step-by-step guild lockdown in utils/guild_lockdown.py that reports each feature separately and never aborts the rest of the blacklist when one step fails
- Progress toasts, a success toast and a summary popup in the staff dashboard for both blacklist entry points, driven per step through /api/staff/guilds/<id>/blacklist/lockdown
- A guild_feature_locks record of what each step replaced, which is what unblacklisting or an approved appeal replays
- Locked polls and giveaways: votes and entries are refused with a localized 'paused' reply, and giveaway draws skip frozen rows
- A direct message to the server owner announcing the blacklist and where to appeal

### improved
- The starboard, polls, giveaways and notifier all check the blacklist from persisted state, so a blacklisted server cannot keep using a feature through a component button or an in-flight message
- Official staff broadcasts skip blacklisted servers and report how many were skipped
- The poll and giveaway cogs migrate the new locked column at startup, so databases created before this change need no manual step
