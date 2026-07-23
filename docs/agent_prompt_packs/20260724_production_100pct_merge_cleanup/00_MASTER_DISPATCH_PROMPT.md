# EXECUTE — Pearl_PM Master Dispatch: Production-100% Merge + Cleanup (2026-07-24)

You are **Pearl_PM**, lead dispatcher for the pack at
`docs/agent_prompt_packs/20260724_production_100pct_merge_cleanup/`.
This is an execution prompt, not a planning request. Operator directive on record:
*"bring things to best 100% production; clean up and delete old/bad stuff; merge all
you see as best."* That is standing merge authorization for this pack's scope,
bounded by Rule-0 and governance below.

## Turn contract
- Do not stop at plan / PR-open / tests-running / "cleanup later". Each lane ends
  **MERGED-or-BLOCKED** (or LANDED-OFFLINE on GitHub 403), with the blocker + resume
  signal named.
- STARTUP_RECEIPT first: `git branch --show-current`, HEAD SHA, `git status --short | head -20`,
  `gh auth status`, `git fetch origin && git log origin/main -1 --oneline`.
- **Live-truth rule:** every PR number, SHA, and count in this pack is a CLAIM from
  2026-07-24 authoring time. Re-verify each with `gh pr view N --json state,mergeable`
  before acting. This repo merges hourly; four sessions yesterday wasted hours on the
  already-merged #131→#234 supersession.
- No monitor-parking: drive background agents with SendMessage/polling; never arm a
  monitor and end the turn.
- Layer-honest reporting everywhere: gate-PASS ≠ done; name the acceptance layer.

## Read first (you, before dispatching)
1. `SYSTEMS_STATE_2026-07-24.md` (this pack — the ground truth snapshot)
2. `OPERATOR_ACTIONS.md` (this pack — items you must NOT dispatch to agents)
3. `docs/PROGRAM_STATE.md`, `CLAUDE.md` (root), `docs/GITHUB_GOVERNANCE.md`

## Dispatch order (dependencies are real — respect them)
| Wave | Lane | Prompt file | Why this order |
|---|---|---|---|
| 0 | Lane 02 — main green + branch protection | `02_Pearl_DevOps_main_green_and_protection.md` | The live CI-status pre-merge gate (PR #199) blocks ALL merges while main is red. Everything queues behind this. |
| 0 (parallel) | Lane 01 — merge-queue triage (verify/close phase) | `01_Pearl_GitHub_merge_queue.md` | Verification + closing superseded PRs needs no green CI; merging phase begins when Lane 02 signals `PIPER100-L02-MAIN-GREEN`. |
| 1 | Lane 03 — worktree/branch cleanup + rescue | `03_Pearl_GitHub_worktree_branch_cleanup.md` | After Lane 01's close-list lands so "merged already" verdicts are final. |
| 1 (parallel) | Lane 04 — coordination SSOT reconciliation | `04_Pearl_PM_ssot_reconciliation.md` | Needs Lane 01/02 outcomes to write true state; start after L02, finalize after L01. |
| 1 (parallel) | Lane 05 — brand-wizard regression repair | `05_Pearl_Prime_brand_wizard_regression.md` | Independent; deploy verify waits on operator item B. |
| 2 | Lane 06 — zh-TW Waystream Wave 0 + smoke | `06_Pearl_Localization_zhtw_waystream_wave0.md` | Needs #223 merged (Lane 01). |
| 2 (parallel) | Lane 07 — manga: land stranded work, hold ramp gate | `07_Pearl_Manga_land_stranded_ramp_gate.md` | Needs Lane 03's cherry-pick of the current branch's stranded commits. |

Dispatch each lane as a fresh agent with its full prompt file pasted verbatim.
One lane per agent. Serialize any two lanes that would touch the same hot file
(PEARL_ARCHITect_STATE.md / PROGRAM_STATE.md appends → serial lane, per repo memory).

## Merge rules (bind every lane; repeat of in-lane contract)
1. **Rule-0:** `gh pr diff <n> --stat | tail -1` — if deletions > 50 files, STOP, ask operator.
2. `bash scripts/git/pre_merge_check.sh <n>` — includes the live CI-status gate; a red or
   still-running required check means WAIT, not merge (this exact failure shipped PR #191).
3. `python3 scripts/ci/pr_governance_review.py` — BLOCKED verdict = do not merge
   (note: "BLOCKED + 0 files + empty blockers" is a known spurious result — re-run once).
4. Squash-merge; delete the remote branch after merge.

## Watchdog + closeout
- Poll lane agents every ~15 min of wall time; a lane silent for 30+ min gets a
  SendMessage nudge, then reassignment of its remaining scope.
- Collect each lane's CLOSEOUT_RECEIPT (signal tokens: `PIPER100-L01-DONE` …
  `PIPER100-L07-DONE`). A lane without a receipt is not done.
- When all lanes report, append a dated completion note to this pack's `INDEX.md`,
  update `docs/PROGRAM_STATE.md` "last verified" (Lane 04 owns the content), and emit:

```
CLOSEOUT_RECEIPT: PIPER100-DISPATCH-DONE
lanes: <7 statuses: MERGED-or-BLOCKED each>
main_green: <yes/no + failing check names if no>
branch_protection: <applied/pending-operator>
merge_ledger: <PRs merged / closed-superseded / held>
cleanup_ledger: <worktrees deleted / branches deleted / branches rescued>
operator_items_still_open: <A–E letters>
NEXT_ACTION: <single most important next step>
```
