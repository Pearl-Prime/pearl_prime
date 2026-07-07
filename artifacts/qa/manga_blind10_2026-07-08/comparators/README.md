# Comparator scan assets (operator-local)

Licensed manga excerpt PDFs for blind-10 judge packets. **Not committed to git.**

Place files here per `COMPARATOR_ACQUISITION_CHECKLIST.md` and `COMPARATOR_REGISTRY.yaml`
`operator_asset` paths (e.g. `yotsuba_v1_ch1_pages_5-8.pdf`).

After each acquisition:
1. `sha256sum <file>.pdf`
2. Update `COMPARATOR_REGISTRY.yaml` → `asset_status: ACQUIRED`, `sha256`, `acquired_date`
3. Update `SOURCING_TRACKER.yaml` → `comparators.acquired` count
