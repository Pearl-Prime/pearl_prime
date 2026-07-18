# Image batch runner scaffold — dual path (Pearl Star + RunComfy)

**Project:** PRJ-DUAL-PATH-IMAGE-RENDER-V1  
**Subsystem:** manga_pipeline + integrations  
**Workstream:** ws_image_batch_generation_orchestration_20260509 / IMG-RENDER-DUAL-PATH-V1-01 (#992)  
**Date:** 2026-05-09  

## What landed (this PR)

- `scripts/image_generation/batch_runner.py` — plan load, Q-IMG-1 locale-first sort, dry-run dispatch router, RunComfy spend cooldown ($10), dispatch TSV logging.
- `scripts/image_generation/dispatchers/pearl_star_dispatcher.py` — stub plan builder; live path raises until Pearl_Int Step 4.
- `scripts/image_generation/dispatchers/runcomfy_dispatcher.py` — stub plan builder; live path raises until RunComfy wiring.
- `tests/image_generation/test_batch_runner.py` — covers the five public behaviors in dry-run / file fixtures.
- This note — activation checklist for follow-up.

**Constraints honored:** stdlib only; no Pearl Star SSH; no RunComfy HTTP or spend; do not edit `artifacts/qa/parallel_image_generation_plan_2026-05-09.md` when it exists as the frozen catalog input.

## Plan markdown format (parser contract)

Fenced blocks labeled `batch` with `key: value` lines, for example:

````markdown
```batch
batch_id: stillness_001_panels
locale: ja-JP
dispatch_path: pearl_star
sequence: 10
panels: p_1_1, p_1_2
```
````

Optional fields are preserved as strings; `sequence` / `panel_count` parse as integers; comma-separated values become lists.

## Q-IMG-1 locale-first ordering

`batch_runner.priority_sort` ranks `ja-JP`, `zh-CN`, `zh-TW`, `ko-KR`, `yue-HK` ahead of other non-English locales, then `en-US` last. Tie-break: `sequence` ascending, then `batch_id`.

## RunComfy spend gate

- Input: `artifacts/qa/runcomfy_monthly_spend.tsv` (optional). Tab-separated; header row may include `spend_usd` or `amount_usd`.
- `runcomfy_cost_check()` sums spend; at **≥ $10** USD (`cooldown_threshold_usd`, default 10) sets `cooldown: true`.
- `run_batches(..., skip_runcomfy_on_cooldown=True)` skips RunComfy batches while still dispatching Pearl Star work.

## Dispatch log

- Output: `artifacts/qa/image_batch_dispatch_log.tsv` (created on first write).
- Columns: UTC timestamp, batch id, path, dry-run flag, status, notes, JSON payload snapshot.

## Activation checklist (follow-up PRs)

1. Pearl_Int Step 4: replace `pearl_star_dispatcher.dispatch(..., dry_run=False)` with SSH + `huggingface-cli` **or** ComfyUI API client; redact secrets in logs.
2. RunComfy: wire REST call using repo credential flow (`docs/INTEGRATION_CREDENTIALS_REGISTRY.md`); respect `runcomfy_cost_check` before enqueue.
3. Drop `RuntimeError` guards in dispatchers after smoke on Pearl Star + RunComfy sandboxes.
4. Point `--plan` at the frozen `parallel_image_generation_plan_2026-05-09.md` once present in `artifacts/qa/`.
5. Add CI job invocation (optional) calling `python3 scripts/image_generation/batch_runner.py --plan … --dry-run` on schedule or manual dispatch.

## Dry-run smoke (local)

If the frozen plan file is not yet present, generate a temporary markdown using the fenced `batch` format above, then:

```bash
PYTHONPATH=. python3 scripts/image_generation/batch_runner.py --plan /path/to/plan.md --dry-run | head -20
```
