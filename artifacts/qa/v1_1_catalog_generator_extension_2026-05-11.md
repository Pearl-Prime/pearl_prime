# V1.1 catalog generator extension — implementation notes

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1)  
**Date:** 2026-05-11  
**Authority:** `docs/PEARL_ARCHITECT_STATE.md` (AMENDMENT-2026-05-11-V1-1-37-BRAND-ACTIVATION); `docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`; PR #1037 allocation TSV.

## What shipped

| Module | Role |
|--------|------|
| `scripts/catalog/v1_1_brand_allocation_loader.py` | Parse PR #1037 TSV → `dict[(brand_id, locale, surface), {series_count, episodes_per_series, priority_phase}]` |
| `scripts/catalog/build_high_confidence_catalog.py` | `--target-phase V1.0` (96 rows) vs `V1.1` (296 rows); writes TSV + optional JSON summary |

Pattern mirrors `scripts/catalog/music_mode_branch.py`: small side module + thin branch in the caller (`select_plan_for_target_phase`) without changing unrelated catalog paths.

## Row counts by locale

| Phase | en_US | ja_JP | zh_TW | zh_CN | Total rows | Distinct brands |
|-------|-------|-------|-------|-------|--------------|-----------------|
| **Before (V1.0 gate)** | 24 | 24 | 24 | 24 | **96** | **12** |
| **After (V1.1 gate)** | 74 | 74 | 74 | 74 | **296** | **37** |

V1.0 rows are exactly the TSV cells tagged `V1.0_matrix_confirmed`. V1.1 adds all `V1.1_proposed` cells for the 25 net-new Path X brands (200 rows) on top of the existing 96.

## Sample commands

```bash
PYTHONPATH=. python3 scripts/catalog/build_high_confidence_catalog.py --target-phase V1.0
PYTHONPATH=. python3 scripts/catalog/build_high_confidence_catalog.py --target-phase V1.1
```

Default outputs:

- `artifacts/catalog/path_x_allocation_catalog_V1_0.tsv`
- `artifacts/catalog/path_x_allocation_catalog_V1_0_summary.json`
- `artifacts/catalog/path_x_allocation_catalog_V1_1.tsv`
- `artifacts/catalog/path_x_allocation_catalog_V1_1_summary.json`

## Sample output row (V1.1, tab-separated)

```
brand_id	locale	surface	series_count	episodes_per_series	priority_phase	target_phase	content_units
stillness_press	en_US	ebook	5	5	V1.0_matrix_confirmed	V1.1	25
```

`content_units` = `series_count * episodes_per_series` (planning-weight hint only).

## Tests

`tests/catalog/test_v1_1_brand_allocation.py` — loader edge cases (missing file, bad surface, duplicate keys, column alias, absent brand); full-dimension checks when the PR #1037 TSV is present in-tree.
