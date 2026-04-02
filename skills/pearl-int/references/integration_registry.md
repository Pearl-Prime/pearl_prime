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

---

## Known Integration Templates

### Anthropic (Claude API)
- **Portal:** https://console.anthropic.com/
- **Variables:** `ANTHROPIC_API_KEY`
- **Token Type:** API key (prefix: `sk-ant-`)
- **Lifespan:** Until revoked
- **Validation:** `GET /v1/messages` with `x-api-key` header
- **Status:** pending

### OpenAI
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
