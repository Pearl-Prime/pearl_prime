# V1.2 Themes — en_US — Cluster C (Grief/Trauma/Healing) — Cluster Summary

**Author:** Pearl_Writer (cluster-C en_US)
**Date:** 2026-05-11
**Branch:** `agent/v1-2-cluster-c-en-us-20260512`
**Output file:** `artifacts/marketing/v1_2_themes_en_US_cluster_c.yaml`
**Authority chain:**
- `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` (BINDING)
- `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md` (PR #1051)
- `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md` (PR #1053)
- `config/manga/canonical_brand_list.yaml` (37-brand canon)

## Brand mapping (constraint doc -> canonical_brand_list.yaml)

| Constraint brand_id | Canonical brand_id | Reason | Demographic |
|---|---|---|---|
| grief_companion_iyashikei | `spiritual_ground_supernatural` | closest canonical grief+companion brand; josei; primary_topic=grief; "Devotion" notes fit grief-companion register | josei |
| trauma_recovery_shojo | `trauma_path_healing` | exact topic fit (grief + trauma_recovery + somatic_healing secondary); josei | josei |
| healing_ground | `healing_ground_healing` | **exact match** (canonical brand_id is suffixed `_healing`) | josei |
| ash_and_steel_warrior_calm | `warrior_calm_cultivation` | `warrior_calm` is the canonical brand stem; cultivation suffix; shonen demographic fits "ash_and_steel" register | shonen |
| surrender_form_warrior_calm | `stoic_edge_battle` | second warrior brand needed; seinen courage+grief+self_worth aligns with "surrender_form" register (battle-as-yielding) | seinen |

All 5 mapped brand_ids exist in `config/manga/canonical_brand_list.yaml`.

## Genre allocation (validation gate)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 7 | 6 | ✅ (per-locale floor 26 / 5 = 5.2; 7 within 5-7 cluster range) |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1-2 | ✅ |
| horror | 1 | 1 | ✅ |
| school | 0 | 0-1 | ✅ |
| other | 0 | 0-1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

**healing floor compliance:** 7 ≥ 6 (binding hard floor). PASS.

## Strict enum confirmation (no drift)

- **serial_engine** (canonical 6 only): `case_of_the_week` ×12, `location_anthology` ×4, `companion_roster` ×3, `mystery_box` ×2, `life_stage_rhythm` ×2, `power_escalation_ladder` ×2 = 25. **No invented engines.**
- **genre_family** (canonical 9 only): all 25 series use values from {healing, slice_of_life, supernatural_everyday, mystery_cozy, fantasy_adventure, romance, horror}. **No compound tags.**

## Persona distribution (target: ~55% GZ, ~10% GA, ~30% ML, ~5% GX)

| persona_archetype | count | % |
|---|---|---|
| ML-bereaved (Millennial bereaved) | 14 | 56% |
| GZ-firstjob | 7 | 28% |
| GZ-uni | 2 | 8% |
| GZ-queer | 1 | 4% |
| GX-bereaved | 1 | 4% |

**Cluster C tilt note:** Per task spec, grief/trauma/healing skews Millennial + elder-Gen-Z. Final distribution is ~40% Gen Z (10 series across GZ-firstjob/uni/queer), ~56% Millennial-bereaved, ~4% Gen X. Gen-Alpha early-bereavement is not represented in this cluster (deferred — the loss-as-engine register did not produce a Gen-Alpha-coded series that felt authentic). Documented for cross-cluster reconciliation in the final 125-series report.

## Magical-register distribution

| magical_register | count | % |
|---|---|---|
| supernatural_everyday | 11 | 44% |
| magical_realism | 6 | 24% |
| soft_fantasy | 4 | 16% |
| none | 3 | 12% |
| occult_cosmic | 1 | 4% |

Aligned with constraint advisory (supernatural_everyday dominant at ~37-44%).

## Serial-engine distribution

| serial_engine | count |
|---|---|
| case_of_the_week | 12 |
| location_anthology | 4 |
| companion_roster | 3 |
| mystery_box | 2 |
| life_stage_rhythm | 2 |
| power_escalation_ladder | 2 |

All 6 canonical engines used; case_of_the_week dominant (matches iyashikei vignette structure).

## Volume-runway median

**Median:** 150 volumes (range 100–200). Skews shorter than Cluster A pilot because grief/trauma series benefit from contained 100–150-volume arcs; longer runways (200) reserved for case-of-the-week shops (Sunday Apothecary register) with renewable client base.

## Voice register notes

A24/Ghibli + Frieren ("what is left when the journey ends"). No therapy-jargon, no Hallmark, no preachy. Loss is the engine, not the plot. Daily-life anchors land on `alt_spirituality` (grief rituals — second funerals, doulas, garden plots), `thrift_vintage` (inherited objects — recipe boxes, sabres, mirrors), `late_night_economy` (grief-insomnia gym, pet-loss hotline, ultra-running), `neurodivergent` (autistic adult grief lamp-shop — fills literature gap), `parasocial_creator` (grief podcast).

Portal mechanics cycle through: letter (×2), recipe, door (×3), ritual (×4), object (×4), mirror (×2), song (×2). All 6 portal types from the spec represented.

## Out of scope / deferred

- Gen-Alpha early-bereavement: not authored this cluster (register fit poor); flag for cross-cluster review.
- Cluster C does not include a `school` or `other` series (within 0-1 range; not floored).
- Real-world resource pointers for grief support (988, GriefShare, etc.) are not embedded in synopses; that is a marketing/publication-layer task, not an authoring task.

## Files changed

- `artifacts/marketing/v1_2_themes_en_US_cluster_c.yaml` (new, 25 series)
- `artifacts/marketing/v1_2_themes_en_US_cluster_c_summary.md` (this file)

No other files touched. No deletions.
