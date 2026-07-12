# Pearl Prime Cloudflare Git Integration Runbook

**Purpose:** operator procedure for the noisy `Workers Builds: pearl-prime` GitHub check.

## Current truth

Verified on 2026-07-13:

- PR `#5576` merged normally even though `Workers Builds: pearl-prime` was red
- the repo-owned worker contract still built locally from repo root with:
  - `npm ci`
  - `npm run build:worker`
- the failing Cloudflare check linked to account `626d6eb8162a8121f74e59235d82a4f5`
- Pearl_Int's current Pages/storefront authority map still points at `b80152c319f941e6e92f928e2617a3d5` for the secret-backed Pages lane
- older repo docs and handoffs also reference `0fe2f0679b00fb8a5c3ce830f4144c98`

Treat hard-coded Cloudflare account IDs in older docs as historical evidence unless they match the current lane's secret-backed authority. Also do not infer current Pages authority from the account attached to a detached worker-build surface.

## Recommendation

If `pearl-prime` remains a non-authoritative worker surface, prefer **Path A: Disconnect**. Rebind only if you intentionally want Cloudflare Git builds and PR check runs for this worker.

## Path A: Disconnect the noisy build surface

Use this when you want PR noise to stop and do not need automatic Cloudflare Git builds for `pearl-prime`.

1. In the Cloudflare dashboard, go to **Workers & Pages**.
2. Open the `pearl-prime` Worker in the intended account.
3. Go to **Settings > Builds**.
4. Select **Disconnect**.
5. Open a small test PR and verify GitHub no longer receives the `Workers Builds: pearl-prime` check run.

Optional GitHub-side cleanup:

1. Go to [GitHub app installations](https://github.com/settings/installations).
2. Open **Cloudflare Workers and Pages**.
3. Select **Configure**.
4. Set **Repository access** to **Only select repositories**.
5. Deselect `Ahjan108/phoenix_omega_v4.8` if you want this repo excluded entirely.

Use full uninstall only if you want to revoke Cloudflare's access to the whole GitHub account. That affects other connected Workers or Pages projects too.

## Path B: Rebind and keep the integration

Use this when you want Cloudflare Git builds to remain active for `pearl-prime`.

### 1. Pick the intended account first

Cloudflare recommends one GitHub account installation map to one Cloudflare account. Before reconnecting anything, confirm which Cloudflare account should own the `pearl-prime` Worker.

Important: the intended worker-build account can differ from the repo's current Pages/storefront account. Do not "fix" the worker by silently rebinding Pages authority to the worker account.

### 2. Fix GitHub app scope

1. Go to [GitHub app installations](https://github.com/settings/installations).
2. Open **Cloudflare Workers and Pages**.
3. Select **Configure**.
4. Under **Repository access**, choose **Only select repositories**.
5. Ensure `Ahjan108/phoenix_omega_v4.8` is explicitly selected.

### 3. Reconnect from Cloudflare

1. In the intended Cloudflare account, open **Workers & Pages**.
2. Open `pearl-prime`.
3. Go to **Settings > Builds**.
4. Select **Manage** if the repo is already attached, or **Connect** if it is not.
5. If repository access looks broken, reinstall the **Cloudflare Workers and Pages** GitHub app and reconnect from the Worker builds screen.

### 4. Confirm the worker contract

The following must match the repo:

- Worker name: `pearl-prime`
- Wrangler config: [wrangler.jsonc](../../wrangler.jsonc)
- Entrypoint: [cloudflare/pearl_prime_worker.js](../../cloudflare/pearl_prime_worker.js)
- Root manifest: [package.json](../../package.json)

If the dashboard worker name and `wrangler.jsonc` name diverge, Workers Builds can fail even when the repo code is fine.

### 5. Confirm build settings

Use repo root as the Worker root directory.

Preferred deploy command:

```bash
npx wrangler deploy
```

Equivalent repo script:

```bash
npm run deploy
```

If dependency installation is the problem, set build variable `SKIP_DEPENDENCY_INSTALL=true` and use:

```bash
npm ci && npx wrangler deploy
```

### 6. Reduce false triggers

If you keep the integration, tighten it so unrelated PRs do not trigger this Worker.

Branch control:

- production branch: `main`
- disable non-production branch builds unless you actively want preview builds on feature branches

Build watch paths:

- include:
  - `cloudflare/pearl_prime_worker.js`
  - `wrangler.jsonc`
  - `package.json`
  - `package-lock.json`
  - `.github/workflows/pearl-prime-worker-build-verify.yml`
- exclude:
  - `docs/*`
  - `artifacts/*`

Note: Workers Builds may still bypass path filtering on unusually large pushes.

### 7. Retry and verify

1. In Cloudflare, open **Deployments** or **Build history** for `pearl-prime`.
2. Retry the latest failed build.
3. Confirm the next GitHub check run points to the intended Cloudflare account.
4. Confirm the build either turns green or at least emits a real error log instead of an instant opaque failure.

## Local verification

Before blaming repo code, run the repo-owned mirror:

```bash
npm ci
npm run build:worker
```

If that succeeds but the GitHub check still fails instantly, suspect Git integration state, account binding, repository access, or build-token drift before suspecting worker code.
