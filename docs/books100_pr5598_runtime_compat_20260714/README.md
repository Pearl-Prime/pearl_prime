# Books-to-100 — PR #5598 Runtime Compatibility Fix

## Grounded live state

- Repository: `Ahjan108/phoenix_omega_v4.8`
- PR: `#5598`
- Branch: `agent/books100-integration-parser-20260714`
- Audited head: `8eee1fdc80b01614edbacd3220c77183eeb35ca0`
- Initial focused parser commit: `40742882eda99f47ec564634aec97decf74a02a3`
- Out-of-scope mass-renumber commit to revert: `8eee1fdc80b01614edbacd3220c77183eeb35ca0`

At the audited head, **Atoms parse sweep is green**, while **Core tests** and
**Release gates** fail in the production-readiness gate step.

## What this handoff changes

1. Reverts the catalog-wide atom-header renumber commit. Legacy catalog cleanup
   belongs in the auditor/content backlog lanes, not the parser runtime PR.
2. Keeps `parse_canonical_blocks(... require_unique_ids=True)` as the strict
   default, preserving `DuplicateAtomIdError` and the existing strict test.
3. Makes only normal runtime readers legacy-compatible:
   - `phoenix_v4/planning/pool_index.py`
   - `phoenix_v4/rendering/prose_resolver.py`
4. Adds focused tests proving:
   - strict direct parsing still fails loudly;
   - pool/runtime reading does not crash on legacy duplicate IDs;
   - prose rendering preserves the historical deterministic last-definition
     behavior until duplicate debt is repaired by the health/auditor lane.
5. Runs the exact focused tests, parse sweep, and production-readiness gates.

## Apply

```bash
cd ~/Downloads/books100_pr5598_runtime_compat_20260714
./apply_pr5598_fix.sh
```

The script creates:

```text
/Users/ahjan/phoenix_omega_worktrees/books100-pr5598-runtime-compat-20260714
```

It commits locally but does not push by default.

To apply, validate, commit, and push in one run:

```bash
PUSH=1 ./apply_pr5598_fix.sh
```

## After push

Watch required checks:

```bash
cd /Users/ahjan/phoenix_omega_worktrees/books100-pr5598-runtime-compat-20260714
gh pr checks 5598 --watch
```

Only after required checks are green:

```bash
gh pr ready 5598
gh pr merge 5598 --squash
```

Do not begin the #5599–#5606 merge sequence before #5598 lands.

## Why the script is head-pinned

The bundle refuses to modify the branch if its remote head is no longer the
audited SHA. That prevents an old patch from silently overwriting newer work.
