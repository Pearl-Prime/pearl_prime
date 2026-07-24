---
name: manga-storyboarder
description: "Pearl manga arc-storyboard skill. Use for ANY task that plans or revises arc_storyboard_plan YAMLs: page maps, panel boards with story_move/visual_proof/information_delta, self-lint, bank-layer selection or bank-gap rows. Supersedes docs/agent_prompt_packs/manga_arc_storyboard_planner.md (kept with superseded-pointer). Thin binding to MANGA_ARC_STORYBOARD_CONTRACT + genre checklists + series bank contracts. Always use this skill instead of the old planner pack file."
---

# Manga Storyboarder — arc board + bank-layer pick (thin binding)

You plan each episode as a **storyboard that moves** before final dialogue or
visual dispatch. This skill **absorbs** the former agent pack
`docs/agent_prompt_packs/manga_arc_storyboard_planner.md` (superseded-pointer
header there; do not delete that file).

## Read first

1. `docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`
2. Schema: `schemas/manga/arc_storyboard_plan.schema.json`
3. Genre craft bible + `panel_grammar_items` from
   `config/manga/genre_craft_checklists.yaml`
4. Scene templates: `config/manga/genre_scene_templates/<genre>.yaml`
5. Strategy bank: `config/source_of_truth/manga_story_strategies/<genre>_strategies.yaml`
6. Interaction grammar: `config/manga/main_character_interaction_grammar.yaml`
7. Series bank contracts:
   `artifacts/manga/<series_id>/bank_contracts/*.yaml`
   (and demand rollup when present:
   `.../bank_contracts/series_demand_rollup.yaml`)
8. Excellence / modern-reader context:
   `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md`

## Sequence (mandatory)

1. **Genre contract** — required story functions → `genre_cadence` in order.
2. **Logline + stakes** — external force; `stakes_now` / `stakes_end`.
3. **Page map** — `page_turn_promises[].promise` per page.
4. **Panel board** — each panel: `story_move`, `visual_proof`, `information_delta`,
   plus `story_function` / `beat_role` / `action_intensity` when genre defines them.
5. **Bank-layer selection (Lane 08 extension)** — for each panel, select layers from
   the series bank contracts **or** emit a bank-gap row (feeds Lane 09
   `series_demand_rollup` / `--series-rollup`). Never invent REAL provenance for
   missing assets; gaps are honest INTERIM demand.
6. **Self-lint**
   - No >2 consecutive face-only `visual_proof`
   - No radio-only climax when genre requires battle/action
   - No therapy-caption episode peak
   - No deferred required story function
7. **Handoff to writer** — chapter script dialogue labels moves already on the board;
   set `arc_storyboard_ref` on the chapter script.
8. **CI**

```bash
PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \
  --arc-plan artifacts/manga/arc_storyboards/<series>/<ep>.arc_storyboard.yaml
```

Optional coverage / excellence after the writer lands dialogue:

```bash
PYTHONPATH=. python3 scripts/manga/plan_genre_scene_coverage.py \
  --genre <genre> --story artifacts/manga/chapter_scripts/<series>/<ep>.yaml
PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
  --story-handoff artifacts/manga/chapter_scripts/<series>/story_architecture_handoff.json \
  --chapter-script artifacts/manga/chapter_scripts/<series>/<ep>.yaml
```

## Output

`artifacts/manga/arc_storyboards/<series_id>/<chapter_id>.arc_storyboard.yaml`
— must validate against `arc_storyboard_plan.schema.json`.

Bank gaps: prefer the series' existing gap format consumed by
`phoenix_v4/manga/chapter/visual_from_script.py::build_assembly_layer_hints`
(e.g. under `assembly_manifests/` or rollup inputs). Do not invent a parallel
gap schema.

## Acceptance

- Plan + `check_manga_arc_storyboard` PASS = `authored_candidate` / `structurally_clear`
- Never claim bestseller / PROVEN-AT-BAR from planning alone
- GPU render is a separate authorized wave (RAP / M5)

## DO NOT

- Present single-shot text-to-image pages as layered panels.
- Label INTERIM layers as final art.
- Weaken the storyboard CI gate or skip self-lint.
- Write dialogue before the `story_move` board exists.
- Delete `manga_arc_storyboard_planner.md` — it keeps a superseded-pointer only.

## References

- `references/gate_commands.md`
- Superseded pack (pointer only): `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`
