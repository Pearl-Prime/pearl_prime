# Pearl Prime Storefront — V1

Calm-tech books, audiobooks & manga storefront on Cloudflare Pages + Workers + D1 + R2 + KV.

**Spec:** [`docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md`](../docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md) + §AMENDMENT-2026-06-04 (Snipcart wraps Stripe; optional/guest checkout; Phase A = en-US + ja-JP × book + audiobook + manga; HARD CTA cutover).
**Cap entry:** `PEARL-PRIME-STOREFRONT-V1-01` · **Subsystem:** `storefront`

---

## Layout

| Path | Purpose |
|---|---|
| `public/` | No-build static frontend (plain ES modules + `styles/storefront.css`). Cloudflare Pages serves this dir as-is. |
| `public/app/` | `main.js` (router + pages), `format.js`, `api.js` (calls `/api/*`, falls back to the bundled sample), `cart.js` (Snipcart drop-in + local fallback), `sample_catalog.en-US.json` (committed dev fixture). |
| `functions/` | Pages Functions = the Worker API (`/api/catalog`, `/api/search`, `/api/sku/:id`, `/api/review`, `/api/account/library`, `/api/webhook/snipcart`) + `_lib.js` + `_middleware.js`. |
| `migrations/0001_init.sql` | Canonical D1 schema (spec §7/§9/§10/§11 + AMENDMENT .5). |
| `wrangler.toml` | Pages config; D1/R2/KV bindings commented until the operator provisions them. |
| `seeds/skus.sql` | Generated D1 seed (gitignored — regenerate with `npm run seed`). |

The D1 `sku` table is a **projection cache** of the catalog CSVs (§7.5), produced by
[`scripts/storefront/project_skus.py`](../scripts/storefront/project_skus.py), which joins
`config/storefront/sku_url_map.yaml` (the content-deterministic SKU spine) against the
catalog CSVs. It reuses the spine's `sku_id`, so it can never drift from
`generate_sku_url_map.py`.

## Local development

```bash
# UI only (no API; uses the bundled sample fixture) — fastest:
python3 -m http.server 4321 --directory public

# Full stack (static + Functions + local D1):
cd storefront && npm ci
npm run seed                                   # -> seeds/skus.sql (en-US + ja-JP × book/audiobook/manga)
wrangler d1 execute pearl_prime_storefront --local --file=migrations/0001_init.sql
wrangler d1 execute pearl_prime_storefront --local --file=seeds/skus.sql
npm run dev                                    # wrangler pages dev public (serves functions/ + local D1)
```

## Deploy (CI only — never `wrangler` from a laptop; see `skills/pearl-int/references/cloudflare_pages_deploy.md`)

On merge to `main`, [`pearl-prime-storefront-deploy.yml`](../.github/workflows/pearl-prime-storefront-deploy.yml)
runs `wrangler pages deploy public --project-name=pearl-prime-storefront` (which bundles
`functions/` automatically). Live at `https://pearl-prime-storefront.pages.dev` →
custom domain `pearlprime.shop` (Q-PRP-DOMAIN-01).

After the D1 binding is live, seed production: `npm run seed && wrangler d1 execute pearl_prime_storefront --remote --file=seeds/skus.sql`.

## Operator-gated (batched in `artifacts/coordination/storefront_operator_actions.tsv`)

CF resource provisioning (Pages/D1/R2/KV under account `b80152c319f941e6e92f928e2617a3d5`) ·
`CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` repo secrets · Snipcart account + keys +
`SNIPCART_WEBHOOK_SECRET` + Stripe connection · `pearlprime.shop` DNS · R2 asset upload.
Digital-download files (EPUB/M4B/PNG) depend on the book-assembly track — cart/checkout/covers/SKUs are real now; downloads light up as books assemble.

## Verified

- D1 schema + seed apply cleanly in SQLite (FTS5 search works).
- `project_skus.py`: 17,792 spine entries → 2,956 en-US SKUs, 0 unmatched.
- Frontend: en-US flow (landing → search → PDP → cart → review → library) browser-verified, 0 console errors.
- Worker API: 14/14 handler tests green against the real schema + seed (catalog/search/sku/review/webhook→entitlement/verified-purchase/idempotency).
