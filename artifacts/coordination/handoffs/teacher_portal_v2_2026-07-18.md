# Handoff — Teacher Portal V2 (lane 08)

**Agent:** Pearl_Int lane 08  
**Date:** 2026-07-18  
**OPD-OC7-03:** build approved ("agreed. do it now")  
**Q-OC7-02:** live Cloudflare deploy = DEFER  

## Signal

```
teacher-portal-v2=<FULL_SHA_AFTER_LAND>
```

(Replace with landed commit SHA from CLOSEOUT; also mirrored below after land.)

## What landed

- Spec: `docs/specs/TEACHER_PORTAL_V2_SPEC.md`
- Draft CRUD Functions under `brand-wizard-app/functions/api/teacher-onboarding/`
- UI: save/resume/edit/delete + rotate-token on `TeacherOnboarding.jsx`
- Operator queue: `teacher_operator_queue.html` + `TeacherOperatorQueue.jsx`
- Local mock API: `brand-wizard-app/server/teacher_portal_dev_api.mjs` (Vite proxy)
- Import dry-run CLI: `scripts/teacher_onboarding/import_dry_run.py` (`production_atoms_created: false`)
- Proof: `artifacts/qa/oldchats7_finish_20260718/lane08/`

## Verify

See `artifacts/qa/oldchats7_finish_20260718/lane08/LOCAL_VERIFY.md`.

## Deploy

`DEPLOY=BLOCKED:GitHub account suspended (403); CF Pages deploy rides GH Actions (brand-admin-onboarding-pages.yml); local Pages REST tokens auth-fail / wrong account — Q-OC7-02 DEFER`

## Next action

When GitHub restored: merge offline ref (or PR) → `brand-admin-onboarding-pages.yml` auto-deploys to `https://brand-admin-onboarding-bu2.pages.dev`. Operator may override Q-OC7-02 with explicit "deploy now" + working CF token on account `b80152c3…`.

## Cleanup

Dev servers stopped after verify; temp git index removed; `node_modules`/`dist` not committed.
