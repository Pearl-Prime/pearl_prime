# Q-FRB-01–08 — Freebie / GHL funnel ratification

**Date:** 2026-06-23  
**Status:** Ratified (research defaults accepted)  
**Logged:** `artifacts/coordination/operator_decisions_log.tsv` → `OPD-20260623-001`

| ID | Question | Decision |
|----|----------|----------|
| Q-FRB-01 | Archetype library size: 12 / 18 / 24? | **18** |
| Q-FRB-02 | Teacher: cosmetic overlay vs registry `teachers:` axis? | **Thin overlay YAML** |
| Q-FRB-03 | Slug: topic-first vs archetype-first? | **Topic-first public; internal `archetype_id`** |
| Q-FRB-04 | Variant B auto for caregivers + trauma topics? | **Yes** (`welcome_depth`) |
| Q-FRB-05 | PDF workbooks as TOF? | **Post-purchase only** |
| Q-FRB-06 | Unify timing on FUNNEL_EMAIL_AUTOMATION_MAP? | **Yes** (E3 +72h, E4 +120h) |
| Q-FRB-07 | Burnout TOF: keep workbook vs flip somatic-primary? | **Phase 2 flip** (workbook grandfathered until flip) |
| Q-FRB-08 | Matrix personas: 10 core vs 12? | **12 in matrix; 10 for density CI** |

**Wiring after ratification:**

- `config/freebies/archetype_assignments.yaml` — 15 funnel topics
- `config/marketing/ghl_persona_variant_map.yaml` — `tight` / `welcome_depth`
- `scripts/marketing/build_marketing_feed.py` — emits `email_slot`, `archetype_id`, `funnel_variant`
- Matrix: `artifacts/research/FREEBIE_PERSONA_TOPIC_MATRIX_20260623.tsv`
