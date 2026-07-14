# 05 - Pearl_Int Channel Routing Contract

```text
EXECUTE. You are Pearl_Int defining delivery-channel routing.

READ FIRST:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md
- brand-wizard-app/public/free/js/phoenix_lead.js

MISSION:
Create the channel routing contract:
- default order: WhatsApp, Telegram, email
- Japan order: LINE, Messenger, WhatsApp, Telegram, email
- fallback when channel config is missing
- validation for phone, Telegram handle/username, LINE ID, Messenger ID, email
- explicit consent copy per channel

DELIVERABLES:
- config/freebies/report_delivery_channels.yaml
- JS/config mapping for channel order and labels
- docs for required env vars/secrets

DO NOT:
- Implement Telegram API calls here.
- Put credentials into docs.

TESTS/PROOFS:
- Contract test for channel order by locale/region.
- Validation test for fallback to email.

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
freebie-channel-routing-contract=<sha>
```
