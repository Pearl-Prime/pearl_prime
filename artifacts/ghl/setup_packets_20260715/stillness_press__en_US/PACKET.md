# GHL Setup Packet — Stillness Press (en_US)

- readiness: **BLOCKED**
- live_writes: **none** (this packet authorizes no GHL write)
- generated_at: 2026-07-15T00:00:00Z
- field_map_version: GHL_YAML_SUBACCOUNT_SYNC_V1

## Blockers (fail-closed)

- blocked_missing_active_yaml: no brand-wizard-app/brands/stillness_press.yaml on this checkout
- blocked_missing_location_mapping: manifest row has no location_id
- blocked_manifest_missing_scale_columns: location_id, phoenix_managed_custom_value_ids, last_readback_at, last_sync_sha, rollback_note

## Brand

- brand_id: `stillness_press`
- locale: `en_US`
- display_name: Stillness Press
- wizard YAML: `ABSENT` (classifier-active: False)
- wizard inactive reason: no brand_wizard YAML found
- rollout_phase: pilot | ghl_enabled: True

## Admin / Person

- brand director: _unresolved_ (`-`)
- status: _unresolved_
- action: Review this packet, then confirm/return the GHL location_id. Phoenix never creates sub-accounts.

## GHL Target

- location_id: `UNMAPPED` (redacted)
- location_name: Stillness Press (en_US)
- policy: update-only; missing sub-account is blocked, never created (spec: Missing Sub-Account Policy)

## Webhook

- env NAME: `PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS`
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
| weekly_marketing_feed | r2_public_json | https://pub-4bac5d0b30be4b16824cd1eaa84ae9f5.r2.dev/pearl-prime-content/stillness_press/en_US/2026-W26/marketing_feed.json | resolved |
| freebie_funnel_pages | cloudflare_pages | https://brand-admin-onboarding.pages.dev/free/ | resolved |
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
| anxiety | `anxiety-nervous-system-reset` | https://brand-admin-onboarding.pages.dev/free/anxiety-nervous-system-reset/ | `breath_timer_interactive` |
| compassion_fatigue | `compassion-fatigue-audit` | https://brand-admin-onboarding.pages.dev/free/compassion-fatigue-audit/ | `capacity_assessment` |
| overthinking | `overthinking-thought-sorter` | https://brand-admin-onboarding.pages.dev/free/overthinking-thought-sorter/ | `thought_sorter_assessment` |
| financial_anxiety | `financial-anxiety-check-in` | https://brand-admin-onboarding.pages.dev/free/financial-anxiety-check-in/ | `financial_checkin` |
| courage | `courage-decision-map` | https://brand-admin-onboarding.pages.dev/free/courage-decision-map/ | `decision_resistance_map` |
| burnout | `burnout-energy-audit` | https://brand-admin-onboarding.pages.dev/free/burnout-energy-audit/ | `capacity_assessment` |
| self_worth | `self-worth-inventory` | https://brand-admin-onboarding.pages.dev/free/self-worth-inventory/ | `worth_inventory` |
| imposter_syndrome | `imposter-evidence-log` | https://brand-admin-onboarding.pages.dev/free/imposter-evidence-log/ | `evidence_log` |
| boundaries | `boundaries-script-kit` | https://brand-admin-onboarding.pages.dev/free/boundaries-script-kit/ | `script_practice` |
| depression | `depression-momentum-kit` | https://brand-admin-onboarding.pages.dev/free/depression-momentum-kit/ | `micro_action_kit` |
| social_anxiety | `social-anxiety-toolkit` | https://brand-admin-onboarding.pages.dev/free/social-anxiety-toolkit/ | `pre_event_protocol` |
| financial_stress | `financial-stress-audit` | https://brand-admin-onboarding.pages.dev/free/financial-stress-audit/ | `financial_stress_audit` |
| sleep_anxiety | `sleep-anxiety-wind-down` | https://brand-admin-onboarding.pages.dev/free/sleep-anxiety-wind-down/ | `wind_down_breath` |
| somatic_healing | `somatic-body-scan` | https://brand-admin-onboarding.pages.dev/free/somatic-body-scan/ | `body_scan_timer` |
| grief | `grief-letter-template` | https://brand-admin-onboarding.pages.dev/free/grief-letter-template/ | `grief_letter_template` |

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
