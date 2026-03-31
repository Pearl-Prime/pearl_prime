# Brand Admin Onboarding — Cloudflare Deployment

**Purpose:** Deploy the **brand-wizard-app** (Vite/React) and static **`config/onboarding/*.json`** to **Cloudflare Pages**, separate from the **`pearl-prime` Worker** ([wrangler.jsonc](../wrangler.jsonc), [docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md](./PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md)).

**Related:** Brand Admin Onboarding Stack plan, [specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md](../specs/ONBOARDING_OUTPUT_PROOF_SYSTEM.md).

---

## 1. Projects

| Project | Role |
|---------|------|
| **Onboarding Pages** (new) | `brand-wizard-app` build output + `public/onboarding/*.json` after sync |
| **pearl-prime** (existing) | Unchanged; do not merge without product decision |

Suggested Pages project name: `brand-admin-onboarding` (set in Cloudflare dashboard to match workflow).

**Default Pages URL:** `https://brand-admin-onboarding.pages.dev` (exact subdomain is assigned when you create the project; note the final hostname in Cloudflare → Pages → project → Domains).

**After first deploy (smoke test):** Open the wizard URL; in devtools Network confirm `GET …/onboarding/example_registry.json` is 200. In the gallery (served from repo static host or mirrored), confirm a stale-ready tile shows the fallback when an image 404s; in the wizard at Primary Reader, confirm the proof strip lists IDs when a mapped persona is selected.

---

## 2. Build pipeline (target)

1. Copy `config/onboarding/*.json` → `brand-wizard-app/public/onboarding/`.
2. `npm ci` && `npm run build` in `brand-wizard-app/`.
3. Deploy `brand-wizard-app/dist` to Cloudflare Pages (`wrangler pages deploy` or `cloudflare/pages-action`).

**Script:** `scripts/onboarding/sync_onboarding_config_to_public.sh` (runs automatically as `npm prebuild` in `brand-wizard-app`).

**CI:** `python scripts/ci/validate_onboarding_registry.py` (also runs in Core tests and the `brand-admin-onboarding-pages` workflow build job).

**GitHub Actions:** `.github/workflows/brand-admin-onboarding-pages.yml` builds `brand-wizard-app` and uploads `dist` as an artifact; uncomment the `deploy` job after `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are set.

---

## 3. GitHub secrets

- `CLOUDFLARE_API_TOKEN` — Pages deploy permission
- `CLOUDFLARE_ACCOUNT_ID`
- Optional: `CLOUDFLARE_PAGES_PROJECT_NAME`

Pearl_GitHub: decide if Pages deploy is **required** or **informational** on `main` ([docs/GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md)).

---

## 4. WordPress shell

- **Link-out (v1):** WP pages point to `https://brand-admin-onboarding.pages.dev` (or your custom domain) for the wizard; static spine pages (`lane_examples_gallery.html`, `market_lane_matrix.html`, etc.) can stay in-repo and be mirrored or linked as needed — avoid duplicating `config/onboarding/*.json` as a second source of truth in WP.
- **Iframe (v2):** requires Pages **`_headers`** (or dashboard) to allow `Content-Security-Policy: frame-ancestors` or relax `X-Frame-Options` for the WP origin—document allowed origins here when set.

---

## 5. Proof assets

Large binaries may eventually use **R2**; v1 can live under Pages static paths referenced by `asset_path` in the registry.

---

## 6. Status

**In repo:** Sync script, `brand-wizard-app` prebuild hook, registry validator, Pages build workflow (artifact + optional deploy stub), default hostname documented above.
