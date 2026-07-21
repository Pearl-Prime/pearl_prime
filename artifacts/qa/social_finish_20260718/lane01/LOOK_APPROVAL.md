# LOOK_APPROVAL — Social Visual Rebuild + Real Shortform MP4s (2026-07-19)

> This is a copy of the canonical packet at
> `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md`,
> placed here for the lane01 proof root. Paths below are repo-root-relative.

Status: **READY for operator look.** Not production-ready. Not live-scheduling
authorized. This packet supersedes the "MP4 status: render-ready / storyboard-only"
line in `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane06_operator_gate/OPERATOR_LOOK_GATE.md`
— host ffmpeg is now fixed (8.1.2 with libass) and the 3 pilot shortform items
have **real, validated MP4s**.

This document does not self-certify "beautiful" or "shippable." It is a checklist
for the operator's eye. Approve/reject per family below.

## What changed since the last look gate

- ffmpeg on this host was broken (missing `libass.9.dylib`); it is now fixed
  (`/opt/homebrew/bin/ffmpeg` 8.1.2, `--enable-libass`). Verified with a smoke
  encode to 1080x1920 before touching pilot assets.
- All 3 pilot shortform storyboards (`tt_anxiety_faceless`, `tt_burnout_faceless`,
  `yt_overthinking_faceless`) are now rendered as real MP4s, not just first-frame
  stills. See `shortform_mp4_rendered/`.
- Static (12) and carousel (3) winners are unchanged from the prior look gate —
  included here again as pointers so this is a single one-stop review packet.

## Open these first

### Shortform MP4s (NEW — real video, open and play each)

1. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/tt_anxiety_faceless.mp4` — TikTok/Reels/Shorts, anxiety, healthcare_staff persona
2. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/tt_burnout_faceless.mp4` — TikTok/Reels/Shorts, burnout, corporate_managers persona
3. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/yt_overthinking_faceless.mp4` — YouTube Shorts, overthinking, gen_z_students persona

Each MP4 today is a **first-frame-accurate 5-image slideshow** (1.8s/frame + held
last frame, ~10.8s, 1080x1920, 30fps) built from the approved storyboard stills —
it is NOT yet the full beat-driven motion/caption/sound edit described in
`shortform_publishable_storyboards.json` (`beats[]`: hook/recognition/mechanism/
practice/payoff with on-screen caption text, motion notes, and sound cues per beat,
totaling 27s). That fuller animated cut (captions burned in, motion/pan per beat,
sound design) is a follow-on Pearl Animator (Remotion) pass, not done in this lane.
Look at the slideshow MP4s for: does the object-metaphor image sequence read in
order, is there a jarring cut, is the still-frame-only pacing acceptable for a
first pass, or do you want to hold for the full beat-driven cut before any look
approval on shortform.

### Static + carousel winners (unchanged pointers, prior look-gate scope)

4. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane07_pilot_packet/pilot_contact_sheets/publishable_pilot_sheet.jpg` (all 18 examples, one sheet)
5. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane04_static_carousel_rebuild/contact_sheets/static_carousel_publishable_sheet.jpg` (12 static + 3 carousels)
6. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_first_frame_contact_sheet.jpg` (3 shortform first frames, for before/after comparison against the new MP4s)

### Validation receipts (machine-checked, not a look judgment)

7. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_render_validation_receipts.jsonl` — per-MP4: dims, fps, duration,
   sha256, full-decode-no-error, first-frame-vs-storyboard pixel diff
8. `artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane06_operator_gate/operator_look_scorecard.tsv` — prior automated pre-gate
   scores (min 87, 0 blocked) for all 18 pilot examples, shortform included

## Validation summary (machine-checked; does not replace your look)

| example_id | dims | fps | duration | plays (full decode) | first-frame match |
|---|---|---|---|---|---|
| tt_anxiety_faceless | 1080x1920 | 30 | 10.77s | yes | mean diff 2.35/255, 1.1% pixels >10 |
| tt_burnout_faceless | 1080x1920 | 30 | 10.77s | yes | mean diff 1.58/255, 2.0% pixels >10 |
| yt_overthinking_faceless | 1080x1920 | 30 | 10.77s | yes | mean diff 3.64/255, 8.3% pixels >10 |

All three decode end-to-end with `ffmpeg -f null -` and zero errors, and each
extracted first frame is within JPEG/h264 encode noise of the approved storyboard
`frame_01.jpg` (no wrong-asset or misordered-frame regressions).

## Approve if (per family)

**Shortform MP4 (faceless_video_broll):**
- The 5-frame slideshow sequence for each topic reads in the intended order
  (context → mechanism → practice framing) and no frame is duplicated/missing
- 1080x1920 vertical fills the frame correctly on a phone-width preview, no
  letterboxing artifacts from the pad/scale filter
- Acceptable as a v1 first-pass MP4, OR you want to hold for the full beat/
  caption/sound Remotion cut before any shortform look approval

**Static + carousel (unchanged from prior gate):**
- Object-metaphor labels match the photo (maze↔overthinking, lantern path↔hope, cord↔anxiety)
- No text overflow into metaphor focal points; landscape Bluesky keeps a protected text panel
- No repeated-background spam across the 12 static examples
- Carousel rhythm is cover → pattern → mechanism → practice → payoff → save

## Reject / send back if

- Any shortform MP4 shows a wrong, missing, or reordered frame vs. the storyboard
- Slideshow pacing is unacceptable for publish even as a v1 (then: request the
  full beat-driven Remotion cut before re-review)
- Any "Visual metaphor:" label mismatches the selected bank image (static/carousel)
- Colliding labels, unreadable type, or same crop reused as the dominant look
- Any row labeled production-ready or scheduled without a separate authorization lane

## Operator decision (fill in)

- [ ] APPROVE shortform MP4s as-is (v1 slideshow) → triggers golden freeze (see below)
- [ ] APPROVE static + carousel (unchanged) → triggers golden freeze (see below)
- [ ] HOLD shortform — request full beat-driven Remotion cut first
- [ ] REVISE (list example_ids + reason)

## What happens on approval (golden freeze — staged, not fired)

A dormant parity gate is staged at `scripts/ci/check_social_visual_parity.py`
(mirrors `scripts/ci/check_pearl_news_sidebar_parity.py`) plus a populate-only tool
at `scripts/social/freeze_social_visual_golden.py`, plus an empty
`artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/` directory. **Nothing is frozen
yet.** Once you approve (any subset, or all), the operator (or an agent acting on
your explicit go-ahead) runs the freeze tool to populate the golden snapshot from
the approved files, and the parity gate flips from skip-if-missing to
defend-forever — the same capture-once pattern as the Pearl News sidebar gate.

Live publishing / Metricool scheduling remains a **separate authorized lane** and
is out of scope here regardless of look approval.
