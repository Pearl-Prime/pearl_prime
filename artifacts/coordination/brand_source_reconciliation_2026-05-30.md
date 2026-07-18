# Brand Source Reconciliation — 2026-05-30

Generated: 2026-05-30
Agent: Pearl_PM
Project: PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1

Planning reconciliation only. **Do not edit configs from this doc** — operator decisions required.

## Summary

- Path X manga canon: **37** brands (`config/manga/canonical_brand_list.yaml`)
- `brand_registry.yaml`: **26** entries (**2** overlap with Path X)
- `manga_brand_series_plan.yaml`: **13** explicit series-plan keys
- `series_plans_en_us/`: **8** prose brands (**275** files)
- `series_plan_alias` entries: **9**
- Mismatch rows flagged: **62**

## Mismatch Register

| ID | Type | Canonical ID | Other ID | Sources | Proposed Canonical | Trust SoT | Notes |
|----|------|--------------|----------|---------|-------------------|-----------|-------|
| M001 | slug_alias | `body_memory_shojo` | `body_memory` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `body_memory_shojo` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps body_memory_shojo → body_memory; BR-CANON-02 accepts variant ids |
| M002 | slug_alias | `bright_presence_tw_seinen` | `bright_presence_tw` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `bright_presence_tw_seinen` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps bright_presence_tw_seinen → bright_presence_tw; BR-CANON-02 accepts variant ids |
| M003 | slug_alias | `devotion_path_shonen` | `devotion_path` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `devotion_path_shonen` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps devotion_path_shonen → devotion_path; BR-CANON-02 accepts variant ids |
| M004 | slug_alias | `heart_balance_shojo` | `heart_balance` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `heart_balance_shojo` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps heart_balance_shojo → heart_balance; BR-CANON-02 accepts variant ids |
| M005 | slug_alias | `relational_calm_iyashikei` | `relational_calm` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `relational_calm_iyashikei` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps relational_calm_iyashikei → relational_calm; BR-CANON-02 accepts variant ids |
| M006 | slug_alias | `sleep_restoration_iyashikei` | `sleep_restoration` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `sleep_restoration_iyashikei` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps sleep_restoration_iyashikei → sleep_restoration; BR-CANON-02 accepts variant ids |
| M007 | slug_alias | `solar_return_isekai` | `solar_return` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `solar_return_isekai` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps solar_return_isekai → solar_return; BR-CANON-02 accepts variant ids |
| M008 | slug_alias | `somatic_wisdom_shojo` | `somatic_wisdom` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `somatic_wisdom_shojo` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps somatic_wisdom_shojo → somatic_wisdom; BR-CANON-02 accepts variant ids |
| M009 | slug_alias | `warrior_calm_cultivation` | `warrior_calm` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml | `warrior_calm_cultivation` | config/manga/canonical_brand_list.yaml (Path X frozen) | series_plan_alias maps warrior_calm_cultivation → warrior_calm; BR-CANON-02 accepts variant ids |
| M010 | missing_series_plan | `adhd_forge_mystery` | `` | manga_brand_series_plan.yaml | `adhd_forge_mystery` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M011 | missing_series_plan | `bio_flow_healing` | `` | manga_brand_series_plan.yaml | `bio_flow_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M012 | missing_series_plan | `calm_student_school` | `` | manga_brand_series_plan.yaml | `calm_student_school` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M013 | missing_series_plan | `career_lift_workplace` | `` | manga_brand_series_plan.yaml | `career_lift_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M014 | missing_series_plan | `confidence_core_romance` | `` | manga_brand_series_plan.yaml | `confidence_core_romance` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M015 | missing_series_plan | `creative_unfold_social` | `` | manga_brand_series_plan.yaml | `creative_unfold_social` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M016 | missing_series_plan | `executive_calm_workplace` | `` | manga_brand_series_plan.yaml | `executive_calm_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M017 | missing_series_plan | `focus_sprint_workplace` | `` | manga_brand_series_plan.yaml | `focus_sprint_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M018 | missing_series_plan | `gentle_growth_healing` | `` | manga_brand_series_plan.yaml | `gentle_growth_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M019 | missing_series_plan | `healing_ground_healing` | `` | manga_brand_series_plan.yaml | `healing_ground_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M020 | missing_series_plan | `high_performer_workplace` | `` | manga_brand_series_plan.yaml | `high_performer_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M021 | missing_series_plan | `hormone_reset_healing` | `` | manga_brand_series_plan.yaml | `hormone_reset_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M022 | missing_series_plan | `legacy_builder_memoir` | `` | manga_brand_series_plan.yaml | `legacy_builder_memoir` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M023 | missing_series_plan | `longevity_lab_healing` | `` | manga_brand_series_plan.yaml | `longevity_lab_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M024 | missing_series_plan | `minimal_mind_healing` | `` | manga_brand_series_plan.yaml | `minimal_mind_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M025 | missing_series_plan | `morning_momentum_workplace` | `` | manga_brand_series_plan.yaml | `morning_momentum_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M026 | missing_series_plan | `night_reset_healing` | `` | manga_brand_series_plan.yaml | `night_reset_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M027 | missing_series_plan | `optimizer_workplace` | `` | manga_brand_series_plan.yaml | `optimizer_workplace` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M028 | missing_series_plan | `relationship_clarity_romance` | `` | manga_brand_series_plan.yaml | `relationship_clarity_romance` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M029 | missing_series_plan | `resilient_parent_social` | `` | manga_brand_series_plan.yaml | `resilient_parent_social` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M030 | missing_series_plan | `spiritual_ground_supernatural` | `` | manga_brand_series_plan.yaml | `spiritual_ground_supernatural` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M031 | missing_series_plan | `stabilizer_healing` | `` | manga_brand_series_plan.yaml | `stabilizer_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M032 | missing_series_plan | `stoic_edge_battle` | `` | manga_brand_series_plan.yaml | `stoic_edge_battle` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M033 | missing_series_plan | `trauma_path_healing` | `` | manga_brand_series_plan.yaml | `trauma_path_healing` | config/manga/canonical_brand_list.yaml; inherit tier defaults via manga_canon_planned_volumes.yaml | No explicit entry in manga_brand_series_plan.yaml; tier baselines only |
| M034 | cross_registry_overlap | `cognitive_clarity` | `cognitive_clarity` | brand_registry.yaml + canonical_brand_list.yaml | `cognitive_clarity` | Both registries; Path X manga canon for manga surfaces; brand_registry for Pearl_Prime book pipeline | Intentional overlap for anchor brands (stillness_press, cognitive_clarity) |
| M035 | cross_registry_overlap | `stillness_press` | `stillness_press` | brand_registry.yaml + canonical_brand_list.yaml | `stillness_press` | Both registries; Path X manga canon for manga surfaces; brand_registry for Pearl_Prime book pipeline | Intentional overlap for anchor brands (stillness_press, cognitive_clarity) |
| M036 | book_registry_only | `gen_z_grounding_cn` | `` | brand_registry.yaml only | `gen_z_grounding_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M037 | book_registry_only | `gen_z_grounding_hk` | `` | brand_registry.yaml only | `gen_z_grounding_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M038 | book_registry_only | `gen_z_grounding_sg` | `` | brand_registry.yaml only | `gen_z_grounding_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M039 | book_registry_only | `gen_z_grounding_tw` | `` | brand_registry.yaml only | `gen_z_grounding_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M040 | book_registry_only | `grief_companion_cn` | `` | brand_registry.yaml only | `grief_companion_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M041 | book_registry_only | `grief_companion_hk` | `` | brand_registry.yaml only | `grief_companion_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M042 | book_registry_only | `grief_companion_sg` | `` | brand_registry.yaml only | `grief_companion_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M043 | book_registry_only | `grief_companion_tw` | `` | brand_registry.yaml only | `grief_companion_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M044 | book_registry_only | `inner_security_cn` | `` | brand_registry.yaml only | `inner_security_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M045 | book_registry_only | `inner_security_hk` | `` | brand_registry.yaml only | `inner_security_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M046 | book_registry_only | `inner_security_sg` | `` | brand_registry.yaml only | `inner_security_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M047 | book_registry_only | `inner_security_tw` | `` | brand_registry.yaml only | `inner_security_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M048 | book_registry_only | `panic_first_aid_cn` | `` | brand_registry.yaml only | `panic_first_aid_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M049 | book_registry_only | `panic_first_aid_hk` | `` | brand_registry.yaml only | `panic_first_aid_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M050 | book_registry_only | `panic_first_aid_sg` | `` | brand_registry.yaml only | `panic_first_aid_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M051 | book_registry_only | `panic_first_aid_tw` | `` | brand_registry.yaml only | `panic_first_aid_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M052 | book_registry_only | `sleep_repair_cn` | `` | brand_registry.yaml only | `sleep_repair_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M053 | book_registry_only | `sleep_repair_hk` | `` | brand_registry.yaml only | `sleep_repair_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M054 | book_registry_only | `sleep_repair_sg` | `` | brand_registry.yaml only | `sleep_repair_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M055 | book_registry_only | `sleep_repair_tw` | `` | brand_registry.yaml only | `sleep_repair_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M056 | book_registry_only | `stabilizer_cn` | `` | brand_registry.yaml only | `stabilizer_cn` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M057 | book_registry_only | `stabilizer_hk` | `` | brand_registry.yaml only | `stabilizer_hk` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M058 | book_registry_only | `stabilizer_sg` | `` | brand_registry.yaml only | `stabilizer_sg` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M059 | book_registry_only | `stabilizer_tw` | `` | brand_registry.yaml only | `stabilizer_tw` | config/brand_registry.yaml (Pearl_Prime locale-specific book brands) | Not in Path X 37; excluded from matrix rows |
| M060 | name_drift | `somatic_wisdom_shojo` | `somatic_wisdom` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml / series_plans_en_us | `somatic_wisdom_shojo` | config/manga/canonical_brand_list.yaml for brand_id; alias table in manga_canon_planned_volumes.yaml for joins | canonical suffix _shojo vs series_plan short key |
| M061 | name_drift | `sleep_restoration_iyashikei` | `sleep_restoration` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml / series_plans_en_us | `sleep_restoration_iyashikei` | config/manga/canonical_brand_list.yaml for brand_id; alias table in manga_canon_planned_volumes.yaml for joins | canonical suffix _iyashikei vs series_plan short key |
| M062 | name_drift | `bright_presence_tw_seinen` | `bright_presence_tw` | canonical_brand_list.yaml vs manga_brand_series_plan.yaml / series_plans_en_us | `bright_presence_tw_seinen` | config/manga/canonical_brand_list.yaml for brand_id; alias table in manga_canon_planned_volumes.yaml for joins | TW market brand; seinen suffix in canon only |

## Operator Actions (none auto-applied)

1. Confirm slug alias table in `manga_canon_planned_volumes.yaml` is complete for all 9 known suffix variants.
2. Decide whether remaining 24 brands without `manga_brand_series_plan.yaml` entries need explicit series plans or tier-inherit is sufficient.
3. Confirm `brand_registry.yaml` locale-specific brands (TW/HK/CN/SG) remain outside Path X 37 for matrix purposes.
4. Music axis: Path X brands remain non-music unless wizard YAML exists; music slot 38+ separate per MUSIC-MODE-BRAND-INTEGRATION-V1-01.

## Cross-references

- Matrix: `artifacts/coordination/brand_locale_surface_coverage_matrix_2026-05-30.tsv`
- Prior en_US plan (input, not overwritten): `artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv`
- BR-CANON-02-GLOBAL-BRAND-IDENTITY: `docs/PEARL_ARCHITECT_STATE.md`
