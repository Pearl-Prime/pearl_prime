# Pearl_GitHub State

Last verified: 2026-03-20
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

## Current Verified Repo State

- Clean working branch for this work:
  - `agent/ops-docs-and-integrations`
- Branch ancestry versus `origin/main`:
  - behind `0`, ahead `1`
- Preflight:
  - `bash scripts/ci/preflight_push.sh` passes
- Push-guard:
  - `scripts/git/push_guard.py` is missing on this branch, so Pearl_GitHub must fall back to ancestry checks plus preflight
- Health check:
  - branch itself is clean
  - repo still warns that local `main` differs from `origin/main`

## Current Verified Branch Inventory

### Local branches kept

- `main`
- `codex/runtime-consolidation`
- `codex/pearl-news-cleanup`
- `codex/next-dev-clean`

### Remote branches still needing audit

- `origin/codex/ei-v2-gate-fix`
- `origin/codex/ei-v2-hybrid-only-clean`
- `origin/codex/ei-v2-hybrid-pr`
- `origin/codex/governance-100`
- `origin/codex/governance-evidence-pack`
- `origin/codex/pearl-news-cleanup`
- `origin/codex/pearl-news-workflows-clean`
- `origin/codex/phoenixcontrol-ui`
- `origin/codex/runtime-consolidation`
- `origin/codex/runtime-governance-core`

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

Not yet confirmed from visible output:

- Step 10 PDF export
- Step 11 provenance manifest
- Step 12 style comparison render
- Step 13 determinism result

Rule: do not mark the notebook complete until those four outputs are visibly confirmed.

## Next Actions

1. Open and review the PR for `agent/ops-docs-and-integrations`
2. Audit the 10 remaining unmerged remote `codex/*` branches
3. Decide what to do about local `main` being ahead of `origin/main` because of the autobackup commit
4. Verify Colab Steps 10-13 from actual notebook output before calling the manga test fully done

## Pearl_GitHub Operating Reminder

When resuming:

1. Read `ps.txt`
2. Run preflight
3. Verify branch reality from git, not from thread text
4. Update this file when state changes
