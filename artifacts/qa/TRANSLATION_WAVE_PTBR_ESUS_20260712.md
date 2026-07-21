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

## Coverage

**Denominator correction (this session):** a sibling wave (East Asia locales) and
this session's own direct filesystem walk both found the true denominator is
**3853** English source `CANONICAL.txt` files (one per persona/topic/slot-type
directory, counted as `find atoms -mindepth 4 -maxdepth 4 -name CANONICAL.txt
-not -path "*/locales/*"` across all 14 personas) — not 3754 as measured by the
prior session's `report_translation_coverage.py` bestseller-slot-only scope. All
numbers below use the 3853 live-walk denominator, re-derived at the start of this
session and again at the end.

| Locale | Session start | Session end | Delta |
|---|---|---|---|
| pt-BR | 37 / 3853 (0.96%) | 108 / 3853 (2.80%) | +71 |
| es-US | 37 / 3853 (0.96%) | 108 / 3853 (2.80%) | +71 |

## Files written this session (142 new CANONICAL.txt files, 71 per locale)

### working_parents — remaining 12 topics, PIVOT/PERMISSION/THREAD/TAKEAWAY (96 files)
Completed the 12 `working_parents` topics not covered by the prior session's first
batch (which did adhd_focus/anxiety/burnout/boundaries/depression/imposter_syndrome):
`anchored`, `compassion_fatigue`, `courage`, `financial_anxiety`, `financial_stress`,
`grief`, `mindfulness`, `overthinking`, `self_worth`, `sleep_anxiety`,
`social_anxiety`, `somatic_healing` — 4 slots x 12 topics x 2 locales = 96 files.
This completes all 18 `working_parents` topics for these 4 slot types in both
locales.

### working_parents — COMPRESSION, real-content variants only (16 files)
8 topics (`burnout`, `financial_anxiety`, `imposter_syndrome`, `overthinking`,
`sleep_anxiety`, `social_anxiety`, `somatic_healing`, `mindfulness`) have COMPRESSION
banks with authored English prose (3-4 variants each) — translated, 8 topics x 2
locales = 16 files.

### working_parents — EXERCISE, all 15 topics that have it (30 files)
`anxiety`, `boundaries`, `burnout`, `compassion_fatigue`, `courage`, `depression`,
`financial_anxiety`, `financial_stress`, `grief`, `imposter_syndrome`,
`overthinking`, `self_worth`, `sleep_anxiety`, `social_anxiety`, `somatic_healing`
— 3 short guided-practice variants per topic (telegraphic, line-broken style,
preserved exactly), 15 topics x 2 locales = 30 files.

All 142 files: `python3 scripts/localization/validate_cjk_atom.py <paths>` → `OK`.

## Stub-source gap found (metadata-only COMPRESSION, skipped per protocol)

8 `working_parents` topics have a COMPRESSION English source that is a
**metadata-only stub**: each `## COMPRESSION vNN` block carries only a
`compression_family: Cx` tag with **zero prose lines** — nothing to translate.
Per the dispatch instruction ("if you encounter an English source that's a
metadata-only stub... skip it and flag it"), these were intentionally **not**
translated (translating would mean writing new prose not present in the source,
which is out of scope for a translation wave):
- `anxiety/COMPRESSION`, `boundaries/COMPRESSION`, `compassion_fatigue/COMPRESSION`,
  `courage/COMPRESSION`, `depression/COMPRESSION`, `financial_stress/COMPRESSION`,
  `grief/COMPRESSION`, `self_worth/COMPRESSION`.
- Also: `working_parents/adhd_focus` and `working_parents/anchored` have no
  `EXERCISE` directory at all (not every topic has this slot type) — not a gap,
  just absent by design.

## Scope notes

- Did not touch `SOURCE_OF_TRUTH/teacher_banks/**` (out of scope per dispatch).
- Did not touch any other locale.
- `ENGINE_DIRS` (comparison/false_alarm/grief/overwhelm/shame/spiral/watcher) files
  remain deferred — still not started for pt-BR/es-US, per prior-session scoping
  note (~28 sub-variants each, should be its own batch).
- `STORY`, `HOOK`, `INTEGRATION`, `SCENE`, `REFLECTION` slot types in
  `working_parents` (200-350+ lines each) were also not started this session.

## Residual / next-session recommendation

- Remaining gap for pt-BR and es-US is still large (3745/3853 files, ~97.2%).
- `working_parents` is now fully covered for the small slot types (PIVOT/
  PERMISSION/THREAD/TAKEAWAY/EXERCISE, plus COMPRESSION where content exists).
  Next lowest-effort-per-file pick: the same 4+1 slot-type pattern applied to the
  next persona (`corporate_managers`, `educators`, `entrepreneurs`, etc. — 13
  personas remain untouched by this wave).
- `STORY` files across topics tend to be much larger (150-350+ lines, 15-20+
  narrative variants) — budget more session time per topic for those.
- Engine-dir files (comparison/false_alarm/grief/overwhelm/shame/spiral/watcher)
  were not started for pt-BR/es-US in this or the prior wave; each is ~28
  sub-variants of multi-sentence prose and should be scoped as its own batch.
