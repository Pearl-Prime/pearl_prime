# Pearl_Int — Metricool integration handoff (2026-07-19)

STATUS=LANDED-OFFLINE
SIGNAL=metricool-integration-landed
ACCEPTANCE_LAYER=system-working (transport wired + offline unit tests + pilot preflight)
NOT=PROVEN-AT-BAR (no live post; pilot BLOCKED)
GITHUB_WRITES=none (403 account-suspended)
BRANCH=offline/metricool-integration-20260719
FEATURE_SHA=d2709ebe97584eb7a997c46da28309b7d2f7a64e
PRIOR_SHA=32fcb02fa17bb94439972bfe4eb206d8b48f0d58
# Branch tip = HEAD of offline/metricool-integration-20260719 (docs pin may sit atop FEATURE_SHA)

## What landed (prior + follow-up)
- Live HTTP client: `scripts/integrations/metricool/client.py` (port of docs/metricool_utils.py minus Django)
- Publish CLI: `scripts/integrations/metricool/post.py` (draft default; --live gated Q-METRIC-01)
- GET list helper: `list_scheduler_posts` (auth proof + postId poll path)
- Pilot preflight: `scripts/integrations/metricool/pilot_preflight.py` (presence-only; never prints API key)
- Brand map: `config/integrations/metricool_brands.yaml` (65 keys; wired=`waystream_sanctuary` placeholder)
- Creds registered: `METRICOOL_API_KEY`, `METRICOOL_USER_ID`, `METRICOOL_BASE_URL` in `integration_env_registry.py` (SSOT; `check_integration_env.py` imports REGISTRY — no twin list drift)
- Leak remediation: `docs/metricool_api.txt` gitignored; store key in Keychain (never commit)
- Tests: `tests/test_metricool_client.py` (offline mocks; 12 passed)

## Gap audit (2026-07-19 GO-ON)
- check_integration_env ↔ registry: OK (import SSOT; Metricool Required=False)
- .gitignore covers docs/metricool_api.txt + docs/*_api.txt; file untracked/ignored; no real key literals in branch diff
- waystream_sanctuary blog_id still `WAYSTREAM_BLOG_ID_PENDING` (not guessed)
- Keychain probe: API_KEY=MISSING, USER_ID=MISSING
- git fetch origin: 403 account-suspended → stay LANDED-OFFLINE

## PRIMARY_BLOCKER
Q-METRIC-CREDS — METRICOOL_API_KEY and METRICOOL_USER_ID missing from env/Keychain.
ADDITIONAL: Q-METRIC-02 blog_id pending; GitHub 403 (no push/PR).

## Operator actions required for pilot
1. Confirm brand key `waystream_sanctuary` (registry archetype alias of `way_stream_sanctuary`).
2. Supply real Metricool `blog_id` → replace `WAYSTREAM_BLOG_ID_PENDING` in metricool_brands.yaml (Q-METRIC-02).
3. Store creds in Keychain:
   ```bash
   security add-generic-password -U -s phoenix-omega -a METRICOOL_API_KEY -w '<paste from app.metricool.com Settings → API>'
   security add-generic-password -U -s phoenix-omega -a METRICOOL_USER_ID -w '3564167'
   eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
   python3 scripts/integrations/metricool/pilot_preflight.py
   ```
4. When preflight READY: draft pilot (not live):
   ```bash
   python3 scripts/integrations/metricool/post.py --brand waystream_sanctuary --asset tests/fixtures/metricool/sample_asset.json --draft
   ```
5. Go-live (Q-METRIC-01): only after explicit operator approval; set `LIVE_PUBLISH_OPERATOR_APPROVED` + pass `--live --i-understand-live`.
6. Unsuspend GitHub account → push `offline/metricool-integration-20260719` → open PR.

## Decisions logged
- OPD-METRIC-01 / 02 / 03 in `artifacts/coordination/operator_decisions_log.tsv`

## NEXT_ACTION
Operator stores Keychain creds + supplies blog_id → `pilot_preflight.py` must print READY → run draft pilot → ratify Q-METRIC-01 before any --live. Unsuspend GitHub for push/PR.
