# GHL Attach Wave 1 Summary

Date: 2026-07-14

Base: `origin/main` `20399837973bdc28d2fa8e650fe83d3c65841cb9`

Prerequisite signal: `waystream-epub-wave1=20399837973bdc28d2fa8e650fe83d3c65841cb9`

## Result

Attached two Wave 1 EPUBs to the existing Waystream delivery feed and uploaded both assets to R2.

| Book ID | Feed week | R2 key | Size | Feed URL |
| --- | --- | --- | ---: | --- |
| `way_stream_sanctuary__nyc_executives__anxiety__false_alarm` | `2026-W29` | `brand/way_stream_sanctuary/deliveries/2026-W29/amazon_kdp/way_stream_sanctuary__nyc_executives__anxiety__false_alarm.epub` | 45319 | `/download/way_stream_sanctuary__nyc_executives__anxiety__false_alarm?week=2026-W29` |
| `way_stream_sanctuary__nyc_executives__anxiety__watcher` | `2026-W29` | `brand/way_stream_sanctuary/deliveries/2026-W29/amazon_kdp/way_stream_sanctuary__nyc_executives__anxiety__watcher.epub` | 47187 | `/download/way_stream_sanctuary__nyc_executives__anxiety__watcher?week=2026-W29` |

## Evidence

- Dry-run attach proof: `artifacts/qa/ghl_attach_wave1_20260714/dry_run_attach.json`
- Live R2 HEAD verification: `artifacts/qa/ghl_attach_wave1_20260714/live_attach_evidence.json`
- Updated feed: `brand-wizard-app/public/brand_deliveries/way_stream_sanctuary.json`

## Validation

- Duplicate check before attach: zero feed matches and zero manifest matches for both book IDs.
- Feed delta: `791 -> 793` delivery entries.
- Proxy URL shape: PASS for both `/download/<book_id>?week=2026-W29` rows.
- R2 live upload verification: both `head_object` calls matched expected byte sizes and `application/epub+zip` content type.
- Secrets: no credentials, presigned URLs, or secret values were written to artifacts.

## Notes

`artifacts/waystream/` is locally ignored and not tracked on `origin/main`, so the durable PR evidence records the R2 keys, object sizes, hashes, and HEAD verification in this proof root rather than committing the local manifest file.
