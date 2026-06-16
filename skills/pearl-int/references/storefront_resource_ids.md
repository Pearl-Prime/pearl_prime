# Pearl Prime Storefront — Resource IDs Reference + Operator Action Runbook

**Status:** TEMPLATE — populated as operator provisions resources.
**Owner:** Pearl_Int
**Spec:** [`docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md`](../../../docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md) §5 (hosting topology) + §AMENDMENT-2026-06-04.2/.3 (Snipcart wraps Stripe).
**Cap:** `PEARL-PRIME-STOREFRONT-V1-01` (active)
**Authored:** 2026-06-06 (Pearl_Int infra scaffold ws)
**Last verified:** TEMPLATE — no resources provisioned yet

---

## TL;DR — What this file is for

A CLI agent session **cannot** provision Cloudflare resources or create a Snipcart account. Those require operator dashboard logins. This file is the **operator-action runbook** + **reference for the resulting IDs**.

Populate the placeholders below as you (operator) walk the runbook. Pearl_Dev's follow-up ws expects these IDs to be present before populating `storefront/wrangler.toml` bindings + `scripts/ci/integration_env_registry.py` Keychain entries.

**This file never stores secrets.** Resource IDs and bucket names are OK here (they're not credentials). API tokens, webhook secrets, and Snipcart keys live in macOS Keychain (locally) + GitHub repo secrets (CI) — never in this file.

---

## §1 — Cloudflare Pages project

| Field | Value | Status |
|---|---|---|
| Project name | `pearl-prime-storefront` | scaffold-set in `storefront/wrangler.toml` |
| Account | `b80152c319f941e6e92f928e2617a3d5` | already-set (shared with brand-admin-onboarding-pages) |
| Default live URL | `https://pearl-prime-storefront.pages.dev` | OPERATOR-ACTION-REQUIRED to confirm post-first-deploy |
| Custom domain (Phase A) | `pearlprime.shop` (Q-PRP-DOMAIN-01, pending DNS) | OPERATOR-ACTION-REQUIRED |
| Deploy workflow | `.github/workflows/pearl-prime-storefront-deploy.yml` | shipped this PR |
| Auto-deploy trigger | `storefront/**` or workflow file change on `main` | shipped this PR |

**Operator runbook — Pages project provisioning:**

1. Log into Cloudflare dashboard for account `b80152c319f941e6e92f928e2617a3d5` (NOT the operator's primary `ahjansamvara@gmail.com` account = `626d6eb8162a8121f74e59235d82a4f5` — that account has zero Pages projects per `cloudflare_pages_deploy.md` Trap 3).
2. Workers & Pages → Create application → Pages → Direct upload (skip Git integration — we deploy from GitHub Actions, not via Cloudflare's git integration).
3. Project name: `pearl-prime-storefront` exactly (case-sensitive — must match `--project-name=pearl-prime-storefront` in the deploy workflow).
4. First "Direct upload" can be an empty `index.html`; the workflow takes over from then on.
5. Verify live URL = `https://pearl-prime-storefront.pages.dev`.

---

## §2 — Cloudflare D1 database

| Field | Value | Status |
|---|---|---|
| Database name | `pearl_prime_storefront` | reserved |
| Database ID | `<OPERATOR-ACTION-REQUIRED: pearl_prime_storefront D1 ID>` | **PLACEHOLDER** |
| Read replicas | none at Phase A (single instance); add regional replicas at Phase B per spec §5.2 + CF e-commerce ref-arch | OPERATOR-ACTION-REQUIRED Phase B |
| Wrangler binding | `DB` | scaffold-set in `storefront/wrangler.toml` (commented) |
| Initial migration | `storefront/migrations/0001_init.sql` (placeholder; Pearl_Dev ws lands real schema) | shipped this PR |
| Env var (CI) | `STOREFRONT_D1_ID` | added to `scripts/ci/integration_env_registry.py` |

**Operator runbook — D1 provisioning:**

1. Cloudflare dashboard → Workers & Pages → D1 → Create database.
2. Name: `pearl_prime_storefront` exactly.
3. Location: default (CF picks the right region; spec §5.2 doesn't pin one).
4. Copy the database ID — paste below as the §2 placeholder + add to Keychain:
   ```bash
   security add-generic-password -s phoenix-omega -a STOREFRONT_D1_ID -w "<the D1 ID>" -U
   ```
5. Bind D1 to the Pages project: dashboard → Pages → pearl-prime-storefront → Settings → Functions → D1 database bindings → Add binding → `DB` → pearl_prime_storefront.
6. Uncomment the `[[d1_databases]]` block in `storefront/wrangler.toml` + paste the ID.

---

## §3 — Cloudflare R2 bucket

| Field | Value | Status |
|---|---|---|
| Bucket name | `pearl-prime-storefront-assets` | reserved |
| Prefixes pre-allocated | `en-US/`, `ja-JP/` (Phase A) + reserved `zh-TW/`, `zh-CN/`, `ko-KR/` (Phase B/C) | OPERATOR-ACTION-REQUIRED |
| Wrangler binding | `ASSETS` | scaffold-set in `storefront/wrangler.toml` (commented) |
| Asset types | EPUB (book), M4B+MP3 (audiobook), WEBTOON PNG + PDF (manga), cover JPG/PNG, album/track audio for music SKUs | spec §5 |
| Signed-URL TTL | 15 minutes (regenerated on demand from `/api/account/library`) | spec §5.1 |
| Env var (CI) | `STOREFRONT_R2_BUCKET` | added to `scripts/ci/integration_env_registry.py` |

**Operator runbook — R2 provisioning:**

1. Cloudflare dashboard → R2 → Create bucket.
2. Bucket name: `pearl-prime-storefront-assets` exactly.
3. Location: default (CF Auto; jurisdiction = no preference unless EU customer data lands here, which it doesn't at Phase A per spec §1.2).
4. Bind R2 to the Pages project: dashboard → Pages → pearl-prime-storefront → Settings → Functions → R2 bucket bindings → Add binding → `ASSETS` → pearl-prime-storefront-assets.
5. Create the Phase A prefixes (R2 doesn't need explicit "folders" — first PUT creates them, but pre-document the layout). Pearl_Dev ws populates them.
6. Save bucket name to Keychain (the bucket name IS the identifier for R2; there's no separate UUID):
   ```bash
   security add-generic-password -s phoenix-omega -a STOREFRONT_R2_BUCKET -w "pearl-prime-storefront-assets" -U
   ```

---

## §4 — Cloudflare KV namespace

| Field | Value | Status |
|---|---|---|
| Namespace name | `pearl_prime_storefront_session_cart` | reserved |
| Namespace ID | `<OPERATOR-ACTION-REQUIRED: pearl_prime_storefront_session_cart KV namespace ID>` | **PLACEHOLDER** |
| Wrangler binding | `SESSION_CART` | scaffold-set in `storefront/wrangler.toml` (commented) |
| TTL | 60 minutes for anonymous browsing cart; persisted to D1 on sign-in | spec §5.1 |
| Env var (CI) | `STOREFRONT_KV_NAMESPACE_ID` | added to `scripts/ci/integration_env_registry.py` |

**Operator runbook — KV provisioning:**

1. Cloudflare dashboard → Workers & Pages → KV → Create namespace.
2. Name: `pearl_prime_storefront_session_cart` exactly.
3. Copy the namespace ID — paste below as the §4 placeholder + add to Keychain:
   ```bash
   security add-generic-password -s phoenix-omega -a STOREFRONT_KV_NAMESPACE_ID -w "<the KV namespace ID>" -U
   ```
4. Bind KV to the Pages project: dashboard → Pages → pearl-prime-storefront → Settings → Functions → KV namespace bindings → Add binding → `SESSION_CART` → pearl_prime_storefront_session_cart.
5. Uncomment the `[[kv_namespaces]]` block in `storefront/wrangler.toml` + paste the ID.

---

## §5 — Cloudflare API token (Pages, scoped to storefront-deploy)

| Field | Value | Status |
|---|---|---|
| Token name | `pearl_prime_storefront_pages_deploy` | reserved |
| Account scope | Specific account → `b80152c319f941e6e92f928e2617a3d5` (NOT "All accounts" which returns empty per Trap 4) | OPERATOR-ACTION-REQUIRED |
| Permissions | Account → Cloudflare Pages → Edit + User → User Details → Read | OPERATOR-ACTION-REQUIRED |
| Client IP filter | blank | OPERATOR-ACTION-REQUIRED |
| TTL | blank (no expiry) | OPERATOR-ACTION-REQUIRED |
| Env var (CI repo secret) | `CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT` (or share existing `CLOUDFLARE_API_TOKEN`) | added to `scripts/ci/integration_env_registry.py` |

**Operator runbook — token provisioning:**

> Recommended path: reuse the existing `CLOUDFLARE_API_TOKEN` repo secret (already scoped to b80152c3... per `cloudflare_pages_deploy.md`). It already has Pages → Edit perms.
>
> Only create a **new** scoped token if you want the storefront workflow to fail-loud if it tries to write to non-storefront Pages projects.

If you do want a separate token:

1. Visit https://dash.cloudflare.com/profile/api-tokens → Create Token → Custom token → Get started.
2. Permissions: `Account → Cloudflare Pages → Edit` + `User → User Details → Read`.
3. Account Resources: **Specific account** (not "All accounts") → pick `b80152c319f941e6e92f928e2617a3d5`.
4. Client IP Filtering: blank.
5. TTL: blank.
6. Add as a GitHub repo secret `CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT` (Settings → Secrets and variables → Actions) AND save locally:
   ```bash
   security add-generic-password -s phoenix-omega -a CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT -w "<the token>" -U
   ```
7. Update `.github/workflows/pearl-prime-storefront-deploy.yml` if you choose this path: replace `secrets.CLOUDFLARE_API_TOKEN` with `secrets.CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT`.

---

## §6 — Snipcart account

| Field | Value | Status |
|---|---|---|
| Account email | `<OPERATOR-ACTION-REQUIRED: Snipcart account email>` | **PLACEHOLDER** |
| Dashboard URL | https://app.snipcart.com/dashboard | reference |
| Tier | Free (Phase A; ≤ $500/mo gross OR ≤ 5 orders/mo per Snipcart's 2026 terms) | per AMENDMENT Q-PRP-PAY-01 |
| Public API key | `<OPERATOR-ACTION-REQUIRED: Snipcart public key — paste in storefront HTML>` | **PLACEHOLDER** (env var `SNIPCART_PUBLIC_API_KEY`) |
| Secret API key | stored in macOS Keychain — `SNIPCART_API_KEY` | **PLACEHOLDER** |
| Webhook URL | `https://pearlprime.shop/api/webhook/snipcart` (returns 404 until Pearl_Dev ws lands code — that is expected) | OPERATOR-ACTION-REQUIRED |
| Webhook secret | `SNIPCART_WEBHOOK_SECRET` — stored in Cloudflare Pages env var (encrypted) | **PLACEHOLDER** |
| Webhook secret rotation | quarterly (next rotation: every 90 days from creation) | per `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` |
| Domains whitelist | `pearlprime.shop` + `pearl-prime-storefront.pages.dev` | OPERATOR-ACTION-REQUIRED |
| Currencies (Phase A) | USD + JPY | per AMENDMENT Q-PRP-ROLLOUT-01 |
| Currencies (Phase B) | + TWD + CNY + KRW | per spec §2.2 |

**Operator runbook — Snipcart account + Stripe connection:**

1. Sign up at https://snipcart.com/ → use operator email (matches WordPress / brand-admin pattern).
2. Free tier confirmation: dashboard → Settings → Plan → confirm "Free" (no payment method required until threshold).
3. Configure Snipcart-wraps-Stripe payment gateway: Dashboard → Settings → Payment gateway → Stripe → Connect → log into the Stripe account the operator picks (**operator chooses which Stripe account; agent never auto-executes financial-system handshakes per `CLAUDE.md`**).
4. Domains: Dashboard → Domains & URLs → Add → `pearlprime.shop` + `pearl-prime-storefront.pages.dev`.
5. Currencies: Dashboard → Regional settings → Currencies → Enable USD + JPY (Phase A); add TWD + CNY + KRW at Phase B.
6. Webhook URL: Dashboard → Webhooks → Add → `https://pearlprime.shop/api/webhook/snipcart` (return 404 OK while Pearl_Dev ws codes the handler).
7. Webhook secret: Dashboard → Webhooks → click the webhook → "Reveal signing key" → copy.
8. Add the webhook secret to Cloudflare Pages env vars: Cloudflare dashboard → Pages → pearl-prime-storefront → Settings → Environment variables → `SNIPCART_WEBHOOK_SECRET` → encrypted → paste.
9. Add API keys to Keychain:
   ```bash
   security add-generic-password -s phoenix-omega -a SNIPCART_API_KEY -w "<the secret key>" -U
   security add-generic-password -s phoenix-omega -a SNIPCART_PUBLIC_API_KEY -w "<the public key>" -U
   security add-generic-password -s phoenix-omega -a SNIPCART_WEBHOOK_SECRET -w "<the webhook secret>" -U
   ```
10. Set the next quarterly rotation reminder (calendar / scheduled task) for `SNIPCART_WEBHOOK_SECRET`.

---

## §7 — Resource ID checklist (operator fills in as resources are created)

Operator-action-required placeholders to populate before Pearl_Dev's application code lands:

- [ ] §1 Pages project — confirmed live URL (post first deploy)
- [ ] §1 Pages project — custom domain `pearlprime.shop` attached (post DNS confirm Q-PRP-DOMAIN-01)
- [ ] §2 D1 database ID
- [ ] §3 R2 bucket (no separate ID — bucket name IS the identifier)
- [ ] §4 KV namespace ID
- [ ] §5 Cloudflare API token — either reuse `CLOUDFLARE_API_TOKEN` OR create `CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT`
- [ ] §6 Snipcart account email
- [ ] §6 Snipcart `SNIPCART_API_KEY` (secret) — Keychain
- [ ] §6 Snipcart `SNIPCART_PUBLIC_API_KEY` (public) — Keychain (used in storefront HTML)
- [ ] §6 Snipcart `SNIPCART_WEBHOOK_SECRET` — Cloudflare Pages env var + Keychain

**Eight operator-action-required slots in total** (5 Cloudflare + 3 Snipcart). Track completion as PRs to this file (replace `<OPERATOR-ACTION-REQUIRED: ...>` placeholders with the actual values; secrets stay in Keychain — NEVER paste secrets into this file).

---

## See also

- `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` §5 (hosting topology) + §AMENDMENT-2026-06-04 (16 Q-PRP-* decisions)
- `skills/pearl-int/references/cloudflare_pages_deploy.md` (Traps 1-4; account split; canonical deploy via CI)
- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` §5 (Cloudflare) — token vars + obtain instructions
- `scripts/ci/integration_env_registry.py` — env var registry rows for `STOREFRONT_*` + `SNIPCART_*`
- `scripts/ci/load_integration_env_from_keychain.py` — Keychain → shell export bridge
- `.github/workflows/pearl-prime-storefront-deploy.yml` — deploy workflow (this PR)
- `.github/workflows/brand-admin-onboarding-pages.yml` — pattern this workflow mirrors
- `skills/pearl-int/references/integration_registry.md` — Storefront row points back at this file
