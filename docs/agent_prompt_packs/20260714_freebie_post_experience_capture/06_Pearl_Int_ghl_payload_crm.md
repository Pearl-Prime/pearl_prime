# 06 - Pearl_Int GHL Payload And CRM Fields

```text
EXECUTE. You are Pearl_Int updating GHL payload and CRM docs.

READ FIRST:
- docs/ghl/GHL_ADMIN_WAYSTREAM_EVERGREEN_FREEBIE_FUNNEL.md
- brand-wizard-app/public/free/js/phoenix_lead.js
- config/freebies/ghl_funnel_capture.yaml
- scripts/freebies/smoke_freebie_capture.py

MISSION:
Extend capture payload to support post-experience report unlock:
- delivery_channel
- delivery_address or channel handle
- channel_consent
- report_id
- report_variant
- report_summary
- answers_json
- completed_at
- completion_duration_seconds
- ab_variant

DELIVERABLES:
- Payload update in shared capture code/config.
- GHL admin custom-field mapping doc update.
- Smoke test payload fixture.

DO NOT:
- Remove existing phoenix_e1..e9 campaign fields.
- Print webhook URL.

TESTS/PROOFS:
- Existing campaign plan validator still passes.
- Smoke capture payload includes old and new fields.

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
freebie-ghl-report-payload=<sha>
```
