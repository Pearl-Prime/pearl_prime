# Lane 10 handoff — storyboard consumption wiring (2026-07-24)

**Lane:** 10 of `docs/agent_prompt_packs/20260724_manga_process_uplift/` · **Agent:** Pearl_Dev
**Signal:** `manga-storyboard-consumed=<merge SHA>` (see PR)
**Acceptance label:** CODE-WIRED with EXECUTED-REAL fixture runs (no GPU rendering in this lane).

## What landed

The arc storyboard (`arc_storyboard_plan.yaml`) is now a consumed INPUT to the
visual path instead of planning-only paperwork:

1. **`phoenix_v4/manga/chapter/visual_from_script.py`**
   - `compile_panel_prompts_from_chapter_script(..., arc_storyboard=, arc_storyboard_ref=)`:
     storyboard page map + panel order drive panel count/ordering; per-panel
     `visual_proof` leads the positive prompt (scene-aware compiler);
     `story_move`/`information_delta`/composition intents ride a per-panel
     `storyboard{}` block; script supplies dialogue (`dialogue` or localized
     `dialogue_lines`).
   - Divergence rule (OPD-154): storyboard wins on panel count; WARN rows in
     `storyboard_divergences[]` (`page_panel_count_mismatch`,
     `script_panel_not_in_storyboard`, `storyboard_panel_missing_from_script`,
     `dialogue_disallowed_by_storyboard`). Nothing silently dropped.
   - `build_assembly_layer_hints(...)`: storyboard `layer_picks[]` → assembly
     manifest `layers[]` entries, provenance carried through (declared INTERIM
     never upgraded); missing/below-50KB assets → flagged INTERIM placeholder
     rows + demand-gap rows in the `panels_with_gaps` format
     (generate_assembly_manifest `bank_gaps.json` convention → Lane 09 rollup).
2. **`scripts/manga/run_chapter_visual.py`** — `--arc-storyboard` +
   `--assembly-hints-out`; YAML chapter scripts now loadable (real writer
   handoffs on disk are YAML); divergence WARN rows printed.
3. **`scripts/manga/assemble_from_bank.py`** — manifest-hint ingestion only:
   optional top-level `arc_storyboard_ref` + per-panel `storyboard{}` block
   validated (block requires non-empty `story_move`+`visual_proof` ≥8 chars —
   contract hard rule 1), carried into `gate_report.json` rows and the
   `_provenance.json` table. Composition grammar G1–G6 unchanged and still
   gates assembly.
4. **`schemas/manga/assembly_manifest.schema.json`** — additive optional
   fields for the two hint carriers above (schema is `additionalProperties:
   false`; without this, hint-carrying manifests would be schema-illegal).
5. **`docs/specs/MANGA_ARC_STORYBOARD_CONTRACT.md`** — v1.0 → v1.1, new
   §"Storyboard consumption" (flow + divergence rule + hints + grammar-stays-
   gatekeeper), edited in place.
6. **Scope add (dispatcher-authorized): `scripts/ci/check_no_legacy_bubble_render.py`**
   — was untracked-only in the shared checkout (referenced by the landed
   assemble_from_bank docstring, never committed). Landed as a **ratchet**:
   6 pre-v2 production callers grandfathered as WARN
   (`KNOWN_LEGACY_CALLERS`), any NEW legacy `bubble_render` import FAILs.
   Live via `tests/ci/test_no_legacy_bubble_render.py` (asserts zero new
   violations + ratchet-only-shrinks).
7. **Tests** — `tests/manga/test_storyboard_consumption.py` (16 tests):
   golden path on the REAL cognitive_clarity ja_JP ep_001 board + script
   (storyboard-ordered, deterministic byte-identical recompile), divergence
   WARN tests, grammar-violation FAIL test (bust × full_render G1 ILLEGAL
   fails assembly even when storyboard-planned) + legal-combo assembly PASS,
   legacy no-storyboard byte-identical regression (inventory EXTENDS proof),
   assembly-hints REAL/INTERIM/gap tests. Plus 5 fence tests.

## EXECUTED-REAL evidence

- `run_chapter_visual.py` on the real ja_JP ep_001 script + storyboard:
  16 panels, `storyboard_driven: true`, 0 divergences (board matches the
  shipped script, as its backfill notes claimed), 37,489-byte
  `panel_prompts.json` + `assembly_layer_hints.json` (0 picks — the real
  boards don't carry `layer_picks` yet; the manga-storyboarder skill flow is
  Lane 08's).
- New tests: 21/21 PASS. Adjacent regression suites
  (`test_manga_chapter_visual`, `test_render_routing_wiring`,
  `test_visual_from_script_scene_aware`, `test_genre_tradition_wiring`,
  `test_stillness_module_recovery`, `test_manga_m1_gates`): 52/52 PASS.

## Known gaps / follow-ups (Lane 12 + program)

- `config/manga/genre_scene_templates/mecha.yaml` untracked → gate 47's
  required-story-function check no-ops until a template lands (pre-existing,
  flagged by dispatcher — NOT this lane's).
- Two gates on main both numbered 46 in `run_production_readiness_gates.py`
  (pre-existing — Lane 12).
- 6 grandfathered legacy `bubble_render` callers need migration to v2
  (`KNOWN_LEGACY_CALLERS` in the fence script — shrink to zero).
- Real arc storyboards carry no `layer_picks[]` yet; hint emission is wired
  and tested but waits on the storyboarder skill flow (Lane 08) to author picks.
- Shared checkout has an untracked `tests/manga/test_arc_storyboard_gate.py`
  (gate #319 merged without its test); not in this lane's scope.
- `chapter_runner.py` production path does not yet pass `arc_storyboard=` to
  the compiler (it only *requires* the plan's existence pre-visual). Wiring the
  runner is a natural next step but was outside Lane 10's write scope.

## Cleanup ledger

- Worktree `/Users/ahjan/phoenix_omega/.worktrees/storyboard-consume-20260724`
  (sparse cone) — removed after merge.
- Scratch outputs under session scratchpad `lane10/` (panel_prompts +
  assembly_layer_hints from the EXECUTED-REAL run) — session-local, auto-cleaned.
- Shared checkout untouched (parked on `agent/bestseller-atom-flow-lanes-20260721`);
  the untracked `scripts/ci/check_no_legacy_bubble_render.py` original left in
  place (now superseded by the tracked, ratcheted version).
