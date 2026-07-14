# 11 - Pearl_Int Existing Messaging Channel Hardening

```text
EXECUTE. You are Pearl_Int hardening existing WhatsApp, LINE, and Messenger paths.

READ FIRST:
- docs/INTEGRATION_CREDENTIALS_REGISTRY.md
- config/freebies/report_delivery_channels.yaml
- docs and code found by lane 01 for WhatsApp, LINE, Messenger

MISSION:
Verify and harden existing non-email channels so report delivery can use them:
- WhatsApp
- LINE for Japan
- Messenger for Japan/fallback if configured

DELIVERABLES:
- verified env var list
- dry-run send commands
- sanitized test fixtures
- missing integration blockers if any channel is docs-only

DO NOT:
- Pretend a channel works if no code path exists.
- Print secrets.

TESTS/PROOFS:
- dry-run send tests
- missing-credential tests fail clearly

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
freebie-existing-channel-hardening=<sha>
```
