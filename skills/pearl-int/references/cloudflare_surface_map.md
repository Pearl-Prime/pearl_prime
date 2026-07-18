# Cloudflare Surface Map — account authority and surface routing

**Last updated:** 2026-07-13
**Owner:** Pearl_Int
**Purpose:** tell Phoenix Omega agents which Cloudflare account is authoritative for which surface, and prevent old worker/build noise from being mistaken for current Pages authority.

---

## Authority rule

Use the Cloudflare account that matches the repo's current `CLOUDFLARE_ACCOUNT_ID` secret.

For this repo's current Pages lane, that means:

- **Authoritative Pages/storefront account:** `b80152c319f941e6e92f928e2617a3d5`
- **Not the operator OAuth account:** `626d6eb8162a8121f74e59235d82a4f5`
- **Not the older worker/dashboard fallback account:** `0fe2f0679b00fb8a5c3ce830f4144c98`

If a dashboard screen, worker check, or older handoff points at a different account, do not automatically promote that account to live authority. First ask whether that surface is a different lane, a detached worker surface, or historical evidence only.

## Evidence chain

- [`docs/sessions/SESSION_HANDOFF_2026-06-03.md`](../../../docs/sessions/SESSION_HANDOFF_2026-06-03.md) says the operator OAuth account `626d6eb8...` was empty for Pages, while Phoenix Omega's Pages projects were on `b80152c3...` and reached via `CLOUDFLARE_API_TOKEN`.
- [`docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md`](../../../docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md) records `0fe2f067...` as an older worker/dashboard fallback account, not the current Pages authority.
- [`docs/handoffs/GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md`](../../../docs/handoffs/GHL_MULTI_BRAND_FUNNEL_WORKFLOW.md) references `626d6eb8...` for a different project lane, which is why repo docs look mixed if they are read without lane context.

## Account map

| Account ID | Meaning | Use it for | Do not use it for |
|---|---|---|---|
| `b80152c319f941e6e92f928e2617a3d5` | Phoenix Omega Pages authority | `brand-admin-onboarding`, current Pages CI lane, `pearl-prime-storefront`, secret-backed deploy workflows | inferring operator login ownership from OAuth alone |
| `626d6eb8162a8121f74e59235d82a4f5` | Operator OAuth account | dashboard actions that truly belong to that account; some detached worker/build surfaces may still live here | current Phoenix Omega Pages authority |
| `0fe2f0679b00fb8a5c3ce830f4144c98` | Older worker/dashboard fallback | historical audits only, unless a specific legacy worker is proven live there | any current Pages/storefront lane by default |

## Surface map

### Keep / authoritative now

- **Brand-admin / brand-wizard Pages CI deploys**
  - Account: `b80152c3...`
  - Authority: repo secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`
  - Runbook: [`cloudflare_pages_deploy.md`](./cloudflare_pages_deploy.md)
- **Pearl Prime storefront scaffold**
  - Account: `b80152c3...`
  - Authority: [`storefront_resource_ids.md`](./storefront_resource_ids.md) + deploy workflow
- **R2 artifact/storage lanes**
  - Account: whichever account owns the named bucket for that lane
  - Do not assume R2 ownership from a Pages worker screen
- **Workers AI**
  - Separate token/scope question from Pages
  - See `docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md`

### Keep, but verify lane ownership before acting

- **GHL / multi-brand funnel Cloudflare references**
  - Some docs cite `626d6eb8...`
  - Treat these as lane-specific until the exact workflow/resource is matched

### Retire as authority

- **`Workers Builds: pearl-prime` as PR truth**
  - Non-authoritative worker build surface
  - Can live in a different account than Pages
  - Do not infer Pages/storefront account ownership from it
- **Local `wrangler pages deploy` as the normal path**
  - Keep only as an emergency/manual path after account reconciliation
- **Any assumption that `phoenix-command` naming proves current authority**
  - Treat as legacy until explicitly re-verified

## Operating rules for Pearl_Int

1. When touching a Pages or storefront lane, start from the repo secret-backed account assumption, not the operator OAuth dashboard tab.
2. When a doc and a dashboard disagree, prefer the lane-specific workflow plus the current `CLOUDFLARE_ACCOUNT_ID` secret mapping.
3. When a worker build check is red, do not assume the current Pages lane is broken.
4. When a surface is unclear, classify it first:
   - Pages deploy surface
   - Worker/build surface
   - R2/storage surface
   - Workers AI surface
   - historical evidence only

## See also

- [`cloudflare_pages_deploy.md`](./cloudflare_pages_deploy.md)
- [`storefront_resource_ids.md`](./storefront_resource_ids.md)
- [`../../../artifacts/analysis/CLOUDFLARE_SURFACE_KEEP_RETIRE_MAP_2026-07-13.md`](../../../artifacts/analysis/CLOUDFLARE_SURFACE_KEEP_RETIRE_MAP_2026-07-13.md)
