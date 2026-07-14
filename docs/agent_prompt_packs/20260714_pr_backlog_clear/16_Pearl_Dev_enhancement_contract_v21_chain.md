# Lane 16 — Enhancement Contract V2.1 sequential landing chain

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev for Phoenix Omega, lane 16 (Wave 1) of the PR Backlog Clear pack.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=enhancement-contract-v21-chain
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=cloud-agent
- PERSISTENCE_SURFACES=PRs #5581,#5585,#5595,#5596; artifacts/coordination/handoffs/
- RESUME_SURFACE=artifacts/coordination/handoffs/enhancement-contract-v21-chain_2026-07-14.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/agent_brief.txt (Bestseller Quality Anti-Drift Doctrine section in CLAUDE.md; Router v3 §1, §9, §17, §18)
- docs/DOCS_INDEX.md
- docs/ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md (if present at this SHA)
- docs/authoring/ANXIETY_FLAGSHIP_ENHANCEMENT_PILOT_PACKET_2026-07-13.md (if present)
- artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv
- memory: "Flagship-locked atoms: gate not content" and "Flagship assembly LOCKED" —
  this chain touches AUTHOR_DISCLOSURE near the frozen flagship golden; #5595
  exists specifically to scope it away from that golden. Do not re-open that fight.

PRE-REQUISITE CHECKS:
- foundation-triage-complete=<signal from lane 01> must exist. If missing, STOP, BLOCKED.
- Confirm PR order and current mergeable state live (this pack's snapshot is
  already hours old by the time you read it):
  `gh pr view 5581 --json mergeable,statusCheckRollup`
  `gh pr view 5585 --json mergeable,statusCheckRollup`
  `gh pr view 5595 --json mergeable,statusCheckRollup`
  `gh pr view 5596 --json mergeable,statusCheckRollup`
  At pack-authoring time: #5581 MERGEABLE, #5585 MERGEABLE, #5595 MERGEABLE,
  #5596 CONFLICTING. Re-verify — CI state and mergeable state both drift fast.

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm none of these 4 PRs has already been merged or
  closed by a sibling session — if so, that's success, stand down on that PR
  and continue the chain from wherever it actually is.
- Confirm the frozen flagship golden files (per memory: ANGLE_CALLBACK /
  PROTECTIVE_ALARM feeds, `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_*`) are
  NOT touched by any of these 4 diffs — `git diff origin/main...<branch> --stat`
  per PR, grep for `artifacts/qa/snapshots/CANONICAL_FLAGSHIP`. If any of the
  4 PRs touches a flagship golden file, STOP that PR and escalate — this is
  the exact drift class PR #5341 was reverted for previously.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- live mergeable/CI state of all 4 PRs;
- confirm #5581 and #5585 are truly independent of each other or sequential
  (check base branch / whether #5585's branch was cut after #5581 merged, or
  before — if before, #5585 may need a rebase once #5581 lands);
- confirm the flagship-golden-safety check above.

PROVENANCE:
- research: docs/ENHANCEMENT_CONTRACT_V2_WORKING_PRIORS_2026-07-13.md (as cited in #5581's own diff)
- documents: docs/DOCS_INDEX.md, the Enhancement Contract V2.1 authority doc chain
- builds_on: existing writing-overlay / accent_planner system (`phoenix_v4/planning/accent_planner.py`,
  `SOURCE_OF_TRUTH/accent_banks/`) — AUTHOR_DISCLOSURE extends this, does not replace it
- inventory: EXTENDS — #5585 adds AUTHOR_DISCLOSURE as a new selectable surface;
  #5595/#5596 are scope-correction fixes on top, not reductions of existing capability

MISSION:
- Land all 4 PRs in dependency order: #5581 → #5585 → #5595 → #5596, each
  gated on the previous one's merge SHA existing on main, rebasing the next PR
  onto the new main tip if its base has drifted.
- #5596 is CONFLICTING at authoring time — resolve the conflict by rebasing
  onto post-#5595 main (do not resolve by discarding either side's intent;
  read both diffs, reconcile, re-run its own tests).

DELIVERABLES:
- 4 merge SHAs, in order, each gated on the previous.
- Confirmation the flagship golden parity gate (`check_flagship_book_parity.py`)
  is still green after all 4 land.

SMALLEST SAFE BATCH:
- smoke: land #5581 alone (docs-only per its file list — lowest risk). Confirm
  CI green on main afterward.
- pilot: land #5585 (the actual feature PR) next, confirm
  `tests/planning/test_accent_planner.py` and the flagship parity gate both green.
- scale: land #5595, then rebase-and-land #5596 — these are narrow fixes, not
  a "batch," so no further ramp is needed beyond sequencing.

HANG PREVENTION:
- checkpoint: after each of the 4 merges, before starting the next.
- no-progress rule: if #5596's rebase conflict can't be resolved cleanly in
  one attempt, stop and report the exact conflicting hunks — do not guess-resolve
  a golden-file conflict.
- hard stall rule: if any single PR's CI has been red for the same reason
  across 3 rebase attempts, mark that PR (and everything after it in the chain)
  BLOCKED and report.
- max window: 60 minutes for the full 4-PR chain.

TESTS/PROOFS:
- Each PR's own CI (required checks) green pre-merge.
- `PYTHONPATH=. python3 -m pytest tests/planning/test_accent_planner.py -v` green after #5585.
- Flagship parity gate green after all 4: whatever command
  `scripts/run_production_readiness_gates.py` or `check_flagship_book_parity.py`
  documents as of the current SHA.

DO NOT:
- do not touch `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_*` to make a gate pass;
- do not merge #5596 by force-resolving conflicts in favor of one side without
  reading what the other side was fixing (it exists specifically to correct a
  scoping mistake in #5585 — losing that fix during rebase reintroduces the bug);
- no `--admin` merge, no `--no-verify`;
- no local-only finish.

LANDING CONTRACT:
- MERGED: all 4 PRs squash-merged in order, branches deleted, flagship parity
  gate confirmed still green, signal emitted.
- BLOCKED: name exactly which PR in the chain stalled and why; the ones before
  it that already landed stay landed (partial chain progress is real progress,
  report it as such, don't roll back successful merges).

CLEANUP LEDGER REQUIRED:
- worktree: declare if you used one for the #5596 rebase (likely yes — declare
  removed after use, or HOLD with reason if you need the operator to inspect
  the conflict resolution).
- local branch: deleted after each merge, or HOLD if a rebase is mid-flight.
- remote branch: deleted for #5581/#5585/#5595 on merge; #5596's branch deleted
  once its rebase-merge lands.
- scratch files: remove any diff/conflict-resolution scratch files.
- background jobs: none expected.
- held artifacts: none expected unless escalating a golden-file conflict.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/enhancement-contract-v21-chain_2026-07-14.md
  with all 4 merge SHAs, the flagship-golden-safety check result, and test output.

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Dev
- LANE=enhancement-contract-v21-chain
- STATUS=MERGED|BLOCKED
- MERGE_SHAS=<5581 sha>,<5585 sha>,<5595 sha>,<5596 sha>
- SIGNAL=enhancement-contract-v21-landed=<sha1>,<sha2>,<sha3>,<sha4>
- PROOF_ROOT=<flagship parity gate output>, <accent_planner test output>
- TESTS=<commands + pass/fail>
- CLEANUP=<ledger above, filled in>
- HANDOFF=artifacts/coordination/handoffs/enhancement-contract-v21-chain_2026-07-14.md
- NEXT_ACTION=<report to Pearl_PM dispatcher>
```
