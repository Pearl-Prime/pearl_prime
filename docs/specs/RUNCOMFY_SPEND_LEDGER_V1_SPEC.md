# RunComfy Spend Ledger V1 Spec

**Spec ID:** RUNCOMFY_SPEND_LEDGER_V1
**Cap entry:** RUNCOMFY-SPEND-LEDGER-V1-01 (to be added to `docs/PEARL_ARCHITECT_STATE.md` on merge)
**Project:** PRJ-DUAL-PATH-IMAGE-RENDER-V1 (companion to `IMG_RENDER_DUAL_PATH_V1_SPEC.md`)
**Status:** active (Pearl_Conductor v3 unattended unblock)
**Owners:** Pearl_Dev (implementation), Pearl_Int (vendor billing reconciliation), Pearl_Architect (authority), Pearl_PM (operator review)

---

## §1 Why this spec exists

`IMG_RENDER_DUAL_PATH_V1_SPEC.md` §4 mandates a `$10/mo` cumulative cap on RunComfy paid spend, enforced by `scripts/image_generation/batch_runner.runcomfy_cost_check` reading `artifacts/qa/runcomfy_monthly_spend.tsv`.

The **vendor billing endpoint** (`GET https://api.runcomfy.com/v1/account/billing/summary`) returns **HTTP 403** in the current Phoenix Omega environment (see `artifacts/qa/batch_runner_activation_smoke_2026-05-10.md` and PR #1043 smoke notes). With no successful billing read, no row is appended, and the cap gate sees `$0.00` indefinitely — the cap is **theater**.

Pearl_Conductor v3 will run unattended for 5–10 days. We need the cap gate to fire on real spend or the operator can be silently overcharged.

---

## §2 Two ingestion paths

| Path | When | Authority |
|---|---|---|
| **`source=billing_api`** | Vendor endpoint returns 200 with the §4.D contract from `IMG_RENDER_DUAL_PATH_V1_SPEC.md` | Vendor truth; preferred |
| **`source=estimated`** | Vendor endpoint returns 403/404 OR token lacks billing scope OR endpoint absent for self-serve accounts | This spec; conservative |

Both paths emit rows into the same per-call ledger, distinguished by the `source` column. Reconciliation against the RunComfy dashboard remains the operator's monthly close-out task; the ledger is the local source of truth for the **gate**, not for accounting.

The `source=estimated` path is intentionally **conservative**: wall-clock seconds always ≥ metered GPU-seconds (queueing + transfer adds wall time but is not metered). Over-counting is the correct posture for an unattended cap that must not silently overshoot.

---

## §3 Per-second rate (estimation path)

Default: **`$0.000337` per GPU-second** (≈ `$1.21 / GPU-hour`), corresponding to RunComfy Serverless **L40S** tier.

**Source:** RunComfy public pricing page (`https://www.runcomfy.com/pricing`, "Pay-as-you-go GPU seconds" tier). Operator should re-verify quarterly; rate changes go into `DEFAULT_PER_SECOND_USD` in `scripts/image_generation/runcomfy_spend_ledger.py` with the spec amended accordingly.

If a workflow is known to dispatch on a different tier (e.g. A100, H100), the caller can pass `rate_per_second_usd=` to `record_dispatch(...)`. Today every Phoenix Omega RunComfy workflow runs on the default deployment (`677edba8-…`), which is L40S — single-rate is correct for V1.

**Conservatism choice:** the `gpu_seconds` value passed in is the dispatcher-side `wall_time_s` (submit → result + download). Actual metered RunComfy compute is wall-time minus queue, transfer, and download. Estimated USD will therefore typically be **higher** than dashboard-charged USD by 10–40%. This bias is acceptable for the cap gate (false-positive cooldown is recoverable; false-negative overrun is not).

---

## §4 Artifact schemas

### §4.A `artifacts/finance/runcomfy_spend_ledger.tsv` (per-call, append-only)

```
timestamp_utc	date_local	batch_id	workflow_id	gpu_seconds	est_usd	cumulative_month_usd	source	rate_per_second_usd	request_id
```

| Column | Type | Meaning |
|---|---|---|
| `timestamp_utc` | ISO 8601 (UTC) | Moment the dispatch row was written |
| `date_local` | `YYYY-MM-DD` (`America/Los_Angeles` per IMG-RENDER §4.C) | Used for daily rollup + month bucketing |
| `batch_id` | string | Matches `image_batch_dispatch_log.tsv.batch_id` |
| `workflow_id` | string | `runcomfy_workflow` stem (e.g. `flux_txt2img_manga`) |
| `gpu_seconds` | float | Wall-clock dispatch time when `source=estimated`; vendor-reported metered seconds when `source=billing_api` |
| `est_usd` | float (6 dp) | `gpu_seconds × rate_per_second_usd` (estimated) or vendor delta (billing) |
| `cumulative_month_usd` | float (6 dp) | MTD sum of `est_usd` for current `date_local` month |
| `source` | enum: `estimated` \| `billing_api` | Provenance flag (cap is computed from both indistinguishably) |
| `rate_per_second_usd` | float (6 dp) | Rate applied this row (auditable per-row) |
| `request_id` | string | RunComfy request id when known (empty for retroactive backfills) |

### §4.B `artifacts/qa/runcomfy_monthly_spend.tsv` (daily rollup, schema unchanged)

Existing schema preserved exactly so `batch_runner.runcomfy_cost_check` and `scripts/brand/runcomfy_spend_endpoint.py` continue to work without changes:

```
date	dispatched_jobs_today	cumulative_month_spend_usd
```

Each `record_dispatch(...)` call appends a fresh rollup row reflecting today's MTD. The cap-gate reader (`batch_runner._parse_spend_tsv`) takes the **last** `cumulative_month_spend_usd` for the month, so multiple intra-day appends are safe.

---

## §5 Wiring

### §5.A Live RunComfy dispatch (auto)

`scripts/image_generation/dispatchers/runcomfy_dispatcher.py::dispatch(...)` calls `runcomfy_spend_ledger.record_dispatch(...)` immediately after a successful download + PNG validation. Failure to write the ledger row is **non-fatal** to dispatch (logged in `result["spend_ledger_error"]`) — we never block image production on bookkeeping.

The cap-gate check (`if spend >= 10.0`) runs **before** dispatch as today, so the next call sees the updated cumulative and is correctly suppressed.

### §5.B Manual / smoke / backfill

`python3 scripts/image_generation/runcomfy_spend_ledger.py --batch-id … --gpu-seconds … [--dry-run]` writes a single row. Used for:

* Operator backfilling rows after an out-of-band RunComfy dashboard reconciliation (use `--source billing_api`).
* PR smoke proof that the write path works without making any vendor call.

### §5.C Future: billing_api restoration

When the vendor billing endpoint becomes accessible (token regenerated with billing scope, or RunComfy ships a self-serve billing API for our account class), `runcomfy_cost_tracker.poll_billing(dry_run=False)` already speaks the §4.D contract. A small follow-up will route its result through `record_dispatch(..., source="billing_api", gpu_seconds=<vendor_metered_seconds>)` once per poll, and stop appending estimated rows for the same period to avoid double-count. Out of scope for V1.

---

## §6 Token hygiene (NORMATIVE)

This module reads **no** RunComfy credentials. All token handling stays in `runcomfy_dispatch.load_token` and `runcomfy_dispatcher._runcomfy_api_key`. The ledger never logs, prints, or persists token material — `git log -p` on the ledger TSV must produce zero hits for `RUNCOMFY_*`.

---

## §7 Action items

1. **(Done in PR for this spec)** Land `runcomfy_spend_ledger.py` + tests + dispatcher wiring + dry-run smoke row.
2. **(Operator)** Verify the L40S `$0.000337/s` rate against the current RunComfy pricing page; amend §3 if changed.
3. **(Pearl_Int follow-up)** Investigate the 403: regenerate token with billing scope if a setting exists; otherwise file with RunComfy support requesting documented self-serve billing access.
4. **(Pearl_PM monthly close-out)** Reconcile `runcomfy_spend_ledger.tsv` cumulative vs RunComfy dashboard invoice; if estimated overshoots actual by >40% sustained, retune `DEFAULT_PER_SECOND_USD` lower.

---

## §8 Anti-drift summary

The cap-gate reader (`batch_runner.runcomfy_cost_check`) reads `cumulative_month_spend_usd` from the daily rollup TSV. This spec preserves that schema verbatim and only **adds** an upstream per-call ledger that feeds it. No reader changes required; `runcomfy_cost_tracker.py` daily poll path remains operative for the day vendor billing returns.
