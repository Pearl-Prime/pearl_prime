# RunComfy cost alert — Brand Admin panel (2026-05-10)

Workstream: `ws_runcomfy_cost_alert_dashboard_20260509` · Spec: IMG-RENDER-DUAL-PATH-V1-01 (#992).

## What shipped

- **`brand-wizard-app/public/brand_admin.html`** — RunComfy month-to-date panel: cap display (default **$10**), utilization bar with **80%** marker, warn banner when spend ≥ 80% of cap. Fetches JSON from local helper (default `http://127.0.0.1:8766/runcomfy-monthly-spend.json`). Override with query **`?rc_endpoint=`** or **`window.__RUNCOMFY_SPEND_URL`**.
- **`scripts/brand/runcomfy_spend_endpoint.py`** — Builds JSON from `artifacts/qa/runcomfy_monthly_spend.tsv` when present; **`--json`** stdout; optional **`--serve`** (default port **8766** to avoid clashing with the active-brand helper on **8765**).
- **`tests/brand/test_runcomfy_spend_endpoint.py`** — Missing file, normative cumulative (latest-by-date), 80% warn, legacy `spend_usd` sum, CLI smoke.

## TSV contract (Pearl_Int)

Normative append-only header (per `docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md` §4.C):

```text
date	dispatched_jobs_today	cumulative_month_spend_usd
```

The endpoint uses the **latest row by `date`** for `cumulative_month_spend_usd` (vendor cumulative, not summed across days).

Legacy tests / partial files may use **`spend_usd`** or **`amount_usd`** columns without `cumulative_month_spend_usd`; those rows are **summed** (matches `batch_runner` cooldown helper behavior).

## Mock sample (local QA)

If the artifact file is absent, **`--json`** still exits **0** with `status: "no_tsv"`. To exercise the UI locally, create `artifacts/qa/runcomfy_monthly_spend.tsv`:

```text
date	dispatched_jobs_today	cumulative_month_spend_usd
2026-05-09	0	7.9500
```

At **$7.95** on a **$10** cap, utilization is **79.5%** (below warn). Change the last field to **`8.00`** or higher to trigger **`budget_warn_80pct": true`** in JSON and the yellow bar + banner in Brand Admin.
