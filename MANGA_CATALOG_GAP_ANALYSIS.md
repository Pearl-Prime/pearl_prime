# Manga Catalog Gap Analysis
**Sprint:** manga-native-system-layer verification
**Date:** 2026-04-19
**Author:** Pearl_Architect + Pearl_Research (Claude Code session)

---

## 1. What Manga Is in Phoenix Today

Phoenix Omega has a production-grade manga pipeline that is substantially more
complete than an external strategic review suggested. The following systems exist
and are operational:

### Pipeline (phoenix_v4/manga/ — 45 Python files)
- Full DAG runner: chapter_runner, dag_order, revision_policy, stage_manifest_io
- Chapter writer with LLM client
- Lettering/speech bubble derivation from chapter script (lettering_from_script.py)
- Visual prompt compiler (visual_prompt_compiler.py)
- ITE pipeline runner
- Series memory accumulation
- ComfyUI/RunComfy render backend integration

### Genre Grammar
- **10 CI workflows** dedicated to manga (pipeline, image gen, smoke test, quality
  forensic analysis, image bank build, rollout notify, etc.)
- **10 genre ITE profiles** in `config/manga/genre_ite_profiles.yaml`:
  shonen, seinen, shojo, sports, horror, iyashikei, cultivation, manhwa,
  webtoon_romance, isekai — each with distinct breath_sequences, fractal_regulation
  density, color_arc, gutter_therapy rules, and soundtrack parameters
- **8 visual style archetypes** in `config/manga/style_archetypes.yaml`:
  cozy_iyashikei, dark_psychological, power_progression, webtoon_vertical_romance,
  hyper_clean_cinematic, meme_chaotic_humor, social_media_simulacra, interactive_branching
- **12 system specs** governing manga production (MANGA_GENRE_AGENT_SPEC.md,
  MANGA_STORY_ARCHITECT_SPEC.md, MANGA_MODE_SYSTEM_SPEC.md, etc.)

### Determinism
- `phoenix_v4/manga/series/story_architect.py` uses SHA-256 hash seeding:
  `seed = f"{series_id}:{arc_id}:{genre_id}"` → deterministic beat/setting/character selection
- Chapter-end hooks (`chapter_end_hook`) are emitted as first-class fields

### Chapter-End Hooks (Serialization Engine)
- `specs/MANGA_STORY_ARCHITECT_SPEC.md` §12 defines a complete chapter_end_hook system:
  cadence-aware rules, hook taxonomy (Cliffhanger/Revelation/Ambiguous/Soft-Close),
  18 worked example hooks
- The system is implemented in story_architect.py and preserved through transmission.py

### QA Gates (4 existing manga-specific gates)
```
MANGA.PROMPT.STRUCTURE     BLOCKER  — visual prompt per-panel compliance
MANGA.PROMPT.TOKEN_BUDGET  MAJOR    — prompt token count ≤120 positive / ≤60 negative
MANGA.TEACHING.PANEL_EXPRESSION  MAJOR  — panel_expression preservation
MANGA.SILENCE.STRUCTURE    BLOCKER  — silent panel intent machine-visible
```

### 18 dedicated test files covering all pipeline paths.

---

## 2. Verified Gaps

These are real gaps, verified against the repo. Not the 7 claimed by the external
review (see `artifacts/audit/manga_framework_reality_check.md` for full ratings):

| Gap | Impact | Priority |
|---|---|---|
| josei ITE profile missing | josei series use shojo or seinen ITE parameters | P1 |
| chapter_hook_family not typed enum | hooks not validated against family taxonomy | P1 |
| manga_profile schema doesn't exist yet | no unified title-level identity record | P0 (this sprint) |
| catalog homogeneity gate missing | all titles could have same emotional engine | P2 |
| restraint-over-exposition gate missing | shojo/josei show-vs-tell not automated | P1 |
| visual grammar → genre mapping not formalized | no rule enforcing archetype consistency | P2 |
| genre_family → ITE profile gap (josei runtime) | josei in author schema but not ITE config | P1 |

**External claims rated INCORRECT (not gaps):**
- "No manga-specific framework" → INCORRECT (45-file pipeline, 12 specs, 18 tests)
- "Taxonomy is demo-labels-only" → INCORRECT (10 genre ITE profiles with runtime params)
- "No chapter-addiction engineering" → INCORRECT (chapter_end_hook system in spec + code)
- "No manga-native QA" → INCORRECT (4 gates, chapter_qc.py, CI workflow)
- "No genre-specific pacing contracts" → INCORRECT (genre_ite_profiles.yaml)
- "No multiple visual grammars" → INCORRECT (8 style archetypes + per-brand visual DNA)

---

## 3. Three Operator Questions — Summary

Full answers with Python signatures: `artifacts/analysis/manga_native/01_three_questions_answered.md`

**Q1 — Determinism:**
manga_profile is ASSIGNED at title-level by an operator (authored YAML, not runtime selected).
Downstream beat/setting selection stays hash-seeded within profile-filtered pools.
`manga_profile_seed = sha256(title_id + ":" + brand_id)[:12]` is used for bank filtering only.
The profile itself does not change between renders. Same (series_id, arc_id, genre_id) → same output.

**Q2 — Manga mode integration:**
New layer EXTENDS current pipeline. Adds one insertion point: `load_manga_profile()` between
operator inputs and `build_genre_blueprint()`. Derives `genre_family` from profile.
Does not replace any existing module. All 45 existing Python files, 18 tests, and 10 CI
workflows are unchanged.

**Q3 — Version identity:**
Same Phoenix v4.8 / phoenix_v4 package. `manga_profile_schema_version: "1.0.0"` is a new
artifact type in the same system. Not a fork. No new pipeline. Existing variants without
manga_profile linkage remain backward compatible.

---

## 4. manga_profile Schema — Summary

Full schema: `config/source_of_truth/manga_profiles/schema.yaml`
Worked examples: `config/source_of_truth/manga_profiles/examples/`

A `manga_profile` is a title-level YAML file capturing the complete identity contract
for a manga series. Key fields:

```yaml
title_id: "anxiety_overwhelm_vol1"
brand_id: "stillness_press"
market_demo: josei                    # shonen|shojo|seinen|josei|kodomo
genre_family: healing                 # 22 values (battle, romance, healing, horror, etc.)
emotional_engine: cozy_restoration    # aspiration|catharsis|tenderness|dread|obsession|...
reader_promise: "You will feel seen in your exhaustion."
serialization_engine: mood_based      # cliffhanger_driven|episodic|arc_based|mood_based|...
chapter_hook_family: almost_confession  # revelation|interruption|betrayal|vow|arrival|...
visual_grammar: iyashikei_minimalism  # kinetic_shonen|soft_shojo_decorative|grounded_josei_realism|...
words_per_page_target: 28
silent_panel_ratio: 0.42
narration_tolerance: minimal          # minimal|moderate|generous
adaptation_targets: [print, webtoon]
```

Three worked examples show:
1. Iyashikei/josei healing (Stillness Press) — cozy_restoration, minimalism, restraint
2. Battle shonen — aspiration, kinetic_shonen, cliffhanger-driven
3. Josei workplace romance — longing, grounded_josei_realism, female-reader grammar

---

## 5. Determinism Approach — Option C

**Option C: Profile assigned, selection hash-seeded within profile-filtered banks.**

```
Operator authors manga_profile YAML → commits to config/source_of_truth/manga_profiles/
    ↓
load_manga_profile(title_id, brand_id)  [new function]
    ↓
profile["genre_family"] → build_genre_blueprint(genre_id=...)
    ↓
build_story_architecture_internal(
    series_id=..., arc_id=..., genre_id=..., manga_profile=profile
)
    where: seed = sha256(f"{series_id}:{arc_id}:{genre_id}")[:8]
    hash selects within profile-filtered beat pool
    ↓
[rest of pipeline unchanged]
```

Why Option C:
- Preserves existing determinism guarantee (same inputs → same outputs)
- Does not break existing selections when new axes are added (profile is additive, not multiplicative)
- Respects the invariant from MANGA_MODE_SYSTEM_SPEC.md: "style_archetype_id locked for entire volume"
- Allows operator override at authoring time without touching runtime code

---

## 6. MDLG Extensions — Proposed Gates 06-11

These extend the existing 4-gate manga QA system (manga_gates.yaml).
The external review used the acronym "MDLG" — this is not a repo-native term.
The equivalent is the manga QC gate family. Proposed additions:

| Gate ID | Name | Description | Severity | Validates Against |
|---|---|---|---|---|
| MDLG-06 | chapter_addiction | chapter_end_hook type belongs to profile's chapter_hook_family enum | MAJOR | manga_profile.chapter_hook_family |
| MDLG-07 | silence_density | silent_panel_ratio within [profile range ± 0.10] | MAJOR | manga_profile.silent_panel_ratio |
| MDLG-08 | genre_authenticity | panel tempo + dialogue density consistent with market_demo and genre_family | MAJOR | genre_ite_profiles.yaml + manga_profile |
| MDLG-09 | catalog_homogeneity | cross-title emotional_engine + chapter_hook_family deduplication; warn if >60% of catalog shares same engine | WARN | all manga_profiles in config/ |
| MDLG-10 | reader_promise_fulfillment | final chapter beat sequence delivers on reader_promise emotional register | MAJOR | manga_profile.reader_promise + ITE scorer |
| MDLG-11 | restraint_over_exposition | shojo/josei chapters: caption text does not duplicate information visible in panel art | BLOCKER | manga_profile.narration_tolerance + market_demo |

MDLG-11 is the female-reader grammar gate. It is the most important new gate.
Implementation: scan lettering_spec for caption panels; for each caption panel,
check whether the dialogue/caption text restates what is visible in the
visual_prompt (character state, emotion, action). If yes → flag as redundant exposition.

---

## 7. Implementation Roadmap — 7 PRs

**Week 1 (2 PRs):**

**PR-01: manga_profile loader + schema**
- New: `phoenix_v4/manga/series/profile_loader.py` (load_manga_profile, manga_profile_seed)
- New: `config/source_of_truth/manga_profiles/schema.yaml` (this sprint — already done)
- New: `config/source_of_truth/manga_profiles/examples/` (3 profiles — this sprint — done)
- Extend: `phoenix_v4/manga/series/story_architect.py` (+manga_profile param)
- New: `tests/test_manga_profile_determinism.py` (3 assertions)

**PR-02: josei ITE profile**
- Extend: `config/manga/genre_ite_profiles.yaml` — add josei profile
  (higher reaction_shot_frequency, botanical fractal sources, relationship_escalation
  serialization awareness, tempo_floor_bpm: 60, distinct color_arc)
- Extend: `config/manga/style_archetypes.yaml` — add grounded_josei_realism archetype
  (maps to brand_illustration_styles.yaml parameters)
- Add: `tests/test_manga_josei_ite_profile.py`

**Week 2 (2 PRs):**

**PR-03: chapter_hook_family typed enum**
- Extend: `schemas/manga/manga_common.schema.json` — add chapter_hook_family enum type
- Extend: `phoenix_v4/manga/series/story_architect.py` — validate chapter_end_hook
  against profile's chapter_hook_family
- Extend: `phoenix_v4/manga/models/validation.py` — schema validator update
- New: `tests/test_manga_chapter_hook_validation.py`

**PR-04: MDLG-06, MDLG-07 gates**
- Extend: `config/manga/manga_gates.yaml` — add MDLG-06, MDLG-07 gate definitions
- Extend: `phoenix_v4/manga/qc/chapter_qc.py` — implement chapter_addiction and
  silence_density checks using manga_profile fields
- New: `tests/test_manga_chapter_addiction_gate.py`
- New: `tests/test_manga_silence_density_gate.py`

**Week 3 (3 PRs):**

**PR-05: MDLG-08, MDLG-09 gates**
- genre_authenticity gate (panel tempo + dialogue density vs genre_ite_profiles)
- catalog_homogeneity gate (cross-title emotional_engine dedup check)
- New scripts: `scripts/manga/catalog_homogeneity_check.py`

**PR-06: MDLG-10, MDLG-11 gates**
- reader_promise_fulfillment gate (ITE scorer integration)
- restraint_over_exposition gate (caption ↔ visual redundancy check)
- This is the female-reader grammar gate — highest impact for shojo/josei content

**PR-07: runner integration**
- Wire manga_profile loading into chapter_runner.py
- Pass manga_profile through to all QC gates
- Integration test: end-to-end chapter run with profile-driven gate validation
- Update MANGA_PIPELINE_ONBOARDING.md with profile setup instructions

---

## 8. Anti-Recommendations

**Do not rebuild speech bubbles / lettering.**
`phoenix_v4/manga/chapter/lettering_from_script.py` and `lettering_from_script.py`
are production-grade. The silence_confirmed + lettering_spec pipeline is tested
and deployed. Build on it, do not replace it.

**Do not rebuild cover design research.**
`artifacts/research/western_illustrated_styles_2026_04_04.md` and the visual style
archetypes in `config/manga/style_archetypes.yaml` provide the cross-format comparison
matrix. No additional cover design research is needed for the schema to function.

**Do not rebuild genre ITE profiles from scratch.**
`config/manga/genre_ite_profiles.yaml` has 10 working profiles.
Add josei (PR-02). Do not redesign the existing profiles.

**Do not create a separate manga pipeline.**
`specs/MANGA_MODE_SYSTEM_SPEC.md` is explicit: manga extends the Pearl Prime pipeline,
not a parallel system. Option C determinism preserves this — one insertion point,
no fork.

**Do not add manga_profile fields as hash-seed inputs.**
That would cause downstream selections to change whenever a new profile axis is added.
Profile fields filter the pool. Hash selects within the pool. These are separate concerns.

**Do not treat the external review's MDLG numbering as canonical.**
The review used "MDLG-06 through MDLG-11" but the repo does not use this terminology.
The correct home for these gates is `config/manga/manga_gates.yaml` using the existing
`MANGA.*` naming convention. The MDLG numbering in this doc is a convenience label only.

---

---

## 9. Note on `config/manga/manga_taxonomy.yaml` (committed 2026-04-19)

This file (673 lines) was committed directly to `main` without a branch or PR, bypassing
push-guard and preflight. It was produced by the same external source as the strategic
read analyzed in Phase 1 of this sprint — the source that got 5 of 7 repo claims wrong.

**What to do with it:**

The taxonomy file is structurally sound and not obviously wrong. However it was written
without access to the existing ITE genre profiles (`config/manga/genre_ite_profiles.yaml`),
style archetypes (`config/manga/style_archetypes.yaml`), or the QA gate system. Before
treating it as canonical, a follow-up task should:

1. Cross-check every `genre_family`, `emotional_engine`, and `visual_grammar` entry against
   the existing 10 ITE profiles and 8 style archetypes — dedup, reconcile, resolve conflicts.
2. Move it to `config/source_of_truth/manga_taxonomy.yaml` once reconciled (the canonical
   path per repo conventions is `config/source_of_truth/`, not `config/manga/`).
3. Add it as PR 0 in the 7-PR roadmap above (reconciliation work, ~0.5 days).

Until reconciled, treat it as **draft / unverified input**, not as a system constraint.

---

*Operator decisions needed: see PR section for open questions.*
*Full verification details: `artifacts/audit/manga_framework_reality_check.md`*
*Full Q&A: `artifacts/analysis/manga_native/01_three_questions_answered.md`*
