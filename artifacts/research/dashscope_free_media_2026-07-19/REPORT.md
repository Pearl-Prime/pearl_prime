# DashScope (Singapore / International) — Free Media Capability Report

**Date:** 2026-07-19  
**Agent:** Pearl_Int  
**Region:** Singapore `ap-southeast-1` / intl endpoint only  
**Acceptance:** EXECUTED-REAL (docs cited + live key probe); live BALANCE = OPERATOR-READ pending  
**Policy:** Investigation only — does **not** wire paid DashScope into pipelines (`llm-policy-enforcement` stays green).

---

## Direct answer (one line per family)

| Family | Free on Singapore new-user quota? | How much (docs) | Usable on THIS account right now? |
|--------|-----------------------------------|-----------------|-----------------------------------|
| **Video** | **Yes** (per model, new-user, 90d) | **50 seconds** typical Wan T2V/I2V (`wan2.6/2.7-*`); HappyHorse **10s** | **No — blocked by `Arrearage`** |
| **Image** | **Yes** (per model, new-user, 90d) | Wan T2I **50–200 images**; Qwen-Image **100 images** | **No — blocked by `Arrearage`** |
| **TTS** | **Yes** (per model, new-user, 90d) | CosyVoice **10,000 chars**; Qwen3-TTS **110,000 chars** | **No — blocked by `Arrearage`** |
| **Text / translation** | **Yes** (per model, new-user, 90d) | Typically **1,000,000 tokens per model** (e.g. `qwen-plus` / `qwen-max` family) | **No — same account-level `Arrearage` block** (not proven as “tokens=0” alone) |

**Shared vs per-model:** Free quota is **per model ID**, not one shared pool across families. Exhausting `qwen-plus` does **not** spend Wan video or CosyVoice free seconds/chars. Account + RAM users **share** each model’s free bucket. Source: [Free quota for new users](https://www.alibabacloud.com/help/en/model-studio/new-free-quota) + per-row figures on [Model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing).

**Critical live finding:** Key authenticates (`GET /models` → **200**, 149 models). Every generation probe returned **`code: Arrearage`** (overdue / not in good standing). Official FAQ: an overdue balance **blocks all invocations even if free quota remains**. So “translation free credit looks exhausted” is most likely **account arrearage**, not proof that media free tiers were already spent.

---

## Capability + quota table (Singapore / International)

| family | model_id(s) | free? | free amount | unit | expiry | rate limit (intl) | key-reachable (probe) | source URL |
|--------|-------------|-------|-------------|------|--------|-------------------|------------------------|------------|
| video | `wan2.7-t2v`, `wan2.6-t2v`, `wan2.5-t2v-preview`, `wan2.1-t2v-turbo`, … | Yes (new-user intl) | **50** | seconds | 90 days from Model Studio activate | task submit **5 RPS** / **5** concurrent (Wan 2.5+) | catalog: partial; generate: **Arrearage HTTP 400** | [model-pricing §Wanx-Text-to-Video](https://www.alibabacloud.com/help/en/model-studio/model-pricing); [rate-limit](https://www.alibabacloud.com/help/en/model-studio/rate-limit) |
| video | `wan2.7-i2v`, `wan2.6-i2v`, `wan2.5-i2v-preview`, … | Yes | **50** | seconds | 90 days | same class (~5/5) | generate: **Arrearage** | same |
| video | `happyhorse-1.x-t2v/i2v/r2v` | Yes | **10** | seconds | 90 days | see pricing/rate-limit pages | not probed (arrearage already blocks) | [model-pricing §HappyHorse](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| image | `wan2.6-t2i`, `wan2.5-t2i-preview` | Yes | **50** | images | 90 days | e.g. `wan2.6-t2i` **5/5** | generate `wan2.1-t2i-turbo`: **Arrearage** | [model-pricing §Wanx Text-to-Image](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| image | `wan2.2-t2i-*` | Yes | **100** | images | 90 days | see rate-limit | blocked by arrearage | same |
| image | `wan2.1-t2i-plus/turbo` | Yes | **200** | images | 90 days | see rate-limit | blocked by arrearage | same |
| image | `qwen-image`, `qwen-image-plus/max/2.0*` | Yes | **100** | images | 90 days | ~2/min or 2/s by model | listed in `/models` (200); generate blocked | same §Qwen Text-to-Image |
| image | `wan2.7-image`, `wan2.7-image-pro`, `wan2.6-image` | Yes | **50** | images | 90 days | see rate-limit | listed in `/models` | same §Wanx Image Gen/Edit |
| TTS | `cosyvoice-v3-flash` | Yes | **10,000** | characters | 90 days | low concurrency (~3 for plus) | native call **Arrearage** (not Model.NotFound) | [model-pricing §CosyVoice](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| TTS | `cosyvoice-v3-plus` | Yes | **10,000** | characters | 90 days | ~3 | same | same |
| TTS | `qwen3-tts-flash` (+ instruct/vd/vc variants) | Yes | **110,000** | characters | 90 days | **180 RPM** (`qwen3-tts-flash`) | listed in `/models`; generate **Arrearage** | [model-pricing §Qwen-TTS](https://www.alibabacloud.com/help/en/model-studio/model-pricing); [rate-limit](https://www.alibabacloud.com/help/en/model-studio/rate-limit) |
| TTS | CosyVoice **voice clone** (creation) | Yes (SG) | **1,000** voices | creations | 90 days | n/a | not probed | [voice cloning](https://www.alibabacloud.com/help/en/model-studio/voice-cloning-user-guide) |
| TTS | **Sambert** | **No Singapore free row found** | — | — | — | — | **absent** from intl pricing + `/models` (legacy Beijing-side family) | pricing page has CosyVoice/Qwen-TTS only for SG speech synth |
| text | `qwen-plus` / `qwen-max` / peers | Yes | **1,000,000** | tokens | 90 days | `qwen-plus` intl **600 RPM / 1.5M TPM** (Batch exempt) | `/models` ok; tiny chat **HTTP 400** (sparse body; account denial class) | [model-pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing); [new-free-quota](https://www.alibabacloud.com/help/en/model-studio/new-free-quota) |

Notes:
- Free quota applies **only** to Singapore + International deployment scope. Beijing / Global / US have **no** free quota on these tables.
- Free covers **real-time inference only** — not batch, fine-tune, or deploy.
- After free quota expires/exhausts → pay-as-you-go (unless Free Quota Only is on → `AllocationQuota.FreeTierOnly`).
- **This account never reached FreeTierOnly in probe** — it hit **`Arrearage` first**.

---

## Translation-quota finding

1. **Docs:** Text free tier is **1M tokens per model**, independent of media families.  
2. **Live:** Key works for catalog; inference denied with **`Arrearage`**.  
3. **Conclusion:** Operator’s “free translation credit looks out” is **consistent with overdue standing**, which also blocks video/image/TTS free leftover. Remaining free balance (if any) is **OPERATOR-READ** from console Free Quota tab after arrears cleared.

---

## Live probe summary

See `artifacts/research/dashscope_free_media_2026-07-19/probe.log` (redacted).

| Probe | HTTP | Result |
|-------|------|--------|
| `GET …/compatible-mode/v1/models` | **200** | 149 models; image + qwen3-tts IDs present |
| `POST chat/completions` (`qwen-plus`, max_tokens=1) | **400** | denied (sparse body) |
| image `wan2.1-t2i-turbo` async | **400** | `Arrearage` |
| video `wan2.1-t2v-turbo` async | **400** | `Arrearage` |
| TTS `cosyvoice-v3-flash` | **400** | `Arrearage` |
| TTS `qwen3-tts-flash` | **400** | `Arrearage` |

Endpoint used: `https://dashscope-intl.aliyuncs.com` (intl / Singapore). Key never printed/committed.

---

## OPERATOR ACTION — live balance (login required)

1. Open **Singapore** console (not Beijing):  
   https://modelstudio.console.alibabacloud.com/ap-southeast-1  
2. **First — clear arrears:** Alibaba Cloud Billing / Expenses → pay overdue balance (probe error links [overdue-payment](https://www.alibabacloud.com/help/en/model-studio/error-code#overdue-payment)). Until this is green, free media cannot run.  
3. Model Studio → **Model usage** → **Free Quota** tab: for each of `wan2.6-t2v` / `wan2.1-t2i-turbo` / `cosyvoice-v3-flash` / `qwen3-tts-flash` / your translation model (`qwen-plus` or configured `DASHSCOPE_MODEL`), read **remaining / total** and **expiry**.  
4. Optional safety: enable **Free Quota Only** on those models so post-quota calls stop instead of billing.  
5. API key page (confirm region): https://modelstudio.console.alibabacloud.com/ap-southeast-1#/api-key  

Account login (registry): `gmalone@oneteamtech.com`.

---

## Policy / production note

- Media free-tier use = **operator-present only** until an explicit policy decision.  
- Do **not** add `DASHSCOPE_API_KEY` reads to scheduled workflows for paid media.  
- Repo already uses DashScope as cloud LLM fallback via existing callers; this report does not expand that surface.

---

## STARTUP_RECEIPT (session)

- branch at start: `codex/realist-social-samples-20260718`  
- pwd: `/Users/ahjan/phoenix_omega`  
- `git fetch/ls-remote origin` → **github=BLOCKED-403** (account suspended)  
- Read: `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §1d, `CLAUDE.md` Critical URLs + LLM tier ban, `scripts/ci/integration_env_registry.py` (`DASHSCOPE_*`)  
- Builds on: Keychain `DASHSCOPE_*` / `QWEN_*`; caller `scripts/translate_atoms_all_locales_cloud.py`
