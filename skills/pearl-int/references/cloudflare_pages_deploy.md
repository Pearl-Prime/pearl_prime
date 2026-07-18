# Cloudflare Pages — Canonical Deploy Path (READ BEFORE attempting local deploy)

**Last verified:** 2026-06-03
**Account authority note refreshed:** 2026-07-13
**Owner:** Pearl_Int + Pearl_GitHub
**Authority:** `.github/workflows/brand-admin-onboarding-pages.yml` + PR #1412 forensic

---

## TL;DR — Do NOT run `wrangler pages deploy` from a laptop. Use CI.

Phoenix Omega's brand wizard (the music-mode onboarding HTML / brand-wizard-app)
deploys via **GitHub Actions**, not via local `wrangler pages deploy`. Any
local deploy attempt will fail with one of three confusing errors depending
on which account/token combo you try. **The canonical path is: PR → merge to
main → workflow auto-fires → fix live in ~2-3 min on CDN.**

For account authority, use the Cloudflare account that matches the repo's
current `CLOUDFLARE_ACCOUNT_ID` secret. For the current Pages lane that is
`b80152c319f941e6e92f928e2617a3d5`, not the operator OAuth account
`626d6eb8162a8121f74e59235d82a4f5`, and not the older fallback
`0fe2f0679b00fb8a5c3ce830f4144c98`.

---

## Canonical deploy path

1. Make code change in `brand-wizard-app/` (or any path matched by the workflow's `paths:` filter).
2. Open PR via the normal `agent/<slug>-<date>` worktree pattern.
3. Merge after Verify governance + Core tests green (Workers Builds red = OPD-153 noise).
4. The push to `main` automatically triggers `.github/workflows/brand-admin-onboarding-pages.yml`:
   - Builds `brand-wizard-app/dist/` via `npm run build`
   - Deploys via `cloudflare/wrangler-action@v3` using `secrets.CLOUDFLARE_API_TOKEN` + `secrets.CLOUDFLARE_ACCOUNT_ID` (GitHub repo secrets — *NOT* your local Keychain)
   - Target project: **`brand-admin-onboarding`** (`--project-name=brand-admin-onboarding`)
5. Live at `https://brand-admin-onboarding-bu2.pages.dev` (+ whatever custom domain is pointed at it).
6. Watch: `gh run watch <run-id>` or `gh run list --workflow=brand-admin-onboarding-pages.yml --limit 3`.

Typical wall-clock: build ~2 min + deploy ~30 sec + CDN propagation ~30 sec = **~3 min from merge to visible**.

---

## Why local `wrangler pages deploy` does NOT work

There are four traps that have wasted hours of agent time. All four hit in succession during the 2026-06-03 music-mode fix attempt before the CI path was rediscovered.

### Trap 1 — Stale `dist/` (silent)

`wrangler pages deploy dist/` uploads whatever is in `dist/` without checking source freshness. If you forgot `npm run build`, you ship the prior bundle. Symptom: deploy reports success, but the live site shows OLD content.

### Trap 2 — `wrangler.toml` project name is stale

`brand-wizard-app/wrangler.toml` says `name = "phoenix-command"` — that is the **legacy** project name from before the CI workflow standardized on `brand-admin-onboarding`. Local `wrangler pages deploy dist/` with no `--project-name` flag tries to deploy to `phoenix-command`, which lives in a different Cloudflare account this email cannot access. The `--project-name=brand-admin-onboarding` override does not save you, see Trap 4.

### Trap 3 — Cloudflare account split (the real killer)

- Your `ahjansamvara@gmail.com` Cloudflare login → account ID `626d6eb8162a8121f74e59235d82a4f5`. **This account has zero Pages projects.** Confirmed via `wrangler pages project list` returning empty.
- Phoenix Omega's Pages projects (`brand-admin-onboarding`, `phoenix-command`, etc.) live in account ID `b80152c319f941e6e92f928e2617a3d5`. **This account is NOT in your OAuth scope from `ahjansamvara@gmail.com`.** Likely owned by a different email or pre-migration login.
- The GitHub repo secret `CLOUDFLARE_API_TOKEN` is scoped to the `b80152c3...` account — that token is what makes the workflow work. There is no copy of that token in your local Keychain.
- Older worker/dashboard evidence may cite `0fe2f0679b00fb8a5c3ce830f4144c98`. Treat that as historical or lane-specific fallback evidence unless a currently active workflow proves otherwise.

### Trap 4 — Cloudflare API token prefixes are misleading

The integration registry (`scripts/ci/integration_env_registry.py` lines 46-47) says: "cfut_ prefix = Workers Builds (IP-locked); CLOUDFLARE_API_TOKEN_PAGES = no cfut_ prefix, no IP filter". **This guidance is outdated.** As of 2026-06-03, ALL Cloudflare Custom Tokens are issued with the `cfut_` prefix. The real distinguishers are:

1. The token's **permissions** (Account → Cloudflare Pages → Edit + User → User Details → Read).
2. The token's **Account Resources** scope — and here Cloudflare's UI has a trap: **"All accounts" actually returns an empty scope list.** You must explicitly pick "Specific account" → choose the account.
3. The token's **Client IP Filtering** — must be blank for laptop deploys (the original `cfut_Orc...` token in Keychain was IP-locked to Cloudflare's CI IP range — error code 9109 from any other IP).

Even with a perfectly-scoped Custom Token on the right account, if your email doesn't own that account, you cannot list its projects.

---

## Diagnostic shortcuts (when a fix isn't showing)

When operator says "I went to brand wizard, clicked X, didn't see Y," check in this order:

1. **Has the change merged to main?** `git log origin/main --oneline | grep <commit>`. If not, that's the bug — open/merge the PR.
2. **Did the workflow fire?** `gh run list --workflow=brand-admin-onboarding-pages.yml --limit 5`. If no run after merge, check `.github/workflows/brand-admin-onboarding-pages.yml` `paths:` to confirm the file(s) changed match the trigger.
3. **Did the workflow succeed?** `gh run view <id>`. The "Deployment complete!" line tells you the live URL — verify it matches what operator is opening.
4. **Is the live URL serving the new bundle?** Curl the page + grep for the JS bundle hash. Then curl that bundle URL and grep for a marker from your change. (HTTP 200 alone is misleading — Cloudflare Pages SPA fallback returns `index.html` with 200 for any missing path.)
5. **Is operator on a custom domain pointing at a stale project?** `command.phoenixprotocolbooks.com` and similar may DNS-point at the legacy `phoenix-command.pages.dev` project that the workflow does NOT update. Verify domain target via Cloudflare dashboard → relevant Pages project → Custom domains.

---

## The "if you absolutely must deploy from laptop" path

For preview deploys, prototype work, or emergencies where CI is broken:

1. **First, reconcile accounts.** You need access to account `b80152c319f941e6e92f928e2617a3d5`. Likely owned by a separate Cloudflare email login. Find it in your password manager / Cloudflare email invitations. Until you have access to that account, no local deploy will reach the `brand-admin-onboarding` project.
2. Once logged into the right account, create a fresh Custom Token from that account's dashboard context:
   - `https://dash.cloudflare.com/profile/api-tokens` → Create Token → Custom token → Get started
   - Permissions: `Account → Cloudflare Pages → Edit` + `User → User Details → Read`
   - Account Resources: **Specific account** (not "All accounts" — that returns empty) → pick the b80152c3 account
   - Client IP Filtering: **blank**
   - TTL: blank
3. Store as `CLOUDFLARE_API_TOKEN_PAGES` in Keychain:
   ```bash
   security add-generic-password -s phoenix-omega -a CLOUDFLARE_API_TOKEN_PAGES -w "<token>" -U
   ```
4. Deploy command:
   ```bash
   cd /Users/ahjan/phoenix_omega/brand-wizard-app
   npm run build
   TOKEN=$(security find-generic-password -s phoenix-omega -a CLOUDFLARE_API_TOKEN_PAGES -w)
   env -u CLOUDFLARE_API_TOKEN CLOUDFLARE_API_TOKEN="$TOKEN" \
     CLOUDFLARE_ACCOUNT_ID="b80152c319f941e6e92f928e2617a3d5" \
     npx wrangler@latest pages deploy dist/ --project-name=brand-admin-onboarding --commit-dirty=true
   ```

If step 1 isn't possible (you don't own/can't get access to the b80152c3 account), the **only** path is CI. That is the canonical path anyway.

---

## Surface routing — which HTML page is the actual wizard?

The Pages project deploys ~28 HTML surfaces. Most are static pages, one is the React wizard. Easy to edit the wrong one. Map (verified 2026-06-03):

| URL | What it actually is | Edit target if behavior change |
|---|---|---|
| `/pearl_prime_v6-3` (+ `-en`, `-ja`, `-tw`, `-zh`) | **Static slide deck** (1300-line standalone HTML with embedded JS — slide navigation, no React). Contains the "Become a Brand Director" orange CTA that links to `/wizard`. Source: `public/pearl_prime_v6-3*.html`. | Direct HTML edit |
| `/wizard` (+ `-ja`, `-tw`, `-zh`) | **React BrandWizard entry point**. Vite-built from `src/BrandWizard.jsx` (+ locale variants). The "Teacher Books" / "Music Books" IntroJourney mode picker lives here at line ~3437. | `src/BrandWizard*.jsx` |
| `/onboarding` (`onboarding.html`) | Same React BrandWizard — alternate URL, same bundle. | `src/BrandWizard.jsx` |
| `/teacher_showcase` | **Static HTML** teacher grid. `chooseTeacher(id)` saves to localStorage + setTimeout-redirects to `wizard.html?teacher=<id>`. Source: `public/teacher_showcase.html`. | Direct HTML edit |
| `/musician_reflections_survey` | **Static HTML** music brand survey. Submit handler saves to localStorage + redirects to `wizard.html?mode=music&step=1`. Source: `public/musician_reflections_survey.html`. | Direct HTML edit |
| `/brand_admin*`, `/marketing_dashboard`, etc. | Various static HTML dashboards | Direct HTML edit |

**The 2026-06-03 trap that wasted an hour:** the operator said "edit the page at `/pearl_prime_v6-3`" and the buttons they described ("Choose Your Teacher" / "Composite mode"). I assumed those buttons were IN `pearl_prime_v6-3.html`. They were NOT — `pearl_prime_v6-3.html` is a pure slide deck. The buttons live in `src/BrandWizard.jsx` (the React wizard the slide deck LINKS to). Diagnostic: if you're about to edit, first `grep -n "<button-text>" public/<page>.html src/BrandWizard*.jsx` to find which file actually owns the UI string.

## Known stale wrangler.toml — followup needed

`brand-wizard-app/wrangler.toml`:
```toml
name = "phoenix-command"   # ← stale; the CI workflow uses --project-name=brand-admin-onboarding
```

This file should either (a) be updated to `name = "brand-admin-onboarding"` so it matches the actual deploy target, or (b) deleted, since the workflow overrides via `--project-name` anyway. Update gated on confirming `phoenix-command.pages.dev` is dead/unused (currently still returns HTTP 200 with stale content from a prior account's deploy).

Track via a Pearl_Dev ws: `ws_wrangler_toml_project_name_realign_<date>`.

---

## See also

- `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` § 5 (Cloudflare) — token vars + obtain instructions
- `docs/VIDEO_CLOUDFLARE_FLUX_CREDENTIALS.md` — Workers AI token (different scope: AI, not Pages)
- `.github/workflows/brand-admin-onboarding-pages.yml` — the canonical deploy workflow
- `scripts/ci/integration_env_registry.py` lines 45-50 — registry rows for Cloudflare vars (some outdated re cfut_ prefix; see Trap 4)
- `skills/pearl-int/references/cloudflare_surface_map.md` — account-authority and keep/retire map
- Memory anchor in `~/.claude/projects/-Users-ahjan-phoenix-omega/memory/project_known_good_anchors.md`: "Cloudflare Pages deploy = CI-only path"
