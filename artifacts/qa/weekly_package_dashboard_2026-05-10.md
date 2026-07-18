# Weekly package Brand Admin panel — implementation notes (2026-05-10)

**Program:** WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 · P2 surface 3 (weekly packaging)  
**Amendment:** AMENDMENT-2026-05-08-PRIORITIES (Q5 = Monday email + coordination file)

## What shipped

| Piece | Role |
|--------|------|
| `scripts/brand/weekly_package_endpoint.py` | Reads `artifacts/coordination/weekly_packages_<YYYY-MM-DD>.tsv` where the date is the **ISO Monday** for the week. Joins rows with **active** brands from `ActiveBrandClassifier`. **`--json`** to stdout; **`--serve --port 8767`** serves `GET /weekly-package-status.json` with `Cache-Control: no-store`. If the TSV is missing, response body is `{}`. |
| `brand-wizard-app/public/brand_admin.html` | Panel directly under the catalog active/inactive table: status pill (ready / pending / error), ready/pending counts, `last_updated`, download link when status is ready. Loads after the active-brand snapshot sets `window.__abActiveBrandIds`. Manual **Refresh** appends a cache-busting query string. |
| `tests/brand/test_weekly_package_endpoint.py` | TSV present/absent, mixed row statuses, payload change on TSV edit (refresh signal), CLI `--week-monday` / `--reference-utc`. |

## TSV contract (writer side)

Tab-separated header (column names case-insensitive):

```text
brand_id	status	download_url	last_updated
```

- **status:** `ready` \| `pending` \| `error` (unknown values treated as `pending` for counts).
- **download_url:** optional; first non-empty URL among `ready` rows is exposed as `download_url` in JSON when aggregate status is `ready`.
- **last_updated:** optional free-text / ISO string; JSON uses the **lexicographic max** per brand across rows.

Multiple rows per `brand_id` are rolled up: any `error` → aggregate `error`; else any `pending` → `pending`; else all `ready` → `ready`.

## Mock TSV sample

```text
brand_id	status	download_url	last_updated
rimuru_ie	ready	https://cdn.example/pearl/rimuru_week_2026-05-04.zip	2026-05-05T09:15:00Z
rimuru_ie	pending			2026-05-05T08:00:00Z
cmp_bp_founder_v1	pending			2026-05-05T07:30:00Z
ghost_lane	error		2026-05-05T10:00:00Z
```

`rimuru_ie` rolls up to **pending** (one ready, one pending). `ghost_lane` would show **error** if that brand is active in the classifier snapshot.

## Text-rendered UI sample (table body)

| brand_id | status | ready / pending | last_updated | download |
|----------|--------|-----------------|--------------|----------|
| alpha_brand | `READY` | 1 / 0 | 2026-05-05T10:00:00Z | [Download](https://files.example/alpha.tgz) |
| beta_brand | `PENDING` | 0 / 1 | 2026-05-05T11:00:00Z | — |

When the coordination file is absent, the endpoint returns `{}` and the dashboard still lists **active** brands with default pending rows and a footnote that the TSV is missing for that ISO week.

## Operator commands

```bash
PYTHONPATH=. python3 scripts/brand/weekly_package_endpoint.py --json
PYTHONPATH=. python3 scripts/brand/weekly_package_endpoint.py --serve --port 8767
```

Optional overrides: `--coord-dir`, `--week-monday YYYY-MM-DD`, `--reference-utc ISO-8601`, `--repo-root`, `--wizard-dir`.

Browser overrides: query `?wp_endpoint=http://127.0.0.1:8767/weekly-package-status.json` or `window.__WEEKLY_PACKAGE_STATUS_URL`.
