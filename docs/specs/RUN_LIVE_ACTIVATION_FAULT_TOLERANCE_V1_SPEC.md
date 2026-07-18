# RUN_LIVE_ACTIVATION_FAULT_TOLERANCE_V1 — Per-batch fault tolerance for unattended dispatch

**Subsystem:** image_generation
**Owner:** Pearl_Dev (impl) + Pearl_Conductor (consumer)
**Authority module:** `scripts/image_generation/batch_runner.py` (`run_live_activation`)
**Tests:** `tests/image_generation/test_run_live_activation_fault_tolerance.py`
**Related project:** PRJ-DUAL-PATH-IMAGE-RENDER-V1 (IMG-RENDER-DUAL-PATH-V1-01) — this spec adds a wrapper **around** the existing routing logic; routing semantics are unchanged.

---

## 1. Problem

Pearl_Conductor v3 will dispatch ~7,400 image-generation units unattended over 5–10 days. PR #1043's 12-cell smoke hit **one** transient RunComfy failure (`No image URL` on `smoke_v11_ahjan_sp_panel_en`) that required a manual retry. With no per-batch fault tolerance, a single transient at unit 800 would abort the entire run, wasting the prior ~10 hours of compute and forcing the operator to manually resume from the failure point.

## 2. Goal

`run_live_activation` MUST:

1. Survive any **single-cell** failure without aborting the run.
2. Retry **transient** errors per a configurable backoff schedule.
3. **Fail fast** for non-retryable errors (auth, invalid workflow, cap exhausted) without burning retry budget.
4. Persist a TSV record of every permanently-failed cell so the operator can re-dispatch them in a follow-up batch.
5. Emit a final summary row (`succeeded N / retried M / failed K`) so the operator can grep one line at run end.

## 3. Non-goals

- Do **not** change `IMG-RENDER-DUAL-PATH-V1-01` routing logic. The retry wrapper sits around `dispatch(...)` and never decides which dispatcher to call.
- Do **not** retry across the cost-cap cooldown gate (cooldown is checked **before** entering the wrapper).
- Do **not** add cross-cell circuit breaking in V1. (If 50 consecutive cells fail, Pearl_Conductor's outer monitor is responsible for paging the operator — not this wrapper.)

## 4. Retry policy

`FaultTolerancePolicy` (frozen dataclass):

| Field | Default | Meaning |
|---|---|---|
| `max_retries` | `2` | Additional attempts after the first failure (so up to 3 total tries per cell). |
| `backoff_schedule_s` | `(30.0, 90.0)` | Sleep before retry attempt N. Last entry is reused if `max_retries` exceeds list length (clamped). |
| `extra_transient` | `()` | Lowercase substrings appended to the built-in transient list. |
| `extra_non_retryable` | `()` | Lowercase substrings appended to the built-in non-retryable list (wins over transient on conflict). |

Backoff is roughly exponential (~3x). 30s/90s was chosen because the observed RunComfy "No image URL" failure typically clears within ~60s when it recurs on a retry.

## 5. Classification table

Match is **case-insensitive substring** on `f"{type(exc).__name__}: {exc}"`. **Non-retryable wins** when both lists match the same exception.

### Transient (retry until budget exhausted)

| Substring | Source |
|---|---|
| `no image url` | RunComfy `extract_image_url` returned None — observed in PR #1043 smoke. |
| `http 502` / `502 bad gateway` | RunComfy or Pearl Star upstream gateway hiccup. |
| `http 503` / `503 service unavailable` | RunComfy queue back-pressure. |
| `http 504` / `504 gateway timeout` | Long-tail render. |
| `timeout` / `timed out` / `read timed out` | requests / urllib3 / httpx timeouts. |
| `queue full` / `queue is full` | RunComfy concurrency cap. |
| `connection reset` / `connection aborted` | TCP-level transient. |
| `temporarily unavailable` | Generic upstream signal. |

### Non-retryable (fail fast — one attempt only)

| Substring | Reason |
|---|---|
| `http 401` / `unauthorized` / `invalid api key` / `invalid token` | Credentials wrong; retrying just rate-limits us further. |
| `http 403` / `forbidden` | Account / endpoint permission. |
| `invalid workflow` / `workflow json` | Malformed graph — won't fix itself. |
| `suppressed_cooldown` | Dispatcher-level cap signal (defense-in-depth alongside the up-front cost gate). |
| `cumulative_month_spend_usd >= $10` / `spend cap` / `cap exhausted` | $10/mo soft cap; do not keep poking. |
| `missing status url` | Malformed RunComfy submit response — config issue, not transient. |

### Unknown (treat as non-retryable)

Any exception whose message matches **neither** list is classified `unknown` and the cell fails-fast. This is intentional: surprise failures should not silently consume the retry budget. The sidecar row records `classification=unknown` so the operator can extend `extra_transient` / `extra_non_retryable` next run.

`KeyboardInterrupt` and `SystemExit` are **never** caught — operator stop must always work.

## 6. Sidecar TSV

Path: `<output_root>/<run_id>_failed_cells.tsv`

`run_id` defaults to `run_<UTC ISO compact>_<6-hex>` if not supplied. Pearl_Conductor SHOULD pass an explicit `run_id` so the operator can correlate the sidecar with conductor logs.

Header: `ts_utc\tbatch_id\tdispatch_path\tclassification\tattempts\terror`

Tabs/newlines inside the error message are collapsed to single spaces; the `error` field is truncated to 2000 chars.

## 7. Summary row

After the final cell, `run_live_activation` appends one extra dict:

```python
{
    "fault_tolerance_summary": True,
    "run_id": "...",
    "succeeded": int,
    "retried": int,           # cells that needed >=2 attempts but eventually succeeded
    "failed": int,
    "failed_cells": [{"batch_id": ..., "classification": ..., "attempts": ...}, ...],
    "failed_cells_sidecar": "<absolute path>" or None,
}
```

Consumers MUST filter on `not r.get("fault_tolerance_summary")` to enumerate only the per-cell rows. The two pre-existing live-dispatch tests have been updated to do this.

## 8. Backwards compatibility

- All new args on `run_live_activation` (`fault_tolerance`, `run_id`, `sleep_fn`) are keyword-only with safe defaults.
- The CLI `main()` continues to call `run_live_activation` with the same arguments as before; behavior changes are: (a) summary row in stdout, (b) sidecar TSV when any cell fails, (c) transient cells now retried instead of aborting the loop.
- Cost-cap cooldown skip path is unchanged.
- Routing (`apply_dispatch_routing` / `resolve_dispatch_path`) is unchanged.

## 9. Verification

| Scenario | Test |
|---|---|
| Success on first try | `test_success_first_try` |
| Transient → retry → success | `test_transient_then_success` |
| Transient → retries exhausted → sidecar + continue | `test_retries_exhausted_logs_sidecar_and_continues` |
| Non-retryable → fail-fast → sidecar + continue | `test_non_retryable_fails_fast` |
| Cost cap (both up-front skip and dispatcher-raised cap message) | `test_cap_exhausted_skip_then_runtime_message_non_retryable` |
| Unknown exception class | `test_unknown_error_treated_as_non_retryable` |
| Operator interrupt always wins | `test_keyboard_interrupt_propagates` |
| Caller-supplied `extra_transient` extends classifier | `test_custom_policy_extra_transient` |

Plus 8 unit tests on the classifier itself (auth, cap, invalid workflow, timeout, http codes, unknown, non-retryable-wins).

## 10. Pearl_Conductor v3 contract

When Pearl_Conductor v3 calls this entry point it SHOULD:

1. Pass an explicit `run_id` (e.g. `conductor_v3_2026_05_12_t0830`).
2. After the run, parse the final element of the result list (the summary). If `failed > 0`, surface the sidecar path in the conductor's daily digest so the operator can re-dispatch failed cells.
3. Treat `failed_cells` as the source of truth for "what to retry next pass". Do not infer failure from per-cell rows alone.

## 11. Out-of-scope follow-ups

- **Cross-cell circuit breaker** — if N consecutive cells fail with the same classification, page operator and stop. Tracked separately.
- **Retry budget per dispatch path** — currently both Pearl Star and RunComfy share `max_retries`. A future spec may split them (RunComfy benefits from more aggressive retries; Pearl Star failures are usually structural).
- **Sidecar replay tool** — a small CLI to read `<run_id>_failed_cells.tsv` and re-dispatch only those `batch_id`s. Will live in `scripts/image_generation/replay_failed_cells.py`.
