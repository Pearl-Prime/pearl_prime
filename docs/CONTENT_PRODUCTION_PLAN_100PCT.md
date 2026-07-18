# Content production plan — toward full repo coverage (Pearl_PM)

This plan pairs with the **content inventory** system. Full contract: `docs/CONTENT_INVENTORY_WORKSTREAM_SPEC.md`.

- Scanner: `scripts/inventory/scan_content_inventory.py`
- Machine-readable output: `artifacts/inventory/content_inventory.json` (and `brand-wizard-app/public/data/content_inventory.json` for static hosting)
- Web UI: `brand-wizard-app/public/content_inventory.html`
- macOS UI: Phoenix Control → **Content inventory** (Core section)

## Definitions

- **Configured**: Rows in `artifacts/catalog/full_catalog.csv` (and similar planning artifacts) that describe planned SKUs or slots.
- **Built**: Files that exist on disk (teacher books, EPUBs, covers, manga assets, `video_plan.json`, rendered MP4/MOV, presenter MP3s, `CANONICAL.txt` atoms).

100% “repo content” is not the same as 100% of every catalog row filled; use phases below to define realistic targets per asset class.

## Phase 1 — Truthful inventory (continuous)

- Run the scanner on every release branch and after large asset drops.
- Commit updated `content_inventory.json` when portal numbers must match production (optional policy: CI check that JSON is fresh or warn).

## Phase 2 — Teacher core (books + packaging)

**Goal**: Each production teacher has at least one complete vertical: manuscript → EPUB → cover where the lane requires it.

- Fill gaps flagged in `missing_sample` for `book_text`.
- Align EPUB and KDP cover paths so per-teacher columns read “yes” in the inventory grid.

## Phase 3 — Video pipeline

**Goal**: For each teacher with a `video_plan.json`, produce YouTube and TikTok renders where planned.

- Dry run: `python3 scripts/video/render_videos.py --dry-run`
- Full run requires FFmpeg and assets referenced by plans.

## Phase 4 — Audio (presenter)

**Goal**: Narration MP3s for presenter segments you intend to ship (deck-by-deck is acceptable).

- Use `scripts/audio/generate_presenter_audio.py` (requires ElevenLabs or replacement TTS) after TTS-friendly copy is finalized.

## Phase 5 — Manga

**Goal**: Covers and panels where manga-forward lanes are in market scope; assemble webtoon/PDF where scripts exist.

- `python3 scripts/release/build_manga_webtoon.py` when panel assets are present.

## Phase 6 — Atoms and story pools

**Goal**: Raise `atoms_canonical` toward the configured target and close thin story pools flagged elsewhere (e.g. content coverage reports).

- Prefer batch writing campaigns and governance checks before expanding catalog rows.

## Phase 7 — Catalog expansion (optional, high scale)

**Goal**: Only after phases 2–6 are stable, increase `full_catalog.csv` footprint or promote additional STRONG/VIABLE configs with a weekly production cap.

- Pearl_PM gates volume by subsystem authority docs and CI simulation/story gates.

## Ownership

| Area            | Primary owner |
|-----------------|---------------|
| Inventory spec  | Pearl_PM      |
| Scanner + JSON  | Pearl_Dev     |
| Portal + charts | Pearl_Dev     |
| PhoenixControl  | Pearl_Dev     |
| Production queue| Pearl_PM      |

## References

- `artifacts/inventory/content_inventory_summary.md` — human-readable snapshot after each scan.
