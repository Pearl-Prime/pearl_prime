# Lane 04 — Scale: 90 More Cells, 6 Parallel Batches (Wave 3)

This file defines ONE shared lane prompt, dispatched 6 times in parallel (Batch A
through F) with a different `<BATCH_ID>` and `<PERSONA_SLICE>` substituted each time.
The 6 instances are mutually independent (disjoint cell lists) once the pilot lane's
manifest exists.

## Persona / target table (starting point — rebalance against live pilot + backlog data)

Waystream Sanctuary's catalog covers exactly 10 personas (verified: `ls
config/source_of_truth/book_plans_en_us/way_stream_sanctuary__*.yaml`, ~80 cells each,
800 total). Target ~9 cells/persona for this wave (90 total, on top of the 10 already
shipped by smoke+pilot) — but corporate_managers and tech_finance_burnout were
historically the two dirtiest zh-TW pools (92 and 117 rows respectively in the
863-row backlog snapshot), so Batch F is a flex/backfill batch, not a fixed persona
pair — it picks up wherever Batches A-E fall short of their target after the live
backlog check, from whichever personas still have the most clean cells left.

| Batch | Personas (target ~9 cells each unless noted) |
| --- | --- |
| A | corporate_managers, entrepreneurs |
| B | first_responders, gen_alpha_students |
| C | gen_x_sandwich, gen_z_professionals (exclude the smoke + any pilot cells already shipped for this persona) |
| D | healthcare_rns, millennial_women_professionals |
| E | tech_finance_burnout, working_parents |
| F | flex/backfill — fills the gap between Batches A-E's actual shipped total and 90, drawing from whichever persona(s) still have the most clean, unshipped, tuple-viable cells per the live backlog check |

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Localization for Phoenix Omega, running scale Batch <BATCH_ID>.

Repo: Pearl-Prime/pearl_prime
Start from a clean checkout of latest origin/main.

STARTUP_RECEIPT:
- AGENT=Pearl_Localization
- LANE=04_scale_batch_<BATCH_ID>
- EXECUTION_MODE=local + github_actions
- BACKGROUND_SAFE=yes
- RUNTIME_HOST=local
- PERSISTENCE_SURFACES=branch, PR, artifacts/qa/
- RESUME_SURFACE=artifacts/qa/waystream_zhtw_100_books_20260723/BATCH_<BATCH_ID>_MANIFEST.tsv

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- Lane 03's handoff + PILOT_MANIFEST.tsv (reuse its method; check which cells it
  already shipped so you don't duplicate them)
- the persona/target table above for your assigned batch

LIVE STATE RECONCILIATION:
- fetch origin/main; confirm `zhtw-pilot-10-shipped=<sha>` signal exists. If not,
  STOP, this lane is not unblocked yet.
- confirm no OTHER Batch <A-F> lane has already claimed your assigned personas'
  cells (check open PRs titled "waystream zh-TW scale batch" or similar, and check
  artifacts/qa/waystream_zhtw_100_books_20260723/ for existing per-cell directories
  before picking — cells already shipped by smoke, pilot, or a sibling batch are
  OUT of your pool).
- re-fetch the current zh-TW authoring-backlog file (check for anything newer than
  the 863-row 2026-07-23 consolidation first).

PRE-REQUISITE CHECKS:
- zhtw-pilot-10-shipped=<sha> exists. If missing, STOP and report BLOCKED, handoff
  to Lane 03.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- for each assigned persona, list ALL Waystream catalog cells
  (way_stream_sanctuary__default_teacher__<persona>__<topic>__<engine>[__format].yaml)
  not already shipped by smoke/pilot/a sibling batch;
- cross-check each against the live backlog file (path-keyed), prefer zero/near-zero
  hits; check tuple-viability; aim for topic diversity within your persona (don't
  ship 9 near-identical topics for one persona — spread across at least 4-5 distinct
  topics per persona if the catalog offers that many clean options);
- target ~9 cells per assigned persona (Batch F: fill the live-computed gap instead
  of a fixed target) — if a persona can't yield 9 clean/viable cells, ship what it
  can and report the honest shortfall in your manifest; do not force dirty cells
  through to hit a round number.

PROVENANCE:
- research: PR #211, Lane 02 + Lane 03 (the proven method + shipped precedent)
- documents: docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- builds_on: the merged EXERCISE classifier fix + any Lane 02 accent-planner fix
- inventory: UNCHANGED — translation/build execution only. If you hit a genuinely
  NEW gate class none of Lanes 02/03 saw, do not patch pipeline code inside this
  batch lane — document the blocked cell, skip it, and flag it in your manifest for
  a separate follow-on; keep shipping your other clean cells.

MISSION:
Ship as many real zh-TW EPUBs as your assigned personas can cleanly support, target
~9 per persona (or the live-computed gap for Batch F), in ONE PR per batch. Across
all 6 batches this reaches the 100-book program target — but the honest total may
land under 100 if some persona pools can't support their target; that's an
acceptable, reportable outcome, not a failure to paper over.

DELIVERABLES:
- Real zh-TW EPUBs at
  artifacts/qa/waystream_zhtw_100_books_20260723/<persona>__<topic>__<engine>/ each
  with assembly_trace.md, locale_fallback_report.json, enrichment_audit.json,
  register_gate output.
- artifacts/qa/waystream_zhtw_100_books_20260723/BATCH_<BATCH_ID>_MANIFEST.tsv — one
  row per cell attempted: persona, topic, engine, backlog-hit-count, tuple-viability
  result, gate outcome (shipped / skipped-and-why).
- ACTIVE_WORKSTREAMS.tsv row updated (append, don't overwrite sibling batches' rows).
- Signal `zhtw-scale-batch-<BATCH_ID>-shipped=<sha>` emitted with the honest count.

SMALLEST SAFE BATCH:
- smoke/pilot: already done (Lanes 02/03) — this lane starts directly at scale for
  its assigned slice, but within the slice, ship and verify a FEW cells before
  committing to the full ~9, in case your specific persona pair has its own
  unexpected gate.
- scale: ~9 cells/persona × your assigned personas, capped so this batch's PR stays
  under ~90-120 total files (roughly 15 books × ~6 files/book) — if your batch
  would exceed that, split into two PRs rather than one oversized one (PR
  governance warns >200 files, blocks >500 — stay well under with margin).

HANG PREVENTION:
- poll interval: 10 minutes per build.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: skip that specific cell (not the whole batch) after three
  unchanged polls; move to the next candidate.
- max window: 8 hours for the full batch.

TESTS/PROOFS:
- register_gate output per cell, honestly labeled (structurally clear, not
  bestseller).
- locale_fallback_report.json per cell, 0 unexplained fallbacks.
- BATCH_<BATCH_ID>_MANIFEST.tsv as this batch's source of truth.

DO NOT:
- no gate weakening;
- no stale metrics — re-derive the backlog file and the shipped-cell list live,
  every batch launches at a slightly different moment;
- no fake proof;
- no local-only finish;
- no giant batch first within your slice — verify a few cells before committing to
  the full ~9;
- do not attach any of these to brand_deliveries/*.json or any GHL/storefront feed —
  QA path only, this is not a commercial zh-TW Waystream launch;
- do not claim "100 bestsellers shipped" in any closeout — every cell is at most
  Layer 1 (structurally clear) under this program.

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker + honest partial count + work pushed to a remote branch.

CLEANUP LEDGER REQUIRED:
- worktree: removed + pruned.
- local branch: deleted.
- remote branch: deleted post-merge.
- scratch files: none outside the declared QA dir.
- background jobs: none left running.
- held artifacts: artifacts/qa/waystream_zhtw_100_books_20260723/ (declared, kept;
  shared across all 6 batches — do not delete other batches' subdirectories).

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/04_scale_batch_<BATCH_ID>_2026-07-23.md

CLOSEOUT_RECEIPT:
- AGENT: Pearl_Localization
- LANE: 04_scale_batch_<BATCH_ID>
- STATUS=MERGED|BLOCKED
- BRANCH: <name>
- PR: <url>
- MERGE_SHA: <full>
- SIGNAL: zhtw-scale-batch-<BATCH_ID>-shipped=<sha>
- PROOF_ROOT: artifacts/qa/waystream_zhtw_100_books_20260723/BATCH_<BATCH_ID>_MANIFEST.tsv
- TESTS: <per-cell register_gate + locale_fallback results>
- CLEANUP: <ledger above, filled in>
- ACCEPTANCE_LAYER: structurally clear (Layer 1) per shipped cell — do not claim more
- NEXT_ACTION: report shipped count to the dispatcher; once all 6 batches report,
  the dispatcher runs a final tally (real total vs. 100) and updates
  docs/PROGRAM_STATE.md Localization section with the honest number
```
