# Lane 06 Handoff — Series Master Plan Contract (2026-07-24)

**Lane:** manga process uplift Lane 06 (Pearl_Architect spec + Pearl_Dev schema/validator)
**Status:** landed (see PR referenced in closeout)
**Signal:** `manga-series-master-plan-contract-merged=<merge SHA in closeout>`
**Gate consumed:** `manga-arc-cadence-research-merged=9446b3e74efc0607d77e5fddce21cf8213aa7f5f` (verified on origin/main before writes)

## What landed

1. **`docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md`** (v1.0) — the per-series
   100-episode planning layer ABOVE arc storyboards, BELOW the series_plan
   listing. Arc segmentation is genre-derived from the pacing yaml `arc_cadence`
   blocks (three segmentation regimes: escalating / fixed / seasonal_cycle —
   never a fixed 12); `first_major_shift_by: null` branches to cyclical
   segmentation (no forced shift); episode-unit mapping assumption is mandatory;
   webtoon cadence comes from the study (no yaml family row — deliberately not
   added here); horizon rule: 100 default, low-evidence families (essay /
   memoir / graphic_medicine) may carry 48–100 with cited rationale. §Migration
   (48-ep → 100-ep, EXTENDS never REDUCED) + §US-illustrated addendum
   (Q-MPU-03 BOTH frames, updated for the merged Lane 02 study: book frame is
   the evidenced primary with page/word-mass targets and class-A no-chapter
   structure; serial frame is strip-cadence → collected book, NOT
   webtoon-episode, study §6).
2. **`schemas/manga/series_master_plan.schema.json`** (1.0.0) — arc blocks
   (premise/promise/shift/MC-vector/topic/mode_arc), per-episode plan pass,
   conformance self-check block, `acceptance_layer` enum matching the
   arc-storyboard schema, teacher/music XOR conditionals.
3. **`scripts/ci/check_manga_series_master_plan.py`** — schema + alias-map
   genre resolution + 1..horizon tiling + cadence conformance (family range
   ±25%) + null-shift branch + mode XOR + episode-coverage + migration credit +
   stub-marker lint + teacher-name scan (primitives imported from
   `check_manga_story_authored`). Wired as **ADVISORY gate 48** in
   `scripts/run_production_readiness_gates.py` (47 was taken by the arc
   storyboard gate; display "46" is duplicated on main by two earlier gates —
   pre-existing collision, noted in-code, not renumbered).
4. **Golden example (EXECUTED-REAL, validator PASS):**
   `artifacts/manga/series_master_plans/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying.master_plan.yaml`
   — 25 seasonal cycles over 100 eps, 4 season wheels; eps 1–12 carry the full
   per-episode pass from the authored storyboards on main; eps 13–48 absorb
   PR #295's blocks verbatim at outline grain (source-credited); eps 49–100
   fresh outline. Craft grade: **authored candidate** at most.
5. **PR #295 absorb (Q-MPU-02):**
   `artifacts/manga/series_master_plans/rework_inputs_pr295/` — all 20 files
   from `claude/manga-12ep-arc-authoring-egnwqf` @ `4c6e2c3d59a9` preserved
   verbatim + README (source credit, consumption rules). #295 was NOT merged,
   NOT closed, NOT pushed to — the dispatcher closes it after Lanes 05+06
   signals exist.
6. **Tests:** `tests/ci/test_manga_series_master_plan.py` (16 tests: golden
   PASS ×2 + real artifact PASS + 4 mutation fixtures FAIL for the named
   reason + null-shift / shift-cap / fixed-12-rejection / mode-mismatch /
   episode-coverage / alias-resolution branches) with fixtures under
   `tests/fixtures/manga/series_master_plan/`. Mutation-tested per
   agent_brief §14. `tests/test_manga_schemas.py` gained the
   `series_master_plan` minimal-payload builder (without it the parametrized
   `test_minimal_instance_validates` KeyErrors on any new schema stem — the
   same trap that broke `arc_storyboard_plan` on main today; that pre-existing
   failure is NOT touched here, its fix lane is separate).

## Acceptance layers (honest)

- Contract + schema + validator: **SPECCED + CODE-WIRED** (advisory gate;
  promotion to required is gated on Lane 11 proving the loop).
- Golden example: **one EXECUTED-REAL migration** (its eps 1–12 have
  byte-real storyboards/scripts beneath); craft = authored candidate.
- Nothing here is system_working or PROVEN-AT-BAR.

## For consumers

- **Lane 09 (bank demand rollup):** the schema's arc/episode structure is the
  series-level demand source; consume `arcs[].episodes[]` + `season_wheels`.
- **Lane 11 (pilot):** pilot series should author a master plan first
  (validator PASS), then run arc pass → episodes → gates → storyboard →
  assembly. The stillness_press golden is a valid pilot candidate.
- **Lane 04 flip:** `conformance.mc_endurance.status: pending_lane_04` in
  existing plans flips to `checked` once
  `config/manga/mc_endurance_checklists.yaml` merges (PR #325 open at landing
  time). Anchor format `mc_endurance_study#<family>/<section>` already matches
  Lane 04's committed `source:` convention — no plan rework needed.
- **Lane 07:** `episodes[].checklist_refs` is the hook for machine-readable
  genre checklists; the validator does not yet enforce ref resolution
  (deliberate — Lane 07 owns checklist wiring).

## Known gaps / follow-ups (dispatcher to route)

1. **Webtoon family row still missing** in `manga_pacing_by_genre.yaml`
   (Lane 03 follow-up #1). The contract routes webtoon series to
   `cadence_source: study_webtoon` in the meantime; when the row lands, flip
   the contract's §1c and the validator's `WEBTOON_ARC_RANGE` to read the yaml.
2. **Registry rows REQUESTED (dispatcher owns the hot file):** add to
   `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`:
   - `manga_series_master_plan_contract` → `docs/specs/MANGA_SERIES_MASTER_PLAN_CONTRACT.md`
   - `manga_series_master_plan_schema` → `schemas/manga/series_master_plan.schema.json`
   - `manga_series_master_plan_gate` → `scripts/ci/check_manga_series_master_plan.py`
   (owner Pearl_Dev, subsystem manga_pipeline, edit_not_recreate YES, this PR as sha_or_pr.)
3. **story_architect consumption** is OUT of this lane's scope (no code
   changes to `phoenix_v4/manga/series/story_architect.py`): a follow-on
   should feed `arcs[].episodes[]` loglines into the architect's inputs
   (series/arc/genre/topic/mode/chapter all resolve today).
4. `tests/test_manga_schemas.py::test_minimal_instance_validates[arc_storyboard_plan]`
   is red on main from #319 (fix lane dispatched, not this PR).

## Cleanup ledger

- Scratchpad only: `<scratchpad>/lane06/` (staging tree, mirrored origin/main
  helper copies for local validation, temp index) — session-local,
  auto-cleaned; nothing written into the shared working tree.
- Shared checkout untouched (plumbing pattern off `origin/main^{tree}`;
  parked branch `agent/bestseller-atom-flow-lanes-20260721` never switched).
- `claude/manga-12ep-arc-authoring-egnwqf` fetched read-only (FETCH_HEAD);
  never checked out, pushed, merged, or closed.
- PR branch deleted on merge (see closeout).

## Verification receipts

- Validator: golden fixture PASS, real golden artifact PASS (25 arcs, family
  healing), default repo scan PASS; all 4 mutation fixtures exit 1 with the
  named reason.
- Tests: 16/16 pass in the staged environment (origin/main copies of
  `drift_detector_git.py` / `check_manga_story_authored.py` /
  pacing + vessels yamls).
- Schema: minimal builder payload + both goldens validate under
  `jsonschema.Draft202012Validator` (the same class
  `phoenix_v4/manga/models/validation.py` uses; no external $refs in this
  schema).
- Absorb integrity: 20/20 files byte-identical to
  `claude/manga-12ep-arc-authoring-egnwqf` @ `4c6e2c3d59a9` (copied via
  `git show`).
