# LOOK_APPROVAL — Research-Complete Faceless Shorts (2026-07-19)

Status: **READY for operator look.** Not production-ready. Not live-scheduling
authorized. Golden freeze stays dormant until you approve.

This supersedes the v1 slideshow MP4s in
`artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/shortform_mp4_rendered/`
for shortform craft judgment. Those remain the functional encode proof; **these**
are the research-complete cuts.

This document does not self-certify "beautiful" or "shippable."

## What changed vs v1 slideshow

| Axis | v1 slideshow (lane 01) | This cut (lane 03) |
|------|------------------------|--------------------|
| Duration | ~10.8s flat | **27s beat-timed** (1.5 / 4.5 / 7 / 9 / 5s) |
| Plates | Storyboard JPGs with director notes + `1/5` | **Clean Pexels plates** from stock bank |
| On-screen text | Caption + motion notes | **Viewer captions only** |
| Motion | Hard cuts | Ken Burns / pan / static per beat |
| Audio | None | Soft ambient bed (AAC) |
| Muted-first | N/A (broken as film) | Captions carry the story muted |

## Open and play these first

1. `shortform_mp4_research_complete/final/tt_anxiety_faceless.mp4`
2. `shortform_mp4_research_complete/final/tt_burnout_faceless.mp4`
3. `shortform_mp4_research_complete/final/yt_overthinking_faceless.mp4`

Also: `frame_checks/` stills at t≈0 / 8 / 20 if you want contact-sheet style skim.

## Machine gates (not a look judgment)

See `shortform_mp4_research_complete/validation_receipts.jsonl` — all 3:

- 1080×1920, ~27.0s, AAC audio, full decode OK
- viewer_captions_only=true, director_notes_on_plate=false

## Still honest gaps (do not hide)

- **License:** `pending_source_page_verification` on Pexels source pages — verify before any publish claim
- **SFX:** continuous soft bed only; per-beat hits/ticks from storyboard `sound` cues not yet layered
- **Platform CTA text:** same English captions across TT/Reels/Shorts (no platform-native CTA variant pass yet)
- **Remotion:** not used; dedicated ffmpeg beat assembler (`scripts/social/render_faceless_research_complete.py`) after VCE `run_render` zoompan+drawbox failed on ffmpeg 8.x

## Approve if

- Reads as a native short muted (hook → recognition → mechanism → practice → payoff)
- No production chrome on screen
- Motion feels intentional (not a slideshow)
- Soft audio doesn't fight the therapeutic tone
- Acceptable to freeze as shortform golden **for craft**, pending license verify for publish

## Reject / send back if

- Any director note / beat counter visible
- Timing feels wrong for a 27s teaching short
- Caption illegible on phone
- You want per-beat SFX / Remotion polish before look-approve
- Metaphor plate feels wrong for the topic

## Operator decision (fill in)

- [ ] APPROVE research-complete shortform → run `scripts/social/freeze_social_visual_golden.py --confirm-operator-approved` (shortform subset)
- [ ] HOLD — want per-beat SFX / platform CTA variants first
- [ ] REVISE (list example_ids + reason)

Live publishing / Metricool stays a **separate authorized lane**.
