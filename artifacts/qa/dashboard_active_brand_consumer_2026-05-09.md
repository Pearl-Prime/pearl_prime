# QA — Brand Admin active/inactive panel consumer

**Date:** 2026-05-09  
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (P1 surface 2)  
**Dashboard path:** `brand-wizard-app/public/brand_admin.html`

## Implementation notes

- **Classifier:** `scripts/brand/active_brand_classifier.py` (PR #972) via `ActiveBrandClassifier.snapshot()`, `summarize_manga_slice()`, `manga_canonical_brand_ids()` — not modified.
- **JSON helper:** `scripts/brand/dashboard_classifier_endpoint.py` — `build_dashboard_payload()`, `--json`, `--serve` (default port `8765`, path `/active-brand-dashboard.json`).
- **UI:** Strip under `#main-progress` loads JSON with `fetch`; highlights current `brand_id` row after selection.
- **last_wizard_run:** Derived from YAML file mtime (UTC ISO); documented in spec as proxy for wizard materialization time.

## Smoke — CLI snapshot (this worktree)

Command:

```bash
cd <repo-root>
PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --json | head -n 45
```

Observed totals at snapshot time:

- **active:** 0  
- **inactive:** 61  
- **universe:** 61  

Sample trimmed JSON (first rows):

```json
{
  "schema_version": 1,
  "totals": { "active": 0, "inactive": 61, "universe": 61 },
  "manga_canonical_slice": { "active": 0, "inactive": 37, "total": 37 },
  "by_region": {
    "manga_canonical": { "active": 0, "inactive": 37, "total": 37 },
    "other_registry": { "active": 0, "inactive": 24, "total": 24 }
  },
  "brands": [
    { "brand_id": "adhd_forge_mystery", "status": "inactive", "reason": "no brand_wizard YAML found", "last_wizard_run": null, "region": "manga_canonical" }
  ]
}
```

*(Second row abbreviated; full output has 61 `brands` entries.)*

## Browser smoke

1. `PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --serve`
2. Serve static files (e.g. `cd brand-wizard-app && npm run dev`) and open `brand_admin.html`, **or** open the HTML file over `http://` so `fetch` to `127.0.0.1:8765` is not blocked as mixed content.
3. Confirm panel shows matching active/inactive counts and table; use **Refresh** after changing YAML.

## Tests

```bash
PYTHONPATH=. python3 -m pytest tests/brand/test_dashboard_classifier_endpoint.py -v
```

## Screenshots

Not attached in-repo; operator can attach PR screenshots from local browser once static server + JSON helper are running.
