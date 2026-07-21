# GHL Credential Scope Probe - 2026-07-15

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md from PR #5686 (official-doc facts captured; lane blocked on non-terminal Core tests)
documents=skills/pearl-int/SKILL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; skills/pearl-int/references/integration_registry.md; skills/pearl-int/references/credential_staging_files.md; skills/pearl-int/references/ghl_freebie_inbound_webhook.md; docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md from PR #5687
builds_on=Phoenix Keychain credential pattern and existing GHL integration registry
inventory=EXTENDS GHL credential model; does not remove legacy feed/webhook vars

## Result

Status: BLOCKED.

No operator-provided OAuth install, Private Integration Token, portal session, sandbox/test location id, or permission to run read-only GHL API calls was available in this chat. No credential was requested, copied, staged, printed, loaded into Keychain, or validated.

## Auth Model Guidance

- Preferred scale model: OAuth 2.0 for the 37-location/sub-account program.
- Private Integration Token: acceptable only for internal/single-account validation or if Pearl_Int proves agency-level scope breadth with read-only calls.
- Legacy `GHL_API_KEY`: remains legacy funnel/Contacts context only and must not be assumed valid for YAML sub-account sync.

## Required Operator Next Step

Provide one of these through the safe Pearl_Int path:

1. OAuth app/install path with user-approved consent for read-only location/custom-value/custom-field scopes, or
2. A GHL Private Integration Token staged in a gitignored local file or direct Keychain entry, plus scope names and whether it is agency-level or sub-account-level, and
3. One known sandbox/test `location_id` or permission to use `GET /locations/search` for read-only discovery.

Do not paste token values into committed files, PRs, screenshots, or handoffs. If a token enters chat or logs, rotate it before use.

## Read-Only Probe To Run After Unblock

- `GET /locations/search` if agency-scope search is authorized.
- `GET /locations/:locationId` for one known sandbox/test location.
- `GET /locations/:locationId/customValues`.
- `GET /locations/:locationId/customFields`.

Record only endpoint names, status codes, non-sensitive rate-limit headers, scope names, and hashed/redacted location id. No PUT/POST/PATCH/DELETE.
