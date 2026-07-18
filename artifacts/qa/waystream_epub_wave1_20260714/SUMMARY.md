# Waystream EPUB Wave 1 Summary

Date: 2026-07-14

Base: `origin/main` `5576257ebe33bbfa8180b858fcd4633e2562dda4`

Prerequisite signal: `thin-persona-four-cell-proof=5576257ebe33bbfa8180b858fcd4633e2562dda4`

## Result

Wave 1 shipped two new real Waystream EPUB artifacts from proof-approved tuples:

| Cell | EPUB | Bytes | Production gates | Stub scan |
| --- | --- | ---: | --- | --- |
| `nyc_executives / anxiety / false_alarm / F006` | `artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__nyc_executives__anxiety__false_alarm.epub` | 45319 | chapter_flow PASS; book_pass PASS; book_quality Pass; EI V2 PASS; register_gate WARN | PASS |
| `nyc_executives / anxiety / watcher / F006` | `artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__nyc_executives__anxiety__watcher.epub` | 47187 | chapter_flow PASS; book_pass PASS; book_quality Pass; EI V2 PASS; register_gate WARN | PASS |

`register_gate WARN` is recorded in the renderer summaries with `F13` counts and no hard gate failure. The current durable Waystream EPUB convention is coverless; `validate_epub.py` therefore reports `missing_cover`, matching existing shipped Waystream EPUBs.

## Attempted But Not Shipped

`educators / imposter_syndrome / false_alarm / F006` rendered text but failed production mode gates and was not packaged:

- failed gates: `chapter_flow`, `book_pass`, `book_quality_gate`
- evidence: `artifacts/qa/waystream_epub_wave1_20260714/logs/way_stream_sanctuary__educators__imposter_syndrome__false_alarm.pipeline.log`

## Evidence

- Output manifest: `artifacts/qa/waystream_epub_wave1_20260714/output_manifest.json`
- Render and packaging logs: `artifacts/qa/waystream_epub_wave1_20260714/logs/`
- EPUB structural validation snapshots: `artifacts/qa/waystream_epub_wave1_20260714/validation/`

## Non-Claims

- This is a two-EPUB micro-wave only, not catalog-scale readiness.
- No LLM prose generation was invoked at build time.
- Temporary render directories were used for build evidence and are not part of the committed durable output contract.
