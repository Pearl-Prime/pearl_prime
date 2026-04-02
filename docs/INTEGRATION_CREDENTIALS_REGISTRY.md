# Integration Credentials Registry

**Purpose:** Single canonical reference for every external service credential in Phoenix Omega.
**Owner:** Pearl_Int / Pearl_Architect
**Last updated:** 2026-04-02 (Phase 1 + 2 scope banner; checker alignment)
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

### 1. Qwen / DashScope (Alibaba Cloud) — LLM

| Field | Value |
|-------|-------|
| **Env vars** | `QWEN_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL` |
| **Alt env vars** | `DASHSCOPE_API_KEY`, `DASHSCOPE_BASE_URL`, `DASHSCOPE_MODEL` |
| **Consumed by** | `pearl_news/pipeline/llm_expand.py`, `pearl_news/pipeline/slot_provider_qwen.py`, `scripts/research/run_research.py`, `scripts/localization/llm_client.py`, `scripts/localization/run_locale_batches.py`, `scripts/translate_atoms_all_locales_cloud.py` |
| **GitHub workflows** | `research-pipeline-run.yml`, `pearl-news-fill-qwen.yml`, `translate-atoms-qwen-matrix.yml`, `translate-bestseller-atoms.yml`, `catalog-book-pipeline.yml`, `marketing-briefs-and-proposals.yml`, `marketing_continuous.yml`, `max-quality-catalog.yml` |
| **How to obtain** | DashScope console: https://dashscope.console.aliyun.com/ — create API key under Access Key Management |
| **Required vs optional** | Required for Pearl News, translation, research pipelines |
| **Status** | Wired in CI and local scripts |
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
| `DASHSCOPE_API_KEY` | Qwen/DashScope workflows (see §1) | **Preferred** GitHub secret name for the DashScope API key; workflows read `DASHSCOPE_API_KEY` first, then fall back to `QWEN_API_KEY` |
| `QWEN_API_KEY` | Same | Legacy secret name; same key value if you do not use `DASHSCOPE_API_KEY` |
| `QWEN_BASE_URL` | Same | DashScope endpoint URL |
| `QWEN_MODEL` | Same | Model name (e.g., `qwen-max`) |
| `CLOUDFLARE_API_TOKEN` | `brand-admin-onboarding-pages.yml` | Cloudflare API token |
| `CLOUDFLARE_ACCOUNT_ID` | `brand-admin-onboarding-pages.yml` | Cloudflare account ID |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions | No manual config needed |

---

## Fallback key files (repo root, gitignored)

Some scripts support reading API keys from local files as an alternative to env vars:

| File | Service | Env var alternative |
|------|---------|-------------------|
| `claude_api_key.rtf` | Anthropic | `ANTHROPIC_API_KEY` |
| `11.txt` (repo root) or `docs/11.txt` | ElevenLabs | `ELEVENLABS_API_KEY` — `generate_briefing_narration.py` loads both paths; **never commit** real keys (see `.gitignore`) |
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
