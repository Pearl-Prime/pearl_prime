# GHL Total Integration Handoff — Stillness Press (15 topics)

**Audience:** Operator → GHL admin (48 Social or agency)  
**Date:** 2026-06-23  
**Brand / locale:** `stillness_press` / `en_US`

This is the **complete** GHL package — not webhook-only. Forward **all four** admin docs listed below plus this cover sheet.

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

**Optional reference:** [FUNNEL_EMAIL_AUTOMATION_MAP.md](../FUNNEL_EMAIL_AUTOMATION_MAP.md) (tier bundles, archetype matrix)

**Copy/paste email:** [GHL_ADMIN_FORWARD_EMAIL_20260623.txt](./GHL_ADMIN_FORWARD_EMAIL_20260623.txt)

---

## GHL admin checklist (6 steps)

| Step | Action | Time | Repo status |
|------|--------|------|-------------|
| 1 | Create / open GHL sub-account | ~30 min | Operator |
| 2 | Import WF1–WF4 from doc #3 | ~45 min | Template ready |
| 3 | Paste weekly **feed URL** (operator provides after R2/CDN) | 2 min | Builder ready — see § Feed |
| 4 | Map 3 fields per feed item: `cta_url`, `pricing`, `content_type` | 10 min | Doc #2 §3.2 |
| 5 | Create **inbound webhook** for 15 funnel pages; return URL | ~20 min | Doc #4; code live |
| 6 | (Optional) Burnout funnel Contacts API | Dev-led | [GHL_HANDBOFF.md](../../funnel/burnout_reset/GHL_HANDBOFF.md) |

**Send back to operator:**

```text
PHOENIX_GHL_FUNNEL_WEBHOOK=<REDACTED_GHL_WEBHOOK_URL>
Feed URL confirmed: https://<cdn>/pearl-prime-content/stillness_press/en_US/<week>/marketing_feed.json
Sub-account: ...
Workflows published: yes
Test contact: yes
```

---

## Feed (Part A) — 15 topics, schema v3

### Builder

```bash
./scripts/marketing/setup_ghl_feed_stack.sh stillness_press en_US
```

- Auto-discovers **all 15 topics** from `config/funnel/freebie_to_book_map.yaml` (no `--topic` flags needed).
- Emits `email_slot`, `archetype_id`, `funnel_variant` per item (schema v3).
- Validates against `config/marketing/marketing_feed_schema.yaml`.

### Feed URL shape (paste to GHL after R2 + CDN live)

```text
https://<cdn>/pearl-prime-content/stillness_press/en_US/{week}/marketing_feed.json
```

Example week: `2026-W26`. Operator sets `PEARL_PRIME_CONTENT_CDN_URL` in Keychain; Monday CI republishes same path with new JSON.

### Coverage (verified 2026-06-23)

| Metric | Expected | Actual |
|--------|----------|--------|
| Topics in feed | 15 | 15 |
| E1 items (`email_slot: e1`) | 15 | 15 |
| E5 items (`email_slot: e5`) | 15 | 15 |
| Total feed items | ~109 | 109 |

### Item fields GHL must map

| Field | Required | Notes |
|-------|----------|-------|
| `cta_url` | **Yes** | Button link |
| `pricing` | **Yes** | `free` vs `paid` (E4 gate) |
| `content_type` | **Yes** | Template branch |
| `email_slot` | Recommended | `e1`–`e5`, `bonus_pre_story`, `post_e5` |
| `topic` | Recommended | Segmentation |
| `archetype_id` | Recommended | WF variant rules |

**Webhook-only fields** (`quiz_id`, `funnel_slug`, `score_band`) come from the **inbound webhook** payload (doc #4), not from the weekly feed.

### Timing (canonical)

| Slot | Offset |
|------|--------|
| E1 | 0 |
| E2 | +24h |
| bonus_pre_story | +48h (Variant B topics only) |
| E3 | +72h |
| E4 | +120h (only if `pricing: paid` item present) |
| E5 | +288h |

---

## Funnel capture (Part B) — 15 interactive pages

Authority: `config/freebies/ghl_funnel_capture.yaml`

| Topic | Funnel slug | Quiz / tool ID |
|-------|-------------|----------------|
| anxiety | anxiety-nervous-system-reset | breath_timer_interactive |
| compassion_fatigue | compassion-fatigue-audit | capacity_assessment |
| overthinking | overthinking-thought-sorter | thought_sorter_assessment |
| financial_anxiety | financial-anxiety-check-in | financial_checkin |
| courage | courage-decision-map | decision_resistance_map |
| burnout | burnout-energy-audit | capacity_assessment |
| self_worth | self-worth-inventory | worth_inventory |
| imposter_syndrome | imposter-evidence-log | evidence_log |
| boundaries | boundaries-script-kit | script_practice |
| depression | depression-momentum-kit | micro_action_kit |
| social_anxiety | social-anxiety-toolkit | pre_event_protocol |
| financial_stress | financial-stress-audit | financial_stress_audit |
| sleep_anxiety | sleep-anxiety-wind-down | wind_down_breath |
| somatic_healing | somatic-body-scan | body_scan_timer |
| grief | grief-letter-template | grief_letter_template |

After GHL admin returns the webhook URL:

```bash
./scripts/freebies/setup_ghl_webhook.sh '<webhook-url>'
python3 scripts/freebies/verify_ghl_webhook_push.py
```

---

## Operator actions (Phoenix side)

| # | Action | Command / doc |
|---|--------|----------------|
| 1 | Forward 4 docs + email to GHL admin | This file |
| 2 | Build + validate feed locally | `setup_ghl_feed_stack.sh` |
| 3 | Publish feed to R2 (when CDN configured) | `publish_marketing_feed_r2.py` |
| 4 | Inject webhook URL when returned | `setup_ghl_webhook.sh` |
| 5 | QA 3 pages (burnout, grief, boundaries) | `smoke_freebie_capture.py` |

---

## Config authority (for engineering)

| File | Role |
|------|------|
| `config/funnel/freebie_to_book_map.yaml` | 15 topics → E1–E5 feed items |
| `config/freebies/ghl_funnel_capture.yaml` | 15 funnel pages → webhook wiring |
| `config/freebies/archetype_assignments.yaml` | `archetype_id`, E2 somatic app, variant B |
| `config/marketing/marketing_feed_schema.yaml` | Schema v3 |
| `config/marketing/ghl_email_slot_rules.yaml` | Slot defaults + WF2 priority |
| `config/marketing/ghl_persona_variant_map.yaml` | Persona → `tight` / `welcome_depth` |

---

## Still pending (not GHL admin)

| Item | Owner |
|------|-------|
| R2 bucket `pearl-prime-content` + public CDN URL | Operator / infra |
| `PHOENIX_GHL_FUNNEL_WEBHOOK` in Keychain | Operator (after admin returns URL) |
| Live GHL sub-account + workflow snapshot export | GHL admin |
| Burnout Contacts API funnel | Dev-led (optional) |

---

**Version:** 2026-06-23 · Supersedes webhook-only handoffs for 15-topic TOF.
