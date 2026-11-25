# Verified Applications and Shared Server Data

Many servers run more than one bot. A moderation bot may record warnings, a leveling bot may keep XP, and a security bot may ban a raid before either of the others notices. When those bots each keep their own private copy of the same facts, staff end up checking three places and acting on the oldest one.

Niko's developer program exists to close that gap without handing anyone a key to everything. A **verified application** is another bot that Niko's owner has checked, approved, and given a short, fixed list of permissions. Only a handful of them exist, on purpose: each one is a bot whose developer we can talk to, audit, and switch off. If your server never adds one of those bots, none of them can reach your server's data.

## Why a warning says "Added via"

When a verified application adds a warning through Niko's API, the case records which application wrote it. That is why `/warnings` shows a line like:

> Added via @TheirBot. Learn more

It is not decoration. A warning is evidence staff may act on days later, so they need to know whether a human moderator or a partner bot created it, and they need a way to ask us about it. Moderator-issued warnings never carry the line. Removing the partner bot from your server stops it from writing new cases immediately, because every write is checked against the servers the application's bot currently shares with Niko.

## What a verified application can access

Access is never all-or-nothing. The owner grants scopes to a developer account, a key can only carry a subset of those grants, and a key attached to an application is narrowed again to the scopes approved for that application. Niko checks all three layers on every request, so removing any one of them closes the door immediately.

| Scope | What it allows | Restricted |
| --- | --- | --- |
| `economy:read` | Read global economy standings and a member's economy profile | No |
| `levels:read` | Read a server's leveling standings and one member's XP and level | No |
| `users:read` | Resolve a user ID to a username, display name, and avatar | No |
| `warns:read` | Read warning cases for servers the integration shares with Niko | No |
| `warns:write` | Create and remove warning cases for those servers | Reviewed |
| `levels:write` | Write XP and levels for one member | Reviewed |
| `blacklist:read` | Read blacklist entries and their recorded reasons | Owner only |
| `blacklist:write` | Add or remove blacklist entries | Owner only |
| `guilds:cross_server` | Reach servers the application's bot does not share with Niko | Owner only |

The two **Reviewed** scopes, `warns:write` and `levels:write`, are available to a verified application, but only once the application review approves them.

The three **Owner only** scopes — `blacklist:read`, `blacklist:write`, and `guilds:cross_server` — are heavily locked down. They are not something a developer can request: they are left out of the application form and out of the key picker entirely, and they exist only for Niko's own internal staff use. The owner grants one directly, by hand, to an account Niko controls. They are never part of a normal developer application and never appear on a standard key.

What is **not** available through any key: message content, ticket transcripts, AI conversation memory, and the dashboard. Transcripts are first-party only. An integration can read the warning cases a server already has and add cases to it — nothing else about how your members talk.

## How a developer gets access

Two separate decisions stand between a developer and a working key, and they are easy to confuse:

| Decision | Where it happens | What it unlocks |
| --- | --- | --- |
| Developer portal access | A support ticket, reviewed by the owner | Being able to use the developer portal at all |
| Application approval | A manual review inside the portal, with no ticket | That one bot's verified identity and permissions |

The first is about the person; the second is about the bot. Approving one never approves the other.

### Step 1 — Ask for developer portal access (support ticket)

The developer portal is gated. Signing in is not enough: an account needs a grant from the owner before it can register applications, accept the developer policy, or create keys. The only way to ask for that grant is a support ticket.

1. Join the [Niko support server](https://niko.sryze.cc/discord) and open a ticket that asks for developer portal access.
2. Include enough detail for a real decision: the Discord account that will own the integration, what it does and who it is for, the scopes it needs and why, how the service stores, protects, and deletes Niko data, and roughly how much it will call the API.
3. The owner reviews the request. If it is granted, that account can open the developer portal with the scopes that were approved. If it is refused, the portal keeps answering that developer access has not been granted.

This ticket is about portal access and nothing else. It does not approve a bot, and it does not create a key. Do not ask for keys in DMs, public channels, or unrelated support threads.

### Step 2 — Register the bot in the portal (no ticket)

Once the account has portal access, the developer registers the application from the portal's Applications page:

- the bot's display name and a short description;
- the bot's user ID (or application ID);
- the permissions it needs, chosen from the ones the account is allowed to request;
- a screenshot of Discord's **Developer Portal → General Information** page, with the account menu open so the username is visible, so we can confirm the bot belongs to them.

Each bot ID can only be registered once, and a denied application may be resubmitted with changes.

### Step 3 — Wait for the application review (a separate review, not a ticket)

The registered application is reviewed manually by the owner. The review checks the bot identity, the verification screenshot, the requested permissions, and whether the integration's purpose justifies them. The owner may approve fewer permissions than requested, approve with a note, or deny the application.

This review is completely separate from the ticket in step 1. It begins when the application is submitted in the portal, it needs no support ticket, and approving it never gives the application more than the developer account already holds.

### Step 4 — Accept the policy and create a key

Once the application is approved, the developer accepts the current developer policy in the portal and creates a key for that application. Keys are shown once; Niko stores only a peppered hash and a short display prefix. A key's effective permissions are the scopes assigned to the key, limited by the scopes approved for the application and by the scopes the developer account still holds.

Approval is manual and can be withdrawn. An application can be denied, and approved access can be narrowed or removed at any time.

## How that access is regulated

- **Per-server consent by presence.** Warn endpoints require the application's bot to share the requested server with Niko *and* Niko to be in it. A partner cannot reach a server its own bot was never added to.
- **Signed webhooks, not polling.** Partners can subscribe to `warn.created`, `warn.deleted`, and `warns.cleared` instead of scraping. Every delivery is signed with HMAC-SHA256 over the timestamp and raw body, so a forged event cannot be mistaken for ours.
- **Rate limits.** External API traffic is limited per source address before a key is even read, and the portal watches per-key volume, error ratios, address spread, and repeated blocks. Crossing a threshold suspends the developer account and revokes every key it owns.
- **Suspension and appeal.** A suspended developer can read their suspension state and appeal through the portal; data access stays off until the owner lifts it. Lifting a suspension does not restore revoked keys.
- **Retention follows the moderation policy.** A warning written by a partner is a moderation record, exactly like one written with `/warn`. It is kept while it is needed to protect communities and is not erased by a routine data-removal request, which is explained in the [privacy policy](https://niko.sryze.cc/privacy).
- **Kill switch.** Removing the partner bot from your server, revoking its access in the portal, or asking us in the support server all stop its access. The first takes effect without anyone on our side doing anything.

## If something looks wrong

A warning you do not recognise, a member who says they were never in your server, or a partner bot writing cases you did not ask for: open a ticket in the support server with the member ID and the case number from `/warnings`. We can trace which application wrote a case, when, and under which key.

Developers who want to build an integration should start by opening a ticket in the support server for portal access. The [developer portal](https://niko.sryze.cc/developers) explains the scopes, the policy, and the endpoint reference once you are in. Server staff who just want to manage warnings should read the [Warning System guide](https://niko.sryze.cc/docs/moderation-warnings).
