## Scope

- [ ] Brief description of changes.

## Checklist

- [ ] Required checks pass (or expected skips documented).
- [ ] If this PR touches workflows, governance, or release docs: CODEOWNER review requested.
- [ ] Preflight run before push: `scripts/ci/preflight_push.sh` (see [GitHub Support System Spec](docs/GITHUB_SUPPORT_SYSTEM_SPEC.md)).
- [ ] Branch from `origin/main`; one PR = one scoped change set; no token files, no bypass scripts.
- [ ] **If this PR changes a planner/composer signal** (slot ordering, atom routing, archetype dispatch, archetype emit order, dimension gate boundary, etc.) — assertions in tests that depend on that signal are updated in the SAME commit. Prevents the CI cascade pattern (PR lands → downstream tests fail → next N PRs' CI breaks → fix-cascade chain). See OPD-150 (2026-05-26).

## Release / evidence (if applicable)

- [ ] Release checklist or go/no-go updated (link or N/A).
