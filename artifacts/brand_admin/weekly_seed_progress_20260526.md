# Weekly packages directory seed — 2026-05-26

**Workstream:** `ws_weekly_packages_directory_seed_20260526`  
**Parent:** `PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1`  
**Week:** `2026-W22` (Monday anchor `2026-05-25`)

## Path decision

**Path B — stub packages (MVP)**

- `build_weekly_brand_package.py --dry-run` for `stillness_press`: exit 0, **0 books planned** (book-registry lane; manga-canon brands are not in `config/brand_registry.yaml` lanes).
- Full build would invoke `run_pipeline.py` per book (30+ min / paid-tier risk) — out of scope.
- `build_admin_packets.py` requires coordination TSV + `manifest.json` first; no prior manifests on disk.
- Stub ZIPs unblock v2: `package_status=current`, non-empty `platform_rows`, Download buttons (each deliverable lists `README.txt` so API `count≥1`).

## Seeded brands (37 manga-canon)

All IDs from `config/manga/canonical_brand_list.yaml` — see coordination TSV for full list.

## Artifacts

| Artifact | Count |
|----------|-------|
| `artifacts/weekly_packages/<brand>/2026-W22/manifest.json` | 37 |
| `artifacts/weekly_packages/<brand>/2026-W22/<brand>_2026-W22.zip` | 37 |
| `artifacts/weekly_packages/<brand>/2026-W22/README.txt` | 37 |
| `artifacts/coordination/weekly_packages_2026-05-25.tsv` | 185 rows (37×5 deliverable types) |

## Sample manifest.json (`stillness_press`)

```json
{
  "brand_id": "stillness_press",
  "week_iso": "2026-W22",
  "week_monday": "2026-05-25",
  "package_type": "stub_mvp",
  "deliverables": {
    "books": {"status": "stub", "files": ["README.txt"]},
    "atoms": {"status": "stub", "files": ["README.txt"]},
    "manga_panels": {"status": "stub", "files": ["README.txt"]},
    "pearl_news": {"status": "stub", "files": ["README.txt"]},
    "podcast": {"status": "stub", "files": ["README.txt"]}
  }
}
```

## Smoke (post-seed)

Recorded in session CLOSEOUT_RECEIPT.

## Follow-up (do not open this session)

1. `ws_weekly_packages_real_content_build_<axis>_20260526` — per-axis real content (Pearl_Editor / Pearl_Dev)
2. `ws_weekly_packages_cron_wireup_20260526` — Pearl_DevOps Monday cron
3. `ws_brand_onboarding_hub_navigate_v2_link_20260526` — Pearl_Brand (~5-line hub link) if operator confirms
