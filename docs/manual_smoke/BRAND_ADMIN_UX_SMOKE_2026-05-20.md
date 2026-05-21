# Brand Admin UX smoke — 2026-05-20

**Surfaces:** `brand-wizard-app/public/brand_admin.html`, `brand-wizard-app/public/brand_admin_weekly_os.html`  
**Prereq:** `python3 scripts/run_server.py` (API on `http://127.0.0.1:8000` unless `?api_base=` override)

---

## Scenario 1 — Happy path (200 + ZIP)

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open `brand_admin.html?brand=zen_clarity_en_us&phase=2` | Phase 2 visible; “Last built” badge loads |
| 2 | Click **Download** | Spinner + “Building…”; button disabled |
| 3 | Wait | Green toast: `Downloaded zen_clarity_en_us_<ISO-week>.zip`; ZIP saves; button resets |

Repeat on `brand_admin_weekly_os.html?brand=zen_clarity_en_us` (Phase 2).

---

## Scenario 2 — 404

| Step | Action | Expected |
|------|--------|----------|
| 1 | Brand/week with no ZIP | Page loads |
| 2 | Click **Download** | Red toast: `No package for <brand>/<week>. Has Monday cron run?` |

---

## Scenario 3 — 500

| Step | Action | Expected |
|------|--------|----------|
| 1 | Staging mock of 500 on download route | — |
| 2 | Click **Download** | Red toast: `Build pipeline failed. Check Monday cron logs.` |

---

## Scenario 4 — Network down

| Step | Action | Expected |
|------|--------|----------|
| 1 | Stop `scripts/run_server.py` | — |
| 2 | Click **Download** | Red toast: `Server unreachable. Is the API running?` |

---

## Scenario 5 — Double-click debounce

| Step | Action | Expected |
|------|--------|----------|
| 1 | Double-click **Download** rapidly | One fetch only; no duplicate ZIP |

---

## Scenario 6 — Background tab polling pause

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open Phase 2; note badge | Populated |
| 2 | Background tab ≥60s | No `coordination-status` while hidden |
| 3 | Foreground tab | Polling resumes |
| 4 | Optional MISSING→CURRENT | One-time info toast: `Weekly package built — refresh to download latest` |

---

## Sign-off

| Scenario | Pass? | Operator | Date |
|----------|-------|----------|------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
