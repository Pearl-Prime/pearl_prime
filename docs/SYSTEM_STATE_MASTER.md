# System State Master

Last verified: 2026-03-22
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
- Pearl_GitHub tooling and hourly alignment infrastructure exist on `main`
- the AI Manga Dharma spec suite is merged
- the first manga kernel/build slice is merged
- there are no open PRs right now
- local `main` has new local-only changes again, so local and GitHub are not perfectly aligned at this moment
- several remote `codex/*` branches still need harvest or disposition work
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
- PR #21 (`codex/runtime-consolidation`) was reviewed as harvest-only and closed as superseded
- hourly repo-alignment tooling exists on `main`:
  - [./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md)
  - [../scripts/git/hourly_repo_alignment.py](../scripts/git/hourly_repo_alignment.py)
  - [../scripts/git/hourly_repo_alignment.sh](../scripts/git/hourly_repo_alignment.sh)
- the most recent saved alignment report in the working checkout was `artifacts/governance/repo_alignment/hourly_repo_alignment_20260322_112949.md`
  - treat repo-alignment artifacts as local operational evidence, not guaranteed committed files for fresh clones
- however, local `main` currently has local-only changes again, so this checkout is not perfectly normalized to GitHub right now

## Branch Reality

### Local branches intentionally present

- `main`
- `codex/main-autobackup-20260320-2124`
- `codex/main-autobackup-20260322-112842`
- `codex/next-dev-clean`
- `codex/pearl-news-cleanup`
- `codex/runtime-consolidation`

### Remote branches still needing work

- `origin/codex/ei-v2-hybrid-pr`
- `origin/codex/governance-100`
- `origin/codex/pearl-news-cleanup`
- `origin/codex/phoenixcontrol-ui`
- `origin/codex/runtime-consolidation`
- `origin/codex/runtime-governance-core`

Short interpretation:

- branch sprawl is much better than before
- but branch cleanup/harvest is not fully finished

## Governance Status

### What is good

- [../ps.txt](../ps.txt) now works better as an agent entry protocol
- [./DOCS_INDEX.md](./DOCS_INDEX.md) is the best canonical doc map
- [./PEARL_GITHUB_ONBOARDING.md](./PEARL_GITHUB_ONBOARDING.md) is closer to repo reality than before
- Pearl_GitHub state and memory docs exist and are useful
- repo-alignment/autopilot tooling exists

### What is still imperfect

- prose docs can drift from machine-enforced config
- local work can move faster than the last committed state doc
- there are still some orphaned or stale references in governance docs

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

- finish remaining remote harvest/disposition work
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
- asset-bank / renderer / assembly / QC still need more implementation slices

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
2. Final harvest/disposition of all remaining remote `codex/*` branches
3. Full manga production render pipeline inside the repo
4. Full production completion of every external integration channel
5. Completion of all backlog-only or file-not-present items listed in [./DOCS_INDEX.md](./DOCS_INDEX.md)

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
