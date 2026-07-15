# GHL Manifest Dry-Run Diff Handoff - 2026-07-15

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md from PR #5686
documents=docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md from PR #5687; docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md; config/marketing/brand_marketing_registry.yaml; docs/handoffs/ghl_location_manifest.example.tsv; docs/GHL_INTEGRATION_GUIDE.md
builds_on=active brand classifier; brand marketing registry; GHL feed/freebie manifest pattern
inventory=EXTENDS existing brand/marketing tooling; does not reduce feed publishing or webhook injection

CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=04_manifest_and_dry_run_diff
STATUS=BLOCKED
PR=https://github.com/Ahjan108/phoenix_omega_v4.8/pull/TBD
MERGE_SHA=none
SCRIPT_PATH=none
CONFIG_PATHS=none
DRY_RUN_PROOF=artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff_example.json
TESTS=not run; no implementation landed because lane 02 and CI are blocked
LIVE_WRITES=none
CLEANUP=plumbing branch, no physical worktree; scratch /tmp/ghl_lane04 removed after push; generated example retained in PR; no background jobs; no credentials touched
HANDOFF=artifacts/coordination/handoffs/ghl_manifest_dry_run_diff_2026-07-15.md
SIGNAL=ghl-yaml-dry-run-diff=BLOCKED
NEXT_ACTION=After lane 02 merges and CI is healthy, implement scripts/integrations/ghl_yaml_subaccount_sync.py with fixture-only tests for active YAML discovery, registry/manifest join, allowlist redaction, blocked missing mappings, and idempotent no-op.

## Implementation Contract

The CLI should be dry-run by default and should not contain a live write mode in V1. Suggested command:

```bash
PYTHONPATH=. python3 scripts/integrations/ghl_yaml_subaccount_sync.py \
  --manifest docs/handoffs/ghl_location_manifest.example.tsv \
  --current-state-fixture tests/fixtures/ghl/current_state_one_location.json \
  --output artifacts/ghl/yaml_subaccount_sync_20260715/dry_run_diff.json
```

Required tests:

- Active brand classifier discovers only valid wizard YAMLs.
- GHL-enabled registry rows without active YAML become `blocked_missing_active_yaml`.
- Duplicate manifest rows become `blocked_duplicate_mapping`.
- Webhook env names are allowed but webhook URL values are redacted/blocked.
- Forbidden fields such as secrets, billing, users, permissions, contacts, phone numbers, and workflows fail closed.
- Matching fixture current state returns `no_op`.
- Different Phoenix-owned custom value returns `update` in dry-run output only.

## Blocker

Lane 02 is not merged and the repo's required Core tests are non-terminal on PR #5686. Lane 03 is blocked for missing operator credential/sandbox location. This lane therefore lands a precise dry-run proof shape and implementation handoff, not code.
