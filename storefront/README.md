# Pearl Prime Storefront — V1 infrastructure scaffold

**Status:** infra scaffold only — application code lands via a subsequent Pearl_Dev ws.
**Owner:** Pearl_Int (operations) → Pearl_Dev (application)
**Spec:** [`docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md`](../docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md) §5 (hosting topology)
**AMENDMENT:** §AMENDMENT-2026-06-04 — Snipcart wraps Stripe (PRIMARY) + optional/guest checkout + HARD CTA cutover + full Phase A launch surface (en-US + ja-JP × book + audiobook + manga) + per-album + per-track + per-brand-sub music SKUs at Phase B.
**Cap entry:** `PEARL-PRIME-STOREFRONT-V1-01` (active per AMENDMENT)
**Subsystem:** `storefront` (see `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`)
**Parent PRs:** [#1433](https://github.com/Ahjan108/phoenix_omega/pull/1433) (spec), [#1446](https://github.com/Ahjan108/phoenix_omega/pull/1446) (AMENDMENT)

---

## What this PR scaffolds

This is an **infrastructure scaffold** only. It introduces:

| Path | Purpose |
|---|---|
| `package.json` | Minimal Vite + TypeScript bootstrap (Pearl_Dev replaces with framework + deps) |
| `wrangler.toml` | Cloudflare Pages project config — `name = "pearl-prime-storefront"` (NOT `phoenix-command`); D1/R2/KV bindings sketched but commented until operator provisions |
| `migrations/0001_init.sql` | Empty placeholder so wrangler can wire D1 at first deploy |
| `.gitignore` | `dist/`, `node_modules/`, `.wrangler/`, `.vite/` |
| `../.github/workflows/pearl-prime-storefront-deploy.yml` | Deploy workflow mirroring `brand-admin-onboarding-pages.yml` |
| `../skills/pearl-int/references/storefront_resource_ids.md` | Operator-action-required runbook for the 5 CF + 3 Snipcart placeholders |
| `../skills/pearl-int/references/integration_registry.md` | New **Storefront** entry pointing at `storefront_resource_ids.md` + deploy workflow |
| `../scripts/ci/integration_env_registry.py` | 7 new env-var rows for storefront secrets (loaded from macOS Keychain locally; populated as GitHub repo secrets for CI) |

## What this PR does NOT do

- **No Cloudflare resources are actually provisioned.** Provisioning requires operator dashboard logins (CF account `b80152c319f941e6e92f928e2617a3d5`) — those can NOT be done from a CLI agent session. See `skills/pearl-int/references/storefront_resource_ids.md` for the operator-action runbook.
- **No Snipcart account is created.** Snipcart account creation requires operator email + dashboard login. Runbook in same reference.
- **No Stripe connection.** Per `CLAUDE.md` Tier policy, agent sessions never auto-execute financial-system handshakes. Operator connects Snipcart's payment gateway to Stripe via the Snipcart dashboard UI flow.
- **No application code.** No frontend components, no Pages Functions, no D1 schemas beyond the placeholder. Pearl_Dev ws follows after this PR merges + UI mockup approval.

## Deploy path

Once Pearl_Dev's application code lands and the operator has provisioned the CF resources + Snipcart account, the deploy is fully automated:

1. PR merges to `main` matching `storefront/**` or `.github/workflows/pearl-prime-storefront-deploy.yml`.
2. `pearl-prime-storefront-deploy.yml` auto-fires.
3. `wrangler-action@v3` deploys via repo secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`.
4. Live at `https://pearl-prime-storefront.pages.dev` (and the operator-chosen custom domain — Q-PRP-DOMAIN-01).

**DO NOT run `wrangler pages deploy` from a laptop.** See `skills/pearl-int/references/cloudflare_pages_deploy.md` Traps 1-4.

## Local development (for Pearl_Dev follow-up ws)

```bash
cd storefront/
npm ci
npm run dev   # vite dev server
npm run build # vite build → dist/
```

## Worktree pattern used to author this scaffold

This scaffold was authored from a `--no-checkout` worktree per memory anchor `feedback_git_worktree_for_lock_contention` to avoid the main tree's persistent `index.lock` contention:

```bash
git worktree add --no-checkout -b agent/pearl-int-storefront-v1-cf-snipcart-wiring-20260606 /private/tmp/wt-pp-int-cf-snipcart-20260606 origin/main
cd /private/tmp/wt-pp-int-cf-snipcart-20260606
git restore --staged .
git checkout HEAD -- <only-files-needed-for-the-task>
# ... author scaffold files ...
git config lfs.locksverify false
PYTHONPATH=. python3 scripts/git/push_guard.py
bash scripts/ci/preflight_push.sh
gh pr list --search "storefront wiring" --state all --limit 10
git add <specific files only>
git commit -m "..."
git push -u origin agent/pearl-int-storefront-v1-cf-snipcart-wiring-20260606
```

## Next steps (post-merge)

1. **Operator action:** provision CF resources (Pages project + D1 + R2 + KV) under account `b80152c3...`. Step-by-step runbook in `skills/pearl-int/references/storefront_resource_ids.md`.
2. **Operator action:** create Snipcart account + connect Stripe + configure webhook secret. Runbook in same reference.
3. **Pearl_Dev ws:** ratify UI mockups from `ws_pearl_prime_storefront_v1_ui_mockups_20260603`, then scaffold the actual application code (frontend bundle, Pages Functions, D1 schema migrations 0002+).
4. **Pearl_Marketing ws:** sweep paid CTAs across surfaces per spec §14 HARD cutover at launch day (zero coexistence).
