# Pearl Prime Quality Lane — Lift Curve (OPD-20260629-002)

Production QA matrix: `scripts/qa/run_duration_topic_matrix_qa.py`
(production profile, persona `corporate_managers`, deterministic spine; 29 cells = 12 durations + 17 topics@standard_book_60min).

Tracked reference so the lift curve does not live only in chat (the matrix artifacts were
untracked-and-wiped once by a sibling session's branch switch — the runner itself was committed in #3043).

## Measured lift curve

| Stage | PASS | Δ | Fix | PR |
|---|---:|---:|---|---|
| Baseline | 10/29 (34%) | — | — | — |
| Runner durability | — | — | commit untracked QA runner | #3043 |
| F4 closing-line | 17/29 (59%) | +7 | expand chapter-flow guarantee pools 3→17/17/12 (`book_renderer.py`) | #3055 |
| F6 cadence | 23/29 (79%) | +6 | add missing pre-gate F6 cadence break (`run_pipeline.py`) | #3060 |
| F2.D orphan strip | 24/29 (83%) | +1 | align orphan-strip word count with gate `.split()` (`register_output_strengthen.py`) | #3067 |

**34% → 83% (10 → 24/29), zero regressions across the wave, no FAIL cells remaining.**

These are core composer/renderer fixes shared by every buildable book — the lift is register-quality
across the whole ~23k buildable catalog, not just these 29 QA cells.

## Keystone correction (measure don't assume)

The original plan's keystone ("register F2 = scene re-stamp → reformat atoms to ARC_POSITION") and its
re-scope ("F1 selector/engine-routing") were both wrong against the per-cell `register_gate_report.json`:
- **F2** = broken slot-template renderer artifacts, not repetition.
- **F1** fires in **0 cells** (renderer dedupe absorbs it) — the engine-routing PR would have bought ~0.
- Real levers (by measured cell count): **F4 (+7), F6 (+6), F2.D (+1)** — all craft/code, no atom reformat.

## Remaining 5 non-PASS — NOT code-fixable in this wave

| cell | verdict | cause | lane |
|---|---|---|---|
| one_hour_book / financial_anxiety | ADVISORY | craft ONTGP 0.382 (warn<0.40) | topic-content (advisory only) |
| standard_book_60min / financial_anxiety | ADVISORY | craft ONTGP 0.386 | topic-content (advisory only) |
| standard_book_60min / adhd_focus | NO_ARC | atoms: 8.9K words, HOOK+5 engines, **no STORY/SCENE** | atom authoring |
| standard_book_60min / mindfulness | NO_ARC | atoms: **0 files (empty)** | atom authoring |
| deep_book_6h / self_worth | INCOMPLETE | 34.9K atom-words → ~48.7K enriched vs **50K floor** (~1.3K short, unique_ratio 1.0) | depth atom authoring |

The 2 craft-WARN cells are a topic-content signature (identical at both durations) — chasing a holistic
heuristic for 2 advisories would be gate-gaming. The 3 content gaps need Pearl_Writer/Qwen atom authoring
(no GPU, no paid LLM) — running the deterministic arc generator on empty pools would convert clean
`NO_ARC` into misleading `FAIL`. Both are a distinct next wave, not this one.

## Final matrix snapshot

See `PEARL_PRIME_QUALITY_LANE_MATRIX_20260629.md` (+ `.json`) for the full 29-cell grid at 24/29.
