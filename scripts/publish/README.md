# scripts/publish/ — operator publishing namespace

This is the operator-facing publishing command surface. Per the Phoenix Omega
100% production pathway doc
([`docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md`](../../docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md)),
publishing actions live here.

## Commands

### Build EPUBs

```bash
# Single book
python3 scripts/publish/build_epub.py \
    --input artifacts/pipeline_examples/<teacher>/book_<topic>_15min.txt \
    --title "<Title>" \
    --author "<Author>" \
    --cover artifacts/pipeline_examples/<teacher>/cover_<topic>.png \
    --output artifacts/epub/<slug>.epub

# Batch — all 13 teacher books
python3 scripts/publish/build_epub.py --batch

# Dry-run
python3 scripts/publish/build_epub.py --batch --dry-run

# Help (full flag list)
python3 scripts/publish/build_epub.py --help
```

### Validate EPUBs (KDP-readiness gate)

```bash
# Single file
python3 scripts/publish/validate_epub.py artifacts/epub/<slug>.epub

# Batch — all EPUBs in a directory
python3 scripts/publish/validate_epub.py --batch artifacts/epub/

# JSON output (for CI / automation)
python3 scripts/publish/validate_epub.py --json artifacts/epub/<slug>.epub
```

The validator checks STRUCTURE / METADATA / COVER / CHAPTERS / SIZE / WORDCOUNT
and optionally calls W3C/IDPF epubcheck if `EPUBCHECK_JAR` env var is set.
Exit code 1 = at least one ERROR (KDP would reject); 0 = all green or only
WARN-level findings.

### KDP submission (manga, today)

`kdp_comics_upload.py` exists for the manga-comics path. The book-EPUB
submission scaffold (D-1.3 in the pathway doc) is a future Session.

### WEBTOON canvas

`webtoon_canvas_upload.py` for the manga-on-WEBTOON path.

## Architecture

```
scripts/publish/                 ← operator-facing namespace
├── build_epub.py                ← thin wrapper, forwards to scripts/release/
├── validate_epub.py             ← KDP-readiness validator
├── kdp_comics_upload.py         ← manga KDP comics submission
├── webtoon_canvas_upload.py     ← WEBTOON Canvas submission
└── _policy_loader.py            ← shared policy helpers

scripts/release/                 ← backend implementation
└── build_epub.py                ← actual EPUB build logic (ebooklib-based)
```

The `build_epub.py` split is deliberate — the publish wrapper is the
operator-stable command surface; the release backend can be refactored
freely without breaking operator scripts. Direct calls to
`scripts/release/build_epub.py` still work and produce identical output.

## Recommended pre-submit flow

1. Build: `python3 scripts/publish/build_epub.py --batch`
2. Validate: `python3 scripts/publish/validate_epub.py --batch artifacts/epub/`
3. Fix any ERRORs (cover dimensions, metadata, etc.)
4. Re-validate
5. Submit to KDP (currently manual; D-1.3 will automate)

## Known issues (as of 2026-04-30)

The 13 EPUBs in `artifacts/epub/` use 1024×1024 square covers. KDP requires
≥1000×1600 portrait. All 13 fail the validator's `cover_below_kdp_min` check
and need cover regeneration before KDP submission. Tracked in
[`docs/campaign/SESSION_2_DISCOVERIES_2026-04-30.md`](../../docs/campaign/SESSION_2_DISCOVERIES_2026-04-30.md).
