# Layer 1 — Catalog Plan Completeness (37 brands × 4 launch locales)

**Author:** Pearl_PM + Pearl_Research
**Date:** 2026-05-27
**Program:** WORLDWIDE-CATALOG-GO-LIVE-V1 — Layer 1 (PLAN) per `docs/SYSTEMS_STATE_20260527.md` §3
**Scope:** Make the catalog plan complete + drift-free for **37 brands × 4 launch locales × 3 content-types** (manga + book + podcast). Planning/data only — no content generation.
**Authority chain:** `config/manga/canonical_brand_list.yaml` (37 brands) · `docs/GENRE_PORTFOLIO_PLAN.md` (tier/genre strategy) · `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (manga reconciliation) · `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (V1.1 ebook+manga allocation, PR #1037/#1038).

---

## Coverage matrix — before → after

The Layer 1 universe is **444 cells = 37 brands × 4 launch locales × 3 surfaces**.

| Surface | SSOT | Before | After | Gate |
|---|---|---|---|---|
| **Manga** | `config/source_of_truth/manga_series_plans/<locale>/` (1,350 series-plan YAMLs) | 148/148 | 148/148 | Already complete (Phase 2X.4 of the reconciliation spec landed). |
| **Book (ebook)** | `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (`ebook` surface) | 148/148 | 148/148 | Already complete at allocation level (PR #1037/#1038). |
| **Podcast** | `artifacts/catalog/worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv` (`podcast` surface) | **0/148** | **148/148** | **Closed this PR.** |
| **TOTAL** | — | **296/444** | **444/444** | **Layer 1 plan-complete.** |

Validator: `scripts/catalog/validate_plan_completeness_37x4.py` → `artifacts/catalog/plan_completeness_37x4_20260527.tsv` (148 (brand,locale) rows, all `COMPLETE`).

---

## What the discovery corrected (vs the initial brief assumptions)

1. **"35/37 brands have manga plans; fix the 2 gaps."** The legacy `config/manga/manga_brand_series_plan.yaml` covers only **13 teacher-mode brands** (a pre-reconciliation operational file). But it is **superseded** by the generated `config/source_of_truth/manga_series_plans/`, which is **37/37 brands × 4 launch locales complete** (270 series/locale, correct tier sizing: flagship 14–18, core 8–10, niche 4–6). Manga needed **no** authoring. The legacy file is stale-but-still-referenced by 6 scripts (e.g. `scripts/brand_admin/generate_manga_canon_planned_volumes.py`) — see Remaining gaps.

2. **Book seed = `high_confidence_catalog_v1.tsv` (801 rows).** That TSV uses a *third* brand taxonomy (`stabilizer_tw`, `sleep_repair_tw`, …) and only en-US/en-GB — it is the zh-helper + en book lane, **not** the 37 canonical brands. The canonical 37-brand book plan already exists as the `ebook` surface of the 05-11 V1.1 allocation TSV (148/148). No new book plan file was needed.

3. **The only genuine Layer 1 gap was podcast.** The 05-11 allocation TSV is a **2-surface contract** (`ebook` + `manga`) enforced strict by `scripts/catalog/v1_1_brand_allocation_loader.py` (`VALID_SURFACES = {ebook, manga}`) and hard-asserted by `tests/catalog/test_v1_1_brand_allocation.py` (`len(plan) == 296`). Adding podcast rows to that file would break the contract + test. Podcast was therefore authored as a **separate, additive plan** with the identical column schema.

---

## Brand-axis reconciliation (the drift the gap report flagged)

`artifacts/catalog/catalog_gap_report.md` cited "166 rows missing series-plan/cover-art mappings" and "legacy teacher-brand names not migrated." Resolution:

- **36 of 37 canonical brands map 1:1** to the book-pipeline `config/catalog_planning/brand_series_plans.yaml` by stripping the genre/demographic suffix (`qi_foundation_cultivation` → `qi_foundation`, `stabilizer_healing` → `stabilizer`, …).
- The 37th, `bright_presence_tw_seinen`, is **zh_TW-first** (Adi Da, `primary_lane: taiwan`); the book-pipeline short key is `bright_presence`.
- The 166-row drift is in the **legacy `full_catalog.csv` generator** (still on the pre-12×37 teacher-brand registry) and the per-locale `brand_genre_allocation.yaml` (only 12 teacher brands had genre rows). The **V1.1 allocation TSV (05-11) already closed this** for the ebook+manga surfaces — all 37 canonical brands now carry rows. This PR extends the same closure to podcast.

---

## Podcast allocation rule (derived, not invented)

`scripts/catalog/generate_podcast_plan_37x4.py` reads `config/podcast/brand_podcast_plans.yaml` market parameters (weekly cadence, all 4 launch locales) and emits per-brand × per-locale rows:

| Locale | series_count (seasons/yr) | episode_per_series_count | source field |
|---|---|---|---|
| en_US | 6 | 10 | `markets.en_us.series_per_brand_year` / `.episodes_per_series` |
| ja_JP | 4 | 8 | `markets.ja_jp.*` (shorter, JP commute culture) |
| zh_TW | 3 | 10 | `markets.zh_tw.*` |
| zh_CN | 4 | 12 | `markets.zh_cn.*` (longer paid 知识付费 series) |

Uniform-per-locale at the allocation layer (mirrors the ebook surface's 5/locale convention); tier depth lives at the series-plan YAML layer.

---

## Remaining gaps (out of Layer 1 scope; for downstream layers / follow-ups)

| Gap | Impact | Owner / Layer |
|---|---|---|
| Legacy `manga_brand_series_plan.yaml` covers 13 of 37 brands but is still read by 6 scripts | Brand-admin planned-volume counts derive from the 13-brand file, under-counting | Follow-up: migrate consumers to `manga_series_plans/` (flagged for separate task) |
| `book_plans_en_us/` (1,001 YAMLs) is en_US-only + 8 legacy brands | Per-chapter book *content* plans not yet fanned to 37×4 | **Layer 2** (brand-1 deep) + **Layer 3** (fan-out) — content authoring, not Layer 1 allocation |
| Podcast surface not wired into `v1_1_brand_allocation_loader.py` (kept 2-surface to avoid breaking the strict contract/test) | Podcast plan is a sibling TSV, not merged into the loader | Future: a deliberate 3-surface contract bump (loader + test) if/when podcast joins the unified allocation |
| Series/episode *titles* are `TBD` in series-plan YAMLs | Expected at plan stage | Layer 2/3 generation |

---

## Layer 1 gate verdict

**PASS — 444/444 cells.** All 37 brands × 4 launch locales have manga + book + podcast plans. Per `docs/SYSTEMS_STATE_20260527.md` §3, the Layer 1 plan-completeness gate is satisfied; it unlocks Layer 2 (brand-1 deep validation) and Layer 3 (36-brand fan-out), the latter still requiring explicit operator authorization.

Reproduce:
```bash
PYTHONPATH=. python3 scripts/catalog/generate_podcast_plan_37x4.py --check
PYTHONPATH=. python3 scripts/catalog/validate_plan_completeness_37x4.py
```
