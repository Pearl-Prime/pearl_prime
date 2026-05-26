# Integration Credentials Registry

**Purpose:** Single canonical reference for every external service credential in Phoenix Omega.
**Owner:** Pearl_Int / Pearl_Architect
**Last updated:** 2026-05-27 (Added §12a fal.ai — serverless GPU inference, blocks Milestone H §7.1 per OPD-151; setup runbook + `FAL_KEY` env var registered)
**Rule:** No actual secrets in this file. Only env var names, documentation, and pointers.

### Phase 1 + 2 scope (deliverables)

- **12 core services** (sections 1–12 below): Qwen/DashScope, Anthropic, OpenAI, ElevenLabs, Cloudflare, GitHub, WordPress, GoHighLevel, Plaid (YAML config, not `.env`), SMTP, Google Analytics 4, Ollama.
- **Environment variables:** `scripts/ci/check_integration_env.py` tracks one row per env var name (includes video platforms and SerpApi); run it for set vs missing. Exit code **1** if any **required** row is unset in the current shell (today: Qwen key + base URL).
- **Messaging:** five operator channels documented in [Messaging channels (Keychain-based)](#messaging-channels-keychain-based); secrets live in macOS Keychain (or local YAML for iMessage), not in the checker.
- **GitHub Actions:** repository secrets used by workflows are summarized in [GitHub Actions secrets](#github-actions-secrets); local shells use `GITHUB_TOKEN` / `GITHUB_REPOSITORY` where applicable.
- **Pearl_Int operational notes:** trend feeds, SerpApi budget, and per-integration validation history remain in `skills/pearl-int/references/integration_registry.md`, which defers env var names to this file.

---

## Quick start

**Check what's wired in your shell:**

```bash
python3 scripts/ci/check_integration_env.py
```

This reads the registry below and reports which env vars are set vs missing.

**Set up all local integrations (WordPress + messaging channels):**

```bash
/bin/zsh ./scripts/integrations/setup_all_local_integrations.sh
```

---

## Service registry

### 0. Pearl Star — Local Inference Server (PRIMARY)

| Field | Value |
|-------|-------|
| **Server** | Ubuntu 24.04 at `PEARL_STAR_IP` (default: 192.168.1.112 LAN) |
| **Services** | Ollama/Qwen3:14b (:11434), ComfyUI/FLUX.1-dev (:8188), CosyVoice2 (:9880) |
| **Env vars** | `PEARL_STAR_IP`, `COMFYUI_URL`, `COSYVOICE_URL` (optional gated downloads: `HF_TOKEN`) |
| **Consumed by** | `phoenix_v4/manga/image_backend.py`, `scripts/image_generation/runcomfy_batch.py`, `scripts/video/flux_client.py`, `scripts/audio/generate_presenter_audio.py`, `scripts/localization/llm_client.py`, `pearl_news/pipeline/llm_expand.py` |
| **How to obtain** | See [docs/UBUNTU_PRODUCTION_SERVER_SETUP.md](./UBUNTU_PRODUCTION_SERVER_SETUP.md) |
| **Required vs optional** | `PEARL_STAR_IP` and `COMFYUI_URL` required; `COSYVOICE_URL` optional (CJK TTS) |
| **Status** | Primary provider for image gen, CJK LLM, and CJK TTS |

**SSH access (configured 2026-04-08):**
- Host alias: `pearl_star` (in `~/.ssh/config`)
- User: `ahjan108`
- Key: `~/.ssh/id_ed25519_pearl_star`
- Test: `ssh pearl_star hostname` → `pearlstar`

**Hardware (verified 2026-04-08):**
- GPU: NVIDIA GeForce RTX 5070 Ti (16 GB VRAM)
- RAM: 64 GB (58 GB free at idle)
- PyTorch: 2.11.0+cu130
- ComfyUI: 0.18.1
- Ollama: qwen3:14b (9.3 GB Q4_K_M)

**Provider migration (2026-04-08):**
- **Image generation:** ComfyUI on Pearl Star is now PRIMARY. RunComfy cloud is optional fallback.
- **CJK LLM:** Ollama/Qwen3:14b on Pearl Star is now the default `QWEN_BASE_URL` target. DashScope is cloud fallback.
- **CJK TTS:** CosyVoice2 on Pearl Star for zh/ja/ko. Edge-TTS is free fallback. ElevenLabs remains primary for EN.
- **EN TTS:** ElevenLabs — NO CHANGE.

**Keychain (macOS, for load_integration_env_from_keychain.py):**
- `PEARL_STAR_IP` = 192.168.1.112
- `COMFYUI_URL` = http://192.168.1.112:8188
- `COSYVOICE_URL` = http://192.168.1.112:9880
- `QWEN_BASE_URL` = http://192.168.1.112:11434/v1

**Hugging Face (`HF_TOKEN`) — Pearl Star gated downloads (optional):**
- **Env var:** `HF_TOKEN` (user access token — **Keychain only**; do not paste into repo docs or commits).
- **Used for:** authenticated pulls of gated/large checkpoints on Pearl Star (`huggingface-cli`, ComfyUI-managed downloads). Install/runbook reference: [docs/runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md](./runbooks/PEARL_STAR_PULID_INSTALL_2026-05-07.md).
- **How to obtain:** Hugging Face → Settings → Access Tokens — create a token with read access to needed models/repos.
- **Required vs optional:** Optional — required only when downloading models that enforce Hugging Face authentication.

### 1a. Together AI — LLM (preferred for Qwen translation; free fallback for Pearl News EN)

| Field | Value |
|-------|-------|
| **Env vars** | `TOGETHER_API_KEY`, `TOGETHER_MODEL` |
| **Consumed by** | `scripts/localization/llm_client.py` (auto-detected, takes priority over DashScope); `pearl_news/pipeline/slot_expansion.py` (`together_slots` fallback 2) |
| **GitHub workflows** | `translate-bestseller-atoms.yml`, `generate-and-translate-atoms.yml` |
| **How to obtain** | Together AI: https://api.together.ai/settings/api-keys — create free key |
| **Required vs optional** | Preferred for all Qwen LLM work (translation, research). Falls back to DashScope if not set. Free tier: **1M tokens/month** |
| **Status** | Wired in CI and local scripts; also Pearl News EN fallback 2 |
| **Default models** | Draft: `Qwen/Qwen2.5-7B-Instruct-Turbo`, Judge: `Qwen/Qwen3-235B-A22B-Instruct-2507-tput`; Pearl News: `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` |
| **Base URL** | `https://api.together.xyz/v1` (hardcoded, OpenAI-compatible) |

### 1b. Groq — LLM (Pearl News EN default, free tier)

| Field | Value |
|-------|-------|
| **Env vars** | `GROQ_API_KEY` |
| **Consumed by** | `pearl_news/pipeline/slot_expansion.py` (`groq_slots` — default provider for EN + non-CJK6) |
| **GitHub workflows** | Pearl News fill workflows |
| **How to obtain** | Groq Console: https://console.groq.com/keys — create free API key |
| **Required vs optional** | **Preferred for Pearl News EN articles.** Free tier: ~14,400 req/day, 6,000 tokens/min |
| **Status** | ⚠️ NOT YET IN KEYCHAIN — must add `GROQ_API_KEY` via `security add-generic-password` |
| **Model** | `llama-3.3-70b-versatile` (free, fast) |
| **Base URL** | `https://api.groq.com/openai/v1` (OpenAI-compatible) |

### 1c. xAI (Grok) — LLM (Pearl News EN fallback 1, free credits)

| Field | Value |
|-------|-------|
| **Env vars** | `XAI_API_KEY` |
| **Consumed by** | `pearl_news/pipeline/slot_expansion.py` (`grok_slots` — fallback 1 when Groq fails) |
| **How to obtain** | xAI Console: https://console.x.ai — create API key ($25/mo free credits auto-applied) |
| **Required vs optional** | Optional fallback. Free tier: **$25/month free credits** |
| **Status** | ⚠️ NOT YET IN KEYCHAIN — must add `XAI_API_KEY` via `security add-generic-password` |
| **Model** | `grok-3-mini` (free) |
| **Base URL** | `https://api.x.ai/v1` (OpenAI-compatible) |

### 1d. Qwen / DashScope (Alibaba Cloud) — LLM (CJK6 primary; EN fallback)

| Field | Value |
|-------|-------|
| **Env vars** | `QWEN_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL` |
| **Alt env vars** | `DASHSCOPE_API_KEY`, `DASHSCOPE_BASE_URL`, `DASHSCOPE_MODEL` |
| **Consumed by** | `pearl_news/pipeline/llm_expand.py`, `pearl_news/pipeline/slot_provider_qwen.py`, `scripts/research/run_research.py`, `scripts/localization/llm_client.py`, `scripts/localization/run_locale_batches.py`, `scripts/translate_atoms_all_locales_cloud.py` |
| **GitHub workflows** | `research-pipeline-run.yml`, `pearl-news-fill-qwen.yml`, `translate-atoms-qwen-matrix.yml` |
| **How to obtain** | DashScope console: https://dashscope.console.aliyun.com/ — create API key under Access Key Management |
| **Required vs optional** | Optional cloud fallback — local Ollama on Pearl Star is now default LLM target |
| **Status** | DEMOTED to fallback (2026-04-08). Wired in CI and local scripts. |
| **Detailed docs** | [docs/AGENT_QWEN_API_KEY_LANE.md](./AGENT_QWEN_API_KEY_LANE.md) |

### 2. Anthropic — LLM

| Field | Value |
|-------|-------|
| **Env vars** | `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` |
| **Consumed by** | `pearl_news/pipeline/llm_expand_claude.py`, `tools/teacher_mining/intake_normalize.py`, `scripts/ci/llm_bestseller_error_report.py`, `scripts/ci/llm_cohesive_bestseller_tester.py` |
| **GitHub workflows** | None (local/CI-runner only) |
| **How to obtain** | Anthropic Console: https://console.anthropic.com/ — API Keys page |
| **Required vs optional** | Optional — Qwen is the primary LLM; Claude is used for cohesive bestseller testing and Pearl News Claude expansion path |
| **Status** | Wired in local scripts |
| **Fallback key file** | `claude_api_key.rtf` (repo root, gitignored) |

### 3. OpenAI — LLM + TTS

| Field | Value |
|-------|-------|
| **Env vars** | `OPENAI_API_KEY` |
| **Consumed by** | `tools/teacher_mining/intake_normalize.py`, `scripts/ci/llm_bestseller_error_report.py`, `scripts/ci/llm_cohesive_bestseller_tester.py`, TTS via `config/tts/engines.yaml` |
| **GitHub workflows** | None (local/CI-runner only) |
| **How to obtain** | OpenAI Platform: https://platform.openai.com/api-keys |
| **Required vs optional** | Optional — used as fallback LLM and for TTS (voice: "nova") |
| **Status** | Wired in local scripts and TTS config |

### 4. ElevenLabs — TTS

| Field | Value |
|-------|-------|
| **Env vars** | `ELEVENLABS_API_KEY` |
| **Consumed by** | TTS pipeline via `config/tts/engines.yaml` (voice: "Rachel") |
| **GitHub workflows** | None |
| **How to obtain** | ElevenLabs: https://elevenlabs.io/ — Profile > API Keys |
| **Required vs optional** | Required for guided audio and journal prompt TTS |
| **Status** | Wired in TTS config |
| **Fallback key file** | `11.txt` (repo root, gitignored) |

### 5. Cloudflare Workers AI — Image generation + Pages

| Field | Value |
|-------|-------|
| **Env vars** | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_AI_API_TOKEN` |
| **Consumed by** | `scripts/video/flux_client.py` |
| **GitHub workflows** | `brand-admin-onboarding-pages.yml` |
| **How to obtain** | Cloudflare Dashboard: https://dash.cloudflare.com/ — Workers & Pages > Overview (account ID in URL); API Tokens under My Profile |
| **Required vs optional** | Required for video/image pipeline and brand-admin pages deployment |
| **Status** | Wired in CI and local scripts |
| **Detailed docs** | [docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md](./VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md) |

### 6. GitHub API

| Field | Value |
|-------|-------|
| **Env vars** | `GITHUB_TOKEN`, `GITHUB_REPOSITORY` |
| **Consumed by** | `dashboard.py`, `scripts/audit/remote_commit_review.py`, `scripts/dashboard/github_tab.py`, `scripts/observability/agent_open_fix_pr.py`, `scripts/ci/verify_github_governance.py` |
| **GitHub workflows** | `production-observability.yml`, `auto-merge-bot-fix.yml`, `ml-loop-daily-promotion.yml`, `github-governance-check.yml`, `remote-commit-review.yml` (uses `secrets.GITHUB_TOKEN` automatically) |
| **How to obtain** | GitHub Settings > Developer settings > Personal access tokens (fine-grained recommended) |
| **Required vs optional** | Required for governance checks, dashboard, observability; auto-provided in GitHub Actions via `secrets.GITHUB_TOKEN` |
| **Status** | Wired |

### 7. WordPress — Pearl News publishing

| Field | Value |
|-------|-------|
| **Env vars** | `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD` |
| **Consumed by** | `pearl_news/publish/wordpress_client.py`, `pearl_news_post_to_wp.py` |
| **GitHub workflows** | Referenced in `pearl-news-fill-qwen.yml` scheduling docs |
| **How to obtain** | WordPress Admin > Users > Application Passwords (generate one for the publishing user) |
| **Required vs optional** | Required for Pearl News article publishing |
| **Status** | Wired (local Keychain via setup scripts) |
| **Local setup** | `scripts/integrations/setup_wordpress_local.sh` — stores in macOS Keychain service `phoenix-omega-wordpress` |
| **Detailed docs** | [docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md](./LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md), [pearl_news/README.md](../pearl_news/README.md) |

### 8. GoHighLevel (GHL) — Funnel CRM

| Field | Value |
|-------|-------|
| **Env vars** | `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CONTACTS_URL` |
| **Consumed by** | `funnel/burnout_reset/app.py` |
| **GitHub workflows** | None |
| **How to obtain** | GoHighLevel dashboard > Settings > API Keys; Location ID from Settings > Business Profile |
| **Required vs optional** | Required for funnel lead capture |
| **Status** | Placeholder — needs live GHL account |
| **Detailed docs** | [funnel/burnout_reset/GHL_HANDBOFF.md](../funnel/burnout_reset/GHL_HANDBOFF.md), [funnel/README.md](../funnel/README.md) |

### 9. Plaid — Payouts banking

| Field | Value |
|-------|-------|
| **Env vars** | N/A (uses `config/payouts/credentials.yaml`) |
| **Config file** | `config/payouts/credentials.yaml` (gitignored; copy from `credentials.yaml.example`) |
| **Consumed by** | Payouts pipeline (see `config/payouts/`) |
| **How to obtain** | Plaid Dashboard: https://dashboard.plaid.com/ — Keys page |
| **Required vs optional** | Required for payout operations |
| **Status** | Template exists; not wired to live account |
| **Detailed docs** | [config/payouts/CHECKLIST.md](../config/payouts/CHECKLIST.md) |

### 10. SMTP — Funnel email

| Field | Value |
|-------|-------|
| **Env vars** | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `FROM_NAME` |
| **Consumed by** | `funnel/burnout_reset/email_send.py` |
| **GitHub workflows** | None |
| **How to obtain** | Your email provider's SMTP settings (e.g., Gmail app password, SendGrid, Mailgun) |
| **Required vs optional** | Required for funnel email delivery |
| **Status** | Placeholder — needs SMTP provider |
| **Detailed docs** | [funnel/README.md](../funnel/README.md) |

### 11. Google Analytics 4 — Funnel analytics

| Field | Value |
|-------|-------|
| **Env vars** | `GA4_MEASUREMENT_ID` |
| **Consumed by** | `funnel/burnout_reset/app.py` |
| **GitHub workflows** | None |
| **How to obtain** | Google Analytics > Admin > Data Streams > Measurement ID (starts with `G-`) |
| **Required vs optional** | Optional — funnel works without analytics |
| **Status** | Placeholder |

### 12. Ollama — Local LLM (research)

| Field | Value |
|-------|-------|
| **Env vars** | `OLLAMA_HOST`, `OLLAMA_MODEL` |
| **Consumed by** | `scripts/research/run_research.py` |
| **GitHub workflows** | None |
| **How to obtain** | Install Ollama locally: https://ollama.com/ — runs on `localhost:11434` by default |
| **Required vs optional** | Optional — alternative to Qwen for local research |
| **Status** | Wired in research script |

### 12a. fal.ai — Serverless GPU inference (Qwen-Image-Layered + other hosted models)

| Field | Value |
|-------|-------|
| **Env vars** | `FAL_KEY` |
| **Consumed by** | Milestone H §7.1 smoke test (`fal-ai/qwen-image-layered/lora` endpoint). Future V5.1 catalog rollout dispatcher pending operator decision. |
| **GitHub workflows** | None yet (smoke test runs locally / interactively) |
| **How to obtain** | fal.ai dashboard: https://fal.ai/dashboard/keys — sign in, "Add Key", copy once (shown only at creation). Free tier: small credit on signup. Full setup runbook: [docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md](./runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md) |
| **Required vs optional** | Optional — blocks Milestone H §7.1 smoke test until operator provisions. Not used elsewhere yet. |
| **Status** | **NOT YET PROVISIONED** — Phoenix has no fal.ai account as of 2026-05-27. OPD-151 (operator-approved) gates Milestone H §7.1 smoke test on this credential. OPD-153 status. |
| **Pricing reference** | [`docs/MANGA_V5_COMPUTE_SCALING_OPTIONS.md`](./MANGA_V5_COMPUTE_SCALING_OPTIONS.md) §3.4: `fal-ai/qwen-image` stage 1 = $0.02/MP, `fal-ai/qwen-image-layered/lora` stage 2 = $0.06/image. Two-stage panel ≈ $0.08 (smoke test cost ≈ $1 for one ep_001 panel pair). |
| **License / commercial-clean** | Apache-2.0 model + fal.ai commercial-clean ToS per scout `artifacts/research/iyashikei_style_lora_scout_2026-05-21.md` Channel 1 + scaling-options doc §3.4 line 150. |
| **Env var name standard** | `FAL_KEY` is the canonical name the [`fal-client`](https://github.com/fal-ai/fal/tree/main/projects/fal_client) Python/JS SDK reads automatically. Do NOT use `FAL_API_KEY` or other variants — the SDK will not find them. |
| **Base URL** | `https://fal.run/<model-id>` (REST queue API, e.g. `https://fal.run/fal-ai/qwen-image-layered/lora`); status polling via `https://queue.fal.run/<model-id>/requests/<request-id>/status`. |
| **Validation** | `curl -sS -H "Authorization: Key $FAL_KEY" https://fal.run/fal-ai/qwen-image -d '{}' -H "content-type: application/json"` — expect a JSON response (queue accept or validation error from a missing-prompt body), NOT a 401. Cheap GET alternative: `curl -sS -H "Authorization: Key $FAL_KEY" https://queue.fal.run/fal-ai/qwen-image/requests/00000000-0000-0000-0000-000000000000/status` should return 404-not-found JSON (proving auth ok), not 401. |
| **Detailed docs** | [docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md](./runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md) — operator setup steps |

---

## Video platforms

### 13. YouTube — Video publishing (per brand: SP, CC, ND)

| Field | Value |
|-------|-------|
| **Env vars** | `YT_CLIENT_ID_SP`, `YT_CLIENT_SECRET_SP`, `YT_REFRESH_TOKEN_SP`, `YT_CLIENT_ID_CC`, `YT_CLIENT_SECRET_CC`, `YT_REFRESH_TOKEN_CC`, `YT_CLIENT_ID_ND`, `YT_CLIENT_SECRET_ND`, `YT_REFRESH_TOKEN_ND` |
| **Consumed by** | `scripts/video/uploaders/youtube.py` |
| **GitHub workflows** | `video-daily-publish.yml` |
| **How to obtain** | Google Cloud Console: https://console.cloud.google.com/ — APIs & Services > Credentials > OAuth 2.0 Client (YouTube Data API v3 enabled) |
| **Required vs optional** | Required for YouTube video publishing |
| **Status** | Missing — credentials not yet provisioned |
| **Detailed docs** | [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) |

### 14. TikTok — Video publishing (per brand: SP, CC, ND)

| Field | Value |
|-------|-------|
| **Env vars** | `TIKTOK_CLIENT_KEY_SP`, `TIKTOK_CLIENT_SECRET_SP`, `TIKTOK_ACCESS_TOKEN_SP`, `TIKTOK_CLIENT_KEY_CC`, `TIKTOK_CLIENT_SECRET_CC`, `TIKTOK_ACCESS_TOKEN_CC`, `TIKTOK_CLIENT_KEY_ND`, `TIKTOK_CLIENT_SECRET_ND`, `TIKTOK_ACCESS_TOKEN_ND` |
| **Consumed by** | `scripts/video/uploaders/tiktok.py` |
| **GitHub workflows** | `video-daily-publish.yml` |
| **How to obtain** | TikTok Developer Portal: https://developers.tiktok.com/ — Content Posting API |
| **Required vs optional** | Required for TikTok video publishing |
| **Status** | Missing — credentials not yet provisioned |
| **Detailed docs** | [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) |

### 15. Instagram — Video publishing (per brand: SP, CC, ND)

| Field | Value |
|-------|-------|
| **Env vars** | `IG_ACCESS_TOKEN_SP`, `IG_USER_ID_SP`, `IG_ACCESS_TOKEN_CC`, `IG_USER_ID_CC`, `IG_ACCESS_TOKEN_ND`, `IG_USER_ID_ND` |
| **Consumed by** | `scripts/video/uploaders/instagram.py` |
| **GitHub workflows** | `video-daily-publish.yml` |
| **How to obtain** | Meta Developer Portal: https://developers.facebook.com/ — Graph API > Instagram Business account |
| **Required vs optional** | Required for Instagram Reels publishing |
| **Status** | Missing — credentials not yet provisioned |
| **Detailed docs** | [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) |

### 16. Bilibili — Video publishing

| Field | Value |
|-------|-------|
| **Env vars** | `BILIBILI_SESSDATA`, `BILIBILI_CSRF` |
| **Consumed by** | `scripts/video/uploaders/bilibili.py` |
| **GitHub workflows** | None (disabled platform) |
| **How to obtain** | Browser cookie extraction — see `scripts/video/credential_setup/bilibili_cookie_setup.py` |
| **Required vs optional** | Optional — platform currently disabled |
| **Status** | Missing, platform disabled |
| **Detailed docs** | [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) |

### 17. Douyin — Video publishing

| Field | Value |
|-------|-------|
| **Env vars** | `DOUYIN_CLIENT_KEY`, `DOUYIN_CLIENT_SECRET`, `DOUYIN_ACCESS_TOKEN` |
| **Consumed by** | `scripts/video/uploaders/douyin.py` |
| **GitHub workflows** | None (disabled platform) |
| **How to obtain** | Douyin Open Platform: https://open.douyin.com/ |
| **Required vs optional** | Optional — platform currently disabled, requires ICP filing |
| **Status** | Missing, platform disabled, requires ICP filing |
| **Detailed docs** | [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) |

### 18. SerpApi — Trend checking

| Field | Value |
|-------|-------|
| **Env vars** | `SERPAPI_KEY` |
| **Consumed by** | `scripts/feeds/check_trends.py` |
| **GitHub workflows** | None |
| **How to obtain** | SerpApi dashboard: https://serpapi.com/dashboard — API Key |
| **Required vs optional** | Optional — used for trend-aware feed enrichment |
| **Status** | Missing (budget_guard limits to 245 calls/month) |

---

## Messaging channels (Keychain-based)

These are stored in macOS Keychain, not environment variables. Managed by `scripts/integrations/setup_messaging_channels_local.sh`.

| Channel | Keychain service | Required secrets | Required metadata | How to obtain |
|---------|-----------------|-----------------|-------------------|--------------|
| **LINE** | `phoenix-omega-line` | `access_token`, `channel_secret` | `user_id`, `group_id`, `channel_id` | LINE Developers Console > Messaging API |
| **WhatsApp** | `phoenix-omega-whatsapp` | `access_token`, `app_secret` | `phone_number`, `phone_number_id`, `business_account_id`, `verify_token` | Meta for Developers > WhatsApp > API Setup |
| **WeChat** | `phoenix-omega-wechat` | `app_secret` | `wechat_id`, `app_id`, `recipient_openid`, `verify_token` | WeChat Official Accounts Platform |
| **FB Messenger** | `phoenix-omega-messenger` | `page_access_token`, `app_secret` | `page_id`, `profile`, `recipient_id`, `verify_token` | Meta for Developers > Messenger > Settings |
| **iMessage** | N/A (local YAML) | None | `handle` | Your Apple ID email or phone number |

**Check missing fields:**

```bash
/bin/zsh ./scripts/integrations/report_messaging_requirements_local.sh
```

**Detailed docs:** [docs/MESSAGING_CHANNELS_LOCAL_SETUP.md](./MESSAGING_CHANNELS_LOCAL_SETUP.md)

---

## Funnel application

The funnel (`funnel/burnout_reset/`) uses these additional config vars:

| Env var | Purpose | Required |
|---------|---------|----------|
| `SECRET_KEY` | Flask session encryption | Yes (runtime) |
| `DATABASE_URL` | PostgreSQL connection (production) | Yes (production) |
| `DATABASE_PATH` | SQLite path (development) | Yes (development) |
| `BASE_URL` | App base URL for links | Yes |
| `PORT` | Server port | Optional (default: 5000) |
| `FLASK_DEBUG` | Debug mode | Optional |

**Detailed docs:** [funnel/README.md](../funnel/README.md)

---

## GitHub Actions secrets

Secrets that must be configured in GitHub repo settings for CI workflows:

| Secret name | Used by workflow(s) | Notes |
|-------------|---------------------|-------|
| `QWEN_API_KEY` | `research-pipeline-run.yml`, `pearl-news-fill-qwen.yml`, `translate-atoms-qwen-matrix.yml` | DashScope API key |
| `QWEN_BASE_URL` | Same as above | DashScope endpoint URL |
| `QWEN_MODEL` | Same as above | Model name (e.g., `qwen-max`) |
| `CLOUDFLARE_API_TOKEN` | `brand-admin-onboarding-pages.yml` | Cloudflare API token |
| `CLOUDFLARE_ACCOUNT_ID` | `brand-admin-onboarding-pages.yml` | Cloudflare account ID |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions | No manual config needed |

---

## Fallback key files (repo root, gitignored)

Some scripts support reading API keys from local files as an alternative to env vars:

| File | Service | Env var alternative |
|------|---------|-------------------|
| `claude_api_key.rtf` | Anthropic | `ANTHROPIC_API_KEY` |
| `11.txt` | ElevenLabs | `ELEVENLABS_API_KEY` |
| `cloudflare_workers_ai.txt` | Cloudflare | `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN` |
| `docs/qwen_*.txt` | Qwen | `QWEN_BASE_URL`, `QWEN_API_KEY`, `QWEN_MODEL` |

---

## Cross-references

This registry consolidates information previously scattered across:

- [docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md](./LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md) — WordPress local import
- [docs/MESSAGING_CHANNELS_LOCAL_SETUP.md](./MESSAGING_CHANNELS_LOCAL_SETUP.md) — messaging channel Keychain setup
- [docs/AGENT_QWEN_API_KEY_LANE.md](./AGENT_QWEN_API_KEY_LANE.md) — Qwen API key management
- [docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md](./VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md) — Cloudflare Workers AI
- [docs/PEARL_NEWS_GITHUB_SCHEDULING.md](./PEARL_NEWS_GITHUB_SCHEDULING.md) — Pearl News CI secrets
- [pearl_news/README.md](../pearl_news/README.md) — WordPress env vars
- [funnel/README.md](../funnel/README.md) — funnel env vars
- [config/tts/engines.yaml](../config/tts/engines.yaml) — TTS API key env refs
- [config/payouts/credentials.yaml.example](../config/payouts/credentials.yaml.example) — Plaid template
- [config/governance/github_repos_registry.yaml](../config/governance/github_repos_registry.yaml) — workflow secret expectations

- [docs/VIDEO_PLATFORM_CREDENTIAL_SETUP.md](./VIDEO_PLATFORM_CREDENTIAL_SETUP.md) — video platform OAuth/cookie credential setup

Those files remain authoritative for their domain-specific setup procedures. This registry is the single index that answers "what credentials does this repo need?"
