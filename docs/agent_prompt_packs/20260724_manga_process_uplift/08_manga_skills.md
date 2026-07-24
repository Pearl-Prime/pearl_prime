# EXECUTE — Lane 08 — Manga skills: editor / story-writer / storyboarder

**AGENT:** Pearl_Architect · **SUBSYSTEM:** manga_pipeline · **WAVE:** 2

## GATE CHECK
Proceed when `manga-genre-checklists-wired=<sha>` exists (the skills bind to the checklist file;
authoring them earlier hard-codes paths that don't exist yet).

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; DISCOVERY REPORT; sibling search for any manga skill landed since
  2026-07-24 inventory (there was none: `skills/` has zero manga entries).
- Reuse-first: skills are THIN BINDINGS to canonical artifacts — contract docs, schemas, gates,
  checklists. A skill that restates craft content (instead of pointing at the bible/checklist
  files) is drift; reject your own draft if it does. Existing agent file
  `docs/agent_prompt_packs/manga_arc_storyboard_planner.md` is ABSORBED by the storyboarder
  skill: the skill supersedes it — add a superseded-pointer header to the old file, don't delete.
- Substrate: plumbing pattern; explicit paths; staged-diff gate; preflight before push.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane08_2026-07-24.md`.
- PROVENANCE: research=(inherited via the artifacts bound); documents=the four contract specs
  named below; builds_on=`manga_arc_storyboard_planner.md`, excellence gate, checklists,
  master-plan contract; inventory=EXTENDS (old agent file superseded-with-pointer, not removed).

## READ FIRST
`skills/pearl-github/SKILL.md` (house skill format), `docs/agent_prompt_packs/manga_arc_storyboard_planner.md`,
`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`, `docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md`
(Lane 06), `docs/specs/MANGA_STORY_EXCELLENCE_REALIZATION_GATE_SPEC.md` (§Editor pass from Lane
07), `config/manga/genre_craft_checklists.yaml`, `scripts/ci/check_manga_story_authored.py`,
`phoenix_v4/manga/series/story_architect.py` (writer skill wraps this path, never bypasses it),
Q-MPU-04 ruling in INDEX (one skill per role, genre-parameterized — NOT 25 genre agents).

## MISSION
Create three repo skills under `skills/` (house format: SKILL.md + references/):

1. **`skills/manga-story-writer/`** — contract: given (series, episode range) → verify master
   plan + arc storyboard exist and are gate-PASS → author `chapter_script_writer_handoff` YAMLs
   via the story_architect path (RICH engine, vessels applied, teacher never named) → self-run
   `validate_story_excellence.py` + `check_manga_story_authored.py` → iterate to gate-PASS →
   label acceptance layer honestly (authored candidate). References: checklist file per genre,
   the operator's craft doctrine ("stories, not scenes" — cite excellence-gate axes), Tier-1
   prose policy (Claude writes; Qwen only for CJK6 unattended lanes).
2. **`skills/manga-editor/`** — contract: the §Editor pass — structured per-item checklist read
   of a script/arc/master-plan against `genre_craft_checklists.yaml` + `mc_endurance_checklists`,
   emitting the review artifact schema from the gate spec; APPROVE/REVISE verdict; revise loops
   back to the writer skill with named items. Also owns the arc-level review (master plan §
   conformance self-check verification) and the storyboard review (panel_grammar_items). The
   editor NEVER edits prose directly — it names failures against checklist keys.
3. **`skills/manga-storyboarder/`** — absorb `manga_arc_storyboard_planner.md`: same contract
   (page map → panel board with story_move/visual_proof/information_delta → self-lint) EXTENDED
   with bank-layer selection: for each panel, select layers from the series bank contract
   (`bank_contracts/*.yaml`) or emit a bank-gap row (feeds Lane 09's demand rollup). Output stays
   `arc_storyboard_plan.schema.json`-valid.

Each SKILL.md: trigger description, read-path, step contract, gate commands (exact CLI), honest
acceptance-layer labels, DO-NOTs (no single-shot pages presented as layered; no gate weakening;
INTERIM never presented as final art). Update `docs/DOCS_INDEX.md` skills row + registry rows via
dispatcher. Validate: run each skill's gate commands against the existing golden artifacts
(e.g. cognitive_clarity ep arcs) to prove the referenced commands actually execute.

## WRITE SCOPE
`skills/manga-story-writer/**`, `skills/manga-editor/**`, `skills/manga-storyboarder/**`,
superseded-pointer header on `manga_arc_storyboard_planner.md`, handoff.
**OUT OF SCOPE:** any pipeline code, configs, gates; `DOCS_INDEX.md`/registry (request via
dispatcher).

## SIGNAL
`manga-skills-registered=<full merge SHA>`
