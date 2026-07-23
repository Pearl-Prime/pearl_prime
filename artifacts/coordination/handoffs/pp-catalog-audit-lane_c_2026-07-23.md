# Handoff — Lane C: catalog-scale assembly-readiness prediction (2026-07-23)

**From:** Pearl_Prime (Lane C) | **To:** Lane F (synthesis) | **Status:** completed, PR opened

## What was done

Full, exact census (not a projected sample) of all 657 distinct (persona, topic, engine) cells that appear
anywhere across the 32,401-file en_US book-plan catalog (all 40 brand archetypes, per Lane A's inventory,
PR #221 merged). For every cell: checked CANONICAL.txt presence, story_atoms presence, thesis-bank topic-overlay
membership, and ran the real `check_tuple_viability()` preflight gate (imported directly, read-only, no render).

## Headline numbers

- **Bind-status (bank presence), weighted by planned book count:** BOUND 1.4% (465/32,401) · UNBOUND-thin 98.5%
  (31,912) · UNKNOWN 0.07% (24).
- **Live tuple-viability sweep (657 cells, full batch):** PASS 72.1% (23,350) · FAIL 27.9% (9,051) — dominant
  error codes NO_BINDING (8,704 books), BAND_DEFICIT (5,704 books), POOL_TOO_SHALLOW (54 books).
- **Cross-tab:** all 465 BOUND books also pass tuple-viability; of the 31,912 UNBOUND-thin books, 9,027 (28.3%)
  ALSO fail tuple-viability (compounding failure — `structurally clear` is optimistic for these; closer to
  `path broken`).
- **corporate_managers** is tied (not unique) for worst on bind-status (7 of 13 personas at literal 0% BOUND,
  53.7% of the whole catalog) but is the single worst-exposed major persona on tuple-viability (32.5% FAIL,
  highest of the 8 non-trivial personas, on the single largest persona by volume).
- NO_BINDING clusters in `burnout`/`imposter_syndrome`/`overthinking`/`sleep_anxiety` (>55% of each topic's
  books) — independent of thesis-bank topic-overlay coverage (burnout and overthinking have overlay AND high
  NO_BINDING; the two gaps don't track each other).
- Caution embedded per mission requirement: `healthcare_rns × burnout × overwhelm` is one of the 10 BOUND cells
  here, and the 07-22 audit's live re-score of that exact cell (seed 43006) still FAILed chapter_flow / got
  Reject on book_quality_gate despite bound research_fit — BOUND is necessary, not sufficient.

## Full evidence

`artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/REPORT.md` +
`evidence/full_cell_table.csv`, `evidence/full_cell_table_with_tuple_viability.csv`,
`evidence/persona_rollup.csv`, `evidence/topic_rollup.csv`, `evidence/rollup_summary.json`,
`evidence/tuple_viability_summary.json`, `evidence/build_cell_table.py`, `evidence/batch_tuple_viability.py`.

## NEXT_ACTION for Lane F

Reconcile this lane's assembly-readiness split against Lane A's catalog-volume headline (per-brand ~800) —
volume and readiness are different axes, both belong in the same synthesis paragraph. Repair candidates
surfaced (not fixed, read-only lane): (1) story_atoms authoring for corporate_managers first; (2)
`config/topic_engine_bindings.yaml` root-cause for the 4 clustered NO_BINDING topics; (3) the 8-cell
gen_z_student engine-mismatch is a small, precisely-scoped fix.
