# Worldwide Catalog Plan V1 — Methodology and Gap Analysis

**Project ID:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2)  
**Date:** 2026-05-10  
**Owner:** Pearl_PM (coordination); Pearl_Marketing (volume alignment)  
**Companion spec:** `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`  
**Numeric SSOT:** `artifacts/catalog/worldwide_catalog_plan_{en_US,ja_JP,zh}_2026-05-10.tsv`

---

## 1. Discovery inputs (read-only)

| Artifact | What was extracted |
|----------|-------------------|
| `config/manga/canonical_brand_list.yaml` | 37 `brand_id` keys, tier (`flagship` 3, `core` 16, `niche` 18), demographic, topic notes |
| `config/manga/brand_lora_plans.yaml` | `character_loras` (12 named teachers + style refs), `brand_style_loras` (suffix + trigger tokens), `protagonist_loras` seeds |
| `config/authoring/pen_name_teacher_profiles.yaml` | External citation anchors for persona economics — **not** a 12-row teacher roster |
| `config/teachers/teacher_registry.yaml` | 13 named teachers including `adi_da` |
| `config/catalog_planning/teacher_brand_archetypes.yaml` | 12 teacher-owned book archetypes (lane naming differs from Path X `_shojo` / `_workplace` suffixes) |
| `config/marketing/weekly_volumes_per_brand.yaml` | V1 draft: manga `1/week` per brand; ebook/audiobook/podcast/video `0` pending Table 6 |
| `artifacts/catalog/pearl_prime_book_script_catalogs/catalog_summary.json` | Row counts: en_US/ja_JP 1478 ready; zh_TW 2818 (160 blocked); zh_CN 2630 ready |
| `artifacts/catalog/manga/manga_catalog_summary.json` | en_US 170 rows; ja_JP 166; zh_TW 275 (84 blocked_lora); zh_CN 269 (69 blocked_lora) |
| `artifacts/qa/parallel_image_generation_plan_2026-05-09.md` | Image targets, wave wall-time model, KDP/audiobook workflow gaps |

No files above were modified in the authoring session.

---

## 2. Derivation rules

### 2.1 Brand-locale-surface grid

**555 cells** = 37 brands × 3 locale buckets × 5 surfaces. The TSV files express **per-brand × locale bucket** rollups; surface-level splits are documented in the master spec (ebook/audiobook share book counts; video splits into short/long columns).

### 2.2 Ebook and audiobook (Q2 baseline)

- **5** ebook series × **5** books per series = **25** books per brand for `en_US` and `ja_JP` rows.  
- **Audiobook** units **equal** ebook units (same script policy per Pearl Prime worldwide program assumptions).  
- **covers_needed** (en/ja) = `2 × total_books` → KDP-class cover + audiobook jacket per title.

### 2.3 Manga series ladder

Aligned to `parallel_image_generation_plan_2026-05-09.md` series-count commentary:

| Tier | Series per brand |
|------|-----------------:|
| flagship (3 brands) | 14 |
| core (16 brands) | 8 |
| niche (18 brands) | 4 |

**Manga episodes** = `manga_series × 24` per locale bucket (planning year stub; not a chapter table from `manga_brand_series_plan.yaml`).

### 2.4 Podcast and video placeholders

`weekly_volumes_per_brand.yaml` sets `0` for non-manga surfaces. Phase 2 still needs dashboard-ready **annual stub** targets:

- **26** podcast episodes per brand per locale bucket (bi-weekly).  
- **12** short + **4** long videos per brand per locale bucket.

These are **planning-only** until marketing SSOT bumps non-zero.

### 2.5 Combined zh bucket (`worldwide_catalog_plan_zh_2026-05-10.tsv`)

Each row aggregates **zh_TW + zh_CN**:

- `total_books` = **50** per brand (25 titles × 2 storefronts).  
- `manga_series`, `manga_episodes`, `podcast_episodes`, `video_short`, `video_long`, `main_chars_needed` are **doubled** vs en_US to reflect parallel TW/CN pipelines.  
- `covers_needed` = `2 × total_books` → **100** per brand (KDP + audiobook for each of the two SKUs).

**Interpretation note:** If the operator prefers **one** zh editorial spine with localized packaging only, rerun the TSV generator with `zh_mult=1` for content columns and keep `covers_needed` at `2 × 25` — that is a Q1/Q2 decision (see master spec Section 10).

---

## 3. Cross-validation (TSV vs master spec)

| Check | Result |
|-------|--------|
| TSV data rows per file | **37** (`brand_id` cardinality matches `canonical_brand_list.yaml`) |
| Master spec Section 2 subsections | **37** (`### 2.1` … `### 2.37`) |
| en_US column sums | Match Section 3.1 table in master spec |
| ja_JP column sums | Identical to en_US at this baseline |
| zh column sums | Match Section 3.3 table |

---

## 4. Gap analysis vs current catalogs

### 4.1 Pearl Prime standard_book catalogs

| Observation | Gap | Mitigation |
|-------------|-----|------------|
| 1478 rows/locale (en/ja) vs 25-book Phase-2 slice | **Two orders of magnitude** between legacy generator breadth and Phase-2 operator default (Q2) | Pick one SSOT for dashboard “target books” — either adopt 25-book slice **or** map Phase-2 to existing 1478-row physics |
| zh_TW blocked_score 160 | Readiness | Finish scoring unblockers before zh Phase 2.3 |

### 4.2 Manga catalogs (`artifacts/catalog/manga`)

| Observation | Gap | Mitigation |
|-------------|-----|------------|
| en_US 170 rows vs Phase-2 target 242 series | **+72** series rows needed after matrix regen / tier ladder adoption | Regenerate `generate_manga_catalog.py` inputs or accept lower series until operator ratifies tier ladder |
| zh blocked_lora rows | TW 84, CN 69 | LoRA + protagonist completion (Wave 1–2 in PR #988) before zh manga production |
| README states zh deferred | Scope | Phase 2.3 explicitly adds zh generator pass |

### 4.3 Marketing SSOT

| Observation | Gap | Mitigation |
|-------------|-----|------------|
| Non-manga surfaces all `0/week` | No scheduling truth for podcast/video | Operator Table 6 ratification → bump `weekly_volumes_per_brand.yaml` |

### 4.4 Image / character pipelines

| Observation | Gap | Mitigation |
|-------------|-----|------------|
| PR #988: missing `flux_kdp_cover.json` / `flux_audiobook_cover.json` | Cover batch blocked on workflow | `ws_image_batch_generation_orchestration_20260509` |
| No `character_design:` in series YAMLs (per 2026-05-07 install log) | Protagonist + PuLID smoke blocked | Pearl_Editor A4 axis authoring |
| `pen_name_teacher_profiles.yaml` not a roster | Author bio provenance | Use `teacher_registry.yaml` + `author_registry.yaml` |

### 4.5 Teacher count vs “12 teacher voices”

Discovery shows **13** `teacher_registry.yaml` entries (includes `adi_da`). Book-lane docs refer to **12 teacher brands + 24 standard** per lane; Path X manga list is **37** brands with partial overlap to the 12 teacher-style anchors. The master plan resolves overlap by **lead voice** + **8-pack** associates per brand.

---

## 5. Aggregated totals (planning math)

**Locale buckets:** en_US + ja_JP + zh (zh counts TW+CN doubled columns).

| Metric | Formula | Total |
|--------|---------|------:|
| ebook SKUs | 925 + 925 + 1850 | **3,700** |
| audiobook SKUs | same as ebook | **3,700** |
| manga episodes | 5808 + 5808 + 11616 | **23,232** |
| podcast episodes | 962 + 962 + 1924 | **3,848** |
| video shorts | 444 + 444 + 888 | **1,776** |
| video longs | 148 + 148 + 296 | **592** |
| cover renders (`covers_needed`) | 1850 + 1850 + 3700 | **7,400** |
| manga main character identities (`main_chars_needed`) | 242 + 242 + 484 | **968** |

**555** brand-locale-surface cells (structural), independent of the SKU totals above.

---

## 6. Operator Q card (verbatim)

**Q1:** Phase order — en_US first, then ja_JP, then zh? OR parallel?  

**Q2:** Per-brand series count default — propose 5 series per brand × 5 books per series = 25 books per brand × 37 brands × 3 locales = 2,775 books total. Override?  

**Q3:** Manga main character source — generate from character_design vocab (auto) OR operator-supplied reference photos?  

**Q4:** Author bio authoring source — Pearl_Writer (auto-generate) OR operator-curated?

---

## 7. Revision control

When any discovery YAML changes (brand list, tier, marketing SSOT), regenerate the three TSVs and update Section 3 rollups plus this methodology Section 5.
