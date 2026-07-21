# Heartbeat — brand_wizard_01 (Lane 01: Pearl_Int + Pearl_Prez, YAML→market verify)

## 2026-07-19 06:20 — Startup + discovery

- Router discovery confirmed: `server/routes/brand_onboarding.py` `POST /api/v1/onboarding/submit`,
  entrypoint `server/app.py` (`create_app`), run via `uvicorn server.app:create_app --factory`.
  `scripts/run_server.py` is the documented launcher.
- 4 locale wizard HTML entrypoints confirmed to exist: `wizard.html` (en_US, loads `main.jsx`→`App.jsx`→`BrandWizard.jsx`),
  `wizard-ja.html` (`main-ja.jsx`→`BrandWizard-ja.jsx`), `wizard-tw.html` (`main-tw.jsx`→`BrandWizard-tw.jsx`),
  `wizard-zh.html` (`main-zh.jsx`→`BrandWizard-zh.jsx`).
- Market/lane derivation is CLIENT-SIDE in `brand-wizard-app/src/brandMatch.js` `matchBrand()`:
  `state.onboardingMarket` → `LANE_FROM_MARKET[market]` → brand_id suffix `_<lane>`. The `lane` field
  POSTed to the server is READ FROM the matched brand's registry entry, not independently chosen —
  so the market bug lives entirely in how `state.onboardingMarket` gets set client-side.
- **REAL GAP FOUND (pre-fix, confirmed by code read):** `BrandWizard-tw.jsx` and `BrandWizard-ja.jsx`
  both define a `resolveOnboardingMarket()` function (reads `?market=` URL param, else
  `localStorage.phoenix_onboarding_market`, else locale default) and call it in a mount `useEffect`
  to correct `state.onboardingMarket` away from its default. `BrandWizard-zh.jsx` (the wizard hub
  routes BOTH `zh_CN` AND `zh_SG` through, per `pearl_prime_entry.html` `LANE_WIZARD`/`LANE_MARKET`
  maps: `zh_CN → wizard-zh.html?market=cn`, `zh_SG → wizard-zh.html?market=sg`) has **NO**
  `resolveOnboardingMarket()` function and **NO** mount effect reading `?market=` AT ALL. Its state
  default is hardcoded `onboardingMarket: "us"` and NOTHING ever changes it. Effect: every
  wizard-zh.html submission — whether the hub sent `?market=cn` or `?market=sg` — resolves to
  `LANE_FROM_MARKET["us"] = "en_us"`, i.e. lands on an `_en_us` brand_id, NOT even `zh_cn`, let alone
  correctly distinguishing zh_SG.
- Next: stand up server, POST synthetic submissions computed via the REAL `matchBrand`/
  `resolveOnboardingMarket` code (Node) for smoke (en_US) + pilot (ja_JP, zh_TW, zh_CN, zh_SG),
  byte-verify written YAML + roster_assignments.yaml, build market-capture matrix, then scope the fix.
