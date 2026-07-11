# REGRESSION_RESULTS — book system truth matrix 2026-07-11

Tip under test: `8338e5f30dd9f7d9691179e359571f7d730ec100` (`origin/main`)
Worktree: `/Users/ahjan/phoenix_omega_worktrees/book-system-truth-matrix-20260711`
Disk at render time: ~5.6Gi available (below 20G soft gate; text renders completed without ENOSPC)

## 1) Core regression pytest

Command:
```bash
PYTHONPATH=. python3 -m pytest -q \
  tests/test_spine_pipeline_integration.py \
  tests/test_spine_packet_preservation.py \
  tests/test_teacher_coverage_gate_blocks.py \
  tests/test_chapter_composer.py \
  tests/unit/rendering/test_story_introduction_bridge.py \
  tests/planning/test_accent_planner.py \
  tests/ci/test_accent_flagship_truth_gate.py
```

Result: **50 passed, 1 skipped, 2 failed** (log: `core_regression_pytest.txt`)

| Test | Result | Note |
|---|---|---|
| spine pipeline integration (most) | PASS | |
| `test_spine_gates_hard_records_production_policy` | FAIL | Non-chord / hard-gates path Reject on chapter_flow+register+book_quality — distinct from mandated chord render below |
| spine packet preservation (incl. Priya back-to-back deferral) | PASS | story-spacing preservation holds |
| teacher coverage gate blocks | PASS | gate wiring from #5545 live |
| chapter composer | PASS | |
| story introduction bridge | PASS | |
| accent planner | PASS | |
| `test_accent_flagship_truth_gate_artifacts_when_present` | FAIL | Pytest wrapper vs shipped proof dir reports missing/empty audit rows; **CLI truth gate PASS** on both shipped proof and fresh flagship (see below) |

## 2) Teacher + music verification tests

Music suite: **12 passed** (`music_pytest.txt`)
```bash
PYTHONPATH=. python3 -m pytest -v tests/test_music_overlay.py tests/test_music_manuscript_overlay.py tests/catalog/test_music_mode_branch.py
```

Teacher compile smoke: **2 passed** (`teacher_pytest.txt`)
```bash
PYTHONPATH=. python3 -m pytest -vv \
  'tests/test_teacher_mode_e2e_smoke.py::test_teacher_mode_compile_smoke[kenjin]' \
  'tests/test_teacher_mode_e2e_smoke.py::test_teacher_mode_compile_smoke[joshin]'
```
Note: smoke uses **burnout** + `--skip-quality-gates`, not the anxiety extended_book_2h production chord.

## 3) Fresh renders

| Surface | Exit / status | Evidence |
|---|---|---|
| flagship regular (anxiety×gen_z×F006×extended_book_2h + production chord) | **PASS** exit 0; book_quality Pass; chapter_flow PASS | `flagship_regular/` (book.txt 122732 bytes) |
| teacher kenjin (same chord + `--teacher kenjin`) | **FAIL** `TeacherCoverageError` | `teacher_kenjin/stdout.txt` + `teacher_kenjin/teacher_coverage_report.json` |
| music ahjan (same chord + `--music-mode with-lyrics --musician-id ahjan`) | **PASS** exit 0; book_quality Pass | `music_ahjan/` (book.txt 145107 bytes) + `music_overlay_audit.json` |

Teacher coverage gaps (live): required HOOK/SCENE/REFLECTION/EXERCISE/TAKEAWAY/INTEGRATION/THREAD = 20 each against format_id `MOD_pocket_guide`; available EXERCISE=12, TEACHER_DOCTRINE=5, PERMISSION=3, STORY=4.

## 4) Accent truth

```bash
PYTHONPATH=. python3 scripts/ci/check_accent_flagship_truth.py \
  --render-dir artifacts/qa/book_system_truth_matrix_2026-07-11/flagship_regular \
  --out artifacts/qa/book_system_truth_matrix_2026-07-11/ACCENT_FLAGSHIP_TRUTH_GATE_fresh.json
```
→ **PASS** (`accent_truth_gate_stdout.txt`, audit_count=7, errors=[])

Shipped proof re-check:
```bash
PYTHONPATH=. python3 scripts/ci/check_accent_flagship_truth.py \
  --render-dir artifacts/qa/proprime_accent_flagship_proof_2026-07-11 \
  --out artifacts/qa/book_system_truth_matrix_2026-07-11/ACCENT_FLAGSHIP_TRUTH_GATE_shipped_proof.json
```
→ **PASS**

## 5) Durable Waystream EPUB

Path: `artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub`
Inspection: `waystream_epub_inspection.md` — valid EPUB3 package (mimetype, container.xml, OPF, 12 chapters); sha256 `b9ca5f30e4dc771b702af3b1bf49a974a879e36fc8eea9bdabb5efd75421298b`
