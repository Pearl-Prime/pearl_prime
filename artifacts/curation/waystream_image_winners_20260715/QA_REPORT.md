# Waystream Image Winners Draft QA - 2026-07-15

Lane: `waystream_image_curation_manifest_2026-07-15`  
Proof root: `artifacts/curation/waystream_image_winners_20260715/`  
Source bank: `artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x/`

## Status

- QA status: `DRAFT_MANIFEST_READY_FOR_SOURCE_PAGE_LICENSE_VERIFICATION`
- Candidate count: `36`
- Topics covered: `overthinking, boundaries, grief, loneliness, anxiety, hope`
- Production-ready count: `0`
- License status on every row: `pending_source_page_verification`
- Source-page verification performed in this lane: `no`
- R2 upload performed in this lane: `no`
- Renderer edits performed in this lane: `no`
- Image generation performed in this lane: `no`
- Raw asset moves/deletes/renames performed in this lane: `no`

## Smoke

Smoke selected two total candidates before expansion:

- `overthinking`: Pexels maze/labyrinth aerial candidate from `topics/overthinking.json` row 001.
- `boundaries`: Pexels gate/threshold candidate from `topics/boundaries.json` row 001.

JSON shape was validated against the required row fields before pilot expansion.

## Pilot

Pilot expanded to 12 candidates across all six requested topics, two per topic. QA notes confirmed the row contract, null pending fields, and crop-note object shape before scale expansion.

## Scale

Scale expanded to `36` candidates, `overthinking=6, boundaries=6, grief=6, loneliness=6, anxiety=6, hope=6`. This stays within the requested 24-36 range and keeps each topic at 4-6 candidates.

## Curation Rationale

- Provider preference: selected all-Pexels rows for the first draft because visual quality was sufficient and the provider class is simpler for the next verification lane than Openverse-derived metadata.
- Visual preference: symbolic, non-human, low-legal-risk metaphors: mazes, spiral stairs, gates, sand lines, empty rooms/chairs, empty benches/swings, lit windows, tangled wires, storm clouds, sunrise, lanterns, and seedlings.
- Legal posture: no row is production approved. Pexels license metadata is carried for review only; source pages must still be opened and snapshotted in the next lane.
- Sensitive-topic posture: all selected rows are intended as mental-health editorial metaphors only. Final use still needs human safety review for tone, implied diagnosis, and platform context.

## Topic Notes

- `overthinking`: strongest cover/social candidates are maze, clock, and spiral-stair abstractions. Avoided sticky-note/person rows and mirror/person rows.
- `boundaries`: gates, thresholds, locks, and sand-line textures selected. Avoided rows with readable warning signs, children, cultural/religious scenes, and Openverse diagrams.
- `grief`: empty bedrooms, empty chairs, and leaves selected. Avoided identifiable people, memorial/news context, screens, and classroom-like ambiguity.
- `loneliness`: empty bench/swing/window imagery selected. One-topic review remains important because loneliness imagery often drifts into recognizable people or despair-coded portraits.
- `anxiety`: tangled wire and storm abstractions selected. Avoided body-part wire images, chest-clutch imagery, panic faces, cliff-danger crops, and protest/crowd Openverse rows.
- `hope`: sunrise, lantern, and seedling imagery selected with muted-tone guidance. Avoided overly cheerful or person-centered rows.

## Validation

- Parsed source topic JSON for all requested topics.
- Confirmed every selected row has an existing local downloaded file.
- Wrote every required candidate field.
- Confirmed `license_verified_at`, `verified_by`, `source_snapshot_path`, `r2_key`, and `operator_approval_ref` are null for every row.
- Confirmed no candidate row has `license_status=verified`.
- Confirmed manifest JSON parses after write.

## Next Lane

Run source-page license verification for the `36` shortlisted rows. For each retained row, open the source page, capture a source snapshot, verify current license/provider terms, run face/logo/readable-text/property review, and only then consider raising `license_status` out of pending.
