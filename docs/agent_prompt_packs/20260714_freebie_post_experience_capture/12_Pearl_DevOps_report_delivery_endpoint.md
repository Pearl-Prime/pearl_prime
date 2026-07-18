# 12 - Pearl_DevOps Report Delivery Endpoint

```text
EXECUTE. You are Pearl_DevOps implementing/reporting the delivery endpoint.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- config/freebies/report_delivery_channels.yaml
- report generator from lane 04
- channel integrations from lanes 10 and 11

MISSION:
Create or wire the endpoint that receives report unlock payloads and dispatches
the report through the requested channel. Prefer existing Cloudflare/R2/worker
patterns if present.

DELIVERABLES:
- endpoint implementation or explicit use of existing endpoint
- R2/report storage plan if reports are persisted
- sanitized local test command
- deploy/runbook doc

DO NOT:
- Store PII in public R2.
- Expose secrets.
- Require paid services without env-gated failover.

TESTS/PROOFS:
- local dry run
- missing credential failure
- successful mocked delivery

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
freebie-report-delivery-endpoint=<sha>
```
