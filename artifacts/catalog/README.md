# Manga Full Catalog Plan Artifacts (2026-05-30)

Planning-only artifacts produced by Pearl_Dev filesystem audit. No config, scripts, or SSOT YAMLs were modified.

## Files

| File | Purpose |
|------|---------|
| `manga_full_catalog_plan_2026-05-30.yaml` | Definitive series+title slate: 37 brands × 5 locales, cadence, serialization slots, Wave 1 flags |
| `manga_image_bank_coverage_plan_2026-05-30.tsv` | Per-brand interior image-bank slot coverage (V2 named-cast scope) |

## Filesystem audit verdict (origin/main)

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Canon brands | 37 | 37 | ✅ |
| In-scope locales | 5 | en_US, ja_JP, ko_KR, zh_CN, zh_TW | ✅ |
| `series_plan.yaml` per locale | 270 | 270 each | ✅ |
| `series_plan.yaml` total | 1,350 | 1,350 | ✅ |
| `book_plan` chapter files | 18,900 | 18,900 | ✅ |
| Brand×locale gaps (series) | 0 | 0 | ✅ |
| Brand×locale gaps (book) | 0 | 0 | ✅ |
| Rendered panel PNGs (`artifacts/manga/`) | — | 231 | partial production |
| Image-bank dirs present | — | 2 (`stillness_press`, `warrior_calm`) | gap before production wave |

**Conclusion:** Series+title+chapter SSOT is **100% complete** at the catalog planning layer (1,350 series × 14 chapters = 18,900 book plans). Image-bank interior slots are **not** production-ready for 35/37 brands.

## Locale scope

In scope: `en_US`, `ja_JP`, `ko_KR`, `zh_CN`, `zh_TW`.

Out of scope (operator bulk regen pending, PR #1369): `fr_FR`, `de_DE`, `it_IT`, `pt_BR`.

## Render policy

Panels render once in layered `en_US` (master). CJK/KR products ship translated text overlays on shared art — no locale re-render (MANGA V2/V5 layered pipeline).

## Wave 1 deep templates

- **US1:** `stillness_press` × `en_US` — anchor series `the_alarm_is_lying`
- **JP1:** `stillness_press` × `ja_JP` — same series, localized overlay

## Image-bank slot taxonomy (V2)

Per `MANGA-LAYERED-PIPELINE-V2-01`: named-cast LoRA scope = **12–14 teachers catalog-wide**, not 200+ per-catalog LoRAs.

**Teacher-anchored brands (60 slots):** character_views(4) + model_sheets(12) + expressions(8) + poses(16) + anchor_panels(6) + location_backgrounds(8) + props(6).

**Style-only brands (30 slots):** location_backgrounds(24) + props(6).

## Authority chain

- `config/manga/canonical_brand_list.yaml`
- `config/manga/manga_brand_series_plan.yaml`
- `config/brand_admin/manga_canon_planned_volumes.yaml`
- `config/source_of_truth/manga_series_plans/`
- `config/source_of_truth/manga_book_plans/`
- `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`

## Regeneration

Do **not** re-generate SSOT YAMLs. To refresh these planning artifacts only, re-run the audit against current filesystem counts and SSOT paths.
