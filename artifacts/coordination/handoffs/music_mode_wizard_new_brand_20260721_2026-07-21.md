# Handoff — music_mode_wizard_new_brand_20260721

## Lane

Prompt 01 of `docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/`
(`01_Pearl_Dev_wizard_mints_real_brand.md`). Wave 1 of the music-mode
wizard→pipeline pack. Code diffs authored by a Cursor session (per operator's
Cursor-codes/Claude-writes-and-lands standing rule); reviewed, tested, and
landed by this Claude session.

## Status: MERGED

- Branch: `agent/music-mode-wizard-brand-lane01-20260721`
- PR: https://github.com/Pearl-Prime/pearl_prime/pull/10
- Merge SHA: `5c96342d944c00d89b4150ccab88a91955ce33df`
- Signal: `music-wizard-new-brand-wired=5c96342d944c00d89b4150ccab88a91955ce33df`

## What landed

- `brandMatch.js`: `matchBrand` branches on `state.mode === "music"` before any
  teacher/composite scoring — returns a synthesized `<handle>_music` brand_id
  (Q2 slug rule), never one of the frozen 37.
- `BrandWizard.jsx` + ja/tw/zh locale mirrors: `generateYAML` emits
  `mode: music`, `brand_id`, and a `musician_reflections:` block (8
  `SURVEY_TEMPLATE.yaml` blocks, reused verbatim, no invented fields) when
  `state.mode === "music"`. Non-music path untouched (early-return only).
- `music_survey_save_handler.py`: appends/updates a row in
  `config/music/music_brand_registry.yaml` via a comment-preserving line
  editor (never a bare overwrite), hard-rejects (400) a `brand_id` colliding
  with `config/manga/canonical_brand_list.yaml` (Path X stays frozen at 37),
  idempotent on re-save (updates in place, keeps original `created` date).
- `music_survey_routes.py`: wires the collision reject to the 400 response.
- Tests: `tests/brand_wizard/test_music_survey_{live_routing,save_handler}.py`
  extended — new brand_id, musician_reflections YAML block, registry append +
  idempotent re-save, and the collision 400 — all against tmp-path fixtures,
  never the real registry file.

## Landing notes

Landed from a plumbing commit (base = live `origin/main`) rather than the
operator's local dirty branch, because the working tree that held Cursor's
diff (`/Users/ahjan/phoenix_omega`, branch
`agent/bestseller-atom-flow-lanes-20260721`) had ~7,000 unrelated uncommitted
files from a different, unmerged lane. Extracted exactly this lane's 9 files
via `git hash-object` + a scratch index, verified the diff stat matched the
lane's own hot-file list exactly before committing.

## Evidence

- `python3 -m pytest tests/brand_wizard/ -q` → 23 passed
- `python3 -m pytest tests/catalog/test_music_mode_branch.py -q` → 8 passed (regression: no change to Path X catalog branch logic)
- `python3 scripts/ci/pr_governance_review.py` → APPROVED
- `push_guard.py` → OK
- CI: 11/12 checks green; "Core tests" red is a pre-existing break on
  `origin/main` unrelated to this PR (`tests/storyblocks/test_fill_social_bank.py`
  fails to import `scripts.storyblocks.api_client`, missing on `origin/main`
  itself — verified before merging on all 3 lane PRs; flag for the storyblocks
  lane owner).

## Cleanup ledger

- worktree: `/Users/ahjan/phoenix_omega_wt_music_lane01_20260721` — reused
  sequentially for lanes 01/02/04 (see their handoffs); removed after this
  handoff PR merges.
- local branch: deleted (squash-merged); reused worktree checked out lane 02
  next.
- remote branch: deleted (`--delete-branch` on merge).
- scratch files: none.
- background jobs: none held.

## Next action

Lane 05 (end-to-end smoke) — gated on 01, 02, 03, 04 all MERGED. All four are
now merged as of this handoff; lane 05 starts next in this session.
