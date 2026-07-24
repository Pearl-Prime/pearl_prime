# Manga Series Master Plan Contract

Status: v1.0 SPECCED + CODE-WIRED (advisory gate + one EXECUTED-REAL golden example)
Owner: Pearl_Architect + Pearl_Dev / Manga Story Governance (manga process uplift Lane 06)
Created: 2026-07-24
Schema: `schemas/manga/series_master_plan.schema.json`
CI: `scripts/ci/check_manga_series_master_plan.py` (advisory gate 48 in `scripts/run_production_readiness_gates.py`)
Research basis: `artifacts/research/manga_arc_cadence_study_2026-07-24.md` +
`config/manga/manga_pacing_by_genre.yaml` `arc_cadence` blocks (all 21 families, PR #322) +
`artifacts/research/us_illustrated_self_help_format_study_2026-07-24.md` (PR #320)

## Purpose

A per-series long-horizon plan (default **100 episodes**) that sits **ABOVE** the
existing per-arc storyboards (`MANGA_ARC_STORYBOARD_CONTRACT.md`) and **BELOW** the
series_plan listing (`schemas/manga/series_plan.schema.json`):

```text
series_plan (catalog listing: format, locale, platforms)
  → SERIES MASTER PLAN (this contract: genre-cadence arcs over eps 1..N,
      per-arc premise/promise/shift/MC-vector/topic/mode-arc,
      per-episode planning pass inside each detailed arc)
  → arc storyboard plan (per episode: story_move + visual_proof)
  → chapter_script_writer_handoff → excellence gate → render
```

A series_plan is a listing, not a story (`check_manga_story_authored` doctrine).
The master plan is the layer that makes 100 episodes *plannable* before any of
them is written — and it is what `phoenix_v4/manga/series/story_architect.py`
and the storyboarder consume: every arc/episode entry resolves to the inputs
story_architect already takes (series / arc / genre / topic / mode / chapter).

## Non-Goals

- Does NOT replace or invalidate the 48-episode program
  (`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/`, PRs #295/#243
  lineage). It **wraps** it: the 48-ep 4×12 plans map onto the master plan as the
  "near-term detailed window" (§Migration). Inventory EXTENDS, never REDUCED.
- Does NOT author master plans at scale. This contract + validator + ONE golden
  example land here; Lane 11 pilots one series through the full loop; scale is a
  follow-on program.
- A validator PASS is at most `structurally_clear` / `authored_candidate` —
  never bestseller, never PROVEN-AT-BAR.

## 1. Arc segmentation is genre-derived — NEVER a fixed 12

Number and lengths of arcs over eps 1..N come from the genre's `arc_cadence`
block in `config/manga/manga_pacing_by_genre.yaml`
(`episodes_per_arc_range`, `episodes_per_arc_median`, `arc_pattern`,
`first_major_shift_by`). The canonical `genre_id` resolves to its pacing family
via `genre_family_aliases` (e.g. `iyashikei → healing`,
`psychological_thriller → mystery`, `sports_competition → sports`).

**Three cadence regimes need three segmentation functions** (study
§Cross-family findings — do not force one tiling algorithm):

| `arc_pattern` | Segmentation function | Families (2026-07-24) |
|---|---|---|
| `escalating` | Arc lengths trend upward as the run matures; start near the range floor, later arcs larger, all within `episodes_per_arc_range` ±25%. Late-run mega-arcs beyond the range are outliers, not planning targets. | battle, mystery, sports, social_issue, fantasy, battle_internal, dark_fantasy, mecha, sci_fi_cyberpunk, historical_period, cultivation_martial |
| `fixed` | Roughly constant arc size near `episodes_per_arc_median` (ladder-rung / episodic-unit genres); stakes escalate, size does not. | romance, workplace, horror, essay, memoir, supernatural_everyday, graphic_medicine, gag |
| `seasonal_cycle` | The calendar is the structure: small vignette/trip cycles (within range) hung on **season wheels** (~3–4 wheels per 100 eps) with demographic — not plot — drift. Declare wheels in `season_wheels`. | healing, school |

**Cadence conformance tolerance:** arc lengths must fall within
`episodes_per_arc_range` ±25% — the same deviation band the pacing file uses
for MDLG-08. Every cadence number in a plan traces to the pacing yaml (or a
declared study source, §1c/§US-illustrated) — a plan may not invent its own.

### 1a. `first_major_shift_by: null` is semantics, not missing data

Five families (healing, horror, supernatural_everyday, gag, essay) have **no
status-quo-shift convention — the loop is the product**. For these:

- plan-level `first_major_shift` MUST be `null`;
- every arc's `status_quo_shift` MUST be `null` (cyclical arc segmentation);
- forcing a shift breaks the genre contract and FAILS the validator.

For non-null families, the plan declares `first_major_shift`
(`arc_id`/`episode`/`description`) with `episode <= first_major_shift_by`
(+25% tolerance), and the arc holding it carries a non-null `status_quo_shift`.

### 1b. Episode unit — mapping assumption is mandatory

Monthly-chapter print genres (fantasy, romance, school) carry systematically
lower arc episode-counts at equal story mass (40–60-page chapters) and are
**not 1:1 episode-comparable** with weekly units. Every plan declares
`episode_unit` (weekly_chapter / biweekly_chapter / monthly_chapter /
webtoon_episode / book_chapter / strip) and `episode_unit_mapping_note`
stating the assumption (e.g. "1 episode = 1 monthly 40–60p chapter;
arc_cadence counts are in this unit").

### 1c. Webtoon lane — study-sourced, no pacing-yaml row

`manga_pacing_by_genre.yaml` has **no webtoon family row** (Lane 03 named
follow-up); webtoon craft bibles exist but webtoon-format series must not
silently inherit print cadence. For `master_format: color_vertical_webtoon`
series: `cadence_source: study_webtoon`, arc grain **15–30 episodes**,
platform seasons are production units of **78–115+ episodes** (NOT ~25; NOT
story units) — all from
`artifacts/research/manga_arc_cadence_study_2026-07-24.md` §Webtoon lanes.
First 100 eps ≈ 4–6 arcs ≈ one platform season + opening of the second;
cliff-per-episode is near-mandatory. Do NOT edit the pacing yaml from this
lane to add the row.

### 1d. Horizon rule — 100 is the default, not a dogma

`episode_horizon` defaults to **100**. Families with **no 100-episode
long-runner evidence anywhere in the market corpus** (study confidence LOW:
`essay`, `memoir`, `graphic_medicine` — single/few-volume forms) MAY carry a
shorter horizon (48–60 recommended; validator allows 48–100) with a mandatory
`horizon_rationale` citing the study evidence line. Do not force 100 where the
market data does not support it.

## 2. Per-arc block

Every arc declares (schema `$defs/arc_block`):

| Field | Meaning |
|---|---|
| `arc_id`, `episode_start`, `episode_end` | Span; arcs tile 1..horizon, no gaps/overlaps |
| `detail_level` | `detailed` (carries per-episode plans) or `outline` (premise/promise level) |
| `arc_premise` | What the arc is about — an external situation, not a therapy summary |
| `arc_promise` | What the reader is promised the arc pays off |
| `status_quo_shift` | Durable change left behind; `null` in no-shift families (§1a) |
| `mc_change_vector` | `from_state` → `to_state` + `endurance_checklist_refs` anchors (`mc_endurance_study#<family>/<section>`; Lane 04 stable keys: `must_have` / `should_have` / `anti_patterns` / `endurance_mechanics`) |
| `self_help_topic` | From the brand's topic set (`self_help_topic_set`) |
| `mode_arc` | The arc-level mode treatment (§3) |
| `source_arc_ref` | Migration credit when upgraded from a 48-ep plan (§Migration) |

Lane 04's `config/manga/mc_endurance_checklists.yaml` was not yet on main when
this contract landed (`manga-mc-endurance-research-merged` pending, PR #325);
plans record `conformance.mc_endurance.status: pending_lane_04` until it
merges, then flip to `checked`. The anchor format above matches Lane 04's
committed `source:` convention, so no plan rework is needed at flip time.

## 3. Mode-arc — teacher XOR music XOR explicit none

One mode per series (`config/manga/manga_mode_vessels.yaml`; series_plan XOR
rule). Every arc's `mode_arc.mode` must equal the series `mode`:

- **teacher:** `vessel` (the genre-native vessel from
  `manga_mode_vessels.yaml` — tea-house hands, the mechanic, the Keeper…) +
  `arc_teaching_resolution` (what the teaching resolves to across the arc).
  The teacher is **NEVER named** in plan prose — `teacher_id` is metadata only;
  the validator runs the same teacher-name scan as
  `check_manga_story_authored`.
- **music:** `motif` (arc-level musical motif) + optional
  `opening` / `mid_recurrence` / `closing` beats per
  `docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md`. Requires `musician_id`, never
  `teacher_id` doctrine delivery.
- **none (regular):** explicit `mode: none` — self-help stays genre-native
  subtext with no mode vessel (the 48-ep program's stance).

## 4. Episode-plan pass (the operator's second pass)

Inside every `detail_level: detailed` arc, one entry per episode — this is the
input `story_architect` + the storyboarder consume:

| Field | Meaning |
|---|---|
| `episode` | Absolute episode number (plans must cover the arc span exactly) |
| `logline` | One sentence including an external force (arc-storyboard logline rule) |
| `genre_pleasure_beat` | The genre-native pleasure the episode delivers |
| `self_help_topic_beat` | How the topic advances as subtext through genre mechanics — never lecture |
| `hook` | `position` (cold_open / mid_episode / closing_panel / none) + `promise`; `none` is legal in cyclical genres (quiet-close convention) |
| `checklist_refs` | Anchors into genre/editor checklists (Lane 07) + `mc_endurance_study#…` |

Per Q-MPU-01 (flagship-first, ratified 2026-07-24): flagship en_US wave-1
series carry eps 1–48 as the near-term detailed window **seeded from the
existing 48-ep artifacts verbatim** — full per-episode plans where episodes are
actually authored (storyboards/scripts on main), block-level `outline` arcs
where the absorbed 48-ep plan is block-level (no invented per-episode detail;
that is the authoring wave's job) — and `outline` arcs for eps 49–100. Other
cells stay on the standing 48-ep cadence until wave 2.

## 5. Marketing/genre conformance self-check

Every master plan carries a filled `conformance` block — machine-checkable
fields, not prose vibes:

- `genre_contract`: `checked` + `craft_bible` path (bible §1 genre contract).
- `cadence_conformance`: `checked` + `family_range` + `arc_pattern` +
  `tolerance_pct` (validator recomputes; the block records the claim).
- `mc_endurance`: `status: checked | pending_lane_04` + `checklist` path +
  `family_key` (canonical genre id in `mc_endurance_checklists.yaml`).
- `mode_arc_coherence`: `checked` + `vessels_config` path.

## §Migration — how a 48-ep plan upgrades to a 100-ep master plan

1. **Eps 1–48 = existing arcs verbatim.** The 48-ep program's 4×12 plans
   (authored episodes, arc storyboards, chapter scripts) become the master
   plan's detailed window unchanged — re-expressed as master-plan arc blocks at
   the genre's cadence grain, each carrying `source_arc_ref` credit. Existing
   artifacts stay valid; **inventory EXTENDS, never REDUCED**.
2. **Eps 49–100 = outline-level** (Q-MPU-01 flagship-first ruling): arc blocks
   with premise/promise/shift/vector/topic/mode only; the episode-plan pass for
   them is authored when their wave activates.
3. **`migration` block:** `migrated_from_48ep: true`, `detailed_window_end: 48`,
   `source` credit. The validator requires `source_arc_ref` on every arc inside
   the migrated window.
4. **PR #295 absorb (Q-MPU-02 ruling: REWORK, never merge #295):** the 20
   structural arc-plan files from branch `claude/manga-12ep-arc-authoring-egnwqf`
   (`arc_plans/` 8 files + `arc_plans_all_genres/` 12 files) are preserved
   source-credited under
   `artifacts/manga/series_master_plans/rework_inputs_pr295/` (landed via Lane
   06's PR) as **rework inputs** for master-plan migration — flagship-first, the
   golden example below being the first. #295 itself is never merged and is
   closed by the dispatcher only after Lanes 05+06 signals exist.

## §US-illustrated addendum (Q-MPU-03 ruling: BOTH frames)

Evidence: `artifacts/research/us_illustrated_self_help_format_study_2026-07-24.md`
(merged 2a7a1b89a0, PR #320) + `config/manga/us_illustrated_pilot_cells.yaml`
(`provenance: RESEARCHED` per-cell `format_parameters` — reference the cell,
do not restate numbers).

**(a) BOOK frame — the commercially-evidenced primary.** `plan_frame:
book_format`. Plans carry **page-count + total-word-mass targets, NOT
chapter/episode counts inherited from manga** (micro/light word classes for 4
of 5 pilot cells; medium only for `cognitive_clarity`). Structure follows the
study's §2d class conventions via `book_format_params.structure_class`:
class-A gift books have **NO chapter contract** (4–8 loose movements — plan
them as page-flow beats via `movement_count`, never a forced `chapter_count`;
e.g. the `healing_ground` cell); classes C/E carry essay/principle counts.
`book_format_params.params_ref` points at the researched cell.

**(b) SERIAL frame — strip-cadence feeding a collection.** `plan_frame:
strip_serial`, `episode_unit: strip`. The Western wellness serial lives on
Instagram/Tumblr strips collecting into 112–144pp books (strip = atom,
collection = book) — **NOT webtoon-episode structure; no episode-framed
wellness comps exist** (study §6: Sarah's Scribbles, Deep Dark Fears, Worry
Lines lineage; WEBTOON Canvas wellness is hobbyist-scale only). Arcs in this
frame are thematic strip clusters sized toward the collection, and cadence
conformance against print-family episode ranges is intentionally not applied.

**Routing rule — the series_plan `format`/`master_format` field decides the
frame:**

| series_plan `master_format` (or `format`) | plan_frame |
|---|---|
| `color_vertical_webtoon` | `serialized_episode` + `cadence_source: study_webtoon` (§1c) |
| `bw_page_manga` / `color_page_manga` | `serialized_episode` + `cadence_source: pacing_yaml` |
| `direct_self_help_illustrated`, ships as a book | `book_format` (frame a) |
| `direct_self_help_illustrated`, ships as a series | `strip_serial` (frame b) |

## Artifact

```text
artifacts/manga/series_master_plans/<series_id>.master_plan.yaml
```

Golden example (EXECUTED-REAL, validator PASS):
`artifacts/manga/series_master_plans/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml`
— the en_US flagship with the deepest existing artifacts (12 authored episodes
with arc storyboards + chapter scripts + panel prompts on main), upgraded per
§Migration from PR #295's `en_US_iyashikei_batch_a.md` blocks. It exercises the
seasonal_cycle regime AND the null-shift branch (iyashikei → healing:
range [1,5], `first_major_shift_by: null`). Craft grade: **authored candidate**
at most; the contract itself is SPECCED + CODE-WIRED.

## Validator + gate

`scripts/ci/check_manga_series_master_plan.py` — schema + cross-ref checks +
cadence conformance + shift-null branch + stub-marker lint + teacher-name scan
(primitives reused from `check_manga_story_authored`) + mode XOR + episode-plan
coverage + migration credit. Wired as **ADVISORY gate 48** in
`scripts/run_production_readiness_gates.py` (display slots 1–47 in use;
promotion to required is gated on Lane 11 proving the loop — do NOT mark
required before that). Mutation-tested per `docs/agent_brief.txt` §14:
`tests/ci/test_manga_series_master_plan.py` (golden PASS + 4 mutation fixtures
FAIL: bad tiling, off-cadence, teacher named, stub markers).

## Acceptance language

| Claim | Allowed when |
|---|---|
| `authored_candidate` / `structurally_clear` | Plan exists; validator PASS |
| `system_working` | The full loop (master plan → arc pass → episodes → gates → storyboard → assembly) ran for this series (Lane 11) |
| `EXECUTED-REAL` | Byte-verified downstream artifacts exist for the planned episodes |
| `PROVEN-AT-BAR` / bestseller | Blind-judged sample only — never from this gate |
