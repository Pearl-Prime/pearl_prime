# 14 - Pearl_QA Analytics Event Taxonomy

```text
EXECUTE. You are Pearl_QA defining analytics and measurement.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- A/B framework from lane 13
- existing GA4/UTM code in freebie pages

MISSION:
Define and implement/verify events:
- tool_view
- tool_start
- tool_step_complete
- tool_complete
- report_offer_view
- channel_selected
- report_capture_submit
- report_delivery_success
- report_delivery_fail
- fallback_email_used

DELIVERABLES:
- analytics spec doc
- JS event helper or integration with existing gtag
- QA event fixture

DO NOT:
- Send PII in analytics events.

TESTS/PROOFS:
- event payloads contain slug, topic, variant, channel, no email/phone/handle.

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
freebie-analytics-taxonomy=<sha>
```
