# V1.2 Cluster A — en_US Pilot Summary

**Date:** 2026-05-11
**Authoring agent:** Pearl_Writer (Tier 1 — Claude Code, operator-present)
**Branch:** `agent/v1-2-themes-en-us-chunked-20260512`
**Output:** `artifacts/marketing/v1_2_themes_en_US_cluster_a.yaml` (25 series)
**Authority chain:**
- `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` (binding genre_family allocation)
- `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md` (PR #1051 magical_register + serial_engine)
- `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md` (PR #1053 portal-anchor + persona archetypes)
- `config/manga/canonical_brand_list.yaml` (37-brand canon)

---

## Per-brand counts

| brand_id | series | demographic | primary_topic |
|---|---|---|---|
| stillness_press | 5 | josei (flagship) | anxiety |
| sleep_restoration_iyashikei | 5 | josei (core) | sleep |
| somatic_wisdom_shojo | 5 | josei (core) | somatic_healing |
| body_memory_shojo | 5 | shojo (core) | somatic_healing |
| stabilizer_healing | 5 | josei (core) | burnout / panic-first-aid |
| **TOTAL** | **25** | | |

## Brand-id mapping table (constraint doc → canonical_brand_list.yaml)

| constraint doc id | canonical id | notes |
|---|---|---|
| `stillness_press` | `stillness_press` | exact match |
| `sleep_restoration_iyashikei` | `sleep_restoration_iyashikei` | exact match |
| `somatic_wisdom_shojo` | `somatic_wisdom_shojo` | exact match |
| `body_memory_seinen` | `body_memory_shojo` | constraint doc used `_seinen` suffix; canonical_brand_list.yaml registers the brand as `_shojo` (matches PR #1051 brand→register table line 167 `body_memory_shojo`) |
| `panic_first_aid_stabilizer` | `stabilizer_healing` | constraint doc used a thematic alias; canonical_brand_list.yaml registers the brand as `stabilizer_healing` (matches PR #1051 brand→register table line 171 `stabilizer_healing` + primary_topic burnout/panic) |

Both mappings are non-controversial — the canonical IDs are the only valid ones in the catalog plan (`artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`) and were used as-is in PR #1051 brand→register table.

## `genre_family` distribution (binding constraint validation)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4–5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1–2 | ✅ |
| horror | 1 | 1 | ✅ |
| school | 1 | 0–1 | ✅ |
| other / sport / comedy | 0 | 0–1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

All 9 rows pass. Constraint gate met.

## `persona_archetype` distribution

| persona | count | notes |
|---|---|---|
| GZ-firstjob | 11 | dominant — Gen Z 23–28 first-job urban knowledge workers |
| GZ-uni | 7 | Gen Z 18–25 university |
| GZ-queer | 4 | queer/non-binary Gen Z |
| Millennial-burnt-29 | 1 | bridge persona (body_memory inn) |
| Millennial-burnt-32 | 1 | bridge persona (stabilizer ember inn) |
| GZ-school-17 | 1 | Gen Alpha bridge (steady heart academy) |
| **TOTAL** | **25** | |

Gen Z 22/25 (88%), Millennial bridge 2/25 (8%), Gen Alpha bridge 1/25 (4%). Per PR #1053, Gen Z dominance is correct for the en_US Cluster A subset; the two Millennial entries are intentional bridge personas tied to the brand's caregiver-of-elders register (inn-keepers).

## `magical_register` distribution

| register | count | notes vs PR #1051 target (~37%/28%/8%/6%/2%/19%) |
|---|---|---|
| supernatural_everyday | 12 (48%) | over-indexed vs framework target of 37%, justified by Cluster A's natsume-of-anxiety / dream-clinic / yokai-roster brand fit (PR #1051 lines 159–171: 4 of 5 Cluster A brands prefer supernatural_everyday) |
| magical_realism | 9 (36%) | above 28% target, also justified by somatic/body-memory brand cluster |
| soft_fantasy | 3 (12%) | above 8% target — bringing in fantasy_adventure and school engines |
| occult_cosmic | 1 (4%) | within range; phantom_limbs horror |
| isekai | 0 (0%) | none — appropriate for Cluster A (constraint doc flags isekai as Cluster C/E weight) |
| none | 0 (0%) | NOT used — every Cluster A series carries magical or supernatural element, consistent with bestseller register fit |

Cluster A skews supernatural_everyday + magical_realism because the brand cluster's primary_topics (anxiety, sleep, somatic_healing, burnout) map directly to the natsume/mushishi/apothecary lineage. Other clusters (especially Cluster E: school/identity, Cluster C: trauma) will absorb more isekai/none entries to balance the full 125-series locale.

## `serial_engine` distribution

| engine | count | notes |
|---|---|---|
| case_of_the_week | 10 (40%) | high — natural fit for clinic/customer/translator/case-book patterns; PR #1051 §2.5 marks this engine HIGH-fit for anxiety/somatic/panic brands |
| companion_roster | 5 (20%) | grief/found-family register; healing-anchor brands |
| location_anthology | 5 (20%) | dream-zones, organ-systems, archives, gym chalk bags, body cartography |
| life_stage_rhythm | 2 (8%) | romance + school (slow tempo) |
| mystery_box | 2 (8%) | the logbook + phantom-limbs master door |
| power_escalation_ladder | 1 (4%) | first-aid adventurer's guild |

All 6 engines represented. case_of_the_week dominance is appropriate for Cluster A (PR #1051 brand-category map lines 141–149 assigns case_of_the_week as the primary engine for anxiety/overthinking/adhd/somatic categories).

## Volume runway

| metric | value |
|---|---|
| min runway target | 80 |
| max runway target | 200 |
| median | 150 |
| mean | 144 |
| ≥80 (V1.2 hard floor) | 25/25 (100%) ✅ |
| ≥150 (mid-bet) | 16/25 (64%) |
| ≥200 (stretch bet) | 9/25 (36%) |

All 25 series hit the V1.2 minimum 30-volume runway target and far exceed it; 9 stretch-bet series target 200+ volumes, anchored on companion_roster / case_of_the_week / location_anthology engines that empirically sustain long runs (PR #1051 §2 evidence: Natsume 30+, Apothecary 12+ ongoing, Mushishi 10 complete, Mononoke open-ended).

## Reading platform fit

| platform | count |
|---|---|
| webtoon_vertical | 21 (84%) |
| both (webtoon + traditional) | 4 (16%) |

The 4 "both" entries are the soft_fantasy / fantasy_adventure / mystery_box series (body cartographer, phantom limbs, stabilizer logbook, first-aid adventurer's guild) where traditional volume packaging adds collectibility value alongside vertical webtoon serialization.

## Notes for follow-on clusters (B / C / D / E)

- The 15 series for stillness_press / sleep_restoration_iyashikei / somatic_wisdom_shojo originally authored in `artifacts/marketing/v1_2_themes_en_US.yaml` (commit `e4b10455f`) were reproduced here with `genre_family` re-tagged to the canonical 9-value vocabulary required by `v1_2_genre_allocation_constraint_2026-05-12.md`. The original file used compound non-canonical tags (e.g. `supernatural_everyday_wellness_episodic`) that fail the constraint gate.
- Follow-on cluster authors should ALWAYS use the canonical genre_family vocabulary from the constraint doc. The compound tags can survive as `emotional_engine` or `marketing_angle` metadata, not as `genre_family`.
- Cluster A intentionally absorbs the bulk of supernatural_everyday allocation; Cluster E will need to absorb most school + isekai entries to keep the per-locale 125-series totals within the binding ranges.
