# Lane 01 — Prereq Unblock (Wave 0)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=01_prereq_unblock
- EXECUTION_MODE=github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local + GitHub Actions
- PERSISTENCE_SURFACES=PR #131, PR #223
- RESUME_SURFACE=this prompt file + the two PR URLs

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- CLAUDE.md (Non-Negotiable Git Rules, Mandatory Preflight, Automated PR Governance)
- PR #211 body (diagnosis of the EXERCISE-BANK-RESOLUTION-01 blocker this unblocks)
- PR #223 body (the fix + its own stated known-pre-existing blocker)
- PR #131 body (the stub-fix this lane actually needs to land)

LIVE STATE RECONCILIATION:
- `gh pr view 131 --json state,mergedAt,statusCheckRollup,files`
- `gh pr view 223 --json state,mergedAt,statusCheckRollup,files`
- Both may have already merged or changed shape since this pack was authored
  (2026-07-23, origin/main `1f5217edb5`) — this program moves several PRs/hour.
  If both are already merged, this lane is DONE — verify, emit the signal, stop.
  Do not re-author work that already landed.

PRE-REQUISITE CHECKS:
- PR #131 exists and is OPEN or MERGED — if CLOSED without merging, STOP and report
  BLOCKED (someone abandoned the stub fix; do not silently re-author it yourself,
  that's out of this lane's narrow scope — escalate).
- PR #223 exists and is OPEN or MERGED — same STOP condition if CLOSED unmerged.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- PR #131's current CI status (its own required checks, not #223's);
- PR #223's current CI status, specifically whether `parse-sweep` / `Core tests`
  are still red for the SAME 4-file reason cited in its own PR body, or a NEW reason
  (if new, STOP — do not merge a PR with an unexplained new red check; escalate as
  BLOCKED with the new failure's evidence);
- whether #223 needs a rebase onto a newer main after #131 merges.

PROVENANCE:
- research: PR #211 (live-reproduced diagnosis, cell-independent)
- documents: docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md;
  phoenix_v4/rendering/locale_fallback_report.py
- builds_on: PR #223's own fix (registry_resolver._stamp_locale_exercise_metadata) —
  this lane does NOT write new code, it lands already-written, already-tested code
- inventory: UNCHANGED from this lane's perspective (no new capability authored here)

MISSION:
Land the two-PR chain that unblocks every zh-TW production build using
--exercise-journeys: merge #131 (unrelated pre-existing zh-CN stub fix), then verify
#223 goes green and merge it. This is a landing/verification task, not a fresh
implementation task — the code in #223 is already written and independently
regression-tested (681/682 in its own sweep). Do not modify #223's fix logic unless
you find a genuine, newly-introduced defect (if so, treat that as its own finding and
escalate rather than silently patching someone else's reviewed PR).

DELIVERABLES:
- #131 merged (or confirmed already merged).
- #223 rebased if needed, CI green, merged (or confirmed already merged).
- Signal `exercise-classifier-fix-merged=<full-sha-of-223-merge-commit>` recorded in
  this lane's handoff doc and in ACTIVE_WORKSTREAMS.tsv.

SMALLEST SAFE BATCH:
- smoke: confirm #131's own CI is green and it merges cleanly.
- pilot: confirm #223 goes green post-#131-merge (rebase if needed).
- scale: n/a — this is a 2-PR lane, no batching needed.

HANG PREVENTION:
- poll interval: 5 minutes on CI runs.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED after three unchanged polls (e.g. CI stuck queued).
- max window: 2 hours.

TESTS/PROOFS:
- `gh pr checks 131` and `gh pr checks 223` both green before merge.
- Post-merge: `git log --oneline -5 origin/main` shows both merge commits.
- proof root: this lane's handoff doc, linking both PR URLs + merge SHAs.

DO NOT:
- no gate weakening — do not touch `test_parse_sweep_is_green_tree_wide` or
  `_check_exercise_strict_canonical_gate` to force green;
- no stale metrics — re-verify both PRs' live state, do not trust this prompt's
  snapshot;
- no fake proof — link real CI run URLs, not a description of what should happen;
- no local-only finish;
- no giant batch first — this is inherently a 2-item lane, nothing to batch.

LANDING CONTRACT:
- MERGED: both #131 and #223 squash-merged, signal emitted, downstream Wave 1 lane
  unblocked.
- BLOCKED: exact blocker (e.g. "#131 CI red for an unrelated third reason") + PRs
  left in their current open state (do not force-merge a red PR).

CLEANUP LEDGER REQUIRED:
- worktree: none created by this lane (PR review/merge only) — if you branch to
  rebase #223, remove the worktree/branch after push.
- local branch: none, or removed per above.
- remote branch: #131/#223 branches deleted post-merge (standard squash-merge cleanup).
- scratch files: none expected.
- background jobs: none.
- held artifacts: none.

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/01_prereq_unblock_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_GitHub
- LANE: 01_prereq_unblock
- STATUS=MERGED|BLOCKED
- BRANCH: (n/a — reviewing existing PR branches)
- PR: #131, #223
- MERGE_SHA: <both, full>
- SIGNAL: exercise-classifier-fix-merged=<sha>
- PROOF_ROOT: artifacts/coordination/handoffs/01_prereq_unblock_2026-07-23.md
- TESTS: gh pr checks 131 / gh pr checks 223 (all green)
- CLEANUP: <ledger above, filled in>
- NEXT_ACTION: dispatch 02_Pearl_Localization_smoke_first_ship.md
```
