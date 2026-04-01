# Translation quality contracts

Quality contracts for locale translation pipelines: glossary, release thresholds, golden regression.

- **glossary.yaml** — Canonical terms and preferred translations per locale.
- **release_thresholds.yaml** — Minimum quality scores and coverage to allow release.
- **golden_translation_regression.yaml** — Golden segments used for regression tests.

See docs/DOCS_INDEX.md § Translation and locale gate workflow.

## When enabling locales (added 2026-03-06)

The following content was added as part of the Pearl Prime structural upgrade and must be
included in any locale implementation:

**New slot types requiring translation:**
- `PIVOT` — 2–3 sentences naming what a story revealed (before teaching). Short; translate whole.
- `TAKEAWAY` — One thesis sentence per chapter, derived from `chapter_thesis[ch]` in the arc YAML.
  Source sentences are in `docs/CHAPTER_THESIS_BANK.md`. Translate those sentences per locale.
- `THREAD` — 1–2 sentences at close of INTEGRATION planting forward pull. Translate whole.
- `PERMISSION` — 2–4 second-person sentences giving chapter-specific emotional permission.
  Requires cultural review per locale. Permission language is culturally variable.

**Arc thesis sentences:**
All 457 master arcs now have (or will have) a `chapter_thesis` field — 20 thesis sentences per arc.
These must be translated and stored per locale alongside the arc. The TAKEAWAY slot text at
render time = the translated `chapter_thesis[ch]` for that chapter.

**Glossary priorities:**
Add translations for core brand terms used in thesis sentences across all engines:
`nervous system`, `the alarm`, `the mask`, `the pattern`, `the strategy`, `the cost`,
`somatic`, `watcher`, `false alarm`, `the thread`. These appear in TAKEAWAY and PIVOT text
at high frequency.

**Golden segments:**
When populating `golden_translation_regression.yaml`, include at least 2 examples each from
PIVOT, TAKEAWAY, and THREAD slot types so the regression covers the new slot content.

## Implementation status (updated 2026-04-01)

**Glossary:** Populated with all 10 core brand terms across all 13 locales.

**Golden regression segments:** 6 segments added (2 PIVOT, 2 TAKEAWAY, 2 THREAD) with
ja-JP translations where available from approved_atoms_localized. Other locale translations
are empty strings pending translation pipeline runs.

**Release thresholds:** Set to min_glossary_coverage=0.8, min_golden_regression_pass=1.0,
min_segment_count_per_locale=10. Teacher bank parity thresholds at 0.0 (advisory) until
translation pipeline runs consistently.

**Teacher bank parity report:** New script at `scripts/localization/teacher_bank_locale_parity.py`.
Reports per-teacher, per-locale coverage with slot-level gap detail. Integrated into
locale-gate CI workflow.

**Current parity gaps:**
- Only `adi_da` has localized atoms (6 CJK locales, 95 atoms each = 36% of 260 en-US atoms).
- 12 other teacher banks have zero localized atoms.
- European locales (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU) have zero coverage for any teacher.
- COMPRESSION slot is missing from all adi_da localized sets.
