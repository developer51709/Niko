# Blacklists and Appeals

A blacklist blocks a Discord server from using Niko. It is applied by the Niko staff team — never by a server owner — when a server breaks the rules Niko is operated under or abuses the bot. The blacklist is recorded with a reason, and the server's owner is sent a direct message announcing it with the reason and where to appeal.

## What a Blacklist Does

A blacklisted server keeps its place in the bot's database but loses every feature. Niko stops answering its commands, and the features that live in buttons rather than commands — poll votes, giveaway entries — are refused as well, with a short reply saying the feature is paused while the server is blacklisted.

Because a blacklist is decided with one click and an appeal can lift it just as quickly, nothing is deleted. What the server had is recorded, switched off, and replayed if the blacklist is ever lifted.

## What Gets Switched Off

Applying a blacklist walks through the server's features in turn, and the staff dashboard reports each one as it finishes:

- **The blacklist entry** — the record itself, with its reason.
- **Social notifications** — the server-wide announcement switch is turned off, so nothing is posted even if it was left on.
- **The starboard** — the saved starboard channel is cleared, so the starboard stops collecting and posting.
- **Polls** — every open poll is locked. Votes are refused and the existing tally is kept.
- **Giveaways** — every active giveaway is locked. No new entries are taken and no winner is drawn.
- **The owner notification** — the server owner is sent a direct message with the reason and the appeal page.

If one of those steps cannot be completed, the dashboard says which one and the server stays blacklisted: a feature that cannot be switched off is never a reason to leave a blacklisted server using Niko.

## What Is Kept and What Comes Back

The lockdown records what each feature looked like before it was switched off, so an approved appeal restores the server instead of leaving it to be rebuilt:

- the starboard channel, with its threshold, emoji and ignored channels,
- every open poll, unlocked with its votes intact,
- every active giveaway, unlocked so entries and the draw resume.

Social notifications are the one exception. The followed accounts, their channels, ping roles and custom messages are all kept, but lifting a blacklist does not turn announcements back on — a server admin flips the switch again in the dashboard's Notifications tab.

## Disabled Means Disabled After a Restart

Every part of the lockdown is stored in the database rather than in memory: the cleared starboard channel, the locked polls and giveaways, and the switched-off notifier. Restarting the bot therefore does not quietly give a blacklisted server its features back, and databases created before polls and giveaways could be locked are migrated when Niko starts.

## Official Announcements Stop

Official Niko announcements are a feature too. A blacklisted server stops receiving staff broadcasts, and the staff dashboard reports how many servers were skipped for that reason when an announcement is published.

## Submitting an Appeal

A blacklisted server's owner can appeal at [niko.sryze.cc/appeals/blacklist](https://niko.sryze.cc/appeals/blacklist). The page shows the blacklist reason and asks for a statement explaining the situation; either the server owner or the affected user submits it, and only one appeal is reviewed per blacklist — a denied appeal cannot be resubmitted.

A staff member reviews the appeal with a note that you can see. If the appeal is approved, the blacklist is lifted immediately and the server's saved starboard, polls and giveaways are unlocked in the same step. If it is denied, the blacklist stands and the features stay off.
