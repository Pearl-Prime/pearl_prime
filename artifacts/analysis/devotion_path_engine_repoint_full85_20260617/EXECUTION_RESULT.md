# devotion_path A′-full-85 engine re-point — NAMING-ENGINE titles edition (EXECUTION RESULT)

**WS:** `ws_devotion_path_engine_repoint_20260615` (re-dispatch 2026-06-17; prior run died on machine-sleep, produced no PR)
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1
**Subsystems:** catalog_planning, core_pipeline
**Date:** 2026-06-17
**Agent:** Pearl_Prime
**Status:** **EXECUTED — 0 illegal / 85 legal cells, all titles from the naming engine (#1677).**
**Authority:** `docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` §5 · `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4` · `config/topic_engine_bindings.yaml` (hard gate) · `config/catalog_planning/engine_title_angles.yaml` (copy source) · `phoenix_v4/naming` (title/subtitle source, PR #1677 = origin/main HEAD 29c3fd76bc).

---

## 0. What changed vs the 2026-06-15 execution

The 2026-06-15 generator (`../devotion_path_engine_repoint_full85_20260615/repoint_generator.py`)
was correct on engine-legality but sourced titles/subtitles from a **hand-authored
`ENGINE_FRAMING` table**. The binding for this re-dispatch is explicit:
**"titles/subtitles from the naming engine (phoenix_v4/naming/), never hand-written."**

This edition (`repoint_with_naming_engine.py`) is identical in mechanics EXCEPT every
title + subtitle now comes from the canonical naming engine (`phoenix_v4.naming.cli.run`,
`angle_id = engine`), batch-deduped across the 85 cells. The 2026-06-15 dir is retained as
the engine-legality forensic record; THIS dir is the authoritative re-point applied to the PR.

**Critical context (clean-main truth):** the §5 re-point had **NOT** landed on origin/main.
Main (HEAD 29c3fd76bc = #1677) still carried **99 devotion plans, 66 engine-ILLEGAL** (anxiety
triad on burnout/courage/imposter), with naming-engine titles applied to those 99 by #1677.
The legal-85 set existed only on a local diverged branch, never merged. This PR is the first
to bring the re-point to a clean origin/main base.

---

## 1. Before / after (clean origin/main 29c3fd76bc)

| Verdict | BEFORE (99 plans, main) | AFTER (85 plans, re-pointed) |
|---|---|---|
| `BUILDABLE_LEGAL` (arc + engine allowed) | 31 | **85** |
| engine-ILLEGAL (forbidden engine) | **66** | **0** |
| arcless legal (no F006 arc) | 2 | 0 written (3 tracked backfill) |
| **TOTAL plans on disk** | **99** | **85** |

Per-topic legal tally (AFTER): burnout **33**, courage **30**, imposter_syndrome **22** = **85**.
**Planned %: 85/85 = 100.0% of the legal arc-backed surface** (96.6% incl. the 3 arc-blocked
gen_z_student courage backfill cells → 85/88).

---

## 2. What executed

Pure engine-axis re-point + naming-engine title/subtitle + plan-copy regeneration + retire-and-recreate.
**Zero arcs authored. Zero atoms touched.** Re-point map applied (all legal vs the binding):

```
burnout            → overwhelm, watcher, grief          # dropped false_alarm, spiral
courage            → false_alarm, spiral, shame          # dropped overwhelm
imposter_syndrome  → shame, comparison                   # dropped false_alarm, overwhelm, spiral
```

- **85 book_plans** written (every legal, arc-backed cell). 31 kept the same book_id (already-legal),
  54 newly created.
- **33 series_plans** re-pointed (`arc:` block redrawn to the topic's legal engine set).
- **68 illegal/superseded book_plan files removed** (retire-and-recreate, provenance in
  `RETIRED_BOOK_IDS.tsv`).
- **Titles/subtitles:** 100% from the naming engine. Persona/topic-specific copy (bisac, price,
  comps, character, keywords.primary, reader_avatar, voice markers) preserved verbatim by cloning
  the same-(persona,topic) source plan. Engine-specific description/cover_tagline/keywords.secondary
  regenerated from `engine_title_angles.yaml` (config-grounded, spec §5 rule 3).

---

## 3. Structural validation (re-derived from disk after apply)

| Check | Result |
|---|---|
| Book plans parse | **85 / 85** |
| Engine ∈ topic `allowed_engines` (Arc-First §4) | **85 / 85 legal** (0 illegal) |
| `engine:` field == filename engine | **85 / 85 match** |
| Arc-backed (`<persona>__<topic>__<engine>__F006.yaml` exists) | **85 / 85** |
| `series_plan:` ref resolves | **85 / 85** |
| Distinct (title, subtitle) pairs | **85 / 85** |
| Titles with "X: A &lt;Topic&gt; Book" tail | **0** |
| Subtitles with "Readers" fallback | **0** |
| Variable-leak `{ }` in title/subtitle | **0** |
| Within-series duplicate titles (reader sees the 3-book set) | **0 / 32 series** |
| Subtitles NOT naming their persona | **0 / 85** |
| Series plans parse | **33 / 33** |
| Series `arc:` engines legal | **88 / 88** |
| Series `master_arc` refs resolve | **85 / 88** (3 missing = gen_z_student courage backfill, marked `backfill_pending`) |

**Title source:** every title/subtitle is naming-engine output (angle_id = engine), e.g.
`burnout/overwhelm/corporate_managers` → "When Everything Is Too Much" / "A Real Talk Guide to
Burnout Recovery for Managers"; `imposter_syndrome/comparison/...` → "The Comparison Habit". Note
titles repeat across personas by design (#1677: title from topic×engine; the **subtitle** carries
the persona and the keyword) — the (title,subtitle) pair is unique and within-series titles differ.

**Not run:** prose render / coherence / register gates — these are F-COHERENCE (#1589/#1590/#1601),
deliberately out of scope (composer SCENE atoms mid-repair). See the wave proof in
`artifacts/release/2026-W25/devotion_path_wave_20260617/` for the draft-profile assembly result.

---

## 4. The 3-cell gen_z_student-courage backfill (enumerated, NOT authored)

```
devotion_path__sai_ma__gen_z_student__courage__false_alarm
devotion_path__sai_ma__gen_z_student__courage__spiral
devotion_path__sai_ma__gen_z_student__courage__shame
```

Engine-legal but arcless (gen_z_student courage arcs are F003 seeds, never promoted to F006). The
gen_z_student courage series_plan IS re-pointed (catalog shape consistent) and carries a
`backfill_pending` enumeration; no book_plans created. Needs a Pearl_Architect arc-schema ruling.

---

## 5. NEXT_ACTION

- This pass (F-ENGINE) is necessary but not sufficient for production prose. Production assembly
  stays GATED on **F-COHERENCE** (#1589 topic-aware atom routing + #1590 SCENE-atom repair + #1601
  register) and the **B2 release-profile contract** (`--quality-profile production` currently emits
  no manuscript). The 2026-06-17 draft wave proves the plans build and pass flow/EI-v2/craft but
  HOLD on scene-anchor-density (the SCENE-atom defect).
- DO-NOT-MERGE pending operator review (per session scope + spec §7 operator A′-shape pick).
