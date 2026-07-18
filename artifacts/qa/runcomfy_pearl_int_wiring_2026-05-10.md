# RunComfy Pearl_Int wiring — 2026-05-10

Workstream: `ws_runcomfy_pearl_int_wiring_20260509` (IMG-RENDER-DUAL-PATH-V1-01).

## Modules

- `scripts/image_generation/runcomfy_dispatch.py` — `load_token()` resolves `RUNCOMFY_API_TOKEN` from the environment (`RUNCOMFY_API_TOKEN`, `RUNCOMFY_API_KEY`, `RUNCOMFY_TOKEN`) then macOS Keychain (`phoenix-omega` / `RUNCOMFY_API_TOKEN`). `dispatch_workflow(..., dry_run=True)` validates the workflow JSON, surfaces deployment id + would-call URL, and reads the spend TSV for `cooldown` when cumulative spend ≥ $10 (aligned with `batch_runner.runcomfy_cost_check`).
- `scripts/image_generation/runcomfy_cost_tracker.py` — `poll_billing(dry_run=True)` returns mock vendor fields (no HTTP). Production path maps `GET https://api.runcomfy.com/v1/account/billing/summary` per `docs/specs/IMG_RENDER_DUAL_PATH_V1_SPEC.md` §4.D (Bearer `RUNCOMFY_API_TOKEN`). Optional `--write-tsv` appends a §4 rollup row.

## Batch runner integration

`scripts/image_generation/dispatchers/runcomfy_dispatcher.py` calls `dispatch_workflow` on dry-run so `batch_runner.dispatch(..., dispatch_path=runcomfy)` includes a `runcomfy_dispatch` preview dict.

`batch_runner._parse_spend_tsv` treats `cumulative_month_spend_usd` as a running total (last data row), not a sum of daily rows.

## Smoke (local, dry-run)

Run from repo root with `PYTHONPATH=.`.

```bash
PYTHONPATH=. python3 scripts/image_generation/runcomfy_dispatch.py \
  --workflow scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json \
  --dry-run
```

Sample (paths reflect local worktree):

```json
{
  "dry_run": true,
  "workflow_node_count": 8,
  "api_base": "https://api.runcomfy.net/prod/v1",
  "token_loaded": true,
  "cooldown": false,
  "status": "dry_run",
  "http_would_call": "https://api.runcomfy.net/prod/v1/deployments/677edba8-ace0-4b2b-bad2-8e94b9959065/requests"
}
```

```bash
PYTHONPATH=. python3 scripts/image_generation/runcomfy_cost_tracker.py --poll --dry-run
```

Sample:

```json
{
  "dry_run": true,
  "billing_url": "https://api.runcomfy.com/v1/account/billing/summary",
  "cumulative_month_spend_usd": 3.25,
  "usage_images_completed_mock": 12,
  "cooldown": false,
  "notes": "Mock vendor response; no HTTP request performed."
}
```

## Constraints

No paid RunComfy job submission and no billing HTTP in this Pearl_Int session; activation is a follow-up after operator confirmation.
