# `POST /api/onboarding/submit` — Cloudflare Pages Function

**Route:** `functions/api/onboarding/submit.js` → `https://<pages-host>/api/onboarding/submit`

## Production (brand-admin-onboarding Pages)

The Function persists signups **directly to R2** (no FastAPI hop). Required Pages secrets (synced by `.github/workflows/brand-admin-onboarding-pages.yml`):

| Secret | Purpose |
|--------|---------|
| `R2_ACCESS_KEY_ID` | S3-compatible API key |
| `R2_SECRET_ACCESS_KEY` | S3-compatible secret |
| `R2_ACCOUNT_ID` | Cloudflare account (builds default endpoint if `R2_ENDPOINT` unset) |
| `R2_ENDPOINT` | Optional full R2 S3 endpoint override |

Optional: `R2_BUCKET` (default `phoenix-omega-artifacts`).

Objects written:

- `onboarding/submissions/<email>__<brand_id>__<ts>.json` — full wizard payload
- `onboarding/claimed/<lane>__<tid>.json` — teacher exclusivity marker (when applicable)
- `onboarding/assignments/<brand_id>.json` — public-safe Brand Director assignment overlay

The assignment overlay contains only deploy-safe fields such as `brand_id`,
`display_brand`, `brand_director_name`, and `brand_director_id`. It deliberately
excludes email, phone, raw wizard YAML, credentials, and contact PII. The ops dashboard
reads it through `GET /api/onboarding/assignment?brand=<brand_id>` so a completed
Brand Wizard user is visible by name immediately, before the next repo promotion.

If R2 creds are missing, the Function returns **503 `unconfigured`**; the wizard still shows the matched brand (localStorage fallback) but displays a live-assignment warning instead of silently treating the activation as complete.

## Local verification

FastAPI `POST /api/v1/onboarding/submit` writes YAML under `artifacts/onboarding/submissions/`. Use the dist proxy so the wizard bundle can hit the API:

```bash
python3 scripts/run_server.py --port 8000
python3 artifacts/verification/brand_wizard_onboarding_20260630/serve_dist_proxy.py
# wizard-ja → http://127.0.0.1:4173/wizard-ja.html
```

The proxy forwards `/api/onboarding/submit` → `http://127.0.0.1:8000/api/v1/onboarding/submit`.
