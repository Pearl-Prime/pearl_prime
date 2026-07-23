# Lane 03 — Pilot: 9 More Diverse Cells (Wave 2)

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Localization for Phoenix Omega.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Localization
- LANE=03_pilot_10
- EXECUTION_MODE=local + github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch, PR, artifacts/qa/
- RESUME_SURFACE=artifacts/qa/waystream_zhtw_100_books_20260723/PILOT_MANIFEST.tsv

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- Lane 02's handoff (artifacts/coordination/handoffs/02_smoke_first_ship_2026-07-23.md)
  and its TRACE_SUMMARY.md — reuse its method, don't reinvent cell selection

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm `zhtw-smoke-cell-shipped=<sha>` signal exists. If not,
  STOP, this lane is not unblocked yet.
- re-fetch `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv` or its
  successor (check `git log --oneline -- 'artifacts/qa/zh_tw*backlog*'` for anything
  newer first) — this is your live sufficiency signal, not a fixed number.

PRE-REQUISITE CHECKS:
- zhtw-smoke-cell-shipped=<sha> exists. If missing, STOP and report BLOCKED, handoff
  to Lane 02.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- candidate cell list: pick 9 (persona, topic, engine) tuples from
  config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml, DIFFERENT
  from the smoke cell (gen_z_professionals x overthinking x spiral), spanning AT
  LEAST 6 distinct personas (of the 14 in the catalog) and at least 5 distinct
  topics, to genuinely pilot diversity ("all sorts") rather than 9 near-identical
  cells;
- for each candidate, cross-check its zh-TW atom paths against the CURRENT
  authoring-backlog file (path-keyed lookup, same method Lane 02 used) — prefer
  zero or near-zero hits;
- run `check_tuple_viability` (or the production gate equivalent) for each
  candidate — a cell can be zh-TW-clean but structurally NO_BINDING; skip those;
- if a candidate cell hits a NEW gate class Lane 02 didn't see (not
  EXERCISE-BANK-RESOLUTION-01, not the accent-planner gap already fixed), that's a
  genuinely new finding — document it, don't silently route around it, and don't
  let one bad cell block the other 8 (swap it for the next-cleanest candidate and
  note the swap + reason).

PROVENANCE:
- research: PR #211 + Lane 02's shipped smoke cell (the proven method)
- documents: docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- builds_on: the now-merged EXERCISE classifier fix + whatever Lane 02 fixed for the
  accent-planner gap (if applicable)
- inventory: UNCHANGED — this lane is translation/build execution, not new pipeline
  code, unless a genuinely new gate class forces a narrow fix (same escalation rule
  as Lane 02: open it as its own PR, don't fold it into this lane silently)

MISSION:
Ship 9 more real zh-TW Waystream EPUBs (10 total including the smoke cell), stratified
across personas and topics, in ONE PR. This proves the mechanism generalizes before
committing to 90 more books across parallel Wave 3 batches. If fewer than 9 of your
10 candidates actually clear all gates, report the honest count — do not force weak
cells through, and do not silently substitute without documenting the swap.

DELIVERABLES:
- 9 real zh-TW EPUBs at
  artifacts/qa/waystream_zhtw_100_books_20260723/<persona>__<topic>__<engine>/ each
  with its own assembly_trace.md, locale_fallback_report.json, enrichment_audit.json,
  register_gate output.
- artifacts/qa/waystream_zhtw_100_books_20260723/PILOT_MANIFEST.tsv — one row per
  cell: persona, topic, engine, backlog-hit-count, tuple-viability result, gate
  outcome (shipped / blocked-and-why).
- ACTIVE_WORKSTREAMS.tsv row updated.
- Signal `zhtw-pilot-10-shipped=<sha>` emitted, with the honest shipped count (e.g.
  if only 8/9 cleared, the signal still fires but the manifest says 9/10 total, not
  10/10 — Wave 3 planning uses the real number).

SMALLEST SAFE BATCH:
- smoke: already done (Lane 02).
- pilot: this lane, 9 cells, 1 PR.
- scale: out of scope — see Lane 04, gated on this signal.

HANG PREVENTION:
- poll interval: 10 minutes per build.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED (for that specific cell only, not the whole lane) after
  three unchanged polls; swap to the next candidate rather than stalling the batch.
- max window: 6 hours for all 9 builds.

TESTS/PROOFS:
- register_gate output per cell, honestly labeled.
- locale_fallback_report.json per cell, 0 unexplained fallbacks.
- PILOT_MANIFEST.tsv as the single source of truth for what actually shipped.

DO NOT:
- no gate weakening;
- no stale metrics — re-derive the backlog file live, don't reuse Lane 02's numbers
  verbatim;
- no fake proof;
- no local-only finish;
- no giant batch first — 9 cells, not 90, in this lane.
- do not attach any of these to brand_deliveries/*.json or any GHL/storefront feed —
  QA path only.

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker + honest partial count + work pushed to a remote branch.

CLEANUP LEDGER REQUIRED:
- worktree: removed + pruned.
- local branch: deleted.
- remote branch: deleted post-merge.
- scratch files: none outside the declared QA dir.
- background jobs: none left running.
- held artifacts: artifacts/qa/waystream_zhtw_100_books_20260723/ (declared, kept).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/03_pilot_10_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Localization
- LANE: 03_pilot_10
- STATUS=MERGED|BLOCKED
- BRANCH: <name>
- PR: <url>
- MERGE_SHA: <full>
- SIGNAL: zhtw-pilot-10-shipped=<sha>
- PROOF_ROOT: artifacts/qa/waystream_zhtw_100_books_20260723/PILOT_MANIFEST.tsv
- TESTS: <per-cell register_gate + locale_fallback results>
- CLEANUP: <ledger above, filled in>
- ACCEPTANCE_LAYER: structurally clear (Layer 1) per shipped cell — do not claim more
- NEXT_ACTION: dispatch the 6 parallel lanes in 04_Pearl_Localization_scale_batches.md,
  assigning each batch its persona slice per that file's table (informed by which
  personas proved cleanest in this pilot)
```
