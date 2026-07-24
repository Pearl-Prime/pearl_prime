# Manga Arc Storyboard Contract

Status: v1.0 SPECCED + CODE-WIRED (CI gate + proving-ground cell)  
Owner: Pearl Research / Manga Story Governance  
Created: 2026-07-20  
Schema: `schemas/manga/arc_storyboard_plan.schema.json`  
CI: `scripts/ci/check_manga_arc_storyboard.py`  
Planner pack: `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`

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
