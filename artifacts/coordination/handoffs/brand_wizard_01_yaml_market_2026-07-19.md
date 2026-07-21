# Handoff — Lane 01 · Pearl_Int + Pearl_Prez · brand-wizard YAML→market verify (2026-07-19)

## TASK
Verify that activating the brand wizard creates a brand YAML connected to a brand, assigned to
the CORRECT global market (JP vs zh-CN vs zh-TW vs zh-SG); fix market mis-capture if broken.

## RESULT: real gap found and fixed

**`wizard-zh.html` (serves BOTH zh_CN and zh_SG per the hub's routing) had no mechanism to read
the hub's `?market=` handoff at all.** Every submission through it — whether intended for China
or Singapore — silently defaulted to the `en_US` lane (`LANE_FROM_MARKET["us"] = "en_us"`), the
SAME collapse for both markets onto the SAME wrong brand. This was confirmed live: pre-fix
synthetic zh_CN and zh_SG submissions both matched `night_reset_en_us` (the exact brand the
en_US smoke test had just claimed) and were correctly 409-rejected as already-claimed — in
production this would either silently misassign a China/Singapore signup to an unrelated
American brand, or block the admin with a confusing "brand already claimed" error.

`wizard-ja.html` and `wizard-tw.html` were NOT broken — both already implement a
`resolveOnboardingMarket()` mount effect reading `?market=`. `wizard.html` (en_US) is also fine
(its own URL/localStorage seeding effect works as documented).

## Fix landed

Single file, scoped: `brand-wizard-app/src/BrandWizard-zh.jsx`. Added the same
`resolveOnboardingMarket()` + mount-`useEffect` pattern the `-tw`/`-ja` siblings already use,
mapping `?market=cn|china|zh_cn` → `"china"` and `?market=sg|singapore|zh_sg` → `"singapore"`
(both already valid `LANE_FROM_MARKET` keys in `brandMatch.js` — untouched, not the bug).
Changed the state default from `onboardingMarket: "us"` to `"china"` (this wizard's primary
market absent a `?market=` param) and fixed one stale YAML-fallback string to match.
No changes to `server/routes/brand_onboarding.py`, `brandMatch.js`, the brand registry, or any
other subsystem — `_is_catalog_bearing`/phantom-books (lane 03) and teacher exclusivity
(lane 02) were not touched.

## Verification (byte-verified, not dispatch-only)

Ran the REAL `matchBrand`/`brandAssignmentPayload`/`appendBrandAssignmentToYAML` production
functions from `brandMatch.js` (unmodified) against the REAL `brand_admin_brands.json` (560
brands), driven by each wizard's real market-resolution logic, POSTing the exact resulting body
to a REAL locally-running FastAPI server (`uvicorn server.app:create_app`, port 8931) at
`POST /api/v1/onboarding/submit`. Byte-opened every written
`artifacts/onboarding/submissions/<date>/<brand_id>__<email>.yaml` and
`artifacts/onboarding/roster_assignments.yaml` (both gitignored, synthetic `@example.com` test
data only). Full matrix: `artifacts/qa/brand_wizard_yaml_market_verify_20260719/MARKET_CAPTURE_MATRIX.md`.

**Before fix:** en_US/ja_JP/zh_TW PASS; zh_CN and zh_SG FAIL (both collapsed to `en_us`).
**After fix:** all 5 scenarios PASS — zh_CN → `stabilizer_zh_cn`, zh_SG → `stabilizer_zh_sg`
(two distinct brands, HTTP 200, byte-verified written YAML for both).

## Live-truth reconciliation (operator's stated beliefs, re-verified — not assumed)

- **"There is no TW wizard"** — FALSE / stale. `wizard-tw.html` exists, is correctly wired
  (`resolveOnboardingMarket()` present and working), and the hub
  (`pearl_prime_entry.html`) already routes both `zh_TW` and `zh_HK` to it with the right
  `?market=` token. This belief most likely originated from the REAL, adjacent bug this lane
  found and fixed: `wizard-zh.html` (the *Simplified Chinese* wizard, a visually similar but
  separate file/URL from `wizard-tw.html`) was silently dropping every submission to en_US —
  an operator testing "the Chinese wizard" and seeing US-lane results could easily have
  concluded "the Taiwan/Chinese wizard doesn't work" without realizing TW itself was fine and
  the failure was specific to the zh (CN/SG) file. Recommend: closing this belief out as
  resolved-by-clarification, not as a build task — no missing wizard exists.
- **Does the "Chinese" wizard disambiguate China vs Singapore vs Taiwan, or collapse them?**
  Before this fix: it collapsed BOTH China and Singapore into en_US (worse than merely
  conflating CN/SG with each other — it dropped both out of the Chinese-language lanes
  entirely). Taiwan was never in scope for `wizard-zh.html` (TW has its own dedicated wizard
  and was never mis-routed). After this fix: China and Singapore are correctly distinct.

## Secondary finding (out of scope, flagged for the record — NOT fixed here)

All four wizard variants' Activate handler calls `fetch("api/onboarding/submit", ...)` — a
relative path with no `/v1/` and not using the configured `window.__ONBOARDING_API_BASE` at
all. This only resolves against the co-deployed Cloudflare Pages Function
(`brand-wizard-app/functions/api/onboarding/submit.js`, which writes straight to R2 — the
ACTUAL production backend; its own header comment confirms "the static Pages deploy has no
reachable FastAPI backend"), not the FastAPI router
(`server/routes/brand_onboarding.py`, mounted at `/api/v1/onboarding/submit`). This is a
uniform, market-independent routing/deployment-target gap (not a market mis-capture — it
affects all locales identically) and touches a different subsystem (CF Pages Functions / R2
persistence vs. the FastAPI local-serve path this lane was scoped to verify). Flagging for
whichever lane/owner covers the CF Pages Functions surface; no fix attempted (CF deploy is
explicitly out of scope for this lane).

## Minor future-proofing note (not fixed — dead code, no behavioral effect)

`brand-wizard-app/src/onboarding/MarketChoiceCard.jsx` (imported but never rendered by any
wizard — "Market/lane step removed 2026-06-03" per code comment) has no `singapore` entry in
its `MARKET_ACCENT` map. If this in-wizard market-picker UI is ever revived, add a `singapore`
key before shipping it — otherwise no functional impact today since the component is unused.

## Coordination note (commit slot)

This fix touches ONLY `brand-wizard-app/src/BrandWizard-zh.jsx` (a wizard component), never
`server/routes/brand_onboarding.py` — no overlap with lane 03's `_is_catalog_bearing` /
phantom-books commit slot on that shared file. No rebase/ordering coordination was required.

## Cleanup ledger

- Local uvicorn server (PID captured at start, port 8931) — stopped.
- Synthetic test submissions (`artifacts/onboarding/submissions/2026-07-18/*bw01_*`,
  `artifacts/onboarding/roster_assignments.yaml` test entries, `artifacts/onboarding/submissions_log.tsv`
  test rows) — all under gitignored paths; purged after evidence capture (byte excerpts already
  captured in `MARKET_CAPTURE_MATRIX.md` / this handoff / `results_prefix.json`/`results_postfix.json`).
- No worktrees created; shared branch `codex/realist-social-samples-20260718` was never switched
  or checked out away from.
- Disk free before: ~18 GiB avail. After: unchanged (no large artifacts written; node_modules
  build attempt did not modify disk usage materially — `npm run build` failed on a pre-existing
  broken `node_modules` in this shared checkout, unrelated to this change; confirmed the edit's
  validity instead via `esbuild --bundle` syntax/bundle check, which succeeded).

## Evidence

`artifacts/qa/brand_wizard_yaml_market_verify_20260719/`:
`DISCOVERY_REPORT.md`, `MARKET_CAPTURE_MATRIX.md`, `verify_market_capture.mjs` (harness, real
production code, kept for re-run/regression use), `results_prefix.json`, `results_postfix.json`.

## SIGNAL

`bw-yaml-market-verified=<see CLOSEOUT_RECEIPT>`
`bw-market-fix-landed=<see CLOSEOUT_RECEIPT>`
