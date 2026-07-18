# Pearl News — LLM Routing Handoff

**Owner:** Pearl_Int / Pearl_Architect
**Last updated:** 2026-04-20
**Config file:** `pearl_news/config/llm_expansion.yaml`
**Env registry:** `scripts/ci/integration_env_registry.py`

---

## What this system does

When Pearl News expands a slot-based article draft into full prose, it calls an LLM. The language of the **output article** determines which LLM is used. All providers use the OpenAI-compatible API format.

---

## Routing table

| Output language | Provider | Model | Cost |
|---|---|---|---|
| `en`, `vi` (and all non-CJK) | **Groq** → xAI → Together AI | llama-3.3-70b-versatile | Free |
| `ja`, `ko`, `zh-cn`, `zh-tw`, `zh-hk`, `zh-sg` | **DashScope Qwen** | qwen-plus | Paid (live key) |

---

## Provider details

### EN default: Groq

| Field | Value |
|---|---|
| Env var | `GROQ_API_KEY` |
| Base URL | `https://api.groq.com/openai/v1` |
| Model | `llama-3.3-70b-versatile` |
| Free tier | ~14,400 requests/day, 6,000 tokens/min |
| Get key | https://console.groq.com/keys |
| Key prefix | `gsk_...` |

### EN fallback 1: xAI / Grok

| Field | Value |
|---|---|
| Env var | `XAI_API_KEY` |
| Base URL | `https://api.x.ai/v1` |
| Model | `grok-3-mini` |
| Free tier | $25/month free credits (no card needed) |
| Get key | https://console.x.ai → API Keys |
| Key prefix | `xai-...` |

### EN fallback 2: Together AI

| Field | Value |
|---|---|
| Env var | `TOGETHER_API_KEY` |
| Base URL | `https://api.together.xyz/v1` |
| Model | `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` |
| Free tier | 1M tokens/month |
| Get key | https://api.together.ai/settings/api-keys |
| Key prefix | `tgp_v1_...` |

### CJK6 primary: DashScope Qwen

| Field | Value |
|---|---|
| Env var | `DASHSCOPE_API_KEY` |
| Base URL | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` (Singapore — do not use Beijing) |
| Model | `qwen-plus` |
| Cost | Paid — live key in Keychain |
| Get key | https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key |

### On-request only: Cloudflare Workers AI

| Field | Value |
|---|---|
| Env vars | `CLOUDFLARE_AI_API_TOKEN`, `CLOUDFLARE_AI_BASE_URL`, `CLOUDFLARE_AI_MODEL` |
| Model | `@cf/google/gemma-3-12b-it` (or similar) |
| Free tier | 10,000 neurons/day — too small for production (~5 articles) |
| Use | CLI only: `--provider cloudflare_slots` |
| Status | **NOT in production routing** |

---

## Fallback chain (EN)

```
groq_slots → grok_slots → together_slots
```

If Groq is rate-limited or errors, xAI is tried. If xAI fails, Together AI is tried. No fallback for CJK6 — DashScope only.

---

## Adding keys to macOS Keychain

All keys live in Keychain under service `phoenix-omega`, account = env var name.

```bash
# Groq
security add-generic-password -s phoenix-omega -a GROQ_API_KEY -w "gsk_..."

# xAI
security add-generic-password -s phoenix-omega -a XAI_API_KEY -w "xai-..."

# Together AI
security add-generic-password -s phoenix-omega -a TOGETHER_API_KEY -w "tgp_v1_..."

# DashScope (CJK6)
security add-generic-password -s phoenix-omega -a DASHSCOPE_API_KEY -w "sk-..."
```

To update an existing key (if key is rotated):

```bash
security delete-generic-password -s phoenix-omega -a GROQ_API_KEY
security add-generic-password -s phoenix-omega -a GROQ_API_KEY -w "gsk_NEW..."
```

---

## Verify all keys load

```bash
python3 scripts/ci/load_integration_env_from_keychain.py --verbose 2>&1 | grep -E "GROQ|XAI|TOGETHER|DASHSCOPE"
```

Expected output (all four lines show `export KEY=...`):

```
export DASHSCOPE_API_KEY=sk-...
export GROQ_API_KEY=gsk_...
export TOGETHER_API_KEY=tgp_v1_...
export XAI_API_KEY=xai-...
```

---

## Load env and test a single article expansion

```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

# EN article via Groq
python3 pearl_news/pipeline/run_expansion.py --lang en --provider groq_slots

# CJK6 article via DashScope
python3 pearl_news/pipeline/run_expansion.py --lang ja --provider qwen_slots

# Force Cloudflare (on-request only)
python3 pearl_news/pipeline/run_expansion.py --lang en --provider cloudflare_slots
```

---

## Config files

| File | Purpose |
|---|---|
| `pearl_news/config/llm_expansion.yaml` | Routing rules, provider configs, fallback chain |
| `scripts/ci/integration_env_registry.py` | Canonical list of all tracked env vars |
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` | Human-facing docs for all credentials |

---

## Free tier limits (approximate)

| Provider | Limit | Articles/day (est. ~1,500 tokens each) |
|---|---|---|
| Groq | 14,400 req/day, 6K tokens/min | ~500+ |
| xAI | $25/mo credit | ~200–500/mo |
| Together AI | 1M tokens/month | ~600/month |
| Cloudflare | 10K neurons/day | ~5/day (**not for production**) |

For typical Pearl News volume, Groq alone covers all EN production traffic. xAI and Together AI are genuine fallbacks, not expected to be hit in normal operation.
