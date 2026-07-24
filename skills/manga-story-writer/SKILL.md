---
name: manga-story-writer
description: "Pearl manga episode authoring skill. Use for ANY task that authors or revises chapter_script_writer_handoff YAMLs for a manga series/episode: writing new episodes, repairing thin/stub scripts, iterating to excellence-gate PASS + story-authored PASS. Thin binding to story_architect + genre craft checklists + excellence gate — never a parallel craft doctrine. Tier-1 Claude for prose; Qwen only for CJK6 unattended lanes. Always use this skill instead of hand-editing scripts without the gate loop."
---

# Manga Story Writer — episode authoring (thin binding)

You author `chapter_script_writer_handoff` episodes for Pearl manga. You do **not**
invent a parallel story system. You bind to the canonical architect path, checklists,
and gates. Gate PASS = at most **authored candidate** / **structurally clear** — never
bestseller / PROVEN-AT-BAR.

## Read first (in order)

1. `docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md` — series plan must exist and gate-PASS.
2. `docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md` + the episode's
   `artifacts/manga/arc_storyboards/<series>/<ep>.arc_storyboard.yaml` — board before dialogue.
3. Genre craft bible + checklist (same genre, never restated here):
   - bible: `docs/research/manga_craft/<genre>.md` (via `config/manga/genre_craft_checklists.yaml` → `bible:`)
   - checklist: `config/manga/genre_craft_checklists.yaml` → `genres.<canonical_genre_id>`
   - MC endurance keys: `config/manga/mc_endurance_checklists.yaml` (referenced by checklist `mc_items`)
4. `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` — axes + Editor-pass contract
   (editor skill owns Stage B; you clear Stage A).
5. `phoenix_v4/manga/series/story_architect.py` — **only** architect path (RICH engine,
   vessels via `apply_mode_vessel`; teacher never named in panel text).
6. Operator doctrine: stories, not scenes — excellence-gate axes are the scoreboard.
7. Q-MPU-04: one writer skill for all genres; parameterize via checklist files — **not**
   25 genre agents.

## Contract

**Given:** `(series_id, episode_id range)`  
**Verify before writing:**

1. Master plan exists:
   `artifacts/manga/series_master_plans/<series_id>.master_plan.yaml`
2. Arc storyboard for each episode exists and CI-PASSes (storyboarder skill / planner).
3. Episode rows in the master plan cover the range (logline / genre-pleasure /
   self_help beat / hook) — extend the plan if missing; do not invent off-plan eps.

**Produce:** `artifacts/manga/chapter_scripts/<series_id>/<ep>.yaml` as
`chapter_script_writer_handoff` (schema
`schemas/manga/chapter_script_writer_handoff.schema.json`), with
`arc_storyboard_ref` set. Dialogue/captions **label** moves already on the board —
do not write dialogue before the board exists.

**Self-gate loop (mandatory):**

```bash
# Story-authored entry (listing-as-story kill)
PYTHONPATH=. python3 scripts/ci/check_manga_story_authored.py \
  --series <series_id> --episode <ep_id>

# Excellence realization (includes GATE_CRAFT / genre craft checklist)
PYTHONPATH=. python3 scripts/manga/validate_story_excellence.py \
  --story-handoff artifacts/manga/chapter_scripts/<series_id>/story_architecture_handoff.json \
  --chapter-script artifacts/manga/chapter_scripts/<series_id>/<ep_id>.yaml \
  --production
```

Iterate until both PASS (excellence ≥ 85 + all hard gates including
`MANGA.STORY.GENRE_CRAFT_CHECKLIST`). Then hand to **manga-editor** for Stage B
checklist read — do not claim SHIP yourself.

## Acceptance labels (honest)

| Outcome | Label |
|---|---|
| Gates PASS, editor not yet SHIP | `authored candidate` |
| Editor SHIP on record | still not bestseller — Layer 4 needs blind-10 |
| Blind-10 judged | only then discuss `PROVEN-AT-BAR` (M6 — out of scope here) |

## DO NOT

- Bypass `story_architect` / invent a second engine.
- Name the teacher in panel text or captions (hard gate).
- Weaken gates, skip GATE_CRAFT, or xfail failing fixtures to "land".
- Present single-shot text-to-image pages as layered assembly.
- Claim bestseller / shippable / production-ready without naming an acceptance layer
  (G-CLAIM / G-LAYER).
- Author CJK6 unattended prose with Claude when the lane is scheduled/unattended —
  that path is Qwen on Pearl Star; operator-present Tier-1 Claude is for this skill.

## References

- `references/gate_commands.md` — exact CLI copy-paste
- Genre parameterization: load checklist block for `genre_id` from the master plan /
  chapter script; never hard-code genre craft prose into this skill.
