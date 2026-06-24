# GHL Total Integration Handoff — Open Vessel Press / Devotion Path

**Audience:** Operator → GHL admin (48 Social or agency)  
**Date:** 2026-06-24  
**Brand / locale:** `devotion_path` / `en_US`  
**Display name:** Open Vessel Press  
**Persona:** `working_parents`  
**Teacher:** Sai Maa (`sai_ma`)

Forward **all four** admin docs listed below plus the copy/paste email in [GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt).

---

## Two halves (both required)

| Half | What | Admin doc |
|------|------|-----------|
| **A — Weekly feed** | E1–E5 Proof Loop emails; WF1–WF4; merge tags from `marketing_feed.json` | [#1–#3 below](#forward-these-4-files-to-ghl-admin) |
| **B — Funnel capture** | 15 interactive TOF pages POST JSON on email capture | [#4 below](#forward-these-4-files-to-ghl-admin) |

Skipping either half breaks the funnel: feed without webhook = no contacts; webhook without feed = no nurture URLs.

---

## Forward these 4 files to GHL admin

| # | File | Purpose |
|---|------|---------|
| **1** | [ghl/GHL_ADMIN_START_HERE.md](../ghl/GHL_ADMIN_START_HERE.md) | Story + 6-step checklist + weekly routine |
| **2** | [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) | Feed schema v3, custom fields, merge tags, timing |
| **3** | [ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md](../ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md) | Import WF1–WF4; `email_slot` branches |
| **4** | [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md) | Inbound webhook for **15** funnel pages |

**Copy/paste email:** [GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt](./GHL_ADMIN_FORWARD_EMAIL_DEVOTION_PATH_20260624.txt)

---

## GHL admin checklist (6 steps)

| Step | Action | Time |
|------|--------|------|
| 1 | Create / open GHL sub-account for **Open Vessel Press** | ~30 min |
| 2 | Import WF1–WF4 from doc #3 | ~45 min |
| 3 | Paste weekly **feed URL** (stable path; new JSON each Monday) | 2 min |
| 4 | Map 3 fields per feed item: `cta_url`, `pricing`, `content_type` | 10 min |
| 5 | Create **inbound webhook** for 15 funnel pages; return URL | ~20 min |
| 6 | Create test contact; confirm E1 fires | ~10 min |

**Send back to operator:**

```text
PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION=https://services.leadconnectorhq.com/hooks/...
Feed URL confirmed: https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/devotion_path/en_US/<week>/marketing_feed.json
Sub-account: ...
Workflows published: yes
Test contact: yes
```

---

## Feed (Part A) — 15 topics, schema v3

### Live feed URL (2026-W26)

```text
https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/devotion_path/en_US/{week}/marketing_feed.json
```

Weekly pattern (same path every Monday):

```text
https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/devotion_path/en_US/2026-W26/marketing_feed.json
```

### Builder

```bash
./scripts/marketing/setup_ghl_feed_stack.sh devotion_path en_US
# or
python3 scripts/marketing/build_marketing_feed.py --brand-id devotion_path --locale en_US
```

### Coverage (verified 2026-06-24, PR #1897)

| Metric | Expected | Actual |
|--------|----------|--------|
| Topics in feed | 15 | 15 |
| E1 items (`email_slot: e1`) | 15 | 15 |
| E5 items (`email_slot: e5`) | 15 | 15 |
| Total feed items | ~120 | **120** |

### Brand-specific feed behavior

| Item | Devotion Path rule |
|------|-------------------|
| E1 `cta_url` | `https://brand-admin-onboarding.pages.dev/free/devotion_path/{slug}/` |
| E4 book offers | `pearlprime.shop` (Sai Maa teacher SKUs) |
| Grief topic | Template only — no book CTA |
| `schema_version` | 3 |

### Item fields GHL must map

| Field | Required | Notes |
|-------|----------|-------|
| `cta_url` | **Yes** | Button link |
| `pricing` | **Yes** | `free` vs `paid` (E4 gate) |
| `content_type` | **Yes** | Template branch |
| `email_slot` | Recommended | `e1`–`e5`, `bonus_pre_story`, `post_e5` |
| `topic` | Recommended | Segmentation |
| `archetype_id` | Recommended | WF variant rules |

---

## Funnel capture (Part B) — 15 interactive pages

**Base URL:** `https://brand-admin-onboarding.pages.dev/free/devotion_path/`

| Topic | Slug | Example URL |
|-------|------|-------------|
| anxiety | anxiety-nervous-system-reset | `/free/devotion_path/anxiety-nervous-system-reset/` |
| burnout | burnout-energy-audit | `/free/devotion_path/burnout-energy-audit/` |
| grief | grief-letter-template | `/free/devotion_path/grief-letter-template/` |
| *(12 more)* | *(same slugs as Stillness)* | See [GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md](./GHL_TOTAL_INTEGRATION_HANDOFF_20260623.md) § Funnel capture |

All pages include: `data-brand-id="devotion_path"`, `data-topic`, `data-funnel-slug`, `data-ghl-webhook=""` (empty until operator injects), `PhoenixLead.captureLead()`.

### After GHL admin returns the webhook URL

```bash
URL='https://services.leadconnectorhq.com/hooks/...'
security add-generic-password -s phoenix-omega -a PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION -w "$URL" -U
export PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION="$URL"
python3 scripts/freebies/inject_ghl_webhook.py --brand-id devotion_path --require-env
# Redeploy brand-admin-onboarding Pages (merge to main or CF dashboard)
```

---

## Operator actions (Phoenix side)

| # | Action | Command / doc |
|---|--------|----------------|
| 1 | Forward 4 docs + email to GHL admin | This file |
| 2 | Confirm feed live on CDN | curl feed URL; expect `schema_version: 3`, 120 items |
| 3 | After merge #1897 | CF Pages deploys 15 `/free/devotion_path/{slug}/` paths (~2 min) |
| 4 | Inject webhook when returned | Keychain + patch block above |
| 5 | QA 3 pages (anxiety, burnout, grief) | Confirm Open Vessel Press branding + pearlprime.shop CTA |

---

## Config authority

| File | Role |
|------|------|
| `config/marketing/brand_marketing_registry.yaml` | Brand profile, `webhook_env`, `funnel_path_prefix` |
| `config/funnel/freebie_to_book_map.yaml` | 15 topics → E1–E5 feed items |
| `config/freebies/ghl_funnel_capture.yaml` | Stillness template paths (synced to brand via `sync_brand_funnel_pages.py`) |
| `config/marketing/marketing_feed_schema.yaml` | Schema v3 |

---

**Version:** 2026-06-24 · Ships with PR #1897 (`agent/ghl-funnel-devotion-waystream`).
