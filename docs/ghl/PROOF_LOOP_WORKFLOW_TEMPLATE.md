# Proof Loop — GHL Workflow Template (WF1–WF4)

**Import this into GoHighLevel.** Pair with [GHL_INTEGRATION_GUIDE.md](../GHL_INTEGRATION_GUIDE.md) and weekly `marketing_feed.json`.

---

## WF1 — Proof Loop (main spine)

**Trigger:** Contact tag `freebie_captured` OR inbound webhook from quiz (tag `source_freebie_quiz`).

### Steps

| # | Wait | Action | Merge tags / feed |
|---|------|--------|-------------------|
| 1 | 0 | Send email **E1** | `{{item.e1.cta_url}}`, `{{item.e1.title}}` from feed slot `e1` |
| 2 | 24h | Send email **E2** | Feed slot `e2` |
| 3 | 24h | **Branch:** `funnel_variant` = `welcome_depth`? → go to WF2 step 1; else continue | |
| 4 | 24h | Send email **E3** (story) | Feed slot `e3` — **no shop link** |
| 5 | 48h | **If/else:** feed has item where `email_slot=e4` AND `pricing=paid` | |
| 5a | — | Send email **E4** (offer) | `{{item.e4.cta_url}}` → pearlprime.shop |
| 5b | — | Else skip E4 | |
| 6 | 168h | Send email **E5** (series) | Feed slot `e5` (optional) |

**Copy templates:** Paste bodies from [proof_loop_sequence.md](../email_sequences/proof_loop_sequence.md); replace placeholders with GHL custom values / feed merge.

### Merge tags (minimum)

| Tag | Source |
|-----|--------|
| `{{contact.first_name}}` | Contact |
| `{{contact.email}}` | Contact |
| `{{custom_values.topic}}` | Custom field |
| `{{feed.e1.cta_url}}` | Feed item `email_slot=e1` |
| `{{feed.e4.cta_url}}` | Feed item `email_slot=e4` |

---

## WF2 — Tier bonus drip (optional free content)

**Trigger:** Contact completed WF1 step 3 (before E3 story) OR tag `bonus_drip_start`.

**Purpose:** Send one extra free asset (guided audio or assessment) from feed `email_slot=bonus_pre_story`. Does **not** replace E1/E2.

| # | Wait | Action |
|---|------|--------|
| 1 | 0 | Send bonus email | Feed `bonus_pre_story` item |
| 2 | — | Return to WF1 step 4 (E3) |

**Rule:** `guided_audio` never goes to E1 — only `bonus_pre_story` (research default).

---

## WF3 — Series upsell

**Trigger:** Tag `buyer` OR completed WF1 E5 without purchase.

| # | Wait | Action |
|---|------|--------|
| 1 | 0 | Email: Book 2 recommendation | `freebie_to_book_map.yaml` / feed `e5` |
| 2 | 72h | Email: Book 3 / bundle |
| 3 | 72h | Email: Last chance / social proof |

---

## WF4 — Re-engagement

**Trigger:** No email open 90 days.

| # | Wait | Action |
|---|------|--------|
| 1 | 0 | “Still here?” + one free tool link |
| 2 | 72h | Reply-based branch (interested / not) |
| 3 | 72h | Remove from active nurture OR restart WF1 |

---

## Variant branch (tight vs welcome_depth)

| Persona / topic | Variant |
|-----------------|---------|
| corporate_managers, gen_z_professionals | `tight` |
| healthcare_rns, first_responders, working_parents | `welcome_depth` |
| Topics: grief, compassion_fatigue, somatic_healing, depression | `welcome_depth` |

Map: `config/marketing/ghl_persona_variant_map.yaml`.

---

## Publish checklist

- [ ] WF1–WF4 created and **Published**
- [ ] Test contact receives E1 with correct `cta_url`
- [ ] E4 suppressed when feed has no `pricing: paid` item
- [ ] Quiz webhook creates contact + tags (see [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md))
- [ ] Unsubscribe / CAN-SPAM footer on all emails

---

**Version:** 2026-06-23
