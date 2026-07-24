# Handoff — Manga Wave-2 Items 1/2/4 — 2026-07-22

Agent: Pearl_Dev. Lane: manga_wave2_items124_20260722.

## What landed

Branch `agent/manga-wave2-items124-20260722`, 3 narrowly-scoped commits off
`origin/main` @ `6f7320fc424b9393f2d4364d0bf485af5207545b`:

1. `1f2886ee` — Item 4: `phoenix_v4/manga/style_resolution.py` +
   3 CLI script `--style-id` default changes + 10 tests.
2. `73973b6e` — Item 1: 6 genre blocks in
   `config/manga/drawing_tradition_per_genre.yaml` + test fixes/additions.
3. `36884bc6` — Item 2: `scripts/pearl_star/worker/qwen_manga_worker.py`
   steps/negative/blob-gate sync + 9 tests.

Full detail, per-item acceptance verification, and the regression check
(pre-existing failures ruled out) are in
`artifacts/qa/manga_wave2_items124_closeout_2026-07-22.md` — read that first.

## Environment note for whoever picks this up

The shared working directory `/Users/ahjan/phoenix_omega` was 44 commits
behind `origin/main` and had heavy concurrent sibling-session lock
contention (`git worktree add` and a full-repo `git clone` both hung/timed
out repeatedly). Worked around this by cloning fresh into a scratch
directory with a **sparse checkout** (`git sparse-checkout set config/manga
phoenix_v4/manga scripts/manga scripts/pearl_star/worker
scripts/image_generation/comfyui_workflows tests/manga tests/pearl_star
tests/fixtures scripts/ci docs/specs artifacts/qa
artifacts/coordination/handoffs CLAUDE.md
docs/ROBUST_AGENT_PROTOCOL.md`), which avoided both the lock contention and
the multi-GB LFS checkout. If you need the full tree, expand the sparse-checkout
list or clone normally when the shared tree's lock contention clears.

`git push` from that scratch clone was slow (multiple 2-5 minute timeouts)
— network/remote-side latency, not a local blocker. If you hit the same
thing, retry with `run_in_background` rather than assuming failure.

## Still open / deliberately deferred

- **Item 2 live PNG smoke**: not attempted. Requires confirming ComfyUI +
  the Qwen model trio are actually on-box on `pearl_star`, then a
  queue-first `pscli` dispatch per RAP doctrine
  (`docs/ROBUST_AGENT_PROTOCOL.md`). This was explicitly out of scope for
  this lane (smallest-safe-batch ordering gated Item 2's live smoke on
  Items 1/4 landing clean first, and on pearl_star availability being
  confirmed — it was not, this session).
- **Item 4 teacher_archetype / profile_grammar layers**: both implemented
  as documented fail-open no-ops (no per-teacher style registry or
  per-format style_id field exists in the repo yet). Populate
  `TEACHER_STYLE_MAP` / add a `style_id` field to
  `format_adaptation_grammars.yaml` entries if/when those conventions are
  established — the resolver already wires the lookup.
- **The pre-existing "Core tests" CI break** (missing
  `config/manga/main_character_interaction_grammar.yaml`): NOT this lane's
  problem, NOT touched by these 3 commits. PRs #53/#55/#75 are racing to
  fix it independently — check their merge status before assuming this
  PR's CI failure (if any) is caused by this diff.

## Resume surface

`docs/specs/MANGA_DRAWING_TRADITION_WAVE2_REIMPLEMENTATION_SPEC_20260721.md`
(as of this session, this file exists only in the shared working tree's
local, unpushed commit `9db3b4f01d` on `agent/bestseller-atom-flow-lanes-20260721`
— it is not yet on `origin/main`. This closeout/handoff pair is
self-contained and does not require that spec commit to land for this PR to
be reviewed or merged.)
