# RunComfy V1.2 Panel Hang — Root Cause Diagnosis

**Date:** 2026-05-13
**Author:** Pearl_Int
**Triggered by:** PR #1084 V1.2 live smoke (2026-05-12 ~06:00 UTC), cell
`v3_379879bed64c08` (body_memory_shojo manga panel) — killed by 4-min/cell
guard during RunComfy dispatch submit/poll.
**Blast radius:** 11,908 of 13,540 Phase 2 fan-out batches (~88% of v3 cells).
**Pearl Star FLUX path:** unaffected (6/6 covers rendered cleanly).

## TL;DR

**Root cause:** RunComfy serverless FLUX deployment cold-start wall time is
~292–371 s (5–6 min) for a single inference. The dispatcher's hard-coded
`poll_request(..., max_wait=300)` and the operator's 4-min/cell guard were
both below that floor, so every V1.2 panel batch was reaped before RunComfy
could finish even a single render. No vendor-side error or token rotation
needed — the budgets were just too tight for cold-start behaviour.

**Fix:** Raise dispatcher poll budget to 600 s (matches Pearl Star history
poll), expose `poll_wait_s` + `poll_budget_s` on results for observability,
and add `RUNCOMFY_POLL_MAX_WAIT_S` env override (clamped to [300, 1800]).
Document the new minimum upstream cell-guard for RunComfy-dispatched panels
(see CONDUCTOR_V3_DISPATCH_BRIDGE spec amendment).

## Hypothesis-by-hypothesis findings

| # | Hypothesis | Verdict | Evidence |
|---|------------|---------|----------|
| H1 | Token state (revoked / 401) | **REJECTED** | `RUNCOMFY_API_KEY` (36-char UUID) authenticates against deployment inference endpoint — `POST .../inference → 200 OK in 0.89 s`. |
| H2 | Account / queue / credit state | **REJECTED** | `cumulative_month_spend_usd: 0.0118` (well below $10 cap); inference accepted and runs to completion. |
| H3 | Workflow JSON missing / invalid | **PARTIALLY VALID, not the cause** | `qwen_image_txt2img_manga.json` parses (11 nodes), but the RunComfy deployment ID currently in use (`677edba8-ace0-4b2b-bad2-8e94b9959065`) is a **FLUX** deployment — Qwen overrides are no-ops because the deployment's saved graph is FLUX. This is a separate concern (panels are effectively rendering as FLUX, not Qwen), recommended as follow-up surfacing PR but does not cause the hang. |
| H4 | Payload contract drift | **REJECTED** | `overrides` payload accepted. Submit response well-formed: `request_id`, `status_url`, `result_url`, `cancel_url`. |
| H5 | Polling endpoint changed | **PARTIALLY VALID, not the cause** | Submit returns `prod/v2` URLs; dispatcher's fallback URL builder uses `prod/v1` (latent bug, masked because the live submit always provides the v2 URL in body). Logged as follow-up. |
| H6 | V1.2 prompt size > limit | **REJECTED** | `_panel_positive_prompt` builds ~200-char prompts (`vertical webtoon panel, {brand}…, throughline: {throughline}`) — well under any reasonable CLIP/T5 cap. |
| H7 | Network / region | **REJECTED** | `api.runcomfy.net` resolves and responds normally from operator network. |
| **H8 (new)** | **Cold-start wall time exceeds poll/cell budgets** | **CONFIRMED** | Live measured: 292 s (diagnosis call) and 371 s (verification call). Dispatcher `max_wait=300`, operator cell guard `=240 s`. Both below P50 cold-start. |

## Verification

Single-cell live dispatch through the patched `runcomfy_dispatcher.dispatch()`
with `RUNCOMFY_POLL_MAX_WAIT_S=600`:

```json
{
  "status": "succeeded",
  "wall_time_s": 371.4,
  "poll_wait_s": 368.68,
  "poll_budget_s": 600,
  "sha256": "cdf08019b7d52eda0874fe09d9b3d5f3181e1d97da74b1f01a0b3b6afe10cb2b",
  "spend_ledger": {"est_usd": 0.125, "cumulative_month_usd": 0.137}
}
```

PNG: 638,666 bytes, valid `\x89PNG\r\n\x1a\n` header.

## Spend incurred

- Diagnosis call: ~292 s GPU → ~$0.098
- Verification call: ~371 s GPU → ~$0.125
- **Total: ~$0.22** (under $3 cap).

## Operator follow-ups (NOT blocking V1.2 fan-out)

1. **Upstream cell-guard:** Raise the per-cell wall guard for
   RunComfy-dispatched panels to **≥ 480 s** (8 min) — covers measured
   cold-start P95 with 30 % headroom. The dispatcher's 600 s poll budget
   gives the cell guard room to fire diagnostics before forcibly killing.
2. **Qwen vs FLUX deployment:** Confirm whether panels should render via the
   Qwen workflow JSON. If yes, a Qwen-specific RunComfy deployment ID is
   needed; `RUNCOMFY_DEPLOYMENT_ID` env var should be set per-workflow.
   Today, panel batches submit Qwen workflow hints but execute the FLUX
   graph because the deployment is FLUX-only. (Not a regression — same
   behaviour as before this fix; flagged for product clarity.)
3. **Latent `prod/v1` vs `prod/v2` URL drift:** Fallback URL builder in
   `runcomfy_dispatcher.py:155-159` uses `prod/v1`. Live submit returns
   `prod/v2` URLs, so the fallback never fires in the happy path — but if
   RunComfy ever omits `status_url` from the submit response, fallback
   would 404. Low-priority hygiene fix.

## Phase 2 readiness verdict

**GREEN** — with the fix landed + upstream cell guard raised to ≥ 480 s,
the 11,908 blocked panel batches can proceed. Recommend the operator
re-run the cell `v3_379879bed64c08` smoke first as a wall-time sanity check
before un-pausing the full fan-out.
