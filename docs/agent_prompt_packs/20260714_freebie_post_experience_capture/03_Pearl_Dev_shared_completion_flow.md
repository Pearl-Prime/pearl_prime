# 03 - Pearl_Dev Shared Completion Flow Engine

```text
EXECUTE. You are Pearl_Dev implementing the shared tool-first completion flow.

STARTUP_RECEIPT:
- EXECUTION_MODE: isolated_worktree
- BACKGROUND_SAFE: yes
- RUNTIME_HOST: declare
- PERSISTENCE_SURFACES: branch, PR, tests
- RESUME_SURFACE: artifacts/coordination/handoffs/freebie_completion_flow.md

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- brand-wizard-app/public/free/js/phoenix_funnel.js
- brand-wizard-app/public/free/js/phoenix_lead.js
- one representative Waystream HTML page

MISSION:
Build shared client-side primitives for:
- tool starts immediately without lead capture
- app stores answers/progress locally
- completion event opens report-offer section
- report-offer can call capture only after completion
- capture payload includes answers_json, result summary, score, score_band, freebie_id, topic, source_page_slug

DELIVERABLES:
- Shared JS API, preferably in phoenix_funnel.js or a new small JS module.
- Backward-compatible helpers for existing pages.
- Tests or static smoke script.

DO NOT:
- Convert all HTML pages in this lane.
- Break existing GHL capture.
- Remove cid/unlock bypass support.

SMALLEST SAFE BATCH:
- Implement shared API and convert one fixture/demo page only if needed.

TESTS/PROOFS:
- Unit/static checks for completion event, answer capture, and report gate opening.
- Manual smoke command for one page.

Acceptance:
- Required deliverables are complete without weakening existing capture, security, or consent behavior.
- Tests/proofs are attached, or the lane returns one exact blocker with file-level evidence.

Return format:
LANE_CLOSEOUT:
- branch:
- commit:
- pr:
- files_changed:
- tests:
- proofs:
- remaining_true_blockers:

CLOSEOUT_RECEIPT:
freebie-completion-flow-engine=<sha>
```
