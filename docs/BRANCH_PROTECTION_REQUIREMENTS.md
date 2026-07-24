# Branch Protection Requirements

**Purpose:** Required status checks for `main`/`master` branch protection.  
**Authority:** [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) (source of truth); [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md).

---

## Required status checks

Machine authority: [config/governance/required_checks.yaml](../config/governance/required_checks.yaml).

For `main`, require exactly these status-check contexts:

| Check | Workflow | Purpose |
|-------|----------|---------|
| **Verify governance** | `github-governance-check.yml` | Enforce the repository governance contract and required-check policy |
| **parse-sweep** | `atoms-parse-sweep.yml` | Block new atom parse, over-match, and stub-content regressions |

Both required checks run on every pull request to `main`, so they always report. `Core tests` still runs `scripts/ci/validate_onboarding_registry.py` and supplies useful optional evidence, but it is intentionally held out of branch protection by the machine policy. Do not infer required-check status from a workflow's test coverage.

Rules:

- Required context names must match workflow-emitted job names exactly.
- Use one active `main` ruleset when possible. If multiple active rulesets exist during a transition, they must require the exact same two contexts above.
- `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`, and `Drift detectors` are not canonical merge requirements. Promote a check only after making it non-path-filtered and reliably green, then update the machine policy and live ruleset together.
- `change-impact` and `Change impact` are forbidden legacy contexts and must not remain required in live rulesets.
- `Workers Builds: pearl-prime` is non-blocking and must not be required for merge.

---

## How to configure

1. Go to **Settings → Rules → Rulesets** for `main`.
2. Enable **Require status checks to pass before merging**.
3. Add required checks:
   - **Verify governance**
   - **parse-sweep**
4. Save the rule and verify a test PR shows only those two checks as blocking.

---

## Failure visibility (recommended)

For immediate visibility when CI breaks:

1. Enable workflow issue alerts via `.github/workflows/production-alerts.yml` (already in repo).
2. Enable GitHub email notifications:
   - GitHub **Settings → Notifications**
   - Turn on **Email** for Actions/workflow failures.
   - Set repo watch to **Custom → Actions** for this repo.
3. Keep `production-observability.yml` scheduled; it writes:
   - `artifacts/observability/evidence_log.jsonl`
   - `artifacts/observability/elevated_failures.jsonl`

This gives both inbox visibility (email) and in-repo tracking (issues + artifacts).

---

## Auto-merge (optional)

For low-risk agent PRs (e.g. dependency fixes from the observability agent), see [AUTO_MERGE_POLICY.md](AUTO_MERGE_POLICY.md). PRs labeled `bot-fix` that pass required checks may be auto-merged via `.github/workflows/auto-merge-bot-fix.yml`.
