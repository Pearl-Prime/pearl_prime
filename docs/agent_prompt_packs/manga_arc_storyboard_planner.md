> **SUPERSEDED (2026-07-24) — manga process uplift Lane 08.**
> Canonical skill: [`skills/manga-storyboarder/SKILL.md`](../../skills/manga-storyboarder/SKILL.md)
> (`manga-skills-registered` signal). Keep this file as a pointer + historical pack
> text; do **not** delete. New work uses the skill (board → bank-layer pick → CI).

---

# EXECUTE — Manga Arc Storyboard Planner (Tier-1)

AGENT: Pearl_Writer / Pearl_Research (operator-present)  
AUTHORITY: `docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`  
SCHEMA: `schemas/manga/arc_storyboard_plan.schema.json`  
CI: `scripts/ci/check_manga_arc_storyboard.py`  
OUTPUT: `artifacts/manga/arc_storyboards/<series_id>/<chapter_id>.arc_storyboard.yaml`

## Mission

Plan the episode as a **storyboard that moves**, before writing final dialogue or
dispatching visual. Every panel must change the world, the relationship, or the
reader’s information — pictures and words together carry the arc.

Do **not** invent a parallel story system. Reuse craft bibles, strategy banks,
scene templates, excellence gate, and beatsheet grammar.

## Inputs (read first)

1. Genre craft bible: `docs/research/manga_craft/<genre>.md` (cadence + failure modes)
2. Scene templates: `config/manga/genre_scene_templates/<genre>.yaml`
   → `story_scene_planning.required_story_functions_per_story`
3. Strategy bank: `config/source_of_truth/manga_story_strategies/<genre>_strategies.yaml`
4. Interaction grammar: `config/manga/main_character_interaction_grammar.yaml`
5. Beatsheet notes: `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md`
6. Excellence spec: `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md`

## Sequence (mandatory order)

1. **Genre contract** — list required story functions; copy into `genre_cadence` in order.
2. **Logline + stakes** — one sentence with **external force**; `stakes_now` / `stakes_end`.
3. **Page map** — for each page, write `page_turn_promises[].promise`
   (what the reader must wonder; show where they are going).
4. **Panel board** — one row per panel with:
   - `story_move` (world/relationship change — not “show face”)
   - `visual_proof` (what the picture proves that dialogue cannot)
   - `information_delta` (new reader knowledge)
   - `story_function` / `beat_role` / `action_intensity` when genre defines them
5. **Self-lint**
   - No >2 consecutive face-only `visual_proof`
   - No radio-only climax when genre requires battle/action
   - No therapy-caption episode peak
   - No deferred required story function (“save battle for later”)
6. **Only then** author `chapter_script_writer_handoff` dialogue/captions that
   **label** moves already visible on the board.
7. Set `arc_storyboard_ref` on the chapter script to the plan path.
8. Run:
   ```bash
   PYTHONPATH=scripts/ci:. python3 scripts/ci/check_manga_arc_storyboard.py \
     --arc-plan artifacts/manga/arc_storyboards/<series>/<ep>.arc_storyboard.yaml
   PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
     --chapter-script artifacts/manga/chapter_scripts/<series>/<ep>.yaml
   PYTHONPATH=. python3 scripts/manga/plan_genre_scene_coverage.py \
     --genre <genre> --story artifacts/manga/chapter_scripts/<series>/<ep>.yaml
   ```
9. Production visual/render only after excellence PASS + coverage PASS.

## Acceptance

- Plan + gates PASS = `authored_candidate` / `structurally_clear`
- Never claim `bestseller` / `PROVEN-AT-BAR` from planning alone
- GPU render is a separate authorized wave

## Anti-patterns (instant FAIL)

| Anti-pattern | Why |
|---|---|
| Standing/sitting + talk, no stakes change | Pictures mean nothing |
| Face CU montage while conflict is radio-only | Talking-head; arc stuck in channel |
| Therapy caption as climax | Genre-wrong landing |
| Required battle/launch deferred forever | Cadence broken |
| Writing dialogue before `story_move` board | Words paper over empty pictures |
