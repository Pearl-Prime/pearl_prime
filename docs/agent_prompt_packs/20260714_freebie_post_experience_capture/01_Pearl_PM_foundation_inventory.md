# 01 - Pearl_PM Foundation Inventory

```text
EXECUTE. You are Pearl_PM running foundation inventory for the freebie
post-experience capture program.

STARTUP_RECEIPT:
- EXECUTION_MODE: local_or_cloud_repo
- BACKGROUND_SAFE: no
- RUNTIME_HOST: declare
- PERSISTENCE_SURFACES: docs, artifacts, PR
- RESUME_SURFACE: artifacts/coordination/handoffs/freebie_foundation_inventory.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/AGENT_PROMPT_ROUTER_V4.md
- brand-wizard-app/public/free/js/phoenix_lead.js
- brand-wizard-app/public/free/js/phoenix_funnel.js
- config/freebies/freebie_registry.yaml
- config/freebies/somatic_app_catalog.yaml
- docs/ghl/GHL_ADMIN_WAYSTREAM_EVERGREEN_FREEBIE_FUNNEL.md

LIVE STATE RECONCILIATION:
- Fetch latest main.
- List all Waystream freebie pages under brand-wizard-app/public/free/way_stream_sanctuary.
- Inventory current capture timing: email-first, tool-first, mixed, unknown.
- Inventory existing delivery/integration docs for GHL, WhatsApp, LINE, Messenger, Telegram.

PRE-REQUISITE CHECKS:
- Confirm no lane already owns these freebie files in ACTIVE_WORKSTREAMS.tsv.
- Confirm webhook URLs/secrets are not printed into artifacts.

DISCOVERY REPORT BEFORE ACTION:
- Page list.
- Shared JS functions.
- Existing campaign payload fields.
- Existing delivery channels.
- Hot files and recommended lane boundaries.

MISSION:
Create the authoritative inventory and register this workstream if safe.

DELIVERABLES:
- artifacts/coordination/handoffs/freebie_foundation_inventory.md
- artifacts/qa/freebie_post_experience_capture_20260714/inventory.json
- ACTIVE_WORKSTREAMS.tsv row if repo policy requires it.

DO NOT:
- Change HTML behavior.
- Change webhooks.
- Start integrations.

SMALLEST SAFE BATCH:
- Read-only plus docs/artifacts only.

TESTS/PROOFS:
- `find brand-wizard-app/public/free/way_stream_sanctuary -maxdepth 2 -name index.html`
- grep proof for current capture forms and scripts.

MERGED-or-BLOCKED:
Open a docs/artifacts PR if changes are required; otherwise close with read-only receipt.

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
freebie-foundation-inventory=<sha-or-readonly>
```
