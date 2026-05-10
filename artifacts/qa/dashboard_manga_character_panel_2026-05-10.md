# Dashboard manga character panel — implementation notes (2026-05-10)

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 P0)  
**Subsystem:** brand_admin + dashboard (Pearl_Brand)

## Scope

- `scripts/brand/manga_character_endpoint.py` builds JSON for `/manga-character-panel.json`.
- `brand-wizard-app/public/brand_admin.html` adds the `manga-character-panel` block, refresh on picker load / brand init / manual button.
- No image generation, no classifier edits, no catalog YAML/TSV commits in this change set.

## Catalog plan TSV

Primary paths (Pearl_PM session):

- `artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv`
- `artifacts/catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv` (optional)

Additional files matching `artifacts/catalog/worldwide_catalog_plan_*_*.tsv` are read once each (deduped) so a renamed drop still parses if the glob matches.

Headers supported (tab-separated):

- Brand: `brand_id` or `brand`
- Series: `series_id` or `series_slug`
- Locale: `locale`, `market_locale`, or `locale_id` (`en_US` / `ja_JP` only; other locales skipped)

If the filename contains `worldwide_catalog_plan_en_US_` or `_ja_JP_`, that locale is the default when the row omits a locale column.

## Character image resolution

Per series, the first existing file wins:

1. `artifacts/manga/<locale>/<brand_id>/<series_id>/main_character.png` (matches manga catalog `output_target_path` layout)
2. `artifacts/manga/<brand_id>/<series_id>/main_character.png`
3. `artifacts/manga/<brand_id>/main_character.png` (shared portrait for all series under the brand)

JSON fields per series: `series_id`, `main_character_image_path` (repo-relative POSIX or `null`), `status` (`ready` | `missing`).

## Mock sample (fixture-style)

```json
{
  "stillness_press": {
    "en_US": {
      "series": [
        {
          "series_id": "stillness_press_healing_01",
          "main_character_image_path": "artifacts/manga/en_US/stillness_press/stillness_press_healing_01/main_character.png",
          "status": "ready"
        }
      ]
    },
    "ja_JP": { "series": [] }
  }
}
```

## UI behavior

- Default fetch URL: `http://127.0.0.1:8768/manga-character-panel.json` (override: `?mcp_endpoint=` or `window.__MANGA_CHARACTER_PANEL_URL`).
- Thumbnails use `../../` + `main_character_image_path` so `file://` opens from `brand-wizard-app/public/` resolve toward repo root.
- `status: missing` or failed image load shows a dashed “missing” tile.
- Empty locale column: helper copy explains missing catalog plan rows.

## Smoke

```bash
PYTHONPATH=. python3 scripts/brand/manga_character_endpoint.py --json | head
```

With no catalog TSV, active brands still appear with empty `series` arrays for both locales.

## Tests

```bash
PYTHONPATH=. python3 -m pytest tests/brand/test_manga_character_endpoint.py -v
```
