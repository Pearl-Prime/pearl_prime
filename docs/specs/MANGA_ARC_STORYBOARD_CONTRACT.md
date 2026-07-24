# Manga Arc Storyboard Contract

Status: v1.1 SPECCED + CODE-WIRED (CI gate + proving-ground cell + downstream consumption)  
Owner: Pearl Research / Manga Story Governance  
Created: 2026-07-20 · Updated: 2026-07-24 (v1.1 — §Storyboard consumption)  
Schema: `schemas/manga/arc_storyboard_plan.schema.json`  
CI: `scripts/ci/check_manga_arc_storyboard.py`  
Planner pack: `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`  
Consumers: `phoenix_v4/manga/chapter/visual_from_script.py`, `scripts/manga/run_chapter_visual.py`, `scripts/manga/assemble_from_bank.py`

## Purpose

Pictures and words must move the reader along an arc. A panel that only shows
someone standing or sitting while dialogue happens — with no change in the
world, relationship, or information the next panel depends on — is illegal for
production.

This contract is a **thin planning layer upstream of chapter prose and visual
production**. It does **not** replace genre craft bibles, strategy banks, scene
templates, excellence realization, or beatsheets. It requires those authorities
to be *realized as a board* before render.

## Formula

```text
genre cadence (required story functions)
  → page-turn promises (where the story is going)
  → per-panel story_move + visual_proof + information_delta
  → then dialogue/captions that LABEL the move already visible
  → excellence gate → scene coverage → panel prompts → render
```

## Non-Goals

- Do not invent a parallel story architect or LLM story generator.
- Do not force explosions on quiet genres. Low-arousal moves are valid
  (object change, spatial reveal, embodied decision) — **no-move talking** is not.
- Do not claim bestseller / PROVEN-AT-BAR from this gate alone.
  Gate PASS = at most `structurally_clear` / `authored_candidate`.

## Existing Authorities (reuse)

| Authority | Role |
|---|---|
| `docs/research/manga_craft/<genre>.md` | Cadence, failure modes, panel scaffolding |
| `config/manga/genre_scene_templates/<genre>.yaml` | `required_story_functions_per_story` |
| `docs/specs/MANGA_BEATSHEET_SCHEMA.yaml` | 1 beat = 1 panel; archetype leverage |
| `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` | Field grammar; talking-head pairing bans |
| `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` | Post-writer doctrine proof |
| `config/manga/main_character_interaction_grammar.yaml` | Interaction must be shown |
| `config/source_of_truth/manga_story_strategies/*_strategies.yaml` | Genre beat banks |

## Artifact

Path convention:

```text
artifacts/manga/arc_storyboards/<series_id>/<chapter_id>.arc_storyboard.yaml
```

Required episode fields: `logline`, `genre_cadence`, `stakes_now`, `stakes_end`,
`page_turn_promises`, `panels[]`, `acceptance_layer`.

Required per-panel fields:

| Field | Meaning |
|---|---|
| `story_move` | What changes in the **world or relationship** (not “show face”) |
| `visual_proof` | What the **picture** must prove that dialogue alone cannot |
| `information_delta` | What the reader knows after this panel that they did not before |

Optional craft binds: `story_function`, `beat_role`, `action_intensity`,
`archetype`, `scene_template_id`, `silence`, `forbidden[]`.

## Hard rules

1. **No empty move.** `story_move` and `visual_proof` must be non-empty (≥8 chars).
2. **Face-only + dialogue illegal.** A panel with dialogue (or caption) whose
   `visual_proof` is only face/reaction (`face_reaction_only` / talking-head
   markers) AND whose `story_move` is a no-op synonym (`none`, `n/a`,
   `stand around`, `sit and talk`, …) is a FAIL — except declared `silence: true`
   intensity-0 breaths that carry a real spatial/object/information delta.
3. **Talking-head density.** Consecutive panels with face-only `visual_proof`
   are capped at **2** (iyashikei anti-pattern mirrored for all genres).
4. **Genre cadence coverage.** Every entry in
   `config/manga/genre_scene_templates/<genre>.yaml` →
   `story_scene_planning.required_story_functions_per_story` (when present)
   must appear at least once in `genre_cadence` **or** as a panel
   `story_function`.
5. **Chapter link.** Production chapter scripts that declare
   `arc_storyboard_ref` must point at a valid plan; changed chapter scripts
   under `artifacts/manga/chapter_scripts/` that lack a sibling arc plan
   (or explicit `arc_storyboard_ref`) FAIL the CI gate when the genre has a
   scene-template file with required story functions.
6. **Excellence before visual.** Production chapter_runner already refuses
   visual without excellence PASS; arc plan is required **before** visual for
   the same production path (see `_require_arc_storyboard_for_visual`).

## Planner sequence (Tier-1 / operator-present)

See `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`.

1. Load genre craft bible cadence + scene-template required functions.
2. Fill `genre_cadence` slots **before** panel prose.
3. Write `page_turn_promises` (show destination → advance → cost).
4. Author one beatsheet row per panel with `story_move` + `visual_proof`.
5. Only then write dialogue/captions that label the visible move.
6. Self-lint: no radio-only climax; no therapy caption as episode peak;
   no deferred battle when genre requires `battle_action`.

## Pipeline position

```text
craft + strategy banks
  → ARC STORYBOARD PLAN (this contract)
  → beatsheet (optional / genre path)
  → chapter_script_writer_handoff
  → excellence realization gate
  → genre scene coverage
  → panel_prompts → V5 render → letter / PDF
```

## Storyboard consumption (v1.1 — the plan is an INPUT, not paperwork)

Before v1.1 nothing downstream consumed `arc_storyboard_plan.yaml` — it was
planning-only. The board is now a first-class input to the visual path:

```text
arc_storyboard_plan ──┐
                      ├─→ compile_panel_prompts_from_chapter_script(...,
chapter_script ───────┘        arc_storyboard=...)   [visual_from_script.py]
                                → panel_prompts.json  (storyboard_driven: true,
                                  per-panel storyboard{} block, WARN divergence rows)
arc_storyboard_plan.layer_picks
                                → build_assembly_layer_hints(...)
                                → assembly_layer_hints.json (manifest layers[] entries,
                                  INTERIM placeholders + demand-gap rows)
assembly manifest (storyboard / arc_storyboard_ref fields)
                                → assemble_from_bank.py (hint ingestion: validated,
                                  carried into gate report + provenance table;
                                  composition grammar G1–G6 still gate assembly)
```

### Rules

1. **Storyboard is the page/panel authority.** With
   `--arc-storyboard` (CLI `scripts/manga/run_chapter_visual.py`) or
   `arc_storyboard=` (library), the board's page map + panel order drive panel
   count and ordering; per-panel `visual_proof` leads the positive prompt as
   the scene beat, `story_move` / `information_delta` travel on the panel's
   `storyboard{}` block. The chapter script still supplies dialogue
   (`dialogue` or localized `dialogue_lines`).
2. **Divergence rule (OPD-154: panel descriptions > writer notes).** When the
   storyboard and script disagree on panel count for a page/beat, the
   storyboard wins and a WARN row is emitted into
   `storyboard_divergences[]` on the panel_prompts artifact
   (`page_panel_count_mismatch`, `script_panel_not_in_storyboard`,
   `storyboard_panel_missing_from_script`, `dialogue_disallowed_by_storyboard`).
   Nothing is silently dropped — every resolution is a named row.
3. **Layer picks → assembly hints.** Storyboard panels may carry
   `layer_picks[]` (`{layer_class, asset, provenance?, bbox_pct?, ...}` — legal
   via this schema's `additionalProperties`). `build_assembly_layer_hints`
   turns them into assembly-manifest `layers[]` entries with **provenance
   carried through** (a declared INTERIM is never upgraded to REAL). Picks
   whose asset is missing or below the 50 KB byte floor become **flagged
   INTERIM placeholder rows** plus demand-gap rows in the
   `panels_with_gaps` format the bank demand rollup consumes.
4. **Grammar stays gatekeeper.** A storyboard-planned manifest panel passes
   through composition grammar G1–G6 unchanged in `assemble_from_bank.py`;
   an illegal `crop_class × bg_class` combination FAILS assembly regardless
   of what the board planned (regression-tested). The manifest `storyboard{}`
   block (when present) must carry non-empty `story_move` + `visual_proof`
   (hard rule 1 above) and is carried into `gate_report.json` +
   `_provenance.json` for panel→plan traceability.
5. **Script-only path unchanged.** With no storyboard passed, the legacy path
   is byte-identical (regression-tested in
   `tests/manga/test_storyboard_consumption.py`).

Acceptance labeling for this wiring: CODE-WIRED with EXECUTED-REAL fixture
runs (cognitive_clarity ja_JP ep_001 board + script). No GPU rendering is
implied by this section; storyboard-driven prompts still claim at most
`structurally_clear` / `authored_candidate`.

## Acceptance language

| Claim | Allowed when |
|---|---|
| `authored_candidate` / `structurally_clear` | Plan + script exist; CI / excellence / coverage PASS |
| `EXECUTED-REAL` | Byte-verified panels on disk for **this** script |
| `PROVEN-AT-BAR` / bestseller | Blind-judged sample only — never from this gate |

## Proving ground

Mecha cell: `warrior_calm_cultivation__master_wu__en_US__burnout__the_chassis_is_listening`
true-mecha rewrite plan + chapter script. Soft iyashikei pilot + lettered TEST PDF
are **path proof only**, not story canon.
