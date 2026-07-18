# Pearl_Int — Integration Registry

> **Canonical repo-wide credentials** (env var names, consumers, Keychain messaging, Actions secrets, cross-links) live in [`docs/INTEGRATION_CREDENTIALS_REGISTRY.md`](../../docs/INTEGRATION_CREDENTIALS_REGISTRY.md). Treat that document as the single source of truth for *what* to set. This file is Pearl_Int **operational memory**: trend feeds, SerpApi budgeting, validation notes, and channel quirks — not a second registry for secret names.

Last updated: 2026-04-02

Pearl_Int consults the canonical registry for credential names and this file for integration-specific run history and procedures.

## Registry Format

Each integration entry:
- **Service** — Name and purpose
- **Status** — `active` | `pending` | `broken` | `expired`
- **Variables** — .env variable names
- **Portal URL** — Developer console link
- **Token Type** — API key, OAuth token, bearer token, etc.
- **Lifespan** — How long the credential is valid
- **Last Validated** — Date of last successful connection test
- **Notes** — Quirks, gotchas, known issues

---

## Active Integrations

### RSS Feed Bundle (Trend + Wellness)
- **Service:** 6 RSS feeds (Trend Hunter, mindbodygreen, Tiny Buddha, Positivity Blog, Marc & Angel, Be More with Less)
- **Status:** active
- **Variables:** None (public feeds)
- **Last Validated:** 2026-03-22 (registered, pending first pull)
- **Notes:** Free, no auth. Managed via feed_sources.md. Feeds into Pearl News Qwen research + ML Editorial trend signals.

### SerpApi (Google Trends)
- **Portal:** https://serpapi.com/manage-api-key
- **Variables:** `SERPAPI_KEY`
- **Token Type:** API key (64-char hex)
- **Lifespan:** Until revoked
- **Free Tier:** 250 searches/month
- **Validation:** `GET /search?engine=google_trends&q=test&api_key=...`
- **Status:** active
- **Last Validated:** 2026-03-22 (key written to .env, 250 searches available)
- **Notes:** Budget: ~130 API calls/month (batching 5 keywords/call). 4-tier keyword system (58 keywords). Budget guard: `scripts/feeds/budget_guard.py`. Config: `config/trend_keywords/budget_config.yaml`.

### Exploding Topics (Browser Scrape)
- **Portal:** https://explodingtopics.com/topic/{slug}
- **Variables:** None (public pages, no auth)
- **Status:** active (daily scrape scheduled)
- **Schedule:** Daily at 9:04 AM via scheduled task `daily-trend-scrape`
- **Scrape Plan:** `skills/pearl-int/references/exploding_topics_scrape_plan.md`
- **Targets:** 5 confirmed Tier 1 slugs (emdr, somatic-therapy, breathwork, rosebud-ai, ketamine-therapy) + 2 category pages (health-topics, lifestyle-topics) + weekly blog roundups
- **Output:** `artifacts/feeds/daily_trend_digest_{date}.jsonl` + `daily_trend_summary_{date}.md`
- **Notes:** No free API. Using browser-based scrape of public topic pages instead. Each page shows volume + growth %. Rate limited to 15 pages/session with 3s delays.

### LINE Messaging API (48 Social Bot)
- **Service:** LINE Messaging API — push messages, file sending, chatbot, content distribution
- **Portal:** https://developers.line.biz/console/channel/2009563079
- **Account Manager:** https://manager.line.biz/account/@327mddum
- **Status:** active
- **Variables:** `LINE_CHANNEL_ID`, `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_BOT_BASIC_ID`
- **Token Type:** Channel access token (long-lived, never expires)
- **Provider:** 48 Social (provider ID: 2004980974)
- **Bot Basic ID:** @327mddum
- **Channel ID:** 2009563079
- **Lifespan:** Long-lived token — does not expire (revocable from console)
- **Free Tier:** 200 push messages/month (broadcast + push combined), unlimited reply messages
- **Validation:** `GET /v2/bot/info` with Bearer auth
- **Last Validated:** 2026-03-22 (credentials written to .env, token format verified)
- **Target Markets:** Taiwan (zh-TW), Japan (ja-JP)
- **Capabilities:**
  - Push messages to specific users (by userId)
  - Broadcast messages to all friends
  - Send text, image, video, audio, file, location, sticker messages
  - Flex Messages (rich card layouts)
  - Rich menus (persistent bottom UI)
  - Webhook receiving (incoming user messages)
  - Group chat messaging (currently disabled, can enable)
- **Notes:** Created via LINE Official Account Manager → enabled Messaging API. Auto-reply and greeting messages currently enabled (disable for bot-only mode). For file sending (CSV, MP3, MP4), use the Messaging API's file message type or upload to external URL + send as content message.

### Pearl Prime Storefront (Cloudflare Pages + D1 + R2 + KV + Snipcart-wraps-Stripe)
- **Service:** Pearl Prime book / audiobook / manga / music marketplace per `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` (active per PR #1433) + AMENDMENT-2026-06-04 (PR #1446 — 16 Q-PRP-* ratified)
- **Status:** scaffold (infra) — application code follows in Pearl_Dev ws; resources are OPERATOR-ACTION-REQUIRED per runbook
- **Cap:** `PEARL-PRIME-STOREFRONT-V1-01`
- **Subsystem:** `storefront`
- **CF account:** `b80152c319f941e6e92f928e2617a3d5` (NOT the operator's primary `626d6eb8...` per `cloudflare_pages_deploy.md` Trap 3)
- **Account authority:** use the repo's current `CLOUDFLARE_ACCOUNT_ID` secret. For the current Pages/storefront lane that resolves to `b80152c319f941e6e92f928e2617a3d5`; treat `626d6eb8...` as operator OAuth and `0fe2f067...` as older fallback/historical unless a specific lane proves otherwise.
- **CF resources (8 operator-action-required slots):**
  - **Pages project** `pearl-prime-storefront` — live at `https://pearl-prime-storefront.pages.dev` post first deploy (custom domain `pearlprime.shop` Q-PRP-DOMAIN-01)
  - **D1 database** `pearl_prime_storefront` — single instance at Phase A; read-replicas at Phase B per spec §5.2
  - **R2 bucket** `pearl-prime-storefront-assets` — `en-US/` + `ja-JP/` prefixes pre-allocated for Phase A
  - **KV namespace** `pearl_prime_storefront_session_cart` — 60-minute TTL for anonymous cart; persisted to D1 on sign-in
  - **API token** — recommend reuse existing `CLOUDFLARE_API_TOKEN` repo secret (already b80152c3-scoped); fallback `CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT` scoped variant
- **Snipcart (3 operator-action-required slots):**
  - Account email (operator-chosen; matches WordPress / brand-admin pattern)
  - `SNIPCART_API_KEY` (secret) + `SNIPCART_PUBLIC_API_KEY` (public, embedded in storefront HTML)
  - `SNIPCART_WEBHOOK_SECRET` (Cloudflare Pages env var + Keychain; quarterly rotation cadence per `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`)
- **Payment gateway:** Snipcart wraps Stripe per AMENDMENT Q-PRP-PAY-01 (Stripe Checkout direct = FALLBACK). Operator picks the Stripe account; agent never auto-executes financial-system handshakes per `CLAUDE.md`.
- **Operator runbook + resource IDs reference:** [`storefront_resource_ids.md`](./storefront_resource_ids.md) (template — populated as resources are provisioned)
- **Deploy workflow:** [`.github/workflows/pearl-prime-storefront-deploy.yml`](../../../.github/workflows/pearl-prime-storefront-deploy.yml) (mirrors `brand-admin-onboarding-pages.yml`; `wrangler-action@v3` via repo secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`; trigger: `storefront/**` or workflow file change on `main`)
- **Repo scaffold:** `storefront/{package.json,wrangler.toml,migrations/0001_init.sql,README.md,.gitignore}` (this PR)
- **Env vars registered:** `STOREFRONT_D1_ID`, `STOREFRONT_R2_BUCKET`, `STOREFRONT_KV_NAMESPACE_ID`, `CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT`, `SNIPCART_API_KEY`, `SNIPCART_PUBLIC_API_KEY`, `SNIPCART_WEBHOOK_SECRET` (see `scripts/ci/integration_env_registry.py`)
- **DO NOT run `wrangler pages deploy` from a laptop** — same Trap 1-4 contraindications as `brand-admin-onboarding`; deploy only via the CI workflow.
- **Last Validated:** 2026-06-06 (scaffold ws; no resources provisioned yet)
- **Notes:** Phase A launch surface per AMENDMENT Q-PRP-ROLLOUT-01 = en-US AND ja-JP × book AND audiobook AND manga (6 smoke combinations green = launch gate). Music SKU model = per-album + per-track + per-brand-subscription (all three at Phase B) per Q-PRP-MUSIC-SKU-01.

---

## Known Integration Templates

### Anthropic (Claude API)
- **Portal:** https://console.anthropic.com/
- **Variables:** `ANTHROPIC_API_KEY`
- **Token Type:** API key (prefix: `sk-ant-`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v1/messages` with `x-api-key` header
- **Status:** pending

### GoHighLevel (GHL) — Burnout funnel + freebie capture
- **Service:** CRM — Contacts API (burnout funnel) + Inbound Webhook (static freebie TOF)
- **Portal:** https://app.gohighlevel.com/ (API keys: Settings → API)
- **Status:** `pending` — no Keychain values for freebie webhook or Contacts API on this machine (2026-06-23)
- **Variables:**
  - `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CONTACTS_URL` — `funnel/burnout_reset/app.py`
  - `PHOENIX_GHL_FUNNEL_WEBHOOK` — `phoenix_lead.js` / flagship landings / CI `freebie-policy.yml`
- **Token Type:** API Key 2.0 (Bearer) + inbound webhook URL (opaque HTTPS endpoint)
- **Lifespan:** Until revoked / workflow deleted
- **Validation:**
  - Contacts: `POST $GHL_CONTACTS_URL` with `Version: 2021-07-28` header (burnout handoff)
  - Freebie: `python3 scripts/freebies/verify_ghl_webhook_push.py`
- **Operator runbook:** [`ghl_freebie_inbound_webhook.md`](./ghl_freebie_inbound_webhook.md)
- **Setup script:** `scripts/freebies/setup_ghl_webhook.sh`
- **Last Validated:** 2026-06-23 (smokes pass; live webhook SKIP — env unset)
- **Notes:** GitHub secret `PHOENIX_GHL_FUNNEL_WEBHOOK` not provisioned. Custom field mapping must use GHL UUIDs per `GHL_HANDBOFF.md`.

---
- **Portal:** https://platform.openai.com/api-keys
- **Variables:** `OPENAI_API_KEY`
- **Token Type:** API key (prefix: `sk-`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v1/models` with Bearer auth
- **Status:** pending

### Meta / Facebook (Messenger + Pages)
- **Portal:** https://developers.facebook.com/apps/
- **Variables:** `FB_APP_ID`, `FB_APP_SECRET`, `FB_PAGE_ACCESS_TOKEN`, `FB_VERIFY_TOKEN`, `FB_WEBHOOK_URL`
- **Token Type:** App credentials + Page access token
- **Lifespan:** App ID/Secret = permanent; Page token = 60 days (extendable to never-expire)
- **Validation:** `GET /me?access_token=...` on Graph API
- **Notes:** Page token must be extended to long-lived via token exchange endpoint. Short-lived tokens expire silently.
- **Status:** pending

### Google Cloud / APIs
- **Portal:** https://console.cloud.google.com/apis/credentials
- **Variables:** `GOOGLE_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Token Type:** API key + OAuth 2.0 client credentials
- **Lifespan:** API key = until revoked; OAuth tokens = varies
- **Validation:** Depends on specific API enabled
- **Status:** pending

### Stripe
- **Portal:** https://dashboard.stripe.com/apikeys
- **Variables:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
- **Token Type:** API keys (prefix: `sk_test_` / `sk_live_` / `pk_test_` / `pk_live_`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v1/balance` with Bearer auth
- **Status:** pending

### Twilio
- **Portal:** https://console.twilio.com/
- **Variables:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- **Token Type:** Account SID + Auth token
- **Lifespan:** Until regenerated
- **Validation:** `GET /2010-04-01/Accounts/{SID}.json`
- **Status:** pending

### SendGrid
- **Portal:** https://app.sendgrid.com/settings/api_keys
- **Variables:** `SENDGRID_API_KEY`
- **Token Type:** API key (prefix: `SG.`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v3/user/profile` with Bearer auth
- **Status:** pending

### Slack
- **Portal:** https://api.slack.com/apps
- **Variables:** `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_APP_TOKEN`
- **Token Type:** Bot token (prefix: `xoxb-`), App token (prefix: `xapp-`)
- **Lifespan:** Until revoked
- **Validation:** `POST /api/auth.test` with Bearer auth
- **Status:** pending

### Discord
- **Portal:** https://discord.com/developers/applications
- **Variables:** `DISCORD_BOT_TOKEN`, `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`
- **Token Type:** Bot token
- **Lifespan:** Until regenerated
- **Validation:** `GET /api/v10/users/@me` with Bot auth
- **Status:** pending

### Notion
- **Portal:** https://www.notion.so/my-integrations
- **Variables:** `NOTION_API_KEY`
- **Token Type:** Internal integration token (prefix: `secret_`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v1/users` with Bearer auth
- **Status:** pending

### Supabase
- **Portal:** https://supabase.com/dashboard/project/_/settings/api
- **Variables:** `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- **Token Type:** Project URL + anon/service keys
- **Lifespan:** Until regenerated
- **Validation:** `GET /rest/v1/` with apikey header
- **Status:** pending

### Vercel
- **Portal:** https://vercel.com/account/tokens
- **Variables:** `VERCEL_TOKEN`
- **Token Type:** Personal access token
- **Lifespan:** Configurable
- **Validation:** `GET /v2/user` with Bearer auth
- **Status:** pending

### GitHub (API — separate from Pearl_GitHub git ops)
- **Portal:** https://github.com/settings/tokens
- **Variables:** `GITHUB_TOKEN`
- **Token Type:** Personal access token (classic or fine-grained)
- **Lifespan:** Configurable (30/60/90 days or no expiry)
- **Validation:** `GET /user` with Bearer auth
- **Status:** pending

---

## Incident Log

(Pearl_Int logs integration failures, expired tokens, and recovery actions here)

| Date | Service | Issue | Resolution |
|------|---------|-------|------------|
| — | — | — | — |
