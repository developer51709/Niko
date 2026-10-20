/**
 * Niko Discord API Proxy
 * ----------------------
 * A self-contained Cloudflare Worker that forwards signed Discord REST
 * requests from the bot. Each request leaves through Cloudflare's Worker
 * egress instead of the bot host's shared IP, so a challenged or rate-limited
 * shared host does not need the paid Webshare proxy for ordinary traffic.
 *
 * Endpoints:
 *   GET  /health           → public liveness plus request totals
 *   GET  /stats            → authenticated latency buckets, recent requests,
 *                            recent errors and status-code counts
 *   POST /internal/verify  → HMAC challenge used by the owner dashboard
 *   POST /internal/proxy   → signed Discord REST relay
 *
 * Required secret:
 *   AUTH_TOKEN  Same value as PROXY_WORKER_TOKEN on the bot.
 *
 * Optional vars:
 *   WORKER_NAME       Label shown in the owner dashboard (default "discord-proxy")
 *   PROXY_TIMEOUT_MS  Upstream timeout in milliseconds (default 15000, max 25000)
 *
 * Deploy:
 *   cd proxy-worker
 *   wrangler login
 *   wrangler secret put AUTH_TOKEN
 *   wrangler deploy
 *
 * The worker keeps telemetry in memory for this isolate only. It is a live
 * operational view, not a billing ledger; Discord traffic itself is never
 * stored.
 */

const SERVICE = "niko-discord-proxy";
const VERSION = "1.0.0";
const MAX_BODY_BYTES = 8 * 1024 * 1024;
const MAX_RESPONSE_BYTES = 12 * 1024 * 1024;
const CLOCK_SKEW_SECONDS = 60;
const BUCKET_MS = 5_000;
const WINDOW_MS = 15 * 60 * 1000;
const MAX_RECENT_REQUESTS = 60;
const MAX_RECENT_ERRORS = 30;
const MAX_NONCES = 4096;
const MAX_SAMPLES = 1_000;

const ALLOWED_METHODS = new Set(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]);
const HOP_BY_HOP_REQUEST_HEADERS = new Set([
  "connection",
  "content-length",
  "host",
  "proxy-authorization",
  "proxy-connection",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
]);
const SAFE_RESPONSE_HEADERS = new Set([
  "content-type",
  "date",
  "location",
  "retry-after",
  "server",
  "via",
  "cf-ray",
  "cf-mitigated",
  "x-ratelimit-bucket",
  "x-ratelimit-global",
  "x-ratelimit-limit",
  "x-ratelimit-remaining",
  "x-ratelimit-reset",
  "x-ratelimit-reset-after",
  "x-ratelimit-scope",
]);

const startedAt = Date.now();
const nonces = new Set();
const state = {
  requests: 0,
  success: 0,
  errors: 0,
  bytesIn: 0,
  bytesOut: 0,
  samples: [],
  statuses: Object.create(null),
  buckets: new Map(),
  recent: [],
  recentErrors: [],
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store, max-age=0",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function workerName(env) {
  return String(env.WORKER_NAME || "discord-proxy").slice(0, 60);
}

function safeEqual(left, right) {
  if (typeof left !== "string" || typeof right !== "string" || left.length !== right.length) {
    return false;
  }
  let difference = 0;
  for (let index = 0; index < left.length; index += 1) {
    difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return difference === 0;
}

function authorize(request, env) {
  if (!env.AUTH_TOKEN) {
    return json({ error: "Proxy worker is not configured. Set the AUTH_TOKEN secret." }, 503);
  }
  const header = request.headers.get("Authorization") || "";
  if (!safeEqual(header, `Bearer ${env.AUTH_TOKEN}`)) {
    return json({ error: "Unauthorized." }, 401);
  }
  return null;
}

async function hmacHex(secret, message) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(message));
  return [...new Uint8Array(signature)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

function bytesToBase64(bytes) {
  let binary = "";
  const chunk = 0x8000;
  for (let index = 0; index < bytes.length; index += chunk) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunk));
  }
  return btoa(binary);
}

function base64ToBytes(value) {
  return Uint8Array.from(atob(value), (character) => character.charCodeAt(0));
}

function round(value) {
  return Math.round(value * 10) / 10;
}

function p95(samples) {
  if (!samples.length) return 0;
  const sorted = [...samples].sort((left, right) => left - right);
  return sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * 0.95) - 1)];
}

/** Hide webhook and interaction tokens so the live feed can never leak one. */
function redactPath(path) {
  return String(path || "/")
    .replace(/(\/webhooks\/\d+\/)[^/]+/i, "$1…")
    .replace(/(\/interactions\/\d+\/)[^/]+/i, "$1…");
}

function allowedDiscordUrl(raw) {
  let target;
  try {
    target = new URL(raw);
  } catch {
    return null;
  }
  if (target.protocol !== "https:" || target.username || target.password || target.port) {
    return null;
  }
  const hostname = target.hostname.toLowerCase().replace(/\.$/, "");
  if (hostname !== "discord.com" && hostname !== "discordapp.com"
    && !hostname.endsWith(".discord.com") && !hostname.endsWith(".discordapp.com")) {
    return null;
  }
  if (!target.pathname.startsWith("/api/") || target.hash) {
    return null;
  }
  return target;
}

function prune(now) {
  const cutoff = now - WINDOW_MS;
  for (const [key, bucket] of state.buckets) {
    if (bucket.t < cutoff) state.buckets.delete(key);
  }
  while (state.samples.length > MAX_SAMPLES) state.samples.shift();
}

function record({ at, method, path, status, latency, ok, error, bytesIn = 0, bytesOut = 0 }) {
  prune(at);
  state.requests += 1;
  if (ok) state.success += 1;
  else state.errors += 1;
  state.bytesIn += bytesIn;
  state.bytesOut += bytesOut;
  state.statuses[String(status)] = (state.statuses[String(status)] || 0) + 1;
  state.samples.push(latency);

  const bucketStart = Math.floor(at / BUCKET_MS) * BUCKET_MS;
  let bucket = state.buckets.get(bucketStart);
  if (!bucket) {
    bucket = { t: bucketStart, count: 0, total: 0, errors: 0, samples: [] };
    state.buckets.set(bucketStart, bucket);
  }
  bucket.count += 1;
  bucket.total += latency;
  if (!ok) bucket.errors += 1;
  bucket.samples.push(latency);
  if (bucket.samples.length > 200) bucket.samples.shift();

  state.recent.unshift({
    at,
    method,
    path: redactPath(path),
    status,
    latency_ms: latency,
    ok,
  });
  if (state.recent.length > MAX_RECENT_REQUESTS) state.recent.length = MAX_RECENT_REQUESTS;

  if (!ok) {
    state.recentErrors.unshift({
      at,
      method,
      path: redactPath(path),
      status,
      message: String(error || "Discord API request failed.").slice(0, 240),
    });
    if (state.recentErrors.length > MAX_RECENT_ERRORS) {
      state.recentErrors.length = MAX_RECENT_ERRORS;
    }
  }
}

function latencySeries() {
  return [...state.buckets.values()]
    .sort((left, right) => left.t - right.t)
    .map((bucket) => ({
      t: bucket.t,
      avg: bucket.count ? round(bucket.total / bucket.count) : 0,
      p95: Math.round(p95(bucket.samples)),
      count: bucket.count,
      errors: bucket.errors,
    }));
}

function totals() {
  const count = state.samples.length;
  return {
    requests: state.requests,
    success: state.success,
    errors: state.errors,
    bytes_in: state.bytesIn,
    bytes_out: state.bytesOut,
    avg_latency_ms: count ? round(state.samples.reduce((sum, value) => sum + value, 0) / count) : 0,
    p95_latency_ms: Math.round(p95(state.samples)),
  };
}

function telemetry(env, full) {
  const now = Date.now();
  prune(now);
  const payload = {
    ok: true,
    service: SERVICE,
    name: workerName(env),
    version: VERSION,
    ready: Boolean(env.AUTH_TOKEN),
    uptime_seconds: Math.max(0, Math.floor((now - startedAt) / 1000)),
    now,
    totals: totals(),
    statuses: { ...state.statuses },
  };
  if (!full) return payload;
  return {
    ...payload,
    latency: latencySeries(),
    recent: state.recent.slice(0, MAX_RECENT_REQUESTS),
    errors: state.recentErrors.slice(0, MAX_RECENT_ERRORS),
  };
}

async function handleVerify(request, env) {
  if (!env.AUTH_TOKEN) {
    return json({ error: "Proxy worker is not configured. Set the AUTH_TOKEN secret." }, 503);
  }
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Body must be valid JSON." }, 400);
  }
  const nonce = body && body.nonce;
  if (typeof nonce !== "string" || nonce.length < 32 || nonce.length > 128) {
    return json({ error: "A valid challenge nonce is required." }, 400);
  }
  const proof = await hmacHex(env.AUTH_TOKEN, `niko-proxy-worker-verification:${nonce}`);
  return json({ ok: true, service: SERVICE, name: workerName(env), proof });
}

async function handleProxy(request, env) {
  if (!env.AUTH_TOKEN) {
    return json({ error: "Proxy worker is not configured. Set the AUTH_TOKEN secret." }, 503);
  }
  let envelope;
  try {
    envelope = await request.json();
  } catch {
    return json({ error: "Body must be valid JSON." }, 400);
  }
  if (!envelope || typeof envelope !== "object") {
    return json({ error: "Invalid relay request." }, 400);
  }

  const method = typeof envelope.method === "string" ? envelope.method.toUpperCase() : "";
  const url = typeof envelope.url === "string" ? envelope.url : "";
  const headers = envelope.headers;
  const timestamp = envelope.timestamp;
  const nonce = envelope.nonce;
  const proof = envelope.proof;
  const encodedBody = typeof envelope.body === "string" ? envelope.body : "";
  if (!ALLOWED_METHODS.has(method)) return json({ error: "Unsupported method." }, 400);
  if (!headers || typeof headers !== "object" || Array.isArray(headers)) {
    return json({ error: "Invalid request headers." }, 400);
  }
  const headerEntries = Object.entries(headers);
  if (headerEntries.some(([name, value]) => typeof name !== "string" || typeof value !== "string")) {
    return json({ error: "Invalid request headers." }, 400);
  }
  if (typeof timestamp !== "string" || typeof nonce !== "string" || typeof proof !== "string") {
    return json({ error: "Invalid relay proof." }, 400);
  }
  if (!/^\d{1,20}$/.test(timestamp) || Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp)) > CLOCK_SKEW_SECONDS) {
    return json({ error: "Relay request has expired." }, 403);
  }
  if (nonce.length < 32 || nonce.length > 128 || nonces.has(nonce)) {
    return json({ error: "Relay request was already used." }, 403);
  }
  const target = allowedDiscordUrl(url);
  if (!target) {
    return json({ error: "Only HTTPS Discord API URLs are allowed." }, 400);
  }

  let requestBody;
  try {
    requestBody = encodedBody ? base64ToBytes(encodedBody) : new Uint8Array();
  } catch {
    return json({ error: "Invalid request body." }, 400);
  }
  if (requestBody.byteLength > MAX_BODY_BYTES) {
    return json({ error: "Request body is too large." }, 413);
  }

  const canonical = JSON.stringify([
    timestamp,
    nonce,
    method,
    url,
    headerEntries.sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0)),
    await sha256Hex(requestBody),
  ]);
  const expected = await hmacHex(env.AUTH_TOKEN, `niko-discord-proxy-relay:${canonical}`);
  if (!safeEqual(proof, expected)) {
    return json({ error: "Invalid relay proof." }, 403);
  }

  nonces.add(nonce);
  if (nonces.size > MAX_NONCES) {
    nonces.clear();
    nonces.add(nonce);
  }

  const upstreamHeaders = new Headers();
  for (const [name, value] of headerEntries) {
    if (!HOP_BY_HOP_REQUEST_HEADERS.has(name.toLowerCase())) {
      upstreamHeaders.set(name, value);
    }
  }

  const timeout = Math.min(25_000, Math.max(1_000, Number(env.PROXY_TIMEOUT_MS) || 15_000));
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  const started = Date.now();
  const path = target.pathname;
  let upstream;
  let responseBody;
  try {
    upstream = await fetch(target.toString(), {
      method,
      headers: upstreamHeaders,
      body: method === "GET" || method === "HEAD" ? undefined : requestBody,
      redirect: "manual",
      signal: controller.signal,
    });
    responseBody = new Uint8Array(await upstream.arrayBuffer());
  } catch (error) {
    clearTimeout(timer);
    const latency = Date.now() - started;
    record({
      at: Date.now(),
      method,
      path,
      status: 502,
      latency,
      ok: false,
      error: error && error.name === "AbortError" ? "Upstream timed out." : "Upstream connection failed.",
      bytesIn: requestBody.byteLength,
    });
    return json({ error: "Discord API request failed.", worker: workerName(env) }, 502);
  }
  clearTimeout(timer);

  const latency = Date.now() - started;
  if (responseBody.byteLength > MAX_RESPONSE_BYTES) {
    record({
      at: Date.now(),
      method,
      path,
      status: 502,
      latency,
      ok: false,
      error: "Discord response exceeded the relay size limit.",
      bytesIn: requestBody.byteLength,
    });
    return json({ error: "Discord response is too large to relay.", worker: workerName(env) }, 502);
  }

  const safeHeaders = {};
  for (const [name, value] of upstream.headers) {
    const lowered = name.toLowerCase();
    if (SAFE_RESPONSE_HEADERS.has(lowered) || lowered.startsWith("x-ratelimit-")) {
      safeHeaders[lowered] = value;
    }
  }
  // discord.py treats a 429 without a Via header as a Cloudflare ban and raises
  // instead of honouring Retry-After. Discord's JSON 429 is a real rate limit
  // even when Cloudflare's edge strips the upstream Via header, so restore the
  // marker for that case (HTML challenge pages stay unmarked).
  if (upstream.status === 429 && !safeHeaders.via && /application\/json/i.test(safeHeaders["content-type"] || "")) {
    safeHeaders.via = "1.1 cloudflare";
  }
  record({
    at: Date.now(),
    method,
    path,
    status: upstream.status,
    latency,
    ok: upstream.status < 500,
    error: upstream.status >= 500 ? `Discord answered HTTP ${upstream.status}.` : "",
    bytesIn: requestBody.byteLength,
    bytesOut: responseBody.byteLength,
  });

  return json({
    ok: true,
    worker: workerName(env),
    status: upstream.status,
    headers: safeHeaders,
    body: bytesToBase64(responseBody),
    latency_ms: latency,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }
    if (request.method === "GET" && url.pathname === "/health") {
      return json(telemetry(env, false));
    }
    if (request.method === "GET" && url.pathname === "/stats") {
      const denied = authorize(request, env);
      if (denied) return denied;
      return json(telemetry(env, true));
    }
    if (request.method === "POST" && url.pathname === "/internal/verify") {
      return handleVerify(request, env);
    }
    if (request.method === "POST" && url.pathname === "/internal/proxy") {
      return handleProxy(request, env);
    }
    return json({ error: "Not found. Use /health, /stats, or the signed relay endpoints." }, 404);
  },
};
