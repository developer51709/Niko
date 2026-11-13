# Verified Applications and Shared Server Data

Many servers run more than one bot. A moderation bot may record warnings, a leveling bot may keep XP, and a security bot may ban a raid before either of the others notices. When those bots each keep their own private copy of the same facts, staff end up checking three places and acting on the oldest one.

Niko's developer program exists to close that gap without handing anyone a key to everything. A **verified application** is another bot whose developer has registered it with Niko, passed a manual review, and been granted specific, narrow permissions. Niko works with a small number of these integrations on purpose: every one of them is a partner we can talk to, audit, and switch off.

## Why a warning says "Added via"

When a verified application adds a warning through Niko's API, the case records which application wrote it. That is why `/warnings` shows a line like:

> Added via @TheirBot. Learn more

It is not decoration. A warning is evidence staff may act on days later, so they need to know whether a human moderator or a partner bot created it, and they need a way to ask us about it. Moderator-issued warnings never carry the line. Removing the partner bot from your server stops it from writing new cases immediately, because every write is checked against the servers the application's bot currently shares with Niko.

## What a verified application can access

Access is never all-or-nothing. The owner grants scopes to a developer account, a key can only carry a subset of those grants, and a key bound to an application is narrowed again to the scopes approved during review. The endpoint enforces the intersection on every request, so tightening any one of those three layers takes effect at once.

| Scope | What it allows | Restricted |
| --- | --- | --- |
| `economy:read` | Read global economy standings and a member's economy profile | No |
| `levels:read` | Read a server's leveling standings and one member's XP and level | No |
| `users:read` | Resolve a user ID to a username, display name, and avatar | No |
| `warns:read` | Read warning cases for servers the integration shares with Niko | No |
| `warns:write` | Create and remove warning cases for those servers | Reviewed |
| `levels:write` | Write XP and levels for one member | Reviewed |
| `blacklist:read` | Read blacklist entries and their recorded reasons | Restricted |
| `blacklist:write` | Add or remove blacklist entries | Restricted |
| `guilds:cross_server` | Reach servers the application's bot does not share with Niko | Restricted |

Restricted scopes are never self-service. They are hidden from the request form and selected by the owner during review, which is why the table marks them separately from ordinary reviewed scopes.

What is **not** available through any key: message content, ticket transcripts, AI conversation memory, and the dashboard. Transcripts are first-party only. An integration can read the warning cases a server already has and add cases to it — nothing else about how your members talk.

## How access is granted

1. A developer joins the support server and opens a ticket.
2. They register an application with their bot's user ID and a screenshot of the Discord Developer Portal's General Information page, with the account menu open, so we can confirm the bot is theirs.
3. The owner reviews the application to `approved` and chooses the final scopes.
4. The developer accepts the current developer policy and creates a key. Keys are shown once; Niko stores only a peppered hash and a short display prefix.

Approval is manual and can be withdrawn. An application can be denied, and a denied application may be resubmitted with changes.

## How that access is regulated

- **Per-server consent by presence.** Warn endpoints require the application's bot to share the requested server with Niko *and* Niko to be in it. A partner cannot reach a server its own bot was never added to.
- **Signed webhooks, not polling.** Partners can subscribe to `warn.created`, `warn.deleted`, and `warns.cleared` instead of scraping. Every delivery is signed with HMAC-SHA256 over the timestamp and raw body, so a forged event cannot be mistaken for ours.
- **Rate limits.** External API traffic is limited per source address before a key is even read, and the portal watches per-key volume, error ratios, address spread, and repeated blocks. Crossing a threshold suspends the developer account and revokes every key it owns.
- **Suspension and appeal.** A suspended developer can read their suspension state and appeal through the portal; data access stays off until the owner lifts it. Lifting a suspension does not restore revoked keys.
- **Retention follows the moderation policy.** A warning written by a partner is a moderation record, exactly like one written with `/warn`. It is kept while it is needed to protect communities and is not erased by a routine data-removal request, which is explained in the [privacy policy](https://niko.sryze.cc/privacy).
- **Kill switch.** Removing the partner bot from your server, revoking its access in the portal, or asking us in the support server all stop its access. The first takes effect without anyone on our side doing anything.

## If something looks wrong

A warning you do not recognise, a member who says they were never in your server, or a partner bot writing cases you did not ask for: open a ticket in the support server with the member ID and the case number from `/warnings`. We can trace which application wrote a case, when, and under which key.

Developers who want to build an integration can start at the [developer portal](https://niko.sryze.cc/developers), where the scope list, policy, and endpoint reference live. Server staff who just want to manage warnings should read the [Warning System guide](https://niko.sryze.cc/docs/moderation-warnings).
