# 02 - Pearl_Architect Product Architecture

```text
EXECUTE. You are Pearl_Architect designing the freebie post-experience capture
architecture.

STARTUP_RECEIPT:
- EXECUTION_MODE: local_or_cloud_repo
- BACKGROUND_SAFE: no
- RUNTIME_HOST: declare
- PERSISTENCE_SURFACES: docs/specs, artifacts, PR
- RESUME_SURFACE: artifacts/coordination/handoffs/freebie_product_architecture.md

READ FIRST:
- artifacts/coordination/handoffs/freebie_foundation_inventory.md
- brand-wizard-app/public/free/js/phoenix_lead.js
- brand-wizard-app/public/free/js/phoenix_funnel.js
- config/freebies/ghl_funnel_capture.yaml
- config/freebies/waystream_evergreen_campaign_plan.yaml

MISSION:
Specify the tool-first flow:
1. Visitor lands directly in the interactive tool.
2. Visitor completes the tool.
3. Completion screen congratulates them.
4. Page shows a personalized report unlock offer.
5. Visitor chooses delivery channel: WhatsApp first by default, Telegram when live, email fallback, LINE/Messenger for Japan where configured.
6. Capture sends tool answers, score/result, channel consent, and campaign plan fields.
7. Report delivery sends the report and starts nurture sequence.

DELIVERABLES:
- docs/specs/FREEBIE_POST_EXPERIENCE_CAPTURE_SPEC_20260714.md
- state machine diagram
- event taxonomy
- data payload schema
- channel priority rules
- safety/claims doctrine

DO NOT:
- Write code.
- Promise diagnosis, cure, guaranteed outcomes, or specific future certainty.

GOTCHAS:
- "Future" hooks must be phrased as reflective forecasts, not fortune-telling or medical prediction.
- Report lock should feel valuable, not punitive.

TESTS/PROOFS:
- Spec contains all 15 Waystream pages.
- Spec names exact shared JS/config surfaces to implement.

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
freebie-product-architecture=<sha>
```
