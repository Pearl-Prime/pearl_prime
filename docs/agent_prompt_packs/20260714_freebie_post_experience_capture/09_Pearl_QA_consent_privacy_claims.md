# 09 - Pearl_QA Consent, Privacy, Claims

```text
EXECUTE. You are Pearl_QA reviewing consent, privacy, and claims.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- config/freebies/report_unlock_copy.yaml
- config/freebies/report_delivery_channels.yaml
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md

MISSION:
Define and enforce the compliance guardrails:
- channel consent language
- opt-out language
- privacy notice for answers_json and channel handles
- medical/therapy claim restrictions
- spiritual language boundaries
- "future" copy must be reflective/educational, not deterministic prediction

DELIVERABLES:
- docs/freebies/FREEBIE_REPORT_CAPTURE_COMPLIANCE_20260714.md
- claim lint checklist or test fixture.

DO NOT:
- Block strong marketing copy just because it is vivid.
- Allow false certainty or health guarantees.

TESTS/PROOFS:
- Copy framework and report specs reviewed against checklist.

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
freebie-consent-claims-qa=<sha>
```
