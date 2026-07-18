# PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC

Status: REFRESHED MERGE NOTE
Classification: MERGE_WITH_EXISTING
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `3c8b87267b0250e57a557cce3dc07d294e9093b79ba138fe8603390d8b8e5a40`
GitHub writes: none; current GitHub substrate blocked.

## Current Relevance

The failure classes are still valid, but this should not land as a standalone
`phoenix_v4/quality/prose_integrity.py` module yet. Current repo machinery
already covers part of the proposed surface through `register_gate.py`, atom
quality gates, reader-layer specs, exercise specs, story/literary repair specs,
and rendered-book acceptance layers.

## Reconcile, Do Not Rebuild

Before adding any new validator, map each proposed check against:

- `phoenix_v4/quality/register_gate.py`
- `tests/test_register_gate.py`
- `tests/test_register_gate_voice.py`
- atom/job quality gate artifacts from `artifacts/qa/atom_job_deep_audit_20260717/`
- reader-layer and deep five-layer exercise specs
- current story/literary repair acceptance artifacts

Already-covered examples:

- Bare wrapper slots and leaked `{TRADITION}`-style placeholders are covered by
  wrapper placeholder/tradition leak detection and tests.
- Dwell/integration starvation is covered by the F13 detector and tests.
- F2.B phrasal false positives are already addressed with phrasal/stranded
  preposition tests.

## Refreshed Merge Plan

Treat the original five proposed validators as gap candidates:

- `PI-1 no-story-adjacency`: merge only if current story/literary gates do not
  catch unbridged story adjacency.
- `PI-2 quote-bridge`: merge into evidence/source bridge gates and keep WARN
  until sampled by operator.
- `PI-3 composite-teaching-band`: merge into atom-depth and reader-layer checks.
- `PI-4 tool-vs-exercise`: merge into the exercise/tool policy from the atom
  taxonomy and deep five-layer exercise spec.
- `PI-5 fallback-sweep`: merge with enrichment selection provenance checks.

Do not create another monolithic validator until those gaps are proven.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: every proposed validator is mapped to existing gate,
  merged gap, or retired duplicate.
- `OPERATOR_READ_PASS`: operator accepts sampled WARN/BLOCK behavior for
  literary quality and reader transformation findings.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted. Automated prose gates
  cannot substitute for operator-read approval.
