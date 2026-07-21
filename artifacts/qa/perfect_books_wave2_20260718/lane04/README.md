# Lane 04 — Wave-2 deferred CI gates (G-F1H / G-ORIENT / G-ACCENT)

**Agent:** Pearl_Dev (lane 04)
**Date:** 2026-07-19 (local execution; substrate `pearlstar_offline`)
**Acceptance layer:** structurally clear (enforcement mechanisms only — no
register/quality claim; see CLAUDE.md Bestseller Quality Anti-Drift Doctrine
and PEARL_PRIME_PERFECT_BOOKS_SPEC.md §0).

## What shipped

| Gate | Script | Severity | Wired |
|---|---|---|---|
| G-F1H | `scripts/ci/check_f1h_templated_cluster_hard.py` | HARD_FAIL (>= 6 distinct chapters in one F1 templated-paragraph cluster) | drift-detectors.yml (BLOCK integrity) + readiness gate 38 |
| G-ORIENT | `scripts/ci/check_orient_ch1_scene_anchor.py` | WARN -> `--strict` escalates to FAIL (Layer-2 authored-candidate eligibility, never Layer-1) | drift-detectors.yml (WARN integrity) + readiness gate 39 |
| G-ACCENT | `scripts/ci/check_accent_supply_preflight.py` | Report-only per-PR; `--fail-closed` weekly cadence job | drift-detectors.yml (report-only) + readiness gate 40 + new `accent-supply-preflight.yml` (cron Mon 07:00 UTC) |

New lexicon SSOT (did not exist before this lane; spec required one for
G-ORIENT): `config/quality/orient_body_scene_lexicon.yaml` — seeded from the
frozen flagship Ch1 exemplar
(`artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`) and the existing
HOOK-SCENE-FIRST-01/F11 scene-first regex vocabulary already "approved" in
`phoenix_v4/quality/register_gate.py` (cited, not re-authored).

## Design notes / why each gate is additive-only

- **G-F1H** imports `_detect_f1_templated_paragraphs` / `_split_chapters`
  directly from `phoenix_v4/quality/register_gate.py` — it does not
  re-implement F1 similarity detection. It adds exactly one new rule the base
  detector doesn't apply: escalate to HARD_FAIL when a cluster's **distinct
  chapter breadth** reaches >= 6 (F1 itself already WARNs at instance-cluster
  size 2 and FAILs at 3+; that severity ladder is untouched — see the
  docstring in the script for the no-double-counting rationale).
- **G-ORIENT** is WARN by default (never touches Layer 1 / never blocks a PR
  unless `--strict` is passed for a Layer-2 eligibility check), matching the
  spec row exactly ("WARN->escalate ... Authored-candidate eligibility").
  SCENE-atom provenance is read from the existing `book_outline.json` schema
  (`phoenix_v4/qa/book_outline.py` `slot_types_landed`) — no new provenance
  plumbing was added upstream.
- **G-ACCENT** imports `resolve_accent_budget` / `_build_pools_with_provenance`
  / `_capability_gaps` directly from `phoenix_v4/planning/accent_planner.py`
  (the same functions `validate_accent_plan()` calls at render time) — it
  orchestrates them across the top-N `MATRIX.tsv` cells without needing a full
  book render. Per-PR it is report-only (never blocks); the weekly
  `accent-supply-preflight.yml` cron uses `--fail-closed`, matching the spec's
  "ops-cadence report + fail-closed, not necessarily per-PR blocker."

**Not touched:** `register_gate.py`'s F16 (G-WRAP) severity logic / thresholds,
the DEF4 detector, F14/beat-line/chord CI, or any Wave-1 gate script
(`check_acceptance_claim_language.py`, `check_catalog_manifest_acceptance_layer.py`,
`check_catalog_ship_wrap_defect4.py`) — all read-only imports, zero edits.

## Proof contents (this directory)

- `PYTEST_OUTPUT.txt` — 15/15 new tests passing
  (`tests/test_check_f1h_templated_cluster_hard.py`,
  `tests/test_check_orient_ch1_scene_anchor.py`,
  `tests/test_check_accent_supply_preflight.py`).
- `MUTATION_CHECKS.md` — §14 mutation check for all three gates: violating
  fixture -> RED -> revert -> green, for each gate.
- `READINESS_GATES_38_40_CHECK.txt` — isolated invocation of the exact
  subprocess loop `scripts/run_production_readiness_gates.py` runs for gates
  38-40 (all rc=0 in integrity mode on this checkout).
- `ACCENT_SUPPLY_PREFLIGHT_SAMPLE.json` — live G-ACCENT report against the
  real top-20 `MATRIX.tsv` cells: 14/20 cells have a real `no_supply_pool` gap
  for a budgeted accent class (matches the ANALYSIS_REPORT.md "Accent
  `no_supply_pool` hard-stops" finding this gate was built to catch).

## Full production-readiness run (34 pre-existing gates)

`scripts/run_production_readiness_gates.py` main() runs the full 1-40 gate
chain serially, including several render/pipeline-heavy checks (gates 1-34)
that take well beyond the 10-minute lane checkpoint on this host. Rather than
block the turn on an unrelated multi-gate run, gates 38-40's exact wiring
block (same `subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=...)`
shape as gates 35-37) was isolated and re-run directly against the live
module (`READINESS_GATES_38_40_CHECK.txt`) — all three report rc=0. This
verifies the new wiring is correct without requiring a full multi-gate
sweep of unrelated pre-existing gates.

## G-ORIENT lexicon: follow-on note

The lexicon at `config/quality/orient_body_scene_lexicon.yaml` is intentionally
minimal (58 words total, English-only, seeded from one exemplar + one existing
regex family). It is NOT blocked/BLOCKED-on-lexicon — a v1 SSOT was authored
per the prompt's fallback instruction ("author a minimal one ... OR mark
G-ORIENT BLOCKED-on-lexicon") — but it should be treated as a v1, not a final
authority. A follow-on (flagged in the coordination handoff / `NEXT_ACTION`)
should widen it against a larger authored-candidate corpus once Lane 03's
line-edited flagship cells land.
