# Dispatch: `ws_planned_volumes_per_brand_backfill_20260526`

**Owners:** Pearl_Editor + Pearl_Marketing  
**Parent:** `PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1`  
**Status:** `in_progress` (routed 2026-05-26 after #1320 + #1315 merge)

## Goal

Fill per-brand planned-volume data so `GET /api/brand_admin/brand/{brand_id}/planned_volumes` returns real `summary_line` values (not only manga defaults + gap strings) for the v2 picker (`brand_admin_v2.html`).

## Read-first

1. `server/routes/brand_admin_public.py` — `planned_volumes()` (reads `manga_brand_series_plan.yaml`; podcast/audiobook gaps are hardcoded today)
2. `config/manga/manga_brand_series_plan.yaml` — **manga axis already wired** (`active_series_target`, `volumes_per_year_target` per brand)
3. `config/podcast/brand_podcast_plans.yaml` — market-level plans; **no per-brand_id rows yet**
4. `BRAND_ADMIN_CANONICAL_PACKAGE.md` + `docs/PEARL_ARCHITECT_STATE.md` **BR-CANON-02-GLOBAL-BRAND-IDENTITY** (37 manga-canon picker; axes remain distinct)
5. `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` — this ws row

## Scope (minimum)

- **37 manga-canon brands** (`config/manga/canonical_brand_list.yaml`) — ensure each has usable `planned` fields surfaced by the endpoint
- **Extension to 26 book + 38 music brands:** operator-decision (defer unless operator says go)

## Suggested split (3 sub-sessions)

| Sub-ws | Owner | Target | Notes |
|--------|-------|--------|-------|
| ebook plan | Pearl_Marketing | `config/brand_management/**` or release-velocity SSOT | Map `volumes_per_year_target` / ebook cadence per brand |
| podcast plan | Pearl_Editor | `config/podcast/brand_podcast_plans.yaml` or new `brands:` section | Wire `planned.podcast` in endpoint after schema agreed |
| audiobook plan | Pearl_Editor | `config/audiobook/**` | Wire `planned.audiobook` after schema agreed |

Coordinate with Pearl_Architect if a **new canonical field** is needed in more than one file.

## Deliverables

- Config backfill (read-only on registries per BR-CANON-01 Path X)
- `artifacts/brand_admin/planned_volumes_coverage_20260526.tsv` (per-brand: brand_id, ebooks, manga_series, podcast, audiobook, gaps)
- Close ws row: `completed`, `last_updated`, evidence_paths

## Verification

```bash
PYTHONPATH=. python3 scripts/run_server.py --port 8000 &
curl -s http://127.0.0.1:8000/api/brand_admin/brand/stillness_press/planned_volumes | python3 -m json.tool
PYTHONPATH=. python3 -m pytest tests/test_brand_admin_v2_api.py -v -k planned_volumes
```

## Out of scope

- Code changes to `brand_admin_public.py` unless schema requires new keys (separate Pearl_Dev ws if needed)
- Manga series plan rewrites beyond filling missing brand rows
