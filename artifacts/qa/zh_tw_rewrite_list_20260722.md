# zh-TW Rewrite List — Reconciled Audit (2026-07-22)

**Author:** Pearl_QA lane `agent/zh-tw-audit-reconcile-v2-20260722`
**Scope:** `atoms/`, `SOURCE_OF_TRUTH/`, `story_atoms/` — any path/filename marked `zh-TW`/`zh_TW`, as tracked on `origin/main` at `7bd30e8f8044af9d63feb2c8df3c603ee85071cb`. `artifacts/qa/` was **excluded** from scope (unlike the 2026-07-15 sweep's `core_scope_regex`): those 16 paths are audit-report artifacts (`.md`/`.json`/`.tsv`/`.html`/`.png`), not translated atom content, and including them corrupted the 07-15 sweep's own numbers (one of its own report TSVs, `zh_tw_scope_matrix.tsv`, got flagged as a "suspect file" because its filename contains `zh_tw` — it is a report listing *other* files' contamination status, not a translation).
**Files scanned:** 5,350 (vs. the 07-15 sweep's 5,085 in the same core scope — normal drift from 7 days of landings).

## Headline

| Verdict | Count | % of 5,350 |
|---|---:|---:|
| **TRUE_CONTAMINATION** (genuine Simplified characters, no valid Taiwan reading) | **880** | **16.4%** |
| AMBIGUOUS_VARIANT (Big5-encodable variant pairs only — 里/裡, 台/臺, 干/幹, 准/準, 于/於, 托/託, etc.) | 916 | 17.1% |
| CLEAN (script-clean, CJK-dense, no register defect found where sampled) | 2,311 | 43.2% |
| **WRONG_REGISTER_CLEAN_SCRIPT — fully untranslated English / stub / LLM-debris (0% CJK)** | **797** | **14.9%** |
| **WRONG_REGISTER_CLEAN_SCRIPT — majority-English / mixed-language (<40% CJK)** | **445** | **8.3%** |
| UNSAMPLED (file too short, <=50 chars, to classify) | 1 | 0.0% |

**Genuine rewrite need (TRUE_CONTAMINATION + fully/majority untranslated): 880 + 797 + 445 = 2,122 files (39.7% of scope).**

## The reconciliation the two prior audits needed

1. `zh_tw_translation_gap_audit_2026-07-15.md` §3 extrapolated **~195/5,078 (3.8%)** contaminated
   from a 600-file manual spot-check. **Too low by ~4.5x.** The manual sample almost certainly
   under-sampled the two personas (`corporate_managers`, `tech_finance_burnout`) that turned out to
   carry almost all of the worst defects (see below) — those two personas are 12.1% of files
   scanned but hold the overwhelming majority of the untranslated-English defect.

2. `zhtw_simplified_sweep_20260715/summary.json` found **1,686/5,085 (33.2%)** files with any
   OpenCC-suspect character. Re-run with a corrected per-character (not whole-string) OpenCC diff
   — the original whole-string `s2twp` conversion silently misaligns after any multi-character
   idiom substitution (e.g. 优盘→随身碟), inflating both true and ambiguous counts — this lane's
   re-scan of the same scope+method logic lands at **880 + 916 = 1,801/5,350 (33.7%)**, confirming
   the sweep's **raw total was directionally right**, but roughly half of it (916 files, 50.9% of
   the flagged set) is `AMBIGUOUS_VARIANT`: legitimate Taiwan usage (托育, 台上, 里維拉 as a
   surname, 占有, 干預, 于當下, 雇用) that a bare character-pair match cannot distinguish from
   contamination. The sweep's own `REPORT.md` flagged this risk ("single-character mappings... can
   be legitimate") but never resolved it into a verdict — that resolution is this lane's contribution.

**The real, defensible contamination number is 880/5,350 = 16.4%** — between the two prior
estimates, closer to the sweep's raw number after ambiguity is properly cleared than to the manual
audit's 3.8%.

## The bigger, previously invisible defect: untranslated English hiding in "clean" files

Neither prior audit could see this, because both worked at the **character** level and untranslated
English text contains **zero** Simplified Chinese characters — it passes every Simplified-detection
sweep as "clean." This lane added a CJK-density check (CJK chars ÷ (CJK chars + ASCII letters)) across
all 3,554 files the character sweep called `CLEAN`, and found:

- **797 files (22.4% of the "clean" bucket) are 0% CJK — entirely non-Chinese.** Manually reading a
  sample of these (8 of the 30-file register sample landed here by chance) showed three distinct
  failure modes, not just "someone forgot to translate":
  - **Untranslated English narrative** sitting directly in the `zh-TW/CANONICAL.txt` slot
    (`atoms/corporate_managers/anchored/boundaries_watcher/...`).
  - **Literal unfilled placeholder stubs**: `[Persona-specific hook for first_responders ×
    financial_anxiety]` repeated across every variant
    (`atoms/first_responders/financial_anxiety/HOOK/...`).
  - **Raw LLM chat meta-commentary left in the file**, never cleaned into content — e.g. "These
    integrations mark a significant shift in how you are processing your reality... Here is what
    stands out in this sequence" (`atoms/tech_finance_burnout/financial_stress/INTEGRATION/...`),
    "I see these exercises. They are sharp, direct..."
    (`atoms/tech_finance_burnout/self_worth/EXERCISE/...`). This is a qualitatively different and
    more severe defect than a translation quality problem — it means an LLM's own commentary about
    the content, not the content itself, got committed as the "translation."
- **445 more files (12.5%) are majority-English (<40% CJK)** — partial/mixed translations.
- This defect is **not evenly distributed**: two personas carry almost all of it —
  **`corporate_managers`: 254/380 files (67%) are 0% CJK**, **`tech_finance_burnout`: 337/580
  (58%)**. Every other persona is in the 2-19% range (`working_parents` is the next-worst at 19%,
  70/373). This reads as a **systemic gap in those two personas' translation passes**, not scattered
  noise — worth its own dedicated lane.

This finding is measured at **full scale, not sampled** (CJK-density is a deterministic per-file
metric computed over all 3,554 script-clean files) — it is not an estimate.

## Method

1. Enumerated scope via `git ls-tree -r --name-only origin/main`, filtered to
   `atoms/|SOURCE_OF_TRUTH/|story_atoms/` + zh-TW/zh_TW marker (excluding `artifacts/qa/`, see above).
2. Fetched all file content in one pass via `git cat-file --batch` against `origin/main`.
3. **Character-level** (not whole-string) OpenCC `s2twp` conversion: every individual CJK character
   in each file is converted alone (`cc.convert(ch)`), avoiding the multi-character idiom-substitution
   misalignment bug in naive whole-string diffing.
4. Per changed character, classified `ambiguous` vs not via **Big5 encodability of the source
   character** — reproducing the 07-15 `REPORT.md`'s own stated rule ("flags only when both hold: s2t
   rewrites it AND Big5 cannot encode it") but applying it consistently file-by-file rather than only
   at the aggregate top-pairs level.
5. File verdict: `TRUE_CONTAMINATION` if any non-Big5-encodable (genuinely Simplified-only) character
   present; else `AMBIGUOUS_VARIANT` if any Big5-encodable variant-pair character present; else
   script-clean, subject to the density reclassification in the section above.

## Sampling — exactly what was and was not manually verified

- **AMBIGUOUS_VARIANT context-check: 45 of 916 files (4.9%)**, chosen by sorting all
  AMBIGUOUS_VARIANT files by `ambig_count` descending and taking an even stride (`step = N/45`)
  across the full rank order — i.e. a spread from the highest-ambiguity-count file down to
  single-occurrence files, not just the top of the list. For each sampled file, the actual source
  lines (via `git show`) around the top 3 flagged character-pairs were read in context.
  **Result: 45/45 (100%) confirmed legitimate Taiwan usage** (e.g. 托育, 里維拉/里奧 as
  transliterated names, 台上, 干預, 于當下, 雇用, 占有, 秘密 written 祕密, 游刃有餘) — **0
  reclassified to TRUE_CONTAMINATION.** This is a real verification, not a rubber stamp: the sample
  spanned files with anywhere from 1 to 63 ambiguous hits.
- **TRUE_CONTAMINATION spot-check: 30 of 880 files (3.4%)**, same stride-sampling method by
  `true_count` descending. **Result: 30/30 (100%) confirmed genuine** — actual Simplified characters
  (这/个/为/无/当/现/紧/却/变/决/东/对/命运/们, etc.) embedded in otherwise-Traditional prose, not
  edge cases. One sampled path (`artifacts/qa/zh_tw_scope_audit_20260715/zh_tw_scope_matrix.tsv`)
  turned out to be a mis-scoped report artifact, not an atom — it was removed from scope entirely
  (see the Scope Reconciliation note above) rather than counted either way.
- **WRONG_REGISTER_CLEAN_SCRIPT / register-drift-on-truly-translated-files sample: 19 files**,
  drawn as part of a 30-file **random** sample of the `CLEAN`-verdict bucket (`random.seed(20260722)`,
  uniform draw, no stratification) taken *before* the density split was known to matter; 8 of the 30
  turned out to be the 0%-CJK untranslated-English defect above and 3 more were partial/mixed —
  those 11 were reclassified programmatically, not judged for register. Of the remaining **19 files
  with genuinely CJK-dense Chinese prose**, all 19 were read in full excerpt against the
  `translate-zh-tw` agent's stated voice bar (`.claude/agents/translate-zh-tw.md`: "humane, clear,
  emotionally literate," "Taiwan-friendly vocabulary," "not Simplified or Mainland-only phrasing").
  **0/19 showed Mainland-phrasing register drift** — all read as native-voiced Taiwan prose
  (natural idiom, appropriate register for the somatic/therapeutic genre, correct use of
  ambiguous-but-legitimate characters like 托/台/里 in context).
  **This is a small sample (19 of 2,311 real-clean files, 0.8%) — the true register-drift rate on
  script-clean, CJK-dense files is honestly UNMEASURED AT SCALE.** Zero hits in 19 is consistent
  with a low true rate but does not prove one; it should not be read as "register is fine
  everywhere." The untranslated-English defect (WRONG_REGISTER_CLEAN_SCRIPT, 1,242 files) is,
  by contrast, measured at full scale via CJK density, not sampled.

## Files

- `artifacts/qa/zh_tw_rewrite_list_20260722.tsv` — 5,350 rows, one per scanned file:
  `path`, `verdict`, `evidence`, `confidence`.
- `artifacts/qa/zh_tw_rewrite_list_20260722.md` — this file.

## Recommended next actions (not executed in this lane)

1. **Priority 1 — dedicated lane for `corporate_managers` (254 files) and `tech_finance_burnout`
   (337 files) 0%-CJK untranslated atoms.** This is bigger than the Simplified-contamination problem
   this reconciliation was originally scoped to answer and was invisible to both prior audits.
   Some fraction of these may be the LLM-meta-commentary failure mode, which likely needs the
   translation to be redone from the English source rather than "fixed," since no real zh-TW
   translation attempt exists in the file at all.
2. **Priority 2 — the 880 TRUE_CONTAMINATION files** via `translate-zh-tw` repair pass (Tier 1
   Claude per `CLAUDE.md` LLM Tier Policy), using this TSV's `path` + `evidence` column directly
   as the worklist.
3. **Priority 3 — the 445 partial/mixed-language files** — likely a lighter repair (finish an
   interrupted translation) rather than a from-scratch redo.
4. Do **not** action the 916 AMBIGUOUS_VARIANT files as contamination — they are confirmed
   legitimate Taiwan usage in this lane's sample; re-running a bare character sweep against them
   again would reproduce the original inflation.
5. Promote this lane's CJK-density check into the CI gate alongside the existing Simplified/Big5
   check (`CLAUDE.md` "memory is recall, not enforcement") — the untranslated-English defect class
   is exactly the kind of regression that can silently re-enter `main` (a stub or an
   English-source-copy landing as "zh-TW coverage") without a density floor to catch it.
