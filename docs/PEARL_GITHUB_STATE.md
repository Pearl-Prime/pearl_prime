# Pearl_GitHub State

Last verified: 2026-03-21
Owner: Pearl_GitHub

## Purpose

This file is the fast resume point for GitHub/repo-health work in Phoenix Omega.
It tracks:

- what Pearl_GitHub already did
- current verified system state
- what still needs to happen next

Read this with:

- [ps.txt](/Users/ahjan/phoenix_omega/ps.txt)
- [CLAUDE.md](/Users/ahjan/phoenix_omega/CLAUDE.md)
- [skills/pearl-github/references/repo_memory.md](/Users/ahjan/phoenix_omega/skills/pearl-github/references/repo_memory.md)

## Completed

- Verified `ps.txt` wiring to Pearl_GitHub
- Verified Pearl_GitHub skill, onboarding, and memory files exist
- Verified [scripts/manga/colab_manga_test.ipynb](/Users/ahjan/phoenix_omega/scripts/manga/colab_manga_test.ipynb) exists on `main`
- Verified current local/remote branch inventory from git, not from pasted thread history
- Confirmed cleanup end state:
  - only 4 local branches remain
  - only 1 live worktree remains
- Deleted merged remote branches:
  - `origin/codex/fix-wp-site-url-normalization`
  - `origin/codex/harden-pearl-news-pipeline`
- Added branch cleanup documentation:
  - [docs/BRANCH_CLEANUP_2026_03_21.md](/Users/ahjan/phoenix_omega/docs/BRANCH_CLEANUP_2026_03_21.md)
- Added browser/Colab verification runbook:
  - [docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md](/Users/ahjan/phoenix_omega/docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md)
- Added local integrations tooling and docs:
  - [scripts/integrations](/Users/ahjan/phoenix_omega/scripts/integrations)
  - [docs/WORDPRESS_LOCAL_SETUP.md](/Users/ahjan/phoenix_omega/docs/WORDPRESS_LOCAL_SETUP.md)
  - [docs/MESSAGING_CHANNELS_LOCAL_SETUP.md](/Users/ahjan/phoenix_omega/docs/MESSAGING_CHANNELS_LOCAL_SETUP.md)
- Moved this work onto a clean branch from `origin/main`:
  - `agent/ops-docs-and-integrations`
- Merged PR #24:
  - [PR #24](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/24)
- Repaired local `main` safely:
  - saved autobackup commits on `codex/main-autobackup-20260320-2124`
  - reset `main` back to `origin/main`
- Deleted merged remote agent branch:
  - `origin/agent/ops-docs-and-integrations`
- Re-fired Colab cells 10-13 via local browser runner
- User explicitly confirmed Colab Steps 10-13 completed after Step 10 output was verified
- Completed branch-by-branch disposition audit for the 10 remaining remote `codex/*` branches:
  - [docs/BRANCH_DISPOSITION_2026_03_20.md](/Users/ahjan/phoenix_omega/docs/BRANCH_DISPOSITION_2026_03_20.md)
- Wired a safe local credentials intake path for integrations:
  - [docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md](/Users/ahjan/phoenix_omega/docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md)
  - `scripts/integrations/intake_all_credentials_local.sh`

## Current Verified Repo State

- PR #25 merged:
  - [PR #25](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/25)
- Local `main` now matches `origin/main`
- Safety backup branch exists:
  - `codex/main-autobackup-20260320-2124`
- `agent/ops-docs-and-integrations` has been merged and deleted on remote
- `agent/pearl-github-state-followup` has been merged and deleted locally

## Current Verified Branch Inventory

### Local branches kept

- `main`
- `codex/main-autobackup-20260320-2124`
- `codex/runtime-consolidation`
- `codex/pearl-news-cleanup`
- `codex/next-dev-clean`

### Remote branches still needing audit

Keep / deliberate audit required:

- `origin/codex/runtime-consolidation` — `5 behind / 165 ahead`

Likely merge-candidate audit:

- `origin/codex/ei-v2-hybrid-pr` — `11 behind / 1 ahead`
- `origin/codex/pearl-news-cleanup` — `5 behind / 1 ahead`
- `origin/codex/phoenixcontrol-ui` — `5 behind / 1 ahead`
- `origin/codex/runtime-governance-core` — `5 behind / 1 ahead`
- `origin/codex/governance-evidence-pack` — `10 behind / 3 ahead`
- `origin/codex/governance-100` — `11 behind / 5 ahead`

Likely archive / stale audit:

- `origin/codex/ei-v2-gate-fix` — `9 behind / 54 ahead`
- `origin/codex/ei-v2-hybrid-only-clean` — `98 behind / 7 ahead`
- `origin/codex/pearl-news-workflows-clean` — `8 behind / 26 ahead`

### Remote branch disposition decided

- `delete`
  - `origin/codex/ei-v2-gate-fix`
  - `origin/codex/ei-v2-hybrid-only-clean`
  - `origin/codex/governance-evidence-pack`
  - `origin/codex/pearl-news-workflows-clean`
- `harvest`
  - `origin/codex/ei-v2-hybrid-pr`
  - `origin/codex/governance-100`
  - `origin/codex/pearl-news-cleanup`
  - `origin/codex/phoenixcontrol-ui`
  - `origin/codex/runtime-governance-core`
- `keep-open`
  - `origin/codex/runtime-consolidation`

## Current Verified Colab Status

Notebook:

- [scripts/manga/colab_manga_test.ipynb](/Users/ahjan/phoenix_omega/scripts/manga/colab_manga_test.ipynb)

Confirmed from visible notebook output:

- Step 1 passed
- Step 2 passed
- Step 3 passed
- Step 4 passed
- Step 5 passed
- Step 6 passed
- Step 7 passed
- Step 8 passed
- Step 9 passed
- Step 10 PDF export passed
- Step 11 provenance manifest passed
- Step 12 style comparison render passed
- Step 13 determinism result passed

Evidence held in thread:

- visible Step 10 output was pasted and verified
- user explicitly confirmed: "all 13 done , i ran them"

## Next Actions

1. Execute the agreed delete set from [docs/BRANCH_DISPOSITION_2026_03_20.md](/Users/ahjan/phoenix_omega/docs/BRANCH_DISPOSITION_2026_03_20.md)
2. Open fresh harvest branches from `origin/main` for any kept feature payloads
3. Keep `runtime-consolidation` as a split-only audit branch, not a direct merge target
4. Keep this file and `repo_memory.md` updated whenever branch inventory or Colab status changes

## Pearl_GitHub Operating Reminder

When resuming:

1. Read `ps.txt`
2. Run preflight
3. Verify branch reality from git, not from thread text
4. Update this file when state changes
