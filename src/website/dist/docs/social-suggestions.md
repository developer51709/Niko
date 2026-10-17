# Suggestions

The suggestions system lets server members submit ideas and feedback that can be voted on by the community. Administrators can approve or deny suggestions with optional reasons.

## Setting Up Suggestions

### Set the Suggestion Channel

```
.suggest channel <channel>
```

```
.suggest channel #suggestions
```

> **Note:** You need **Manage Server** permission to configure suggestions.

## Submitting a Suggestion

```
.suggest submit <text>
```

```
.suggest submit Add a meme channel for #memes-only content
```

Suggestions are posted in the configured suggestion channel with:
- The suggestion text
- The submitter's name
- Upvote and downvote buttons
- A suggestion ID for admin reference

## Voting

Members vote on suggestions using the buttons below each suggestion:

- 👍 **Upvote** — Supports the suggestion
- 👎 **Downvote** — Opposes the suggestion

Votes can be toggled — click the same button again to remove your vote.

## Admin Actions

### Approve a Suggestion

```
.suggest approve <id> [reason]
```

### Deny a Suggestion

```
.suggest deny <id> [reason]
```

When approved or denied, the suggestion message updates to show:
- A status indicator (Approved ✅ or Denied ❌)
- The admin who made the decision
- The reason (if provided)

Voting buttons are removed once a suggestion receives a verdict.

## Viewing Configuration

```
.suggest config
```

Shows the current suggestion channel and settings.

## Requirements

- **Manage Server** permission to set the channel, approve, or deny suggestions
- **Send Messages** permission to submit suggestions
- The bot needs **Read Messages** and **Send Messages** permissions in the suggestion channel
