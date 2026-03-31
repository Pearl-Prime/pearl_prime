# Branch Protection Requirements

**Purpose:** Required status checks for `main`/`master` branch protection.  
**Authority:** [GITHUB_GOVERNANCE.md](GITHUB_GOVERNANCE.md) (source of truth); [FULL_REPO_TEST_SUITE_PLAN.md](./FULL_REPO_TEST_SUITE_PLAN.md).

---

## Required status checks

Machine authority: [config/governance/required_checks.yaml](../config/governance/required_checks.yaml).

For `main`, require exactly these status-check contexts:

| Check | Workflow | Purpose |
|-------|----------|---------|
| **Core tests** | `core-tests.yml` | Fast pytest + production readiness gates |
| **Release gates** | `release-gates.yml` | Lightweight PR gate plus heavier release/canary/rollback checks outside PRs |
| **EI V2 gates** | `ei-v2-gates.yml` | EI V2 tests, eval, calibration, promotion checks |
| **Change impact** | `change-impact.yml` | Change observation + impact analysis evidence |

**Core tests — onboarding proof regression guard:** The **Core tests** job runs `scripts/ci/validate_onboarding_registry.py` on every PR/push to `main`/`master`. That step enforces registry schema, `ready` → non-empty `asset_path`, source/fidelity consistency, and blocks critical comparison/product-proof rows from returning to `planned`/`missing` without an explicit intentional marker. No extra required status name is needed in branch protection.

Rules:

- Required context names must match workflow-emitted job names exactly.
- Use one active `main` ruleset when possible. If multiple active rulesets exist during a transition, they must require the exact same four contexts above.
- `change-impact` is a forbidden legacy alias after cleanup and must not remain required in live rulesets.
- `Workers Builds: pearl-prime` is non-blocking and must not be required for merge.

---

## How to configure

1. Go to **Settings → Rules → Rulesets** for `main`.
2. Enable **Require status checks to pass before merging**.
3. Add required checks:
   - **Core tests**
   - **Release gates**
   - **EI V2 gates**
   - **Change impact**
4. Save the rule and verify a test PR shows only those four checks as blocking.

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
