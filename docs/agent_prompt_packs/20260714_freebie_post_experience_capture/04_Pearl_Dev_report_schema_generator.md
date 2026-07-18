# 04 - Pearl_Dev Report Schema And Generator

```text
EXECUTE. You are Pearl_Dev implementing the freebie report schema and generator.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- config/freebies/freebie_registry.yaml
- config/freebies/somatic_app_catalog.yaml
- scripts/freebies/validate_campaign_plan.py

MISSION:
Define a stable report model for every freebie:
- tool answers
- score/result band
- insight summary
- somatic/nervous-system/psychological/spiritual benefit copy
- "what this may reveal for your next week" reflective forecast
- recommended next practice/book
- delivery-ready HTML/text payload

DELIVERABLES:
- config/freebies/freebie_report_templates.yaml or equivalent.
- generator/validator script under scripts/freebies.
- sample reports for at least 3 tools.

DO NOT:
- Make medical claims.
- Store secrets.
- Commit user PII.

TESTS/PROOFS:
- JSON/YAML schema validation.
- Snapshot tests for sample reports.
- Report includes no unresolved placeholders.

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
freebie-report-schema-generator=<sha>
```
