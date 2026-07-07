# M6 — Comparator Scan Delivery Checklist

**Run ID:** `manga_blind10_2026-07-08`  
**Status:** 0/20 acquired · 2/2 P0 ready_to_acquire  
**Asset root:** `artifacts/qa/manga_blind10_2026-07-08/comparators/` (gitignored PDFs)

---

## P0 pilot — deliver first (blocks slot_01 judge packet)

| Step | comp_01_a (Yotsuba&!) | comp_01_b (Barakamon) |
|---|---|---|
| Purchase | Yen Press Vol 1 · ISBN 978-0-7595-0410-5 | Yen Press Vol 1 · ISBN 978-0-316-36217-6 |
| Excerpt pages | pp 5–8 (4 pages) | pp 6–10 (5 pages) |
| Output filename | `yotsuba_v1_ch1_pages_5-8.pdf` | `barakamon_v1_ch1_pages_6-10.pdf` |
| Min size | ≥ 500 KB | ≥ 500 KB |
| Max size | ≤ 15 MB | ≤ 15 MB |

### Scan spec (both)

1. Flatbed scanner **300 DPI minimum** (600 DPI preferred for halftone)
2. Crop to page bleed only — no scanner bed, fingers, or spine shadow on text
3. Export **PDF**, sRGB color space
4. Verify EN Yen Press edition page numbers (count from first story page if TOC differs)
5. Confirm no Phoenix watermarks or AI artifacts

---

## Per-file closeout (operator — repeat for each PDF)

```
[ ] PDF saved to comparators/<filename>.pdf
[ ] sha256sum comparators/<filename>.pdf  → record hash
[ ] COMPARATOR_REGISTRY.yaml → asset_status: ACQUIRED, sha256, acquired_date, source_isbn
[ ] SOURCING_TRACKER.yaml → increment comparators.acquired; flip slot status
[ ] Run validator (see below)
```

---

## Validation commands

```bash
cd /Users/ahjan/phoenix_omega

# P0 pilot gate (must exit 0 before judge packets)
python3 scripts/qa/validate_manga_blind10_comparators.py \
  --run-id manga_blind10_2026-07-08 \
  --require-p0

# JSON report for closeout receipt
python3 scripts/qa/validate_manga_blind10_comparators.py \
  --run-id manga_blind10_2026-07-08 \
  --require-p0 --json

# Single slot check
python3 scripts/qa/validate_manga_blind10_comparators.py --slot 01 --json
```

**Expected after P0 closeout:** `acquired: 2`, `pilot_ready: true`, `errors: 0`, exit code 0.

**Current state (2026-07-08):** `acquired: 0`, `pilot_ready: false`, 2 missing_p0 errors.

---

## Registry fields to update (per comparator)

In `COMPARATOR_REGISTRY.yaml`, for each acquired entry:

```yaml
asset_status: ACQUIRED
sha256: "<sha256sum output>"
acquired_date: "2026-07-XX"
source_isbn: "<ISBN-13>"
```

---

## Priority order after P0

| Priority | Slots | Comparators | When |
|---|---|---|---|
| P0 | 01 | Yotsuba&!, Barakamon | **Now** — blocks pilot |
| P1 | 02–04 | March, Mushishi, Gundam Origin, Planetes, Monster, 20th Century Boys | Order while M5 renders |
| P2 | 05–10 | Remaining 12 excerpts | Before full blind-10 (Aug 2026) |

Full title list: `COMPARATOR_ACQUISITION_CHECKLIST.md`

---

## Forbidden sources

- Phoenix internal renders
- AI-generated reference images
- Unlicensed aggregate / pirate sites

---

## Unblocks

| Milestone | Blocker cleared |
|---|---|
| P0 validated (2 PDFs) | M6-BLK-004 pilot subset |
| All 20 acquired | M6-BLK-004 full |

See `PILOT_SLOT_01_ACQUISITION_EXECUTION.md` for purchase URLs and execution order.
