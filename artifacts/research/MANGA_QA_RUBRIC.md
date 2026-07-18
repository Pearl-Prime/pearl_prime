# Manga QA Rubric
## Phoenix Omega — Document of Record
**Date:** 2026-04-20
**Authority:** This document describes gates live in the production pipeline.

---

## Purpose

This rubric documents all manga-native QC gates. It covers:
- Gates live in `phoenix_v4/manga/qc/chapter_qc.py` (per-chapter)
- Gates live in `scripts/manga/check_catalog_homogeneity.py` (catalog-level)
- How gates interact with `manga_profile` (title-level identity)
- Escalation behavior on gate failure

Gates that use `manga_profile` skip gracefully when no profile is resolved — all profile-dependent gates are designed to be backward-compatible with chapters run without a profile.

---

## Dimensional Scope

Each gate scores along one of 6 dimensions:

| # | Dimension | What It Measures |
|---|-----------|-----------------|
| 1 | **Reads-like-manga** | Balloon density, over-explanation, silence use |
| 2 | **Genre authenticity** | Does pacing match the declared manga_profile? |
| 3 | **Chapter addiction** | Does the chapter end create next-click desire? |
| 4 | **Visual consistency** | Style matches profile visual_grammar? |
| 5 | **Catalog distinctiveness** | Does this title differ from its neighbors? |
| 6 | **Reader promise** | Does the chapter deliver on profile.reader_promise? |

---

## Live Gates

### Baseline Infrastructure Gates (always active, profile-independent)

#### MANGA_GATE_STORY_HANDOFF
- **Scope:** Pre-chapter-write (transmission_split stage)
- **Checks:** `story_architecture_handoff.json` is present and valid per schema
- **Severity:** BLOCKER
- **Implementation:** `phoenix_v4/manga/qc/chapter_qc.py`

#### MANGA_GATE_IMAGES_ALL_OK
- **Scope:** Post-image-gen
- **Checks:** All panels in `panel_images_manifest.json` have status=ok, path, width, height
- **Severity:** BLOCKER
- **Implementation:** `phoenix_v4/manga/qc/chapter_qc.py`

#### MANGA_GATE_LETTERING_SILENCE
- **Scope:** Post-lettering
- **Checks:** `silence_confirmed` in lettering spec matches actual dialogue presence in script
- **Severity:** BLOCKER
- **Implementation:** `phoenix_v4/manga/qc/chapter_qc.py`

#### MANGA_GATE_LAYOUT_PAGES
- **Scope:** Post-layout
- **Checks:** All expected `page_NNN.png` composites exist in `final_pages/`
- **Severity:** BLOCKER
- **Implementation:** `phoenix_v4/manga/qc/chapter_qc.py`

---

### Profile-Dependent Gates (skip gracefully when manga_profile is None)

#### MANGA.CHAPTER.HOOK (MDLG-06)
- **Dimension:** Chapter addiction
- **Scope:** Chapter end (last panel of last page)
- **Checks:** Does the final beat contain keyword signals matching `profile.chapter_hook_family`?
- **11 hook families covered:** revelation, interruption, betrayal, vow, arrival, almost_confession, new_rival, hidden_truth_glimpse, ominous_image, emotional_rupture, ambiguous_line
- **Severity:** MAJOR (not BLOCKER — writer can regenerate final beat)
- **Fires on:** Chapter without detectable hook signal matching declared family
- **Implementation:** `phoenix_v4/manga/qc/hook_gate.py` → called by `chapter_qc.py`
- **Tests:** `tests/manga/test_hook_gate.py`

#### MANGA.SILENCE.DENSITY (MDLG-07)
- **Dimension:** Reads-like-manga
- **Scope:** Full chapter
- **Checks:** Silent panel ratio (panels with no dialogue / total panels) within `profile.pacing.silent_panel_ratio ± 0.15`
- **Severity:** MAJOR
- **Note:** Iyashikei targets 0.35–0.60; shonen targets 0.10–0.25. Deviation beyond ±0.15 signals wrong register.
- **Implementation:** `phoenix_v4/manga/qc/pacing_gates.py::check_silence_density`
- **Tests:** `tests/manga/test_pacing_gates.py`

#### MANGA.GENRE.AUTHENTICITY (MDLG-08)
- **Dimension:** Genre authenticity
- **Scope:** Full chapter
- **Checks:** Words-per-page within `profile.pacing.words_per_page_target ± 30%`
- **Severity:** MAJOR
- **Cross-reference:** `config/manga/manga_pacing_by_genre.yaml` provides genre-family level contracts; individual profile may override within ±25% of genre contract.
- **Implementation:** `phoenix_v4/manga/qc/pacing_gates.py::check_genre_authenticity`
- **Tests:** `tests/manga/test_pacing_gates.py`

#### MANGA.RESTRAINT.EXPOSITION (MDLG-09a)
- **Dimension:** Reads-like-manga + Reader promise
- **Scope:** Chapter (josei, shojo, romance only)
- **Checks:** Explicit emotional narration ("she felt", "he realized", "her heart") in >25% of panels
- **Severity:** MAJOR
- **Applies to:** `market_demo in [josei, shojo]` OR `genre_family = romance`
- **Skip condition:** Shonen/seinen chapters outside romance — gate skips completely
- **Implementation:** `phoenix_v4/manga/qc/restraint_gate.py`
- **Tests:** `tests/manga/test_restraint_gate.py`

#### MANGA.YEARNING.PACING (MDLG-09b) — NEW in this sprint
- **Dimension:** Reads-like-manga + Reader promise (yearning-family craft)
- **Scope:** Chapter (shojo + josei + romance genre_family)
- **Checks:**
  1. Show/tell ratio (show = reaction panels, gesture, silence; tell = narration, internal monologue) ≥ 0.40
  2. Confession events delivered via pure exposition (no preceding scene work)
  3. First-person realization patterns ("I realized I loved him", "I understood now I") — warned at ≥ 2 hits
- **Severity:** Block on show/tell < 0.40 OR exposition-only confessions; WARN on smell-test hits
- **Skip condition:** Not shojo/josei/romance → gate skips; no profile → gate skips
- **Implementation:** `phoenix_v4/manga/qc/yearning_gate.py` → called by `chapter_qc.py`
- **Reference corpus:** Fruits Basket vol 1 ch1, Honey and Clover vol 1 ch1, Ao Haru Ride vol 1 ch1
- **Tests:** `tests/manga/test_yearning_gate.py`

---

### Catalog-Level Gates (run outside per-chapter pipeline)

#### MANGA.CATALOG.HOMOGENEITY (MDLG-10)
- **Dimension:** Catalog distinctiveness
- **Scope:** Cross-title (catalog-plan stage, not per-chapter)
- **Checks:**
  1. No two active titles share identical `(emotional_engine, chapter_hook_family)` — EXIT 2 (collision, blocking)
  2. No three+ titles share identical `(market_demo, genre_family, visual_grammar)` — EXIT 1 (lane overlap, warning)
- **Exit codes:** 0 = clean, 1 = warnings only, 2 = blocking collision
- **Implementation:** `scripts/manga/check_catalog_homogeneity.py`
- **Tests:** `tests/manga/test_catalog_homogeneity.py`
- **Run:** Pre-merge for any new manga_profile addition. Integrated into CI via `scripts/ci/preflight_push.sh`.

---

## ITE Gates (T-01 through T-20)

Twenty immersive-therapeutic-expression gates defined in `config/manga/ite_profiles/` and run by `phoenix_v4/manga/ite_pipeline.py`. These gates score:
- Panel breath (T-01..T-05)
- Gutter therapy (T-06..T-10)
- Color arc (T-11..T-15)
- Fractal compliance (T-16..T-20)

See `artifacts/research/ITE_FRAMEWORK.md` for full ITE gate documentation.

---

## Operator Escalation

Gate fires at BLOCKER → chapter is held, not delivered. Runner retries up to configured `max_revision_attempts`.
Gate fires at MAJOR → chapter enters revision queue. Writer stage is re-invoked with gate evidence + fix hint.
Gate fires at WARN → logged, chapter proceeds. Reviewed at catalog plan stage.

Repeated BLOCKER failure (exhausted retries) → chapter surfaces to operator with gate evidence, fix direction from `profile.reader_promise`, and reference corpus suggestion from `config/manga/manga_pacing_by_genre.yaml`.

---

## Regression Museum Interaction

All MANGA.* and MANGA_GATE_* failures also emit entries to the regression museum (`config/governance/regression_museum.yaml`). Any confirmed manga failure pattern can be locked as a museum entry to block CI on regression.

See `phoenix_v4/quality/regression_museum/` for museum tooling.

---

## Adding a New Gate

1. Create `phoenix_v4/manga/qc/{gate_name}.py` — single function returning `dict | None`
2. Add import + call to `chapter_qc.py::build_revision_queue_for_chapter()` in the profile-dependent block
3. Register in `config/manga/manga_gates.yaml`
4. Add to this rubric under the appropriate dimension
5. Write tests: known-good, known-bad, skip-case, no-profile-case
