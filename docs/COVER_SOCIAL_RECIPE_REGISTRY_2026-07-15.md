# Cover/Social Visual Recipe Registry — 2026-07-15

Status: **NOT_PRODUCTION_APPROVED**. `PRODUCTION_READY_COUNT = 0`.

Lane 09 of `docs/agent_prompt_packs/20260715_finish_open_ops_bundle/`.
Implements the example/proof layer of
`docs/STOCK_AND_GENERATED_IMAGE_BANK_COVER_SOCIAL_PLAN_2026-07-15.md`.

This document is the human-readable face of
`config/publishing/waystream_cover_social_recipes.yaml`. The YAML is the SSOT;
this table is generated-by-hand commentary and must not be treated as the
machine contract.

## What shipped

| Piece | Path | Kind |
| --- | --- | --- |
| 12-topic recipe registry | `config/publishing/waystream_cover_social_recipes.yaml` | config (SSOT) |
| Image-aware placement engine | `scripts/publish/waystream_covers/image_placement.py` | code (additive) |
| Deterministic example builder | `scripts/publish/build_cover_social_examples.py` | code (non-production) |
| Tests | `tests/test_cover_social_recipes.py` | 20 tests |
| Examples + manifest | `artifacts/curation/waystream_image_winners_20260715/examples_v2/` | artifacts |

## Anti-reinvention: what was reused, not rebuilt

The repo already had most of this. This lane added the one missing step.

| Need | Existing thing reused | Where |
| --- | --- | --- |
| Busy-region detection | `BUSY_VARIANCE_THRESHOLD` / `BUSY_EDGE_THRESHOLD`, `_is_busy` | `waystream_covers/templates.py` |
| Thumbnail legibility rule | `THUMBNAIL_TEST_W`, `MIN_THUMB_CAP_PX`, `_thumb_cap_px` | `waystream_covers/templates.py` |
| Symbol vocabulary | `MOTIF_FN` (ring, ember, jagged, stem, …) | `waystream_covers/symbols.py` |
| Abstract background + fingerprint | `build_background()` | `scripts/publish/abstract_cover_art.py` |
| Zone/collision primitives | `Rect`, `find_clear_y`, `rects_collide` | `waystream_covers/layout_zones.py`, `layout_solver.py` |

**Added:** choosing *where the title goes based on the photograph underneath*.
The production renderer picks its zone plan from `book_id`, never from pixels.

The production cover path (`render.py`, `assign.py`, `templates.py`) is **not
modified**. `image_placement.py` is a new sibling module that no production
code imports. Thresholds are *imported* from `templates.py`, never restated, so
the proof layer cannot silently drift from the renderer — `tests/
test_cover_social_recipes.py::test_fast_busy_verdict_agrees_with_production_is_busy`
pins the two together.

## How placement works

1. Measure every candidate band on a 220px greyscale downsample:
   `variance` (tonal spread) and `edge` (mean gradient magnitude).
2. Score each band `variance/BUSY_VAR + edge/BUSY_EDGE`. Lowest wins — the
   title goes to the calmest real negative space.
3. Decide the treatment from what was measured:

| Measured band | Treatment | Rationale |
| --- | --- | --- |
| `var <= 405` and `edge <= 9.9` | `plain` | genuine negative space (sky, wall, bokeh) — set type directly |
| between quiet and busy | `scrim` | full-bleed gradient band holds contrast without hiding the photo |
| `var >= 900` or `edge >= 22` | `backing_box` | opaque inset card; nothing else survives a busy image |

4. Ink is chosen from measured luminance (dark ink on a bright quiet band);
   scrim/box impose their own dark ground, so cream always wins there.
5. Subtitle size is floored at the production thumbnail rule: it must still
   present `>= 11px` cap height at a 280px-wide thumbnail.

`prefer` only breaks ties within 12% — a recipe can nudge, but the image
decides. This is enforced by a test.

## The 12 topics

`plan_status` is inherited from the plan doc, not re-judged here.
`image` is what the example actually rendered on today.

| Topic | Title | Symbol | Plan status | Image source today | Cover treatment |
| --- | --- | --- | --- | --- | --- |
| anxiety | Untangle the Alarm | `link` | COVER_READY | curated (verified) | scrim |
| depression | The Grey Window | `bars` | SOCIAL_READY | abstract placeholder | plain |
| grief | The Room That Remains | `wane` | COVER_READY | curated (needs_owner_call) | plain |
| overthinking | Quiet the Loop | `loop` | COVER_READY | curated (verified) | **backing_box** |
| burnout | The Last Match | `ember` | RERUN_NEEDED | abstract placeholder | plain |
| self_worth | Worth Without Proof | `stem` | RERUN_NEEDED | abstract placeholder | plain |
| anger | The Signal Under the Heat | `jagged` | COVER_READY | abstract placeholder | plain |
| loneliness | When No One Checks In | `bars` | COVER_READY | curated (verified) | plain |
| healing | The Repaired Place | `rise` | SOCIAL_READY | abstract placeholder | plain |
| boundaries | The Line That Holds | `divider` | COVER_READY | curated (verified) | scrim |
| trauma | After the Weather | `jagged` | RERUN_NEEDED | abstract placeholder | plain |
| hope | The Next Small Light | `stem` | COVER_READY | curated (verified) | plain |

Only **6 of 12** topics have curated imagery (the curation lane covered
anxiety, boundaries, grief, loneliness, overthinking, hope). The other 6 render
on a deterministic abstract background. That is the honest state of the image
bank, not a defect of the builder.

## The two hard cases

The lane exists to prove these two, and both are exercised:

- **Busy image** — `overthinking`, an aerial hedge maze. Measured
  `var=740 edge=22.3` -> busy -> the engine placed the title in the calmest
  available band and gave it an opaque backing box. The title is legible over a
  maze with no natural negative space anywhere.
- **Negative-space image** — `hope`, a seedling against dark bokeh. Measured
  `var=250 edge=3.0` -> quiet -> plain type directly on the photograph, no
  backing, metaphor untouched.

## Platform formats

Pilot renders all five; scale renders the 4:5 feed card per topic.

| Format | Size | Source of sizing |
| --- | --- | --- |
| `instagram_feed_4x5` | 1080x1350 | plan doc (Meta 4:5 vertical feed) |
| `story_reel_short_9x16` | 1080x1920 | plan doc (TikTok/Reels/Shorts) |
| `pinterest_pin_2x3` | 1000x1500 | plan doc (Pinterest 2:3 standard) |
| `linkedin_landscape_1_91x1` | 1200x627 | plan doc (LinkedIn single image) |
| `square_1x1` | 1080x1080 | plan doc (square fallback) |

## Safety finding — the raw-bank fallback is opt-in and OFF

The first scale run used "first bank file in sorted order" for the 6 uncurated
topics. Sorted order is blind to image content, and it selected:

- `burnout` — a **recognizable face** at the crop edge beside **alcohol
  bottles** (face risk + substance imagery);
- `healing` — an **identifiable firefighter in a live wildfire/emergency
  scene** (face risk + emergency/news context);
- `depression` — a warm golden sunset, metaphor-inverted for "The Grey Window".

All three are excluded by the plan doc's legal/safety gates (§face/person
review, §sensitive-topic safety) **and** by these topics' own `avoid` lists.

The default fallback is therefore the abstract renderer, which is license-clean
and face/logo-free by construction. The raw bank is reachable only via
`--uncurated-bank`, and rows it produces are marked
`uncurated_bank_placeholder_UNREVIEWED_FACE_LOGO_RISK`.

**This is a curation finding, not a renderer bug.** An automated pick from an
unreviewed bank cannot satisfy the plan's gates; only human curation can.

## What would make this production

Nothing here is production. To graduate, per the plan doc:

1. Source-page license verification for every chosen asset (12 rows are
   `needs_owner_call`, 3 `rejected`, only 21 `verified` today).
2. Human visual shortlist + face/logo/trademark scan.
3. Sensitive-topic safety review, especially trauma/burnout/self_worth.
4. Curated imagery for the 6 abstract topics (the weak-topic rerun lane).
5. Operator look approval.
6. Only then: R2 upload of curated winners.

Until all six pass, `PRODUCTION_READY_COUNT` stays `0`.

## Reproduce

```bash
# the raw bank is local-only provenance and is NOT tracked in git
python3 scripts/publish/build_cover_social_examples.py --ramp smoke
python3 scripts/publish/build_cover_social_examples.py --ramp pilot
python3 scripts/publish/build_cover_social_examples.py --ramp scale
PYTHONPATH=. python3 -m pytest tests/test_cover_social_recipes.py -q
```

Deterministic: same registry + same source images -> byte-identical placement
decisions. No randomness, no clock, no network, no GPU, no paid API.
