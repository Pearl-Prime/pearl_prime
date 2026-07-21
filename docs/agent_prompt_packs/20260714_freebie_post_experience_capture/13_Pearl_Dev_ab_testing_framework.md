# 13 - Pearl_Dev A/B Testing Framework

```text
EXECUTE. You are Pearl_Dev adding A/B testing for report unlock channels/copy.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- config/freebies/report_unlock_copy.yaml
- config/freebies/report_delivery_channels.yaml
- brand-wizard-app/public/free/js/phoenix_funnel.js

MISSION:
Add deterministic A/B assignment for:
- channel order
- WhatsApp-first vs Telegram-first vs email fallback presentation
- headline/benefit copy variant
- report cliffhanger framing

Requirements:
- stable assignment by cid if present, otherwise localStorage
- allow `?ab_variant=` override for QA
- include ab_variant in capture payload
- default production weighting: WhatsApp-first most often, Telegram included only when integration configured, email fallback always visible

DELIVERABLES:
- A/B config
- shared JS assignment helper
- tests

DO NOT:
- Randomize every page load.
- Hide email fallback.

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
freebie-ab-testing-framework=<sha>
```
