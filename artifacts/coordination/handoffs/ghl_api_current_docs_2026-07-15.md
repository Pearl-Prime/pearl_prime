# GHL API Current Docs Handoff - 2026-07-15

CLOSEOUT_RECEIPT
AGENT=Pearl_Research
LANE=01_ghl_api_current_docs
STATUS=BLOCKED
PR=https://github.com/Ahjan108/phoenix_omega_v4.8/pull/5686
MERGE_SHA=none
OFFICIAL_DOCS_CHECKED=https://help.gohighlevel.com/support/solutions/articles/48001060529-highlevel-api-documentation;https://marketplace.gohighlevel.com/docs/;https://marketplace.gohighlevel.com/docs/Authorization/PrivateIntegrationsToken/;https://marketplace.gohighlevel.com/docs/Authorization/Scopes/;https://marketplace.gohighlevel.com/docs/ghl/locations/search-locations/;https://marketplace.gohighlevel.com/docs/ghl/locations/get-location/;https://marketplace.gohighlevel.com/docs/ghl/locations/put-location/index.html;https://marketplace.gohighlevel.com/docs/ghl/locations/create-location/;https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-values/;https://marketplace.gohighlevel.com/docs/ghl/locations/update-custom-value/;https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-fields/;https://marketplace.gohighlevel.com/docs/ghl/locations/update-custom-field/
AUTH_RECOMMENDATION=OAuth for 37-location scale; PrivateIntegrationToken only for internal/single-account or agency-scope path after Pearl_Int proof
ENDPOINTS_RECOMMENDED=GET /locations/search;GET /locations/:locationId;GET /locations/:locationId/customValues;GET /locations/:locationId/customFields;PUT /locations/:locationId/customValues/:id for one approved pilot only
STALE_ASSUMPTIONS=legacy GHL_API_KEY is not proof for new sync;single token cannot be assumed to cover 37 locations;create-location is Agency Pro and explicit-approval gated;version/header cannot be implicit
CLEANUP=plumbing branch, no physical worktree retained after dispatcher merge; scratch files in /tmp/ghl_lane01 removed after commit; no background jobs; no credentials touched
HANDOFF=artifacts/coordination/handoffs/ghl_api_current_docs_2026-07-15.md
SIGNAL=ghl-api-current-docs-researched=BLOCKED
NEXT_ACTION=Use the pushed research artifact in PR #5686 as sufficient blocked docs proof for Wave 1 if dispatcher accepts external CI non-terminal blocker; otherwise wait for Core tests to finish and merge #5686.

## Notes

- No API calls were made.
- No credentials were requested, read, staged, or printed.
- Write endpoints remain blocked until lane gates and operator approval phrase are satisfied.

## Blocker

PR #5686 was opened with the official-doc research artifact and handoff. All checks except `Core tests` completed successfully; `Core tests` remained `IN_PROGRESS` with GitHub reporting logs unavailable while the job was still running. This is an external CI non-terminal blocker, not a research/content blocker.

Blocked signal for dispatcher gate: `ghl-api-current-docs-researched=BLOCKED`.
