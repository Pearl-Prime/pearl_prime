# GitHub governance (source of truth)

**Purpose:** Single source of truth for repo rulesets, required checks, branch flow, and token hygiene.  
**Verifier:** [scripts/ci/verify_github_governance.py](../scripts/ci/verify_github_governance.py) (reads [config/governance/required_checks.yaml](../config/governance/required_checks.yaml)).

---

## Rulesets

- Intended live shape: **one active ruleset** for `refs/heads/main` only (or `~DEFAULT_BRANCH` when it resolves to `main`).
- During cleanup or transition, multiple active rulesets are acceptable only if they target `main` and require the **exact same** status-check contexts.
- The verifier must fail duplicate or conflicting active rulesets that require different contexts on `main`.
- **Enable:** Require pull request before merging, require status checks to pass, block force pushes.
- **Do not** require status checks on feature-branch push (causes deadlock on first push).

---

## Required checks

- Canonical required contexts for PR merge to `main` are:
  - **Core tests**
  - **Release gates**
  - **EI V2 gates**
  - **Change impact**
- Required context names are contract-sensitive and must match workflow-emitted job names exactly, including case and punctuation.
- **Core tests** remains the always-on baseline check; path-filtered or conditional workflows must never be the only merge requirement.
- **Release gates** stays PR-required, but its PR path must remain lightweight. Heavy release/canary/rollback steps belong to push, schedule, or manual runs.
- `Workers Builds: pearl-prime` is non-blocking operationally and must **not** be a required merge check.
- Legacy contexts such as `change-impact` must be removed from live rulesets once cleanup is complete.
- Policy is versioned in config; the verifier enforces it.

## Evidence

- Capture before/after ruleset snapshots under `artifacts/governance/`.
- Confirm live GitHub required contexts match [config/governance/required_checks.yaml](../config/governance/required_checks.yaml).
- Run `python3 scripts/ci/verify_github_governance.py --mode api --strict` after live ruleset edits.

---

## Branch / PR flow

- Branch from `origin/main` only. No orphan branches.
- Naming: `codex/<topic>` recommended.
- Push branch → open PR to `main` → merge only when required checks are green.
- **Preflight:** Run `scripts/ci/preflight_push.sh` before push to block direct push to main and orphan branches.

---

## Security and tokens

- **No tokens in repo.** No `.github_token`, no token `.rtf` files. Use repo/org secrets or OS keychain.
- **Revoke** any token ever pasted in chat or logs immediately.
- Token rotation: document cadence and emergency revoke in org/repo runbooks. Prefer short-lived tokens or GitHub App over long-lived PAT for normal flow.

---

## Drift detectors (Layer 5 anti-drift)

Three structural CI checks in [.github/workflows/drift-detectors.yml](../.github/workflows/drift-detectors.yml) catch recurring footguns without relying on human review. All run on PR and push to `main`; they are parallel-safe with Wave 1 governance checks.

**Canonical pipeline path** ([scripts/ci/check_canonical_pipeline_path.py](../scripts/ci/check_canonical_pipeline_path.py)): Scans PR-touched `scripts/**`, `.github/workflows/**`, and `docs/**` for `scripts/run_pipeline.py` invocations in production context (workflows, `--render-book` / `--quality-profile` / `--render-dir`, or docs shell examples). Production calls must include `--pipeline-mode spine`. Legitimate legacy-registry dev/test paths may opt in with `# CI-ALLOWLIST: legacy-registry-ok — <reason>`. **Severity:** blocking FAIL once PR #1379 (spine default) lands; **WARN** until then so legacy main does not block merges.

**Duplicate modules** ([scripts/ci/check_duplicate_modules.py](../scripts/ci/check_duplicate_modules.py)): For each newly added `.py` file in the PR diff, extracts top-level function/class signatures via AST and warns when name + positional arg count (functions) or class name (classes) already exists elsewhere in the repo. **Severity:** WARN only (non-blocking).

**Authority doc read** ([scripts/ci/check_authority_doc_read.py](../scripts/ci/check_authority_doc_read.py)): Maps changed files to subsystems via [artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv](../artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv) and warns when the PR body plus commit messages cite none of that subsystem's authority docs. Best-effort backstop — it verifies mention, not that a doc was actually read. **Severity:** WARN only (non-blocking).

---

## Related docs

- [BRANCH_PROTECTION_REQUIREMENTS.md](BRANCH_PROTECTION_REQUIREMENTS.md) — Required checks and configuration.
- [GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md](GITHUB_GOVERNANCE_INCIDENT_RUNBOOK.md) — Incident response.
- [GITHUB_GOVERNANCE_PLAN.md](GITHUB_GOVERNANCE_PLAN.md) — Full plan and checklist.
