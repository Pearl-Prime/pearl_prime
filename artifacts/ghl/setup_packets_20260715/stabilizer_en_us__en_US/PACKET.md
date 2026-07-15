# GHL Setup Packet — Harbor Line Books (en_US)

- readiness: **BLOCKED**
- live_writes: **none** (this packet authorizes no GHL write)
- generated_at: 2026-07-15T00:00:00Z
- field_map_version: GHL_YAML_SUBACCOUNT_SYNC_V1

## Blockers (fail-closed)

- blocked_inactive_yaml: brand_id not in classifier universe
- blocked_missing_registry_row: stabilizer_en_us absent from config/marketing/brand_marketing_registry.yaml
- blocked_missing_manifest_row: no row for stabilizer_en_us/en_US in docs/handoffs/ghl_location_manifest.example.tsv
- blocked_manifest_missing_scale_columns: location_id, phoenix_managed_custom_value_ids, last_readback_at, last_sync_sha, rollback_note
- blocked_missing_webhook_env_name: no webhook env var NAME resolved

## Brand

- brand_id: `stabilizer_en_us`
- locale: `en_US`
- display_name: Harbor Line Books
- wizard YAML: `brand-wizard-app/brands/stabilizer_en_us.yaml` (classifier-active: False)
- wizard inactive reason: brand_id not in classifier universe
- rollout_phase: _unresolved_ | ghl_enabled: False

## Admin / Person

- brand director: Kamiko Parker (`kamiko_parker`)
- status: assigned
- action: Review this packet, then confirm/return the GHL location_id. Phoenix never creates sub-accounts.

## GHL Target

- location_id: `UNMAPPED` (redacted)
- location_name: _unresolved_
- policy: update-only; missing sub-account is blocked, never created (spec: Missing Sub-Account Policy)

## Webhook

- env NAME: `UNRESOLVED`
- URL value: **never stored here** — ENV NAME ONLY. The webhook URL value is a secret-class field: never committed, never printed, never synced to a GHL custom value. Operator sets it in the deploy env.

## Custom Values (Phoenix-owned targets)

| field | safety class | source | live write allowed |
|---|---|---|---|
| `phoenix_brand_id` | phoenix_managed | `registry:brand_id` | True |
| `phoenix_brand_display_name` | operator_approval_required | `registry:display_name` | False |
| `phoenix_locale` | phoenix_managed | `registry:locale` | True |
| `phoenix_feed_url` | phoenix_managed | `manifest:feed_url` | True |
| `phoenix_funnel_base_url` | phoenix_managed | `manifest:funnel_base_url` | True |
| `phoenix_shop_cta_style` | manual_ghl_admin | `manifest:shop_cta_style` | False |
| `phoenix_rollout_phase` | manual_ghl_admin | `registry:rollout_phase` | False |
| `phoenix_last_sync_sha` | phoenix_managed | `engine:sync_sha` | True |
| `phoenix_last_sync_at` | phoenix_managed | `engine:sync_at` | True |
| `phoenix_brand_tagline` | operator_approval_required | `wizard:wizard_core.tagline` | False |
| `phoenix_positioning_line` | operator_approval_required | `wizard:wizard_core.positioning_line` | False |

Pilot field order: `phoenix_last_sync_sha`, `phoenix_last_sync_at`

## Channels

| channel | kind | target | status |
|---|---|---|---|
| weekly_marketing_feed | r2_public_json | — | unresolved_missing_manifest_row |
| freebie_funnel_pages | cloudflare_pages | — | unresolved_missing_manifest_row |
| inbound_webhook_capture | ghl_inbound_webhook | — | env_name_only |
| email_automation | ghl_workflow | — | manual_ghl_admin |
| shop | storefront | https://pearlprime.shop | resolved |

## Expected Tags

- score bands: `severity_high`, `severity_low`, `severity_medium`
- preferred format: `pref_audio`, `pref_somatic`, `pref_worksheet`
- readiness: `ready_act`, `ready_buy`, `ready_learn`
- per-topic defaults: 15 topics (see packet.json)

## Funnel / Freebie URLs

| topic | slug | url | quiz_id |
|---|---|---|---|
| anxiety | `anxiety-nervous-system-reset` | _unresolved_missing_funnel_base_url_ | `breath_timer_interactive` |
| compassion_fatigue | `compassion-fatigue-audit` | _unresolved_missing_funnel_base_url_ | `capacity_assessment` |
| overthinking | `overthinking-thought-sorter` | _unresolved_missing_funnel_base_url_ | `thought_sorter_assessment` |
| financial_anxiety | `financial-anxiety-check-in` | _unresolved_missing_funnel_base_url_ | `financial_checkin` |
| courage | `courage-decision-map` | _unresolved_missing_funnel_base_url_ | `decision_resistance_map` |
| burnout | `burnout-energy-audit` | _unresolved_missing_funnel_base_url_ | `capacity_assessment` |
| self_worth | `self-worth-inventory` | _unresolved_missing_funnel_base_url_ | `worth_inventory` |
| imposter_syndrome | `imposter-evidence-log` | _unresolved_missing_funnel_base_url_ | `evidence_log` |
| boundaries | `boundaries-script-kit` | _unresolved_missing_funnel_base_url_ | `script_practice` |
| depression | `depression-momentum-kit` | _unresolved_missing_funnel_base_url_ | `micro_action_kit` |
| social_anxiety | `social-anxiety-toolkit` | _unresolved_missing_funnel_base_url_ | `pre_event_protocol` |
| financial_stress | `financial-stress-audit` | _unresolved_missing_funnel_base_url_ | `financial_stress_audit` |
| sleep_anxiety | `sleep-anxiety-wind-down` | _unresolved_missing_funnel_base_url_ | `wind_down_breath` |
| somatic_healing | `somatic-body-scan` | _unresolved_missing_funnel_base_url_ | `body_scan_timer` |
| grief | `grief-letter-template` | _unresolved_missing_funnel_base_url_ | `grief_letter_template` |

## Sample Inbound Payload

```json
{
  "email": "sample.lead@example.invalid",
  "first_name": "Sample",
  "quiz_id": "capacity_assessment",
  "topic": "burnout",
  "score": 7,
  "score_band": "medium",
  "answers_json": "{\"q1\":\"b\",\"q2\":\"c\"}",
  "funnel_slug": "burnout-energy-audit"
}
```

Placeholder values only. No real contact data. Map JSON keys to GHL custom field UUIDs, not string ids.

> LIVE_WRITES=none. This packet is a read-only handoff; it authorizes no GHL write.
> A BLOCKED packet must not be treated as a provisioning green light.
