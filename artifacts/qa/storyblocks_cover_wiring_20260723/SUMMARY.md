# Storyblocks Cover Wiring — Verification Summary (2026-07-23)

## Correction of the source closeout's false provenance claim

An operator-pasted closeout claimed two "delivered" commits — `053a6243ed`
and `5c5177c627` — plus a ZIP artifact. **Both claims are false and are
explicitly corrected here:**

- `git cat-file -t 053a6243ed` -> `fatal: Not a valid object name 053a6243ed`
- `git cat-file -t 5c5177c627` -> `fatal: Not a valid object name 5c5177c627`
- Re-verified live against `origin/main` at `0ce62bca0533e3b919f42a668456b60f8d6f716e`
  (moved from the router pass's `cdcdf5db58722396a479da01de26e095c4d9643f`); neither
  SHA resolves against the current tip either.
- No ZIP matching any claimed SHA-256 was found on disk.
- The only real artifact was one **uncommitted** `git format-patch` file at
  repo root: `storyblocks_cover_wiring_20260723/storyblocks_cover_wiring_20260723.patch`
  (455 lines, "From: Codex <codex@openai.com>", claiming to be commit `053a6243ed`
  -- a commit that does not exist in this repository's object database). It had
  never been applied or committed. Nothing in this repository's history
  corroborates the closeout's "delivered" framing; it is fabricated/unverifiable
  provenance and none of its specific numbers should be trusted going forward.

This lane treated the patch file strictly as an unapplied, unverified diff and
independently re-verified every claim in it before applying anything.

## What was verified

- `git fetch origin && git rev-parse origin/main` -> `0ce62bca0533e3b919f42a668456b60f8d6f716e`.
- `git apply --check` of the patch against a fresh `origin/main` checkout -> clean
  (10 files, 328 insertions / 8 deletions, matching the patch's own diffstat).
- Prerequisite imports: `scripts.storyblocks.consumer_guard.assert_storyblocks_licensed_for_consumer`,
  `scripts.storyblocks.license_store.{LicenseStore,LicenseRecord,DEFAULT_INDEX_PATH}` --
  all present with the expected surface.
- `config/catalog/catalog_generation_config.yaml` exists with both `locales:` and
  `topics:` top-level keys.
- `gh pr list --search "storyblocks"` / `--search "cover"` (live, both `--state all`) --
  no open PR duplicates this work (prior Storyblocks PRs #19/#30/#35/#45/#52 are
  merged and cover EULA/licensing/audio, not cover imagery).
- Read the full patch file directly (not from any prior summary) before applying.

## Bug found and fixed in the patch (pre-merge)

`scripts/publish/bank_image_picker.py`'s `validate_candidate()` included
`metadata.keywords` in the haystack used for the "descriptive metadata has a
topic-positive cue" check. Because the test fixtures (and, in production,
any honestly-tagged Storyblocks row) set `keywords` to mirror `topic_keys`,
this made the check vacuous: a candidate whose title/description had **no**
genuine relevance to the topic (e.g. description `"generic landscape"` for
topic `anxiety`) still passed, because `keywords=["anxiety"]` alone satisfied
the positive-cue match. This showed up as a real test failure
(`test_mismatch_or_unverified_fails_closed[anxiety-generic landscape-True-cover]`
did not raise). Fixed by excluding `keywords` from the haystack -- the
`topic_keys` exact-match check above it already covers mechanical tagging;
the positive-cue check now requires independent evidence from title/description/tags.
This **strengthens** the fail-closed gate; it does not weaken it. After the
fix, all 8 tests in the two new test files pass, plus the pre-existing
`tests/test_publish_render_kdp_cover.py` (25 tests) -- 33/33 total.

## Reconciliation finding -- Q-COVER-SOURCE-01

**Question:** do `bank_image_picker.py` / `five_layer_cover_orchestrator.py`
collide with the existing `config/authoring/author_cover_art_registry.yaml`
4-slot cover system, or are they additive?

**Finding:** these are **not the same surface**. Two independent, non-overlapping
systems already coexist under `COVER-REGISTRY-01` (ratified 2026-05-05,
`docs/PEARL_ARCHITECT_STATE.md`):

1. **Audiobook 4-slot system** (`docs/authoring/AUTHOR_COVER_ART_SPEC.md`,
   `config/authoring/author_cover_art_registry.yaml`) -- 2400x2400 square,
   4 FLUX base images generated once per pen-name author, `slot =
   SHA256(author_id+":"+book_id) % 4`, PIL composition only. No script named
   `generate_cover.py` was found in the repo, so this system's per-book
   generator itself appears to be SPECCED/CONFIG-EXISTS rather than fully
   CODE-WIRED -- a separate, pre-existing gap, not something this patch touches.
2. **KDP ebook/print cover renderer** (`scripts/publish/render_kdp_cover.py`,
   1600x2560, template-based, R5) -- the canonical render code per PR #4269
   (`docs/authoring/BOOK_COVER_UNIFIED_RESEARCH_2026-07-01.md`: "PR #4269 ...
   is the LIVE cover-render actor ... do not fork"). Its Stage-1 image source
   today is `scripts/publish/render_imagery_for_template.py` (FLUX), invoked
   directly by `scripts/publish/waystream_covers/pools.py` and
   `scripts/publish/brand_covers/pools.py` -- neither of which this patch
   touches or rewires.

The patch **extends #2 in place**: `bank_image_picker.py` +
`five_layer_cover_orchestrator.py` are a new, additive Stage-1 sourcing
strategy (licensed Storyblocks stills, fail-closed, no silent fallback) that
calls the existing `render_kdp_cover()` Stage-2 compositor unchanged. The only
edit to `render_kdp_cover.py` is docstring/comment text describing the new
Stage-1 option; it does not touch the wrap/font-shrink logic that
`BOOK_COVER_UNIFIED_RESEARCH` marks "owned by PR #4269 -- do not edit" (verified:
the diff touches only the module docstring, ~lines 1-17, and one parameter
docstring line, ~line 1063 -- no code in between). It does not touch
`config/authoring/author_cover_art_registry.yaml` or system #1 at all. No
existing call site (`waystream_covers/pools.py`, `brand_covers/pools.py`,
`render_imagery_for_template.py`) currently imports the new orchestrator, so
merging this does not switch any book's live cover sourcing -- it adds a new,
not-yet-invoked production path.

**Decision (in-envelope, logged per contract):** proceed as additive. Default:
audiobook/4-slot books keep the existing 4-slot system unchanged; the new
Storyblocks Stage-1 path is available to the existing KDP ebook/print renderer
as an alternative to FLUX, gated fail-closed on licensed inventory, and is not
wired into any production call site by this PR. Wiring an actual call site
(e.g. routing Waystream/no-author-slot topics through the new orchestrator by
default) is a follow-up, operator-tier product-scope decision, not made here.

## Tests / proofs

```
pytest tests/test_bank_image_picker_storyblocks.py tests/test_verify_cover_topic_imagery.py tests/test_publish_render_kdp_cover.py -x -q
33 passed in 96.28s
```

`python3 scripts/ci/verify_cover_topic_imagery.py` -> exit code 1 (non-zero),
output: `Storyblocks cover coverage: 0/17 topics; uncovered=[... all 17 canonical
topics ...]`. This is the **expected, correct** result -- there is no licensed
Storyblocks cover-surface license index committed yet (that inventory-build
work is Lane 02's job). Full output captured at
`artifacts/qa/storyblocks_cover_wiring_20260723/verify_cover_topic_imagery_output.txt`.

## Acceptance layer

This lands **CODE-WIRED** at most: the selection/orchestration code exists,
imports resolve, unit tests pass, and the coverage gate runs and correctly
fails closed. It is not EXECUTED-REAL (no real book cover has been produced
through this path) and not PROVEN-AT-BAR (no licensed inventory exists to
judge against). Do not report this as "covers shipped."
