# Pearl_GitHub State

Last verified: 2026-03-23
Owner: Pearl_GitHub

## Purpose

This file is the fast resume point for GitHub/repo-health work in Phoenix Omega.
It tracks:

- what Pearl_GitHub already did
- current verified system state
- what still needs to happen next

Read this with:

- [ps.txt](../ps.txt)
- [CLAUDE.md](../CLAUDE.md)
- [skills/pearl-github/references/repo_memory.md](../skills/pearl-github/references/repo_memory.md)

## Completed

- Verified `ps.txt` wiring to Pearl_GitHub
- Verified Pearl_GitHub skill, onboarding, and memory files exist
- Verified [scripts/manga/colab_manga_test.ipynb](../scripts/manga/colab_manga_test.ipynb) exists on `main`
- Verified current local/remote branch inventory from git, not from pasted thread history
- Confirmed cleanup end state:
  - only 4 local branches remain
  - only 1 live worktree remains
- Deleted merged remote branches:
  - `origin/codex/fix-wp-site-url-normalization`
  - `origin/codex/harden-pearl-news-pipeline`
- Added branch cleanup documentation:
  - [docs/BRANCH_CLEANUP_2026_03_21.md](./BRANCH_CLEANUP_2026_03_21.md)
- Added browser/Colab verification runbook:
  - [docs/COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md](./COLAB_AND_BROWSER_VERIFICATION_RUNBOOK.md)
- Added local integrations tooling and docs:
  - [scripts/integrations](../scripts/integrations)
  - [docs/WORDPRESS_LOCAL_SETUP.md](./WORDPRESS_LOCAL_SETUP.md)
  - [docs/MESSAGING_CHANNELS_LOCAL_SETUP.md](./MESSAGING_CHANNELS_LOCAL_SETUP.md)
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
  - [docs/BRANCH_DISPOSITION_2026_03_20.md](./BRANCH_DISPOSITION_2026_03_20.md)
- Wired a safe local credentials intake path for integrations:
  - [docs/LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md](./LOCAL_CREDENTIALS_INTAKE_RUNBOOK.md)
  - `scripts/integrations/intake_all_credentials_local.sh`
- Added conservative hint-prefill support to messaging setup from the local credentials source:
  - `scripts/integrations/setup_messaging_channels_local.sh`
- Added a short per-channel messaging requirements report:
  - `scripts/integrations/report_messaging_requirements_local.sh`
- Merged the AI Manga Dharma spec suite on `main`:
  - [PR #31](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/31)
  - [specs/AI_MANGA_PIPELINE_SUMMARY.md](../specs/AI_MANGA_PIPELINE_SUMMARY.md)
  - [specs/README.md](../specs/README.md)
- Added a manual self-hosted GitHub workflow path for maximum QA catalog runs:
  - `.github/workflows/max-quality-catalog.yml`
  - `scripts/run_max_quality_catalog.py`
- Opened a clean manga implementation branch from `origin/main`:
  - `agent/manga-pipeline-kernel`
- Added a high-level implementation map for future agents:
  - [docs/MANGA_IMPLEMENTATION_OUTLINE.md](./MANGA_IMPLEMENTATION_OUTLINE.md)
- Extended the first manga implementation slice with low-cost production scaffolding:
  - `panel_prompts.json` manifest compiler for free Colab and later backends
  - retrieval-first manga asset resolver
  - `config/manga/asset_selection_priority.yaml`
- Audited PR #21 / `codex/runtime-consolidation` at deeper commit and file-scope level:
  - [docs/RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md](./RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md)
- Added an hourly Pearl_GitHub autopilot path for repo alignment:
  - `scripts/git/hourly_repo_alignment.py`
  - `scripts/git/hourly_repo_alignment.sh`
  - [docs/PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md)
- **2026-03-22 governance audit session** — full read of `ps.txt` + all 10 referenced `.md` files, cross-checked against repo reality:
  - Identified 6 problems: phantom script references, required-checks discrepancy, missing state pointers, invisible Pearl_Int state, orphaned patch doc, non-existent files in onboarding table
  - `ps.txt` patched: push_guard gated with "if present", state pointers added for both agents, STATE + GOVERNANCE NOTES section added with YAML-over-prose precedence rule
  - `docs/PEARL_GITHUB_ONBOARDING.md` patched: `python3`, push_guard gated, fallback instructions, key files table cleaned, key docs list extended
  - Session documented locally during the governance audit; do not assume a committed session-status file exists on `main`
  - Changes are in working tree only — not committed or pushed
- **2026-03-23 GitHub governance normalization** — live ruleset drift was cleaned up end to end:
  - merged [PR #40](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/40)
  - deleted stale active rulesets `Main protection` and `main_branch_protection`
  - kept one active canonical ruleset on `main`: `Protect main`
  - removed the legacy `change-impact` alias job from `.github/workflows/change-impact.yml`
  - extended `scripts/ci/verify_github_governance.py --mode api --strict` to fail on conflicting active rulesets, forbidden legacy contexts, non-blocking required contexts, and required contexts not emitted by workflows
  - captured before/after evidence under [../artifacts/governance/rulesets/](../artifacts/governance/rulesets/)

## Current Verified Repo State

- Open PRs: `0`
- Recent repo-alignment / governance / manga cleanup PRs already landed on `main`:
  - [PR #33](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/33)
  - [PR #35](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/35)
  - [PR #36](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/36)
  - [PR #37](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/37)
  - [PR #40](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/40)
- PR #21 was closed as superseded after harvest planning
- Live GitHub branch protection is now normalized:
  - one active ruleset on `main`
  - canonical required checks are `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`
  - `Workers Builds: pearl-prime` is not merge-required
- Local `main` was previously hard-aligned to `origin/main`; individual checkouts may still have local-only changes and should verify with git before assuming alignment
- Safety backup branch exists:
  - `codex/main-autobackup-20260320-2124`
  - `codex/main-autobackup-20260322-112842`
- `agent/ops-docs-and-integrations` has been merged and deleted on remote
- `agent/pearl-github-state-followup` has been merged and deleted locally
- The AI Manga Dharma system is now documented on `main` as a 14-document spec suite under `specs/`
- A shardable max-quality catalog path now exists for GitHub-triggered QA runs across teacher-mode and regular mode
- The first manga build slice is now defined as a kernel:
  - config-backed style archetypes and panel layouts
  - deterministic visual prompt compiler in `phoenix_v4.manga`
  - seed teaching-library atom support for `panel_expression`
  - focused tests
- The low-cost render path is now clearer:
  - free Colab remains the validated renderer for seed images
  - manga can now export `panel_prompts.json` and resolve reusable assets before requesting new renders
  - ComfyUI is still planned as the later production backend, not current repo wiring
- The best single-file onboarding and state summary is now:
  - [docs/SYSTEM_STATE_MASTER.md](./SYSTEM_STATE_MASTER.md)
- The hourly Pearl_GitHub autopilot path is already on `main`

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

- [scripts/manga/colab_manga_test.ipynb](../scripts/manga/colab_manga_test.ipynb)

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

## Open Governance Items (from 2026-03-22 audit)

1. `docs/PEARL_GITHUB_PS_TXT_PATCH.md` is orphaned — delete or archive
2. `docs/LOCAL_GIT_DRIFT_PREVENTION_SOP.md` is referenced in onboarding but does not exist — create or remove reference
3. Keep [docs/SYSTEM_STATE_MASTER.md](./SYSTEM_STATE_MASTER.md) current when repo reality changes
4. Keep [docs/DOCS_INDEX.md](./DOCS_INDEX.md) and evidence inventory current when governance artifacts change

## Next Actions

1. Use [specs/AI_MANGA_PIPELINE_SUMMARY.md](../specs/AI_MANGA_PIPELINE_SUMMARY.md) as the governed entry point for manga implementation and review
2. Progress manga implementation in slices:
   - kernel/config
   - chapter artifact contracts
   - retrieval-first asset reuse
   - render/assembly
   - QC/memory
3. Execute the agreed delete set from [docs/BRANCH_DISPOSITION_2026_03_20.md](./BRANCH_DISPOSITION_2026_03_20.md)
4. For PR #21 specifically, use [docs/RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md](./RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md) as the execution plan
5. Open fresh harvest branches from `origin/main` for any kept feature payloads
6. Use the hourly Pearl_GitHub autopilot to keep repo-alignment reports current
7. Keep `runtime-consolidation` as a split-only audit branch, not a direct merge target
8. Continue executing the remaining harvest buckets and remote branch dispositions from the documented plans
9. Keep this file and `repo_memory.md` updated whenever branch inventory or Colab status changes
10. Use `report_messaging_requirements_local.sh` before channel integration work so the missing token and recipient-ID set is explicit
11. Treat free Colab as the current manga render engine and ComfyUI as a later scaling backend until actual ComfyUI workflow/config lands in repo
12. Use `max-quality-catalog.yml` for manual sharded self-hosted QA runs when local serial execution is too slow

## Pearl_GitHub Operating Reminder

When resuming:

1. Read `ps.txt`
2. Run preflight
3. Verify branch reality from git, not from thread text
4. Update this file when state changes
