# FEATURE-KNOB-CATALOG-VARIATION-V1-01 P0-1 — Handoff (2026-05-09)

## Summary

P0-1 serializes the four ratified structural-variation axes plus a stable
signature on every Pearl Prime catalog row, using the same SSOT-driven
selector that the runtime pipeline runs at Stage 2
(`phoenix_v4/planning/variation_selector.py::select_variation_knobs`). This
makes catalog rows reflect what `run_pipeline` will actually execute, and
makes catalog-time selection byte-deterministic for identical input.

## Axes serialized

- `angle_id` — resolved via `catalog_planner_resolution.topic_angle_map` when
  declared (P0-2 SSOT); otherwise via deterministic SHA256 over
  `(locale|brand|topic|persona)` against the registry-declared `angles:` keys.
- `motif_id` — selected via `select_variation_knobs` against
  `config/source_of_truth/recurring_motif_bank.yaml`.
- `book_structure_id` — selected via `select_variation_knobs` against
  `config/source_of_truth/book_structure_archetypes.yaml`.
- `journey_shape_id` — selected via `select_variation_knobs` against
  `config/source_of_truth/journey_shapes.yaml`, gated by the Pearl Prime
  12-chapter count.

## Axes placeholder

- None for P0-1. All four ratified axes are emitted with non-null,
  registry-valid values on every row (including teacher-blocked rows, which
  use an empty-string `teacher_id` seed component for explicit determinism).
- Out-of-scope axes (e.g. `platform_knob_tuning`) are P1 per the cap entry
  and are not emitted in this PR.

## Stable signature shape

`variation_signature` is the existing
`phoenix_v4.planning.schema_v4.compute_variation_signature` value: a 32-char
hex SHA-256 prefix over the canonical variation tuple as returned by
`select_variation_knobs`.

## Determinism

Re-running `python3 scripts/catalog/generate_pearl_prime_book_script_catalog.py`
on identical input produces byte-identical CSV output for both en_US and
ja_JP catalog files (verified by `git diff` immediately after re-run).

## Cross-refs

- Cap entry: `docs/PEARL_ARCHITECT_STATE.md` —
  FEATURE-KNOB-CATALOG-VARIATION-V1-01 (operator-ratified 2026-05-08).
- Audit: PR #960 (variation-axis audit and ratification scope).
- Stack base: PR #978 (P0-3 explicit `angle_id` per row).
- Companion workstreams: `ws_feat_knob_p0_2_angle_registry_align`,
  `ws_feat_knob_p0_3_explicit_angle_id_per_row`.
