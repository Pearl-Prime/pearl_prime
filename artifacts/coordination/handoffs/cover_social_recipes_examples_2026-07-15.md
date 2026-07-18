# Handoff — Lane 09 cover/social visual recipes + examples (2026-07-15)

Agent: Pearl_Design (Pearl_Marketing review hat)
Lane: `09_cover_social_recipes_examples`
Signal: `waystream-cover-social-recipes-examples`
Branch: `agent/cover-social-recipes-20260715` (based on `origin/main` `5472f4a5`)

## Status

**NOT_PRODUCTION_APPROVED. PRODUCTION_READY_COUNT = 0.**

12 topics covered. 24 examples byte-verified on disk (12 covers + 12 social
4:5 feed cards), plus 2 contact sheets and 1 manifest = 27 files.

## BLOCKER — rendered images could not be pushed (LFS budget exhausted)

`*.jpg` is LFS-tracked (`.gitattributes`). Pushing the 26 rendered examples
failed:

```
batch response: This repository exceeded its LFS budget.
The account responsible for the budget should increase it to restore access.
! [remote rejected] (pre-receive hook declined)
```

This is an **account billing limit**, not a repo/code problem, and it is
outside this lane's authority to change. Options considered and rejected:

- overriding `.gitattributes` to commit 26 JPEGs into git proper — smuggles
  ~9MB of binaries past the repo's deliberate LFS convention. Not done.

**What this PR therefore contains:** the registry, the placement engine, the
builder, the tests, the docs, and `examples_manifest.json` (JSON, not LFS —
it carries every placement decision, treatment, measured variance/edge, and
full source provenance, so the proof is reviewable as data).

**The 26 rendered images exist and are byte-verified locally** at
`/tmp/wt-covers/artifacts/curation/waystream_image_winners_20260715/examples_v2/`
and are archived to
`~/phoenix_workspace_archive/cover_social_examples_v2_20260715.tgz`.

Reproduce anywhere with the bank present:

```bash
python3 scripts/publish/build_cover_social_examples.py --ramp scale \
  --source-root /Users/ahjan/phoenix_omega
```

**Operator action needed:** raise the LFS budget, then re-push the images, or
accept the manifest + local archive as the proof of record.

## What landed

| Piece | Path |
| --- | --- |
| 12-topic recipe registry (SSOT) | `config/publishing/waystream_cover_social_recipes.yaml` |
| Image-aware placement engine | `scripts/publish/waystream_covers/image_placement.py` |
| Example builder (non-production) | `scripts/publish/build_cover_social_examples.py` |
| Tests (20) | `tests/test_cover_social_recipes.py` |
| Recipe table + doctrine | `docs/COVER_SOCIAL_RECIPE_REGISTRY_2026-07-15.md` |
| Examples + manifest | `artifacts/curation/waystream_image_winners_20260715/examples_v2/` |

## Anti-reinvention

The production cover path (`render.py`, `assign.py`, `templates.py`) is **not
modified**. Reused rather than rebuilt:

- busy-region thresholds + `_is_busy` (`templates.py`) — *imported*, not restated;
- thumbnail legibility rule `MIN_THUMB_CAP_PX` / `THUMBNAIL_TEST_W` (`templates.py`);
- motif vocabulary `MOTIF_FN` (`symbols.py`) — registry symbols are validated against it;
- `abstract_cover_art.build_background()` for topics with no curated imagery;
- `Rect` / zone primitives (`layout_zones.py`).

The single genuinely new thing is choosing the title band **from the pixels**.
The production renderer picks its zone plan from `book_id` and never looks at
the image. `test_fast_busy_verdict_agrees_with_production_is_busy` pins my fast
downsampled verdict to the production per-pixel verdict so the two cannot drift.

## Proof — the two hard cases

| Case | Topic | Measured | Verdict |
| --- | --- | --- | --- |
| Busy image | overthinking (aerial hedge maze) | `var=740 edge=22.3` | -> `backing_box`, title legible where no negative space exists |
| Negative space | hope (seedling, dark bokeh) | `var=250 edge=3.0` | -> `plain` type straight on the photo, metaphor untouched |
| Mid-busy | anxiety (tangled wire on concrete) | `var=145 edge=19.8` | -> `scrim`, type moved to y=0.70 away from the wire |

Treatment mix across 12 covers: `plain=9 scrim=2 backing_box=1`.
All 12 subtitles pass the thumbnail legibility rule.

## FINDING — raw-bank auto-pick is unsafe; now opt-in and OFF

The first scale run fell back to "first bank file in sorted order" for the 6
topics with no curated row. Sorted order is blind to content. It selected:

- **burnout** — recognizable face at the crop edge beside **alcohol bottles**;
- **healing** — **identifiable firefighter in a live wildfire/emergency scene**;
- **depression** — warm golden sunset, metaphor-inverted for "The Grey Window".

The first two are excluded by the plan doc's face/person and sensitive-topic
gates **and** by those topics' own `avoid` lists in the registry. They were
caught by looking at the rendered contact sheet, not by any gate.

Default fallback is now `abstract_cover_art.build_background()` — license-clean,
face/logo-free by construction. The raw bank is reachable only via
`--uncurated-bank` and its rows are marked
`uncurated_bank_placeholder_UNREVIEWED_FACE_LOGO_RISK`.

This is a **curation finding, not a renderer bug**: no automated pick from an
unreviewed bank can satisfy the plan's legal gates.

## Honest gaps

1. **Only 6 of 12 topics have curated imagery** (anxiety, boundaries, grief,
   loneliness, overthinking, hope). The other 6 render abstract. The weak-topic
   rerun lane (trauma, burnout, self_worth, depression, healing) is still open.
2. **License is not verified.** Of 36 curated rows: 21 `verified`,
   12 `needs_owner_call`, 3 `rejected`. `grief`'s top row is `needs_owner_call`
   and was still used — as a labeled example only.
3. **No operator look approval.** Nothing here has been through a look gate.
4. **The raw image bank is not tracked in git** (local-only provenance), so the
   builder needs `--source-root` pointing at a machine that has it. Without it
   the script reports the gap and exits non-zero rather than emitting stubs.
5. **Prior untracked sibling work exists** at
   `artifacts/curation/waystream_image_winners_20260715/examples/`
   (`build_deterministic_examples.py`, 6 topics, hardcoded top/bottom placement,
   no saliency). It is untracked in the shared tree and NOT committed here.
   Archived to `~/phoenix_workspace_archive/curation_examples_untracked_20260715.tgz`.
   `examples_v2/` supersedes it. Recommend deleting the old dir once reviewed.

## Next actions

1. Operator look-review of `examples_v2/contact_sheet_covers.jpg`. The
   curated-photo vs abstract-placeholder split is deliberately obvious.
2. Resolve the 12 `needs_owner_call` rows before any topic advances.
3. Run the weak-topic rerun lane to give the 6 abstract topics real imagery.
4. If/when the registry graduates, wire `image_placement` into the production
   cover path behind a flag — it is currently imported by nothing in production.

## Cleanup ledger

- Worktree `/tmp/wt-covers` — removed at close.
- Branch `agent/cover-social-recipes-20260715` — pushed, PR open, not merged.
- Generated images retained: 27 files under `examples_v2/` (bounded set: 12
  covers + 12 feed cards + 2 sheets + 1 manifest). Pilot-only platform renders
  (16 files across 5 formats) were regenerated and NOT retained, to keep the PR
  small — reproduce with `--ramp pilot`.
- Archive: `~/phoenix_workspace_archive/curation_examples_untracked_20260715.tgz` (37MB).
- No R2 upload. No image generation on Pearl Star / ComfyUI. No paid API.
