# Pearl_Int — Metricool integration handoff (2026-07-19)

STATUS=LANDED-OFFLINE
SIGNAL=metricool-draft-pilot-proven
ACCEPTANCE_LAYER=PROVEN-AT-BAR (draft pilot) — NOT live-social
NOT=live autoPublish (Q-METRIC-01 still OPEN)
GITHUB_WRITES=none (403 account-suspended)
BRANCH=offline/metricool-integration-20260719

## What changed (draft-pilot 100%)

1. **Keychain creds** — imported `METRICOOL_API_KEY` (64-char token from local gitignored
   `docs/metricool_api.txt`) + `METRICOOL_USER_ID=3564167` into service `phoenix-omega`.
   First import attempt wrongly stored a markdown line; corrected before any successful API use.
2. **Q-METRIC-02 resolved** — live brand list had **no** Waystream-labeled profile among 17
   brands. Created Metricool brand **Waystream Sanctuary** via `GET /admin/add-profile` +
   `PATCH settings/brands/:id` → `blog_id=6582629`. Wired in
   `config/integrations/metricool_brands.yaml`.
3. **Draft pilot proven** — `post.py --draft --network` → `postId=351226639` with
   `draft:true`, `autoPublish:false`. Verified via
   `list_scheduler_posts(post_id=...)` and date-window GET
   (`start=2026-07-20` / `end=2026-07-25`).
4. **Client fix** — `list_scheduler_posts` accepts `start`/`end`/`timezone`/`post_id`
   (bare GET without a window returns empty `data: []`).

## Proof roots (no secrets)

- `artifacts/coordination/metricool_brand_discovery_20260719.json`
- `artifacts/coordination/metricool_waystream_brand_create_20260719.json`
- `artifacts/coordination/metricool_pilot_get_posts_20260719.json`
- `artifacts/coordination/metricool_pilot_post_response_20260719.jsonl`
- `artifacts/coordination/metricool_pilot_verify_20260719.json`

## Managed commands

```bash
export METRICOOL_API_KEY="$(security find-generic-password -s phoenix-omega -a METRICOOL_API_KEY -w)"
export METRICOOL_USER_ID="$(security find-generic-password -s phoenix-omega -a METRICOOL_USER_ID -w)"
python3 scripts/integrations/metricool/validate_config.py --strict-blog-ids
python3 scripts/integrations/metricool/status.py
python3 scripts/integrations/metricool/pilot_preflight.py
python3 scripts/integrations/metricool/post.py --brand waystream_sanctuary \
  --asset tests/fixtures/metricool/pilot_draft_asset.json --draft --dry-run
PYTHONPATH=. python3 -m pytest tests/test_metricool_client.py -q
```

## Gates

| Gate | Status |
|------|--------|
| Q-METRIC-CREDS | RESOLVED (Keychain) |
| Q-METRIC-02 blog_id | RESOLVED (`6582629`) |
| Q-METRIC-03 leak | RESOLVED (gitignored; untracked) |
| Q-METRIC-01 go-live | OPEN — draft-only until operator approves |

## NEXT_ACTION

1. Operator: confirm new Metricool brand `Waystream Sanctuary` (`6582629`) is the intended
   posting brand (or supply a different existing blog_id to swap in yaml).
2. Optional: connect Instagram/etc. OAuth on that brand via Metricool UI (`whiteLabelLink`).
3. When ready for live social: ratify Q-METRIC-01 → flip
   `LIVE_PUBLISH_OPERATOR_APPROVED` + `--live --i-understand-live --network`.
4. Unsuspend GitHub → push `offline/metricool-integration-20260719` → PR.

## Branch tip

BRANCH_TIP=99565398ebf7053f72912acdc9ef627acafc27c8
