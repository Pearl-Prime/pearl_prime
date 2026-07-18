# Discovery Report — brand-wizard YAML→market verification (Lane 01, 2026-07-19)

## (a) How to run the server locally

Entrypoint: `server/app.py` (`create_app()` factory, FastAPI). Documented launcher:

```bash
python3 scripts/run_server.py --port <PORT>
# or directly:
uvicorn server.app:create_app --factory --port <PORT>
```

No API key required by default (`config/server.yaml` / `PHOENIX_API_KEY` unset in this checkout
→ `APIKeyMiddleware` no-ops). Verified live on `http://127.0.0.1:8931` for this pack
(`GET /health` → `200 {"status":"degraded", ...}` — degraded only because of an unrelated missing
`config/source_of_truth/master_arc_registry.yaml`, not a blocker for the onboarding route).

**IMPORTANT reconciliation finding — TWO parallel backends exist, not one:**

1. `server/routes/brand_onboarding.py` → `POST /api/v1/onboarding/submit`. Writes gitignored
   `artifacts/onboarding/submissions/<date>/<brand_id>__<email-slug>.yaml` +
   `artifacts/onboarding/roster_assignments.yaml`. This is the router the lane pack's
   "Router discovery (CLAIMS)" section describes, and the one this pack verifies against
   (it is the documented local-serve path and the only one reachable without a CF deploy).
2. `brand-wizard-app/functions/api/onboarding/submit.js` — a **Cloudflare Pages Function**
   that is the ACTUAL production backend the deployed wizard hits (writes JSON straight to
   R2 via `AwsClient`/SigV4, no FastAPI hop — see its own header comment: "the static Pages
   deploy has no reachable FastAPI backend"). The wizard's client fetch call is
   `fetch("api/onboarding/submit", ...)` — a **relative path with no `/v1/` and no
   `window.__ONBOARDING_API_BASE` usage at all**, in ALL FOUR wizard variants
   (`BrandWizard.jsx`, `-ja`, `-tw`, `-zh`). That path only resolves against the co-deployed
   Pages Function, not the FastAPI router. This is a pre-existing, uniform (not
   market-specific) routing gap — flagged for the record, **out of scope to fix here**
   (different subsystem: CF Pages Functions/R2, not the market-capture bug; also CF deploy
   verification is explicitly out of scope for this lane). It does NOT change the
   market-capture finding below: both backends receive whatever `brand_id`/`lane` the
   **client** computes, and the client-side bug is what's broken.

## (b) Exact market/lane field flow: wizard HTML → POST body → written YAML → assignment

```
wizard*.html (mounts main*.jsx)
  → main.jsx/-ja/-tw/-zh (mounts BrandWizard.jsx/-ja/-tw/-zh)
    → mount-time effect resolves `state.onboardingMarket` from ?market= URL param
      (hub-provided, see (d)) or localStorage `phoenix_onboarding_market`, else a
      hardcoded per-locale default
    → Activate (Step11Launch.handleLaunch): matchBrand(state, brands, teacherMode)
        (brand-wizard-app/src/brandMatch.js) — `laneSuffix = "_" + (LANE_FROM_MARKET[market] || "en_us")`
        picks a brand_id ENDING IN that lane suffix from brand_admin_brands.json
    → POST body: { brand_id: m.brand_id, lane: m.lane, publication_corp, ...brandAssignmentPayload,
        brand_email, contact, wizard_yaml, match_score, match_basis }
    → server/routes/brand_onboarding.py submit_onboarding():
        - validates brand_id against global_brand_registry_unified.yaml (39x14... now 40x14/560)
        - writes artifacts/onboarding/submissions/<date>/<brand_id>__<email>.yaml
          (server-computed `lane: req.lane` field = whatever the client sent — the SERVER
          does not independently re-derive or cross-check the market; it trusts the client's
          brand_id, which already encodes the lane as its suffix)
        - upserts artifacts/onboarding/roster_assignments.yaml[brand_id] = {...}
```

**Key insight:** the `lane` value that ends up in the written YAML and the roster overlay is
determined ENTIRELY by client-side JS before the request is even sent. The server has no
market-correction logic — it is a pure recorder keyed by whatever `brand_id` the client picked.
So the whole "market mis-capture" question reduces to: *does each wizard variant correctly set
`state.onboardingMarket` before Activate is pressed?*

## (c) Valid market lanes (config/localization/locale_registry.yaml)

`en-US, zh-CN, zh-TW, zh-HK, zh-SG, ja-JP, ko-KR, es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU, pt-BR`
(14 locales; brand registry mirrors these as `en_US/zh_CN/zh_TW/zh_HK/zh_SG/ja_JP/ko_KR/es_US/
es_ES/fr_FR/de_DE/it_IT/hu_HU/pt_BR`, 40 archetypes × 14 lanes = 560 brands in
`global_brand_registry_unified.yaml`). Locale registry explicitly documents zh-CN (Simplified,
mainland), zh-TW (Traditional, Taiwan), zh-HK (Traditional, Cantonese), and zh-SG (Simplified,
Singapore, English-dominant commerce) as 4 **distinct, non-mixable** locales.

## (d) Are zh_SG / zh_TW / zh_CN distinct selectable options at wizard entry?

Distinct **hub routing** exists in `brand-wizard-app/public/pearl_prime_entry.html`:

```js
var LANE_WIZARD = { ..., zh_TW:"wizard-tw.html", zh_CN:"wizard-zh.html", zh_HK:"wizard-tw.html", zh_SG:"wizard-zh.html", ... };
var LANE_MARKET = { ..., zh_TW:"tw", zh_CN:"cn", zh_HK:"hk", zh_SG:"sg", ... };
// goOnboarding(): window.location.href = base + '?mode=composite&market=' + encodeURIComponent(market);
```

So the hub's INTENT is correct: zh_CN → `wizard-zh.html?market=cn`, zh_SG → `wizard-zh.html?market=sg`,
zh_TW → `wizard-tw.html?market=tw`, zh_HK → `wizard-tw.html?market=hk`. **Distinct market tokens
ARE handed to the wizard.** The bug is downstream (see MARKET_CAPTURE_MATRIX.md): `wizard-tw.html`'s
`BrandWizard-tw.jsx` correctly reads `?market=` via a `resolveOnboardingMarket()` mount effect;
`wizard-zh.html`'s `BrandWizard-zh.jsx` (which the hub routes BOTH zh_CN and zh_SG through) had
**no such mechanism at all** before this lane's fix — confirmed by source grep and confirmed
live by the pre-fix verification run (both zh_CN and zh_SG synthetic submissions collapsed onto
the identical `_en_us` brand `night_reset_en_us`, already claimed by the en_US smoke submission,
and were correctly 409-rejected by the server as already-claimed — i.e. an operator submitting a
real China or Singapore signup through this wizard would have been assigned into an unrelated
American brand, or blocked with a confusing "already claimed" error).

The in-app market SELECTOR UI (`MarketChoiceCard.jsx`) is dead code in ALL FOUR wizard variants —
imported but never rendered (comment: "Market/lane step removed 2026-06-03 — locale routing
happens server-side" — actually client-side, per (b) above, but the comment correctly describes
that there's no in-wizard picker; routing is 100% via the hub's `?market=` handoff). Its
`MARKET_ACCENT` map also has no `singapore` key (an unrelated dead-code gap, not fixed here since
the card is unused — see handoff for the future-proofing note).

## (e) PROVENANCE

- research: operator's stated requirement that wizard activation must assign the CORRECT
  distinct global market (JP / zh-CN / zh-TW / zh-SG), not a collapsed/wrong one.
- documents: `config/brand_management/global_brand_registry_unified.yaml` (560 brands, 14
  lanes), `config/localization/locale_registry.yaml` (canonical locale definitions, explicit
  zh-CN/zh-TW/zh-HK/zh-SG distinctness), `brand-wizard-app/public/brand_admin_brands.json`
  (generated brand index the client matcher reads).
- builds_on: `server/routes/brand_onboarding.py` (`POST /api/v1/onboarding/submit`, unmodified),
  `brand-wizard-app/src/brandMatch.js` (`matchBrand`/`LANE_FROM_MARKET`, unmodified — the map
  already correctly supports `china`/`singapore`/`taiwan` tokens; the bug was the missing
  wiring in `BrandWizard-zh.jsx`, now added by EXTENDING it in place with the same
  `resolveOnboardingMarket()` pattern its `-tw`/`-ja` siblings already use).
- inventory: EXTENDS (fixes a wiring gap in an existing, deployed component; does not
  introduce a new subsystem).
