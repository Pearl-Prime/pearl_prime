# Content Inventory Workstream — Implementation Spec

**Workstream:** `ws_content_inventory_20260407`  
**Owner:** Pearl_PM / Pearl_Dev  
**Status:** Active (scanner + portal + Phoenix Control; regenerate JSON after asset drops)  
**Canonical doc path:** `docs/CONTENT_INVENTORY_WORKSTREAM_SPEC.md`

---

## Problem

The catalog engine can generate large configured sets (see `artifacts/catalog/full_catalog.csv`). Operators need a single view of **what exists on disk** (books, manga, video, covers, audio, atoms) versus **metadata/config** rows, plus queued **missing** actions.

---

## Implementation

### 1. Scanner

**Path:** `scripts/inventory/scan_content_inventory.py`  

**Outputs:**

- `artifacts/inventory/content_inventory.json`
- `artifacts/inventory/content_inventory_summary.md`
- `brand-wizard-app/public/data/content_inventory.json` (Pages `fetch`)

**Summary object (contract):**

| Field | Meaning |
|-------|---------|
| `catalog_rows` | Rows in `full_catalog.csv` (minus header) |
| `total_configured` | Same as `catalog_rows` for the primary KPI |
| `total_built` | Rollup of built counts for deliverable types (excludes atoms) |
| `coverage_pct` | `100 * total_built / max(total_configured, 1)` rounded |
| `missing_count` | Length of `missing` array |
| `total_built_assets` | Includes atoms + all file categories (legacy rollup) |
| `by_type` | Per-type `configured`, `built`, `pct` |

**`by_type` keys:** `book_text`, `epub`, `cover`, `manga_cover`, `manga_panels`, `video_plan`, `video_rendered`, `audio_presenter`, `atoms_canonical`.

**Patterns (primary):**

| Type | Location | Pattern |
|------|----------|---------|
| book_text | `teacher_books/` | `*_book.txt` / teacher globs |
| epub | `artifacts/**/*.epub` | `*.epub` |
| cover | `brand-wizard-app/public/assets/covers/` | `cover_*.png` (fallback: any image in tree) |
| manga_cover | `.../manga_covers/` | `*_cover_*` in filename (fallback: images in tree) |
| manga_panels | `.../manga_panels/`, `artifacts/**/manga_book/`, `**/panels/` | `p*.png` preferred |
| video_plan | `artifacts/pipeline_examples/*/video_plan.json` | |
| video_youtube / tiktok | `artifacts/videos/youtube/`, `tiktok/` | `*.mp4`, `*.mov` |
| audio_presenter | `artifacts/audio/presenter/`, `public/.../audio/presenter/` | `*.mp3` |
| atoms | `atoms/**/CANONICAL.txt`, `SOURCE_OF_TRUTH/...` | |

**Arrays:** `teachers`, `missing` (full list, capped at 500), `missing_sample` (first 200), `commands`.

**Run:** `python3 scripts/inventory/scan_content_inventory.py`

---

### 2. Portal dashboard

**Path:** `brand-wizard-app/public/content_inventory.html`

- KPI row: **Total configured**, **Total built**, **Coverage %**, **Missing count** (plus scan date / teachers when present).
- Chart.js bar (% by type) and doughnut (built counts).
- Per-teacher table: compact **six columns** — Book, EPUB, Cover, Manga (cover or panels), Video (plan + any render), Audio — plus detailed columns optional in JSON only for tooling.
- Build command buttons (clipboard).
- **Sortable** missing table (client-side).

**Data:** `data/content_inventory.json`

---

### 3. Phoenix Control

**Path:** `PhoenixControl/Views/ContentInventoryView.swift`

- Tab: **Content inventory** (Core).
- Loads `artifacts/inventory/content_inventory.json`.
- **Scan repo** runs allowlisted `scripts/inventory/scan_content_inventory.py`.

---

### 4. Production plan

**Path:** `docs/CONTENT_PRODUCTION_PLAN_100PCT.md`

---

### 5. Coordination

Row in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for `ws_content_inventory_20260407`.

---

## Operations

```bash
python3 scripts/inventory/scan_content_inventory.py
```

Deploy static site per your usual `wrangler pages deploy` flow for `brand-wizard-app/public`.

---

## Translation coverage (reference)

See prior Pearl_Dev audits for `brand-wizard-app/public/assets/i18n.js`; inventory page is English-only unless i18n is extended.
