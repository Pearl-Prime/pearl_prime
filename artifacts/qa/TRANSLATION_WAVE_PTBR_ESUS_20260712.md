# Translation Wave: pt-BR + es-US Atom Translation (2026-07-12)

**Workstream:** `ws_translation_wave_ptbr_esus_20260712`
**Parent:** `ws_cjk_atom_translation_qwen25_20260420`
**Agent:** Pearl_Translator (Claude Code, Tier 1, direct authoring — no LLM API, no Ollama, no queue)
**Branch:** `agent/translation-wave-d-ptbr-esus-20260712` (base `origin/main` @ `3c181aa361`)

## Method

All translations in this wave were authored directly by Claude (no Ollama, no Pearl
Star, no external LLM API call of any kind), per Tier 1 policy. Every file was
validated with `scripts/localization/validate_cjk_atom.py` (structure-only validator;
confirmed it applies the same slot-role/story-role parse rules to non-CJK locales)
before commit.

- **pt-BR:** Brazilian Portuguese — `você`-based address, Brazilian vocabulary and
  spelling conventions (not European Portuguese).
- **es-US:** neutral US Hispanic Spanish — `tú`-based address, no `vosotros`, no
  Castilian laísmo/leísmo, neutral Latin American vocabulary choices.

File structure (headers, `## SLOT vNN` delimiters, `---` metadata blocks including
empty ones, `STORY_TYPE`/`STORY_TYPE_SOURCE` metadata, path lines, ordering) was
preserved exactly from the English `CANONICAL.txt` source for every file.

## Coverage (bestseller-slot metric, `scripts/ci/report_translation_coverage.py`)

Denominator = 3754 English source `CANONICAL.txt` files across the 5 bestseller
slots (PIVOT/TAKEAWAY/THREAD/PERMISSION/STORY) + 7 engine dirs
(comparison/false_alarm/grief/overwhelm/shame/spiral/watcher), all personas/topics.

| Locale | Before | After | Delta |
|---|---|---|---|
| pt-BR | 7 / 3754 (0.19%) | 34 / 3754 (0.91%) | +27 |
| es-US | 5 / 3754 (0.13%) | 34 / 3754 (0.91%) | +29 |

(Note: `report_translation_coverage.py`'s own native-check sub-scan is slow/hangs
on a full run in this environment; the bestseller-slot numbers above were verified
directly via `_bestseller_english_sources`/`_bestseller_translated_count` inline
against the same 3754-file baseline the CI script itself measures against.)

## Files written (56 new CANONICAL.txt files, 28 per locale)

### working_parents (6 topics x 4 slots x 2 locales = 48 files)
PIVOT / PERMISSION / THREAD / TAKEAWAY, fresh in both pt-BR and es-US, for:
- `atoms/working_parents/adhd_focus/`
- `atoms/working_parents/anxiety/`
- `atoms/working_parents/burnout/`
- `atoms/working_parents/boundaries/`
- `atoms/working_parents/depression/`
- `atoms/working_parents/imposter_syndrome/`

### corporate_managers/adhd_focus (gap-fill, 8 files)
- pt-BR: `PERMISSION`, `STORY`, `TAKEAWAY` (PIVOT + THREAD already existed on main)
- es-US: `PIVOT`, `PERMISSION`, `THREAD`, `STORY`, `TAKEAWAY` (all five, fresh)
- `STORY` is the 16-variant `character_study` narrative set (Tom/Sana/Devon/Aisha/
  Raj/Nadia/Carlos/Mei/Greg/Bianca/Owen/Priya/Dana/Yuki/Sam/Lena vignettes);
  `STORY_TYPE`/`STORY_TYPE_SOURCE` metadata preserved on the 8 variants that carry it.

All 56 files: `python3 scripts/localization/validate_cjk_atom.py <paths>` → `OK`.

## Scope notes

- Did not touch `SOURCE_OF_TRUTH/teacher_banks/**` (out of scope per dispatch).
- Did not touch any other locale.
- `ENGINE_DIRS` (comparison/false_alarm/grief/overwhelm/shame/spiral/watcher) files
  are large (up to ~335 lines / 28 sub-variants each) and were deliberately deferred
  in this session in favor of completing more persona/topic breadth on the smaller,
  higher-value bestseller slot files (PIVOT/PERMISSION/THREAD/STORY/TAKEAWAY) —
  this is the smallest-safe-batch call for a single-session direct-authoring wave.

## Residual / next-session recommendation

- Remaining gap for pt-BR and es-US is still large (3720/3754 files, ~99.1%).
  `working_parents` has 12 more topics with only the 4 small slot files (PIVOT/
  PERMISSION/THREAD/TAKEAWAY) missing per locale — same low-effort-per-file
  pattern as this wave's first batch — recommended as the next pick.
- `STORY` files across other topics tend to be much larger (150-350+ lines,
  15-20+ narrative variants) — budget more session time per topic for those.
- Engine-dir files (comparison/false_alarm/grief/overwhelm/shame/spiral/watcher)
  were not started for pt-BR/es-US in this wave; each is ~28 sub-variants of
  multi-sentence prose and should be scoped as its own batch.
