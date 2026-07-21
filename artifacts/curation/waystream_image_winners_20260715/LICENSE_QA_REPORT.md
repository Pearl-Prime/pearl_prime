# Waystream Image License QA Report - 2026-07-15

Lane: `waystream_image_license_verification_2026-07-15`  
Proof root: `artifacts/curation/waystream_image_winners_20260715/`  
Ledger: `artifacts/curation/waystream_image_winners_20260715/license_verification_ledger.json`  
Production-ready count: `0`

## Status

- Candidate count reviewed: `36`
- Rows with `license_status=verified`: `21`
- Rows with `license_status=rejected`: `3`
- Rows with `license_status=needs_owner_call`: `12`
- Source provider mix: `Pexels=36`
- Source snapshots written: `36`
- Raw bank asset edits: `0`
- R2 uploads: `0`
- Renderer edits: `0`
- Operator look approval performed: `no`

## Smoke

Smoke checked one Pexels `overthinking` row and one Pexels `boundaries` row:

- `waystream_overthinking_pexels_10290189_01`: source page reachable by web-rendered page evidence; creator `Max Ravier`; page shows `Free to use`; Pexels license allows commercial use and modification without required attribution. Result: `verified`.
- `waystream_boundaries_pexels_36120859_01`: source page reachable by web-rendered page evidence; creator `Hassan Bouamoud`; page shows `Free to use`; no visible person/logo/property concern from source title/tags. Result: `verified`.

Smoke JSON validation passed with:

```bash
python3 -m json.tool artifacts/curation/waystream_image_winners_20260715/license_verification_ledger.json >/tmp/waystream_license_ledger_shape.json
```

## Pilot

Pilot reviewed two rows per topic before scaling. Pattern found:

- Pexels source pages generally expose creator, free-use status, title/subject, download surface, and license links.
- The global Pexels license allows free use, attribution optional, modification/cropping, promotional use, print materials/books, and social media use.
- The global Pexels restrictions still matter for final cover/ad use: identifiable people must not be shown in a bad/offensive light, endorsement must not be implied, unaltered physical resale and stock redistribution are disallowed, and trademark/service-mark use is disallowed.
- Local `curl` and `agent-browser` were blocked by Pexels/Cloudflare security verification, so snapshots are textual source-page evidence captures rather than raw HTML dumps.

## Scale Results

All 36 shortlisted rows were evaluated in the ledger. `production_ready_count` remains `0`.

Rejected rows:

- `waystream_boundaries_pexels_16055508_05`: exact Pexels source page was not confirmed; local/browser access hit Cloudflare and web search did not return the exact id.
- `waystream_grief_pexels_7303856_05`: exact Pexels source page was not confirmed; local/browser access hit Cloudflare and web search did not return the exact id.
- `waystream_grief_pexels_5429891_06`: exact Pexels source page was not confirmed; local/browser access hit Cloudflare and web search did not return the exact id.

Owner-call rows:

- `waystream_boundaries_pexels_10529669_02`
- `waystream_boundaries_pexels_35505659_03`
- `waystream_boundaries_pexels_31654445_04`
- `waystream_boundaries_pexels_982004_06`
- `waystream_grief_pexels_6634248_01`
- `waystream_grief_pexels_9775794_02`
- `waystream_grief_pexels_8251591_03`
- `waystream_grief_pexels_33312355_04`
- `waystream_loneliness_pexels_21044597_01`
- `waystream_loneliness_pexels_6120151_05`
- `waystream_loneliness_pexels_10659974_06`
- `waystream_hope_pexels_6864829_05`

Primary owner-call reasons are distinct private property/interior/venue context and one row with a visible single person in a mental-health loneliness use case.

## Next Gate

Proceed to operator look gate or crop/contact-sheet preview only for `license_status=verified` rows. Do not promote rejected or owner-call rows without replacement source-page evidence or explicit owner/legal decision.
