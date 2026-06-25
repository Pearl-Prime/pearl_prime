# GHL Agency Scale Playbook — 48 Social / GHL Admin

**Audience:** GHL agency admin (48 Social)  
**Operator:** Forward this + the 4 canonical admin docs (see bottom)  
**Pilot (now):** 3 brands × `en_US` — Stillness Press, Devotion Path, Waystream Sanctuary  
**Scale (later):** up to **37 brands × 14 locales** — same template, bulk deploy (not 518 manual setups)

---

## Super simple — what you do

### Pilot (3 brands today)

Do this **once per brand** (3 sub-accounts):

1. **Paste feed URL** — GHL reads weekly emails from our JSON file (same URL every week; we replace the file on Mondays).
2. **Import WF1–WF4** — automated E1–E5 email sequence (attached template).
3. **Map 3 feed fields** — `cta_url`, `pricing`, `content_type`.
4. **Create one Inbound Webhook** — catches signups from 15 free-tool pages per brand.
5. **Map webhook JSON fields** — `email`, `first_name`, `quiz_id`, `topic`, `funnel_slug`, `score`, `score_band`, `tags`.
6. **Publish + test** — submit a test email on a live tool page; contact appears in GHL.
7. **Send us the webhook URL** — we plug it into the live pages.

**That’s it for weekly ops:** Pearl Prime updates the feed every Monday. You do **not** re-type links or rewrite emails.

### Full scale (37 × 14 — do NOT repeat the pilot 518 times)

1. **Perfect one sub-account** (Stillness `en_US` pilot) → save as **GHL Snapshot**.
2. **Bulk-create** sub-accounts from our location manifest CSV (see `ghl_location_manifest.example.tsv`).
3. **Push Snapshot** to all new locations.
4. **Bulk-fill** per location: `feed_url`, `funnel_base_url` (and webhook URL if not cloned).
5. **Weekly:** nothing — workflows poll the same feed URL path.

---

## Two jobs per brand (plain English)

| Job | What it does | You do once |
|-----|----------------|-------------|
| **A — Weekly emails (Proof Loop)** | Someone signs up → GHL sends E1–E5 nurture + offer emails using our feed | Import WF1–WF4, paste feed URL, map 3 fields |
| **B — Free-tool capture (webhook)** | 15 interactive pages POST email + quiz data when user opts in | One Inbound Webhook per brand, map JSON fields |

**You do not:** build landing pages, write email copy from scratch, or update shop links weekly.

---

## Location manifest CSV (bulk scale)

**File:** `docs/handoffs/ghl_location_manifest.example.tsv` (tab-separated for GHL import)

### Column spec

| Column | Required | Example | Notes |
|--------|----------|---------|-------|
| `location_name` | Yes | `Stillness Press (en_US)` | GHL sub-account display name |
| `brand_id` | Yes | `stillness_press` | Phoenix registry id |
| `locale` | Yes | `en_US` | BCP-47 locale |
| `display_name` | Yes | `Stillness Press` | Shown on free-tool pages |
| `feed_url` | Yes | `https://pub-….r2.dev/pearl-prime-content/stillness_press/en_US/2026-W26/marketing_feed.json` | Paste in GHL; path stable, JSON updates Mondays |
| `feed_url_pattern` | Optional | `…/pearl-prime-content/{brand_id}/{locale}/{week}/marketing_feed.json` | For docs / formula columns |
| `funnel_base_url` | Yes | `https://brand-admin-onboarding.pages.dev/free/` | Stillness: no brand prefix |
| `funnel_base_url` | Yes | `https://brand-admin-onboarding.pages.dev/free/devotion_path/` | Devotion / Waystream: include prefix |
| `webhook_env` | Yes | `PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS` | Operator stores returned URL under this name |
| `webhook_url` | After setup | `https://services.leadconnectorhq.com/hooks/…` | **Filled by GHL admin** after step 4; returned to operator |
| `shop_cta_style` | Optional | `pearlprime` or `download_proxy` | Waystream uses `/download/` not pearlprime.shop |
| `rollout_phase` | Optional | `pilot` | `pilot` → `wave2` → `all` |
| `ghl_enabled` | Optional | `true` | Skip rows where Phoenix feed not ready |

### Feed URL formula

```text
{cdn_base}/pearl-prime-content/{brand_id}/{locale}/{iso_week}/marketing_feed.json
```

**CDN base (pilot):** `https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev`  
**Week:** ISO week e.g. `2026-W26` — same path each Monday; Phoenix replaces file in place.

### Funnel base URL rules

| `brand_id` | `funnel_path_prefix` | Base URL |
|------------|----------------------|----------|
| `stillness_press` | (none) | `…/free/{tool-slug}/` |
| `devotion_path` | `devotion_path` | `…/free/devotion_path/{tool-slug}/` |
| `way_stream_sanctuary` | `way_stream_sanctuary` | `…/free/way_stream_sanctuary/{tool-slug}/` |

**15 tool slugs (same all brands):**  
`anxiety-nervous-system-reset`, `burnout-energy-audit`, `self-worth-inventory`, `imposter-evidence-log`, `boundaries-script-kit`, `depression-momentum-kit`, `courage-decision-map`, `overthinking-thought-sorter`, `compassion-fatigue-audit`, `social-anxiety-toolkit`, `financial-anxiety-check-in`, `financial-stress-audit`, `sleep-anxiety-wind-down`, `somatic-body-scan`, `grief-letter-template`

---

## Pilot feed URLs (paste in GHL now)

| Brand | Feed URL |
|-------|----------|
| Stillness Press | `https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/stillness_press/en_US/2026-W26/marketing_feed.json` |
| Open Vessel Press (Devotion) | `https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/devotion_path/en_US/2026-W26/marketing_feed.json` |
| Waystream Sanctuary | `https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/way_stream_sanctuary/en_US/2026-W26/marketing_feed.json` |

---

## What admin sends back (per brand)

```text
PHOENIX_GHL_FUNNEL_WEBHOOK_<BRAND>=https://services.leadconnectorhq.com/hooks/...
Feed URL confirmed: yes
Workflows published: yes
Test contact created: yes
```

| Brand | Webhook env var (operator Keychain) |
|-------|-------------------------------------|
| Stillness | `PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS` |
| Devotion Path | `PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION` |
| Waystream | `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM` |

---

## Attachments (read once — same for all brands)

| File | Why |
|------|-----|
| [GHL_ADMIN_START_HERE.md](../ghl/GHL_ADMIN_START_HERE.md) | Start here — overview + checklist |
| [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) | Feed JSON fields, timing E1→E5, merge tags |
| [PROOF_LOOP_WORKFLOW_TEMPLATE.md](../ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md) | Import WF1–WF4 |
| [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md) | Inbound webhook + field mapping |

**Operator index:** [GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md](./GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md)

---

## Phoenix side (not GHL admin)

- Builds/publishes feeds: `scripts/marketing/build_all_marketing_feeds.py`, `publish_marketing_feed_r2.py`
- Generates funnel pages: `scripts/marketing/sync_brand_funnel_pages.py`
- Registry: `config/marketing/brand_marketing_registry.yaml`
- Injects webhook after admin reply: `scripts/freebies/setup_ghl_webhook.sh` or `inject_ghl_webhook.py --brand-id <id>`

**Version:** 2026-06-25
