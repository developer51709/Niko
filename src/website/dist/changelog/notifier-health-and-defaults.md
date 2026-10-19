# The Notifier Keeps Quiet Channels and Uses Your Default Channel

- Date: 2026-10-19
- Tags: notifier, dashboard, youtube, twitch, social, fixed, improved

Quiet channels are no longer mistaken for broken ones: a YouTube channel with no uploads, an offline Twitch channel with no VODs and an empty subreddit all stay healthy, and a successful check clears the failed-check count. Adding an account also no longer demands a channel when the server has a default channel saved — leave the picker on the default and the follow posts there, and the picker only becomes required again once that default is cleared.

## Highlights

### Quiet Is Not Broken
When a poll finds nothing to announce, Niko asks the platform whether the account still exists instead of counting a failure. Only a channel the platform reports as gone is paused, so an empty or offline channel is never paused for being quiet.

### Verification Is About Existing
Adding an account checks that it exists, not that it has already posted something. A brand-new YouTube channel, an offline Twitch channel and a subreddit with no posts are all valid follows.

### The Default Does the Work
The announcement channel picker starts on the saved default channel, so adding an account can be one choice shorter. Clearing the default marks the field required and refuses to add an account until a channel is chosen.

## Changes

### fixed
- YouTube and Twitch channels are no longer paused for having nothing new to announce
- A successful check resets the failed-check count, and resuming a paused follow starts its health record over
- Lost announcement channels and Discord permission errors no longer count against the followed account
- YouTube verification, and subreddit verification, accept accounts that have not posted anything yet
- The Twitch test and dashboard test message distinguishes a quiet account from an unreachable one

### improved
- The announcement channel is optional when adding an account if the server has a default channel saved
- Clearing the default channel makes the announcement channel required again, and saving a new default makes it optional
- The Add an account card explains which channel new follows will use before the account is checked
