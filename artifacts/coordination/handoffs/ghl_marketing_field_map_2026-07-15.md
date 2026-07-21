# GHL Marketing Field Map Handoff - 2026-07-15

CLOSEOUT_RECEIPT
AGENT=Pearl_Marketing
LANE=06_ghl_content_fields_workflows
STATUS=BLOCKED
PR=https://github.com/Ahjan108/phoenix_omega_v4.8/pull/TBD
MERGE_SHA=none
FIELD_MAP_PATH=docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md
PILOT_FIELDS=phoenix_last_sync_sha; phoenix_last_sync_at fallback
BLOCKED_FIELDS=contacts/customer PII; secrets/API keys/OAuth tokens/webhook URLs; billing; users; permissions; phone numbers; sender settings; workflows/automations/funnels; brand identity fields without operator approval
SCALE_COLUMNS=location_id;location_name;brand_id;locale;display_name;feed_url;funnel_base_url;webhook_env;shop_cta_style;rollout_phase;ghl_enabled;phoenix_managed_custom_value_ids;last_readback_at;last_sync_sha;rollback_note
LIVE_WRITES=none
CLEANUP=plumbing branch, no physical worktree; scratch /tmp/ghl_lane06 removed after push; no background jobs; no credentials touched
HANDOFF=artifacts/coordination/handoffs/ghl_marketing_field_map_2026-07-15.md
SIGNAL=ghl-marketing-field-map=BLOCKED
NEXT_ACTION=Merge the docs field map after CI recovers, then use it to constrain lane 04 implementation and any future lane 05 pilot.

## Blocker

The field map is authored and pushed, but lane 01/02 are not merged because Core tests are non-terminal. This lane therefore lands as BLOCKED with pushed docs proof.
