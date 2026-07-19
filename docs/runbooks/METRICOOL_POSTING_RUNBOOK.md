# Metricool Posting Runbook (SAFE / SUPPORTED / MANAGED / DURABLE)

**Owner:** Pearl_Int  
**Subsystem:** integrations / Metricool  
**Acceptance layer:** `PROVEN-AT-BAR` for **draft** transport (`postId=351226639`,
`blog_id=6582629`) — **not** live-social (Q-METRIC-01 still open)  
**Authority:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §7b, `docs/METRICOOL_API_REFERENCE.md`

---

## What this system is

A fail-closed Metricool scheduling lane for Phoenix Omega:

| Pillar | Guarantee |
|--------|-----------|
| **SAFE** | Draft-default; live autoPublish gated (Q-METRIC-01); placeholder/null blog_ids refused; network kill-switch OFF by default; no secrets in git |
| **SUPPORTED** | This runbook + `status.py` + `pilot_preflight.py` + `doctor.py` |
| **MANAGED** | Brand map SSOT + `validate_config.py` + `sync_brands_from_registry.py` + offline tests |
| **DURABLE** | Frozen pin `metricool_waystream_pin.yaml`; CI `check_metricool_managed.py` (Drift detectors + production readiness #34); Keychain installer; sync re-applies pin |

Transport lives only in `scripts/integrations/metricool/` — do **not** fork a second client. Payload construction reuses `phoenix_v4.social.deterministic_social.build_metricool_payload`.

---

## Durability surface (do this first after clone)

```bash
# 1) Creds → Keychain (safe parser; ignores markdown lines in docs/metricool_api.txt)
python3 scripts/integrations/metricool/install_keychain_creds.py
export METRICOOL_API_KEY="$(security find-generic-password -s phoenix-omega -a METRICOOL_API_KEY -w)"
export METRICOOL_USER_ID="$(security find-generic-password -s phoenix-omega -a METRICOOL_USER_ID -w)"

# 2) Offline durability doctor (CI gate + pin + config)
python3 scripts/integrations/metricool/doctor.py
PYTHONPATH=scripts/ci:scripts/integrations/metricool:. python3 scripts/ci/check_metricool_managed.py

# 3) Optional auth probe (no publish)
python3 scripts/integrations/metricool/doctor.py --network
```

Pin file (do not invent blog_ids): `config/integrations/metricool_waystream_pin.yaml`  
(`waystream_sanctuary` → `6582629`, proven draft `351226639`).

---

## Keychain setup (credentials)

Canonical env vars (optional at repo level; required for non-dry-run posts):

- `METRICOOL_API_KEY` — X-Mc-Auth header
- `METRICOOL_USER_ID` — Waystream account default **`3564167`**
- `METRICOOL_BASE_URL` — optional; default `https://app.metricool.com/api/v2/`

Preferred installer (avoids storing markdown header lines as the key):

```bash
python3 scripts/integrations/metricool/install_keychain_creds.py
```

Manual fallback:

```bash
security add-generic-password -U -s phoenix-omega -a METRICOOL_API_KEY -w '<paste from app.metricool.com → Settings → API>'
security add-generic-password -U -s phoenix-omega -a METRICOOL_USER_ID -w '3564167'
```

**Never** commit keys. Staging file `docs/metricool_api.txt` is gitignored — if you used it once, move the value to Keychain and delete the file locally.

Presence-only checks never print the API key value.
---

## Brand map SSOT

Path: `config/integrations/metricool_brands.yaml`

- One Metricool **account**: `waystream`
- CLI brand key for the live path: **`waystream_sanctuary`** (alias of registry archetype `way_stream_sanctuary`)
- All other brands: `status: unwired`, `blog_id: null` until an account is connected
- Placeholder `WAYSTREAM_BLOG_ID_PENDING` counts as **not ready** for real HTTP (Q-METRIC-02)

### Validate

```bash
python3 scripts/integrations/metricool/validate_config.py
# Fail if placeholders remain:
python3 scripts/integrations/metricool/validate_config.py --strict-blog-ids
```

### Sync keys after registry growth (preserve blog_id/status)

```bash
python3 scripts/integrations/metricool/sync_brands_from_registry.py --dry-run
python3 scripts/integrations/metricool/sync_brands_from_registry.py --write
# Only if intentional cleanup of unknown keys:
python3 scripts/integrations/metricool/sync_brands_from_registry.py --write --prune-orphans
```

### Add a new brand blog_id safely

1. Confirm the brand key exists in registries (or run sync `--write` so the key appears as unwired).
2. Operator supplies the **real** Metricool `blog_id` from the Metricool UI (never guess).
3. Edit only that row: set `blog_id: "<digits>"` and `status: wired` (optional `timezone`).
4. Run `validate_config.py` then `status.py` / `pilot_preflight.py --brand <key>`.
5. First post must be `--draft` (and needs `--network` or `METRICOOL_ALLOW_NETWORK=1`).

---

## Ramp: SMOKE → PILOT → SCALE

### SMOKE (offline, no network) — always safe

```bash
python3 scripts/integrations/metricool/validate_config.py
PYTHONPATH=. python3 -m pytest tests/test_metricool_client.py -q
python3 scripts/integrations/metricool/post.py \
  --brand waystream_sanctuary \
  --asset tests/fixtures/metricool/sample_asset.json \
  --draft --dry-run
python3 scripts/integrations/metricool/status.py
```

Expect: config OK (warnings OK for pending blog_id), tests green, dry-run JSON with `draft:true` / `autoPublish:false`.

### PILOT (network, draft only)

**Ready when:** Keychain has `METRICOOL_API_KEY` + `METRICOOL_USER_ID` **and**
`waystream_sanctuary.blog_id` is a real Metricool id (currently **`6582629`**, label
Waystream Sanctuary — created 2026-07-19 under userId `3564167`).

```bash
export METRICOOL_API_KEY="$(security find-generic-password -s phoenix-omega -a METRICOOL_API_KEY -w)"
export METRICOOL_USER_ID="$(security find-generic-password -s phoenix-omega -a METRICOOL_USER_ID -w)"
# Prefer targeted Keychain reads if the full registry loader is slow.
python3 scripts/integrations/metricool/pilot_preflight.py
export METRICOOL_ALLOW_NETWORK=1   # or pass --network
python3 scripts/integrations/metricool/post.py \
  --brand waystream_sanctuary \
  --asset tests/fixtures/metricool/pilot_draft_asset.json \
  --draft --network --when 2026-07-22T15:00:00
```

**Verify postId** (Metricool list is empty without a date window):

```python
# list_scheduler_posts(..., post_id="<id>")  OR
# list_scheduler_posts(..., start="...", end="...", timezone="America/New_York")
```

Proven draft pilot (2026-07-19): `postId=351226639`, `draft=true`, `autoPublish=false`.

Do **not** pass `--live`.

### SCALE (live autoPublish)

**Gated by Q-METRIC-01.** Requires:

1. Explicit operator approval (log to `operator_decisions_log.tsv`)
2. Flip `LIVE_PUBLISH_OPERATOR_APPROVED = True` in `post.py` (or successor approval mechanism)
3. CLI: `--live --i-understand-live --network`

Until then, `--live` always errors.

---

## SAFE controls (cheat sheet)

| Control | Default | Override |
|---------|---------|----------|
| Draft vs live | draft | `--live` + `--i-understand-live` + Q-METRIC-01 |
| Network HTTP | OFF | `--network` or `METRICOOL_ALLOW_NETWORK=1` |
| Placeholder blog_id | refuse (non-dry-run) | dry-run only for payload inspection |
| Empty media | refuse | `--allow-text-only` (documented; API may still 500) |
| Secrets | Keychain / env | never commit; never echo key |

---

## Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `PRIMARY_BLOCKER=Q-METRIC-CREDS` | Keychain/env empty | Store keys; `load_integration_env_from_keychain.py` |
| `PRIMARY_BLOCKER=Q-METRIC-02` / placeholder refuse | blog_id still PENDING | Operator pastes real Metricool blog_id into yaml |
| `Network kill-switch is OFF` | Forgot `--network` | Pass `--network` or set env for intentional pilot |
| `unwired` refuse | Brand not wired | Wire blog_id or use a wired brand |
| `media requires ≥1 URL` | Empty media | Attach media URLs or `--allow-text-only` |
| `--live` + Q-METRIC-01 | Go-live not ratified | Stay on `--draft` |
| GitHub 403 | Account suspended | Stay LANDED-OFFLINE; push later |
| HTTP 401 | Bad/rotated API key | Re-copy from Metricool Settings → API |
| HTTP 500 on post | Often empty media / bad payload | Check media + providers + publicationDate |

---

## Operator questions (open)

- **Q-METRIC-01** — Approve live autoPublish? Default: **no** (draft-only).
- **Q-METRIC-02** — Supply real Waystream `blog_id`? Default: keep `WAYSTREAM_BLOG_ID_PENDING` until provided.

---

## Managed surface (commands)

```text
scripts/integrations/metricool/client.py           # HTTP transport
scripts/integrations/metricool/post.py             # publish CLI (SAFE defaults)
scripts/integrations/metricool/pilot_preflight.py  # draft-pilot readiness
scripts/integrations/metricool/status.py           # managed status (presence-only)
scripts/integrations/metricool/validate_config.py  # brand map validator
scripts/integrations/metricool/sync_brands_from_registry.py
config/integrations/metricool_brands.yaml          # routing SSOT
tests/test_metricool_client.py                     # offline unit tests
docs/runbooks/METRICOOL_POSTING_RUNBOOK.md         # this file
```
