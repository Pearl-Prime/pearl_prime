# Q7 — Documentation Cliff

**Date:** 2026-04-29

## A. Volume

- `docs/` markdown files: **288**
- `specs/` markdown files: **79**
- Total spec/doc surface: **367 .md files**
- `docs/DOCS_INDEX.md` size: 2,255 lines

## B. DOCS_INDEX freshness drift

`docs/DOCS_INDEX.md:5` — `**Last updated:** 2026-04-10`

Days since update: **19**.

Major work landed AFTER 2026-04-10 that DOCS_INDEX does not reflect:

- The entire spec-739 wave (PR #739, #743–#770, #780, #788–#795) — variant coverage gate is now strict; not in DOCS_INDEX
- `docs/PIPELINE_DASHBOARD_INDEX.md` (PR #730, 2026-04-26) — created post-DOCS_INDEX last_updated; not linked
- `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` reconciliation completion (PR #682, #684) — not reflected
- `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` (836 lines) — not linked
- `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` — not linked
- `docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md` — not linked
- `docs/FULL_REPO_SYSTEM_AUDIT_2026-04-26.md` (predecessor audit) — not linked
- `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md` (239 lines) — exists but not in DOCS_INDEX; lifecycle status unclear
- All Pearl Prime spec-739 phase 1/2/3 docs

DOCS_INDEX claims to be the single canonical doc index. Today it indexes ~80% of pre-2026-04-10 surface and ~0% of post-2026-04-10 surface.

## C. Anchor-doc presence vs CLAUDE.md read-first list

The audit brief named 10 read-first anchors. Existence check against `docs/`:

| # | anchor | exists | size |
|---|---|:---:|---:|
| 1 | CLAUDE.md (root) | yes | 247L |
| 2 | docs/DOCS_INDEX.md | yes | 2,255L |
| 3 | docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md | yes | 184L |
| 4 | docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md | yes | 587L |
| 5 | docs/PEARL_PRIME_RELEASE_CONTRACT.md | yes | 89L |
| 6 | docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md | yes | 442L |
| 7 | docs/MANGA_PIPELINE_COMPLETE_GUIDE.md | yes | 58L |
| 8 | docs/MANGA_PIPELINE_AUDIT_2026-04-26.md | yes | 836L |
| 9 | **docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md** | **NO** | n/a |
| 10 | docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md | yes | 155L |
| 11 | docs/FULL_REPO_IMPLEMENTATION_GAP_PLAN_2026-04-26.md | yes | 160L |
| 12 | docs/PIPELINE_DASHBOARD_INDEX.md | yes | 264L |
| 13 | docs/PEARL_PM_STATE.md | yes | 145L |
| 14 | docs/PEARL_ARCHITECT_STATE.md | yes | 388L |

**Missing:** `docs/PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md`. The audit brief implicitly depends on this for "feed catalogs to storefronts". This is a Phase-1 documentation cliff. **Recommend operator-authored plan covering: which catalogs, which storefronts, submission cadence, locale-rollout order, KPIs.**

## D. Stale-by-content (not by mtime)

`find docs/ -mtime +60` reports 0 because filesystem mtime is reset on worktree creation. Use `git log` instead.

`git log --since='2026-03-01' --name-only` shows 311 distinct paths under `docs/` modified by commits since 2026-03-01 — slightly higher than 308 .md count because some paths are subdirectory `*.md` files (sub-folders not in top-level scan). Approximately **all** `docs/*.md` have been touched in the last 8 weeks. So nothing is "60-day-stale" by git-log measure.

**But:** "touched" ≠ "current". Spot-check sample:

- `docs/SYSTEMS_V4.md` referenced by SUBSYSTEM_AUTHORITY_MAP for `teacher_mode` — verify that its claims about teacher_banks/ schema match current SOURCE_OF_TRUTH/teacher_banks/. (Deferred — recommend in next audit pass.)
- `docs/AUDIOBOOK_PIPELINE_SPEC.md` claims a "fully-automated Qwen comparator loop, no human in repair loop". Verify against `audiobook-regression.yml:3` which gates full regression behind manual dispatch only — drift.
- `docs/BRANCH_PROTECTION_REQUIREMENTS.md` and `docs/PEARL_PRIME_RELEASE_CONTRACT.md` name 4 required checks. Live ruleset requires only `Verify governance` (q6 §C.3). Drift.

## E. Specs that exist but have no canonical-status marker

A clean spec doc states upfront: AUTHORITATIVE / SUPERSEDED-BY-X / DEPRECATED. Spot-check on 10 random specs/*.md:

- Most specs lack a lifecycle header.
- `docs/FULL_REPO_DEPRECATION_AND_DELETION_PLAN_2026-04-26.md` schedules deletions but does not mark its targets in the targets' own files.

**Recommendation:** add a `## Status` line to every spec/*.md and docs/*_SPEC.md by next audit cycle. 10 minutes per file × ~80 specs = ~13 operator-hours.

## F. Index drift — referenced files that don't exist

A full broken-link audit of DOCS_INDEX would take ~2 hours and is deferred. Spot-check shows the index references several "backlog" or "planned" files explicitly with ⚠️ markers — that policy is good. Recommend re-running this check programmatically every quarter.

## G. Phase tag rollup for documentation cliffs

| phase | doc cliff | severity |
|---|---|---|
| 0 | DOCS_INDEX 19 days stale | MED |
| 0 | spec-vs-config-vs-CI required-checks triple-disagreement (q6 §C.3) | HIGH |
| 1 | PHOENIX_OMEGA_MASTER_CATALOG_PLAN.md missing | HIGH |
| 4 | INTEGRATION_CREDENTIALS_REGISTRY missing 3 APIs | MED |
| all | spec lifecycle headers absent | LOW |
| all | DOCS_INDEX broken-link audit not run | LOW |

## H. Single-action recommendation

**Re-run DOCS_INDEX last_updated + add the 8 post-2026-04-10 doc references in one PR.** 1-hour operator job. Highest-leverage doc fix.
