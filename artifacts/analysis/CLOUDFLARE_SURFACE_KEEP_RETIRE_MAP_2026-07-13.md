# Cloudflare Surface Keep/Retire Map — 2026-07-13

## Purpose

Separate the Cloudflare surfaces Phoenix Omega actually wants from the ones that are legacy, noisy, or misleading.

This is the clean answer to:

- why Cloudflare was introduced at all
- which Cloudflare surfaces are real product infrastructure
- which Cloudflare surfaces should be retired
- what the 2026-07-13 `pearl-prime` disconnect actually fixed

## Executive verdict

Cloudflare is not one thing in this repo. It is four different categories:

1. **Real product hosting surfaces we want**
2. **Real storage / media infrastructure we want**
3. **Planned storefront infrastructure we still likely want**
4. **A small legacy/noise worker surface we do not need**

The `pearl-prime` Worker Git-build integration that we disconnected on 2026-07-13 belongs in category 4. It was not the real Cloudflare strategy. It was a detached, non-authoritative check surface that kept creating false-red PR noise.

## Why Cloudflare was done in the first place

Per Pearl_Architect, Pearl_Int, and the storefront specs, Cloudflare was introduced for real platform reasons:

- **Pages** for hosted frontend surfaces like the brand wizard, freebie capture pages, and branded web experiences
- **Workers / Pages Functions** for lightweight server-side endpoints close to the frontend
- **D1 + KV + R2** for a Cloudflare-native storefront/data plane
- **R2** for binary artifact offload and content-feed publishing
- **Workers AI** for image-generation wiring

Those are real reasons. The tiny `pearl-prime` Worker check was not one of the core business reasons.

## Keep now

### 1. Brand admin / brand wizard Pages deploy surface

**Why keep it**

- This is a real user-facing surface.
- It is the canonical deploy path for the brand wizard and related freebie/onboarding pages.
- Pearl_Int explicitly documents this as a CI-owned deploy path, not a laptop flow.

**Authority**

- [brand-admin-onboarding-pages.yml](../../../.github/workflows/brand-admin-onboarding-pages.yml)
- [skills/pearl-int/references/cloudflare_pages_deploy.md](../../../skills/pearl-int/references/cloudflare_pages_deploy.md)
- [GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md](../../../docs/GHL_ADMIN_HANDOFF_FREEBIE_CAPTURE.md)

**Status**

- Keep
- Active / meaningful
- Needs account-authority reconciliation

### 2. R2 binary artifact offload

**Why keep it**

- This is a real infra strategy to stop repo/worktree growth from generated binaries.
- It is part of the “cloud-native agents” storage plan, not random experimentation.

**Authority**

- [CLOUD_NATIVE_AGENTS_LAYER2.md](../../../docs/CLOUD_NATIVE_AGENTS_LAYER2.md)
- `scripts/artifacts/r2_sync.py`
- `scripts/artifacts/setup_r2.sh`

**Status**

- Keep
- Real infra value
- Not tied to the `pearl-prime` worker noise

### 3. GHL marketing-feed publishing to R2

**Why keep it**

- This is an actual content-delivery surface: publishing `marketing_feed.json` to R2/CDN for operational use.

**Authority**

- [provision-pearl-prime-content-ghl.yml](../../../.github/workflows/provision-pearl-prime-content-ghl.yml)

**Status**

- Keep
- Real delivery surface
- Separate from the disconnected `pearl-prime` worker check

### 4. Workers AI / FLUX image-generation wiring

**Why keep it**

- This is a real feature integration for image generation in video/cover workflows.

**Authority**

- [VIDEO_AND_COVER_ART_FLUX_WIRING.md](../../../docs/VIDEO_AND_COVER_ART_FLUX_WIRING.md)

**Status**

- Keep
- Real capability
- Not affected by the `pearl-prime` worker disconnect

## Keep, but planned / not yet cleanly live

### 5. Pearl Prime storefront on Cloudflare Pages + Workers + D1 + R2 + KV

**Why keep it**

- This is the actual Pearl_Architect vision for owning the paid-content destination instead of sending users to third-party platforms.
- It is strategically meaningful: marketplace, reviews, checkout flow, assets, session/cart state.

**Authority**

- [PEARL_PRIME_STOREFRONT_V1_SPEC.md](../../../docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md)
- [PEARL_ARCHITECT_STATE.md](../../../docs/PEARL_ARCHITECT_STATE.md)
- [pearl-prime-storefront-deploy.yml](../../../.github/workflows/pearl-prime-storefront-deploy.yml)
- [storefront/wrangler.toml](../../../storefront/wrangler.toml)

**Status**

- Keep
- Strategically real
- Scaffold exists
- Not launch-clean yet
- Requires account/resource reconciliation and operator provisioning

## Retire

### 6. `pearl-prime` Worker Git-build attachment as a PR signal

**Why retire**

- It was non-authoritative by contract.
- It had zero in-repo consumers.
- It repeatedly created false-red PR checks and bad merge habits.
- Its only stated purpose was to give Cloudflare Git integration something to build.

**Authority**

- [PEARL_PRIME_RELEASE_CONTRACT.md](../../../docs/PEARL_PRIME_RELEASE_CONTRACT.md)
- [PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md](../../../docs/PEARL_PRIME_CLOUDFLARE_DEPLOYMENT.md)
- [workers_builds_pearl_prime_audit_2026-04-27.md](../audits/workers_builds_pearl_prime_audit_2026-04-27.md)

**Status**

- Retire as a GitHub check surface
- Disconnected in Cloudflare dashboard on 2026-07-13
- Keep source files only if you still want the contract stub in-repo

### 7. Treating `Workers Builds: pearl-prime` as release or merge truth

**Why retire**

- The repo’s own governance docs say it is non-blocking.
- It is not the authoritative release readiness surface.

**Authority**

- [GITHUB_OPERATIONS_FRAMEWORK.md](../../../docs/GITHUB_OPERATIONS_FRAMEWORK.md)
- [BRANCH_PROTECTION_REQUIREMENTS.md](../../../docs/BRANCH_PROTECTION_REQUIREMENTS.md)
- [PEARL_PRIME_RELEASE_CONTRACT.md](../../../docs/PEARL_PRIME_RELEASE_CONTRACT.md)

**Status**

- Retire the mental model entirely

### 8. Local laptop `wrangler pages deploy` as the normal path

**Why retire**

- Pearl_Int’s runbook is explicit that this is the wrong operational habit for the important Pages surfaces.
- It leads to stale builds, wrong accounts, wrong project names, and misleading success states.

**Authority**

- [skills/pearl-int/references/cloudflare_pages_deploy.md](../../../skills/pearl-int/references/cloudflare_pages_deploy.md)

**Status**

- Retire as the default operator behavior
- Keep only as an emergency path after account reconciliation

### 9. Legacy `phoenix-command` Pages naming/path assumptions

**Why retire**

- The runbook explicitly calls this a stale project-name trap.
- It causes operators and agents to target the wrong project.

**Authority**

- [skills/pearl-int/references/cloudflare_pages_deploy.md](../../../skills/pearl-int/references/cloudflare_pages_deploy.md)

**Status**

- Retire stale assumptions
- Replace with a single canonical project-name map

## Reconcile before more Cloudflare work

These are not “retire” items. They are real blockers or drift that need one source of truth.

### 10. Account authority drift: `626d6...` vs `b80152c3...` vs older `0fe2...`

Current repo truth is split:

- the disconnected `pearl-prime` worker Git-build surface was attached to account `626d6eb8162a8121f74e59235d82a4f5`
- the Pearl_Int Pages runbook says the important Pages projects live under `b80152c319f941e6e92f928e2617a3d5`
- older audits and handoffs reference `0fe2f0679b00fb8a5c3ce830f4144c98`
- `brand-admin-onboarding-pages.yml` comments currently cite `626d6...`, which conflicts with Pearl_Int’s runbook

**Meaning**

The real Cloudflare problem is not “Cloudflare is bad.” It is that the account map drifted and the repo now contains multiple historical truths.

### 11. Secret authority drift for Pages deploys

The repo contains conflicting assumptions about which account `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` point at.

This must be reconciled before treating any Pages/Storefront deploy lane as clean.

## What the 2026-07-13 disconnect helped

The disconnect fixed a **noise problem**, not the entire Cloudflare program.

It helped by:

- stopping a non-authoritative PR red check from the `pearl-prime` worker surface
- removing one major source of merge confusion
- separating “real Cloudflare product work” from “legacy Cloudflare noise”

It did **not**:

- reconcile the real account split
- prove storefront provisioning is correct
- settle the brand-admin Pages account authority
- remove the need for a clean Cloudflare surface map

## Recommended next actions

### Immediate

1. Keep the `pearl-prime` worker Git-build integration disconnected.
2. Do not reattach it unless the worker becomes a real load-bearing surface.

### Short follow-on

1. Audit which Cloudflare account actually owns:
   - `brand-admin-onboarding`
   - `pearl-prime-storefront`
   - `phoenix-omega-artifacts`
   - `pearl-prime-content`
2. Reconcile repo comments, runbooks, and workflow headers to one account map.

### Real Cloudflare program

1. Preserve / maintain the Pages deploy path for brand-admin / freebie surfaces.
2. Preserve / maintain R2 for artifacts and marketing-feed publishing.
3. Decide whether Pearl Prime storefront is still an active business goal.
4. If storefront is still active, validate D1/R2/KV resource IDs and CI secrets under the intended account before any more build/debug work.

## Bottom line

**What we actually want from Cloudflare**

- Pages-hosted customer/admin surfaces
- R2 storage and content delivery
- Workers AI where it is truly wired
- potentially the full Pearl Prime storefront stack

**What we do not want**

- detached, non-authoritative Git-build noise from the tiny `pearl-prime` worker
- stale project-name/account assumptions
- local deploy habits that bypass the repo’s actual CI ownership model
