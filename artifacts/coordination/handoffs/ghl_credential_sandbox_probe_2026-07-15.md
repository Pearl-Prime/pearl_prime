# GHL Credential + Sandbox Read-Only Probe — 2026-07-15

PROVENANCE
research=artifacts/research/ghl_api_current_docs_20260715.md (PR #5686, merge 49374307a56d3129eb4400289e6cfc33853a9e24); official HighLevel docs re-fetched 2026-07-15 for verbatim scope names and portal path: https://marketplace.gohighlevel.com/docs/Authorization/Scopes/, https://marketplace.gohighlevel.com/docs/Authorization/PrivateIntegrationsToken/
documents=docs/specs/GHL_YAML_SUBACCOUNT_SYNC_V1_SPEC.md (PR #5687); artifacts/qa/ghl_credential_scope_probe_20260715/README.md (PR #5688); docs/ghl/GHL_YAML_SYNC_FIELD_MAP.md (PR #5690); docs/INTEGRATION_CREDENTIALS_REGISTRY.md; skills/pearl-int/references/credential_staging_files.md; scripts/ci/load_integration_env_from_keychain.py; scripts/ci/integration_env_registry.py
builds_on=PR #5688 credential scope probe blocker (which named the block but not the exact scopes, portal path, env var names, or staging command)
inventory=EXTENDS the GHL credential model with three registered V2 env var names + exact operator setup steps; removes nothing; legacy funnel/webhook vars untouched

## Result

Status: **BLOCKED** — no GHL API credential exists to probe with.
AUTH_MODEL=blocked. LIVE_WRITES=none. No API call was made. No credential was requested, copied, staged, or validated.

This is the expected and correct outcome. PR #5688 already established the block. This lane's contribution is to make the block **durable and actionable**: exact scope names, exact portal path, registered env var names the Keychain loader will actually read, and the exact staging command the operator runs themselves.

## 1. Credential Absence — Independently Verified

Re-verified 2026-07-15 against `origin/main` @ `5472f4a517345ec9fbfc158f1562efd3667a9a26`.

```bash
python3 scripts/ci/load_integration_env_from_keychain.py --count   # -> 100 tracked names
python3 scripts/ci/load_integration_env_from_keychain.py --list | grep -i ghl
```

Seven GHL-family names are tracked in the registry. Direct per-name Keychain existence probe
(`security find-generic-password -s phoenix-omega -a <NAME>`, exit code only — value never read):

| Keychain account name (service=`phoenix-omega`) | Present | Usable for a location read? |
|---|---|---|
| `GHL_API_KEY` | NO | No — legacy V1, end-of-support 2025-12-31 (#5686) |
| `GHL_LOCATION_ID` | NO | No — not a credential |
| `GHL_CONTACTS_URL` | NO | No — not a credential |
| `PHOENIX_GHL_FUNNEL_WEBHOOK` | NO | No — inbound trigger URL, not an API credential |
| `PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS` | NO | No — same |
| `PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION` | NO | No — same |
| `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM` | **YES** | **No** — inbound funnel webhook trigger URL. It authenticates nothing and cannot perform `GET /locations/{id}`. |

`GHL_API_KEY`, `GHL_LOCATION_ID`, `GHL_CONTACTS_URL` are also unset in the environment.

**Conclusion:** exactly one GHL-family secret exists, and it is an inbound webhook trigger URL — the wrong
shape of thing entirely. There is no bearer credential to probe with. The lane is blocked at the credential,
not at the code.

## 2. Auth Model Required (cited)

Per `artifacts/research/ghl_api_current_docs_20260715.md` (#5686):

- **OAuth 2.0 is the recommended model at 37-location scale.** The support article steers multi-location
  access to OAuth; Agency Pro unlocks OAuth and agency-level tokens.
- **A Private Integration Token (PIT) is acceptable for internal/single-account validation** — which is
  exactly the shape of this lane's read-only probe. PIT is a static OAuth2-style bearer token, does not
  auto-refresh, and HighLevel recommends 90-day rotation.
- **Legacy `GHL_API_KEY` must not be used** as proof for the YAML sub-account sync path (#5686 stale-assumptions
  table; #5687 §auth: "Legacy `GHL_API_KEY` is not accepted for this sync path").

**Ruling for this lane:** the minimum credible unblock is a **read-only Private Integration Token scoped to one
sandbox location**. That satisfies the read-only probe without provisioning an OAuth app. OAuth remains the
scale model and is lane 06/07's problem, not a prerequisite for this probe.

## 3. Scopes Required for a Read-Only Location Read

Verbatim scope identifiers, confirmed 2026-07-15 against the official scopes doc cited by #5686:

| Endpoint (#5686 endpoint family) | Required scope (verbatim) |
|---|---|
| `GET /locations/{locationId}` | `locations.readonly` |
| `GET /locations/{locationId}/customValues` | `locations/customValues.readonly` |
| `GET /locations/{locationId}/customFields` | `locations/customFields.readonly` |

These three read-only scopes are the complete set for the probe in #5688 §"Read-Only Probe To Run After Unblock".
Tick **nothing else**. In particular do NOT tick any `.write` scope — no write scope is needed, and granting one
would put a live-write capability behind a token this lane has declared read-only.

`GET /locations/search` (agency-scope discovery) is deliberately **excluded** from the smoke step: it requires
agency-level breadth that a sandbox-scoped PIT will not have, and #5686 flags that breadth as unproven. Scale
breadth is proven later, not at smoke.

Required request headers (per the official Private Integration Token doc):

```
Authorization: Bearer <token>
Version: 2021-07-28
Accept: application/json
```

## 4. OPERATOR SETUP STEPS

> **The operator runs every step below themselves. Pearl_Int never sees the token value.
> Do not paste the token into chat, a PR, an artifact, a screenshot, or a log.**

### Step 1 — Create a read-only Private Integration Token

1. Portal URL: **https://app.gohighlevel.com/**
2. Select the **sandbox / test sub-account** to scope the token to. Do **not** select a production location.
   (If no sandbox location exists, stop and tell Pearl_PM — creating one is `POST /locations/`, which is
   Agency-Pro-gated and blocked by #5686. Do not create a sub-account to unblock this lane.)
3. Menu path: **Settings → Private Integrations → Create new Integration**
   - If *Private Integrations* is not visible under Settings, enable it under **Settings → Labs** first.
4. Name it something traceable, e.g. `phoenix-omega-readonly-probe`.
5. Tick **exactly these three scopes and no others**:
   - `locations.readonly`
   - `locations/customValues.readonly`
   - `locations/customFields.readonly`
6. Create. **The token is shown once.** Keep the tab open until Step 2 succeeds.

### Step 2 — Stage the token in Keychain (operator runs this; value is never typed into chat)

Run in a local terminal. The `-w` flag is given **with no value**, so `security` prompts for the token on a
hidden line — this keeps it out of shell history and out of the process argument list:

```bash
security add-generic-password -s phoenix-omega -a GHL_PRIVATE_INTEGRATION_TOKEN -w -U
# -> paste the token at the "password data for new item:" prompt, then press Return
```

Then stage the sandbox location id and the API version (these two are not secret, but are staged the same way
so the loader picks them up):

```bash
security add-generic-password -s phoenix-omega -a GHL_SANDBOX_LOCATION_ID -w -U
security add-generic-password -s phoenix-omega -a GHL_API_VERSION       -w -U   # value: 2021-07-28
```

The sandbox location id is at **Settings → Business Profile** of the sandbox sub-account, or in the URL when
that sub-account is open.

### Step 3 — Verify staging worked (safe; prints names only, never values)

```bash
python3 scripts/ci/load_integration_env_from_keychain.py --list | grep -i ghl
for a in GHL_PRIVATE_INTEGRATION_TOKEN GHL_SANDBOX_LOCATION_ID GHL_API_VERSION; do
  security find-generic-password -s phoenix-omega -a "$a" >/dev/null 2>&1 \
    && echo "PRESENT: $a" || echo "ABSENT : $a"
done
```

Three `PRESENT` lines means the lane is unblocked. Reply to Pearl_Int with **only** the word `staged` — never
the token.

> **Do NOT run `load_integration_env_from_keychain.py --verbose`** and paste the result anywhere. `--verbose`
> emits `export NAME=<value>` lines containing real secret values. See §6.

## 5. Exact Env Var Names (now registered)

Added to `scripts/ci/integration_env_registry.py` in this PR, so
`eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"` exports them automatically:

| Keychain account name | Purpose | Secret? |
|---|---|---|
| `GHL_PRIVATE_INTEGRATION_TOKEN` | V2 PIT bearer token, read-only scopes | **Yes** |
| `GHL_SANDBOX_LOCATION_ID` | Operator-selected sandbox location id | No |
| `GHL_API_VERSION` | `Version` header value (`2021-07-28`) | No |

Keychain convention is **`-s phoenix-omega -a <ENV_VAR_NAME>`** — service is the constant, account is the
variable name. This is the only shape `load_integration_env_from_keychain.py:keychain_get()` reads.

## 6. Two Defects Found While Verifying (both need operator action)

### 6a. ROTATE: `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM` value reached an agent transcript

While verifying credential absence, Pearl_Int ran
`python3 scripts/ci/load_integration_env_from_keychain.py --verbose`. That flag emits `export NAME=<value>`
for every **present** Keychain item, so the live Waystream funnel webhook URL was written to the agent session
transcript. The value was **not** committed, and is **not** reproduced in this handoff or anywhere in this PR.

Per #5688 ("If a token enters chat or logs, rotate it before use") this warrants rotation:

1. GHL → **Automation → Inbound Webhook trigger** for the Waystream funnel → regenerate the trigger URL.
2. Re-stage: `security add-generic-password -s phoenix-omega -a PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM -w -U`
3. Update the `PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM` GitHub Actions secret if set.

Severity is low — an inbound webhook trigger URL accepts lead payloads but reads nothing back and grants no
account access. It is not an API credential. But it is a live secret URL and rotation is cheap.

**Mechanism fix, not just a note:** `--verbose` is a foot-gun that prints secret values to stderr while
advertising itself as a diagnostic. Flagged for a follow-up to redact values under `--verbose`.

### 6b. Inverted `add-generic-password` convention in existing docs

Several repo docs show `security add-generic-password -a "$USER" -s <VARNAME> -w <value>` — service and account
**swapped**. A credential staged that way is invisible to `load_integration_env_from_keychain.py`, which reads
`-s phoenix-omega -a <VARNAME>`. An operator following those docs would stage a token successfully and still
see the loader report it missing. Flagged for a follow-up doc sweep; the correct shape is in §4 above.

## 7. What Happens After Unblock

Pearl_Int re-runs this lane and executes, read-only, with two retries and a 30s timeout:

1. `GET /locations/{GHL_SANDBOX_LOCATION_ID}` → expect 200
2. `GET /locations/{GHL_SANDBOX_LOCATION_ID}/customValues` → expect 200
3. `GET /locations/{GHL_SANDBOX_LOCATION_ID}/customFields` → expect 200

Recorded proof: endpoint names, status codes, `X-RateLimit-*` headers, scope names, and a **hashed** location id.
No response bodies (they may contain PII). No PUT/POST/PATCH/DELETE. Stop on 401/403/429.

Scale breadth (can one token reach multiple locations?) is a **separate** question and stays blocked until a
read-only `GET /locations/search` is authorized at agency scope — see #5686 lane-03 note.

## 8. Cleanup Ledger

| Item | State |
|---|---|
| Keychain items created | **none** — Pearl_Int staged nothing; §4 is for the operator to run |
| Credential values printed/committed | none in this PR; see §6a for the one transcript leak, rotation requested |
| Staging files created | none — `config/local/ghl_funnel_webhook.url` untouched |
| GHL API calls | **none** |
| Live writes | **none** |
| Sub-accounts created | **none** |
| Browser/portal session | none opened; official public docs fetched read-only |
| Worktree | `/tmp/wt-ghl-cred` removed; `git worktree prune` run |
| Branch | `agent/ghl-credential-probe-20260715` (this PR) |
| Scratch files | session scratchpad only; nothing persisted to the repo |
| Background jobs | none left running |

## 9. Next Action

**Operator:** run §4 Steps 1–3 (~10 minutes), then reply `staged`. Separately, rotate the Waystream funnel
webhook per §6a.

Until then this lane stays BLOCKED and lanes 06/07 must not claim any GHL auth proof.
