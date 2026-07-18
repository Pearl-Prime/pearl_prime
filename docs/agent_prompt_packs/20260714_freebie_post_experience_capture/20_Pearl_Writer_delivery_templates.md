# 20 - Pearl_Writer Delivery Templates And Nurture

```text
EXECUTE. You are Pearl_Writer plus Pearl_Int updating report delivery templates.

READ FIRST:
- funnel/waystream_sanctuary/emails/*.html
- config/freebies/report_unlock_copy.yaml
- config/freebies/report_specs/way_stream_sanctuary/*.yaml
- channel docs from lanes 10 and 11

MISSION:
Create delivery copy for:
- WhatsApp report message
- Telegram report message
- email report delivery
- LINE/Messenger fallback if configured
- follow-up nurture that references the completed tool

DELIVERABLES:
- templates/config for each channel
- updated email templates if needed
- preview fixtures

DO NOT:
- Remove existing 9-email campaign plan.
- Send real messages.

TESTS/PROOFS:
- every template renders with sample report payload.
- no unresolved merge tags.

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
freebie-report-delivery-templates=<sha>
```
