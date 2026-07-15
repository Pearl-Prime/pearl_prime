# GHL Sub-Account API Pilot Handoff - 2026-07-15

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md from PR #5686
documents=docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md from PR #5687; artifacts/coordination/handoffs/ghl_credential_scope_probe_2026-07-15.md from PR #5688; artifacts/coordination/handoffs/ghl_manifest_dry_run_diff_2026-07-15.md from PR #5689; docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md from PR #5690
builds_on=Pearl_Int credential proof and dry-run desired-state engine
inventory=EXTENDS GHL integration; does not alter feed/webhook behavior

CLOSEOUT_RECEIPT
AGENT=Pearl_Int
LANE=05_subaccount_api_pilot
STATUS=BLOCKED
PR=https://github.com/Ahjan108/phoenix_omega_v4.8/pull/TBD
MERGE_SHA=none
AUTH_MODEL=blocked
PILOT_LOCATION=none
LIVE_WRITE_COUNT=0
READBACK_PROOF=none
IDEMPOTENCY_PROOF=none
SCALE_RECOMMENDATION=blocked: no credential/scope proof, no merged dry-run implementation, no merged field map, and no exact operator approval phrase
CLEANUP=plumbing branch, no physical worktree; scratch /tmp/ghl_lane05 removed after push; credential staging files never created; background jobs none; live GHL target none; live write count 0
HANDOFF=artifacts/coordination/handoffs/ghl_subaccount_api_pilot_2026-07-15.md
SIGNAL=ghl-subaccount-api-pilot=BLOCKED
NEXT_ACTION=After PRs #5686-#5690 merge and the operator provides credential/sandbox proof plus exact phrase OPERATOR_GHL_LIVE_PILOT_APPROVED, run one custom-value pilot on phoenix_last_sync_sha only.

## Missing Gates

- `ghl-credential-scope-probe=<full-sha>` does not exist; lane 03 is BLOCKED.
- `ghl-yaml-dry-run-diff=<full-sha>` does not exist; lane 04 is BLOCKED and has only a dry-run example/handoff.
- `ghl-marketing-field-map=<full-sha>` does not exist; lane 06 is BLOCKED pending CI/merge.
- The operator has not typed the exact approval phrase `OPERATOR_GHL_LIVE_PILOT_APPROVED`.
- No operator-selected sandbox/test `location_id` is available.

## Safety Result

No reads or writes were attempted. No PUT/POST/PATCH/DELETE was performed. No credentials were touched. No sub-accounts were created.
