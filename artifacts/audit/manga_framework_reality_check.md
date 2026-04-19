# Manga Framework Reality Check
**Sprint:** manga-native-system-layer verification
**Date:** 2026-04-19
**Method:** Static repo analysis — no API calls, no web search

---

## External Claims Under Review

The external strategic read argued that Phoenix Omega has a "Western illustrated-format
framework" but no manga-native story grammar layer, citing seven specific gaps.
Each claim is rated below against actual repo evidence.

---

## Claim 1: "No manga-specific framework"

**Claim text (paraphrase):** Phoenix has no manga-specific pipeline; manga output
is produced via the general illustrated format system without genre-native architecture.

**Rating: INCORRECT**

**Evidence:**
- `phoenix_v4/manga/` — 45 Python files, full production pipeline with DAG runner,
  chapter writer, visual prompt compiler, lettering, QC, and series memory
- `specs/MANGA_MODE_SYSTEM_SPEC.md` — Full system spec defining manga as distinct from
  all other format modes, with invariants (visual prompt determinism, teacher-pure rule,
  arc-first rule, structural entropy gates)
- `specs/MANGA_GENRE_AGENT_SPEC.md` — Defines genre-specific structural embedding doctrine
  (structural embedding over dialogue embedding); per-genre conventions as "load-bearing
  architecture"
- `specs/MANGA_STORY_ARCHITECT_SPEC.md` — Full spec for chapter-level beat architecture,
  chapter_end_hook system, serialization-aware beat density rules
- `.github/workflows/manga-pipeline.yml`, `manga-image-gen.yml`, `manga-smoke-test.yml`,
  `manga-quality-forensic-analysis.yml`, `manga-image-bank-build.yml` — 10 dedicated CI workflows
- `tests/test_manga_*.py` — 18 dedicated test files

**Note on PR history:** The claim references "PR #473 (speech bubbles)" and "PR #497
(cover design)" as evidence of ad-hoc patches. What the repo shows instead is a
coherent, production-grade pipeline with architectural specs, dedicated DAG runner,
and CI coverage. The lettering system (speech bubbles) is at
`phoenix_v4/manga/chapter/lettering_from_script.py` — a first-class module, not a patch.

---

## Claim 2: "Taxonomy is demo-labels-only"

**Claim text (paraphrase):** Genre labels (shonen, seinen, etc.) are decorative metadata
used for naming/categorization but have no effect on story generation logic.

**Rating: INCORRECT**

**Evidence:**
- `config/manga/genre_ite_profiles.yaml` — 10 genre-specific ITE profiles with different
  `breath_sequences`, `fractal_regulation` density, `color_arc` profiles, `gutter_therapy`
  rules, `sabido_roles`, and `soundtrack` parameters. Iyashikei has 4–6 breath sequences/chapter
  (vs shonen's 1–4). These are not labels — they are runtime control parameters.
- `phoenix_v4/manga/series/story_architect.py` — genre_id controls beat selection:
  `_SETTINGS["shonen"]` vs `_SETTINGS["iyashikei"]` vs `_SETTINGS["seinen"]` produce
  different settings, protagonist names, and rival archetypes from the same beat templates.
- `specs/MANGA_GENRE_AGENT_SPEC.md` — Genre Agent spec explicitly maps genre to structural
  behavior: "Shōnen battle carries teachings through escalation and sacrifice rituals;
  Seinen psychological carries through silence and subtext compression" — with Cold Read Gate
  enforcement.
- `config/manga/style_archetypes.yaml` — 8 visual style archetypes (cozy_iyashikei,
  dark_psychological, power_progression, etc.) with distinct prompt templates, negative
  prompts, and rendering parameters.
- `artifacts/research/manga_genre_writing_styles_2026_04_04.md` — Full playbook for
  10 genres with quantified metrics (words/page, panels/page, silent panel ratios,
  dialogue-to-narration ratios) used by the Chapter Writer.

---

## Claim 3: "No female-reader grammar"

**Claim text (paraphrase):** The pipeline has no mechanics specific to female-reader
demographics (shojo, josei). The audience model is gender-neutral or defaults to
male-coded shonen grammar.

**Rating: PARTIALLY CORRECT**

**Evidence for existing female-reader coverage:**
- `config/authoring/manga_authors/schema.yaml` — `genre_tie_in` enum explicitly includes
  `josei` and `shojo`. Author identities can be genre-tied to female-reader demographics.
- `config/manga/genre_ite_profiles.yaml` — `shojo` has its own ITE profile with distinct
  `breath_sequences` (min 2, required in resolution), `fractal_regulation: botanical`
  source categories, `color_arc: standard`, and `tempo_floor_bpm: 66`
- `config/manga/brand_illustration_styles.yaml` — brand-level illustration styles
  reference "shojo" and genre-appropriate visual DNA
- `specs/MANGA_GENRE_AGENT_SPEC.md` — "Shōjo romance carries teachings through
  vulnerability sequencing and mirror dynamics" is explicitly codified as structural behavior
- `config/manga/manga_mode_spec` at line 214: `target_audience: [gen_z_female, asia]`

**What is missing (genuine gap):**
- `josei` does NOT have its own ITE profile in `config/manga/genre_ite_profiles.yaml`
  (shojo does; josei does not)
- No dedicated `josei` visual style archetype in `style_archetypes.yaml`
- No explicit "restraint-over-exposition" or "show-don't-tell-in-romance" rule in the
  Chapter Writer spec — the shojo/josei grammar requires this distinction
- The author schema allows josei genre_tie_in but the ITE execution layer does not yet
  implement josei as distinct from seinen/shojo

**Verdict:** Shojo coverage is substantive. Josei coverage is schema-only (no runtime
ITE profile). The gap is real but narrower than claimed.

---

## Claim 4: "No chapter-addiction engineering"

**Claim text (paraphrase):** The pipeline produces chapters with arbitrary endings.
There is no system for engineering chapter-end hooks that drive compulsive re-reads
or next-chapter purchases.

**Rating: INCORRECT**

**Evidence:**
- `specs/MANGA_STORY_ARCHITECT_SPEC.md` §12 (Chapter End Hook System):
  - `chapter_end_hook` is a required field in story architecture output
  - Serialization-cadence-aware rules: weekly serialization requires "high-tension
    chapter_end_hook (question, danger, revelation)"; volume format allows soft close
  - Hook taxonomy in spec: Cliffhanger, Revelation, Ambiguous, Soft-Close — each
    with behavioral requirements
  - 18 worked example hooks in spec appendix including revelation, interruption, vow,
    arrival, emotional rupture
- `phoenix_v4/manga/series/story_architect.py` line 118: `"chapter_end_hook": hook`
  is emitted as a first-class field in every chapter's story architecture
- `phoenix_v4/manga/transmission.py` lines 28-29: `chapter_end_hook` is preserved
  in the writer handoff (not stripped)
- Spec §12 line 466: "Weekly: chapter_end_hook must be high-tension (question,
  danger, revelation)"

**What is missing (genuine refinement opportunity):**
- `chapter_end_hook` exists as freeform text, not a typed enum
- No `chapter_hook_family` enum enforced at schema level (the family taxonomy
  in the spec is descriptive, not validated)
- No cross-chapter hook deduplication gate (MDLG-09 equivalent)

---

## Claim 5: "No manga-native QA"

**Claim text (paraphrase):** There is no QA system specific to manga output. Quality
control applies the same gates as prose books.

**Rating: INCORRECT**

**Evidence:**
- `config/manga/manga_gates.yaml` — 4 manga-specific QA gates:
  - `MANGA.PROMPT.STRUCTURE` (BLOCKER) — visual prompt per-panel compliance
  - `MANGA.PROMPT.TOKEN_BUDGET` (MAJOR) — prompt token count ≤120 positive, ≤60 negative
  - `MANGA.TEACHING.PANEL_EXPRESSION` (MAJOR) — panel_expression preservation
  - `MANGA.SILENCE.STRUCTURE` (BLOCKER) — silent panel intent must be machine-visible
- `phoenix_v4/manga/qc/chapter_qc.py` — Full QC implementation with:
  - Story handoff validation
  - Panel manifest completeness check
  - Lettering-silence mismatch detection
  - Layout composite page verification
- `phoenix_v4/manga/qc/gate_registry.py` — Gate registry loader
- `phoenix_v4/manga/qc/ite_scorer.py` — ITE-specific scoring
- `.github/workflows/manga-quality-forensic-analysis.yml` — CI-level forensic analysis
- 18 test files covering all QC paths

**What is missing (genuine refinement opportunity):**
- No genre-aware QA (a shonen chapter passing MANGA.SILENCE.STRUCTURE at 5% silent panels
  would fail if it were iyashikei which requires 30%+ silence)
- No chapter_addiction gate (hook quality check is not automated)
- No catalog-level homogeneity gate

**Note on MDLG:** The claim referenced "MDLG" as a system that might or might not exist.
Searching the main repo for "MDLG" returns no results — this acronym is not used in
the Phoenix codebase. The equivalent system is the manga QC gate infrastructure
(manga_gates.yaml + chapter_qc.py). The external doc's MDLG terminology is not
native to this repo.

---

## Claim 6: "No genre-specific pacing contracts"

**Claim text (paraphrase):** There are no per-genre contracts defining panel density,
words/page, silence ratios, or reader pacing expectations.

**Rating: INCORRECT**

**Evidence:**
- `artifacts/research/manga_genre_writing_styles_2026_04_04.md` — full quantified
  pacing metrics for 10 genres:
  - Shonen: 30-80 words/page, 3-5 panels/page, 10-15% silent panel ratio
  - Seinen: narrative compression, higher silence tolerance
  - Iyashikei: 20-40 words/page implied, 4-6 breath sequences/chapter
  - Horror: specific breath_sequence constraints (1-2/chapter), gothic pacing
- `config/manga/genre_ite_profiles.yaml` — per-genre ITE profiles with `breath_sequences`
  (min/max per chapter, required sections), `fractal_regulation` density,
  `gutter_therapy` rules, soundtrack tempo ranges — these are pacing contracts
  in machine-readable form
- `specs/MANGA_GENRE_AGENT_SPEC.md` — "When dharma conflicts with genre convention,
  the convention wins" — the genre's emotional contract with its reader is treated
  as inviolable constraint

**What is missing (genuine refinement opportunity):**
- No formal `pacing_contract` schema object (pacing rules are distributed across
  research docs and ITE profiles, not consolidated in one schema)
- No `words_per_page_target` or `silent_panel_ratio_target` as first-class fields
  in a manga_profile schema (proposed in this sprint)
- Josei-specific pacing is not in the ITE profiles

---

## Claim 7: "No multiple visual grammars"

**Claim text (paraphrase):** The pipeline renders all manga output in a single visual
style; there is no system for selecting or switching visual grammars by genre.

**Rating: INCORRECT**

**Evidence:**
- `config/manga/style_archetypes.yaml` — 8 named visual style archetypes:
  - `cozy_iyashikei` — pastel, soft lighting, watercolor
  - `dark_psychological` — high contrast, heavy ink, screen tones, halftone
  - `power_progression` — dynamic action, speed lines, shonen style
  - `webtoon_vertical_romance` — full color, soft shading, atmospheric
  - `hyper_clean_cinematic` — glossy, lens flare, 4K anime
  - `meme_chaotic_humor` — exaggerated expressions, 4-koma style
  - `social_media_simulacra` — UI elements, digital aesthetic
  - `interactive_branching` — visual novel style, cel shading
- `config/manga/brand_illustration_styles.yaml` — per-brand visual DNA (each brand
  gets its own style: stillness_press = "Contemplative Ink Wash" / cozy_iyashikei;
  cognitive_clarity = "Stark Zen Ink" / dark_psychological)
- `specs/MANGA_MODE_SYSTEM_SPEC.md` invariant: "Every volume has exactly one
  `style_archetype_id` locked for its entire duration. No mid-volume style switching."
- `config/manga/genre_ite_profiles.yaml` — genre-level style differentiation
  through `color_arc`, `fractal_regulation.source_categories`, and `shading` parameters

**What is missing (genuine refinement opportunity):**
- No formal mapping of genre → recommended visual grammar (the 8 archetypes exist
  but there is no rule saying "shonen should use power_progression")
- `line_weight_profile`, `black_fill_ratio`, `screentone_profile` are not yet
  first-class schema fields (proposed in this sprint's manga_profile schema)
- `spread_frequency` and `reaction_shot_frequency` are not yet formalized

---

## Summary Table

| Claim | Rating | Key Evidence |
|---|---|---|
| No manga-specific framework | INCORRECT | phoenix_v4/manga/ (45 py), 12 specs, 10 CI workflows |
| Taxonomy is demo-labels-only | INCORRECT | genre_ite_profiles.yaml (10 profiles), story_architect.py hash-seeding |
| No female-reader grammar | PARTIALLY CORRECT | shojo ITE profile exists; josei ITE profile missing |
| No chapter-addiction engineering | INCORRECT | chapter_end_hook in spec §12 + story_architect.py + transmission.py |
| No manga-native QA | INCORRECT | manga_gates.yaml (4 gates), chapter_qc.py, 18 test files |
| No genre-specific pacing contracts | INCORRECT | genre_ite_profiles.yaml + manga_genre_writing_styles research |
| No multiple visual grammars | INCORRECT | style_archetypes.yaml (8 styles), brand_illustration_styles.yaml |

**Score: 5 INCORRECT / 1 PARTIALLY CORRECT / 0 CORRECT**

---

## Genuine Gaps (Not Overstated)

1. **Josei ITE profile** — josei is in the author schema enum but has no runtime ITE
   profile (unlike shojo which does)
2. **chapter_hook_family enum** — hooks exist as freeform text, no typed schema
3. **manga_profile as title-level identity** — no `manga_profile` schema yet
   (genre, visual grammar, pacing contract all stored separately; no unified record)
4. **Catalog homogeneity gate** — no gate preventing all titles from having the same
   emotional engine or hook pattern
5. **Restraint-over-exposition gate** — no automated check that shojo/josei chapters
   show rather than tell in emotional scenes

These are refinement opportunities, not foundational absences.
