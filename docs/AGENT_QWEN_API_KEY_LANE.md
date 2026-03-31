# Agent instruction — Qwen API key lane (not local runtime)

**Audience:** Pearl_Dev, Pearl_GitHub, and any automation describing work on branch `agent/qwen3-live-run-20260331`.

---

## Read this first (send to Pearl_Dev / Pearl_GitHub)

```text
Important: in this repo, qwen3 means the Qwen API key lane, not a local LM Studio/Ollama/llama.cpp runtime.

Use the checked-out repo on branch `agent/qwen3-live-run-20260331` at commit `f45f1a1c`.
Run the validation/build/push steps there, then open the PR to `main`.
After merge, trigger `brand-admin-onboarding-pages.yml`.
```

---

## Dev — repo checkout / working tree

```bash
cd /path/to/phoenix_omega_v4.8

git checkout agent/qwen3-live-run-20260331
git pull --ff-only

python3 scripts/ci/validate_onboarding_registry.py
bash scripts/onboarding/sync_onboarding_config_to_public.sh
cd brand-wizard-app && npm run build && cd ..

git status
git push origin agent/qwen3-live-run-20260331
```

---

## GitHub agent — open the PR

Create a **draft PR** from:

* `agent/qwen3-live-run-20260331` → `main`

**Title**

```text
Brand admin onboarding Pages deploy + onboarding proof system scaffolds
```

**Body** — use **exactly** the following (paste into GitHub as the PR description):

```md
## Summary

This PR lands the brand admin onboarding Pages workflow on `main` so it becomes visible in GitHub Actions and can be triggered from the Actions UI / `gh workflow run`.

It also includes the onboarding proof-system scaffolds and related config/UI work that support the brand admin onboarding experience.

## Why this is needed

GitHub only exposes a workflow in Actions after the workflow file exists on the default branch.

Before this merge:

- `.github/workflows/brand-admin-onboarding-pages.yml` exists only on this branch
- it does not exist on `main`
- the workflow therefore does not appear in the Actions sidebar
- `gh workflow run brand-admin-onboarding-pages.yml` returns 404

After merge:

- the workflow will appear under Actions
- it can be triggered from the UI or CLI
- Cloudflare Pages deployment should run using the existing `CLOUDFLARE_*` GitHub secrets

## Included in this PR

### Deployment / workflow
- add `.github/workflows/brand-admin-onboarding-pages.yml`
- add Cloudflare Pages deployment doc
- add onboarding Pages spec

### Brand admin onboarding surfaces
- add `brand_admin_master_onboarding.html`
- add `brand_admin_weekly_os.html`
- add `lane_examples_gallery.html`
- add `market_lane_matrix.html`
- update `brand_onboarding_hub.html`

### Onboarding proof system / wizard support
- add onboarding registry + decision explainer JSON
- add React onboarding components:
  - `OutputProofStrip.jsx`
  - `LaneChoiceCard.jsx`
  - `MarketChoiceCard.jsx`
  - `DecisionImpactSummary.jsx`
  - registry matching/loading helpers
- add sync + validation scripts for onboarding registry

### Proof asset change in this pass
- replace Picsum proof placeholders with committed repo seed SVGs under `brand-wizard-app/public/onboarding/proof/`
- keep one intentionally stale-ready demo row for gallery fallback behavior
- allow optional `placeholder_reason` in registry validation
- ensure repo-root static serving resolves `/onboarding/...` assets correctly during local smoke tests

### Safety / hygiene
- update `.gitignore` to exclude local Cloudflare credential scratch files from accidental commit

## Important scope note

This branch also contains additional supporting work outside the narrow Pages deploy path, including related specs/docs plus duration, manga, research, video, fixtures, tests, and generated artifacts.

Reviewers should treat this as a broader branch merge, not a workflow-only change.

## Post-merge steps

1. Trigger:

   ```bash
   gh workflow run brand-admin-onboarding-pages.yml
   ```

   or select **Brand admin onboarding (Pages)** in GitHub Actions.

2. Confirm deploy completes successfully.

3. Smoke test the live Pages site:

   * open the Cloudflare Pages domain
   * in DevTools Network, confirm:

     * `GET /onboarding/example_registry.json` → `200`
   * confirm seed SVGs load from:

     * `/onboarding/proof/<id>.svg`
   * in app:

     * verify Primary Reader proof strip shows IDs
     * verify at least one ready example renders
     * verify stale fallback behavior in the gallery

4. After confirming GitHub secrets are working, delete any remaining local credential scratch files if still present.

5. If the Cloudflare token was ever exposed, rotate it and update `CLOUDFLARE_API_TOKEN` in GitHub secrets.

## Risk

Medium, because this branch includes more than the deployment workflow alone.

## Expected result

The onboarding Pages workflow is available on `main`, deploys from GitHub Actions, and the onboarding proof surfaces can be smoke-tested on the live Cloudflare Pages site.
```

---

## After merge — run and smoke test

```bash
gh workflow run brand-admin-onboarding-pages.yml
```

Then verify:

```text
https://brand-admin-onboarding.pages.dev/onboarding/example_registry.json
https://brand-admin-onboarding.pages.dev/onboarding/proof/cmp_bp_founder_v1.svg
```

In the UI, check:

* Primary Reader proof strip shows IDs
* at least one seed SVG renders
* stale-ready gallery fallback still works

---

## Cleanup

```bash
rm -f ~/Desktop/cloudflare_credentials.txt
rm -f docs/cloudflare_credentials.txt
rm -f .claude/cloudflare_credentials.txt
```

If the token was ever exposed, rotate it in Cloudflare and update the GitHub secret.

---

## Reference — what `qwen3` means in this repo

**Qwen3 is the model/API lane for this branch, not a GitHub workflow name and not a local runtime.**

This repo’s **standard** for research and related automation is the **Qwen API key path**: OpenAI-compatible HTTP with `QWEN_BASE_URL`, `QWEN_API_KEY`, and `QWEN_MODEL` (GitHub Actions secrets or the documented fallback files under `docs/qwen_*.txt`).

Do **not** describe this task as local Qwen, LM Studio, Ollama, or llama.cpp unless you are explicitly documenting **optional backward compatibility** only.

### Wording

| Wrong | Right |
|-------|--------|
| “local qwen”, “LM Studio lane”, “Ollama lane”, “llama.cpp lane” (as the default) | **“Qwen API key lane”** |
| “Research runs on Ollama only” | Default: **Qwen API**; Ollama only if URL/port 11434 or doc says compat path |

**One-line version:** Use the **Qwen API key lane** on branch `agent/qwen3-live-run-20260331`, open the PR to `main`, merge, then run `brand-admin-onboarding-pages.yml` when onboarding deploy is the goal.

**One sentence for handoffs:** The commands are fine; just don’t describe this as a local Qwen setup — this repo uses the **Qwen API key lane**.

### Code / CI pointers

- Research runner: [scripts/research/README.md](../scripts/research/README.md) — **Qwen API** first; Ollama section is optional compat.
- Workflow: `.github/workflows/research-pipeline-run.yml` — Qwen API via secrets.
