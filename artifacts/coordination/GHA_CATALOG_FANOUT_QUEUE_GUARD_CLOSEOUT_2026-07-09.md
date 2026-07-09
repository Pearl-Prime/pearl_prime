# GHA Catalog Fanout Queue Guard — Closeout (2026-07-09)

**Lane:** Permanent catalog-fanout throttle / queue-guard patch  
**Agent:** Pearl_GitHub (Cursor session)

## Problem

Wave 1 and wave 2 queue relief proved catalog fanout workflows can refill GitHub Actions indefinitely: each `ci/catalog-*` PR triggers the full PR check suite, starving non-catalog work (manga PRs #5419/#5428).

## Patch mechanisms

| Mechanism | Detail |
|---|---|
| `scripts/ci/gha_queue_pressure_guard.py` | Shared fail-closed guard; samples last 200 runs via `gh run list` |
| Queue-pressure thresholds | Block when `queued_total ≥ 80` OR `catalog_queued ≥ 60` OR catalog/non-catalog starvation ratio ≥ 5× |
| `force_when_queue_hot` input | Boolean workflow_dispatch override, **default false**, on all three fanout workflows |
| `max-parallel` reduction | locale `4→2`, campaign `6→2`, complete `4→2` |
| `actions: read` permission | Added so guard can query workflow run queue |
| Tests | `tests/test_gha_queue_pressure_guard.py` |

## Workflows patched

- `.github/workflows/catalog-fanout-locale.yml`
- `.github/workflows/catalog-fanout-campaign.yml`
- `.github/workflows/catalog-fanout-complete.yml`

## Rationale

- **Fail closed** when queue is hot — fanout discover job exits before matrix fan-out.
- **Manual override OFF by default** — operator must explicitly set `force_when_queue_hot=true`.
- **Lower parallelism** — halves concurrent brand jobs even when queue is cool.
- **No governance bypass** — required PR checks unchanged; guard only gates fanout dispatch.

## Proof lane (lane 3)

After merge, dispatch one guarded run with override OFF when queue is hot OR one tiny pilot when cool — see `GHA_CATALOG_RESUME_CLOSEOUT_2026-07-09.md` (written by proof lane).
