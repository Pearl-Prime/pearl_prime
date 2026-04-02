# Pearl Prime Cloudflare Deployment Contract

**Purpose:** Define the repo-owned Cloudflare deployment surface for the `pearl-prime` worker check so the external Cloudflare build is backed by versioned repo truth.

## Scope

This contract covers only the Cloudflare Worker build target that emits the GitHub check:

- `Workers Builds: pearl-prime`

It does **not** replace the authoritative Pearl Prime release signal in [`docs/PEARL_PRIME_RELEASE_CONTRACT.md`](./PEARL_PRIME_RELEASE_CONTRACT.md). The authoritative release path remains the repo-owned GitHub workflow and evidence bundle.

## Repo-owned deployment files

- Worker config: [`wrangler.jsonc`](../wrangler.jsonc)
- Worker entrypoint: [`cloudflare/pearl_prime_worker.js`](../cloudflare/pearl_prime_worker.js)

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
