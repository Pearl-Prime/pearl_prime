# Market-Capture Matrix — brand-wizard Lane 01 (2026-07-19)

Methodology: executed the REAL, unmodified `matchBrand`/`brandAssignmentPayload`/
`appendBrandAssignmentToYAML` production functions from `brand-wizard-app/src/brandMatch.js`
against the REAL production brand index (`brand-wizard-app/public/brand_admin_brands.json`,
560 brands), driven by each wizard variant's REAL mount-time market-resolution logic (copied
verbatim from source into `verify_market_capture.mjs` — see file header). The resulting POST
body (byte-identical to what each wizard's Activate handler sends) was submitted to a REAL
locally-running FastAPI server (`uvicorn`, `server.app:create_app`) at the REAL documented
endpoint `POST /api/v1/onboarding/submit`, and the WRITTEN files were byte-opened to confirm
the captured lane. Raw run output: `results_prefix.json` (before fix) / `results_postfix.json`
(after fix). Full server source (`server/routes/brand_onboarding.py`), client source
(`BrandWizard.jsx`/`-ja`/`-tw`/`-zh`, `brandMatch.js`), and hub routing
(`pearl_prime_entry.html`) were read in full — not assumed.

## BEFORE FIX (results_prefix.json)

| Wizard file | Hub `?market=` | Intended lane | Captured brand_id | Captured lane | Written YAML | Verdict |
|---|---|---|---|---|---|---|
| `wizard.html` | (none) | en_US | `night_reset_en_us` | en_US | `submissions/2026-07-18/night_reset_en_us__...yaml` ✅ | **PASS** |
| `wizard-ja.html` | `jp` | ja_JP | `stabilizer_ja_jp` | ja_JP | `submissions/2026-07-18/stabilizer_ja_jp__...yaml` ✅ | **PASS** |
| `wizard-tw.html` | `tw` | zh_TW | `stabilizer_zh_tw` | zh_TW | `submissions/2026-07-18/stabilizer_zh_tw__...yaml` ✅ | **PASS** |
| `wizard-zh.html` | `cn` | zh_CN | `night_reset_en_us` ⚠️ | **en_US** | HTTP 409 `brand_claimed` (would have written the SAME en_US brand file the smoke test already claimed) | **FAIL** |
| `wizard-zh.html` | `sg` | zh_SG | `night_reset_en_us` ⚠️ | **en_US** | HTTP 409 `brand_claimed` (identical collapse — zh_CN and zh_SG land on the exact same wrong brand as each other AND as en_US) | **FAIL** |

**Root cause (confirmed by source read, not inference):** `BrandWizard-zh.jsx` state initialized
`onboardingMarket: "us"` and had **no `resolveOnboardingMarket()` function and no mount
`useEffect` reading `?market=`/localStorage at all** — unlike its `-tw`/`-ja` siblings, which both
implement this pattern. Every `wizard-zh.html` submission, regardless of the hub's
`?market=cn` or `?market=sg` handoff, silently defaulted to `LANE_FROM_MARKET["us"] = "en_us"`.

## AFTER FIX (results_postfix.json)

| Wizard file | Hub `?market=` | Intended lane | Captured brand_id | Captured lane | Written YAML | Verdict |
|---|---|---|---|---|---|---|
| `wizard.html` | (none) | en_US | `night_reset_en_us` | en_US | (re-submit of already-claimed brand → 409, expected/idempotent) | **PASS** |
| `wizard-ja.html` | `jp` | ja_JP | `stabilizer_ja_jp` | ja_JP | (re-submit, 409, expected) | **PASS** |
| `wizard-tw.html` | `tw` | zh_TW | `stabilizer_zh_tw` | zh_TW | (re-submit, 409, expected) | **PASS** |
| `wizard-zh.html` | `cn` | zh_CN | `stabilizer_zh_cn` | **zh_CN** ✅ | `submissions/2026-07-18/stabilizer_zh_cn__...yaml` (HTTP 200, byte-verified) | **PASS** |
| `wizard-zh.html` | `sg` | zh_SG | `stabilizer_zh_sg` | **zh_SG** ✅ | `submissions/2026-07-18/stabilizer_zh_sg__...yaml` (HTTP 200, byte-verified) | **PASS** |

**All-PASS matrix achieved.** zh_CN and zh_SG now resolve to two DISTINCT brands
(`stabilizer_zh_cn` vs `stabilizer_zh_sg`) — no collapse, no cross-market contamination. The
en_US/ja_JP/zh_TW rows show `409 brand_claimed` on the second run only because they are
re-submitting the SAME already-claimed brand from the first (pre-fix) run — this is the
server's teacher/assignment-conflict guard working correctly, not a regression; the
`matched_brand_id` in both runs is identical and correct, which is the signal under test.

## Fix applied (scoped, single file)

`brand-wizard-app/src/BrandWizard-zh.jsx`:
- Added `resolveOnboardingMarket()` (mirrors the `-tw`/`-ja` pattern exactly): reads `?market=`
  URL param, else `localStorage.phoenix_onboarding_market`, normalizes `cn/china/zh_cn` →
  `"china"` and `sg/singapore/zh_sg` → `"singapore"` (both already valid keys in
  `brandMatch.js`'s `LANE_FROM_MARKET` — that map was NOT the bug and was not touched).
- Added the matching mount `useEffect` calling it and updating `state.onboardingMarket`.
- Changed the state default from `onboardingMarket: "us"` to `onboardingMarket: "china"`
  (this wizard's primary market when reached without a `?market=` param, consistent with the
  `-tw`/`-ja` siblings each defaulting to their own primary market).
- Updated the one stale YAML-generation fallback string (`state.onboardingMarket || "us"` →
  `|| "china"`) for consistency.

No changes to `server/routes/brand_onboarding.py`, `brandMatch.js`, or any other file — the
gap was isolated to one wizard component's missing mount-time wiring.
