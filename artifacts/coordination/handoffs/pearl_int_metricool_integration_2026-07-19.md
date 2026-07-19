# Pearl_Int — Metricool integration handoff (2026-07-19)

STATUS=LANDED-OFFLINE
SIGNAL=metricool-managed-system-landed
ACCEPTANCE_LAYER=system-working (managed safe layer + offline tests)
NOT=PROVEN-AT-BAR (no live post; pilot BLOCKED)
GITHUB_WRITES=none (403 account-suspended)
BRANCH=offline/metricool-integration-20260719
FEATURE_SHA=d2709ebe97584eb7a997c46da28309b7d2f7a64e
PRIOR_TIP=79f5deb10db9fbc37b9b1ad935cf35d9494b3ec8
# Branch tip = HEAD after managed-system hardening commit (see CLOSEOUT_RECEIPT)

## What landed (transport + managed system)

### Transport (prior)
- Live HTTP client: `scripts/integrations/metricool/client.py`
- Publish CLI: `scripts/integrations/metricool/post.py` (draft default; --live gated Q-METRIC-01)
- GET list helper: `list_scheduler_posts`
- Pilot preflight: `scripts/integrations/metricool/pilot_preflight.py` (presence-only)
- Brand map: `config/integrations/metricool_brands.yaml` (65 keys; wired=`waystream_sanctuary` placeholder)
- Creds: `METRICOOL_*` in `integration_env_registry.py`
- Leak remediation: `docs/metricool_api.txt` gitignored

### Managed system (this land)
| Pillar | Surface |
|--------|---------|
| SAFE | Network kill-switch (`METRICOOL_ALLOW_NETWORK` / `--network`); media ≥1 unless `--allow-text-only`; draft-default + live gate + placeholder refusal retained |
| SUPPORTED | `docs/runbooks/METRICOOL_POSTING_RUNBOOK.md`; `scripts/integrations/metricool/status.py` |
| MANAGED | `validate_config.py`; `sync_brands_from_registry.py` + `brand_keys.py`; offline tests expanded |

## Managed commands
```bash
python3 scripts/integrations/metricool/validate_config.py
python3 scripts/integrations/metricool/status.py
python3 scripts/integrations/metricool/sync_brands_from_registry.py --dry-run
python3 scripts/integrations/metricool/pilot_preflight.py
python3 scripts/integrations/metricool/post.py --brand waystream_sanctuary \
  --asset tests/fixtures/metricool/sample_asset.json --draft --dry-run
PYTHONPATH=. python3 -m pytest tests/test_metricool_client.py -q
```

## PRIMARY_BLOCKER
Q-METRIC-CREDS — METRICOOL_API_KEY and METRICOOL_USER_ID missing from env/Keychain.
ADDITIONAL: Q-METRIC-02 blog_id pending; Q-METRIC-01 live gate OPEN; GitHub 403 (no push/PR).

## Operator actions required for pilot
1. Confirm brand key `waystream_sanctuary`.
2. Supply real Metricool `blog_id` → replace `WAYSTREAM_BLOG_ID_PENDING` (Q-METRIC-02).
3. Store creds in Keychain (see runbook) → `status.py` / `pilot_preflight.py` → READY.
4. Draft pilot with explicit network enable:
   ```bash
   python3 scripts/integrations/metricool/post.py --brand waystream_sanctuary \
     --asset tests/fixtures/metricool/sample_asset.json --draft --network
   ```
5. Go-live (Q-METRIC-01): only after explicit operator approval.
6. Unsuspend GitHub → push branch → open PR.

## Decisions logged
- OPD-METRIC-01 / 02 / 03 (prior)
- OPD-METRIC-04 — managed-system hardening (SAFE/SUPPORTED/MANAGED); Q-METRIC-01/02 still open

## NEXT_ACTION
Operator stores Keychain creds + supplies blog_id → preflight READY → draft pilot with `--network` → ratify Q-METRIC-01 before any `--live`. Unsuspend GitHub for push/PR.
