# Worldwide catalog — 37-brand allocation audit (Path X)

**Project ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2)  
**Subsystem:** pearl_pm + Pearl_Marketing  
**Date:** 2026-05-11  
**Authority:** `docs/PEARL_ARCHITECT_STATE.md` cap WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01; `config/manga/canonical_brand_list.yaml` (37 brands); `config/manga/brand_genre_allocation.yaml`; `config/manga/manga_brand_series_plan.yaml`  
**Cross-reference:** Catalog planning diagnostic PR **#1035** (artifact path cited in program brief: `artifacts/qa/catalog_planning_status_per_market_2026-05-11.md` — use PR branch if not yet on main).  
**Outputs:** `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (machine-readable); `docs/specs/MANGA_ONLY_BRAND_ALLOCATION_V1_SPEC.md` (25-brand logic).

---

## STARTUP_RECEIPT

| Field | Value |
|-------|--------|
| project_id | PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 |
| branch | `agent/worldwide-catalog-37-brand-allocation-20260511` |
| base | `origin/main` |
| write_scope | 5 files max (audit MD, allocation TSV, worldwide plan appendix, manga-only allocation spec, ACTIVE_WORKSTREAMS rows) |
| out_of_scope | Code, `canonical_brand_list.yaml`, `brand_lora_plans.yaml`, edits to teacher-12 genre percentages, merges |

---

## Phase 1 — Inventory of the current 12-brand teacher subset

**Source:** `config/manga/brand_genre_allocation.yaml` (`allocations.en_US` / `ja_JP` / `zh_TW` / `zh_CN`) + `config/manga/manga_brand_series_plan.yaml` (`brands`).

**Short keys in YAML** map to **canonical** `brand_id` as follows (Path X suffix convention):

| YAML short key | Canonical `brand_id` | Tier / demographic (canonical list) | `manga_brand_series_plan` (active_series_target / new_series_per_year / chapters_per_series_per_month / max_chapters_before_volume) | Locale coverage in genre matrix |
|----------------|----------------------|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| stillness_press | stillness_press | flagship / josei | 3 / 4 / 2 / 10 | en_US, ja_JP, zh_TW, zh_CN |
| cognitive_clarity | cognitive_clarity | flagship / seinen | 4 / 5 / 3 / 12 | en_US, ja_JP, zh_TW, zh_CN |
| digital_ground | digital_ground | flagship / manhwa | 4 / 5 / 4 / 14 | en_US, ja_JP, zh_TW, zh_CN |
| sleep_restoration | sleep_restoration_iyashikei | core / josei | 2 / 3 / 2 / 8 | en_US, ja_JP, zh_TW, zh_CN |
| somatic_wisdom | somatic_wisdom_shojo | core / josei | 3 / 4 / 2 / 10 | en_US, ja_JP, zh_TW, zh_CN |
| relational_calm | relational_calm_iyashikei | core / josei | 4 / 5 / 3 / 10 | en_US, ja_JP, zh_TW, zh_CN |
| body_memory | body_memory_shojo | core / josei | 3 / 4 / 2 / 10 | en_US, ja_JP, zh_TW, zh_CN |
| heart_balance | heart_balance_shojo | core / josei | 3 / 4 / 2 / 10 | en_US, ja_JP, zh_TW, zh_CN |
| qi_foundation_cultivation | qi_foundation_cultivation | niche / seinen | 3 / 3 / 4 / 16 | en_US, ja_JP, zh_TW, zh_CN |
| warrior_calm | warrior_calm_cultivation | niche / shonen | 3 / 4 / 4 / 16 | en_US, ja_JP, zh_TW, zh_CN |
| solar_return | solar_return_isekai | niche / shonen | 3 / 4 / 3 / 12 | en_US, ja_JP, zh_TW, zh_CN |
| devotion_path | devotion_path_shonen | niche / shonen | 3 / 4 / 3 / 12 | en_US, ja_JP, zh_TW, zh_CN |

**Locale bias (marketing / Pearl_Marketing):** `brand_genre_allocation` header comments: en_US ebook-primary mix; ja_JP manga-primary; zh_TW / zh_CN add cultivation/historical bias vs en baseline; zh_CN YAML notes design intent if/when local entity access exists.

---

## Phase 2 — The 25 Path X brands with no genre-matrix row today

Cross-reference: all keys under `canonical_brand_list.yaml:brands` **minus** the 12 canonical rows above.

| `brand_id` | demographic | `current_state` |
|------------|-------------|-----------------|
| healing_ground_healing | josei | no allocation row in `brand_genre_allocation` (any locale) |
| minimal_mind_healing | seinen | no allocation row |
| night_reset_healing | josei | no allocation row |
| gentle_growth_healing | josei | no allocation row |
| stabilizer_healing | seinen | no allocation row |
| career_lift_workplace | josei | no allocation row |
| high_performer_workplace | seinen | no allocation row |
| executive_calm_workplace | seinen | no allocation row |
| morning_momentum_workplace | shonen | no allocation row |
| optimizer_workplace | seinen | no allocation row |
| focus_sprint_workplace | seinen | no allocation row |
| trauma_path_healing | josei | no allocation row |
| resilient_parent_social | josei | no allocation row |
| confidence_core_romance | shojo | no allocation row |
| relationship_clarity_romance | josei | no allocation row |
| adhd_forge_mystery | shonen | no allocation row |
| stoic_edge_battle | seinen | no allocation row |
| spiritual_ground_supernatural | josei | no allocation row |
| legacy_builder_memoir | seinen | no allocation row |
| bio_flow_healing | seinen | no allocation row |
| longevity_lab_healing | seinen | no allocation row |
| hormone_reset_healing | josei | no allocation row |
| creative_unfold_social | shojo | no allocation row |
| calm_student_school | shojo | no allocation row |
| bright_presence_tw_seinen | seinen | no allocation row under this canonical id (TW lane uses `bright_presence_tw` in zh_TW matrix + `manga_brand_series_plan`; see Phase 4) |

---

## Phase 3 — Proposed per-locale × per-surface allocation (25 missing)

**Defaults (Pearl_PM baseline, operator-ratifiable):**

- **Series count:** 5 per locale per surface (ebook lanes + manga lanes) unless Q2 selects tier ladder from `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` Phase 2 defaults.
- **Episodes per series (manga):** 5 for this planning slice (Pearl_Conductor pilot scale); supersede with 24-episode planning year from worldwide plan after Q2.
- **Surface mix (ebook % / manga %)** — marketing-leaning heuristic by demographic + locale:

| demographic | en_US | ja_JP | zh_TW | zh_CN |
|-------------|-------|-------|-------|-------|
| josei | 35 / 65 | 20 / 80 | 30 / 70 | 35 / 65 |
| seinen | 30 / 70 | 15 / 85 | 28 / 72 | 32 / 68 |
| shojo | 40 / 60 | 25 / 75 | 38 / 62 | 40 / 60 |
| shonen | 25 / 75 | 15 / 85 | 25 / 75 | 28 / 72 |
| manhwa | 20 / 80 | 15 / 85 | 22 / 78 | 25 / 75 |

**Non-obvious operator callouts**

1. **`bright_presence_tw_seinen`:** Distribution is **zh_TW-first** per `manga_brand_series_plan.yaml` (`primary_lane: taiwan`). Canonical id differs from matrix key `bright_presence_tw`. Propose **TW = full ebook+manga** stack; **en_US / ja_JP / zh_CN** = do not mirror full ebook program until architect TEACHER-MANGA gate clears; Japan **parallel manga-only** lane may still consume `brand_id` parity under `JAPAN_MANGA_ONLY_CATALOG_V1_SPEC` (separate workstream).
2. **Workplace cluster (`career_lift_*` … `focus_sprint_*`):** Seinen-heavy; ja_JP manga weight **85%** default — confirm salaryman / workplace genre bundle with `canonical_genre_list` before generator materializes cells.
3. **Clinical / grief-heavy (`trauma_path_healing`, `spiritual_ground_supernatural`):** zh_CN regulatory thinning already documented for zh-specific brands in `brand_genre_allocation` comments; apply same **graphic_medicine / horror / social_issue** dampening when authoring CN rows.
4. **`stabilizer_healing` vs zh helper `stabilizer_tw` / `stabilizer_cn`:** Different `brand_id`s; do not conflate Path X `stabilizer_healing` rows with ahjan-anchored zh helper brands.

**Priority phase column in TSV:** `V1.1_proposed` for all 25×4×2 missing-brand cells pending Q1; teacher 12 rows tagged `V1.0_matrix_confirmed`.

---

## Phase 4 — Four-locale coverage for the existing 12 (reconcile PR #1035 headline counts)

**Same 12 canonical brands** appear in **both** `en_US` and `ja_JP` sections of `brand_genre_allocation.yaml` (identical teacher set).

**zh_TW vs zh_CN “extra” brands:** The genre matrix lists **6 zh-specific helper brands** per locale (`sleep_repair_*`, `stabilizer_*`, `panic_first_aid_*`, `gen_z_grounding_*`, `grief_companion_*`, `inner_security_*`) that are **not** in `canonical_brand_list.yaml` (37). These inflate **row counts** in PR #1035 style dashboards (e.g. 19 vs 18) **without** covering the 25 missing Path X canonical ids.

**`bright_presence_tw`:** Present under `zh_TW` only (+ `manga_brand_series_plan`); absent from `zh_CN` block per YAML comment — maps to canonical **`bright_presence_tw_seinen`**.

**Reconciliation table — Path X canonical × locale matrix presence**

Legend: **M** = non-zero genre portfolio row exists in `brand_genre_allocation` for that locale block. **·** = no row (gap).

For the 12-teacher canonical ids, all four locales = **M**. For `bright_presence_tw_seinen`, **M** only in zh_TW (as `bright_presence_tw`). All other 24 Path X canonical brands = **·** in every locale block.

| Locale bucket | Path X brands with matrix row | Path X brands missing row | Notes |
|---------------|------------------------------|----------------------------|-------|
| en_US | 12 | 25 | Same 12 as ja_JP |
| ja_JP | 12 | 25 | Same 12 as en_US |
| zh_TW | 13 (`bright_presence_tw` + 12 teachers) | 24 | +6 non-Path helper brands also present |
| zh_CN | 12 | 25 | No `bright_presence_*` row |

**Answer to “are zh extras part of the 25 missing in en/ja?”** No — the six zh helper brands are **separate** catalog lanes. The 25 missing Path X brands remain missing in **zh_TW and zh_CN** as well (except `bright_presence_tw_seinen` gains partial coverage only in zh_TW via the `bright_presence_tw` key).

---

## Phase 5 — Gap matrix summary + machine export

| Metric | Value |
|--------|------:|
| TSV rows total | 296 (= 37 brands × 4 locales × 2 surfaces) |
| Teacher-12 confirmation rows | 96 |
| Proposed new rows (25 brands × 4 × 2) | 200 |
| PR #1035 style “brands with rows” headline (Path X only) | en_US 12/37; ja_JP 12/37; zh_TW 13/37; zh_CN 12/37 |

---

## Operator decision card (verbatim)

**Q1:** 25 missing brands — ship all in V1.1 (parallel with existing 12), OR phase to V1.2?

**Q2:** Default series count per missing brand (5 series × 5 episodes = 25 books-equivalent)? Override per-brand?

**Q3:** Locale priority for missing brands — en_US first (per locale-first), OR all 4 locales simultaneously?

**Q4:** blocked_lora / blocked_score follow-up — Pearl_Dev priority order?

---

## CLOSEOUT_RECEIPT (pre-merge)

| Field | Value |
|-------|--------|
| commit_sha | *(fill after `git commit`)* |
| pr_url | *(fill after `gh pr create`)* |
| gap counts (Path X / locale) | en_US 25; ja_JP 25; zh_TW 24; zh_CN 25 |
| proposed allocation totals | +200 surface rows in TSV for 25 brands (see Phase 5) |
| Q1–Q4 | Verbatim in section above |
