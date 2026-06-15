# VERIFY-2 PROOF — Book #6 (educators × anxiety) bridge-repeater + register-failer rebuild

Date: 2026-06-14
Branch: `agent/gold-reference-7tier-redirect-20260530` (lane fixes committed on this branch vs origin/main)
Target: book #6, persona `educators`, topic `anxiety` (top §10 promote candidate; ONTGP 0.69, smallest overshoot in pilot).

## Build provenance

- **Baseline (DO NOT OVERWRITE):** `artifacts/pearl_prime/pilot_10/06_educators__anxiety/book.txt` (20378 words, angle PROTECTIVE_ALARM).
- **Rebuild:** `artifacts/pearl_prime/fix_wave_rebuild_20260614/bridge/book.txt` (24098 words, angle PROTECTIVE_ALARM, 12 chapters).
- **Arc used:** `config/source_of_truth/master_arcs/educators__anxiety__overwhelm__F006.yaml`.
  - NOTE: the task prompt named `educators__anxiety__spiral__F006.yaml`, which **does not exist**. Only `educators__anxiety__overwhelm__F006.yaml` exists for educators/anxiety. Baseline stderr confirms thesis=`emotional_overwhelm` → the baseline used the overwhelm arc. The "spiral" path in the prompt was generic boilerplate copied from book #5's command.txt.
- **Profile note:** the canonical command pins `--quality-profile production`. Production composed the full book but **aborted before writing book.txt** at the `scene_anchor_density` gate (`scripts/run_pipeline.py:874`, `gates_hard=True`) because chapter 12 repeats the teacher-wrapper template `"ahjan keeps pointing toward"` 4× > cap 3. That is a SEPARATE scaffolding-repetition defect, not one of the 10 targeted bridge/label defects.
  - To obtain an **identical-compose** book.txt for defect proof, the rebuild was re-run with `--quality-profile draft --render-book`. `_publishable_book` is `True` for BOTH production AND (draft + `--render-book`) [`run_pipeline.py:652-654`], and it is the ONLY compose-affecting profile flag in spine mode (`compose_from_enriched_book`'s `quality_profile` arg is "unused in pilot", chapter_composer.py:2975). So the composed prose is byte-identical to production; only gate-BLOCKING differs.
  - Production attempt evidence preserved: `prod_attempt_run_stderr.log`, `prod_attempt_scene_anchor_density_report.json`.
- Commands recorded in `command.txt`. Register gate run with the **origin/main** `register_gate.py` (1269 lines) because the branch copy is gutted (904 lines, -365); extracted to `/tmp/register_gate_main.py`.

## Defect table — BASELINE → REBUILD

| Defect | Signature | Baseline | Rebuild | Expected | Verdict |
|---|---|---:|---:|---|---|
| D1a verbatim bridge | `What remains is the moment after the alarm fires` | 10 | **1** | drop→~0 | **FIXED** (10× within-book repeat eliminated) |
| D1b generic bridge | `What remains is the next ordinary moment` | 1 | 2 | drop→~0 | PARTIAL (no 10× repeat, but +1) |
| D1 success marker | `Ahead of you:` | 0 | **0** | appear >0 | **NOT MET** (authored bank still not reached) |
| D2 truncation orphan | `sternum. still bracing` | 20 | **0** | drop | **FIXED** |
| D2 correct full form | `sternum. That is the part still bracing` | 2 | **22** | survive | **FIXED** (orphan replaced by full form) |
| D2 body-scan orphan | `to fix anything you find.` | 1 | 1 | drop | unchanged (embedded, 1× both) |
| D5 HOOK stub | `[Persona-specific hook for` | 0 | 0 | drop→0 | N/A (absent in book #6 both runs) |
| D7 leaked atom-id label | `^(INTEGRATION\|RECOGNITION\|EMBODIMENT\|TURNING_POINT\|MECHANISM_PROOF) v\d+$` | 0 | **0** | drop→0 | **CLEAN** |
| D7 ANY leaked label | `^[A-Z_]+ v\d+$` | 0 | **0** | drop→0 | **CLEAN** |

### Within-book bridge-repeat (the headline DEFECT-1 metric)

- **Baseline:** highest single-bridge-sentence frequency = **10** (`"...moment after the alarm fires..."` byte-identical 10×).
- **Rebuild:** highest single-bridge-sentence frequency = **2** (three distinct generic-pool sentences each appear 2×: "next ordinary moment", "The next pressure point is smaller than it sounds", "The next chapter begins where insight usually thins out").
- The catastrophic 10× verbatim repeat is eliminated and bridges now diverge across chapters. **However**, the strict criterion "no bridge repeats >1× within the book" is **NOT** fully met — 3 sentences repeat exactly 2× due to generic-fallback-pool exhaustion (5 options across 11 chapter boundaries when the data bank misses).

## Gate results — BASELINE → REBUILD

| Gate | Baseline | Rebuild | Notes |
|---|---|---|---|
| Register (main gate) verdict | HARD_FAIL | **HARD_FAIL** | F2 dropped **13 → 6**; verdict stays HARD_FAIL (any F2 → HARD_FAIL) |
| Register F2 count | 13 | **6** | residual F2 are NOT label-leaks: F2.B sentence-end-preposition ×4 (ch2,ch11), F2.E colon-no-content ×1 (ch1), F2.D sub-4-word-paragraph ×1 ("Small Exposures" subhead ch7) |
| Leaked-label lines (`^TOKEN vNN$`) | 0 | **0** | clean |
| word_budget (`book_pass_report.json`) | PASS (20378 ≤ 22000) | **FAIL** (24098 > 22000) | ceiling IS [9000,22000] (DEFECT-6 fix present) but rebuild **overshot** the ceiling by 2098 words |
| §9 band_distribution | PASS | PASS | |
| §9 identity_stages | PASS | PASS | recognition/mechanism/integration |
| §9 callback_completion | PASS | PASS | |
| §9 angle_journey_coherence | PASS | PASS | |
| chapter_flow | PASS | PASS (0/12) | |
| EI v2 | — | PASS (0.65) | |
| bestseller craft / ONTGP | — | PASS (0.67) | |
| scene_anti_genericity | WARN | WARN | unchanged |
| scene_anchor_density | PASS | **FAIL** | ch12 `"ahjan keeps pointing toward"` ×4 > cap 3 (teacher-wrapper repeat; would block a production write) |

## Root-cause: why "Ahead of you:" (the DEFECT-1A data-bank success marker) still = 0

The fix (`_resolve_emotional_job` + `_select_bridge_candidate(bridge_type="thread_fallback", …)`) **works in isolation** — every per-chapter emotional_job (`recognition, mechanism, deepening, reframe, practice, integration, resolution`) resolves and the `thread_fallback` bank returns an `"Ahead of you:"` candidate (verified directly against `config/rendering/bridge_transition_families.yaml:7373`).

But in the real book it returns `None`, falling through to the literal pool, because:
1. The spine path renders chapters via `golden_chapter_synthesis.compose_golden_spine_chapter` → `compose_chapter_prose`, which shares ONE book-level `bridge_memory` across ALL bridge types (PIVOT, INTEGRATION, TAKEAWAY, THREAD). By the time the THREAD thread-forward is reached per chapter, the shared memory has already consumed the bank's candidates for that emotional_job/position bucket → `_select_bridge_candidate` returns `None` → `_fallback_thread` drops to its literal pool.
2. Simulating the per-chapter loop with a shared `BridgeMemory` reproduces ~6/11 bank hits, yet the on-disk book shows 0 — indicating cross-bridge-type memory contention is even more aggressive at runtime than a thread-only simulation predicts.

This is a real residual: the data-driven bank is reachable in principle (fix A is wired) but is starved by shared-memory contention before THREAD slots are served. The literal fallback pool (fix B/C) is doing the heavy lifting and successfully kills the 10× cross-book repeat, but its 5 generic options are too few to guarantee zero within-book repeats.

## Overall verdict: PARTIAL

PROVEN beyond doubt:
- DEFECT-1 verbatim cross-book bridge: the 10× byte-identical within-book repeat is eliminated (max repeat 10 → 2).
- DEFECT-2 truncation orphan: fully fixed (`sternum. still bracing` 20 → 0, replaced by the correct full sentence 2 → 22).
- DEFECT-7 leaked atom-id labels: 0 → 0 (clean; book #6 never carried them — the leaks live in books 02/07/08).
- Register F2 halved (13 → 6).

NOT met (the prompt's stated PROVE bar requires all):
- `Ahead of you:` success marker still 0 (data bank starved by shared bridge_memory; see root-cause).
- Max within-book bridge repeat = 2, not ≤1.
- word_budget FAILS (rebuild 24098 > 22000 ceiling; baseline 20378 passed).
- Register verdict still HARD_FAIL (6 residual F2, none of them label-leaks).
