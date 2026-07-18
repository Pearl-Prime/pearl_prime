# Pearl_GitHub Autopilot Runbook

Purpose: keep local Phoenix Omega aligned with `origin/main` and continuously reduce GitHub drift without waiting for a manual cleanup session.

## What it does each run

1. Fetches and prunes remote refs when the network is available.
2. When online, inspects open PRs and auto-merges the clean ones.
3. Ignores non-blocking Cloudflare preview failures for `pearl-prime`.
4. Refuses to merge draft PRs, PRs with unresolved review threads, or PRs with other failing or pending checks.
5. When online and not `--dry-run`, creates a timestamped backup branch from local `main` if local `main` is dirty or diverged, then hard-resets local `main` to `origin/main`.
6. When **offline or degraded** (`mode: offline_degraded` in the report), skips remote mutations: no PR merges, no reset of `main` to `origin/main`, no deletion of local branches (candidates are still listed).
7. Deletes local branches whose upstream is gone, unless they are checked out in a live worktree — **only when online and not `--dry-run`**.
8. Writes a JSON and Markdown report under `artifacts/governance/repo_alignment/`.
9. Runs the Pearl_GitHub health check at the end of the cycle (or after a recoverable error once the report is assembled).

## Commands

Dry run:

```bash
bash scripts/git/hourly_repo_alignment.sh --dry-run
```

Dry run with a run label (for automation vs manual):

```bash
bash scripts/git/hourly_repo_alignment.sh --dry-run --report-label manual
```

Live run:

```bash
bash scripts/git/hourly_repo_alignment.sh
```

Automation-style label:

```bash
bash scripts/git/hourly_repo_alignment.sh --report-label automation
```

Branch census only (no PR merges, main sync, or pruning — still writes alignment report + census):

```bash
bash scripts/git/hourly_repo_alignment.sh --dry-run --branch-census-only --report-label audit
```

## Output

Always read the stable aliases (do not guess timestamped filenames):

- `artifacts/governance/repo_alignment/latest_hourly_repo_alignment.json`
- `artifacts/governance/repo_alignment/latest_hourly_repo_alignment.md`
- `artifacts/governance/repo_alignment/latest_branch_census.json` (when census runs)

Each run also writes timestamped copies: `hourly_repo_alignment_<timestamp>.json` / `.md`, and `branch_census_<timestamp>.json` when the branch census executes.

Invalid CLI flags still produce a failure-state alignment report (and refresh `latest_hourly_repo_alignment.*`) instead of exiting with only a argparse message and no artifact.

### Report fields (JSON)

- `mode`: `online_live` or `offline_degraded` (remote fetch or GitHub inspection failed).
- `run_label`: optional string from `--report-label`.
- `success`, `failure_reason`, `finished_at`: run outcome metadata (`failure_reason` set on argparse errors or subprocess failures).
- `run_context`: argv snapshot, HEAD / `origin/main` SHAs when resolvable, `gh_auth_ok`.
- `branch_census_summary`: counts and sample unmanaged / registry-only branches when census ran.
- `branch_census_path`: path to the timestamped full census JSON, or null if census skipped.
- `github_inspection_ok`: whether GitHub PR list/detail inspection completed (do not treat `open_pr_count` as live when this is false).
- `remote_errors`: strings describing fetch/GitHub/command failures.
- `local_branch`: current branch at repo root.
- `local_main_state`: parsed `git status --short --branch` for the `main` worktree (dirty, ahead, behind).
- `open_pr_count`: integer when GitHub inspection succeeded, else `unknown`.
- `merged_prs`, `blocked_prs`, `blocked_items` (structured), `backup_branch`, `synced_main`, `pruned_branches`.
- `remaining_branch_drift`: local branches with ahead/behind/gone/no-upstream signals.
- `followup_candidates`: suggested next steps (safe, non-executing hints).
- `notes`, `actions` (audit log).

If `mode` is `offline_degraded`, the Markdown summary states that remote/GitHub mutations were intentionally skipped where applicable. Do not claim live GitHub PR state when `github_inspection_ok` is false.

## Current decision policy

Autopilot is conservative.

- Auto-merge:
  - required checks green
  - no unresolved review threads
  - PR is mergeable
- Do not auto-merge:
  - draft PRs
  - unresolved review discussions
  - pending non-ignored checks
  - failing non-ignored checks
  - when review-thread GraphQL cannot be verified (treated as blocked)

Ignored check failures:

- `Workers Builds: pearl-prime`

That Cloudflare preview is currently treated as non-authoritative for Pearl_GitHub merge decisions because it has failed across otherwise-green cleanup PRs. It is also not part of the canonical required-check set for `main` branch protection.

## Governance note

This tool is for repo alignment and housekeeping. It is not a substitute for:

- `ps.txt`
- `docs/PEARL_GITHUB_ONBOARDING.md`
- `scripts/ci/preflight_push.sh`

Pearl_GitHub should still follow the onboarding order and state tracking discipline in `docs/PEARL_GITHUB_STATE.md`.

Promotion of feature payloads from convergence branches belongs in the separate harvest-to-main lane (`docs/REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md` Workstream B), not in this hourly loop.

## Branch policy registry and census

- Canonical registry scaffold: `config/governance/branch_registry.json` (patterns such as `agent/*`, `codex/*`, and explicit branch rows).
- Each alignment run loads this registry (when the file exists), compares live local + `origin/*` branch names against patterns and explicit rows, records ahead/behind vs `origin/main`, and writes a full census JSON plus `branch_census_summary` on the main report.
- Use `--branch-census-only` for audit-style runs that must not merge PRs or reset local `main`.
