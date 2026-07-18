# Dashboard Active Brand Panel — V1 Spec

**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1  
**Subsystem:** `dashboard` + `brand_admin`  
**Authority:** `docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md` (classifier PR #972, frozen)  
**UI:** `brand-wizard-app/public/brand_admin.html` (canonical Brand Admin)

## Purpose

Executive visibility: per `brand_id`, show classifier-derived **active** vs **inactive** status, inactive **reason**, and a **last wizard** timestamp for active rows, plus universe totals and a **region** slice (manga canonical vs other registry). Locale is not in the classifier; `locale_breakdown` is always `null` in V1 JSON.

## Data contract (`GET /active-brand-dashboard.json`)

Produced by `scripts/brand/dashboard_classifier_endpoint.py` (`--serve` or `--json`).

| Field | Type | Notes |
|-------|------|--------|
| `schema_version` | int | `1` |
| `generated_at` | string | UTC ISO-8601 |
| `totals.active` / `totals.inactive` / `totals.universe` | int | From full classifier snapshot |
| `manga_canonical_slice` | object | `active`, `inactive`, `total` for 37-manga slice (`summarize_manga_slice`) |
| `by_region` | object | `manga_canonical` and `other_registry` each: `active`, `inactive`, `total` |
| `locale_breakdown` | null | Reserved; classifier has no locale dimension |
| `music_registry_deferred` | bool | From classifier |
| `brands[]` | array | Sorted by `brand_id` |
| `brands[].brand_id` | string | |
| `brands[].status` | `"active"` \| `"inactive"` | |
| `brands[].reason` | string | Empty when active |
| `brands[].last_wizard_run` | string \| null | UTC ISO mtime of `brand-wizard-app/brands/<id>.yaml` when active; else `null` |
| `brands[].region` | string | `manga_canonical` or `other_registry` |

## UI behavior

- **Placement:** Fixed strip directly under the main phase progress bar (visible on brand picker and after brand selection).
- **Refresh:** On picker render, after brand selection, and on **Refresh** button click. Manual refresh is sufficient for V1 (no polling interval).
- **Endpoint URL:** Default `http://127.0.0.1:8765/active-brand-dashboard.json`. Override with query `?ab_endpoint=<url>` or `window.__ACTIVE_BRAND_DASHBOARD_URL` before first fetch.
- **CORS:** Helper server sends `Access-Control-Allow-Origin: *` for local dev (Vite / file hosting).

## Operator runbook

From repository root:

```bash
PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --serve
```

Optional: `PYTHONPATH=. python3 scripts/brand/dashboard_classifier_endpoint.py --json` for CI or scripted checks.

## Out of scope (V1)

- Changing `scripts/brand/active_brand_classifier.py`
- Music-mode brand UX
- Weekly download packaging UI
