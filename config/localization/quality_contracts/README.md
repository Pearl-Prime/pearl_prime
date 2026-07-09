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
PIVOT, TAKEAWAY, THREAD, and PERMISSION slot types so the regression covers the new slot
content (PERMISSION segments landed 2026-07-09 — see "Implementation status" below).

## Implementation status (updated 2026-07-09 — 14-locale truth pass)

**Canonical locale count is 14, not 13.** `pt-BR` was ratified as the 14th locale
(Q-MANGA-01, OPD-20260704-005) and is fully defined in `../locale_registry.yaml` and
`../content_roots_by_locale.yaml`. Any "13 locales" language elsewhere in this repo
(including in older revisions of this file) predates that ratification and is stale —
the 14 canonical locales are: `en-US, zh-CN, zh-TW, zh-HK, zh-SG, ja-JP, ko-KR, es-US,
es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR` (see `../locale_registry.yaml` →
`locale_groups.all_locales` for the authoritative list).

**Glossary:** All 10 core brand terms have `source_en` + context defined (fully
supported). Translations are populated for the **6 CJK locales only**
(ja-JP, ko-KR, zh-CN, zh-TW, zh-HK, zh-SG) — 60/60 of that subset. The 8
remaining locales (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR) have **0/10**
glossary translations; populating them is a Pearl_Localization translation-pipeline
task, not a source-authoring one — this file records the gap, it does not fill it.

**Golden regression segments:** 8 segments (2 PIVOT, 2 TAKEAWAY, 2 THREAD, 2
PERMISSION — PERMISSION added 2026-07-09, closing the gap where a named
translation-required slot type had zero golden coverage even though
`scripts/check_golden_translation.py` already validates it). All 8 segments carry
real ja-JP/zh-CN/zh-TW translations from the live corpus; the 2 PERMISSION segments
additionally carry real ko-KR/zh-HK/zh-SG translations (also live-corpus, not newly
authored) — `python3 scripts/check_golden_translation.py --locales zh-CN zh-TW ja-JP
ko-KR zh-HK zh-SG` passes 8/8 × 6 locales. Remaining ko-KR/zh-HK/zh-SG cells on the
PIVOT/TAKEAWAY/THREAD segments stay empty strings pending translation pipeline runs
for those slot types.

**Release thresholds:** Actual values in `release_thresholds.yaml` are
min_glossary_coverage=0.90, min_golden_regression_pass=1.0,
min_segment_count_per_locale=6 (this doc previously said 0.8 / 10, which did not
match the file — corrected 2026-07-09). Teacher bank parity thresholds at 0.0
(advisory) until translation pipeline runs consistently.

**Teacher bank parity report:** New script at `scripts/localization/teacher_bank_locale_parity.py`.
Reports per-teacher, per-locale coverage with slot-level gap detail. Integrated into
locale-gate CI workflow.

**Current parity gaps:**
- Only `adi_da` has localized atoms (6 CJK locales, 95 atoms each = 36% of 260 en-US atoms).
- 12 other teacher banks have zero localized atoms.
- European + Americas locales (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR — all 8
  non-CJK locales in the 14-locale set) have zero translation coverage for any teacher.
- COMPRESSION slot is missing from all adi_da localized sets.

## Translation source-pack readiness (2026-07-09)

Source-authoring pass (not a translation pass — see `CLAUDE.md` LLM tier policy and
`SUBSYSTEM_AUTHORITY_MAP.tsv` `translation` row, owner `Pearl_Localization`) over the
English-source surfaces downstream translation depends on, ahead of 14-market rollout:

| Surface | State before | State after | Locale-readiness |
|---|---|---|---|
| `locale_registry.yaml` | 14 locales, correct | unchanged (already correct) | **translation-ready** |
| `content_roots_by_locale.yaml` | 14 locales, correct | unchanged (already correct) | **translation-ready** |
| `golden_translation_regression.yaml` | PIVOT/TAKEAWAY/THREAD only (6 segs); PERMISSION named in this README since 2026-03-06 but had **zero** golden coverage | +2 PERMISSION segments, real live-corpus anchors, 8/8 pass across all 6 CJK locales | **translation-ready** (CJK); non-CJK still pending Pearl_Localization translation pass (expected — not a source gap) |
| `quality_contracts/README.md` (this file) | said "13 locales"; glossary claim (13 locales) didn't match the file (6); threshold numbers didn't match `release_thresholds.yaml` | corrected to 14-locale truth; glossary/threshold claims now match the actual files byte-for-byte | **translation-ready** |
| `docs/PROGRAM_STATE.md` Localization row | said "13 locales can inherit clean titles" | corrected to 14 | **translation-ready** |
| `docs/DOCS_INDEX.md` locale-doc blurbs | 4 blurbs said "13 locale(s)" — 2 describing `locale_registry.yaml`/`content_roots_by_locale.yaml` (genuinely stale, both files are 14-locale), 2 describing `AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md` (a Pearl_Marketing doc that itself is still 13-locale) | the 2 config-file blurbs were independently fixed to 14 by a concurrent sibling PR (#5478, "formalize Pearl_Localization + reconcile 14-locale canon") while this lane was in flight — reconciled onto that version rather than duplicating; the 2 marketing-plan blurbs (untouched by #5478) fixed in this pass, left at 13 (accurate to that doc's actual content) with a pt-BR gap noted for Pearl_Marketing follow-up | **translation-ready** (config-file blurbs); marketing-doc blurbs correctly flagged, not overclaimed |
| `translation_checklist.yaml` `locale_overrides` | native-fit/cultural-adaptation guidance for 6 CJK locales only; **english-stub** for the other 8 (no override block at all → translator falls back to the generic gate with no locale grounding) | added English-language locale_overrides blocks for es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR, sourced from the existing cultural/register notes already ratified in `locale_registry.yaml` / `content_roots_by_locale.yaml` | **translation-ready** (all 14 locales now have judge-facing register guidance) |
| `glossary.yaml` term translations for the 8 non-CJK locales | **missing** (0/10 per locale) | unchanged — this is translator output, not a source-authoring gap; left for Pearl_Localization | **flagged, not filled** (by design — see DO NOT in the authoring lane's mission) |

No locale translations were produced in this pass. No 15th locale was introduced;
`pt-PT` / `ru-RU` remain out of scope. `scripts/localization/run_locale_batches.py`
was not touched.
