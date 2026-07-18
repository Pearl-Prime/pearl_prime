# Harvest-to-main runbook

Purpose: **report-only** promotion intelligence. This lane is separate from [PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md) (hourly repo alignment). Alignment keeps checkout truth; harvest identifies **what should become clean PR slices** against `origin/main` without merging `codex/*` wholesale.

**Authority:** [docs/REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md](./REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md) Workstream B.

## Commands

```bash
bash scripts/git/harvest_to_main.sh
```

With label and custom output directory:

```bash
bash scripts/git/harvest_to_main.sh --report-label manual --report-dir artifacts/governance/main_harvest
```

## Output

- Timestamped: `artifacts/governance/main_harvest/main_harvest_<timestamp>.json` and `.md`
- Stable aliases: `latest_main_harvest.json`, `latest_main_harvest.md`

## What the report contains

- **`merge_policy`:** explicit rule — never merge `codex/*` convergence branches directly to `main`; use clean `agent/*` branches from `origin/main` and transplant spec-listed files only.
- **`pearl_prime_slices`:** three governed slices transcribed from [docs/PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md](./PEARL_PRIME_MAIN_RECOVERY_DEV_SPEC.md) (PR 1–3), each with file lists, recommended branch names, required tests, blocking dependencies, and per-path divergence vs `origin/main` when the convergence ref exists.
- **`branch_candidates`:** local and `origin/codex/*` branches with classifications (`already_on_main`, `needs_clean_pr`, `blocked`, `superseded`, `keep_open`) using [docs/BRANCH_DISPOSITION_2026_03_20.md](./BRANCH_DISPOSITION_2026_03_20.md) where applicable.
- **`auxiliary_items`:** spec-backed items that are not generic repo cleanup (e.g. salvage-audit signoff branch pointer, Pearl Prime source-repair lane marked `blocked` as new work).

## Modes

- **`online_live`:** `git fetch origin --prune` succeeded and `origin/main` is present.
- **`offline_degraded`:** fetch failed or `origin/main` missing — distances/diffs may be stale; read `notes` in the JSON.

## Cadence

Manual or low-frequency. Do **not** run hourly by default (see REPO_ALIGNMENT spec §6).

## Ownership

Pearl_GitHub runs the script and owns git/GitHub execution when implementing slices. Pearl_Dev implements transplants; Pearl_PM tracks workstreams. This runbook does not perform git writes.
