# Branch Disposition — 2026-03-20

Owner: Pearl_GitHub
Verified against: `origin/main` at `24c2b902`

## Purpose

This is the branch-by-branch disposition record for the 10 remaining remote
`codex/*` branches after the first cleanup pass. It is based on actual branch
distance, unique commit history, PR history, and top-level file scope.

Disposition labels:

- `delete` — do not merge; remove remote branch after preserving anything useful
- `harvest` — do not merge wholesale; cherry-pick or rebuild only the useful part
- `archive` — historical snapshot; governed content absent or superseded on `main`; safe to drop remote after record (cherry-pick later only if product asks)
- `superseded` — carrier branch whose governed slices landed elsewhere on `main`; keep local/remote only for audit if desired, not for merge
- `keep-open` — branch still has an active review vehicle or meaningful unique work
- `keep-audit` — explicitly keep for deliberate deeper audit; unsafe for blind action

## Summary Matrix

| Branch | Distance vs `origin/main` | Disposition | Why |
|---|---:|---|---|
| `origin/codex/ei-v2-gate-fix` | `10 behind / 54 ahead` | `delete` | stale CI/backups branch; PR history already merged/closed; huge unrelated artifact drift |
| `origin/codex/ei-v2-hybrid-only-clean` | `99 behind / 7 ahead` | `delete` | no merge-base with current main; contains ruleset-bypass history; superseded by later EI work |
| `origin/codex/ei-v2-hybrid-pr` | `12 behind / 1 ahead` | `harvest` | one focused EI v2 feature commit; closed PR; valid content but too stale to merge directly |
| `origin/codex/governance-100` | `12 behind / 5 ahead` | `harvest` | merged governance PR exists; remaining drift mixes backup noise with marketing research payload |
| `origin/codex/governance-evidence-pack` | `11 behind / 3 ahead` | `delete` | merged PR exists; remaining delta is stale docs evidence/index drift |
| `origin/codex/pearl-news-cleanup` | `6 behind / 1 ahead` | `harvest` | one substantial refactor; candidate for selective resurrection, not direct merge |
| `origin/codex/pearl-news-workflows-clean` | `9 behind / 26 ahead` | `delete` | merged PRs exist; branch accumulated backups plus mixed workflow/dashboard drift |
| `origin/codex/phoenixcontrol-ui` | `6 behind / 1 ahead` | `harvest` | one focused UI feature commit; no PR yet; rebase/cherry-pick candidate |
| `origin/codex/runtime-consolidation` | `6 behind / 165 ahead` | `keep-open` | active open PR #21; still far too large for blind merge and must be split/audited |
| `origin/codex/runtime-governance-core` | `6 behind / 1 ahead` | `harvest` | one large runtime/governance seed commit; likely source material for smaller PRs |

## Branch Notes

### `origin/codex/ei-v2-gate-fix`

- Latest tip: `2026-03-06` `b5469ff8` `chore(backup): auto backup 2026-03-06 14:30:50`
- PR history:
  - PR #13 merged: `ci(ei-v2): run hybrid test only when present`
  - PR #15 closed
- Unique branch history now is mostly backup churn plus stale CI retriggers and a
  very large unrelated artifact/content surface.
- Action:
  - do not reopen
  - delete remote branch after no-value confirmation

### `origin/codex/ei-v2-hybrid-only-clean`

- Latest tip: `2026-03-04` `4112d012` backup commit
- No current PR
- Critical finding:
  - branch has no merge-base with current `origin/main`
  - unique history includes `ci: add push_ei_branch_bypass script for ruleset workaround`
- Action:
  - do not merge
  - delete remote branch
  - if EI hybrid work is wanted, use `origin/codex/ei-v2-hybrid-pr` as the source instead

### `origin/codex/ei-v2-hybrid-pr`

- Latest tip: `2026-03-04` `6aefc237`
- Closed PR #10 exists for the same feature
- Unique payload is focused and technically meaningful:
  - 12 files
  - EI config, dimension gates, warnings, hybrid selector, learner, calibration/eval scripts, tests
- Action:
  - do not merge branch directly
  - harvest by cherry-picking or rebuilding this one feature set on a fresh branch from `origin/main`

### `origin/codex/governance-100`

- Latest tip: `2026-03-04` `7d606283` backup commit
- PR #11 merged already
- Remaining branch drift is not a clean governance-only delta:
  - includes `marketing_deep_research/*`
  - includes backup noise
- Action:
  - do not merge branch directly
  - harvest only specific docs/research files if still needed
  - otherwise delete remote branch

### `origin/codex/governance-evidence-pack`

- Latest tip: `2026-03-04` `99b265ba`
- PR #12 merged already
- Remaining unique content is small and docs-only, centered on old `DOCS_INDEX`
  backlog wording and evidence artifacts.
- Action:
  - no direct merge
  - delete remote branch unless a specific docs line still needs rescue

### `origin/codex/pearl-news-cleanup`

- Latest tip: `2026-03-10` `29cf7e47`
- No PR currently attached
- Unique payload is large but coherent:
  - 26 files
  - Pearl News refactor plus doc/config cleanup
  - too large for Pearl_GitHub PR scope and too stale for direct merge
- Action:
  - do not merge branch as-is
  - harvest by splitting into smaller fresh branches from `origin/main`
  - likely split: docs/spec cleanup, config deletions, pipeline changes

### `origin/codex/pearl-news-workflows-clean`

- Latest tip: `2026-03-07` `a7d10958` backup commit
- PR history:
  - PR #16 merged
  - PR #17 merged
- Remaining branch drift mixes:
  - backup churn
  - dashboard work
  - video/image bank work
  - workflow and Pearl News changes
- Action:
  - do not reopen as a merge branch
  - delete remote branch after any wanted ideas are separately harvested

### `origin/codex/phoenixcontrol-ui`

- Latest tip: `2026-03-10` `b1e265b6`
- No PR currently attached
- Unique payload is one focused UI feature commit:
  - 13 PhoenixControl files
  - runtime launcher and multiple new views
- Action:
  - harvest on a fresh branch from `origin/main`
  - good candidate for one dedicated UI PR after current app state review

### `origin/codex/runtime-consolidation`

- Latest tip: `2026-03-17` `8ea98097` backup commit
- Open PR #21 exists
- Unique payload is massive:
  - `165` commits ahead
  - touches nearly every system surface
  - includes thousands of generated/content/artifact files
- Action:
  - keep branch and PR for audit reference
  - do not merge directly
  - split into bounded follow-up branches if any part is still wanted
  - use [docs/RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md](./RUNTIME_CONSOLIDATION_HARVEST_PLAN_2026_03_22.md) as the concrete extraction plan

### `origin/codex/runtime-governance-core`

- Latest tip: `2026-03-10` `caefb809`
- No PR currently attached
- Unique payload is one large seed commit across workflows, governance docs,
  localization scripts, audit scripts, runner tooling, and article judge logic.
- Action:
  - do not merge directly
  - harvest selectively into smaller topic branches
  - likely split: governance checks, localization tooling, runner tooling, article judge

## Recommended Execution Order

### Safe delete after final human acknowledgment

- `origin/codex/ei-v2-gate-fix`
- `origin/codex/ei-v2-hybrid-only-clean`
- `origin/codex/governance-evidence-pack`
- `origin/codex/pearl-news-workflows-clean`

### Harvest next if product value still matters

- `origin/codex/ei-v2-hybrid-pr`
- `origin/codex/phoenixcontrol-ui`
- `origin/codex/runtime-governance-core`
- `origin/codex/pearl-news-cleanup`
- `origin/codex/governance-100`

### Keep open for deliberate decomposition

- `origin/codex/runtime-consolidation`

## Harvest triage addendum — 2026-03-30

Pearl_GitHub triage vs `artifacts/governance/main_harvest/latest_main_harvest.md` (post PR #90). Rows: branch | disposition | rationale | date.

| Branch | Disposition | Rationale | Date |
|--------|-------------|-----------|------|
| `origin/codex/main-autobackup-20260320-2124` | `archive` | Autobackup snapshot (~2 commits ahead); misc docs/backup noise; no governed merge target. Remote absent at triage — record only. | 2026-03-30 |
| `origin/codex/main-autobackup-20260322-112842` | `archive` | Autobackup snapshot (~22 commits ahead); GTM/marketing/PhoenixControl noise; rescue via future cherry-picks if needed. Remote absent at triage — record only. | 2026-03-30 |
| `origin/codex/main-salvage-20260323-153043` | `archive` | Salvage snapshot (~15 commits ahead); teacher-bank deltas superseded by S6/S7 on `main`; remainder superseded. Remote absent at triage — record only. | 2026-03-30 |
| `origin/codex/marketing-brand-alias-resolution` | `archive` | Marketing workflows + artifacts; not governed by active spec; future marketing lane may revisit. | 2026-03-30 |
| `origin/codex/state-convergence-20260328` | `superseded` | Pearl Prime convergence carrier; governed PR1 + PR3 slices confirmed **satisfied on `main`** (no transplant vs stale tip). PR2 already_on_main per harvest. Keep branch for audit only; do not merge wholesale. | 2026-03-30 |

## Pearl_GitHub Rule Going Forward

For any harvested branch above:

1. start from `origin/main`
2. cherry-pick or manually reapply only the bounded useful commit(s)
3. keep the PR inside push-guard and PR scope limits
4. never revive the old remote branch as the merge vehicle
