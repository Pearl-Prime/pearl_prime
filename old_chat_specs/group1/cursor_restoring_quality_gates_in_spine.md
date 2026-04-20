# Restoring quality gates in spine pipeline mode
_Exported on 4/16/2026 at 19:28:14 GMT+8 from Cursor (3.1.15)_

---

**User**

STARTUP — Restore Full Quality Stack to Spine Pipeline Mode
═══════════════════════════════════════════════════════════

You are operating in the Phoenix Omega repo (Ei V2 active).
Read before doing any work:

  1. docs/SESSION_UNITY_PROTOCOL.md
  2. scripts/run_pipeline.py          (full _run_spine_pipeline_mode function)
  3. phoenix_v4/qa/bestseller_editor.py
  4. phoenix_v4/qa/editorial_report.py
  5. phoenix_v4/quality/ei_v2/ei_adapter.py
  6. phoenix_v4/qa/book_pass_gate.py
  7. artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
  8. artifacts/coordination/ACTIVE_PROJECTS.tsv

Emit a STARTUP_RECEIPT before doing any work.

─────────────────────────────────────────────────────────────────────────────
WHAT HAPPENED AND WHY THIS FIX IS NEEDED
─────────────────────────────────────────────────────────────────────────────

When spine mode was introduced (PR #381) and made default (PR #408),
the following quality gates that were working on the registry path were
left behind — either explicitly skipped or never wired into
_run_spine_pipeline_mode:

  SKIPPED (explicit):
    - EI V2 compare         — line ~518: "skipped in spine mode"
    - Book pass gate         — line ~524: "SKIPPED (spine mode)"

  NEVER WIRED:
    - bestseller_editor.py  — thesis drift, full editorial report
    - editorial_report.py   — structured editorial JSON
    - memorable_line_gate.py
    - transformation_heatmap.py
    - identity_shift_gate.py
    - mechanism_escalation_gate.py

  PARTIALLY WIRED (already present, keep as-is):
    - chapter_flow_gate     ✓ wired
    - bestseller_craft_gate ✓ wired (advisory)
    - scene_anti_genericity ✓ wired (opt-in via --enforce-scene-gate)

The books produced by spine mode have been getting worse because
the quality system that was making them good got bypassed.
This session restores full parity. Do not break what already works.
Do not remove anything from the registry path.

─────────────────────────────────────────────────────────────────────────────
THE FIX — WIRE MISSING GATES INTO _run_spine_pipeline_mode
─────────────────────────────────────────────────────────────────────────────

FILE: scripts/run_pipeline.py
FUNCTION: _run_spine_pipeline_mode (starts ~line 327)

All gates below run AFTER prose is generated and cleaned.
All gates follow the same pattern already used for chapter_flow_gate:
  - try/except (non-crashing)
  - print status to stderr
  - append to _quality_gate_failures if gates_hard and gate fails
  - write report JSON to render_dir

─────────────────────────────────────────────────────────────────────
GATE 1 — EI V2 RIGOROUS EVAL (was: explicitly skipped)
─────────────────────────────────────────────────────────────────────

Replace the "skipped in spine mode" print with a real call.

The spine path does not have a ResolvedBook slot structure, but
scripts/ci/run_ei_v2_rigorous_eval.py already runs against book.txt
directly. Use that path.

  from scripts.ci import run_ei_v2_rigorous_eval  # or subprocess call

If direct import is messy, call as subprocess:
  python3 scripts/ci/run_ei_v2_rigorous_eval.py \
    --book-path <render_dir>/book.txt \
    --topic <topic_id> \
    --persona <persona_id> \
    --out <render_dir>/ei_v2_report.json

Parse ei_v2_report.json and:
  - Print summary to stderr: "EI V2: <status> — composite <score>"
  - Append to _quality_gate_failures if gates_hard and composite < 0.55
  - Merge into quality_summary.json

─────────────────────────────────────────────────────────────────────
GATE 2 — BESTSELLER EDITOR + EDITORIAL REPORT (was: never wired)
─────────────────────────────────────────────────────────────────────

  from phoenix_v4.qa.bestseller_editor import run_bestseller_editorial
  from phoenix_v4.qa.editorial_report import build_editorial_report

The bestseller_editor expects a plan dict and prose map.
For spine mode, build a minimal spine-compatible plan:
  spine_plan = {
      "source": "spine_pipeline",
      "topic_id": topic_id,
      "persona_id": persona_id,
      "teacher_id": teacher_for_enrich or "",
      "runtime_format_id": runtime_fmt,
      "chapter_count": len(enriched.chapters),
  }

Build prose_map from enriched chapters:
  prose_map = {
      f"chapter_{i}": chapter_prose
      for i, chapter_prose in enumerate(
          _extract_registry_chapters(prose)
      )
  }

Run:
  editorial_result = run_bestseller_editorial(spine_plan, prose_map)
  editorial_report = build_editorial_report(editorial_result)

Save:
  (render_dir / "editorial_report.json").write_text(
      json.dumps(editorial_report, indent=2)
  )

Print to stderr:
  "Editorial report: <status> — thesis drift <n> chapters, 
   ONTGP <score>, flow <score>"

Advisory only (do not block pipeline) unless gates_hard and
editorial_result.status == "FAIL".

─────────────────────────────────────────────────────────────────────
GATE 3 — MEMORABLE LINE GATE (was: never wired)
─────────────────────────────────────────────────────────────────────

  from phoenix_v4.quality.memorable_line_gate import evaluate_memorable_lines

  chapters = _extract_registry_chapters(prose)
  memorable_result = evaluate_memorable_lines(chapters)
  
Save to render_dir/memorable_line_report.json.
Print: "Memorable lines: <n> chapters with ≥2 quotable lines / <total>"
Advisory only.

─────────────────────────────────────────────────────────────────────
GATE 4 — TRANSFORMATION HEATMAP (was: never wired)
─────────────────────────────────────────────────────────────────────

  from phoenix_v4.quality.transformation_heatmap import (
      build_transformation_heatmap
  )

  heatmap = build_transformation_heatmap(prose, spine_plan)

Save to render_dir/transformation_heatmap.json.
Print: "Transformation arc: <status>"
Advisory only.

─────────────────────────────────────────────────────────────────────
GATE 5 — BOOK PASS GATE (was: explicitly skipped)
─────────────────────────────────────────────────────────────────────

  from phoenix_v4.qa.book_pass_gate import evaluate_book_pass

The book_pass_gate requires atom_ids and chapter_slot_sequence which
spine mode does not produce. Use the spine-compatible fallback:

  Read book_pass_gate.py to understand what inputs it needs.
  If it can accept prose + plan dict directly: use that.
  If it strictly requires atom_ids: skip only that sub-check and
    run the remaining checks (word budget, band distribution,
    identity_stages, callback_completion) using enrichment_audit.json
    data which IS available in spine mode.

  Save result to render_dir/book_pass_report.json
  Print: "Book pass gate: <status>"
  If gates_hard and status FAIL: append "book_pass" to
    _quality_gate_failures

─────────────────────────────────────────────────────────────────────
GATE 6 — QUALITY SUMMARY (consolidate all gate results)
─────────────────────────────────────────────────────────────────────

After all gates run, write a consolidated:
  render_dir/quality_summary.json

  {
    "source": "spine_pipeline",
    "topic_id": ...,
    "persona_id": ...,
    "runtime_format": ...,
    "gates": {
      "chapter_flow":       {"status": ..., "report": "chapter_flow_report.json"},
      "bestseller_craft":   {"status": ..., "overall_score": ...},
      "ei_v2":              {"status": ..., "composite": ..., "report": "ei_v2_report.json"},
      "editorial":          {"status": ..., "report": "editorial_report.json"},
      "memorable_lines":    {"status": ..., "report": "memorable_line_report.json"},
      "transformation_arc": {"status": ..., "report": "transformation_heatmap.json"},
      "book_pass":          {"status": ..., "report": "book_pass_report.json"}
    },
    "overall_status": "PASS" | "WARN" | "FAIL",
    "quality_gate_failures": [...],
    "governance_report": <_governance_report>
  }

─────────────────────────────────────────────────────────────────────────────
NON-NEGOTIABLE CONSTRAINTS
─────────────────────────────────────────────────────────────────────────────

  1. DO NOT touch the registry path. Not one line.
  2. DO NOT remove any gate that already exists anywhere.
  3. All new gate calls must be wrapped in try/except — pipeline must
     never crash because a quality gate throws.
  4. Gates are ADVISORY by default (warn, log, continue).
     Only block when gates_hard=True AND gate explicitly fails.
  5. If a gate cannot run in spine mode due to missing input structure,
     write {"status": "SKIPPED", "reason": "..."} to its report JSON.
     Do NOT silently skip. Every gate must produce a report file.

─────────────────────────────────────────────────────────────────────────────
TESTS
─────────────────────────────────────────────────────────────────────────────

Add to tests/test_spine_pipeline_integration.py (or new file):

  test_spine_produces_quality_summary_json
    → after spine run, render_dir/quality_summary.json exists and has
      all 7 gate keys

  test_spine_ei_v2_not_skipped
    → quality_summary gates.ei_v2.status is not "SKIPPED"

  test_spine_editorial_report_exists
    → render_dir/editorial_report.json exists after spine run

  test_spine_gates_advisory_by_default
    → pipeline exits 0 even when gates report FAIL (advisory mode)

  test_spine_gates_hard_blocks_on_failure
    → with gates_hard=True and forced gate failure, pipeline exits non-zero

─────────────────────────────────────────────────────────────────────────────
VERIFICATION PILOT
─────────────────────────────────────────────────────────────────────────────

After implementation, run:

  PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic anxiety \
    --persona gen_z_professionals \
    --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
    --teacher master_sha \
    --pipeline-mode spine \
    --runtime-format standard_book \
    --render-book \
    --render-dir artifacts/pilots/spine_full_quality_verify/ \
    --quality-profile draft \
    --no-job-check \
    --no-generate-freebies

Confirm render_dir contains ALL of:
  book.txt
  chapter_flow_report.json
  editorial_report.json
  ei_v2_report.json
  memorable_line_report.json
  transformation_heatmap.json
  book_pass_report.json
  quality_summary.json

And quality_summary.json has no gate with status "SKIPPED"
(except book_pass sub-checks that genuinely require atom_ids).

─────────────────────────────────────────────────────────────────────────────
GIT
─────────────────────────────────────────────────────────────────────────────

  Branch: agent/restore-spine-quality-gates from origin/main
  Commit scope: scripts/run_pipeline.py, test additions only.
                No other files unless a gate import requires a small
                spine-compatible adapter.
  Run push_guard + preflight before pushing.
  PR title: fix(pipeline): restore full quality gate stack to spine mode

─────────────────────────────────────────────────────────────────────────────
AGENT ROSTER
─────────────────────────────────────────────────────────────────────────────

Pearl_PM     — STARTUP_RECEIPT, register ws_restore_spine_quality_gates_20260413,
               CLOSEOUT_RECEIPT
Pearl_Dev    — all gate wiring + tests + pilot
Pearl_GitHub — branch, push-guard, preflight, PR

─────────────────────────────────────────────────────────────────────────────
DONE CRITERIA
─────────────────────────────────────────────────────────────────────────────

  ✓ ws_restore_spine_quality_gates_20260413 registered
  ✓ EI V2 no longer skipped in spine mode
  ✓ Book pass gate no longer skipped in spine mode
  ✓ editorial_report.json produced on every spine run
  ✓ memorable_line_report.json produced on every spine run
  ✓ transformation_heatmap.json produced on every spine run
  ✓ quality_summary.json consolidates all 7 gates
  ✓ No gate silently skipped — every gate writes a report file
  ✓ Registry path untouched
  ✓ All tests passing, no regression
  ✓ Pilot verification: all 8 report files present
  ✓ PR open; CLOSEOUT_RECEIPT lists every gate restored and
    its status in the pilot quality_summary.json


---

**Cursor**

STARTUP_RECEIPT
- Workstream: `ws_restore_spine_quality_gates_20260413` (registered in-session)
- Mode: Spine pipeline quality parity restore
- Scope locked: implement only spine-mode gate wiring and tests; registry path unchanged
- First step: read all required files, inspect `_run_spine_pipeline_mode`, then implement gated, non-crashing report generation for all requested quality gates.

I’ve loaded the required protocol and gate modules; next I’m inspecting `scripts/run_pipeline.py` and the current spine integration tests to wire each missing gate with report outputs and hard/advisory behavior exactly as requested.

I hit repo-wide search timeouts, so I’m narrowing to targeted directories now to map the correct EI and book-pass entry points before editing.

I found the exact callable entry points available in this repo (some names in your instructions differ), so I’m using the repo’s current APIs and now pulling `quality_bundle_builder` to mirror status/report conventions.

I’ve mapped the available APIs and am now patching `scripts/run_pipeline.py` to implement all six missing spine gates with per-gate report files, hard/advisory behavior, and consolidated `quality_summary.json` without touching registry mode.

Code edits are in place; I’m now running the spine integration test file to validate the new gates and summary behavior end-to-end.

Pilot verification run is executing now with your exact command; I’m monitoring it and will confirm all required report artifacts plus gate statuses as soon as it finishes.

Implemented spine-mode quality stack restoration in `scripts/run_pipeline.py` and added spine integration tests in `tests/test_spine_pipeline_integration.py`, while keeping registry mode logic untouched.

### What was restored in spine mode
- EI V2 is now executed (no longer skipped), with `ei_v2_report.json`, stderr summary, and hard-fail behavior when `gates_hard` and composite `< 0.55`.
- Editorial evaluation now runs and writes `editorial_report.json` with status, thesis-drift count, ONTGP score, and flow score.
- Memorable-line gate now runs and writes `memorable_line_report.json` with per-chapter results and aggregated quotable-line coverage.
- Transformation heatmap now runs and writes `transformation_heatmap.json`.
- Book pass now runs in spine-compatible fallback mode and writes `book_pass_report.json` (including explicit skipped sub-check metadata where atom-structure-specific checks are unavailable).
- Consolidated `quality_summary.json` now includes all 7 gate entries under `gates`, plus `overall_status`, `quality_gate_failures`, and `governance_report`.

### Tests added/updated
In `tests/test_spine_pipeline_integration.py`:
- `test_spine_produces_quality_summary_json`
- `test_spine_ei_v2_not_skipped`
- `test_spine_editorial_report_exists`
- `test_spine_gates_advisory_by_default`
- `test_spine_gates_hard_blocks_on_failure`

All spine integration tests passed:
- `python3 -m pytest tests/test_spine_pipeline_integration.py`
- Result: **11 passed**

### Pilot verification run
Executed your exact pilot command. Output directory `artifacts/pilots/spine_full_quality_verify/` contains all required files:
- `book.txt`
- `chapter_flow_report.json`
- `editorial_report.json`
- `ei_v2_report.json`
- `memorable_line_report.json`
- `transformation_heatmap.json`
- `book_pass_report.json`
- `quality_summary.json`

Gate statuses from pilot `quality_summary.json`:
- `chapter_flow`: FAIL
- `bestseller_craft`: PASS
- `ei_v2`: PASS
- `editorial`: WARN
- `memorable_lines`: WARN
- `transformation_arc`: PASS
- `book_pass`: PASS

No gate is `SKIPPED` in the final pilot summary.

---

CLOSEOUT_RECEIPT
- AGENT: Codex (Pearl_Dev execution lane)
- TASK: Restore full quality gate stack to spine pipeline mode
- COMMIT_SHA: no commits yet
- FILES_WRITTEN: `scripts/run_pipeline.py`, `tests/test_spine_pipeline_integration.py`
- STATUS: completed (implementation + tests + pilot verification)

I detected many unrelated working-tree changes outside this task while preparing to continue with GitHub steps. Per safety protocol, I stopped before branch/push/PR actions.  
If you want, I’ll proceed next with:
1) branch creation from `origin/main`,  
2) staging only these two files,  
3) push-guard + preflight,  
4) PR creation with your requested title.

---

**User**

Right A book. from Pearl Prime CLI. A book in the six hour format. A book in the 5 hour, 4 hour, 3 hour, 2 hour, 1 hour, 30 minute, 20 minute, 15 minute micro. Put it all in one Text file. and then Open it for me. The book topic is Anxiety for Gen Z Professionals. And... It's in teacher mode. with Ajahn is the teacher. So this is like all formats coming from Pearl. crime pipeline CLI so I can QA the system output. Open in Finder when you're done.

---

**Cursor**

Understood — I’ll generate Anxiety/Gen Z/Teacher Mode books across all requested runtimes via the Pearl Prime CLI, combine them into one QA text file, and then open that file in Finder for you. I’m first checking valid runtime format IDs and the teacher ID for Ajahn/Ahjan so the batch run succeeds cleanly.

I found your teacher ID (`ahjan`) and the supported runtime formats. I’m now running a single batch script that builds every requested runtime in order, captures failures for unsupported runtime IDs (3h/5h if absent), and writes one combined QA text file.

Batch generation is still running; I’ll keep monitoring until all formats finish, then I’ll open the combined QA file and reveal it in Finder.

Still in progress (it’s iterating through multiple full pipeline runs). I’m continuing to wait and will verify file creation immediately on completion.

The batch is still actively running (deep-format generations can take a while). I’m continuing to monitor and will finalize as soon as it exits.

Done. I generated the multi-format Pearl Prime CLI QA bundle and opened it for you (revealed in Finder + opened the file).

- Combined file: `artifacts/qa/pearl_prime_all_formats_anxiety_genz_ahjan/anxiety_gen_z_professionals_teacher_ahjan_all_formats.txt`
- Teacher mode used: `--teacher ahjan`
- Topic/persona used: Anxiety / Gen Z Professionals

Included in the file:
- 6h (`deep_book_6h`)
- 5h (`deep_book_5h`) → recorded CLI error
- 4h (`deep_book_4h`)
- 3h (`deep_book_3h`) → recorded CLI error
- 2h (`extended_book_2h`)
- 1h (`standard_book`)
- 30m (`short_book_30`)
- 20m (`micro_book_20`)
- 15m (`micro_book_15`)

Important QA note:
- `deep_book_5h` and `deep_book_3h` are not valid runtime IDs in this repo right now, so those sections in the file include the exact CLI failure (`Unknown runtime format`) and no `book.txt`.
- The other formats include the rendered book text plus CLI stdout/stderr in the same file for QA traceability.

