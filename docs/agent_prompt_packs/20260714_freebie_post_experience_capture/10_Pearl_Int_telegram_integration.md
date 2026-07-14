# 10 - Pearl_Int Telegram Integration

```text
EXECUTE. You are Pearl_Int implementing Telegram report delivery.

READ FIRST:
- config/freebies/report_delivery_channels.yaml
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md
- existing WhatsApp/LINE/Messenger integration docs or code discovered by lane 01

MISSION:
Add Telegram as a report delivery channel, matching the existing messaging
integration pattern as closely as possible.

Required:
- env var registry for Telegram bot token/webhook or provider key
- send report payload to Telegram when delivery_channel=telegram
- safe failure when credentials are missing
- local dry-run mode that prints sanitized payload only
- docs for setup

DELIVERABLES:
- integration code or adapter
- docs/ghl or docs/integrations Telegram setup doc
- tests for missing credentials and sanitized dry-run

DO NOT:
- Commit bot token.
- Send real messages in tests.

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
freebie-telegram-delivery=<sha>
```
