# Pearl Prime Gap Analysis

Date: 2026-03-23
Repo: `Ahjan108/phoenix_omega_v4.8`
Workspace: `/Users/ahjan/phoenix_omega`
Head: `8d25c34274e0bcc3710d9cb052518fad8b986284`

## Scope

Assess what remains for `Workers Builds: pearl-prime` to be considered fully aligned with repo governance and operational expectations, using repo authority docs, live GitHub ruleset state, and live check-run evidence.

## Authority reviewed

- `docs/GITHUB_OPERATIONS_FRAMEWORK.md`
- `docs/GITHUB_NO_FAILURE_FRAMEWORK.md`
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md`
- `docs/GITHUB_GOVERNANCE.md`
- `docs/GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md`
- `docs/PEARL_GITHUB_AUTOPILOT_RUNBOOK.md`
- `docs/PEARL_GITHUB_STATE.md`
- `docs/SYSTEM_STATE_MASTER.md`
- `docs/RIGOROUS_SYSTEM_TEST.md`
- `config/governance/required_checks.yaml`

## Verified current state

### 1. GitHub governance is normalized

Live rules for `main` now show exactly one active required-status-check source with the canonical contexts:

- `Core tests`
- `Release gates`
- `EI V2 gates`
- `Change impact`

`Workers Builds: pearl-prime` is not required by branch protection.

### 2. Repo machine policy explicitly treats Pearl Prime as non-blocking

`config/governance/required_checks.yaml` encodes:

- canonical `required_checks`
- `non_blocking_checks` including `Workers Builds: pearl-prime`
- `forbidden_legacy_checks` including `change-impact`

This matches the current live ruleset behavior.

### 3. Repo docs consistently describe Pearl Prime as non-blocking

The governance and operations docs now agree that `Workers Builds: pearl-prime`:

- is operational noise for merge purposes today
- must not be required for merge
- should be ignored by Pearl_GitHub automation when canonical required checks are green

### 4. The Cloudflare Pearl Prime check still fails on current `main`

For head commit `8d25c34274e0bcc3710d9cb052518fad8b986284`, the GitHub Checks API reports:

- check name: `Workers Builds: pearl-prime`
- app slug: `cloudflare-workers-and-pages`
- app id: `85455`
- status: `completed`
- conclusion: `failure`
- started_at: `2026-03-23T21:28:38Z`
- completed_at: `2026-03-23T21:28:38Z`

The instantaneous failure strongly suggests an integration or target mismatch, not a long-running build failure inside this repo's normal CI path.

### 5. There is no first-class Pearl Prime Cloudflare deployment config in this repo

Searches across the repo did not find:

- `wrangler.toml`
- `wrangler.json`
- `package.json`
- `package-lock.json`
- `pnpm-lock.yaml`
- `yarn.lock`

There is no obvious repo-owned Worker deployment surface for a Cloudflare service named `pearl-prime`.

### 6. The repo's own required GitHub Actions path is healthy enough for merge

On the current `main` head, the canonical governance path is green:

- `Core tests`: success
- `GitHub governance check`: success
- `Docs CI`: success
- `Locale gate`: success
- `Change impact`: success

The current Pearl Prime Cloudflare failure does not block merge anymore, which is the intended governance outcome.

## Gap summary

Pearl Prime is not "100%" in the sense of being an evidenced, repo-owned, green deployment path. The main remaining gaps are operational and integration-related, not GitHub branch-protection related.

### Gap 1. No repo-owned deployment contract for Pearl Prime

There is a live external Cloudflare integration posting checks for `pearl-prime`, but there is no corresponding versioned deployment config in this repo that explains:

- what gets built
- from which directory
- with which toolchain
- against which environment
- under which success criteria

Without that contract, the check is noise rather than trustworthy release evidence.

### Gap 2. Failing external integration has no in-repo root-cause evidence

The Cloudflare check links to a dashboard build record, but the repo does not currently preserve:

- build target definition
- deployment config
- failure mode taxonomy
- expected ownership and remediation path

This means repeated failures are visible but not actionable from repo truth alone.

### Gap 3. "100%" production proof is broader than mergeability

`docs/RIGOROUS_SYSTEM_TEST.md` sets a higher bar than "PR merged":

- real pipeline canary runs
- evidence on `main`
- release-path smoke
- rollback proof

None of that is currently established for Pearl Prime in this repo.

### Gap 4. Other non-canonical failures still exist on `main`

Recent GitHub Actions runs on the current head show additional failures outside the canonical required set, including:

- `.github/workflows/max-quality-catalog.yml`
- `.github/workflows/audiobook-regression.yml`
- one `pages build and deployment` dynamic failure

Those are separate from Pearl Prime, but they matter if the target becomes "zero noise on main" rather than "merge-safe governance."

## Verdict

Pearl Prime is governance-safe but not deployment-complete.

More precisely:

- branch protection and Pearl_GitHub behavior are now correct
- the Cloudflare Pearl Prime check is confirmed non-blocking
- the remaining problem is that the Cloudflare integration appears detached from a repo-owned, versioned deployment contract

## Recommended next actions

Choose one path and make it explicit:

### Option A. Retire the stale external integration

Use this if Pearl Prime is not supposed to deploy from this repo anymore.

Actions:

- detach or disable the Cloudflare `pearl-prime` GitHub integration
- document retirement in governance/operations docs
- confirm no check-run is emitted on fresh pushes

Success condition:

- fresh `main` pushes no longer receive `Workers Builds: pearl-prime`

### Option B. Productize Pearl Prime as a repo-owned deployment target

Use this if Pearl Prime is supposed to remain a real deployable service from this repo.

Actions:

- add the missing deployment contract to version control
- define owner, source directory, toolchain, build command, secrets contract, and environment mapping
- make the Cloudflare build reproducible from repo instructions
- add canary/smoke and rollback evidence expectations

Success condition:

- fresh `main` pushes produce a green, reproducible Pearl Prime deployment signal with repo-backed configuration and operator docs

## Recommended order

1. Decide whether Pearl Prime is still a real deployment target for this repo.
2. If no, remove the external Cloudflare integration.
3. If yes, add repo-owned deployment config before treating the Cloudflare check as meaningful.
4. Separately audit the remaining non-canonical failing workflows on `main` if the goal is full no-noise operations.

## Evidence commands used

```bash
gh api repos/Ahjan108/phoenix_omega_v4.8/rules/branches/main
gh api repos/Ahjan108/phoenix_omega_v4.8/commits/8d25c34274e0bcc3710d9cb052518fad8b986284/check-runs
gh run list --limit 12 --json databaseId,name,headSha,conclusion,event,createdAt,url
rg -n "pearl-prime|Cloudflare|cloudflare-workers-and-pages|wrangler" docs config scripts .github phoenix_v4 public
find . -maxdepth 3 \( -name 'wrangler.toml' -o -name 'wrangler.json' -o -name 'package.json' -o -name 'package-lock.json' -o -name 'pnpm-lock.yaml' -o -name 'yarn.lock' \)
```
