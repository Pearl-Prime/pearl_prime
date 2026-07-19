# Pearl_Int — Metricool integration handoff (2026-07-19)

STATUS=LANDED-OFFLINE
SIGNAL=metricool-integration-landed
ACCEPTANCE_LAYER=system-working (transport wired + offline unit tests)
NOT=PROVEN-AT-BAR (no live post; pilot BLOCKED on Q-METRIC-02 blog_id)
GITHUB_WRITES=none (403 account-suspended)
BRANCH=offline/metricool-integration-20260719

## What landed
- Live HTTP client: `scripts/integrations/metricool/client.py` (port of docs/metricool_utils.py minus Django)
- Publish CLI: `scripts/integrations/metricool/post.py` (draft default; --live gated Q-METRIC-01)
- Brand map: `config/integrations/metricool_brands.yaml` (65 keys; wired=`waystream_sanctuary` placeholder)
- Creds registered: `METRICOOL_API_KEY`, `METRICOOL_USER_ID`, `METRICOOL_BASE_URL` in integration_env_registry + credentials doc
- Leak remediation: `docs/metricool_api.txt` gitignored; store key in Keychain (never commit)
- Tests: `tests/test_metricool_client.py` (offline mocks)

## Operator actions required for pilot
1. Confirm brand key `waystream_sanctuary` (registry archetype alias of `way_stream_sanctuary`).
2. Supply real Metricool `blog_id` → replace `WAYSTREAM_BLOG_ID_PENDING` in metricool_brands.yaml (Q-METRIC-02).
3. Store creds in Keychain:
   ```bash
   security add-generic-password -U -s phoenix-omega -a METRICOOL_API_KEY -w '<paste from app.metricool.com Settings → API>'
   security add-generic-password -U -s phoenix-omega -a METRICOOL_USER_ID -w '3564167'
   eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
   ```
4. Pilot draft (not live): `python3 scripts/integrations/metricool/post.py --brand waystream_sanctuary --asset tests/fixtures/metricool/sample_asset.json --draft` (requires real blog_id + creds; media URL must be uploadable).
5. Go-live (Q-METRIC-01): only after explicit operator approval; set `LIVE_PUBLISH_OPERATOR_APPROVED` + pass `--live --i-understand-live`.

## Decisions logged
- OPD-METRIC-01 / 02 / 03 in `artifacts/coordination/operator_decisions_log.tsv`

## NEXT_ACTION
Operator supplies blog_id + Keychain creds → run pilot draft post → ratify Q-METRIC-01 before any --live.
