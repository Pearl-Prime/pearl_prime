# GHL YAML Sub-Account Sync V1 Spec

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md from PR #5686 (blocked by non-terminal Core tests, official-doc facts captured)
documents=docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md; docs/GHL_INTEGRATION_GUIDE.md; docs/handoffs/GHL_AGENCY_SCALE_PLAYBOOK.md; docs/handoffs/GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md; docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md; config/marketing/brand_marketing_registry.yaml; docs/handoffs/ghl_location_manifest.example.tsv; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; skills/pearl-int/SKILL.md
builds_on=brand-wizard YAML SSOT; brand_marketing_registry; existing GHL feed/freebie docs
inventory=EXTENDS active-brand and GHL admin systems; no reduction of current feed/webhook behavior

## Status

V1 contract for deterministic, dry-run-first updates from Phoenix brand wizard YAML and marketing registries into GoHighLevel/HighLevel sub-accounts. This spec does not authorize live writes. It defines the allowlist, stop conditions, provenance, and pilot/scale gates.

## Source Eligibility

Eligible YAML source files are only files under `brand-wizard-app/brands/*.yaml` that pass `scripts/brand/active_brand_classifier.py` according to `ACTIVE_BRAND_SSOT_V1_SPEC`. The sync engine must re-derive eligibility from the live checkout/commit it runs against and must not assume the 37-brand universe has YAML files.

As of `origin/main` SHA `8956e2222592fcc9105e4972479cd6c1f989c6bd`, the only checked-in wizard YAML is `brand-wizard-app/brands/stabilizer_en_us.yaml`. Current GHL pilot registry rows are `stillness_press`, `devotion_path`, and `way_stream_sanctuary`, so a dry-run must be able to report `blocked_missing_active_yaml` when a GHL-enabled row has no active wizard YAML.

## Target Mapping Inputs

The sync joins these read-only inputs:

| Input | Purpose |
|---|---|
| Active brand wizard YAML | Brand identity source fields. |
| `config/marketing/brand_marketing_registry.yaml` | GHL-enabled brand rows, locale default, funnel path prefix, webhook env name, shop base, rollout phase. |
| `docs/handoffs/ghl_location_manifest.example.tsv` or future manifest | Human-reviewed mapping from Phoenix brand/locale to GHL location id, feed URL, funnel base URL, and webhook env name. |
| Read-only GHL snapshot fixture/API response | Current custom values/fields/settings for diff comparison. |

A target row is syncable only when exactly one active wizard YAML, exactly one marketing registry row, and exactly one manifest row resolve to the same `brand_id` + `locale` + GHL `location_id`. Missing or duplicate mapping is `blocked`, not create.

## Field Policy

Allowlist-only. Missing fields never delete GHL values in V1.

| Phoenix source | GHL target | Policy | Notes |
|---|---|---|---|
| `brand_id` | custom value `phoenix_brand_id` | `phoenix_managed` | Immutable after pilot unless operator approves migration. |
| `display_name` | custom value `phoenix_brand_display_name` | `phoenix_managed` with review | Useful in workflows; do not overwrite manual public brand naming if mismatch. |
| `wizard_core.tagline` | custom value `phoenix_brand_tagline` | `operator_approval_required` | Brand identity/taste sensitive. Dry-run may show diff; live update needs operator approval. |
| `wizard_core.positioning_line` | custom value `phoenix_positioning_line` | `operator_approval_required` | Brand identity/taste sensitive. |
| registry `locale` | custom value `phoenix_locale` | `phoenix_managed` | Must match manifest locale. |
| manifest `feed_url` | custom value `phoenix_feed_url` | `phoenix_managed` | Required for proof-loop feed wiring; redact signed URLs if ever present. |
| manifest `funnel_base_url` | custom value `phoenix_funnel_base_url` | `phoenix_managed` | Public URL only. |
| registry `webhook_env` | Phoenix-only manifest | `phoenix_only` | Env var name may be stored; webhook URL value must never sync or print. |
| sync commit SHA | custom value `phoenix_last_sync_sha` | `phoenix_managed` | Preferred one-field pilot candidate. |
| sync timestamp | custom value `phoenix_last_sync_at` | `phoenix_managed` | Low-risk audit field. |
| rollout phase | custom value `phoenix_rollout_phase` | `manual_ghl_admin` or dry-run only | Avoid changing live workflow behavior without review. |
| topics/freebie slugs | Phoenix feed JSON only | `phoenix_only` | Existing feed/webhook behavior remains authority. |
| contacts/customers/lead data | none | `blocked` | PII is out of scope. |
| secrets/API keys/OAuth tokens/webhook URLs/billing/users/permissions | none | `blocked` | Never sync from YAML or manifests. |

## Object Ownership

V1 writes only Phoenix-prefixed custom values after gates are satisfied. It must not update workflows, automations, funnels, email sender settings, phone numbers, billing, users, permissions, or contact records. Custom fields are read-only in V1 except a later spec may define Phoenix-owned field creation after explicit approval.

## Diff Semantics

Every run produces a desired-state diff with one decision per field:

- `no_op`: current GHL value matches desired value.
- `update`: target exists, is Phoenix-owned, and value differs.
- `create`: target Phoenix-prefixed custom value is missing, but create is only proposed; live creation requires lane 05 approval.
- `blocked`: missing YAML, inactive YAML, duplicate manifest row, mismatched location id, forbidden field, missing target id, non-Phoenix-owned target, credential/scope failure, or unexpected current value ownership.

The diff records source YAML path, source blob SHA, source commit SHA, manifest row id, field map version, generated timestamp, target location id hash/redaction, before/after redacted values, and rollback/no-op notes.

## Missing Sub-Account Policy

Update-only by default. If the GHL sub-account/location is missing, the decision is `blocked_missing_location_mapping` or `blocked_location_not_found`. Creating sub-accounts is out of scope until Agency Pro eligibility, create endpoint scopes, exact payload, and explicit operator create approval are all proven.

## Pilot And Scale Gates

Smoke: dry-run one checked-in active YAML against a fixture; no API calls; output JSON and human table.

Pilot: one operator-selected sandbox/test location. Required sequence: before snapshot, dry-run diff, one Phoenix-owned low-risk custom value update (`phoenix_last_sync_sha` preferred), readback, second dry-run no-op proof, rollback notes.

Scale: 1 -> 3 -> 10 -> remaining 37. Stop the batch on 401/403, 422, 429/rate-limit exhaustion, missing or duplicate mapping, mismatched location id, missing active YAML, missing custom value id, unexpected diff, failed readback, or operator stop.

## Auth Contract

OAuth is the recommended auth model for 37-location scale. Private Integration Token can be used only after Pearl_Int proves its scope and location breadth with read-only calls. Legacy `GHL_API_KEY` is not accepted for this sync path.
