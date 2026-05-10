# V1.1 — warrior_calm ja_JP tentpole metadata fix

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1)  
**Agent:** Pearl_Editor  
**Date:** 2026-05-11  
**Refs:** PR #1035 catalog status diagnostic; PR #1038 V1.1 AMENDMENT (non-critical cleanup)

## What was wrong

The mono-genre tentpole profile `config/source_of_truth/manga_profiles/brands/warrior_calm_cultivation.yaml` declared **`genre_family: battle`** while the manga portfolio SSOT maps the teacher brand tentpole genre to **`cultivation`** in `config/manga/brand_genre_allocation.yaml` (`brand_tentpole.warrior_calm: cultivation`).

That inconsistency surfaces most clearly for **ja_JP**, where the allocation matrix primary cell is **battle (25%)** under the registered **coexist** divergence policy (`tentpole_divergence_policy.warrior_calm.ja_JP`), while generated catalog rows still mark **cultivation** as `is_tentpole=true`. Homogeneity and catalog-status checks that join profile metadata to tentpole genre therefore reported a single-brand mismatch without changing any locale matrix row.

## What was fixed

- Set `genre_family` to **`cultivation`** in `warrior_calm_cultivation.yaml` so the lane profile matches the declared tentpole genre and the `title_id` / `brand_id` naming (`warrior_calm_cultivation` / `warrior_calm`).
- **No edits** to `canonical_brand_list.yaml`, en_US or zh_TW/zh_CN matrix blocks, or `manga_brand_series_plan.yaml` (already `genre: cultivation` for `warrior_calm`).

## Verification

1. **Config alignment:** `brand_genre_allocation.yaml` → `brand_tentpole.warrior_calm` remains `cultivation`; profile `genre_family` now matches.
2. **Catalog generator (unchanged inputs):** Regenerate ja_JP slice if desired:

   ```bash
   python3 scripts/catalog/generate_manga_catalog.py \
     --locales ja_JP \
     --output-dir artifacts/catalog/manga/
   ```

   Expected: `warrior_calm` cultivation rows still carry `tentpole_match`; battle primary rows still carry `intentional_portfolio_divergence:matrix_primary=battle,tentpole=cultivation` under the coexist policy.
3. **Homogeneity helper:** `scripts/manga/check_catalog_homogeneity.py` groups profiles by `(market_demo, genre_family, visual_grammar)`; this brand lane now keys under **cultivation**, consistent with tentpole SSOT.

## Commit

Message: `editor(v1-1): warrior_calm ja_JP tentpole metadata fix`
