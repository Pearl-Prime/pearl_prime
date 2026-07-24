# Lane 02 — Smoke: Ship the First Real zh-TW Waystream Book (Wave 1)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Localization for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Localization
- LANE=02_smoke_first_ship
- EXECUTION_MODE=local + github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch, PR, artifacts/qa/
- RESUME_SURFACE=artifacts/qa/waystream_zhtw_100_books_20260723/<cell>/

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- PR #211 body IN FULL, and its branch's `artifacts/qa/zhtw_first_book_20260723/
  TRACE_SUMMARY.md` (the prior diagnostic trail — you are continuing this, not
  starting fresh)
- PR #223 body (the fix you're building on — confirm it's merged before starting)
- phoenix_v4/rendering/locale_fallback_report.py
- phoenix_v4/qa/assembly_trace.py

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm `exercise-classifier-fix-merged=<sha>` signal exists
  (Lane 01's output) — if not, STOP, this lane is not unblocked yet.
- Re-check whether PR #211 has been superseded/closed by someone else already since
  this pack was authored — if so, read what shipped and stand down rather than
  redoing it.
- check open PRs for any other "zhtw-smoke" or "first zh-TW book" work in flight.

PRE-REQUISITE CHECKS:
- exercise-classifier-fix-merged=<sha> exists on origin/main. If missing, STOP and
  report BLOCKED, handoff to Lane 01.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- confirm the cell `gen_z_professionals x overthinking x spiral` is still the right
  pick (re-run the zh-TW backlog cross-reference against the CURRENT
  `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv` or its successor —
  do not assume PR #211's pick is still valid without re-checking, but it likely
  still is since it was chosen FOR being clean);
- re-run the exact four-piece-chord command from PR #211's TRACE_SUMMARY.md against
  current origin/main to confirm EXERCISE-BANK-RESOLUTION-01 now clears (it should,
  per Lane 01's signal) and to see what the NEXT gate is (PR #223 itself reports it
  hit an "accent-planner supply gap for AUTHOR_DISCLOSURE" next — confirm this is
  still the state, or whether it's changed).

PROVENANCE:
- research: PR #211 (cell selection + first diagnosis); PR #223 (the classifier fix)
- documents: docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- builds_on: scripts/run_pipeline.py canonical spine+production CLI;
  phoenix_v4/qa/assembly_trace.py; the now-merged EXERCISE classifier fix
- inventory: if you need to fix the AUTHOR_DISCLOSURE accent-planner supply gap,
  that inventory is EXTENDS (adding locale-aware supply, same pattern as the
  EXERCISE fix) — never REDUCED. If the fix is out of your WRITE_SCOPE (pipeline
  code, not translation), open a narrowly-scoped follow-on PR rather than
  patching it as a side effect of a translation lane.

MISSION:
Take ONE real zh-TW Waystream book (the PR #211 cell, or its live-reverified
replacement if that cell has since become non-viable) all the way through the
mandatory four-piece-chord production build to a real, gate-passing EPUB. This is
the smoke test that everything downstream (pilot, then 90 more books) depends on.
Diagnose and resolve whatever gate comes after EXERCISE-BANK-RESOLUTION-01 (expected:
an accent-planner AUTHOR_DISCLOSURE supply gap) — if it's a genuine content/atom gap,
fix the atom; if it's another locale-blind classifier bug (same shape as the EXERCISE
one), that's a real code fix, scope it narrowly and land it as its own PR before
returning to this lane's book. Do not force the gate to pass.

Command (adjust runtime-format per the catalog entry, do not invent):
  PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic overthinking --persona gen_z_professionals \
    --arc config/source_of_truth/master_arcs/gen_z_professionals__overthinking__spiral__F006.yaml \
    --pipeline-mode spine --quality-profile production --exercise-journeys \
    --locale zh-TW \
    --no-job-check --render-book \
    --render-dir artifacts/qa/waystream_zhtw_100_books_20260723/gen_z_professionals__overthinking__spiral/

(Confirm the exact arc filename against what's actually on disk — do not guess the
F006 suffix if the real file differs.)

DELIVERABLES:
- One real zh-TW EPUB (or the render-format equivalent) at
  artifacts/qa/waystream_zhtw_100_books_20260723/gen_z_professionals__overthinking__spiral/
- assembly_trace.md, locale_fallback_report.json, enrichment_audit.json,
  register_gate output, and a TRACE_SUMMARY.md bundling all four with a plain-English
  narrative, in the same directory.
- PR #211 superseded: comment on it linking this lane's PR, then close it (its
  diagnosis is preserved — don't delete the docs it added, just mark it resolved).
- ACTIVE_WORKSTREAMS.tsv row for this lane.
- Signal `zhtw-smoke-cell-shipped=<full-sha>` emitted.

SMALLEST SAFE BATCH:
- smoke: this whole lane IS the smoke test — one cell only. Do not pick a second
  cell "just in case" before this one either ships or is proven structurally
  unshippable with a documented reason.
- pilot / scale: out of scope for this lane — see Lanes 03/04.

HANG PREVENTION:
- poll interval: 10 minutes on the pipeline render (these can run long).
- no-progress rule: inspect stdout/stderr after two unchanged polls.
- hard stall rule: BLOCKED after three unchanged polls or 45 minutes of no new
  log lines, whichever comes first.
- max window: 3 hours (includes any narrow code-fix cycle for a second gate).

TESTS/PROOFS:
- register_gate output attached (state PASS/WARN/FAIL per rule honestly — a PASS
  here is "structurally clear," not "bestseller").
- locale_fallback_report.json shows 0 unexplained English fallbacks.
- If a code fix was needed: its own test file + a regression sweep of files that
  import the changed module (same pattern as PR #223's own sweep).

DO NOT:
- no gate weakening — a hard fail on this cell after a genuine attempt means either
  fix the real gap or report BLOCKED with the cell abandoned and a reason; never
  bypass locale-fallback, EXERCISE-BANK-RESOLUTION-01, or the contamination ratchet
  gate;
- no stale metrics — re-derive the backlog check live;
- no fake proof — attach real command output, not a description;
- no local-only finish;
- no giant batch first — this lane ships exactly one book.

LANDING CONTRACT:
- MERGED: PR opened (translation/QA-artifact content + any narrowly-scoped code fix
  as a SEPARATE PR if needed), required checks green, squash-merged, signal emitted,
  PR #211 closed with a comment.
- BLOCKED: exact blocker (e.g. "AUTHOR_DISCLOSURE accent-planner gap requires a
  pipeline-code fix outside WRITE_SCOPE, opened as follow-on PR #<N>, this lane's
  book cannot ship until that merges") + work pushed to a remote branch.

CLEANUP LEDGER REQUIRED:
- worktree: removed + pruned.
- local branch: deleted.
- remote branch: deleted post-merge.
- scratch files: none outside artifacts/qa/waystream_zhtw_100_books_20260723/ (that
  dir is the declared kept artifact — evidence, not scratch).
- background jobs: none left running.
- held artifacts: artifacts/qa/waystream_zhtw_100_books_20260723/gen_z_professionals__overthinking__spiral/
  (declared, kept).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/02_smoke_first_ship_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Localization
- LANE: 02_smoke_first_ship
- STATUS=MERGED|BLOCKED
- BRANCH: <name>
- PR: <url>
- MERGE_SHA: <full>
- SIGNAL: zhtw-smoke-cell-shipped=<sha>
- PROOF_ROOT: artifacts/qa/waystream_zhtw_100_books_20260723/gen_z_professionals__overthinking__spiral/
- TESTS: <register_gate result, locale_fallback result>
- CLEANUP: <ledger above, filled in>
- ACCEPTANCE_LAYER: structurally clear (Layer 1) — do not claim more
- NEXT_ACTION: dispatch 03_Pearl_Localization_pilot_10.md
```
