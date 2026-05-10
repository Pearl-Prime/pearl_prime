# Manga-only brand allocation — V1 (25 Path X brands)

**Status:** planning spec (Pearl_PM + Pearl_Marketing). No generator edits.  
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Consumes:** `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`; `artifacts/qa/worldwide_catalog_37_brand_allocation_audit_2026-05-11.md`  
**Frozen inputs:** `config/manga/canonical_brand_list.yaml` (37 brands) — do not edit from this workstream.

## 1. Scope

This spec governs **allocation logic** for the **25** Path X `brand_id` values that currently have **no** row in `config/manga/brand_genre_allocation.yaml` in any locale. Pearl_Dev extends the catalog generator / matrix materializer in a **separate** workstream (`ws_catalog_generator_extend_to_37_brands_20260511`).

## 2. Idempotence rules

1. **Do not** rename the 12 teacher short keys in YAML; append new blocks under each locale for missing canonical ids only.
2. **Canonical id** in generated catalog rows must always match `canonical_brand_list.yaml` keys (e.g. `sleep_restoration_iyashikei`, not `sleep_restoration`).
3. **`bright_presence_tw_seinen`:** matrix authoring may continue to use `bright_presence_tw` as the **lane key** in zh_TW only; generator must emit canonical `brand_id` for downstream Conductor + dashboards.

## 3. Surface mix defaults

Use the demographic × locale **ebook / manga weight table** in the audit MD (Phase 3). Materialization rule: percentages are **portfolio** weights for genre lanes inside `brand_genre_allocation` once Pearl_Dev adds rows; they are **not** Phoenix cell denominators by themselves (see `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` for 222 + 37 JP manga-only cell math).

## 4. Series depth defaults (pending operator Q2)

| Track | Default in TSV (V1.1 proposal) | Worldwide plan Phase 2 anchor (for later realignment) |
|-------|--------------------------------|------------------------------------------------------|
| ebook | 5 × 5 | Matches Section 1.2 ebook rule in worldwide plan |
| manga | 5 × 5 (pilot) | Tier ladder: flagship 14 / core 8 / niche 4 × 24 episodes |

## 5. Phasing (pending operator Q1 + Q3)

- **Q1 = V1.1 parallel:** treat all 200 proposed TSV cells as runnable alongside teacher-12 saturation work.
- **Q1 = V1.2 defer:** mark `priority_phase` column to `V1.2_proposed` for cohorts Pearl_Marketing selects (e.g. niche workplace bundle last).
- **Q3 = en_US first:** materialize `brand_genre_allocation.en_US` first per locale, then roll ja_JP → zh_TW → zh_CN.

## 6. blocked_lora / blocked_score (Pearl_Dev)

Follow **Q4** ordering from operator session. Default Pearl_PM recommendation: **(1)** unblock `blocked_lora` for zh_TW/zh_CN manga rows that already exist in partial catalogs; **(2)** rerun / clear `blocked_score` after LoRA refs stable — evidence trail in PR #1035 audit and `manga_catalog_summary.json` lineage.
