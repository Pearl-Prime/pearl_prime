# Runtime Consolidation Harvest Plan — 2026-03-22

Owner: Pearl_GitHub
Source branch: `codex/runtime-consolidation`
Source PR: [PR #21](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/21)
Verified against: `origin/main` at `866101bc`

## Decision

Do not merge `codex/runtime-consolidation` directly.

Use it only as a harvest source.

Why:

- `199` commits ahead of `origin/main`
- `12` commits behind `origin/main`
- about `22,611` changed paths
- branch is dominated by backup churn and large generated/content drift
- GitHub already reports merge conflicts and failed Cloudflare deployment on PR #21

## Useful Non-Backup Commits

These are the real payload commits currently visible on the branch:

- `af75e944` `feat(runtime): consolidate Qwen runtime into phoenix_omega (allowlist only)`
- `4c432267` `docs(governance): OWNERSHIP_MATRIX, registry, framework + drift-audit workflow`
- `565b8326` `fix(consolidation): update runner paths, docs alignment, remove legacy Qwen-Agent references`
- `54707f6d` `feat(consolidation): import high-value runtime assets and restore 2-author registry`
- `7c090743` `feat(consolidation): merge planner, dashboard, and flux bank improvements`
- `87444bcd` `chore(workflows): enforce canonical lm lock path in phoenix_omega workflows`
- `6eb87106` `governance: add PR-safe drift controls and required-check validation`
- `f7a07cc9` `Recover funnel copy for all 12 topic hubs and update configs`
- `f9803648` `Fill authority_narrative for all 13 hubs and update spec §1`
- `cdacbc01` `repo(cleanup): remove nested Qwen gitlinks and migrate onboarding docs/tooling`
- `6fca4cb7` `Recover all stranded files from codex/github-no-failure-enforcement`
- `85e8a365` `Add Pearl News full QA workflow and fix Qwen slot handoff`
- `bd5a9a1c` `feat(musician): complete musician bank content for Nihala, Miki, and Erika`
- `ed6c3d83` `Add multi-platform agent instruction files pointing to ps.txt`
- `cf64e790` `Rewrite all 125 teacher_intro options in Pearl News packs to pass the gate.`

## Top-Level Drift Signal

The branch diff is too large for direct reconciliation. Top-level changed-path counts:

- `artifacts`: `5634`
- `assets`: `3579`
- `SOURCE_OF_TRUTH`: `3419`
- `PhoenixControl`: `2840`
- `content`: `2522`
- `atoms`: `1792`
- `pearl_news`: `671`
- `config`: `668`
- `docs`: `276`
- `scripts`: `226`
- `.github`: `37`
- `specs`: `29`

This confirms the branch is not a single mergeable change set.

## Harvest Buckets

### Bucket A — Runtime Core And Runner Tooling

Primary source commits:

- `af75e944`
- `565b8326`
- `87444bcd`
- `cdacbc01`

Recommended action:

- open one fresh branch from `origin/main`
- harvest only runtime lock, runner guard, cleanup, and canonical path fixes
- exclude localization payloads and unrelated workflow churn

Suggested PR title:

- `feat(runtime): harvest lm lock and runner tooling from runtime consolidation`

### Bucket B — Governance And Drift Controls

Primary source commits:

- `4c432267`
- `6eb87106`

Recommended action:

- harvest as a dedicated governance PR
- compare carefully against already-merged governance work before cherry-picking
- do not re-import stale docs wording blindly

Suggested PR title:

- `feat(governance): harvest drift and required-check controls`

### Bucket C — Pearl News QA And Slot-Handoff Fixes

Primary source commit:

- `85e8a365`

Recommended action:

- reapply as a bounded Pearl News pipeline PR
- verify against current `main` workflow naming and required checks

Suggested PR title:

- `fix(pearl-news): harvest full QA workflow and slot handoff fixes`

### Bucket D — Marketing / Recommender Stack

Primary source commit:

- `54707f6d`

Recommended action:

- do not harvest wholesale
- split into at least two follow-up PRs if still wanted:
  - marketing/recommender core
  - git push-guard tooling

Suggested PR titles:

- `feat(marketing): harvest recommender and promotion gate core`
- `feat(git): harvest push-guard tooling`

### Bucket E — Content Recovery

Primary source commits:

- `f7a07cc9`
- `f9803648`
- `cf64e790`
- `bd5a9a1c`

Recommended action:

- content review first
- only harvest after current product owners confirm these content updates still match current canon
- do not mix content recovery with runtime/governance PRs

### Bucket F — Agent And Onboarding Meta

Primary source commits:

- `ed6c3d83`
- `6fca4cb7`
- `916e42a3`

Recommended action:

- only harvest if those files are still missing on `main`
- likely low priority because `ps.txt` and Pearl_GitHub memory now already exist on `main`

## Execution Order

1. Bucket B — governance/drift controls
2. Bucket A — runtime core and runner tooling
3. Bucket C — Pearl News QA fixes
4. Bucket D — push-guard and marketing/recommender split
5. Bucket E — content recovery only after explicit content review
6. Bucket F — meta/onboarding only if gaps remain

## PR #21 Final Disposition

Keep PR #21 open only while harvesting is active and while it remains useful as an audit reference.

After the wanted buckets above are either harvested or explicitly rejected:

- close PR #21
- keep the branch only if a historical reference is still useful
- otherwise archive/delete the remote branch

## Pearl_GitHub Rule For This Branch

For every bucket above:

1. start from `origin/main`
2. use a fresh branch
3. cherry-pick or manually rebuild only the bounded payload
4. run preflight before push
5. never use `codex/runtime-consolidation` itself as the merge vehicle
