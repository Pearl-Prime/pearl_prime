# Lane 01 — Real Vertical MP4s + Look-Approval-to-Golden (Pearl_Video, 2026-07-19)

This directory is the lane-01-specific proof root required by the prompt pack
(`docs/agent_prompt_packs/20260718_social_finish_mp4_evergreen/`). The actual
rendered assets and full look packet live under the rebuild proof root; this
file is the pointer index.

## Render-path decision

**Chosen: (a) fix local ffmpeg.** Host ffmpeg (`/opt/homebrew/bin/ffmpeg`) was
already fixed to 8.1.2 with `--enable-libass` before this session started (per
live discovery). Verified independently in this session: `ffmpeg -version`
succeeds, and a 3s smoke encode + the 3 pilot renders all completed cleanly.
No Remotion/RunComfy fallback was needed. $0 spend.

## What was rendered (pilot = full storyboard set; no scale set exists)

`shortform_publishable_storyboards.json` has exactly 3 entries. Pilot set ==
scale set. **SCALE=pilot-only** — nothing left unrendered.

| example_id | platform | topic | MP4 | dims | duration | validated |
|---|---|---|---|---|---|---|
| tt_anxiety_faceless | tiktok_reels_shorts | anxiety | [MP4](../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/tt_anxiety_faceless.mp4) | 1080x1920 | 10.77s | yes |
| tt_burnout_faceless | tiktok_reels_shorts | burnout | [MP4](../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/tt_burnout_faceless.mp4) | 1080x1920 | 10.77s | yes |
| yt_overthinking_faceless | youtube_shorts | overthinking | [MP4](../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/yt_overthinking_faceless.mp4) | 1080x1920 | 10.77s | yes |

Render mode: 5-frame slideshow concat (1.8s/frame + held last frame) built from
the approved storyboard stills. This is a validated v1 render, NOT yet the full
beat-driven motion/caption/sound Remotion cut described in the storyboards'
`beats[]` array. See LOOK_APPROVAL.md for the honest framing operators need.

## Pointers

- **Look packet (open this):** `../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md`
- **Rendered MP4s:** `../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/`
- **Validation receipts:** `../../social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_render_validation_receipts.jsonl`
- **Static winners (12) + carousel winners (3), unchanged from prior gate:**
  `../../social_visual_rebuild_publishable_quality_20260718/lane04_static_carousel_rebuild/static_carousel_render_samples/`
- **Dormant golden-freeze harness:**
  - Gate: `scripts/ci/check_social_visual_parity.py` (exit 0/SKIP today — verified)
  - Populate-only tool: `scripts/social/freeze_social_visual_golden.py` (refuses without `--confirm-operator-approved` — verified)
  - Empty golden dir + README: `artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/`

## Acceptance layer

**System working** (rendered + validated: plays, correct dims/duration,
first-frame matches approved storyboard). **NOT** "beautiful" or "shippable" —
that is the operator's Layer-4 look-approval read via `LOOK_APPROVAL.md`, not a
machine claim.

## Handoff

`artifacts/coordination/handoffs/social_mp4_render_2026-07-18.md`
