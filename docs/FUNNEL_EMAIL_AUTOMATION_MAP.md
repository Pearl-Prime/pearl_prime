# Funnel Email Automation Map

**Audience:** GHL admin + marketing ops.  
**Simple version:** [ghl/GHL_ADMIN_START_HERE.md](./ghl/GHL_ADMIN_START_HERE.md).  
**Import steps:** [ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md](./ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md).

---

## Spine (do not change order)

**Exercise → Exercise → Story → Offer → Series** (Proof Loop E1–E5).

---

## Pre-offer variants

| Variant | Code | When | Emails before offer |
|---------|------|------|---------------------|
| **Tight Proof Loop** | `tight` | Default; executives; Gen Z | E1 + E2 → E3 |
| **Welcome & Depth** | `welcome_depth` | Caregivers; healthcare; grief; compassion fatigue; somatic | E1 + E2 + **bonus** → E3 |

Config: `config/marketing/ghl_persona_variant_map.yaml`.

---

## Tier bundle → email slots

Authority: `config/freebies/tier_bundles.yaml`, `config/freebies/nurture_asset_mix.yaml`.

| Slot | Timing | What to send | Tier source |
|------|--------|--------------|-------------|
| E1 | T0 | Lead magnet (somatic tool or assessment) | TOF capture |
| E2 | +24h | Second exercise | `exercise_pairs` |
| bonus_pre_story | +48h | One audio or assessment | **Better** tier — WF2 only |
| E3 | +72h | Story — no pitch | Story bank |
| E4 | +120h | Paid offer → pearlprime.shop | Feed `pricing: paid` |
| E5 | +288h | Series upsell | `freebie_to_book_map.yaml` |
| Post-E5 weekly | +336h+ | Remaining Better/Best PDFs/tools | WF2 drip |
| Post-purchase | `buyer` tag | Good tier (Listener's Kit) | After shop purchase |

**PDF rule:** Checklists OK pre-purchase (≤35% of nurture slots). **Workbooks only after `buyer` tag.**

---

## TOF format priority (lead magnet)

1. Somatic HTML tool (best conversion)
2. Guided audio
3. Assessment / quiz
4. Workbook PDF — **not** for TOF (post-purchase)
5. Checklist PDF — sparingly

---

## Four GHL workflows

| WF | Name | Trigger |
|----|------|---------|
| WF1 | Proof Loop | `freebie_captured` |
| WF2 | Tier bonus drip | Before E3 (variant B) |
| WF3 | Series upsell | `buyer` or post-E5 |
| WF4 | Re-engagement | 90d no open |

---

## Feed schema v3 fields (for builders)

| Field | Purpose |
|-------|---------|
| `email_slot` | e1, e2, bonus_pre_story, e3, e4, e5 |
| `archetype_id` | Maps to freebie archetype |
| `funnel_variant` | tight \| welcome_depth |
| `pricing` | free \| paid |
| `content_type` | Template branch |
| `cta_url` | Primary link |

Schema: `config/marketing/marketing_feed_schema.yaml`.

---

## Feed builder (automated)

Phoenix emits schema v3 fields via:

```bash
python3 scripts/marketing/build_marketing_feed.py --brand-id stillness_press --locale en_US
python3 scripts/marketing/publish_marketing_feed_r2.py --brand-id stillness_press --dry-run
```

Weekly CI: `.github/workflows/weekly-marketing-feed-publish.yml` (Mondays 06:00 UTC).

---

## Still manual / future

- Default `funnel_variant` per hub in `funnel_proof_loop.yaml` (feed uses persona/topic map today)
- Formal research artifact: audio vs PDF vs quiz conversion rates (chat research → doc)

---

## Authority cross-links

| Doc | Role |
|-----|------|
| [FREEBIE_MARKETING_PLAN.md](./FREEBIE_MARKETING_PLAN.md) | Proof Loop psychology |
| [email_sequences/proof_loop_sequence.md](./email_sequences/proof_loop_sequence.md) | Canonical copy |
| [GHL_INTEGRATION_GUIDE.md](./GHL_INTEGRATION_GUIDE.md) | Feed + setup |
| [48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md](./48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md) | 48 Social context |

---

**Version:** 2026-06-23
