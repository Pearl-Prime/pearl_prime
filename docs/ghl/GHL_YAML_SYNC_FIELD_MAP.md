# GHL YAML Sync Field Map

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md from PR #5686
documents=docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md from PR #5687; docs/GHL_INTEGRATION_GUIDE.md; docs/handoffs/GHL_AGENCY_SCALE_PLAYBOOK.md; docs/handoffs/GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md; docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md; docs/ghl/PROOF_LOOP_WORKFLOW_TEMPLATE.md; config/marketing/brand_marketing_registry.yaml; docs/handoffs/ghl_location_manifest.example.tsv
builds_on=existing GHL weekly feed, freebie funnel capture, brand marketing registry
inventory=EXTENDS marketing field map; no reduction of proof-loop behavior

## Purpose

This map defines which Phoenix brand and marketing fields may appear in GoHighLevel sub-accounts during the YAML sync program. It does not change the existing feed/webhook workflow and does not authorize live writes.

## Safety Classes

| Class | Meaning |
|---|---|
| `phoenix_managed` | May be updated by the future dry-run/live pilot only when target custom value is Phoenix-prefixed and readback is proven. |
| `manual_ghl_admin` | GHL admin/operator manages this in workflows or UI; Phoenix may document but not overwrite. |
| `operator_approval_required` | Dry-run may show a proposed diff; live write needs explicit operator approval because it affects brand identity/taste/legal posture. |
| `blocked` | Must not sync to GHL in V1. |
| `phoenix_only` | Remains in Phoenix feed/manifests/social planners, not GHL custom values. |

## Custom Values And Workflow Merge Tags

| Field | Source | GHL representation | Safety class | Notes |
|---|---|---|---|---|
| `phoenix_brand_id` | wizard `brand_id` / registry key | Custom value | `phoenix_managed` | Must match manifest row. |
| `phoenix_brand_display_name` | wizard `display_name` or registry `display_name` | Custom value / merge tag | `operator_approval_required` | Prefer registry display name when GHL pilot row already exists. |
| `phoenix_locale` | registry/manifest locale | Custom value | `phoenix_managed` | V1 pilot is `en_US`. |
| `phoenix_feed_url` | manifest `feed_url` | Custom value / workflow feed connector | `phoenix_managed` | Public stable URL only; no presigned URLs. |
| `phoenix_funnel_base_url` | manifest `funnel_base_url` | Custom value | `phoenix_managed` | Public Cloudflare Pages URL. |
| `phoenix_shop_cta_style` | manifest `shop_cta_style` | Custom value | `manual_ghl_admin` | May affect offer routing; dry-run only until operator approves. |
| `phoenix_rollout_phase` | registry/manifest `rollout_phase` | Custom value | `manual_ghl_admin` | Useful for audit, not automation switching in V1. |
| `phoenix_last_sync_sha` | sync engine | Custom value | `phoenix_managed` | Preferred one-field live pilot target. |
| `phoenix_last_sync_at` | sync engine | Custom value | `phoenix_managed` | Low-risk audit target. |
| `phoenix_brand_tagline` | wizard `wizard_core.tagline` | Custom value | `operator_approval_required` | Brand identity copy. |
| `phoenix_positioning_line` | wizard `wizard_core.positioning_line` | Custom value | `operator_approval_required` | Brand identity copy. |
| `webhook_env` | registry/manifest | Phoenix-only manifest | `phoenix_only` | Env var name is okay; webhook URL value is blocked/secret-like. |
| `cta_url`, `pricing`, `content_type`, `email_slot`, `title`, `topic` | weekly `marketing_feed.json` | Existing feed connector / workflow merge | `manual_ghl_admin` | Existing proof-loop behavior remains authority. Do not duplicate every feed item into GHL custom values. |
| quiz fields `email`, `first_name`, `quiz_id`, `topic`, `score`, `score_band`, `funnel_slug`, `tags` | inbound webhook payload | Existing contact/custom fields | `manual_ghl_admin` | Existing webhook mapping only; not YAML sync. |
| contacts, customer PII, purchase state | GHL/contact systems | none | `blocked` | Out of scope. |
| secrets, API keys, OAuth tokens, webhook URLs, billing, users, permissions, phone numbers, sender settings | any | none | `blocked` | Never sync or print. |

## Pilot Field Set

The first live pilot, if ever approved, should update exactly one Phoenix-owned custom value:

1. `phoenix_last_sync_sha`, preferred; or
2. `phoenix_last_sync_at`, fallback.

Do not pilot with display name, tagline, positioning, feed URL, funnel base URL, workflows, tags, or contact fields.

## Scale Manifest Columns

A 37-sub-account manifest needs these columns before scale:

`location_id`, `location_name`, `brand_id`, `locale`, `display_name`, `feed_url`, `funnel_base_url`, `webhook_env`, `shop_cta_style`, `rollout_phase`, `ghl_enabled`, `phoenix_managed_custom_value_ids`, `last_readback_at`, `last_sync_sha`, `rollback_note`.

Stop on missing active YAML, missing feed URL, missing manifest `location_id`, duplicate brand/locale, duplicate location id, missing webhook env name, missing Phoenix custom value id, or mismatch between GHL location display name and manifest row.

## Social / Visual Recipe Boundary

Operator-provided cover/social visual recipes for the 12 core topics are useful for cover generation and 48 Social planning, but they are not GHL custom values in V1. Treat them as Phoenix-only social planner metadata unless a later social-planner API spec proves a safe target.

The topic recipe structure is:

- photo metaphor
- symbol pack
- palette behavior
- layout behavior
- unique cover treatment

For GHL, only the resulting public asset URLs or feed item titles/CTAs should flow through existing feed/workflow paths. The visual recipe internals stay outside GHL to avoid bloating CRM configuration and accidentally overwriting brand taste decisions.
