# zh-TW Resolver Locale-Threading Fix — Implementation Spec

**Problem (verified via `artifacts/qa/zhtw_targetbook_fallback_manifest.json`):** The
Gen Z anxiety `--locale zh-TW` book renders ~91% English. Of 72 fallen-back
body-prose slots, **68 already have zh-TW source on disk** — the fallback is a
resolver locale-dispatch gap, not a translation gap. `persona_atom` (HOOK/SCENE)
threads `locale` and localizes correctly; four other resolver paths do not.

**The pattern (identical for all four loaders):**
1. Add a `locale: Optional[str] = None` parameter to the loader.
2. Route every `CANONICAL.txt` (or per-locale JSON) read through the existing
   helper `phoenix_v4/planning/registry_resolver.py::_locale_canonical_path(slot_dir, locale)`
   — it returns `{slot_dir}/locales/{locale}/CANONICAL.txt` when present and
   `locale != en-US`, else the base English path. Missing localized file →
   honest English fallback (P2's gate #5635 flags it).
3. Thread `locale` from the call site (already in scope as `request.locale`).
4. en-US / Latin-script locales MUST be byte-identical (regression test).

## Loader status

| # | Source class | Slots | Loader | Call site | Status |
|---|---|---|---|---|---|
| 1 | composite_doctrine | REFLECTION ×12 | `registry_resolver.py::_load_composite_doctrine_atoms` | `enrichment_select.py::select_enrichment` (~L2372) | **DONE** — this commit. Verified: en-US 0 CJK / zh-TW 10,109 CJK. |
| 2 | story_plan | STORY ×36 | `story_planner.py::build_story_schedule` → `_load_all_atoms` → `_load_atoms_for_engine` | `enrichment_select.py::select_enrichment` (L2507) | **DONE** — pt2. Selection metadata derives from English (deterministic); rendered text swapped to `{arc_pos}/locales/{locale}/micro/{stem}.txt` when present. Verified: 107 atoms both locales, metadata identical, 36/107 render Chinese, en-US 0 CJK. |
| 3 | angle_atom | ANGLE_DEFINITION + ANGLE_CALLBACK ×12 | `enrichment_select.py::_try_angle_definition` (CANONICAL.txt) + `_try_angle_callback` (level_N.yaml), via new `_locale_file_path` helper | `select_enrichment` (L2603/L2618) | **DONE** — pt3. Verified: en-US 0 CJK; zh-TW DEF 85 / CALLBACK 385 CJK, both still authored `angle_atom`. |
| 4 | practice_library | EXERCISE ×12 | `practice_library_loader.py::load_practice_library` + `get_exercise_for_chapter` + `compose_exercise`; `enrichment_select.py::_try_practice_library` + `_try_practice_library_by_id` | `select_enrichment` (L2362/L2692/L2802) | **DONE** — pt4. Locale-aware inbox + locale-keyed cache; `load_component_templates(locale)` already existed. Verified: cache isolated (en 0 / zh 1088 CJK), composed en-US 0 CJK / zh-TW 144 CJK. Residual English scaffolding ('This is {name}.') = template-authoring gap, flagged by #5635, follow-up. |

### pt4 practice_library — precise plan (verified on disk)
**Correction to the manifest:** the 4 EXERCISE items it marked `no zh-TW source`
are NOT missing. zh-TW practice content **exists** at
`SOURCE_OF_TRUTH/practice_library/locales/zh-TW/inbox/*_PRODUCTION_READY.json`
(body_awareness / sensory_grounding / integration_bridges confirmed, real CJK).
**⇒ the separate P1b translation lane is MOOT — practice is a pure resolver gap too.**
A localized composition template also exists:
`config/pearl_practice/locales/zh-TW/component_templates.yaml`.

Edits (same pattern, plus cache-keying — this loader has a module-level cache):
1. `load_practice_library(locale=None)` — read inbox from
   `practice_library/locales/{locale}/inbox/` when `locale not in (None,'en-US')`
   and it exists, else base `INBOX_ROOT`. **Key `_LIBRARY_CACHE` by locale**
   (dict[locale] → library) — the current single global would serve the first
   locale to everyone.
2. `load_component_templates(locale=None)` — prefer
   `config/pearl_practice/locales/{locale}/component_templates.yaml` when present;
   key `_TEMPLATES_CACHE` by locale.
3. Thread `locale` through `get_exercise_for_chapter` / `compose_exercise` /
   `_try_practice_library` / `_try_practice_library_by_id` and their call sites in
   `enrichment_select.py` (`locale` already in scope in `select_enrichment`).
4. Verify at loader level: en-US byte-identical (0 CJK), zh-TW EXERCISE text CJK.

## On-disk zh-TW source paths (from manifest, confirmed present)
- doctrine: `SOURCE_OF_TRUTH/composite_doctrine/{topic}/locales/zh-TW/CANONICAL.txt`
- story:    `atoms/{persona}/{topic}/{slot}/locales/zh-TW/CANONICAL.txt`
- angle:    `atoms/{persona}/{topic}/ANGLE_DEFINITION/{ANGLE_ID}/locales/zh-TW/CANONICAL.txt`

## Verification (after all four)
Re-run the exact production CLI (topic=anxiety, persona=gen_z_professionals,
arc F006, `--quality-profile production --locale zh-TW`). Expect: `locale_fallback_report.json`
(from #5635) shows ~0 english_fallback body slots (bar the 4 missing exercises
until the translation PR lands), QUOTE floor filled (#5634), and book.txt CJK
ratio inverts. Do NOT trust gate-PASS alone — measure the fallback report and
CJK ratio.

## Companion PRs
- #5634 — CJK-honest QUOTE supply (accent word-count fix)
- #5635 — honest locale-fallback gate + this manifest
