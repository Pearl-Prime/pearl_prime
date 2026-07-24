# EXECUTE — Lane 10 — Wire arc_storyboard into the panel/assembly path

**AGENT:** Pearl_Dev · **SUBSYSTEM:** manga_pipeline · **WAVE:** 2

## GATE CHECK
Proceed when `manga-stranded-landed=<sha>` exists (Lane 01 — the storyboard CI gate + bubble-v2
wiring must be on main so you extend the merged state, not the stranded branch).

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; DISCOVERY REPORT; sibling-PR search "storyboard".
- Reuse-first: the consumption points EXIST — `phoenix_v4/manga/chapter/visual_from_script.py`
  (`compile_panel_prompts_from_chapter_script`) and `scripts/manga/assemble_from_bank.py`
  (manifest-driven). You are adding the storyboard as an INPUT to these, not building a new
  compositor. Discovery finding to honor: today NOTHING downstream consumes
  `arc_storyboard_plan.yaml` — it is planning-only; this lane closes that gap.
- Substrate: sparse-cone worktree for code+tests (poison protocol) or plumbing.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane10_2026-07-24.md`.
- PROVENANCE: research=`manga_composition_grammar_research_2026-07-07.md`; documents=
  `MANGA_ARC_STORYBOARD_CONTRACT.md`, `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §4/§10,
  `MANGA_COMPOSITION_GRAMMAR_SPEC.md`; builds_on=`visual_from_script`, `assemble_from_bank`,
  `panel_planning_rules`; inventory=EXTENDS (script-only path stays working — see DO NOT).

## READ FIRST
`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md` + `schemas/manga/arc_storyboard_plan.schema.json`,
`phoenix_v4/manga/chapter/visual_from_script.py`, `scripts/manga/run_chapter_visual.py`,
`scripts/manga/assemble_from_bank.py` (manifest schema + layer selection),
`scripts/manga/composition_grammar.py` (G1–G6), `scripts/manga/plan_panel_layout.py` +
`config/manga/page_grid_templates.yaml`, real arc storyboards under
`artifacts/manga/arc_storyboards/` (cognitive_clarity ep_001–012 ja_JP/zh_TW).

## MISSION
Make the storyboard the authority it was designed to be: page/panel decisions flow storyboard →
panel prompts → assembly manifest, instead of being re-derived from the chapter script.

1. **`visual_from_script.py`:** accept an optional `--arc-storyboard <path>`; when present, the
   storyboard's page map + per-panel `story_move`/`visual_proof`/`information_delta` +
   composition intents drive panel count, ordering, and per-panel prompt scaffolds (script text
   still supplies dialogue). Divergence rule: if the storyboard and script disagree on panel
   count for a beat, storyboard wins and a WARN row is emitted (panel descriptions > writer
   notes — OPD-154 precedent).
2. **Assembly manifest generation:** where a series has a bank contract, emit layer-selection
   hints per panel (storyboard's layer picks from the manga-storyboarder skill flow → manifest
   `layers[]` entries with provenance carried through). Missing layers → INTERIM placeholder rows
   flagged, never silently dropped; the demand-gap rows feed Lane 09's rollup format.
3. **Composition grammar stays gatekeeper:** storyboard-driven panels still pass G1–G6 in
   `assemble_from_bank.py` — add a test proving a storyboard-planned panel violating the
   crop×bg_class legality matrix FAILS assembly.
4. **Tests:** golden path (cognitive_clarity ep_001 storyboard + script → panel_prompts.json
   deterministic diff), divergence WARN test, grammar-violation FAIL test, and the no-storyboard
   legacy path byte-identical regression test (inventory EXTENDS proof).
5. **Doc:** §"Storyboard consumption" added to `MANGA_ARC_STORYBOARD_CONTRACT.md` (edit in
   place, version bump) documenting the flow + divergence rule.

Label honestly: CODE-WIRED with EXECUTED-REAL fixture runs; no GPU rendering in this lane.

## WRITE SCOPE
`phoenix_v4/manga/chapter/visual_from_script.py`, `scripts/manga/run_chapter_visual.py`,
`scripts/manga/assemble_from_bank.py` (manifest-hint ingestion only), tests, contract-doc
section, handoff. **OUT OF SCOPE:** render dispatch, bubble renderer, storyboard schema changes
(request via dispatcher if truly needed), skills.

## DO NOT
- The script-only path (no storyboard) must keep working byte-identically — regression-tested.
- Never present an INTERIM layer as final art; provenance labels flow through untouched.
- No new compositor, no single-shot page path.

## SIGNAL
`manga-storyboard-consumed=<full merge SHA>`
