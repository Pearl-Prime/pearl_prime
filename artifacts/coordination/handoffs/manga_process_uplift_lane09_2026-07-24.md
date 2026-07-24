# Lane 09 handoff — Image-bank demand rollup from series plans (2026-07-24)

**Lane:** 09 of `docs/agent_prompt_packs/20260724_manga_process_uplift/` · **Agent:** Pearl_Dev
**Signal:** `manga-bank-demand-rollup-merged=<merge SHA in closeout>`
**Acceptance label:** CODE-WIRED + one EXECUTED-REAL rollup (analysis only — no GPU render, no LoRA training).
**Gates consumed:** `manga-series-master-plan-contract-merged=1cbb40adf0094081adc38da6188041a3dc9f9fca`
(Lane 06 schema/golden re-verified on origin/main before writes);
`manga-storyboard-consumed=007a69d1…` (Lane 10 gap format reused, not reinvented).

## What landed

The operator ask — "when we plan 100 episodes, analyze them and know exactly what
to build for the image bank" — is now a runnable analysis pass.

1. **`scripts/manga/generate_bank_contracts_from_script.py`** — EXTENDED (not
   forked) with a `--series-rollup` mode. `series_demand_rollup(master_plan, repo_root)`
   reads a `series_master_plan` (Lane 06 schema) + the series' authored bank
   contracts + storyboards + on-disk `image_bank/` and emits
   `artifacts/<series>/bank_contracts/series_demand_rollup.yaml`. The original
   `--chapter-script` stub path is unchanged (regression-tested, byte-shape
   identical: `m5_prep:true`, `status:specced_awaiting_gpu`).
2. **`schemas/manga/series_demand_rollup.schema.json`** (1.0.0, Draft 2020-12) —
   validates the rollup: L0 backdrops / L2 poses / L3 objects, coverage summary,
   identity-lock plan, render-queue estimate, storyboard-gap rollup.
3. **`tests/manga/test_series_demand_rollup.py`** (13 tests) — golden fixture →
   rollup shape, schema validation, byte-real coverage (a 4-byte stub does NOT
   count as present; only ≥ MIN_BYTES), outline authoring-gap surfacing, a
   mutation test (an outline arc referencing a NEW backdrop `candidate__subway` +
   cast `priya` surfaces gap rows the control run does not have — the
   "unknown reference → FAIL row" guarantee), Lane 10 `panels_with_gaps`
   aggregation, chapter-stub regression, and a run against the real Lane 06 golden.
4. **EXECUTED-REAL artifact:**
   `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/bank_contracts/series_demand_rollup.yaml`
   — the real rollup for the Lane 06 golden series (100-ep horizon).

## What the rollup computes (and its honest limits)

- **Required render universe = the authored bank contracts** (scene/object/pose
  inventories). This is the deterministic "what to build" list: each L0 scene ×
  its light-rig variants, each L2 pose, each L3 object × its state variants.
- **Episode-touch counts** are a *prose-scan estimate* (master-plan arc/episode
  text + detailed-episode storyboard `visual_proof`) for prioritization only —
  NOT a hard contract (declared in `provenance.note`).
- **Confidence** per row: `authored` = backed by a contract row and/or a detailed
  (per-episode) arc; `outline` = only implied by outline-level arc prose beyond
  the detailed window — **candidate demand needing bank-contract authoring, not an
  asserted asset**. Outline-only backdrops/objects/cast the 100-ep plan implies
  but the contract does not yet cover are surfaced as `authoring_gap:true` rows
  from a documented seed vocab (`provenance.backdrop_seed_vocab` /
  `object_seed_vocab`).
- **"Present" = byte-real ≥ 50 KB**, reusing
  `scripts/ci/check_render_progress_bytes.py` `MIN_BYTES` + `_lfs_or_disk_bytes`
  (LFS-pointer-aware — the golden's PNGs are 132-byte pointers carrying real
  1.5 MB sizes; a naive `stat()` would have called every asset absent). Floor
  never weakened.
- **Storyboard gap rollup** aggregates Lane 10's `panels_with_gaps` shape across
  `assembly_manifests/*_bank_gaps.json` (reused, not a competing format). Real
  boards carry no `layer_picks[]` yet (waits on Lane 08), so today the golden's
  `ep_001_bank_gaps.json` aggregates to 0 panel gaps.
- **Identity-lock plan:** PuLID reference sheets required for ALL cast (V5
  PuLID-first); flagship LoRA read from `config/manga/canonical_brand_list.yaml`
  (tier) + `config/manga/brand_lora_plans.yaml` (rows) — never invented.
- **Render-queue estimate** reuses `manga_asset_estimator.py`'s per-panel economic
  constants (its `_estimate_brand` API is brand-plan-lane shaped, not per-asset,
  so it is cited as constants, not called — stated in `heuristic_source`).

## Golden-series findings (real numbers, EXECUTED-REAL)

- 100-ep horizon, 100 episodes tiled, detailed window ends at ep 12.
- L0 = 13 authored backdrops + 7 outline authoring-gap candidates (apartment,
  bar, breakroom, coffee, counter, cupboard, sill).
- L2 = 2 in-contract cast (mira_aoki 26 poses, dr_morimoto 3) + 3 outline cast
  with no pose inventory yet (devon, kenji, yara). (`mother` is a role, not a
  proper name — deliberately not rostered.)
- L3 = 6 authored objects + 3 outline candidates (door, lamp, wrist).
- **Coverage: 95 required renders, 6 byte-real present (2 Mira poses + cup×3 +
  kettle×1), 89-render gap → 6.3% covered.** Render-queue estimate: 89 assets,
  ~$1.07 GPU, ~$2223 human-labor-equivalent (planning heuristic, not a quote).
- Identity: `stillness_press` is tier `flagship`; `style_sp` brand LoRA planned;
  **no en_US protagonist_lora row exists** (existing rows are ja_JP
  `stillness_jp_01`) — flagged as a single series-level authoring gap naming the
  protagonist candidate `mira_aoki`. PuLID reference sheet present for mira_aoki
  only; gap for the other 4 cast.

## For consumers / follow-ups (dispatcher to route)

- **Bank-contract authoring wave (M5):** the 7 backdrop + 3 object + 3 cast
  `authoring_gap` rows are the concrete "extend the contract for the 100-ep
  horizon" backlog. The rollup is deterministic — re-run after each contract
  edit to watch the gap shrink.
- **Render lanes (M5, RAP/queue-first):** the `coverage_gap`/`by_class` numbers
  are the render queue. This lane does NOT dispatch renders.
- **Lane 08 (storyboarder):** once real boards carry `layer_picks[]`, the
  `storyboard_gap_rollup` will begin aggregating true per-panel gaps; no rollup
  code change needed — it already consumes the Lane 10 format.
- **Registry rows REQUESTED (dispatcher owns the hot
  `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`):**
  - `manga_series_demand_rollup_generator` → `scripts/manga/generate_bank_contracts_from_script.py` (EDIT of existing row: now dual-mode)
  - `manga_series_demand_rollup_schema` → `schemas/manga/series_demand_rollup.schema.json`
  (owner Pearl_Dev, subsystem manga_pipeline, edit_not_recreate YES, this PR as sha_or_pr.)

## CI / merge notes (honest)

- **Required checks** (parse-sweep + Verify governance) named and read at merge;
  see closeout for the live per-check status.
- **Data dictionary is dict-NEUTRAL:** my change adds no `check_*.py`, no
  workflow, no `KNOWN_WIRED`/schema-tracked row, and the extended generator's
  consumers are unchanged (tests are excluded). `build_data_dictionary.py --check`
  reports STALE *inside a sparse cone* only because `.github/workflows` (192 rows)
  and other cones are not materialized — a sparse false-stale (same class as the
  flagship-parity sparse false-FAIL). **Do NOT regenerate DATA_DICTIONARY.tsv in
  a sparse tree — it would destructively drop those 192 rows.** On a full checkout
  the committed TSV already matches a fresh build.
- **tests/manga baseline reds (pre-existing, NOT mine):** collection errors in
  `test_qwen_manga_worker_graph.py` and `test_story_excellence_gate.py`; Lane 10's
  `test_storyboard_consumption.py` and my `test_series_demand_rollup.py` both pass
  on a full checkout (16/16 and 13/13). Three storyboard-consumption "failures"
  seen mid-session were sparse-cone false-FAILs (missing cognitive_clarity
  fixtures) — they pass once the cone includes those fixtures.

## Cleanup ledger

- Sparse-cone worktree `<scratchpad>/wt-bank-demand` (branch
  `agent/manga-bank-demand-rollup-20260724` off origin/main) — removed after
  merge; `git worktree prune`. Poison protocol honored (sparse-checkout set, no
  `--no-checkout` phantom deletions; `git status` clean throughout).
- Shared checkout untouched (parked on `agent/bestseller-atom-flow-lanes-20260721`,
  never switched).
- Scratch input copies under `<scratchpad>/main_inputs/` — session-local,
  auto-cleaned.
- PR branch deleted on merge (see closeout).
