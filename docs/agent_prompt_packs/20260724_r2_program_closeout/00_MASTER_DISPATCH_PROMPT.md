# 00 — Master Dispatch (Pearl_PM) — R2 Offload Program Closeout

```text
EXECUTE. Do not stop at plan, at PR-open, at tests-running, or at "cleanup later".
End each dispatched lane MERGED or BLOCKED. You are Pearl_PM for Phoenix Omega,
dispatching the R2 / LFS offload closeout program. You do NOT author the lane work
yourself — you sequence, dispatch, verify each lane's CLOSEOUT, and reconcile.

Repo: Ahjan108/phoenix_omega_v4.8. Base every branch on origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- PROGRAM=r2-offload-program-closeout
- PACK=docs/agent_prompt_packs/20260724_r2_program_closeout/
- SCOPE=R2/LFS architecture + integration ONLY (NOT manga authoring/render)
- RESUME_SURFACE=artifacts/coordination/handoffs/r2-program-closeout_2026-07-24.md

READ FIRST (in order):
- docs/PROGRAM_STATE.md §"DevOps / repo hygiene" (lines ~185-190) — the STALE surface Lane A fixes.
- docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md — program authority. §7 wave table, §4.2 gate contract.
- artifacts/coordination/handoffs/disk_r2_offload_session_2026-07-23.md — prior session's own record ("2 of 5 PRs merged"); treat as leads, re-verify every claim.
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv → ws_lfs_setup_20260410 row.
- This pack's INDEX.md — the verified live-state table.
- docs/agent_brief.txt §10 (PROGRAM_STATE is SSOT), §17 (landing contract), §11 (correct the source, don't reproduce a false premise).

LIVE-TRUTH RECONCILIATION (do this before dispatching anything):
- git fetch origin; record origin/main SHA (pack snapshot = 82ef39572e — re-verify).
- Confirm Waves 3/4 really are on main (squash-merge trap — check the '→' emoji squash commits
  b702de43f9 / bccb188535 are ancestors of origin/main, NOT the '->' branch-head commits).
  `gh pr view 151 --json state,mergeCommit` and `gh pr view 161 ...` to confirm MERGED.
- Confirm `git ls-files assets/manga_catalog | wc -l` is still 0 (Wave-2 N/A premise).
- Confirm `grep -rl deep_verify_r2_offload .github/` is still empty (Lane B premise).
- If any premise has changed since 2026-07-24, correct the affected lane prompt's DISCOVERY
  section before dispatch — do not dispatch a lane on a false premise (agent_brief §11).

DISPATCH ORDER (sequential — each gates the next):
1. Lane A (01_R2_PROGRAM_RECONCILIATION.md) → Pearl_Int. Wait for MERGED.
2. Lane B (02_R2_DURABILITY_VERIFIER_WIRING.md) → Pearl_Int. Wait for MERGED.
3. Lane C (03_PHASE_B_HISTORY_REWRITE_DECISION_PACKET.md) → Pearl_Architect. Ends at a
   packet + explicit operator go/no-go gate — NOT an executed history rewrite.

Dispatch each by pasting the lane file into a fresh agent (or Agent tool). Do NOT run
lanes in parallel: A writes the truthful baseline B and C both cite; B proves the R2
blobs are retrievable, which C's risk section depends on.

WATCHDOG:
- After dispatching a lane, poll its branch/PR every ~5 min (`gh pr checks`, `gh pr view`).
- If a lane reports BLOCKED, capture the exact blocker, do NOT auto-advance to the next
  lane, and surface to the operator. Owner-gated items (Lane C decision, any >50-deletion
  merge in Lane A branch cleanup) require the operator's explicit "yes" in chat — never infer.
- No monitor-parking: if you arm a wait, drive it with active polling, not an idle end-turn
  ([[feedback_agent_monitor_parking]]).

LANDING CONTRACT: program is COMPLETE when Lanes A+B are MERGED, PROGRAM_STATE + spec +
ws_lfs_setup_20260410 all read truthfully, the durability verifier runs on a schedule with
a green proof, and Lane C's decision packet is delivered to the operator with a clear
go/no-go recommendation. Phase B itself is NOT executed under this pack.

CLEANUP LEDGER: prune the merged pre-squash branches
origin/agent/lane02-wave{3,4}-lfs-offload-20260723 (Lane A does this); no worktrees or
background jobs left running; name any HOLD.

HANDOFF: artifacts/coordination/handoffs/r2-program-closeout_2026-07-24.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_PM
- PROGRAM: r2-offload-program-closeout
- STATUS=COMPLETE|PARTIAL|BLOCKED
- LANES: A=<sha/PR> B=<sha/PR> C=<packet path + operator decision: GO/NO-GO/PENDING>
- SIGNAL: r2-program-closeout=<A-sha>,<B-sha>,C=<packet-path|pending>
- ACCEPTANCE_LAYER: Lanes A/B = system-working (merged + green scheduled proof);
  Lane C = decision-packet-delivered (owner ratification PENDING is the correct end-state).
- HANDOFF: artifacts/coordination/handoffs/r2-program-closeout_2026-07-24.md
- NEXT_ACTION: <e.g. "operator go/no-go on Phase B packet" or named held lane>
```
