# Comparator scan assets (operator-local)

Licensed manga excerpt PDFs for blind-10 judge packets. **Not committed to git.**

Place files here per `COMPARATOR_SCAN_DELIVERY_CHECKLIST.md`, `COMPARATOR_ACQUISITION_CHECKLIST.md`,
and `COMPARATOR_REGISTRY.yaml` `operator_asset` paths.

## P0 pilot files expected

| File | Comparator | Pages |
|---|---|---|
| `yotsuba_v1_ch1_pages_5-8.pdf` | Yotsuba&! Vol 1 Ch1 | 5–8 |
| `barakamon_v1_ch1_pages_6-10.pdf` | Barakamon Vol 1 Ch1 | 6–10 |

## After each acquisition

1. `sha256sum comparators/<filename>.pdf`
2. Update `COMPARATOR_REGISTRY.yaml` → `asset_status: ACQUIRED`, `sha256`, `acquired_date`
3. Update `SOURCING_TRACKER.yaml` → `comparators.acquired` count
4. Run validation:

```bash
python3 scripts/qa/validate_manga_blind10_comparators.py \
  --run-id manga_blind10_2026-07-08 \
  --require-p0
```

Expected when P0 complete: exit 0, `pilot_ready: true`, `acquired: 2`.

See also: `EXPECTED_MANIFEST.yaml`, `PILOT_SLOT_01_ACQUISITION_EXECUTION.md`.
