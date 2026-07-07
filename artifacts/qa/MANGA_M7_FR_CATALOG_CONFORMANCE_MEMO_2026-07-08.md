# M7 fr_FR Catalog + Conformance Closeout — 2026-07-08

**M7 status:** PARTIAL (fr_FR plans+catalog lane GREEN; full 14-locale grid not green)
**Base:** `origin/main` @ `3ae513eb7abb` (Wave A batches #4727–#4730 merged)
**Branch:** `agent/manga-m7-fr-catalog-conformance-20260708`

---

## 1. Live main verification

| Check | Result |
|---|---|
| fr_FR series plans on main | **390** (`config/source_of_truth/manga_series_plans/fr_FR/`) |
| Brands represented | **36** / 37 canonical (`bright_presence_tw_seinen` skipped — `manga_locales`) |
| Schema dry-run (`run_m7_wave_a.py --dry-run`) | **390 derived, 0 failures** |
| Top genres | workplace_drama=39, dark_fantasy=38, psychological_horror=38 |

---

## 2. Commands run

### Preflight — plan count per locale

```bash
for loc in en_US ja_JP zh_TW zh_CN ko_KR fr_FR pt_BR de_DE es_ES es_US it_IT hu_HU zh_SG zh_HK; do
  c=$(ls config/source_of_truth/manga_series_plans/$loc/*.yaml 2>/dev/null | wc -l | tr -d ' ')
  echo "$loc $c"
done
# → fr_FR 390; shipped locales 266–274; 8 wave-a zero-plan locales 0
```

### Catalog CSV (2X.5 / SSOT rollup)

```bash
PYTHONPATH=. python3 scripts/catalog/rollup_manga_catalog_from_ssot.py --locale fr_FR
```

**Output:**
- `artifacts/catalog/manga/ssot_rollup/fr_FR_manga_catalog_ssot.csv` (390 rows)
- `artifacts/catalog/manga/ssot_rollup/fr_FR_manga_catalog_ssot.summary.json`
- `docs/manga/MANGA_FULL_CATALOG_PLAN_fr_FR.md`

### Conformance grid re-run

```bash
PYTHONPATH=. python3 scripts/qa/manga_m7_plan_coverage_grid.py
```

**Output:** `artifacts/qa/manga_m7_plan_coverage_grid_20260708.tsv`

---

## 3. Grid results (honest)

| Locale | Plans | Routing | Catalog SSOT | Cell | Blockers |
|---|---:|---|---|---|---|
| **fr_FR** | **390** | yes | **yes** | **GREEN** | none |
| ja_JP | 269 | yes | yes | GREEN | none |
| en_US | 268 | yes | no | PARTIAL | catalog_ssot_csv_missing |
| zh_TW | 274 | yes | no | PARTIAL | catalog_ssot_csv_missing |
| zh_CN | 268 | yes | no | PARTIAL | catalog_ssot_csv_missing |
| ko_KR | 266 | yes | no | HOLD | Q-MANGA-05 hold |
| pt_BR, de_DE, es_ES, es_US, it_IT, hu_HU, zh_SG, zh_HK | 0 | no | no | BLOCKED | format_routing_missing |

**Grid summary:** `locales=14 with_plans=6 green=2 partial=3` — **manga-m7-grid-green=NO**

fr_FR is the first Wave A locale at GREEN. Full grid cannot be green until:
- 8 locales get `format_routing.yaml` blocks + Wave A emit
- ko_KR hold clears
- shipped locales (en_US/zh_TW/zh_CN) get SSOT catalog rollups (out of fr_FR scope)

---

## 4. Machine summary

```
manga-m7-status=PARTIAL
manga-m7-fr-fr-derived-count=390
manga-m7-fr-fr-catalog-rows=390
manga-m7-fr-catalog-advanced=<commit-or-pr-pending>
manga-m7-fr-conformance=artifacts/qa/manga_m7_plan_coverage_grid_20260708.tsv
manga-m7-fr-catalog-status=complete
manga-m7-fr-catalog-blockers=none
manga-m7-locales-with-plans=6
manga-m7-zero-plan-locales=8
manga-m7-grid-green=NO
manga-m7-grid-green-locales=ja_JP,fr_FR
manga-100pct=NO
```
