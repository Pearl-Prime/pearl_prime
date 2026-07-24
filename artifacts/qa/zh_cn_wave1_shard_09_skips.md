# zh-CN Wave 1 Shard 09 — Skip Report

Shard file: `wave1_shard_09.jsonl` (20 atoms). 13 accepted, 7 skipped.

All 7 skips are real, pre-existing blockers in the English source — not
translation-quality failures, and not repaired by hand-patching per the
shard instructions.

## Missing source file (3)

- `atoms/educators/social_anxiety/comparison/CANONICAL.txt` — no `comparison`
  shape directory exists under `atoms/educators/social_anxiety/`.
- `atoms/educators/grief/spiral/CANONICAL.txt` — no `spiral` shape directory
  exists under `atoms/educators/grief/` (only `grief/`, `watcher/` present).
- `atoms/educators/imposter_syndrome/watcher/CANONICAL.txt` — no `watcher`
  shape directory exists under `atoms/educators/imposter_syndrome/` (only
  `false_alarm/`, `shame/` present).

## EN source corrupted — duplicate header-version IDs (4)

Confirmed by direct inspection: the same `## SHAPE vNN` header line recurs
multiple times with *different* story content under it (a version-number
authoring bug, not a translation issue). This matches the known
EN-source-corrupted-atom backlog (see commit `386bf02bef` "atom authoring
backlog for EN-source-corrupted atoms (650 rows)").

- `atoms/educators/financial_stress/overwhelm/CANONICAL.txt` — `RECOGNITION
  v01`–`v05` each duplicated 7x (35 RECOGNITION blocks under only 5 distinct
  version labels).
- `atoms/educators/financial_stress/shame/CANONICAL.txt` — `RECOGNITION
  v01`–`v05` each duplicated 5x.
- `atoms/educators/financial_stress/REFLECTION/CANONICAL.txt` — `REFLECTION
  v16`–`v25` each duplicated 2x.
- `atoms/educators/grief/REFLECTION/CANONICAL.txt` — `REFLECTION v16`–`v25`
  each duplicated 2x (same pattern as the financial_stress sibling).

## Notes on accepted items

- `atoms/corporate_managers/compassion_fatigue/COMPRESSION/CANONICAL.txt` was
  accepted as a **verbatim copy** (no DashScope call) — this shape's body is
  metadata-only (`compression_family: CN`), no translatable prose. Mirrors
  the already-landed convention in sibling `zh-CN` COMPRESSION files (e.g.
  `atoms/gen_z_student/financial_stress/COMPRESSION/locales/zh-CN/`), which
  also fail `structural_validator.py`'s `untranslated_english` check for the
  same structural reason — a known gate blind-spot for this atom shape, not
  a live defect.
- One recurring glossary drift was caught and fixed during a post-run
  spot-check: `compassion fatigue` (topic-locked critical_recurring term,
  `共情耗竭` per `glossary_project.yaml`) was rendered as the secondary
  variant `同情疲劳` in `corporate_managers/compassion_fatigue/{shame,
  comparison}` — corrected to `共情耗竭` in both files, re-validated OK.
- One deterministic glossary violation (`identity` → forbidden `身份` instead
  of locked `自我认同`) recurred across 2 atoms and was repaired
  programmatically (string substitution) rather than by burning a repeat
  DashScope call, since the fix was fully deterministic.
