# SUMMARY — book system truth matrix 2026-07-11

**Acceptance layer:** `system working` (machine verification only; not PROVEN-AT-BAR; not catalog-scale 100%).

**Tip:** `8338e5f30dd9f7d9691179e359571f7d730ec100`  
**Worktree:** `/Users/ahjan/phoenix_omega_worktrees/book-system-truth-matrix-20260711`  
**Host:** Ahjans-MacBook-Air.local (Darwin arm64)

## PASS / FAIL by scoped surface

| Surface | Verdict |
|---|---|
| 1. Flagship regular spine path (production chord) | **PASS** |
| 2. Regular path carries composite / angle / story-plan / exercise-journey enhancements | **PASS** (see matrix) |
| 3a. Teacher mode compiles (kenjin/joshin smoke) | **PASS** |
| 3b. Teacher mode fresh anxiety×kenjin×extended_book_2h production render | **FAIL** — `TeacherCoverageError` (gate working; inventory short vs required slots) |
| 4. Music mode compile/overlays + fresh with-lyrics render | **PASS** |
| 5. Accent truth gate on fresh flagship | **PASS** (CLI); shipped proof CLI also PASS; pytest wrapper vs shipped dir still FAIL |
| 6. Story-spacing preservation (Priya back-to-back deferral tests) | **PASS** |
| 7. Durable Waystream EPUB readable package | **PASS** |
| 8. Enhancement-usage reporting artifact-backed | **PASS** (`ENHANCEMENT_USAGE_MATRIX.md`) |
| Core regression suite overall | **MIXED** — 50 pass / 2 fail (hard-gates policy test + accent pytest wrapper) |

## What this proves

On live main tip `8338e5f30…`, the mandated production chord still renders a readable flagship anxiety×gen_z×F006×extended_book_2h book with angle definition/callbacks, story_plan stories, composite_doctrine reflections, practice_library exercises, and planned exercise journeys; music-mode applies 72 lyric/reflection overlay injections; accent truth gate passes on the fresh flagship audit; story-spacing regression tests for Priya back-to-back deferral pass; teacher compile smoke for kenjin/joshin passes; and the shipped Waystream burnout EPUB remains a real EPUB3 with readable chapter prose.

## What this does NOT prove

Catalog-scale 100%; every teacher×cell production book-quality Pass; PROVEN-AT-BAR / blind-10 bestseller register; that anxiety×kenjin×extended_book_2h can clear the teacher coverage gate today; that `test_spine_gates_hard_records_production_policy` is green (it is not); that the pytest accent wrapper agrees with the CLI gate on the shipped proof dir; or that a fresh Waystream burnout rebuild would Pass (deliberately not re-run).

## Story-spacing note

`tests/test_spine_packet_preservation.py::test_compose_additive_chapter_prose_defers_scene_adjacent_and_back_to_back_stories` passes on tip after `#5547` (`a08403fa`). In the fresh flagship book, Priya remains the continuous story body across all 12 chapters (4 mentions/chapter in the rendered prose), e.g. Ch1 opens with “Priya's bedroom is dark except for the laptop screen…” and later “Priya submits the project update at 11:47pm…”, while the composer regression specifically asserts scene-adjacent / back-to-back Priya stacks are deferred rather than naively concatenated.

## Enhancement-atom usage across surfaces

On the fresh regular flagship, section-packet sources are explicit: 1 `ANGLE_DEFINITION` + 11 `ANGLE_CALLBACK` from `angle_atom`, 36 `STORY` from `story_plan`, 12 `REFLECTION` from `composite_doctrine`, 12 `EXERCISE` from `practice_library`, plus 12 planned `exercise_journeys`, with persona_atom filling the remaining spine slots and seven accent families assigned/rendered under the accent budget; music mode keeps that spine and adds 72 `music_overlay` injections (`with-lyrics` / ahjan); teacher EXERCISE/teacher_atom fill is **not** freshly proven on the blocked kenjin anxiety chord (coverage report persisted) and is only supported by compile smoke + the local historical modes mirror; the durable Waystream EPUB proves packaging, not enhancement-atom routing.

## Key evidence paths

- `REGRESSION_RESULTS.md`
- `ENHANCEMENT_USAGE_MATRIX.md`
- `flagship_regular/`
- `teacher_kenjin/`
- `music_ahjan/`
- `waystream_epub_inspection.md`
- `ACCENT_FLAGSHIP_TRUTH_GATE_fresh.json`
