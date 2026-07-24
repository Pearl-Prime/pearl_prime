# EXECUTE — Lane 09 — Image-bank demand rollup from series plans

**AGENT:** Pearl_Dev · **SUBSYSTEM:** manga_pipeline · **WAVE:** 2

## GATE CHECK
Start when Lane 06's PR exists (schema readable from the PR branch); FINALIZE only after
`manga-series-master-plan-contract-merged=<sha>` (re-pin your reader to the merged schema).

## EXECUTION CONTRACT (binding, in-band)
- EXECUTE end-to-end; terminal = signal token or ONE BLOCKER (evidence + pushed work +
  NEXT_ACTION). STARTUP_RECEIPT / CLOSEOUT_RECEIPT bracket the work.
- Re-verify premises live; DISCOVERY REPORT; sibling-PR search "bank contract"/"demand".
- Reuse-first: EXTEND `scripts/manga/generate_bank_contracts_from_script.py` (canonical,
  M5-prep) — per-episode today; you add the series-level rollup. Do NOT write a parallel
  generator. Bank-contract YAML shapes (`scene_inventory`, `object_inventory`,
  `character_pose_inventory`) are the existing convention — match them byte-for-byte in style.
- Substrate: sparse-cone worktree allowed for code+tests (poison protocol) or plumbing.
- Landing: MERGED (checks read + named) or BLOCKED. Cleanup ledger + handoff
  `artifacts/coordination/handoffs/manga_process_uplift_lane09_2026-07-24.md`.
- PROVENANCE: research=`MANGA_LAYER_RENDER_CONTRACT_SPEC` + V5 architecture; documents=
  `MANGA_SERIES_MASTER_PLAN_CONTRACT.md`; builds_on=`manga_bank_contract_generator`,
  `manga_asset_estimator.py`; inventory=EXTENDS.

## READ FIRST
`scripts/manga/generate_bank_contracts_from_script.py`, existing bank contracts
(`artifacts/manga/*/bank_contracts/*.yaml` — stillness, warrior_calm, cognitive_clarity),
`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` (L0–L4 taxonomy),
`docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (PuLID-first face lock; LoRA flagship-only),
`config/manga/brand_lora_plans.yaml` (plans-only status), `scripts/manga/manga_asset_estimator.py`,
`schemas/manga/series_master_plan.schema.json` (Lane 06).

## MISSION
The operator's ask: "when we plan 100 episodes, analyze them and know exactly what to build for
the image bank." Build the **series-level demand rollup**:

1. **Extend the generator** with a `--series-rollup` mode: input = a series master plan + all
   existing episode scripts/storyboards for that series; output =
   `artifacts/manga/<series>/bank_contracts/series_demand_rollup.yaml`:
   - union of required **L0 backdrops** (deduped by scene key; count of episodes touching each),
   - **L2 character poses** per cast member (pose key × emotion/outfit variants; consumes the
     pose-inventory convention),
   - **L3 objects** (recurring vs one-shot),
   - **coverage delta:** required vs present in the series' existing `image_bank/` (byte-real
     files only — a manifest row is not an asset; reuse `check_render_progress_bytes` byte-floor
     logic for "present"),
   - **identity-lock plan:** cast members needing PuLID reference sheets (all) vs flagship LoRA
     rows (only if the brand is on the flagship list — read brand_lora_plans, don't invent),
   - **render-queue estimate:** asset count × per-asset render class (reuse
     `manga_asset_estimator.py` heuristics if importable, else cite why not).
   For episodes that exist only at outline level (49–100), derive demand from arc-level scene
   fields and mark rows `confidence: outline`.
2. **Schema + tests:** `schemas/manga/series_demand_rollup.schema.json`; fixture series with
   known scripts → golden rollup; mutation fixture (script referencing an unknown pose) → FAIL
   row surfaces. `pytest` the manga suite for regressions (name pre-existing reds).
3. **Prove on one real series:** run against the Lane 06 golden master-plan series; commit the
   real rollup artifact. Label: CODE-WIRED + one EXECUTED-REAL rollup. The rollup is ANALYSIS —
   no GPU rendering in this lane (render dispatch stays RAP/queue-first in M5 lanes).

## WRITE SCOPE
`scripts/manga/generate_bank_contracts_from_script.py`, new schema, tests, one real
`series_demand_rollup.yaml`, handoff. **OUT OF SCOPE:** any rendering/GPU dispatch, LoRA
training, assemble_from_bank, master-plan schema itself.

## SIGNAL
`manga-bank-demand-rollup-merged=<full merge SHA>`
