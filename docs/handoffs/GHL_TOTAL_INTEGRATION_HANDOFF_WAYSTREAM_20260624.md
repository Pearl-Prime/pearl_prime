# GHL Total Integration Handoff — Waystream Sanctuary

**Audience:** Operator → GHL admin (48 Social or agency)  
**Date:** 2026-06-24  
**Brand / locale:** `way_stream_sanctuary` / `en_US`  
**Display name:** Waystream Sanctuary  
**Persona:** `corporate_managers`  
**Teacher:** none (composite EPUB brand; no byline)

Forward **all four** admin docs listed below plus the copy/paste email in [GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt).

---

## Two halves (both required)

| Half | What | Admin doc |
|------|------|-----------|
| **A — Weekly feed** | E1–E5 Proof Loop emails; WF1–WF4; merge tags from `marketing_feed.json` | [#1–#3 below](#forward-these-4-files-to-ghl-admin) |
| **B — Funnel capture** | 15 interactive TOF pages POST JSON on email capture | [#4 below](#forward-these-4-files-to-ghl-admin) |

---

## Forward these 4 files to GHL admin

| # | File | Purpose |
|---|------|---------|
| **1** | [ghl/GHL_ADMIN_START_HERE.md](../ghl/GHL_ADMIN_START_HERE.md) | Story + 6-step checklist + weekly routine |
| **2** | [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) | Feed schema v3, custom fields, merge tags, timing |
| **3** | [ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md](../ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md) | Import WF1–WF4; `email_slot` branches |
| **4** | [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md) | Inbound webhook for **15** funnel pages |

**Copy/paste email:** [GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_WAYSTREAM_20260624.txt)

---

## GHL admin checklist (6 steps)

| Step | Action | Time |
|------|--------|------|
| 1 | Create / open GHL sub-account for **Waystream Sanctuary** | ~30 min |
| 2 | Import WF1–WF4 from doc #3 | ~45 min |
| 3 | Paste weekly **feed URL** | 2 min |
| 4 | Map 3 fields per feed item: `cta_url`, `pricing`, `content_type` | 10 min |
| 5 | Create **inbound webhook** for 15 funnel pages; return URL | ~20 min |
| 6 | Create test contact; confirm E1 fires | ~10 min |

**Send back to operator:**

```text
PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM=https://services.leadconnectorhq.com/hooks/...
Feed URL confirmed: https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/way_stream_sanctuary/en_US/<week>/marketing_feed.json
Sub-account: ...
Workflows published: yes
Test contact: yes
```

---

## Feed (Part A) — 15 topics, schema v3

### Live feed URL (2026-W26)

```text
https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/way_stream_sanctuary/en_US/{week}/marketing_feed.json
```

Example:

```text
https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/way_stream_sanctuary/en_US/2026-W26/marketing_feed.json
```

### Builder

```bash
./scripts/marketing/setup_ghl_feed_stack.sh way_stream_sanctuary en_US
# or
python3 scripts/marketing/build_marketing_feed.py --brand-id way_stream_sanctuary --locale en_US
```

### Coverage (verified 2026-06-24, PR #1897)

| Metric | Expected | Actual |
|--------|----------|--------|
| Topics in feed | 15 | 15 |
| E1 items | 15 | 15 |
| E5 items | 15 | 15 |
| Total feed items | ~109 | **109** |

### Brand-specific feed behavior

| Item | Waystream rule |
|------|----------------|
| E1 `cta_url` | `https://phoenix-brand-admin.pages.dev/free/way_stream_sanctuary/{slug}/` |
| E4 book offers | `/download/...` proxy URLs (not pearlprime.shop) |
| Grief topic | Template only — no book CTA |
| Branding | No Stillness Press, Sai Maa, or `_ahjan` references |
| `schema_version` | 3 |

---

## Funnel capture (Part B) — 15 interactive pages

**Base URL:** `https://phoenix-brand-admin.pages.dev/free/way_stream_sanctuary/`

| Topic | Slug | Example URL |
|-------|------|-------------|
| anxiety | anxiety-nervous-system-reset | `/free/way_stream_sanctuary/anxiety-nervous-system-reset/` |
| burnout | burnout-energy-audit | `/free/way_stream_sanctuary/burnout-energy-audit/` |
| grief | grief-letter-template | `/free/way_stream_sanctuary/grief-letter-template/` |
| *(12 more)* | *(same slugs as Stillness)* | See [GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md](./GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md) § Funnel capture |

All pages include: `data-brand-id="way_stream_sanctuary"`, `data-topic`, `data-funnel-slug`, `data-ghl-webhook=""` (empty until operator injects), `PhoenixLead.captureLead()`.

### After GHL admin returns the webhook URL

```bash
URL='https://services.leadconnectorhq.com/hooks/...'
security add-generic-password -s phoenix-omega -a PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM -w "$URL" -U
export PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM="$URL"
python3 scripts/freebies/inject_ghl_webhook.py --brand-id way_stream_sanctuary --require-env
# Redeploy brand-admin-onboarding Pages (merge to main or CF dashboard)
```

---

## Operator actions (Phoenix side)

| # | Action | Command / doc |
|---|--------|----------------|
| 1 | Forward 4 docs + email to GHL admin | This file |
| 2 | Confirm feed live on CDN | curl feed URL; expect `schema_version: 3`, 109 items |
| 3 | After merge #1897 | CF Pages deploys 15 `/free/way_stream_sanctuary/{slug}/` paths |
| 4 | Inject webhook when returned | Keychain + patch block above |
| 5 | QA 3 pages (anxiety, burnout, grief) | Waystream branding + `/download/...` CTA on book topics |

---

## Config authority

| File | Role |
|------|------|
| `config/marketing/brand_marketing_registry.yaml` | Brand profile, `webhook_env`, `shop_url_source: brand_catalog` |
| `config/funnel/freebie_to_book_map.yaml` | 15 topics → E1–E5 feed items |
| `scripts/marketing/sync_brand_funnel_pages.py` | Generates brand pages from Stillness templates |

---

**Version:** 2026-06-24 · Ships with PR #1897 (`agent/ghl-funnel-devotion-waystream`).
