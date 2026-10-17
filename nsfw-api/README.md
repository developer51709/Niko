# NSFW Image Filter API (Cloudflare Worker)

This is the externally-hosted image classification API used by Niko's
AutoMod **NSFW Image Filter**. It runs on Cloudflare Workers and uses
Cloudflare **Workers AI** (vision model) to decide whether an image is
NSFW. The bot itself never talks to Workers AI directly — it only calls
this worker.

## API

### `GET /health`
Returns `{ "ok": true, "model": "..." }` — useful for connectivity checks.

### `POST /check`
```
Content-Type: application/json
Authorization: Bearer <AUTH_TOKEN>   (only required if the secret is set)

{ "image": "<base64-encoded image bytes>" }
```

Response:
```json
{ "nsfw": true, "score": 0.95, "model": "@cf/llava-hf/llava-1.5-7b-hf" }
```

Errors: `401` unauthorized, `400` bad body, `413` image too large (~10 MB),
`502` classification failed.

## Deploying

```bash
cd nsfw-api
npm install -g wrangler    # or: bun add -g wrangler
wrangler login
wrangler deploy
```

After deploying, note the URL wrangler prints, e.g.
`https://niko-nsfw-api.<your-subdomain>.workers.dev`.

### Optional: protect the endpoint

```bash
wrangler secret put AUTH_TOKEN
```

Pick a long random string. If set, every `/check` request must send
`Authorization: Bearer <AUTH_TOKEN>`.

## Connecting the bot

Set these environment variables on the bot host (Freebuff: Settings →
Environment, or `freebuff-deploy env set` for production):

| Variable          | Required | Description                                                        |
|-------------------|----------|--------------------------------------------------------------------|
| `NSFW_API_URL`    | yes      | Base URL of the deployed worker (e.g. `https://niko-nsfw-api.me.workers.dev`) |
| `NSFW_API_TOKEN`  | no       | Value of `AUTH_TOKEN`, if you set the secret on the worker         |

Per-guild, enable the filter via the AutoMod panel (`automod` command) →
**Image Filtering** tab → toggle **NSFW Filter**. The MrBeast Scam Image
filter toggle lives in the same tab.

## Behaviour on the bot side

- Only messages with image attachments (`image/png`, `image/jpeg`, `image/webp`,
  `image/gif`) under ~10 MB are checked; at most 2 images per message.
- Whitelisted users/roles are skipped (same whitelist as other automod).
- The filter **fails open**: if the API is unreachable, misconfigured, or
  errors out, the message is allowed and a warning is logged.
- On a positive verdict the message is deleted and logged to the mod-log
  ("NSFW Filter").
