# Social Media Notifier

The notifier system automatically tracks social media accounts and posts a notification to a Discord channel whenever new content is published. It supports YouTube, Twitch, Twitter/X, TikTok, Bluesky, and Reddit.

## Supported Platforms

| Platform | What it tracks | Credentials | Update interval |
|----------|---------------|-------------|-----------------|
| **YouTube** | New videos (via RSS feed) | None | Every 5 minutes |
| **Twitch** | Streams going live and new broadcasts | App credentials | Every 5 minutes |
| **Twitter/X** | New tweets | None | Every 5 minutes |
| **TikTok** | New posts | None | Every 5 minutes |
| **Bluesky** | New posts | None | Every 5 minutes |
| **Reddit** | New posts in a subreddit | None | Every 5 minutes |

> **Twitch credentials:** set `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` from a [Twitch developer app](https://dev.twitch.tv/console/apps). The same application credentials power the Twitch profile cards on the team page, and Niko only reads public channel data — no user login is ever required.
> Credentials for a platform with a paid API are never needed: X profile and post lookups use public endpoints instead.

## Opening the Setup Panel

```
.notifier
```

This opens an interactive panel with buttons for each platform. Click a platform button to open a modal where you enter:

- **Account/Channel Name** — The username, handle, or channel ID
- **Notification Channel** — Where to post notifications (defaults to the current channel)

> **Note:** You need **Manage Server** permission to use the notifier.

## Quick Follow Command

For faster setup, use the shortcut command:

```
.follow <platform> <username> [#channel]
```

**Platforms:** `youtube`, `twitch`, `twitter`, `tiktok`, `bluesky`, `reddit`

**Examples:**
```
.follow youtube @MrBeast
.follow twitch shroud #live-feed
.follow twitter elonmusk #social-feed
.follow reddit programming
```

## Viewing Followed Accounts

```
.notifier list
```

Shows all tracked accounts with their platform, channel, and notification target.

## Unfollowing

```
.unfollow <platform> <username>
```

Stops tracking an account. You can also remove follows through the "View Follows" button in the setup panel.

## Testing a Follow

Before following an account, you can verify it works:

```
.notifier test <platform> <query>
```

This validates the account exists and shows the latest post.

## Notification Format

Notifications use Discord CV2 containers styled to match each platform's branding:

- **YouTube** — Red accent, video thumbnail, channel name
- **Twitch** — Purple accent, stream thumbnail, live or new-broadcast wording
- **Twitter/X** — Blue accent, tweet text preview
- **TikTok** — Pink accent, video link
- **Bluesky** — Light blue accent, post text
- **Reddit** — Orange accent, subreddit name and post title

Each notification includes a link to view the original post.

## How It Works

1. A background task runs every 5 minutes
2. For each followed account, it fetches the latest post
3. If the post ID differs from the last-seen ID, a notification is sent
4. The last-seen ID is updated to prevent duplicate notifications
5. On first follow, the current latest post is recorded without sending a notification
