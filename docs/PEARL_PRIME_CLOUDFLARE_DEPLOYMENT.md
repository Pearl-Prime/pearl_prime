# Pearl Prime Cloudflare Deployment Contract

**Purpose:** Define the repo-owned Cloudflare deployment surface for the `pearl-prime` worker check so the external Cloudflare build is backed by versioned repo truth.

## Scope

This contract covers only the Cloudflare Worker build target that emits the GitHub check:

- `Workers Builds: pearl-prime`

It does **not** replace the authoritative Pearl Prime release signal in [`docs/PEARL_PRIME_RELEASE_CONTRACT.md`](./PEARL_PRIME_RELEASE_CONTRACT.md). The authoritative release path remains the repo-owned GitHub workflow and evidence bundle.

## Repo-owned deployment files

- Worker config: [`wrangler.jsonc`](../wrangler.jsonc)
- Worker entrypoint: [`cloudflare/pearl_prime_worker.js`](../cloudflare/pearl_prime_worker.js)
- Root build manifest: [`package.json`](../package.json) + [`package-lock.json`](../package-lock.json) (wrangler only; satisfies Cloudflare Workers Builds dependency install in this monorepo)

## Contract

- Cloudflare worker name must be `pearl-prime`
- Cloudflare build entrypoint must be `cloudflare/pearl_prime_worker.js`
- The worker must build from repo root without an additional build step
- The health endpoint must answer on:
  - `/`
  - `/healthz`

## Response contract

Successful health responses return JSON with at least:

- `service`
- `status`
- `contract_version`

## Operational note

This contract exists so the Cloudflare GitHub integration has a real, versioned build target in this repo. Until the external Cloudflare check is observed green on `main`, it remains non-authoritative for release readiness.

## Live integration drift

Verified on 2026-07-13 while investigating PR `#5576`:

- the repo-owned CI mirror succeeded from repo root with `npm ci` + `npm run build:worker`
- the Cloudflare GitHub check failed instantly and exposed no GitHub-visible annotations
- the failing check linked to account `626d6eb8162a8121f74e59235d82a4f5`
- the current Pages/storefront authority in Pearl_Int's lane map remains `b80152c319f941e6e92f928e2617a3d5`, which is the account tied to the repo's current Pages secret-backed lane
- older session docs and prior fallbacks referenced account `0fe2f0679b00fb8a5c3ce830f4144c98`

Implication: the worker-build account and the Pages account are not the same authority surface. Hard-coded Cloudflare account IDs in older handoffs are historical evidence unless they match the current lane's secret-backed account. Confirm the intended Cloudflare surface first, then confirm the account.

### Cloudflare Workers Builds (monorepo)

The repo has additional `package.json` files under `brand-wizard-app/` and `storefront/`. Without a root manifest, Workers Builds can fail during dependency install before `npx wrangler deploy` runs.

**Repo-side fix:** root `package.json` installs only `wrangler`. Deploy command should remain `npx wrangler deploy` (or `npm run deploy`) with an empty optional build command.

**Node pin:** Cloudflare Workers Builds runs Node 20.x. Wrangler 4.87+ requires Node 22; root manifest pins `4.86.0`.

**Dashboard fallback:** first confirm the intended Cloudflare account for `pearl-prime`. After that, if builds still fail, set build env `SKIP_DEPENDENCY_INSTALL=true` and deploy command `npm ci && npx wrangler deploy`. Root directory: repository root.

**CI mirror:** [`.github/workflows/pearl-prime-worker-build-verify.yml`](../.github/workflows/pearl-prime-worker-build-verify.yml) runs `npm ci` + `wrangler deploy --dry-run` on worker file changes.

**Operator runbook:** [docs/runbooks/PEARL_PRIME_CLOUDFLARE_GIT_INTEGRATION_RUNBOOK.md](./runbooks/PEARL_PRIME_CLOUDFLARE_GIT_INTEGRATION_RUNBOOK.md) documents the two supported paths:

- disconnect the Cloudflare Git integration to eliminate non-authoritative PR noise
- rebind the integration cleanly, with branch control and build-watch-path limits, if the check surface is intentionally retained
