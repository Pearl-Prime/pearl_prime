# System State Master

Last verified: 2026-03-24
Owner: Pearl_GitHub

## Purpose

This is the best single-file answer to:

- what the system is
- what is actually true right now
- what is already done
- what is still not done
- where a new developer should start

If this file disagrees with live git state, machine-readable config, or fresh artifacts, trust the live repo and update this file.

## Executive Summary

Phoenix Omega is a large multi-system repo with real production code, major documentation/governance infrastructure, active local work, and some backlog-only or partially wired areas. The repo is usable, but it is not in a final “everything complete and production-clean” state.

The clearest current truth is:

- governance and repo-operations docs are substantial and now better aligned
- GitHub branch protection is now normalized to one active canonical ruleset on `main`
- Pearl_GitHub tooling and hourly alignment infrastructure exist on `main`
- the AI Manga Dharma spec suite is merged
- manga pipeline implementation through Chunks A-F is merged on `main`
- there are no open PRs right now
- the current checkout is on `agent/manga-sdf-revision-workspace` (2 commits ahead of `origin/main`) with 3468 dirty paths (`2539` modified, `929` untracked)
- local repo stabilization is still active because `.git/index.lock` is present again and held by live editor-side git activity
- 16 stale remote branches were deleted from GitHub on 2026-03-24; 15 remote branches remain including `main`
- only two remote `codex/*` branches remain: `origin/codex/runtime-consolidation` and `origin/codex/marketing-brand-alias-resolution`
- some areas are fully real, some are scaffolding, and some are still backlog/reference only

## What New Developers Should Know First

If you only read one file first, read this file.

Then read, in order:

1. [../ps.txt](../ps.txt)
2. [./DOCS_INDEX.md](./DOCS_INDEX.md)
3. [./PEARL_GITHUB_STATE.md](./PEARL_GITHUB_STATE.md)
4. [../skills/pearl-github/references/repo_memory.md](../skills/pearl-github/references/repo_memory.md)

After that, go to the domain you are actually touching.

## Current Repo Truth

- Open PRs: `0`
- Repo cleanup / governance / manga alignment PRs already landed on `main`
- PR #40 normalized GitHub governance drift:
  - one active `main` ruleset remains
  - canonical required checks are `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`
  - legacy `change-impact` is removed from workflow emission and live rulesets
  - `Workers Builds: pearl-prime` is not merge-required
- PR #21 (`codex/runtime-consolidation`) was reviewed as harvest-only and closed as superseded
- hourly repo-alignment tooling exists on `main`:
  - [./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md)
  - [../scripts/git/hourly_repo_alignment.py](../scripts/git/hourly_repo_alignment.py)
  - [../scripts/git/hourly_repo_alignment.sh](../scripts/git/hourly_repo_alignment.sh)
- the most recent saved alignment report in the working checkout was `artifacts/governance/repo_alignment/hourly_repo_alignment_20260322_112949.md`
  - treat repo-alignment artifacts as local operational evidence, not guaranteed committed files for fresh clones
- however, local `main` currently lags `origin/main`, and the active manga workspace is far from normalized into clean PR flow

## Branch Reality

### Local branches currently present (19 total)

- active agent branches include `agent/manga-sdf-revision-workspace`, `agent/repo-alignment-hardening`, manga chunk branches, and repo-health helpers
- safety/local reference branches include `codex/main-autobackup-20260320-2124`, `codex/main-autobackup-20260322-112842`, `codex/main-salvage-20260323-153043`, `codex/marketing-brand-alias-resolution`, `codex/runtime-consolidation`, and `main`

### Remote branches on GitHub (15 total including `main`)

- active `origin/agent/*` branches remain for current local work, including `origin/agent/repo-alignment-hardening`
- keep-open `origin/codex/*` branches now are only:
  - `origin/codex/runtime-consolidation`
  - `origin/codex/marketing-brand-alias-resolution`
- the 16 stale remote branches from the old disposition set were deleted on 2026-03-24

Short interpretation:

- branch sprawl is much better than before
- remote stale-branch cleanup is materially improved
- remaining repo-health risk is concentrated in local dirt and active branch/worktree state, not stale GitHub remnants

## Governance Status

### What is good

- [../ps.txt](../ps.txt) now works better as an agent entry protocol
- [./DOCS_INDEX.md](./DOCS_INDEX.md) is the best canonical doc map
- [./PEARL_GITHUB_ONBOARDING.md](./PEARL_GITHUB_ONBOARDING.md) is closer to repo reality than before
- Pearl_GitHub state and memory docs exist and are useful
- repo-alignment/autopilot tooling exists
- governance verifier now checks for conflicting active rulesets and stale required-check contexts

### What is still imperfect

- prose docs can drift from machine-enforced config
- local work can move faster than the last committed state doc
- some state docs can still lag fast-moving branch or evidence changes

### Rule for truth

For required checks and enforcement, the machine-readable source of truth is:

- [../config/governance/required_checks.yaml](../config/governance/required_checks.yaml)

If prose disagrees with that file, the YAML wins until the prose is updated.

## Major System Status

### Pearl_GitHub / repo health

Status:

- real and active
- docs, memory, cleanup runbooks, branch-disposition docs, and autopilot tooling are present

Still not done:

- stabilize local repo activity around the live `.git/index.lock`
- normalize current local-only changes through clean branch/PR flow
- keep state docs current as repo reality changes

### Integrations

Status:

- meaningful local setup tooling and runbooks exist
- WordPress local setup has been wired before
- messaging setup flows and requirement-reporting scripts exist

Still not done:

- not all external channels are fully production-proven end to end
- some integrations are still token/credential dependent and manual

### Manga

Status:

- major spec suite is merged:
  - [../specs/AI_MANGA_PIPELINE_SUMMARY.md](../specs/AI_MANGA_PIPELINE_SUMMARY.md)
- implementation outline exists:
  - [./MANGA_IMPLEMENTATION_OUTLINE.md](./MANGA_IMPLEMENTATION_OUTLINE.md)
- first kernel/build slice exists in `phoenix_v4.manga`
- Colab validation exists for the prototype render path

Still not done:

- full in-repo production rendering path is not complete
- ComfyUI scaling path is planned, not fully wired
- the active SDF revision workspace changes are not yet normalized through PR flow

### Video pipeline

Status:

- substantial real system exists
- local artifacts and planning outputs are present

Still not done:

- some current work is still local-only and not yet normalized through GitHub truth

### Marketing / trend feeds / editorial routing

Status:

- active local work is visible in:
  - [../config/marketing/consumer_language_by_topic.yaml](../config/marketing/consumer_language_by_topic.yaml)
  - [../phoenix_v4/planning/catalog_planner.py](../phoenix_v4/planning/catalog_planner.py)
  - [../scripts/ml_editorial/run_market_router.py](../scripts/ml_editorial/run_market_router.py)
  - `config/trend_keywords/` local-only working directory, not yet landed on `main`
  - `scripts/feeds/` local-only working directory, not yet landed on `main`

Still not done:

- this active local work has not yet been cleanly normalized into GitHub via fresh branch/PR flow

## What Is Local-Only Right Now

Local `main` currently contains changes that are not yet normalized into clean GitHub truth.

That means:

- this checkout is useful and active
- but it is not the same thing as saying GitHub already contains the best current local work

## What Is Definitely Not Done

1. Full local-to-GitHub normalization of current working-tree changes
2. Full manga production render pipeline inside the repo
3. Full production completion of every external integration channel
4. Completion of all backlog-only or file-not-present items listed in [./DOCS_INDEX.md](./DOCS_INDEX.md)

## Best Operating Model

Use the repo in this order:

1. Read [./SYSTEM_STATE_MASTER.md](./SYSTEM_STATE_MASTER.md)
2. Read [../ps.txt](../ps.txt)
3. Use [./DOCS_INDEX.md](./DOCS_INDEX.md) to find the right authority doc
4. Use [./PEARL_GITHUB_STATE.md](./PEARL_GITHUB_STATE.md) for GitHub/repo-health resume state
5. Use machine-readable config and live artifacts when docs are stale

## For Onboarding Leads

If you are onboarding a new developer, tell them:

- this repo has strong documentation, but not all docs are equal
- this file is the best one-file summary
- `ps.txt` is protocol, not the full current state
- `DOCS_INDEX.md` is the navigation map
- `PEARL_GITHUB_STATE.md` is the fast GitHub/repo-health resume point
- current local work may be ahead of the last normalized GitHub state

## Update Rule

Update this file whenever one of these changes:

- branch inventory meaningfully changes
- the local-vs-GitHub alignment situation changes
- a major system moves from planned to real
- a major area is declared blocked, superseded, or complete
