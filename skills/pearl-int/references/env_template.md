# Pearl_Int — .env Template Reference

> **Preferred local path (2026-04-03):** All keys are now in macOS Keychain under service `phoenix-omega`. Load them with the shell snippet in `CLAUDE.md` or `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` § "Load all keys in your shell". The `.env` template below is for CI/Docker environments that can't use Keychain.

This file defines the canonical .env structure for Phoenix Omega.
Pearl_Int uses this as the source of truth when creating or updating .env files.

## .env Rules

1. `.env` lives at repo root — NEVER committed to git
2. `.env.example` mirrors the structure with empty values — IS committed
3. Every variable belongs to a service section with a header comment
4. No duplicate variable names
5. Pearl_Int timestamps the file header on every modification
6. Values with special characters must be quoted: `VAR="value with spaces"`
7. No trailing whitespace after `=`
8. Empty values use just `=` with nothing after: `VAR=`

## Canonical Template

```env
# ═══════════════════════════════════════════════════════════
# PHOENIX OMEGA — ENVIRONMENT VARIABLES
# Managed by Pearl_Int | Owner: Nihala (Ma'at)
# Last updated: YYYY-MM-DDTHH:MM:SSZ
# ═══════════════════════════════════════════════════════════

# ── APP CONFIG ─────────────────────────────────────────────
NODE_ENV=development
APP_PORT=3000
APP_URL=http://localhost:3000

# ── ANTHROPIC (Claude API) ────────────────────────────────
ANTHROPIC_API_KEY=

# ── OPENAI ─────────────────────────────────────────────────
OPENAI_API_KEY=

# ── META / FACEBOOK ────────────────────────────────────────
FB_APP_ID=
FB_APP_SECRET=
FB_PAGE_ACCESS_TOKEN=
FB_VERIFY_TOKEN=
FB_WEBHOOK_URL=

# ── GOOGLE ─────────────────────────────────────────────────
GOOGLE_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ── STRIPE ─────────────────────────────────────────────────
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# ── TWILIO ─────────────────────────────────────────────────
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# ── SENDGRID ───────────────────────────────────────────────
SENDGRID_API_KEY=

# ── GOHIGHLEVEL (GHL) ─────────────────────────────────────
GHL_API_KEY=
GHL_LOCATION_ID=
GHL_CONTACTS_URL=https://services.leadconnectorhq.com/contacts/
PHOENIX_GHL_FUNNEL_WEBHOOK=

# ── SLACK ──────────────────────────────────────────────────
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_APP_TOKEN=

# ── DISCORD ────────────────────────────────────────────────
DISCORD_BOT_TOKEN=
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=

# ── NOTION ─────────────────────────────────────────────────
NOTION_API_KEY=

# ── SUPABASE ───────────────────────────────────────────────
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# ── GITHUB (API tokens, not git auth) ─────────────────────
GITHUB_TOKEN=

# ── VERCEL ─────────────────────────────────────────────────
VERCEL_TOKEN=

# ── SERPAPI (Google Trends — free 250/month) ───────────────
SERPAPI_KEY=

# ── EXPLODING TOPICS (no API — public page scrape via browser)
# No key needed. See skills/pearl-int/references/exploding_topics_scrape_plan.md

# ── RSS / FEEDS (config only, no credentials) ─────────────
RSS_POLL_INTERVAL_MINUTES=30
RSS_MAX_ENTRIES_PER_FEED=50
TREND_HEAT_THRESHOLD=0.6
TREND_FAST_PUBLISH_THRESHOLD=0.8
```

## Validation Prefixes

Pearl_Int checks these known prefixes to catch obvious paste errors:

| Variable | Expected Prefix | Min Length |
|----------|----------------|-----------|
| ANTHROPIC_API_KEY | `sk-ant-` | 40 |
| OPENAI_API_KEY | `sk-` | 40 |
| FB_APP_ID | (numeric) | 10 |
| FB_APP_SECRET | (hex) | 20 |
| FB_PAGE_ACCESS_TOKEN | `EAA` | 50 |
| STRIPE_SECRET_KEY | `sk_test_` or `sk_live_` | 20 |
| STRIPE_PUBLISHABLE_KEY | `pk_test_` or `pk_live_` | 20 |
| TWILIO_ACCOUNT_SID | `AC` | 30 |
| SLACK_BOT_TOKEN | `xoxb-` | 30 |
| SLACK_APP_TOKEN | `xapp-` | 30 |
| DISCORD_BOT_TOKEN | (base64-ish) | 50 |
| NOTION_API_KEY | `secret_` | 30 |
| SENDGRID_API_KEY | `SG.` | 30 |
| SUPABASE_ANON_KEY | `eyJ` (JWT) | 100 |
