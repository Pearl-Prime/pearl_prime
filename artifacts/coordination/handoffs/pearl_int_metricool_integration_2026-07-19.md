# Pearl_Int — Metricool integration handoff (2026-07-19)

STATUS=LANDED-OFFLINE
SIGNAL=metricool-durable
ACCEPTANCE_LAYER=PROVEN-AT-BAR (draft) + DURABLE (CI pin/gate) — NOT live-social
GITHUB_WRITES=none (403 account-suspended)
BRANCH=offline/metricool-integration-20260719

## Durability layer

| Surface | Path |
|---------|------|
| Pin SSOT | `config/integrations/metricool_waystream_pin.yaml` (blog_id=6582629) |
| CI gate | `scripts/ci/check_metricool_managed.py` (Drift detectors + readiness #34) |
| Doctor | `scripts/integrations/metricool/doctor.py` |
| Keychain install | `scripts/integrations/metricool/install_keychain_creds.py` |
| Sync pin re-apply | `sync_brands_from_registry.py::apply_waystream_pin` |

## Proven draft pilot

- blog_id=`6582629` (Waystream Sanctuary)
- postId=`351226639` (`draft:true`, `autoPublish:false`)

## Commands

```bash
python3 scripts/integrations/metricool/install_keychain_creds.py
export METRICOOL_API_KEY="$(security find-generic-password -s phoenix-omega -a METRICOOL_API_KEY -w)"
export METRICOOL_USER_ID="$(security find-generic-password -s phoenix-omega -a METRICOOL_USER_ID -w)"
python3 scripts/integrations/metricool/doctor.py
PYTHONPATH=scripts/ci:scripts/integrations/metricool:. python3 scripts/ci/check_metricool_managed.py
PYTHONPATH=. python3 -m pytest tests/test_metricool_client.py -q
```

## Gates

| Gate | Status |
|------|--------|
| Q-METRIC-CREDS | RESOLVED |
| Q-METRIC-02 | RESOLVED (6582629) |
| Q-METRIC-03 | RESOLVED |
| Q-METRIC-01 | OPEN |
| DURABLE CI | wired |

## NEXT_ACTION

Unsuspend GitHub → push branch → PR. Ratify Q-METRIC-01 only when ready for live autoPublish.
