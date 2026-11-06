# Build with Niko: The Developer API

- Date: 2026-11-06
- Version: 2.28.0
- Tags: api, developers, website, dashboard, docs, added

Niko has a documented developer platform. `/api/v1` serves economy standings and profiles, server leveling data, Discord user profiles, warning cases, and the user and server blacklist behind per-key scopes, while signed webhooks deliver warning events instead of forcing a poll. The API has its own documentation site at `/developers` and a portal at `/dashboard/developer` where approved developers register applications, create one-time keys, read their request log, and manage webhooks.

## Highlights

### A Reference, Not a README
`/developers` is a complete documentation site: quickstart, authentication, versioning, applications, permissions, and one page per resource family — economy, leveling, users, warnings and the blacklist. Every endpoint names its scope, its parameters, its response shape and its error codes, and the webhook guide verifies the signature in both Python and JavaScript. The docs page carries a developer card that links straight into it.

### A Portal, Not a Support Queue
`/dashboard/developer` is a real workspace built from the same dashboard components as guild settings: an overview of the scopes the account holds, applications and webhooks in one place, a key manager, and the request log behind every call. Registration is a form in a dialog instead of a page, and the owner reviews each application — with the exact scopes it asked for — from an Application review tab.

### Secrets Shown Once
Keys start with `niko_dev_`. Niko stores a peppered SHA-256 hash plus a short display prefix and never the secret itself, so a key is shown exactly once, cannot be recovered, and is replaced by revoking it. Each key carries only the scopes it was created with and can be bound to an approved application. Creating the first key requires accepting the developer policies, which the portal opens before anything else.

### Webhooks with a Signature
An approved application points Niko at an HTTPS endpoint and chooses which events it wants. Each delivery carries `X-Niko-Signature: t=...,v1=...`, an HMAC-SHA256 digest over the timestamp and the raw body using the application's signing secret, so the receiver can prove the delivery came from Niko. The portal shows the signing secret, the last delivery time and status, and can send a test event on demand.

## Changes

### added
- Public developer documentation at `/developers`: introduction, quickstart, authentication, versioning, applications, permissions, the endpoint reference, webhooks, rate limits and appeals, maintenance, errors, developer policies and support
- A developer portal at `/dashboard/developer` with overview, applications and webhooks, API keys, and usage logs
- Application registration in a modal, with the required Discord Developer Portal screenshot and an example asset
- One-time API keys with per-key scopes, optional application binding, a display prefix and immediate revocation
- A webhook editor per application: HTTPS endpoint, per-event switches, signing secret, test delivery and last-delivery status
- Owner review in `Application review`, and `Access management` for granting, scoping and revoking developer access
- `/api/v1` endpoint families for economy, leveling, users, warnings and the blacklist
- A versioned developer policy, accepted in the portal before the first key is created
- A Developers card on the docs page, linking the site to the developer documentation

### improved
- The registration dialog opens above the dashboard on phone-sized viewports, and its header scrolls with the form instead of floating over it
- The developer overview fits a 320px phone: the quickstart `curl` example wraps instead of widening the page
- The staff workspace, mailbox and report pages keep the developer portal in the sidebar for accounts that also hold API access
- Every endpoint page names the scope it needs, and the errors guide documents codes and report codes alongside them

### fixed
- A registration form clipped by the dashboard layout — it now renders above the page instead of inside its column
- The developer portal disappearing from the sidebar on staff pages that did not report API access to the shell

## Chart data

```json
{
  "type": "metrics",
  "title": "The Platform at a Glance",
  "data": [
    {
      "label": "Doc pages",
      "value": "18",
      "detail": "quickstart through policies",
      "color": "#4a7fb5"
    },
    {
      "label": "Endpoints",
      "value": "13",
      "detail": "five resource families",
      "color": "#66866f"
    },
    {
      "label": "Scopes",
      "value": "9",
      "detail": "read, write and restricted",
      "color": "#d96545"
    }
  ]
}
```
