# Handoff: cover-wiring-land (2026-07-23)

**Agent:** Pearl_Dev
**Lane:** cover-wiring-land
**Status:** see CLOSEOUT_RECEIPT in the executing session's final report / PR thread.

## What this lane did

Verified, fixed, and landed the one real Storyblocks-cover-wiring artifact:
an uncommitted `git format-patch` file at
`storyblocks_cover_wiring_20260723/storyblocks_cover_wiring_20260723.patch`
(falsely claimed by an operator-pasted closeout to already be commit
`053a6243ed` -- that SHA does not exist in this repo; see
`artifacts/qa/storyblocks_cover_wiring_20260723/SUMMARY.md` for full
correction). The patch adds a licensed-Storyblocks Stage-1 image-sourcing
path (`scripts/publish/bank_image_picker.py`,
`scripts/publish/five_layer_cover_orchestrator.py`,
`config/publishing/storyblocks_cover_topic_map.yaml`,
`scripts/ci/verify_cover_topic_imagery.py`) as an additive alternative to the
existing FLUX-based Stage 1, feeding the same canonical
`scripts/publish/render_kdp_cover.py` Stage-2 compositor (edited in place,
docstrings only, per PR #4269 ownership).

## Bug fixed pre-merge

`bank_image_picker.py::validate_candidate()` included `metadata.keywords` in
the positive-cue haystack, making the "descriptive metadata has a topic cue"
check vacuous whenever keywords mirrored topic_keys (the normal case). Fixed
by excluding `keywords` from that haystack -- strengthens the fail-closed
gate. Full detail in the SUMMARY.md above.

## Reconciliation logged: Q-COVER-SOURCE-01

Storyblocks Stage-1 sourcing is additive to the KDP ebook/print renderer; it
does not touch or collide with the separate audiobook 4-slot cover system
(`AUTHOR_COVER_ART_SPEC.md` / `author_cover_art_registry.yaml`). No existing
call site imports the new orchestrator yet, so nothing in production
switches sourcing as a result of this merge. Full finding in the SUMMARY.md.

## Proof root

`artifacts/qa/storyblocks_cover_wiring_20260723/` --
`SUMMARY.md` + `verify_cover_topic_imagery_output.txt`.

## Next action (handed to next lane / operator)

- Lane 02 (per the source prompt pack): build the actual licensed
  Storyblocks cover-surface inventory (`scripts/storyblocks` license index
  rows with `surface: cover`) so `verify_cover_topic_imagery.py` can go green
  for the 17 canonical topics. This lane's gate correctly reports 0/17
  covered today -- that is expected, not a regression.
- Lane 03 (per the source prompt pack, out of this lane's scope): decide
  whether/how to wire `five_layer_cover_orchestrator.py` into an actual
  production call site (e.g. Waystream/no-author-slot books) now that
  Q-COVER-SOURCE-01 has established it is safe to do so additively.
- The stray `storyblocks_cover_wiring_20260723/` directory at repo root
  (in the main checkout `/Users/ahjan/phoenix_omega`, not this worktree) was
  removed after its patch was applied and verified -- see CLOSEOUT_RECEIPT
  Cleanup Ledger.
