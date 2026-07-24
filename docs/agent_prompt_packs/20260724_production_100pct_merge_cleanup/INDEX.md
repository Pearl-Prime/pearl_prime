# Prompt Pack — Production 100%: Merge, Clean, Reconcile (2026-07-24)

**Authored by:** Piper · **Operator directive:** analyze yesterday's handoffs, document
systems state (Pearl_PM × Pearl_Architect), fix all, bring to best 100% production,
clean up old/bad stuff, merge all that's best.

## Paste-ready next action
Paste `00_MASTER_DISPATCH_PROMPT.md` into a fresh Pearl_PM lead agent.
Operator items live in `OPERATOR_ACTIONS.md` (A–E) — five things only the operator can do.

## Contents
| File | What |
|---|---|
| `REPO_STATE_2026-07-24.txt` | Repo status in plain English (operator-facing) |
| `SYSTEMS_STATE_2026-07-24.md` | Pearl_PM × Pearl_Architect joint state snapshot (evidence-grounded) |
| `OPERATOR_ACTIONS.md` | Operator-only items A–E with unblock phrases |
| `00_MASTER_DISPATCH_PROMPT.md` | Pearl_PM dispatcher — order, watchdog, merge rules, closeout |
| `01_Pearl_GitHub_merge_queue.md` | Drain all 33 open PRs (merge / close-superseded / hold) |
| `02_Pearl_DevOps_main_green_and_protection.md` | Fix main's 2 CI breaks; enable branch protection |
| `03_Pearl_GitHub_worktree_branch_cleanup.md` | Delete 9 dead worktrees, sweep ~980 branches, rescue 6 work branches, land this branch's 9 stranded commits |
| `04_Pearl_PM_ssot_reconciliation.md` | PROGRAM_STATE + TSVs + DOCS_INDEX reconciled to 2026-07-24 truth |
| `05_Pearl_Prime_brand_wizard_regression.md` | Restore pt_BR lane, fix 3 red tests, resolve closed-unmerged #58 |
| `06_Pearl_Localization_zhtw_waystream_wave0.md` | Execute the 20260723 waystream pack's Wave 0 + smoke (reuse, not re-author) |
| `07_Pearl_Manga_land_stranded_ramp_gate.md` | Land 4 stranded manga branches; hold #243/#245 + scale at operator read gate |

## Dependency graph
Lane 02 → (signal MAIN-GREEN) → Lane 01 merges → Lanes 03/04/05 → Lane 06 (needs #223
+ waystream pack on main) ∥ Lane 07 (needs Lane 03's cherry-picks).
Operator items B (CF token) gates Lane 05's deploy verify; D gates Lane 02's
protection apply; E1/E2 gate manga + zh-TW scale.

## Key live-truth corrections this pack encodes (vs yesterday's handoffs)
1. PR #131 is NOT the blocker anymore — **#234 merged 2026-07-23T18:17Z**; #131/#231/#235 are close-as-superseded.
2. main has **no branch protection at all** (live 404) — CLAUDE.md's ruleset claim is currently false.
3. The zh-TW retranslate rescue branch is verify-then-DISCARD (batches broken/superseded), not a recovery target.

## Completion log (lanes append here)
- (empty — lanes append dated CLOSEOUT summaries)
