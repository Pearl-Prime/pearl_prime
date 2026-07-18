# Handoff — Lane 03 · Brand Director page + phantom-books fix (2026-07-19)

## Verdict
**LANDED-OFFLINE** — page-load proof + before/after + fail-closed catalog bearing + ops_url retarget + regression tests green.

## Page routing (EXECUTED-REAL)
- Roster: `http://127.0.0.1:4319/brand_directors.html` → HTTP 200 (vite PID served).
- Per-brand ops: `?brand=<id>` on `brand_handoff_dashboard.html` (scoped identity via query param).
- Test brand zero-asset: `optimizer_en_us` (Daybreak Editions) — no `brand_deliveries/optimizer.json`.
- Test brand with delivery metadata: `stabilizer_en_us` — delivery file present.

## Bug repro (BEFORE)
- Roster `ops_url` pointed to stale `/brand_admin.html?brand=…`.
- That page hardcodes UPLOADS title counts (`titles:6/4/3/…`) for every brand regardless of real assets.
- Evidence: `artifacts/qa/brand_wizard_director_page_verify_20260719/before/`
  - `VISIBLE_PROOF_before.html`
  - `phantom_books_optimizer_en_us.json` (KDP=6, GP=4, …)
  - `brand_admin_optimizer_en_us.html` (served HTML)

## Fix (layers)
1. **Back-end gate** (`server/routes/brand_onboarding.py`):
   - `_is_catalog_bearing` → **fail-closed** (unknown / empty index → False).
   - `available_downloadable_assets(delivery)` → only real file+url rows; pending/catalog-only → `[]`.
2. **React data source**:
   - `brand-wizard-app/src/brandDirectorRoster.js` — `ops_url` → `brand_handoff_dashboard.html`.
   - `brand-wizard-app/src/brandDirectorAvailability.js` — real-asset summary + empty label "No titles available yet".
   - `BrandDirectorDashboard.jsx` — canonical ops URLs + available-books panel from delivery feed.
3. **Live assignments API** (`functions/api/onboarding/assignments.js`) — same ops_url retarget so live overlay consumers match static fallback.

## AFTER proof
- `artifacts/qa/brand_wizard_director_page_verify_20260719/after/`
  - `VISIBLE_PROOF_after.html`
  - `ops_url_fix_proof.json` → `/brand_handoff_dashboard.html?brand=optimizer_en_us`
  - `empty_state_optimizer_en_us.json` — no delivery file; handoff page HTTP 200 with production-pending gate
  - `catalog_bearing_fail_closed.json` — all four fail-closed/show cases true

## Regression tests (green)
```
PYTHONPATH=. python3 -m pytest tests/brand_wizard/test_catalog_bearing_and_ops_url.py -q
# 10 passed
```
Also updated `test_pages_assignment_lookup.py` ops_url assertion to handoff dashboard.

## Sibling surfaces (follow-on — do NOT treat as fixed here)
- `brand_admin.html` still hardcodes phantom UPLOADS counts if opened directly (setup console; no longer Ops deep-link).
- Storefront / GHL feed / exec dashboard may still share fail-open or catalog-as-available patterns — audit separately.
- `brand_admin_weekly_os.html` synced from repo-root — edit root source only if touching that surface.

## Cleanup
- vite on `:4319` should be stopped after closeout.
- No worktrees created.
- Shared tree stayed on `codex/realist-social-samples-20260718`.
- Synthetic data: none persisted outside evidence dir.

## PROVENANCE
- research: operator "stop showing planned books as available; show what we've got, which is nothing"
- documents: DASH-02; BRAND_ADMIN_CANONICAL_PACKAGE; COLAB/browser verification runbook; brand_director_assignments.yaml
- builds_on: brand_directors React + brand_onboarding availability (EXTEND)
- inventory: EXTENDS (adds real-asset gating; drops nothing)
