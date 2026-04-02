# System State Master

Last verified: 2026-04-01
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

Phoenix Omega is a large multi-system repo with real production code, major documentation/governance infrastructure, active local work, and some backlog-only or partially wired areas. The repo is usable, but it is not in a final "everything complete and production-clean" state.

The clearest current truth is:

- governance and repo-operations docs are substantial and well aligned
- GitHub branch protection is normalized to one active canonical ruleset on `main`
- Pearl_GitHub tooling and hourly alignment infrastructure exist on `main`
- the AI Manga Dharma spec suite is merged
- manga pipeline implementation through Chunks A-F is merged on `main`
- atom coverage is complete: 11 types x 12 personas (3,969 files) on `main`
- teacher banks cover 13 teachers with 2,143 files in SOURCE_OF_TRUTH/teacher_banks/
- translation pipeline infrastructure is merged but no translations generated yet (DashScope API in arrears)
- video pipeline Stage 18 Upload/Publish is merged; 0/24 credentials provisioned, dry-run mode active
- brand wizard / onboarding is live on Pages with premium studio UI
- branch consolidation complete: PR #146 reduced 46 to 8 local branches; `main` is the only active remote branch
- open PRs: 1 (#152 — YAML repair + exercise promotion + governance files)
- canonical credential registry exists: docs/INTEGRATION_CREDENTIALS_REGISTRY.md
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

- Open PRs: `1` (#152 — fix: repair broken YAMLs + promote exercises + create governance files)
- Branch consolidation landed via PR #146 on 2026-04-01
- Canonical required checks are `Core tests`, `Release gates`, `EI V2 gates`, `Change impact`
- hourly repo-alignment tooling exists on `main`:
  - [./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md](./PEARL_GITHUB_AUTOPILOT_RUNBOOK.md)
  - [../scripts/git/hourly_repo_alignment.py](../scripts/git/hourly_repo_alignment.py)
  - [../scripts/git/hourly_repo_alignment.sh](../scripts/git/hourly_repo_alignment.sh)

## Branch Reality

### Post-consolidation state (2026-04-01)

PR #146 performed a full branch consolidation: 46 local branches triaged down to 8, with 12 promotions cherry-picked and 37 branches archived.

- `main` is the only active remote branch
- 4 remote refs remain besides `main`: `origin/agent/brand-admin-media-generation-spec`, `origin/agent/manga-author-system`, `origin/agent/verify-and-fix`, `v48-main`
- local branch sprawl is eliminated

Short interpretation:

- branch hygiene is now excellent
- remaining work is on `main` or in short-lived agent branches
- no stale `codex/*` branches remain on remote

## Atom Coverage

### atoms/ directory (3,969 files on main)

All 11 atom types x 12 personas are covered:

- PIVOT/TAKEAWAY/THREAD/PERMISSION landed in PR #138 (588 files)
- STORY coverage landed in PR #140 (172 files)
- COMPRESSION/INTEGRATION and other base types were present from earlier PRs

### SOURCE_OF_TRUTH/teacher_banks/ (13 teachers, 2,143 files)

Teachers: adi_da, ahjan, joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma

- adi_da has full 11-type coverage (COMPRESSION, EXERCISE, HOOK, INTEGRATION, PERMISSION, PIVOT, REFLECTION, SCENE, STORY, TAKEAWAY, THREAD) plus localized atoms (ja-JP)
- Other teachers have 6 types (base coverage)

## Translation Pipeline

- Infrastructure merged across PRs #142, #143, #148, #149:
  - CJK6 translation pipeline for bestseller atoms (PR #142)
  - CJK6 bestseller atom translation CI workflow (PR #143)
  - Full comparator loop for translation pipeline (PR #148)
  - CI workflows switched to ubuntu-latest (PR #149)
- Zero translations generated yet — pipeline is ready but DashScope API is in arrears
- Quality contracts (glossary, golden segments) are stubs awaiting first real translation run
- Target locales: ja-JP, zh-CN, zh-TW, ko-KR, vi-VN, th-TH (CJK6)

## Video Pipeline

Status:

- Stage 18 Upload/Publish merged (PR #144): 5 platform uploaders, daily CI workflow
- 0/24 credentials provisioned
- Dry-run mode active — no real uploads happening
- Substantial local planning artifacts and pipeline code exist

Still not done:

- credential provisioning for all 24 platform slots
- first real upload run

## Brand Wizard / Onboarding

- Premium studio UI pass landed (PR #147)
- Last 5% polish landed (PR #151) — copy, blueprint, launch checklist
- Pages deploy live at brand-admin-onboarding.pages.dev
- Proof asset generation and completion reporting merged (PR #133)
- Onboarding spine HTML deployed via Cloudflare Pages (PRs #135, #136, #137)

## Exercise Component System

- Component assembler built: bridge/intro/description/aha/integration pipeline
- 39 production-ready exercises created from teacher bank atoms
- 11 exercises_v4 promoted from candidate to approved
- Exercise YAML repair and promotion in progress (PR #152)

## Governance Status

### What is good

- [../ps.txt](../ps.txt) works as an agent entry protocol
- [./DOCS_INDEX.md](./DOCS_INDEX.md) is the canonical doc map
- [./PEARL_GITHUB_ONBOARDING.md](./PEARL_GITHUB_ONBOARDING.md) is close to repo reality
- Pearl_GitHub state and memory docs exist and are useful
- repo-alignment/autopilot tooling exists
- governance verifier checks for conflicting active rulesets and stale required-check contexts
- canonical integration credentials registry exists (PR #145)

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
- branch consolidation complete (PR #146)

### Integrations

Status:

- meaningful local setup tooling and runbooks exist
- canonical credential registry exists: [docs/INTEGRATION_CREDENTIALS_REGISTRY.md](./INTEGRATION_CREDENTIALS_REGISTRY.md) — every env var, service, and setup link in one place
- validation script: `python3 scripts/ci/check_integration_env.py` reports what's wired vs missing

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
- STORY engine prose IDs aligned with Stage 3 assembly (PR #141)

Still not done:

- full in-repo production rendering path is not complete
- ComfyUI scaling path is planned, not fully wired

### Marketing / trend feeds / editorial routing

Status:

- active local work is visible in:
  - [../config/marketing/consumer_language_by_topic.yaml](../config/marketing/consumer_language_by_topic.yaml)
  - [../phoenix_v4/planning/catalog_planner.py](../phoenix_v4/planning/catalog_planner.py)
  - [../scripts/ml_editorial/run_market_router.py](../scripts/ml_editorial/run_market_router.py)
- band-aware sort and post-merge coordination artifacts landed (PR #150)

## What Is Definitely Not Done

1. Translation pipeline: DashScope API in arrears, zero translations generated, quality contracts are stubs
2. Video pipeline: 0/24 credentials provisioned, dry-run only
3. Full manga production render pipeline inside the repo
4. Full production completion of every external integration channel
5. Research citation gaps: 20 of 22 gaps still open (ws_research_citation_gaps_20260330)
6. Research pipeline activation: blocked on citation gap closure
7. Completion of all backlog-only or file-not-present items listed in [./DOCS_INDEX.md](./DOCS_INDEX.md)
8. Exercise YAML repair and promotion (PR #152 in progress)

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
- branch consolidation is complete; `main` is the only active branch

## Update Rule

Update this file whenever one of these changes:

- branch inventory meaningfully changes
- the local-vs-GitHub alignment situation changes
- a major system moves from planned to real
- a major area is declared blocked, superseded, or complete
