# AI Provider Compatibility Guide

Niko uses Groq's OpenAI-compatible chat-completions API
(`/openai/v1/chat/completions`) through the existing `openai` Python client.
Configure the provider with:

```
GROQ_API_KEY=<your Groq API key>
```

The bot uses Groq by default for chat, image understanding, and transcription.
The endpoint and model names remain configurable with `GROQ_BASE_URL`,
`GROQ_MODEL`, `GROQ_VISION_MODEL`, and `GROQ_TRANSCRIPTION_MODEL`.

---

## Active Provider

| Provider | Chat model | Vision model | Transcription model |
|---|---|---|---|
| **Groq** | `openai/gpt-oss-20b` | `meta-llama/llama-4-scout-17b-16e-instruct` | `whisper-large-v3-turbo` |

These defaults can be overridden through the `GROQ_*` environment variables
listed above. Use models available to the Groq account when overriding them.

---

## Other OpenAI-Compatible Providers

The active bot configuration is Groq. The providers below are reference
options for future provider work; they are not used unless the client code is
changed accordingly.

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
- **Free models:** `openai/gpt-oss-20b`, `mixtral-8x7b-32768`,
  `gemma2-9b-it`
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

## Groq Setup

1. Create a Groq API key in the Groq console.
2. Add `GROQ_API_KEY` in the project environment/Keys panel.
3. Optionally set `GROQ_MODEL`, `GROQ_VISION_MODEL`, or
   `GROQ_TRANSCRIPTION_MODEL` to models enabled for the account.
4. Restart the bot so the client picks up the new settings.

---

## Token Usage at Niko's Settings

With the current optimised prompt pipeline (Groq chat-model defaults):

| Scenario | Approx. input tokens | Approx. output tokens |
|---|---|---|
| Basic message, no experiments | ~400 | ~80 |
| Better Context enabled | ~550 | ~80 |
| AI Actions enabled | ~900 | ~80 |
| Both experiments enabled | ~1 050 | ~80 |

Provider pricing and quotas vary by Groq model and account tier; consult the
Groq console for current limits before enabling high-volume multimodal use.
