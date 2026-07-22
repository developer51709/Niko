# AI Provider Compatibility Guide

Niko uses the OpenAI-compatible chat-completions API
(`/v1/chat/completions`). Any provider that implements this standard can be
plugged in by setting two environment variables:

```
OPENAI_API_KEY=<your key>
AI_INTEGRATIONS_OPENAI_BASE_URL=<provider base URL>   # omit for native OpenAI
```

If only `OPENAI_API_KEY` is set (no base URL), the official OpenAI endpoint is
used. The Replit built-in integration sets both automatically.

---

## Paid Providers

| Provider | Model used | Input (per 1M tokens) | Output (per 1M tokens) | Notes |
|---|---|---|---|---|
| **OpenAI** | `gpt-4o-mini` | $0.15 | $0.60 | Default; best reliability |
| **OpenAI** | `gpt-4o` | $2.50 | $10.00 | Higher quality, higher cost |
| **Anthropic** | `claude-3-5-haiku` | $0.80 | $4.00 | Via compatible wrapper only |
| **Google** | `gemini-1.5-flash` | $0.075 | $0.30 | Via compatible wrapper |
| **Mistral** | `mistral-small` | $0.20 | $0.60 | Direct OpenAI-compat endpoint |
| **Cohere** | `command-r` | $0.15 | $0.60 | Via compatible wrapper |

---

## Free Providers (Ranked)

These providers offer free tiers with OpenAI-compatible endpoints. Set
`OPENAI_API_KEY` to their key and `AI_INTEGRATIONS_OPENAI_BASE_URL` to their
base URL.

### Rank 1 — **OpenRouter** (Recommended)
- **Base URL:** `https://openrouter.ai/api/v1`
- **Free models:** `meta-llama/llama-3.1-8b-instruct:free`,
  `mistralai/mistral-7b-instruct:free`, `google/gemma-2-9b-it:free` and
  dozens more
- **Rate limit:** ~20 req/min (free tier)
- **Why #1:** Largest selection of free models, reliable uptime, easy
  model-switching, no credit card required to start
- **Recommended model:** `meta-llama/llama-3.1-8b-instruct:free`

### Rank 2 — **Groq**
- **Base URL:** `https://api.groq.com/openai/v1`
- **Free models:** `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`,
  `mixtral-8x7b-32768`, `gemma2-9b-it`
- **Rate limit:** 30 req/min, 14,400 req/day (free)
- **Why #2:** Extremely fast inference (LPU hardware), generous daily quota,
  good model quality
- **Recommended model:** `llama-3.1-8b-instant`

### Rank 3 — **Together AI**
- **Base URL:** `https://api.together.xyz/v1`
- **Free models:** Several Llama 3 and Mistral variants (free tier with $1
  starting credit, then pay-as-you-go)
- **Rate limit:** Varies by model
- **Why #3:** Good model variety and quality, $1 free credit goes a long way
  at Niko's token usage level
- **Recommended model:** `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`

### Rank 4 — **Mistral AI (free tier)**
- **Base URL:** `https://api.mistral.ai/v1`
- **Free models:** `mistral-small-latest` (limited free quota)
- **Rate limit:** 1 req/s, 500K tokens/month (free)
- **Why #4:** Native first-party endpoint, predictable behaviour, but the
  free quota is tighter than Groq or OpenRouter
- **Recommended model:** `mistral-small-latest`

### Rank 5 — **Cerebras**
- **Base URL:** `https://api.cerebras.ai/v1`
- **Free models:** `llama3.1-8b`
- **Rate limit:** 30 req/min (free)
- **Why #5:** Very fast for an 8B model; free tier is solid but model
  selection is limited
- **Recommended model:** `llama3.1-8b`

### Rank 6 — **Hugging Face Inference API**
- **Base URL:** `https://api-inference.huggingface.co/v1`
- **Free models:** Many open-source models via the serverless API
- **Rate limit:** Varies; can be slow at peak times
- **Why #6:** Huge model library, but cold starts and rate limits make it
  unreliable for a real-time Discord bot without a Pro plan
- **Recommended model:** `meta-llama/Meta-Llama-3-8B-Instruct`

---

## How to Switch Providers

1. Open your Replit Secrets (or `.env`).
2. Set `OPENAI_API_KEY` to the new provider's API key.
3. Set `AI_INTEGRATIONS_OPENAI_BASE_URL` to the provider's base URL (see
   table above).
4. Update the `model` name in `src/utils/ai/openai_client.py` → `generate_reply_openai`
   (look for `model="llama-3.1-8b-instant"`) to a model the new provider supports.
5. Restart the bot.

> **Tip:** The Replit built-in OpenAI integration sets both variables
> automatically when you connect it, so you don't need to touch secrets for
> the default setup.

---

## Token Usage at Niko's Settings

With the current optimised prompt pipeline (gpt-4o-mini defaults):

| Scenario | Approx. input tokens | Approx. output tokens |
|---|---|---|
| Basic message, no experiments | ~400 | ~80 |
| Better Context enabled | ~550 | ~80 |
| AI Actions enabled | ~900 | ~80 |
| Both experiments enabled | ~1 050 | ~80 |

At OpenAI `gpt-4o-mini` pricing ($0.15 / $0.60 per 1M tokens), **1,000
messages cost roughly $0.11** with no experiments and **~$0.17** with both
experiments enabled.
