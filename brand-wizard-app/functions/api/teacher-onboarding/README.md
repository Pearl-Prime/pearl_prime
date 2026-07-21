# Teacher onboarding Pages Functions

## One-shot intake (v1 — unchanged)

`POST /api/teacher-onboarding/submit`

Writes:

- `teacher_onboarding/submissions/<teacher_id>__<timestamp>.json`
- `teacher_onboarding/activations/<teacher_id>.json`

Never creates production teacher atoms (`production_atoms_created: false`).

## Portal v2 (draft / resume / queue)

Authority: `docs/specs/TEACHER_PORTAL_V2_SPEC.md`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/teacher-onboarding/drafts` | Create draft |
| GET | `/api/teacher-onboarding/drafts?edit_token=` | Resume by token |
| GET/PUT/DELETE | `/api/teacher-onboarding/drafts/:id` | Load / update / delete (token required) |
| POST | `/api/teacher-onboarding/drafts/:id/rotate-token` | Rotate edit token |
| GET | `/api/teacher-onboarding/queue` | Operator pending queue (read-only) |

Draft objects live at `teacher_onboarding/drafts/<id>.json` with token index
`teacher_onboarding/drafts_by_token/<token>.json`.

Set `TEACHER_PORTAL_MOCK=1` on a Pages/wrangler env to use the in-memory mock store
(for Function unit tests). Local UI verify uses
`node server/teacher_portal_dev_api.mjs` (filesystem store) proxied by Vite.

## Import step

Dry-run CLI only (no production atoms):

```bash
python3 scripts/teacher_onboarding/import_dry_run.py \
  --submission artifacts/qa/oldchats7_finish_20260718/lane08/fixtures/sample_submission.json
```

## UI surfaces

- `/teacher_onboarding.html` — intake + draft save/resume/edit/delete
- `/teacher_operator_queue.html` — operator queue
