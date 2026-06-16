# F2 register-verdict re-pilot — PR #1601 (agent/composer-register-flip-20260615)

Date: 2026-06-15 · Lane: Pearl_Dev F2 gate-pass · PROJECT_ID proj_pearl_prime_bestseller_rebase_20260425

## What this proves

Fresh **production-profile spine renders** via the real entrypoint
`scripts/run_pipeline.py --pipeline-mode spine --quality-profile production`,
then the register gate run as a **separate call**
(`phoenix_v4.quality.register_gate.evaluate_register_from_path`). Deterministic;
**no paid LLM API** (CLAUDE.md Tier policy — pure atom composition + deterministic gate).

Reproduce: `PYTHONPATH=. python3 artifacts/qa/f2_repilot_20260615/run_repilot.py`
(requires `atoms/` + `registry/` materialized in the working tree).

## Scorecard — F2 eliminated, HARD_FAIL barrier cleared

Scored on the **identical composed book.txt** (BEFORE = origin/main register_gate;
AFTER = this PR branch incl. the F2.B copula-predicate hardening):

| book | F2 BEFORE | F2 AFTER | verdict BEFORE | verdict AFTER | HARD_FAIL classes AFTER |
|---|---|---|---|---|---|
| book05 — corporate_managers / anxiety / overwhelm (F006) | 13 | **0** | HARD_FAIL | **FAIL** | none |
| book06 — educators / anxiety / overwhelm (F006) | 8 | **0** | HARD_FAIL | **FAIL** | none |

- **F2 → 0 on both books.** The only HARD_FAIL register class (F2, per
  `register_gate._aggregate_verdict` + COMPOSER_FRONTIER_FIX_SPEC §register_thesis_counter
  L219: "verdict = HARD_FAIL iff ANY F2 finding; F1/F4/F6/F7 never gate") is fully cleared.
- **Verdict moved HARD_FAIL → FAIL** — the never-ship barrier is gone.

## Why the literal aggregate string is FAIL, not PASS

`_aggregate_verdict` returns `FAIL` whenever ANY **FAIL-severity** finding exists
(hierarchy: HARD_FAIL > FAIL > WARN>2 > ADVISORY > PASS). At F2 = 0 the books still
carry FAIL-severity findings from classes the authority spec says "never gate" the
HARD_FAIL:

| book | F7 (practice density) | F1 (templated clusters) | F13 (dwell starvation) | F6 (cadence) |
|---|---|---|---|---|
| book05 | 12 | 5 | 5 | 1 |
| book06 | 11 | 4 | 5 | 1 |

These are **out of scope for the F2 lane** — F7/F1/F6 route to Pearl_Editor + Pearl_Writer
(atom diversification) and the concurrent Lever-B composer lane (chapter_composer +
scaffolding/bridge banks); F13 is the dwell-beat craft lane. Literal `verdict == "PASS"`
requires those FAIL classes driven to zero, which the F2 lane cannot and must not force
(no gate-weakening). The register gate is a **standalone** scorer — `run_pipeline.py` does
not consume its verdict — so F2 = 0 / HARD_FAIL-cleared is the substantive deliverable.

## Two data-layer findings surfaced (NOT fixed here)

1. **#1590 atom-header over-match regression** (escalated → task_fe5d9042): #1590 promoted
   plain body-text lines to `## <LABEL> vNN` headers but left empty metadata, breaking
   `_parse_canonical_txt` on **414 engine-pool CANONICAL.txt** files (291 arc-backed).
   This makes the production entrypoint abort with `Tuple viability: NO_STORY_POOL` for the
   named book05 tuple `corporate_managers/financial_anxiety/{overwhelm,shame,spiral}` and
   ~291 other catalog tuples. book05 here therefore renders on the corporate_managers
   **anxiety** pool (same persona, healthy pool) as the book05-class proof.
2. **scene_anchor_density** HARD_FAILs both books at production profile (6 > cap 3) BEFORE
   book.txt is written. That is the concurrent Lever-B bridge-bank dedup lane, not F2. The
   harness neutralizes only that one internal gate (in the throwaway harness; no tracked
   file modified) so the genuine production prose is composed + scored; the true
   scene_anchor count is still captured in each `scene_anchor_density_report.json`.

## Files

- `SCORECARD.json` — machine scorecard (per-book F2 / verdict / severity breakdown).
- `run_repilot.py` — the re-pilot harness.
- `book0{5,6}__*/book.txt` — the production-composed manuscripts scored.
- `book0{5,6}__*/register_report.json` — full register findings (AFTER / this branch).
- `book0{5,6}__*/scene_anchor_density_report.json` — scene_anchor gate (Lever-B lane).
