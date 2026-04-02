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

**Post–Package A:** The `deploy` job in `.github/workflows/brand-admin-onboarding-pages.yml` is **enabled**. After `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are set in GitHub Actions secrets, merges to `main` that touch the workflow paths trigger build + deploy. Confirm the live hostname in Cloudflare and run the smoke checks in §4.

---

## 2. Build pipeline (target)

1. `npm prebuild` runs `scripts/onboarding/sync_onboarding_config_to_public.sh`, which copies `config/onboarding/*.json` → `brand-wizard-app/public/onboarding/` and copies repo-root spine HTML (`lane_examples_gallery.html`, `market_lane_matrix.html`, etc.) → `brand-wizard-app/public/`.
2. `npm ci` && `npm run build` in `brand-wizard-app/` (Vite emits `brand-wizard-app/dist`).
3. The workflow `deploy` job runs `wrangler pages deploy dist --project-name=brand-admin-onboarding` via `cloudflare/wrangler-action@v3`.

**CI:** `python3 scripts/ci/validate_onboarding_registry.py` runs in the workflow build job before `npm run build`.

**GitHub Actions:** [.github/workflows/brand-admin-onboarding-pages.yml](../.github/workflows/brand-admin-onboarding-pages.yml) — `build` uploads `dist` as artifact `brand-admin-onboarding-dist`; `deploy` publishes to Cloudflare Pages (requires both secrets).

---

## 3. GitHub secrets

| Secret | Purpose |
|--------|---------|
| `CLOUDFLARE_API_TOKEN` | API token with **Account → Cloudflare Pages → Edit** (or broader template that includes Pages deploy). |
| `CLOUDFLARE_ACCOUNT_ID` | Account ID from Cloudflare dashboard (zone overview sidebar). |

Optional: use a GitHub **Environment** (e.g. `cloudflare-pages`) and store these as environment secrets if you want deployment protection rules.

Project name is fixed in the workflow as `brand-admin-onboarding` (must match the Pages project name in Cloudflare).

Pearl_GitHub: this workflow is **not** a required branch-protection check by default; treat deploy failures as release hygiene ([docs/GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md)).

---

## 4. Operator runbook — Package A (go live)

### 4.1 Create the Pages project (once)

1. Cloudflare → **Workers & Pages** → **Create** → **Pages** → Connect or **Direct Upload** is not required if you only deploy from CI; the first `wrangler pages deploy` with `--project-name=brand-admin-onboarding` can create the project depending on account settings. Prefer creating an empty Pages project named **`brand-admin-onboarding`** in the dashboard so DNS and settings are explicit.
2. Open **Domains** on the project and note the **`*.pages.dev`** hostname (update links in docs/specs if it differs from `brand-admin-onboarding.pages.dev`).

### 4.2 Add GitHub secrets

1. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Add `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as documented in §3.

### 7.3 Run the workflow

- Push to `main`/`master` with a change under the workflow `paths` filters, or
- **Actions** → **Brand admin onboarding (Pages)** → **Run workflow**.

### 4.4 Smoke checks (hosted)

Replace `BASE` with your confirmed Pages origin (no trailing slash):

```bash
BASE=https://brand-admin-onboarding.pages.dev
curl -sS -o /dev/null -w "%{http_code}" "$BASE/" && echo " /"
curl -sS -o /dev/null -w "%{http_code}" "$BASE/onboarding/example_registry.json" && echo " registry"
curl -sS -o /dev/null -w "%{http_code}" "$BASE/lane_examples_gallery.html" && echo " gallery"
curl -sS -o /dev/null -w "%{http_code}" "$BASE/market_lane_matrix.html" && echo " matrix"
```

Expect `200` for each. Open the wizard at `BASE/` in a browser and confirm the app loads; open the gallery HTML paths above and confirm `fetch('onboarding/example_registry.json')` succeeds (same origin).

### 4.5 Failure notes

- **Deploy fails with auth error:** rotate or recreate `CLOUDFLARE_API_TOKEN` with Pages Edit permission.
- **Build fails on validator:** fix `config/onboarding/example_registry.json` until `validate_onboarding_registry.py` passes locally.

---

## 5. WordPress shell

- **Link-out (v1):** WP pages point to `https://brand-admin-onboarding.pages.dev` (or your custom domain) for the wizard; static spine pages (`lane_examples_gallery.html`, `market_lane_matrix.html`, etc.) can stay in-repo and be mirrored or linked as needed — avoid duplicating `config/onboarding/*.json` as a second source of truth in WP.
- **Iframe (v2):** requires Pages **`_headers`** (or dashboard) to allow `Content-Security-Policy: frame-ancestors` or relax `X-Frame-Options` for the WP origin—document allowed origins here when set.

---

## 6. Proof assets

Large binaries may eventually use **R2**; v1 can live under Pages static paths referenced by `asset_path` in the registry.

---

## 7. Status

**In repo:** Sync script, `brand-wizard-app` prebuild hook, registry validator, Pages workflow with **build + deploy** to Cloudflare, default hostname documented above. **Operator steps:** §4.
