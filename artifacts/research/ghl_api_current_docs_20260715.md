# GHL API Current Docs Research - 2026-07-15

PROVENANCE
research=official HighLevel docs checked 2026-07-15: https://help.gohighlevel.com/support/solutions/articles/48001060529-highlevel-api-documentation (modified Fri, 19 Jun 2026 05:16); https://marketplace.gohighlevel.com/docs/; https://marketplace.gohighlevel.com/docs/Authorization/PrivateIntegrationsToken/; https://marketplace.gohighlevel.com/docs/Authorization/Scopes/; https://marketplace.gohighlevel.com/docs/ghl/locations/search-locations/; https://marketplace.gohighlevel.com/docs/ghl/locations/get-location/; https://marketplace.gohighlevel.com/docs/ghl/locations/put-location/index.html; https://marketplace.gohighlevel.com/docs/ghl/locations/create-location/; https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-values/; https://marketplace.gohighlevel.com/docs/ghl/locations/update-custom-value/; https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-fields/; https://marketplace.gohighlevel.com/docs/ghl/locations/update-custom-field/
documents=docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md; docs/INTEGRATION_CREDENTIALS_REGISTRY.md; skills/pearl-int/SKILL.md; skills/pearl-int/references/integration_registry.md; docs/GHL_INTEGRATION_GUIDE.md; docs/handoffs/GHL_AGENCY_SCALE_PLAYBOOK.md; docs/handoffs/GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md
builds_on=existing GHL feed/freebie integration docs; Pearl_Int credential registry
inventory=EXTENDS existing GHL integration knowledge; does not reduce feed/webhook behavior

## Executive Decision

Use OAuth 2.0 as the recommended auth model for a 37 sub-account/location program unless Pearl_Int proves an agency-level Private Integration Token has the exact required scopes and can access all intended locations. A Private Integration Token is acceptable for internal or single-account validation, but it is static, manually rotated, and must be scope-limited. Legacy `GHL_API_KEY` remains a legacy funnel lead-capture credential only and must not be used as proof for the YAML-to-GHL sync path.

No live writes are authorized by this research. Sub-account creation is blocked unless Agency Pro eligibility, create endpoint scope, and explicit operator create approval are all proven.

## Official Facts Re-Verified

| Topic | Current official fact | Safety impact |
|---|---|---|
| API documentation home | HighLevel points developers to `https://marketplace.gohighlevel.com/docs/` and says docs are versioned. The marketplace UI currently exposes `v3`, `2023-02-21`, `2021-07-28`, and `2021-04-15` selectors. | Every implementation must cite the selected doc version and send the required `Version` header where endpoint examples require it. |
| V1 status | The support article says V1 reached end-of-support on 2025-12-31; existing integrations may continue but receive no support or updates. | `GHL_API_KEY` / old Contacts API assumptions cannot be used for new sub-account sync. |
| API key generation | HighLevel says new API key generation will be removed for accounts that have not generated or are not using an API key. | Do not design new sync around legacy keys. |
| Auth methods | HighLevel lists Private Integration Tokens and OAuth 2.0. Private Integration Tokens are available for agencies and sub-accounts, are scoped, and are used as Bearer tokens. | Token setup must be Pearl_Int/operator assisted and least-scope. |
| Private token lifecycle | Private Integration Tokens are static/fixed OAuth2-style access tokens, do not auto-refresh, and HighLevel recommends rotation every 90 days. | Batch tooling needs token-rotation/expiry handling and no token in git/logs. |
| Multi-account guidance | The support article recommends OAuth 2.0 for multiple locations/accounts and secure user-approved access; Private Integration Tokens are best for internal or single-account use cases. | Default scale model is OAuth. A single token for all 37 locations is not assumed. |
| Rate limits | Public V2 OAuth docs state 100 requests per 10 seconds per client/resource and 200,000 requests per day per client/resource, with `X-RateLimit-*` response headers. | Ramp should be 1 -> 3 -> 10 -> remaining, with backoff and stop-on-429. |
| Plan constraints | Support docs say Agency Pro unlocks advanced API access including OAuth and agency-level tokens. The create location endpoint says `POST /locations/` is only available on Agency Pro ($497) plan. | Create operations are blocked by default. |
| Support limits | HighLevel Support does not provide hands-on API build/debug review. | Phoenix must rely on official docs, readback, and fail-closed probes. |

## Relevant Endpoint Family

All endpoints below are from the official marketplace docs current `v3` navigation observed on 2026-07-15. The visible pages did not expose full request schemas in the text fetch, so payload details remain implementation-time verified from the interactive docs/portal before write code or live writes.

| Operation | Endpoint | Risk | Minimum guidance |
|---|---|---|---|
| Search locations/sub-accounts | `GET /locations/search` | Read-only | First candidate for agency-scope read-only credential validation if scopes allow it. |
| Get one location | `GET /locations/:locationId` | Read-only | Safest validation when operator supplies a known test/sandbox location id. |
| Update location | `PUT /locations/:locationId` | Write | Do not use for pilot unless the exact field is allowlisted and readback-safe. Prefer custom value sync marker first. |
| Create location | `POST /locations/` | High write / billing-plan gated | Blocked until Agency Pro, scopes, payload, and explicit create approval are proven. |
| Get custom values | `GET /locations/:locationId/customValues` | Read-only | Preferred pilot readback surface for Phoenix-owned sync-marker values. |
| Update custom value | `PUT /locations/:locationId/customValues/:id` | Write | Candidate one-field pilot only after lane 02/06 approve the field and lane 04 dry-run proves desired state. |
| Get custom fields | `GET /locations/:locationId/customFields` | Read-only | Required before any contact/custom-field mapping; do not touch contact PII in this program. |
| Update custom field | `PUT /locations/:locationId/customFields/:id` | Write | Higher risk than custom values; block unless field is Phoenix-owned and schema is proven. |

## Stale Assumptions Table

| Phoenix assumption/source | Current assessment | Required correction |
|---|---|---|
| `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` section 8 lists `GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CONTACTS_URL` from dashboard API keys for funnel capture. | Still valid only as historical/freebie funnel context if the existing integration still works. It is not a basis for new V2/V3 sub-account sync. | Keep legacy vars for existing funnel lead capture, but add separate V2/OAuth/PIT env names only after Pearl_Int proves the model. |
| Existing funnel/webhook docs center contacts and inbound capture. | This prompt pack is about sub-account/location desired-state sync, custom values, and field maps. | Extend docs; do not reduce feed/webhook behavior. |
| Any single GHL token can update all 37 locations. | Not proven. Official docs steer multi-location access toward OAuth; Private Integration Tokens can be agency or sub-account but access breadth must be portal/API proven. | Lane 03 must prove search/get access across intended locations or block scale. |
| Create sub-account can be part of deterministic sync. | Official create endpoint is Agency Pro gated and high-risk. | Update-only by default; create requires separate operator approval and plan/scope proof. |
| API version can be implicit. | Docs are versioned and examples include a `Version` header for Private Integration Token calls. | CLI/config must carry endpoint version/header as explicit desired-state metadata. |

## Recommended Auth And Scope Proof

1. Smoke: no secrets; inspect `.env`, `.gitignore`, `.env.example`, credential registry, and Keychain loader patterns.
2. Operator-assisted credential setup: prefer OAuth app/install path for the 37-location program. If the operator instead supplies a Private Integration Token, record whether it is agency-level or sub-account-level, its scopes by name only, and its rotation date. Never print the token.
3. Read-only proof: run at most `GET /locations/search` or `GET /locations/:locationId`, then `GET /locations/:locationId/customValues` and `GET /locations/:locationId/customFields` for one operator-selected or sandbox location. Record only endpoint names, status codes, redacted location id hash, and rate-limit headers.
4. Write proof: no write before lanes 02, 04, 06 and the exact operator phrase `OPERATOR_GHL_LIVE_PILOT_APPROVED`.

## Smoke -> Pilot -> Scale Guidance

Smoke: official docs only, no API calls, no credentials, no live writes. This lane completed that stage.

Pilot: one operator-selected sub-account. Before snapshot, dry-run diff, one Phoenix-owned custom value update, readback, dry-run no-op proof, rollback notes.

Scale: 1 -> 3 -> 10 -> remaining 37. Stop the batch on 401/403, 422 schema error, mismatched location id, missing Phoenix-owned field, unexpected diff, readback mismatch, duplicate mapping, 429/rate-limit exhaustion, or operator stop.

## Open Blocks For Later Lanes

- Full request payload schemas were not visible in the text fetch and must be verified in the interactive official docs immediately before implementing any write body.
- Actual account plan, OAuth app availability, Private Integration Token scope breadth, and location access are unknown until Pearl_Int/operator credential proof.
- Current repo state has only one known checked-in active brand YAML according to the prompt pack; lane 04 must re-derive that from `origin/main`.
