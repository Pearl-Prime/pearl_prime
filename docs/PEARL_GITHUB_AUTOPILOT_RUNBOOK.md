# Pearl_GitHub Autopilot Runbook

Purpose: keep local Phoenix Omega aligned with `origin/main` and continuously reduce GitHub drift without waiting for a manual cleanup session.

## What it does each run

1. Fetches and prunes remote refs.
2. Inspects open PRs and auto-merges the clean ones.
3. Ignores non-blocking Cloudflare preview failures for `pearl-prime`.
4. Refuses to merge draft PRs, PRs with unresolved review threads, or PRs with other failing or pending checks.
5. Creates a timestamped backup branch from local `main` if local `main` is dirty or diverged.
6. Hard-resets local `main` to `origin/main`.
7. Deletes local branches whose upstream is gone, unless they are checked out in a live worktree.
8. Writes a JSON and Markdown report under `artifacts/governance/repo_alignment/`.
9. Runs the Pearl_GitHub health check at the end of the cycle.

## Commands

Dry run:

```bash
bash scripts/git/hourly_repo_alignment.sh --dry-run
```

Live run:

```bash
bash scripts/git/hourly_repo_alignment.sh
```

## Output

- JSON: `artifacts/governance/repo_alignment/hourly_repo_alignment_<timestamp>.json`
- Markdown: `artifacts/governance/repo_alignment/hourly_repo_alignment_<timestamp>.md`

Each report records:

- merged PRs
- blocked PRs and why they were not merged
- whether a `main` backup branch was created
- whether local `main` was synced
- which stale local branches were pruned
- the tail of the health-check result

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

Ignored check failures:

- `Workers Builds: pearl-prime`

That Cloudflare preview is currently treated as non-authoritative for Pearl_GitHub merge decisions because it has failed across otherwise-green cleanup PRs.

## Governance note

This tool is for repo alignment and housekeeping. It is not a substitute for:

- `ps.txt`
- `docs/PEARL_GITHUB_ONBOARDING.md`
- `scripts/ci/preflight_push.sh`

Pearl_GitHub should still follow the onboarding order and state tracking discipline in `docs/PEARL_GITHUB_STATE.md`.
