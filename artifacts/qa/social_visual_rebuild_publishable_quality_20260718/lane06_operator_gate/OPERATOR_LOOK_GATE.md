# OPERATOR LOOK GATE — Social Visual Rebuild Final (2026-07-18)

Status: **READY for operator look** (not production-ready; not live-scheduling authorized)

Automated pre-gate: `PASS_DRAFT_OPERATOR_QA_READY`  
Scorecard: `operator_look_scorecard.tsv` — **18 rows**, **0 blocked**, **min score 87**  
MP4 status: **render-ready / storyboard-only** (host ffmpeg broken: missing `libass.9.dylib`)

## Open these first

1. `../lane07_pilot_packet/pilot_contact_sheets/publishable_pilot_sheet.jpg`
2. `../lane04_static_carousel_rebuild/contact_sheets/static_carousel_publishable_sheet.jpg` (all 3 carousels)
3. `../lane05_pearl_animator_rebuild/shortform_first_frame_contact_sheet.jpg`
4. Scorecard: `operator_look_scorecard.tsv`

## Approve if

- Object-metaphor labels match the photo (maze↔overthinking, lantern path↔hope, cord↔anxiety)
- No text overflow into metaphor focal points; landscape Bluesky keeps a protected text panel
- No repeated-background spam across the 12 static examples
- Carousel rhythm is cover → pattern → mechanism → practice → payoff → save
- Every example stays `production_ready=false` / operator QA required

## Reject / send back if

- Any "Visual metaphor:" label mismatches the selected bank image
- Colliding labels, unreadable type, or same crop reused as the dominant look
- Any row labeled production-ready or scheduled without a separate authorization lane
- Fake MP4 claims while ffmpeg remains broken on this host

## Human-eye findings (lane 04, ≤2 repair cycles)

| Finding | Disposition |
|---|---|
| Bluesky object metaphor said "tangled note" over a maze | **Repaired** — label co-locked to "a maze with one exit"; caption-aware asset pick |
| Hope object metaphor could pick seedling over lantern path | **Repaired** — `OBJECT_ASSET_HINTS` prefer lantern/path assets |
| Contact sheet truncated 3rd carousel (`carousel_paths[0:12]`) | **Repaired** — full static+carousel sheet (30 thumbs) |
| `fb_burnout_local_note` uses anxiety wire asset | **Residual** — curated bank has no `burnout` topic; fallback pool + lifestyle family |
| Shortform MP4s | **Residual / expected** — storyboard + frames only until ffmpeg/libass fixed |

## Operator decision (fill in)

- [ ] APPROVE packet for license gate next
- [ ] REVISE (list example_ids)
- [ ] HOLD

Live publishing / Metricool scheduling remains a **separate authorized lane**.
