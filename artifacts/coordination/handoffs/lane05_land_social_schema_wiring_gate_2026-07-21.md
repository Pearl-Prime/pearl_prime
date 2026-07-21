# Lane 05 handoff — social atom bank brand/author-vibe schema + wiring + anti-spam gate

**Status:** LANDED-OFFLINE (pushed to `pearlstar_offline`). GitHub push deliberately **not attempted**
per operator instruction ("don't do github yet. workaround for now") — do not push
`agent/social-schema-wiring-gate-20260721` to `origin` until told to.

## Corrected base branch (why this superseded the original plan)
Cursor drafted the 3 diffs (schema/registry, brand-author wiring, anti-spam gate) on
`agent/storyblocks-fill-social-bank-20260721` — an unrelated, already 231-file/38k-line-diverged
branch. Landing there would have bundled unrelated work and blown PR-size governance.

Worse: the canonical `phoenix_v4/social/deterministic_social.py` these diffs extend was **missing
from that branch's git history entirely** (`git cat-file -e` confirmed absent from both `origin/main`
and `agent/storyblocks-fill-social-bank-20260721`). The real canonical file (1,995 lines, commit
`3478f4077d3ea2e1850e6ea873cc3c11b86bf694`) only exists on `agent/media-bank-deterministic-assembly-20260719`
(a prior LANDED-OFFLINE lane from 2026-07-19).

**Fix applied:** rebased the diffs onto the correct base via a **plumbing commit** — a temp index
built from `agent/media-bank-deterministic-assembly-20260719^{tree}` (never a full working-tree
checkout; this repo is ~287k files and `git worktree add`/`checkout-index -a` both time out at
that scale — confirmed twice this session). New branch: `agent/social-schema-wiring-gate-20260721`.

## What landed
Commit `52ba6fb03a3742e6438d3ced9039c175cff511f6` on `agent/social-schema-wiring-gate-20260721`,
parent = `agent/media-bank-deterministic-assembly-20260719` (`66f264eed5`). Exactly 9 files,
1,244 insertions / 45 deletions (verified via `git diff --stat` against the parent — no leakage
from the storyblocks bundle):

- `docs/PEARL_SOCIAL_MEDIA_WRITER_AGENT_SPEC_2026-07-18.md` — § Brand/Author Vibe Extension addendum
- `docs/PEARL_ARCHITECT_STATE.md` — new cap `SOCIAL-ATOM-BANK-VIBE-01`
- `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` — new row `evergreen_social_atom_bank`
  (merged onto the **base branch's** version of the file, not the working tree's — those two
  versions had diverged by 12 lines; blind-copy would have dropped rows)
- `config/authoring/social_brand_author_voice_profiles.yaml` — brand voice catalog (real brands:
  Waystream Sanctuary, Stillness Press, Clear Seeing Books, Granite Ridge Publishing + `universal`)
- `phoenix_v4/social/deterministic_social.py` — brand/author kwargs threaded through
  generate_copy_package/select_visual/render_static_asset/build_carousel_package/select_beat_media;
  CLI `--brand-id`/`--author-id` in the file's own `main()` (confirmed base for this file was
  byte-identical to `3478f4077d`, so no drift to reconcile)
- `scripts/ci/check_social_post_variation.py` — deterministic rotation + anti-near-duplicate +
  cross-brand-distinctness gate
- `tests/test_deterministic_social_system.py` — 8 tests
- `artifacts/qa/social_atom_composition_pilot_20260721/` — fresh sample packet (posts.jsonl + README)

## Verification actually run (not copied from Cursor's report)
- `python3 -c "import json; ..."` on evergreen_en_us_atoms.jsonl → parses clean, **1,642 rows**
- `python3 -m pytest tests/test_deterministic_social_system.py -v` → **8/8 PASSED**, including
  `test_no_brand_args_copy_package_is_byte_identical_to_baseline` and
  `test_brand_voice_changes_cta_and_sign_off`
- `python3 scripts/ci/check_social_post_variation.py` → **PASS** (20 posts, 2 brands, 2 surfaces)
- `python3 scripts/ci/check_social_post_variation.py --inject-duplicates 3` → **FAIL, exit 1**, 6
  violations reported — mutation test proves the gate is real, not a rubber stamp
- `python3 scripts/ci/pr_governance_review.py` — run, but scoped to the ambient shared-tree diff
  (7,194 files, unrelated to this lane), not to the isolated 9-file commit; not informative for
  this specific change. The 9-file diff itself is small/single-subsystem and does not trip any of
  mass-deletion/PR-size/subsystem-scope by inspection.
- `PYTHONPATH=. python3 scripts/git/push_guard.py` — started, did not complete within session
  (backgrounded, no output before interruption); not a blocker given the manual scope verification
  above, but re-run it before this branch ever targets `origin`.

## Landing
- Branch `agent/social-schema-wiring-gate-20260721` pushed to `pearlstar_offline` (succeeded).
- One push attempt to `origin` was made **before** the operator said to hold off — it failed with
  `remote: fatal: did not receive expected object ... / error: remote unpack failed: index-pack
  failed` (an object-transfer error, not a 403 — GitHub was reachable). Root cause not
  investigated further per operator instruction to stand down on GitHub. **Do not retry origin
  push without operator go-ahead**; if/when retried, diagnose the missing-object error first
  (possibly an LFS pointer/object gap inherited from the base branch — check
  `GIT_LFS_SKIP_SMUDGE`/`git fsck` before pushing).
- Ledger row appended to `artifacts/coordination/pearlstar_offline/LEDGER.tsv` (`pushed` status) in
  a separate one-line commit `8c7f35cdffc741a7f730b86ea75b07eba8921af5` on the then-active shared
  branch `agent/bestseller-atom-flow-lanes-20260721`, also pushed to `pearlstar_offline`.

## Cleanup ledger
- worktree: attempted `git worktree add .../social-schema-wiring-gate-20260721` off the correct
  base — timed out (287k-file checkout) and left a half-populated, unregistered directory; removed
  (`rm -rf`, backgrounded to avoid a second timeout) and switched to the plumbing-commit approach
  instead. No worktree left behind for this lane.
- local branch: `agent/social-schema-wiring-gate-20260721` — kept (pushed to pearlstar_offline,
  not yet on origin).
- remote branch: `pearlstar_offline/agent/social-schema-wiring-gate-20260721` — pushed. `origin` —
  not pushed, on hold per operator.
- scratch files: `/tmp/registry_base.tsv`, `/tmp/registry_merged.tsv`, `/tmp/ledger_base.tsv`,
  `/tmp/social_landing_*.txt` — temp-index bookkeeping, safe to leave in `/tmp` or clean up, not
  part of the repo.
- rescue tarball: `~/phoenix_workspace_archive/social_schema_wiring_gate_rescue_20260721.tgz` —
  intentionally kept (safety copy of the original untracked Cursor diffs before the rescue).
- held artifacts: `artifacts/qa/social_atom_composition_pilot_20260721/` — intentionally kept
  (operator-review sample packet), landed in the commit, not scratch.

## Next action
Lane 03 (atom-authoring, `/Users/ahjan/phoenix_omega_worktrees/social-atom-scaleup-20260721` on
`agent/social-atom-scaleup-20260721`) should target **`agent/social-schema-wiring-gate-20260721`**
as its merge base going forward, not `origin/main` directly, since that's where the schema fields
it depends on actually live right now. When the operator clears GitHub again: (1) diagnose the
`index-pack failed` error before retrying the `origin` push, (2) open the PR from
`agent/social-schema-wiring-gate-20260721`, (3) re-run `push_guard.py` to completion first.
