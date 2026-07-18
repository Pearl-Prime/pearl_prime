# Lane 08 — Local verification (teacher portal v2)

**Date:** 2026-07-18  
**Stack:** Vite `127.0.0.1:5173` + mock API `127.0.0.1:8790` (`TEACHER_PORTAL_DEV_STORE=/tmp/teacher_portal_lane08_vfy`)  
**Deploy:** BLOCKED (GitHub suspended; CF Pages path is GH-Actions-only per Q-OC7-02)

## Commands used

```bash
TEACHER_PORTAL_DEV_STORE=/tmp/teacher_portal_lane08_vfy \
  node brand-wizard-app/server/teacher_portal_dev_api.mjs --port 8790
cd brand-wizard-app && npm run dev -- --host 127.0.0.1 --port 5173
python3 artifacts/qa/oldchats7_finish_20260718/lane08/run_api_smoke.py
python3 -m pytest tests/teacher_onboarding/test_import_dry_run.py -q
python3 scripts/teacher_onboarding/import_dry_run.py \
  --submission artifacts/qa/oldchats7_finish_20260718/lane08/fixtures/sample_submission.json
```

## Browser evidence (DOM + screenshots; tokens redacted)

| Artifact | Proves |
|----------|--------|
| `01_initial.png` + `dom_text_initial.txt` | Draft portal UI on existing intake (`Save draft`, production-atoms disclaimer) |
| `03_resumed.png` + `resume_hydrate.json` | Leave → resume via `edit_token` hydrates teacher name/email/id |
| `06_operator_queue.png` + `dom_text_queue.txt` | Operator queue lists drafts + submissions; atoms column `false` |
| `api_smoke.json` | API create → resume → edit → submit; `production_atoms_created: false` |
| `intake_regression.json` | One-shot submit (no draft) still OK |
| `import_dry_run_out.json` | Import CLI scaffold; `production_atoms_created: false` |

## Acceptance

- Draft CRUD + resume token: **yes** (local mock + browser)
- Operator queue: **yes**
- Import dry-run: **yes**
- One-shot intake regression: **yes**
- Production atoms created: **no**
- Live Cloudflare deploy: **BLOCKED** (GitHub 403; GH-Actions deploy unavailable)
