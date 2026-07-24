# zh-TW Quality Program — Handoff, 2026-07-23

## Status: complete, all work landed on `origin/main`

This document closes out a same-day, multi-track zh-TW (Taiwan Traditional
Chinese) quality program spanning corpus analysis, glossary authoring,
contamination repair, character-name conversion, corrupted-content
retranslation, and audit reconciliation. Every track below is verified merged
(spot-checked directly against the GitHub API and `origin/main` tree, not
taken on trust from any agent's self-report).

## Why this program existed

zh-TW coverage was reported at 99.87% (2026-07-15), which read as "essentially
done." It was not. Two prior audits of *quality* (not just existence)
disagreed by an order of magnitude on how much landed content was actually
contaminated (3.8% conservative vs. 33% raw mechanical sweep), a corpus-derived
terminology glossary had never been built, character names were inconsistently
Latin-vs-Chinese across the corpus, and — the biggest surprise — a large
fraction of "translated" files turned out to contain corrupted content (raw
LLM meta-commentary, refusal messages, truncated output) rather than real
translated prose. This program found the real shape of the problem and fixed
what could be fixed today.

## What landed (all merged, verified)

### 1. Audit reconciliation
Reconciled the two conflicting contamination audits into one real, file-level
verdict set: 880 `TRUE_CONTAMINATION`, 916 `AMBIGUOUS_VARIANT` (legitimate
Taiwan character variants, correctly not touched), 2,311 `CLEAN`, 1,242
initially `WRONG_REGISTER_CLEAN_SCRIPT` (later found to be mostly mislabeled —
see §5).

### 2. Glossary + style guide
Corpus-derived `analysis/glossary_core.yaml`, `glossary_project.yaml`,
`style_guide_zh_tw.yaml`, and 8 supporting artifacts, built from full-corpus
reading (not metadata alone). Two operator decisions applied: character names
must be Chinese corpus-wide (not the previously-drafted 5-name partial lock),
and the imposter-syndrome term fixed to the locked `冒牌者症候群`.

### 3. Contamination-glyph repair — **PRs #81–86, merged**
872 files with genuine Simplified-character contamination fixed. CI ratchet
gate landed as **PR #175** (gate renumbered 44→46 to avoid a collision with a
gate added since the original was drafted; baseline TSV now holds only 8
residual rows, down from 869).

### 4. Character-name conversion, all 14 families — **PRs #61, #67, #92, #157–160, #167–171, #178–181, merged**
Every Latin-script character name in the zh-TW corpus converted to its
registry-locked Chinese form (registry: `analysis/character_name_registry_zh_tw.yaml`,
238 names after 3 merges — Quin→Quinn, Brien→Brian, Farah→Farrah). One family
(`midlife_women`, PR #92) was independently completed by a sibling session;
detected and reused rather than duplicated.

### 5. Corrupted-content retranslation — **PRs #152–155, merged**
The real discovery of this program: ~1,051 zh-TW files weren't
under-translated, they were **corrupted** — containing raw LLM
meta-commentary ("Here is an analysis of which hook might resonate..."),
refusal messages, or truncated output instead of actual translated prose.
Retranslated from clean English source via a 9-way parallel `translate-zh-tw`
dispatch:

- **909 files genuinely retranslated** (real hand-composed Taiwan Traditional
  Chinese, every file gate-verified)
- **~116 files correctly identified as blocked** — the *English* source
  itself is broken (empty body, literal `[Persona-specific hook for X × Y]`
  placeholder text) — these need authoring, not translation, and were
  deliberately left untouched rather than fabricated
- A real validator bug was found and fixed mid-program (a "fix" for one edge
  case introduced a worse regression that silently false-passed empty
  translations for the *most common* block shape in the corpus) — every
  completed chunk was re-verified against the final corrected validator with
  zero false-passes found.
- The originally-flagged 1,242-file "WRONG_REGISTER" bucket (§1) was
  re-investigated (**PR #93**) and found to be almost entirely this same
  corruption class, not a register/tone problem — a wrong initial diagnosis
  caught before any content was rewritten on a false premise.

### 6. Authoring-backlog reconciliation — **PR #162, merged**
Three independently-produced "files that need English authoring" lists (the
WRONG_REGISTER re-triage, the retranslation program's own per-chunk findings,
and an earlier corpus-wide corruption scan) were merged, deduplicated, and
cross-verified into one master list:
**`artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv` — 863
unique files.** This is now the single source of truth for what needs English
content authored before it can be translated into *any* locale (a broken
English source blocks every locale's translation of that atom, not just
zh-TW).

## What is NOT done — real remaining work

1. **863 files need English authoring.** This is out of scope for translation
   agents by design (`translate-zh-tw` correctly refused to invent content for
   every one of these across the whole program). This needs a `Pearl_Writer`
   authoring pass, not a translation dispatch. See
   `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv` +
   `.md` for the full list, priority ranking (weighted by how many locales are
   blocked, since a broken English source blocks every locale), and
   methodology.

2. **~916 `AMBIGUOUS_VARIANT` files were never touched** (by design — they're
   legitimate Taiwan character-variant usage, not contamination). No action
   needed unless a future native-speaker pass wants to standardize variant
   forms as a style choice.

3. **Register-drift rate in the true `CLEAN` bucket (2,311 files) is still
   "unmeasured at scale."** The original audit sampled 19 files, found 0 hits,
   and explicitly declined to extrapolate. Nobody has run a real
   register-quality read at scale. If flagship-quality Taiwan voice matters
   beyond "not contaminated, not corrupted," this is the next real audit to
   run — and it should use native-speaker judgment (`translate-zh-tw` +
   `.claude/skills/translation-qa/SKILL.md`), not another mechanical script,
   given this program's repeated finding that mechanical heuristics
   (character-sweep, density-based corruption detection) produced false
   positives and false negatives that only direct reading caught.

4. **Two unrelated CI regressions are being fixed in separate, already-running
   cloud sessions** — not part of this program, but worth tracking since they
   were blocking merges during parts of this session:
   - `task_4307de72` — Core tests regression
     (`tests/planning/test_enhancement_contract_v21_integrity.py`)
   - `task_2db92229` — zh-CN atom stub-content regression (parse-sweep)

   Both showed as in-progress (not failed, not passed) on `main`'s latest
   commit as of this handoff. Check those sessions directly for status, not
   this document.

5. **A separate Cursor/Grok session's stray local branches**
   (`agent/zh-tw-rewrite-contam-01{5-9,20}-20260722`) were investigated
   earlier this session and confirmed **never pushed to origin and
   structurally broken** (mass phantom deletions of unrelated files, including
   test files). They pose no risk — nothing from them ever reached `main` —
   but are safe to delete locally if anyone wants to tidy up that machine's
   checkout. Not urgent.

## Key artifacts, for future reference

- Glossary/registry: `analysis/glossary_core.yaml`, `glossary_project.yaml`,
  `style_guide_zh_tw.yaml`, `character_name_registry_zh_tw.yaml`
- Reconciled contamination audit:
  `artifacts/qa/zh_tw_rewrite_list_20260722.tsv`
- Authoring backlog (the one to use going forward):
  `artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv` +
  `.md`
- Retranslation tooling (reusable for future corruption-repair work):
  `scripts/qa/zhtw_clean_retranslate/{triage.py,emit.py,emit_batch.py,validate.py}`
  — `validate.py`'s final correct commit is `4b37c8bd5078b7b6f04f23ff702fade84a619524`;
  do not use an earlier copy from any feature branch, several intermediate
  buggy versions circulated during this program.
- CI gate: contamination ratchet, gate slot 46,
  `scripts/ci/zh_tw_simplified_baseline.tsv` (8 residual rows)

## PR index (all merged)

| PR | Scope |
|---|---|
| #61, #67 | Character-name registry (draft + operator-resolved) |
| #81–86 | Contamination-glyph repair, 872 files |
| #92 | Name conversion: midlife_women |
| #93 | WRONG_REGISTER bucket re-triage (scope correction) |
| #152–155 | Corrupted-content retranslation, 842 files |
| #157–160, #167–171, #178–181 | Name conversion: remaining 12 families |
| #162 | Authoring-backlog reconciliation, 863 files |
| #175 | Contamination CI ratchet gate (rebase of #49) |

## Signal

`ZHTW_PROGRAM_COMPLETE_20260723`
