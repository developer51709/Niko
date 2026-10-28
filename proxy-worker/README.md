# Discord API Proxy (Cloudflare Worker)

This is the optional egress proxy used by Niko's Discord REST traffic. The bot
sends a signed request to this worker with the target Discord URL, method,
headers and body. The worker performs the request from Cloudflare's Worker
egress (which is not the bot host's shared IP), then returns Discord's status,
safe response headers and body.

It is deployed and updated exactly like `nsfw-api/`. Cloudflare's Workers Builds
Git integration can deploy this folder without manual intervention; the same
`wrangler deploy` command works locally.

## API

### `GET /health`

Public liveness and request totals.

### `GET /stats`

Requires `Authorization: Bearer <AUTH_TOKEN>`. Returns in-memory telemetry for
this isolate:

- request, success, error, byte and status-code totals
- 15 minutes of 5-second latency buckets (`avg`, `p95`, `errors`)
- the latest requests with method, redacted path, status and latency
- the latest proxy/Discord errors

### `POST /internal/verify`

Body: `{ "nonce": "..." }`. Returns an HMAC proof so the owner dashboard can
register a worker without sending the shared token.

### `POST /internal/proxy`

The signed relay used by the bot. Only HTTPS `discord.com`/`discordapp.com`
API paths are accepted. Requests are HMAC-signed with a timestamp and nonce and
are rejected after 60 seconds or when a nonce is replayed.

## Deploy

```bash
cd proxy-worker
npm install -g wrangler    # or: bun add -g wrangler
wrangler login
wrangler secret put AUTH_TOKEN
wrangler deploy
```

After deploying, note the printed URL, for example
`https://niko-discord-proxy.<your-subdomain>.workers.dev`.

Deploy more than one worker for extra egress diversity. Each additional Worker
needs its own `name` in `wrangler.toml` (Cloudflare cannot create two Workers
with the same name) and its own copy of the same `AUTH_TOKEN` secret. Register
each URL in the owner dashboard; Niko rotates through the registered workers
and falls back to the next worker, then to its normal direct/Webshare route, if
one is unreachable.

## Connect the bot

Set these on the bot host (Freebuff: Settings → Environment, or
`freebuff-deploy env set` for production):

| Variable             | Required | Description |
|----------------------|----------|-------------|
| `PROXY_WORKER_TOKEN` | yes      | Same value as the worker's `AUTH_TOKEN` secret. |
| `MONGODB_URL`        | yes      | Proxy registrations and the routing switch persist in the shared MongoDB database. |

Then open **Staff workspace → Discord proxy** as the bot owner:

1. Enter a label and the worker's HTTPS origin.
2. Choose **Verify & add worker**.
3. Turn on **Route Discord traffic through workers** when you are ready.

The feature stays disabled until that switch is on, so existing deployments are
unaffected. Removing every worker or switching routing off returns to the
normal direct/Webshare path.

## Notes

- Workers relay Discord **REST** traffic, including dashboard and OAuth calls.
  The Discord gateway is a long-lived WebSocket and stays on the bot's normal
  connection because a Worker cannot proxy that socket.
- The worker never stores Discord request bodies or responses. Telemetry is
  kept in memory per isolate and is only a live operational view.
- Webhook and interaction tokens in request paths are redacted before they
  appear in the feed.
- Requests with multipart attachments are left on the bot's normal route; JSON
  and form-encoded Discord API calls use the proxy.
- Cloudflare Worker egress addresses are managed by Cloudflare and vary between
  requests and isolates; the exact IP is not exposed.
