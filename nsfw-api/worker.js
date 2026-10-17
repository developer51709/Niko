/**
 * Niko's AutoMod — NSFW Image Filter API
 * ---------------------------------------
 * A self-contained Cloudflare Worker that classifies images as NSFW using
 * Cloudflare Workers AI (vision model via the `AI` binding).
 *
 * Endpoints:
 *   GET  /health → { ok: true }
 *   POST /check  → body: { "image": "<base64-encoded image bytes>" }
 *                  returns: { "nsfw": bool, "score": number, "model": string }
 *
 * Environment / bindings (see wrangler.toml):
 *   AI          — Workers AI binding (automatic, no setup needed)
 *   AUTH_TOKEN  — optional secret; when set, requests must send
 *                 `Authorization: Bearer <AUTH_TOKEN>`
 *
 * Deploy:
 *   npm install -g wrangler   (or: bun add -g wrangler)
 *   wrangler login
 *   wrangler secret put AUTH_TOKEN        (optional but recommended)
 *   wrangler deploy
 */

const MODEL = "@cf/llava-hf/llava-1.5-7b-hf";

// Strict prompt — the vision model answers with a single line; we parse it.
const NSFW_PROMPT =
  "You are a strict content moderator. Look at this image and decide whether " +
  "it contains NSFW (not safe for work) content: nudity, sexual acts, " +
  "pornography, or explicit sexual content. Answer with exactly one word: " +
  "'YES' if it is NSFW, or 'NO' if it is safe. Do not explain.";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS_HEADERS },
  });
}

function authorize(request, env) {
  if (!env.AUTH_TOKEN) return true; // auth disabled when no token is set
  const header = request.headers.get("Authorization") || "";
  return header === `Bearer ${env.AUTH_TOKEN}`;
}

/** Ask the Workers AI vision model and derive a boolean + confidence. */
async function classifyImage(env, base64Image) {
  const result = await env.AI.run(MODEL, {
    image: [...new Uint8Array(atob(base64Image)).values()],
    prompt: NSFW_PROMPT,
    max_tokens: 8,
  });

  const text = String(result?.description ?? "").trim().toUpperCase();
  const nsfw = text.includes("YES");

  // Rough confidence: a plain YES/NO is decisive, anything hedged is ~0.5.
  const decisive = text.startsWith("YES") || text.startsWith("NO");
  const score = decisive ? (nsfw ? 0.95 : 0.05) : 0.5;

  return { nsfw, score, model: MODEL, raw: result?.description ?? "" };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    if (url.pathname === "/health" && request.method === "GET") {
      return json({ ok: true, model: MODEL });
    }

    if (url.pathname === "/check" && request.method === "POST") {
      if (!authorize(request, env)) {
        return json({ error: "Unauthorized" }, 401);
      }

      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "Body must be valid JSON." }, 400);
      }

      const image = body?.image;
      if (typeof image !== "string" || image.length === 0) {
        return json({ error: "Missing 'image' field (base64-encoded image)." }, 400);
      }

      // ~10 MB decoded cap keeps Workers AI payloads sane.
      if (image.length > 14_000_000) {
        return json({ error: "Image too large (max ~10 MB)." }, 413);
      }

      try {
        const verdict = await classifyImage(env, image);
        return json(verdict);
      } catch (err) {
        console.error("Workers AI error:", err);
        return json({ error: "Classification failed.", detail: String(err) }, 502);
      }
    }

    return json({ error: "Not found. Use POST /check or GET /health." }, 404);
  },
};
