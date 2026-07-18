# VERIFY-1 PROOF — Book #3 (gen_z_professionals × financial_anxiety)

**Date:** 2026-06-14
**Output dir:** `artifacts/pearl_prime/fix_wave_rebuild_20260614/book3/`
**Baseline:** `artifacts/pearl_prime/pilot_10/03_gen_z_professionals__financial_anxiety/`
(NO book.txt — aborted pre-render; stderr.log 6840B; `SystemExit EXERCISE-BANK-RESOLUTION-01`)
**Arc:** `config/source_of_truth/master_arcs/gen_z_professionals__financial_anxiety__spiral__F006.yaml`
**Build:** canonical spine CLI, `--pipeline-mode spine --quality-profile production`, Tier-1 (no paid LLM API).

---

## HEADLINE

| Claim | Result |
|---|---|
| **(a) It BUILDS** (baseline aborted pre-render on EXERCISE shortage) | **PROVEN** — `book.txt` 133,822 B, 12 chapters |
| **Primary verify signal** `slots_from_practice_library == 0` | **PROVEN** — `=0` (was the abort cause); EXERCISE now `slots_from_persona=120` |
| EXERCISE-BANK-RESOLUTION-01 gate fires | **0×** this run (baseline: SystemExit) |
| **(b) word_budget PASSES** | **NO** — 22,709 words > ceiling 22,000 (FAIL by 709; expected overshoot, book IS built) |
| **(c) no leaked atom-id labels** (`^ROLE vN$`) | **PROVEN** — 0 |
| **(d) no truncation orphan** (`sternum. still bracing.`) | **PROVEN** — 0 |
| **(e) no HOOK stubs** (`[Persona-specific hook for`) | **NO** — 12 present (HOOK bank is 29/30 placeholder atoms — data gap, not addressed by this lane) |
| register_gate verdict | **HARD_FAIL** (baseline: 8/8 built books HARD_FAIL) — driven by F2 (1 real SCENE-token defect + false-positive grammar heuristics) |

**Build exit code = 1**, but `book.txt` IS produced. Exit 1 = post-render quality gates
(chapter_flow, scene_anti_genericity, book_pass, book_quality_gate) reject in production
mode; this is the expected "book built, then evaluated" pattern (project memory:
"exit-1 on >20k word_budget overshoot is EXPECTED").

---

## PREREQUISITE: lane-fix corruption that blocked the build (NO_STORY_POOL)

The lane fix is *itself broken*: with the command run verbatim, the build aborted
**earlier than the baseline** — at the tuple-viability hard entry gate (before Stage 1)
with `Tuple viability: NO_STORY_POOL`.

Root cause: `atoms/gen_z_professionals/financial_anxiety/spiral/CANONICAL.txt` (lane-fix
file, mtime 14:29 today) appended valid band-fill atoms (v06+) but left **10 EMPTY stub
blocks** (header + lone `---`, no `path:` line, no body):
`RECOGNITION v02/v04, MECHANISM_PROOF v01/v03/v05, TURNING_POINT v02/v04, EMBODIMENT v01/v03/v05`.
`phoenix_v4.planning.assembly_compiler.validate_canonical_atom_file` rejects the WHOLE
file on any missing-`path:` block → `_load_story_atoms_for_engine` returns `[]` →
`check_tuple_viability` → `NO_STORY_POOL` → hard abort (`run_pipeline.py:1978`, "No override").

Note: the *same* 10-stub corruption is present in sibling spiral files (e.g.
`corporate_managers/financial_anxiety/spiral`) and in `*/overwhelm`, `*/watcher` files —
a latent corruption that only bites when that engine is selected. Book #5 (corp_mgr
financial_anxiety spiral) shows a `book.txt` in pilot_10 only because it was rendered in
an earlier run *before* this corruption landed; it would NO_STORY_POOL now too.

**Repair applied** (`repair_spiral_story.py`, corruption removal — zero content authored):
dropped the 10 empty stub blocks; kept all 33 blocks that have a real `path:`.
After repair: file validates **clean (0 errors)**, parses to **33 STORY atoms**, all 4
roles, **all 5 bands present** → tuple viability `PASS`. Original preserved at
`spiral_STORY_CANONICAL.BEFORE.txt` (md5 f151cd26d571de7312438e8332eb1507).

This repair is in-scope: VERIFY-1 says "build against the applied lane fixes," and the
lane fix shipped a malformed STORY file that makes *any* build of this tuple impossible.

---

## EXERCISE fix — the primary VERIFY-1 signal (PROVEN)

`atoms/gen_z_professionals/financial_anxiety/EXERCISE/CANONICAL.txt` (lane fix, 14:24
today) holds **13 EXERCISE atoms; 10 pass `_filter_practice_pool`** (v04–v13; v01–v03 are
list-of-questions, correctly rejected). All 10 survive practice-filter + doctrine
quarantine + `atom_passes_book_governance`.

Build audit (`enrichment_audit.json`):
```
slots_from_teacher           = 36
slots_from_persona           = 120   <- EXERCISE now resolves here
slots_from_registry          = 36
slots_from_practice_library  = 0     <- VERIFY SIGNAL (was the abort cause)
```
Authored EXERCISE prose verified present in `book.txt` (e.g. line 351 "find a wall.
Press your back flat against it…" = EXERCISE v09; line 368 "put the card down. Step 2:
place one hand on your sternum…" = EXERCISE v11).

The 3 residual `EXERCISE FALLBACK` warning lines in stderr are the practice_library
loader logging that it was *consulted*; the audit confirms it won **0** slots, so the
production gate correctly did not fire.

---

## §9 / book_pass gate (book_pass_report.json)

| §9 check | status |
|---|---|
| word_budget | **FAIL** (22,709 / [9000, 22000]) |
| band_distribution | PASS (12 distinct roles) |
| identity_stages | PASS |
| callback_completion | PASS |
| angle_journey_coherence | PASS |

word_budget is the **SOLE §9 failure** — exactly the healthy profile of the 9 books that
built ("all 9 built books PASS every §9 check EXCEPT word_budget"). ei_v2 PASS (composite
0.6316). chapter_flow FAIL = 1/12 (Ch 11 MISSING_CLEAR_POINT).

**word_budget note:** task PROVE blurb said "ceiling now 24000," but the live SSOT
(`config/format_selection/format_registry.yaml` → `standard_book.word_range`) is
**[9000, 22000]** with **no diff vs origin/main** (confirmed). The gate-baseline section of
the same task agrees ([9000,22000]). At 22,709 the book overshoots by 709 → word_budget
FAIL. Honest result: it does NOT pass; it overshoots within the "expected, book-still-built"
band.

---

## Per-defect before/after

Baseline counts are the task-provided cross-book aggregates (book #3 has no baseline
book.txt). Rebuilt counts are grepped on this run's `book.txt`.

| Defect | Signature | Baseline | Rebuilt #3 | Move | Verdict |
|---|---|---|---|---|---|
| D1 verbatim bridge | `What remains is the moment after the alarm fires` | 48 (6 books) | 0 | ↓ | clean (N/A topic) |
| D1 verbatim bridge | `What remains is the next ordinary moment` | 21 (all 9) | 2 | ↓ | within range |
| D1 success marker | `Ahead of you:` | 0 | 0 | — | (bank still bypassed; not regressed) |
| D2 truncation orphan | `Start with the pressure under the sternum. still bracing.` | 153 (9 books) | **0** | ↓ | **FIXED** |
| D2 (correct full form) | `sternum. That is the part still bracing` | 2/book | 19 | ↑ | correct form present |
| D2 body-scan orphan | `…into view. to fix anything you find.` | all books | **0** | ↓ | **FIXED** (correct form "You do not need to fix anything you find." present 1×) |
| D5 HOOK stub | `[Persona-specific hook for` | 71 (books 02/04/05) | **12** | n/a | **NOT FIXED** — 1 stub/chapter |
| D7 cross-persona bleed | `…hook for gen_z_professionals × burnout` | present (04/05) | **0** | ↓ | clean |
| D7 leaked atom-id label | `^(INTEGRATION|RECOGNITION|EMBODIMENT|TURNING_POINT|MECHANISM_PROOF) v\d+$` | 8 (02/07/08) | **0** | ↓ | **FIXED** |
| D7 leaked label | `INTEGRATION v06` standalone | present | **0** | ↓ | **FIXED** |
| D7 leaked label | `RECOGNITION v04` standalone | present | **0** | ↓ | **FIXED** |

---

## register_gate (origin/main 1269-line version; branch version gutted to 904)

**verdict = HARD_FAIL** (90 findings: 58 WARN, 22 FAIL, 10 HARD_FAIL).
HARD_FAIL is the baseline state for all 8 built books. Success criterion (verdict !=
HARD_FAIL) is **not** met.

All 10 HARD_FAIL findings are **F2** (task: "HARD_FAIL iff any F2"). Classification:

- **REAL defect (1):** F2.C ch1 — SCENE atom v05 template tokens `{weather_detail}` /
  `{street_name}` substituted into broken lowercase fragments:
  "…moves through the room. **through the window to your left.** … **traffic pulses below.**"
  Pre-existing SCENE-bank/renderer defect, independent of the lane fix.
- **FALSE POSITIVES (≈9):** F2.B flags legitimate sentence-final prepositions
  ("…input it should never be asked to extrapolate from." — valid prose); F2.C splits on
  abbreviation periods ("Payday hit at 6 a.m. and by the time…" — one valid sentence
  mis-split at "a.m.").

The DEFECT-7 register concern the task named (leaked `^TOKEN vN$` atom-id labels) is
**genuinely 0** — the register HARD_FAIL is driven by F2 grammar heuristics, not by the
leaked-label defect.

---

## Artifacts

- `book.txt` (133,822 B, 12 ch) — the rebuilt book
- `command.txt` — exact build + register-gate commands
- `repair_spiral_story.py` + `spiral_STORY_CANONICAL.BEFORE.txt` — prerequisite STORY repair
- `enrichment_audit.json` — `slots_from_practice_library=0` proof
- `book_pass_report.json`, `book_quality_report.json`, `chapter_flow_report.json`,
  `ei_v2_report.json`, `scene_gate/`, `register_gate_report.json`
