# zh-TW Track Deconfliction — 2026-07-23

Scope: every branch matching `origin/agent/zh-tw-*` / `origin/agent/zhtw-*`, plus the
open PRs layered on top of them, checked pairwise for file-level overlap against
current `origin/main` (fetched fresh this session). All numbers below are computed
directly from `git diff origin/main..<branch> --name-only`, not from narrative claims.

## 0. Branch/PR inventory (re-verified live, this session)

`git branch -r --list 'origin/agent/zh-tw-*' 'origin/agent/zhtw-*'` returns **25
branches**. Contamination-wave branches exist for **000–012, 014, and 014-b2 only**
(13 branches) — **there is no `-013` branch on origin**, and nothing beyond `014`/`014-b2`
exists. The "021–026" claim in the task prompt is confirmed false for this origin as of
this fetch.

`gh pr list --state open` (fetched live) confirms the PR numbers named in the task:

| PR | Branch | Title |
|----|--------|-------|
| 49 | agent/zh-tw-simplified-contamination-gate-20260722 | ci(zh-TW): land Simplified-contamination ratchet gate |
| 61 | agent/zhtw-name-registry-20260722 | zh-TW corpus-wide character-name registry (241 names) |
| 62 | agent/zhtw-glossary-imposter-syndrome-fix-20260722 | correct imposter-syndrome glossary term across 6 files |
| 65 | agent/governance-exception-dashscope-scoped | scope DashScope exemption to zh-CN (unrelated content) |
| 66 | agent/translation-quality-pipeline-20260722 | translation-quality pipeline scaffolding (zh-CN mirror prioritized) |
| 67 | agent/zhtw-name-registry-resolutions-20260722 | resolve ambiguous zh-TW name-registry entries |
| 68 | agent/zhtw-clean-corrupted-retranslate-20260722 | zh-TW retranslation, EN_CLEAN_ZH_CORRUPTED batch 1-5 (45 files) |
| 69 | agent/zhtw-name-conversion-millennial-women-20260722 | convert names, millennial_women_professionals family (1/14) |

No open PR exists yet for the 13 contamination-wave branches, `zh-tw-glossary-build`,
`zh-tw-glossary-build2`, `zh-tw-audit-reconcile-v2`, or
`zh-tw-audit-reconcile-glossary-rewrite` — they are branches only.

Total tracks/branches surveyed: **26** (25 zh-TW-prefixed branches + PR #66's
scaffolding branch, added because it touches a zh-TW-named watchlist config file).
PR #65 was checked and excluded from the branch-level analysis below: its diff
(`.github/workflows/brand-admin-onboarding-pages.yml`, `CLAUDE.md`,
`config/governance/banned_llm_patterns.yaml`) contains zero zh-TW content or config
files — it is docs/governance-only and does not intersect any zh-TW track.

## 1. Critical finding: a universal false-positive in the raw diff

A naive `git diff origin/main..<branch> --name-only` on **every one of the 25
zh-TW branches** reports the same 7 files as "changed":

```
.github/workflows/brand-admin-onboarding-pages.yml
brand-wizard-app/functions/api/onboarding/assignment.js
brand-wizard-app/functions/api/onboarding/submit.js
phoenix_v4/content_banks/loader.py
phoenix_v4/planning/enrichment_select.py
phoenix_v4/quality/chapter_flow_gate.py
tests/test_genz_anxiety_pipeline_fixes.py
```

This is **not** real overlapping work. All 25 branches were cut before two later
commits landed on `origin/main`:

- `159434e89a` — PR #59, fix(enrichment): genz anxiety 2h pipeline
- `1e9f7a3a7e` — PR #63, fix(ci): stop unrelated Waystream GHL webhook gate

`git diff origin/main..<branch>` shows the branch "reverting" those two commits
because the branch simply predates them, not because the branch edited those files.
Confirmed directionally: the diff on `phoenix_v4/content_banks/loader.py` shows the
branch *removing* a `logging` import and `LOGGER` line that PR #59/#63 *added* to
main — i.e. absence, not edit. A normal `git merge origin/main` (or GitHub's
"Update branch") into any of these 25 branches resolves this with **zero manual
work** — none of the 25 branches has a real edit to those 7 files.

**All real-overlap analysis below excludes this 7-file noise set.** The raw
(noise-included) pairwise table showed 300 "overlapping" pairs; after filtering,
only **3 pairs** have genuine file-level overlap.

## 2. Real (post-filter) file-level overlap table

| Track A | Track B | Overlap count | Files |
|---|---|---|---|
| PR #61 (zhtw-name-registry) | PR #67 (zhtw-name-registry-resolutions) | 3 | `.claude/glossaries/zh-TW.json`, `analysis/character_name_registry_zh_tw.yaml`, `analysis/glossary_project.yaml` |
| agent/zh-tw-glossary-build (no PR) | PR #61 (zhtw-name-registry) | 1 | `analysis/glossary_project.yaml` |
| agent/zh-tw-glossary-build (no PR) | PR #67 (zhtw-name-registry-resolutions) | 1 | `analysis/glossary_project.yaml` |

Every other pairwise combination among the 26 tracks surveyed — including all 13
contamination-wave branches against each other, against PR #68, against PR #69,
and against everything else — has **zero** real file overlap.

Full machine-readable table (noise-filtered): `artifacts/qa/zh_tw_track_deconfliction_20260723.tsv`

## 3. Overlap-by-overlap disposition

### 3a. PR #61 <-> PR #67 (name-registry <-> name-registry-resolutions) — COMPATIBLE, not a conflict

`git merge-base --is-ancestor origin/agent/zhtw-name-registry-20260722
origin/agent/zhtw-name-registry-resolutions-20260722` returns true: **PR #67's
branch literally contains PR #61's commit plus one more** (`62b66be21b` on top of
`19adb129cc`). This is not two independent tracks touching the same file — it is a
linear stack. The diff between the two branches on `character_name_registry_zh_tw.yaml`
is a clean incremental resolution (e.g. `Mika`/`Suki`/`Ren` get resolved
`AMBIGUOUS-FLAG` → `RESOLVED ... operator-approved` rationale, `Dev` kept distinct
from `Dave`, `Chen` marked `do_not_convert: true`, `Quin` dropped/merged into
`Quinn`). `.claude/glossaries/zh-TW.json` has **zero diff** between the two
branches (PR #67 didn't touch it further).

**Merge order: PR #61 first, then PR #67.** No rebase needed for #67 — it is
already based on #61's commit. If #61 is merged via squash-merge (not
fast-forward), #67 will need a trivial rebase to replay its one commit on top of
the squashed result, but there is no content conflict to resolve, only a
mechanical rebase.

### 3b. zh-tw-glossary-build <-> {PR #61, PR #67} on `analysis/glossary_project.yaml` — REAL CONFLICT, needs manual reconciliation

Both sides create `analysis/glossary_project.yaml` as a **new file** (both diffs
show `new file mode`, `--- /dev/null`) with **different content**:

- PR #61/#67's version: a thin pointer file — `named_recurring_characters` section
  only, referencing `analysis/character_name_registry_zh_tw.yaml` (241 names).
  Its own header comment states: *"This file intentionally does not duplicate
  coined-metaphor entries drafted on other unmerged sibling branches (e.g.
  agent/zh-tw-glossary-build-20260722) — those were never reviewed against
  origin/main and are out of scope for this PR."*
- `zh-tw-glossary-build`'s version: a much larger file (117 lines) with a
  `coined_metaphors` section (9 entries: "depletion dressed as dedication",
  "running on fumes", "golden handcuffs", etc., each with `preferred_by_context` /
  `avoid` / `recurrence` / `risk_tier`) **plus its own independently-drafted**
  `named_recurring_characters` section (5 names: Marcus/Elena/James/Priya/Devon)
  that predates and duplicates what PR #61 later superseded with the 241-name
  registry.

`git merge-base origin/agent/zh-tw-glossary-build-20260722
origin/agent/zhtw-name-registry-20260722` = `7bd30e8f80` — **the two branches
diverged independently from the same commit**; neither is descended from the
other. This is a genuine two-sided new-file conflict — git cannot auto-merge two
different "create this file" diffs at the same path, and a blind rebase of either
branch onto the other's merged state will hard-conflict on this file.

**Disposition:** the branches' own commit messages already state the intended
resolution — PR #61/#67's character-name section is authoritative and supersedes
glossary-build's 5-name draft (verified unchanged in the new registry per PR
#61's note). The **coined-metaphor content is not superseded and is not yet
landed anywhere** — it needs to be preserved. Recommended action for whoever picks
up `zh-tw-glossary-build`: after PR #61 and #67 merge, **manually re-author**
`analysis/glossary_project.yaml` by appending glossary-build's `coined_metaphors:`
block onto the now-merged (PR #67) file's existing `named_recurring_characters:`
section — do not push glossary-build's version over the top, and do not attempt
an automatic rebase of this one file.

**File needing manual (human) review before merge: `analysis/glossary_project.yaml`
— count = 1.**

### 3c. zh-tw-glossary-build2 — not mergeable, appears abandoned

`agent/zh-tw-glossary-build2-20260722` has **zero files** of real (non-noise)
content — `git diff origin/agent/zh-tw-glossary-build-20260722..origin/agent/zh-tw-glossary-build2-20260722
--stat` shows it *deleting* 11,958 lines across `analysis/risk_map.jsonl`,
`analysis/style_guide_zh_tw.yaml`, and other glossary-build artifacts, and its tip
commit is `7bd30e8f80` — the exact same commit as the merge-base with
`zh-tw-glossary-build`. In other words, `glossary-build2` is `glossary-build`'s
parent commit with no unique work of its own: an empty/reset branch. **Recommend:
do not merge; treat as superseded/stale and safe to delete.**

## 4. Specific checks requested in the task

**Do any contamination-wave branches (000–014, +b2) overlap PR #69's remaining 13
families?** No. Contamination waves 000 through 014-b2 cover personas in strict
alphabetical/sequential order — `corporate_managers` → `educators` →
`entrepreneurs` → `first_responders` → `gen_alpha_students` → `gen_x_sandwich` →
`gen_z_professionals` (wave 014-b2 stops mid-`gen_z_professionals` at
`overthinking`). None of the waves has reached `millennial_women_professionals`
(PR #69's persona) — confirmed by exact file-set intersection: **zero overlap**.

**Do any contamination-wave branches overlap PR #68's `EN_CLEAN_ZH_CORRUPTED` file
list?** No. PR #68 touches `corporate_managers/anchored/*` (financial_stress,
grief, imposter_syndrome, overthinking, self_worth, sleep_anxiety, social_anxiety,
somatic_healing — the `anchored` sub-tree specifically) plus
`corporate_managers/{financial_anxiety,sleep_anxiety,social_anxiety,somatic_healing}/COMPRESSION`,
`healthcare_rns/*` COMPRESSION+EXERCISE, and `first_responders/compassion_fatigue/COMPRESSION`.
The contamination waves that also touch `corporate_managers` (wave 000 only) hit a
disjoint set of engine dirs (`burnout/TEACHER_DOCTRINE`, `courage/INTEGRATION`) —
confirmed by exact file-set intersection: **zero overlap**. Waves never reach
`healthcare_rns` at all (alphabetically past `gen_z_professionals`, where the
waves currently stop).

## 5. Merge-order recommendation (all active tracks)

1. **PR #49** (zh-tw-simplified-contamination-gate) — CI ratchet gate, docs, and
   snapshots only; zero content overlap with anything else. Land first so it
   protects every zh-TW content PR that follows. It is 8 commits behind main
   (mechanical rebase only, no conflict).
2. **PR #61** (zhtw-name-registry) — docs/config-only character-name registry.
3. **PR #67** (zhtw-name-registry-resolutions) — already stacked on #61's commit;
   merge immediately after, trivial/no-conflict.
4. **Contamination waves 000 → 012 → 014 → 014-b2** (13 branches, no PRs opened
   yet) — mutually non-overlapping, each needs only a mechanical `git merge
   origin/main` to absorb PR #59/#63 (no real conflict). Open PRs and merge in any
   order; numeric order is simplest for review tracking.
5. **PR #68** (zhtw-clean-corrupted-retranslate) — no overlap with the waves or
   PR #69; mechanical rebase only.
6. **PR #69** (zhtw-name-conversion-millennial-women) — no file-level conflict
   with anything, but should merge *after* #61/#67 land so its name conversions
   for the remaining 13 families are checked against the now-locked registry
   (a content/logical dependency, not a git conflict).
7. **agent/zh-tw-audit-reconcile-v2** and
   **agent/zh-tw-audit-reconcile-glossary-rewrite** (docs artifacts, no PRs) —
   low-priority, no overlap, land whenever convenient.
8. **PR #66** (translation-quality-pipeline scaffolding) — independent, no
   overlap; land whenever convenient.
9. **PR #65** (governance-exception-dashscope-scoped) — unrelated to zh-TW
   content; land whenever convenient, no dependency on this lane.
10. **agent/zh-tw-glossary-build** — hold until after step 3. Requires the
    manual reconciliation of `analysis/glossary_project.yaml` described in §3b
    before it can be opened as a mergeable PR. Do not rebase this file
    automatically.
11. **agent/zh-tw-glossary-build2** — do not merge; recommend deleting as an
    abandoned/empty branch (see §3c).

## 6. Files requiring human diff review before any merge (not safe to blind-rebase)

Exactly **one**: `analysis/glossary_project.yaml`, where `zh-tw-glossary-build`
and `{PR #61, PR #67}` both introduce a new file at the same path with materially
different content (§3b). Every other real overlap (`.claude/glossaries/zh-TW.json`,
`analysis/character_name_registry_zh_tw.yaml` between PR #61/#67) is a clean linear
stack and safe to auto-merge/rebase.
