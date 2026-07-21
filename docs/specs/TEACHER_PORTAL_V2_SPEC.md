# Teacher Portal V2 Spec

**Status:** SPECCED + CODE-WIRED (lane 08, 2026-07-18)  
**Authority:** extends live one-shot intake at `/teacher_onboarding`  
**OPD:** OPD-OC7-03 (build approved). Q-OC7-02 = live Cloudflare deploy DEFER.

## Purpose

Upgrade the one-shot teacher intake into a management portal:

- draft save / resume / edit / delete
- edit-token recovery (no accounts)
- operator pending-queue (read-only)
- import-step contract (dry-run only; never auto-create production atoms)

The existing `POST /api/teacher-onboarding/submit` contract remains unchanged.

## R2 layout

| Prefix | Mutability | Purpose |
|--------|------------|---------|
| `teacher_onboarding/drafts/<draft_id>.json` | mutable until submitted/deleted | Working draft + edit token |
| `teacher_onboarding/drafts_by_token/<edit_token>.json` | mutable with draft | Index: `{ draft_id }` for resume lookup |
| `teacher_onboarding/submissions/<teacher_id>__<ts>.json` | immutable | Submitted intake (v1) |
| `teacher_onboarding/activations/<teacher_id>.json` | overwrite status only | Public-safe activation status |

Dev/local mock may mirror the same key layout on a filesystem root when R2 is unconfigured.

## Draft record schema

```json
{
  "schema_version": "teacher_onboarding_draft_v1",
  "draft_id": "<uuid>",
  "edit_token": "<unguessable>",
  "status": "draft",
  "created_at": "<iso8601>",
  "updated_at": "<iso8601>",
  "teacher_id": "<slug>",
  "teacher_name": "<string>",
  "ui_state": { },
  "server_policy": {
    "production_atoms_created": false,
    "operator_review_required": true,
    "client_readiness_trusted_for_production": false
  },
  "submission_key": null
}
```

`ui_state` is the form hydrate blob (identity, rights, materials fields). It is not a production atom bank.

## Lifecycle

```
draft → submitted → imported → candidate_atoms → approved → production_ready
```

| State | Who | Notes |
|-------|-----|-------|
| `draft` | teacher (edit-token) | CRUD allowed; delete allowed |
| `submitted` | teacher submit → intake | Submissions immutable; draft marked submitted |
| `imported` | operator import step | Candidate scaffold only |
| `candidate_atoms` | Pearl Writer / operator | Not production |
| `approved` | human operator | Explicit approval |
| `production_ready` | production gates | Only after approval + gates |

**Hard rule:** every object in this portal path carries `production_atoms_created: false` until a separate, operator-gated promotion lane flips it. This lane never flips it.

## Edit-token model

- Unguessable token (≥128 bits entropy, URL-safe).
- Resume URL: `/teacher_onboarding.html?edit_token=<token>` (or `?draft=<id>&edit_token=<token>`).
- No accounts / passwords / CAPTCHA in v2.
- Token required for GET/PUT/DELETE of a draft.
- `POST .../rotate-token` issues a new token, invalidates the old index key, returns the new resume URL fragment.

## Delete semantics

- **Drafts only** may be deleted (status `draft`).
- **Submissions are immutable** — no delete/edit API for submission JSON.
- Deleting a draft removes the draft object and its token index.

## API surface

| Method | Path | Auth | Behavior |
|--------|------|------|----------|
| POST | `/api/teacher-onboarding/drafts` | none | Create draft; returns `draft_id`, `edit_token`, resume hint |
| GET | `/api/teacher-onboarding/drafts?edit_token=` | token | Load draft for resume |
| PUT | `/api/teacher-onboarding/drafts/:id` | token header/body | Update `ui_state` |
| DELETE | `/api/teacher-onboarding/drafts/:id` | token | Delete draft |
| POST | `/api/teacher-onboarding/drafts/:id/rotate-token` | token | Rotate edit token |
| GET | `/api/teacher-onboarding/queue` | none (operator surface; public-safe fields only) | List pending drafts + submissions |
| POST | `/api/teacher-onboarding/submit` | none | **Unchanged** one-shot / final submit |

Token may be sent as `edit_token` query param, JSON body field, or `X-Edit-Token` header.

## Operator pending queue

Read-only page (`/teacher_operator_queue.html`) lists:

- drafts (`status=draft`) — id, teacher name, updated_at
- submissions — key, teacher name, received_at, readiness score, `production_atoms_created: false`

No edit of submissions from the queue. No production promotion controls.

## Import-step contract

**Input:** a submission JSON (`teacher_onboarding_intake_v1`).  
**Output:** normalized teacher-bank **candidate scaffold** (directories/manifest stubs only).

Required output fields:

```json
{
  "schema_version": "teacher_bank_import_scaffold_v1",
  "source_submission_key": "<r2 key or fixture path>",
  "teacher_id": "<slug>",
  "lifecycle_status": "imported",
  "production_atoms_created": false,
  "operator_review_required": true,
  "candidate_paths": {
    "doctrine": "...",
    "stories": "...",
    "practices": "...",
    "quotes": "...",
    "reflections": "..."
  },
  "counts_from_submission": { },
  "notes": ["dry-run only; no files written to SOURCE_OF_TRUTH unless --write-scaffold"]
}
```

CLI: `python3 scripts/teacher_onboarding/import_dry_run.py --submission <path>`.  
Default mode prints JSON to stdout and does **not** write into `SOURCE_OF_TRUTH/`. Optional `--write-scaffold <dir>` writes under a scratch directory only.

## UI contract

- One-shot Activate submit keeps working with no draft required.
- Save draft / Resume / Delete draft / Rotate token controls on the existing teacher onboarding surface.
- Resume hydrates `ui_state` without wiping empty optional sections incorrectly.
- After submit from a draft, draft status becomes `submitted` and `submission_key` is recorded when known.

## Deploy

Live Cloudflare Pages deploy rides GitHub Actions (`brand-admin-onboarding-pages.yml`).  
While GitHub is blocked, lane lands code+spec offline; `DEPLOY=BLOCKED` per Q-OC7-02.

## Non-goals (this lane)

- Account/password auth
- CAPTCHA
- Production atom creation / teacher-bank wiring execution
- Live CF deploy without restored GH path or explicit operator override
