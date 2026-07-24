# Handoff — zh-TW Simplified Contamination Audit (Lane 04)

**Agent:** Pearl_QA · **Date:** 2026-07-15 · **Signal:** `zh-tw-simplified-contamination-audit`
**Measured at:** `origin/main` = `9e9b9e606791590337cd7d0f2fb425def2e6f760`
**Report:** `artifacts/qa/zh_tw_simplified_contamination_20260715/`
**REPAIRS_PERFORMED: none** — this lane edited zero contaminated files.

## What landed

1. **Independent verification** of lane 02's contamination count (report-only).
2. **Tiered report artifact** organized WHOLE_FILE-first, with #5682 ownership marked.
3. **A CI gate** — the durable deliverable, closing the enforcement gap lane 02 named.

## Headline numbers (all from executed commands; see report §6 to reproduce)

| Metric | Value |
|---|---|
| zh-TW atoms scanned | 5,172 |
| `HIGH_CONFIDENCE_SIMPLIFIED` | **869** — lane 02 **CONFIRMED** |
| `REVIEW_VARIANT_ONLY` (legit Taiwan usage — do NOT "fix") | 1,651 |
| `CLEAN` | 2,652 |
| Severity (distinct chars) | WHOLE_FILE 42 · PARTIAL 321 · SPOT_LEAK 506 |
| Net after #5682 merges | **862** (869 − 7) |

`origin/main` moved `b748f706 → 9e9b9e60` during the lane; **0 zh-TW atoms changed** across
those moves, so lane 02's number carries forward exactly rather than by assumption.

## Two corrections to lane 02 (neither changes the 869)

1. **Severity tiers key on DISTINCT chars, not total occurrences.** Lane 02's README says
   "1–2 chars" without disambiguating. Distinct reproduces its 506/321/42 exactly; total
   occurrences gives 445/342/82 — a 40-file swing in the WHOLE_FILE tier. The TSV now
   carries both columns so this cannot recur. **Distinct is canonical.**
2. **`zhtw_qa.py` was never landed.** Lane 02 cites "detector reused from the prior lane's
   `zhtw_qa.py`"; that file is not on `origin/main` and not on disk — it was a scratch
   script. What was reused is the *calibrated rule*. This lane freezes it into repo code as
   the first landed implementation. Agreement is evidenced by independent re-derivation
   matching lane 02 on every number including the #5682 split.

## FOR THE #5682 LANE OWNER — action required

PR #5682 is `OPEN` / `MERGEABLE` at head `5666b796938ba0f5d80e0287b01e7d9294244240`.
Verified against its own head (not assumed):

- It owns **20** zh-TW paths; it script-fixes **7** of them.
- **6 zh-TW files it touches REMAIN Simplified after it merges** — they are
  PLACEHOLDER-class fixes, not script fixes. **This is the named follow-up set:**
  `artifacts/qa/zh_tw_simplified_contamination_20260715/followup_after_5682_merges.tsv`

  ```
  PARTIAL   4  记录双变  atoms/gen_z_professionals/burnout/INTEGRATION/locales/zh-TW/CANONICAL.txt
  PARTIAL   3  个这双    atoms/gen_z_professionals/financial_anxiety/INTEGRATION/locales/zh-TW/CANONICAL.txt
  SPOT_LEAK 2  续来      atoms/healthcare_rns/burnout/INTEGRATION/locales/zh-TW/CANONICAL.txt
  SPOT_LEAK 2  这个      atoms/healthcare_rns/financial_anxiety/INTEGRATION/locales/zh-TW/CANONICAL.txt
  SPOT_LEAK 2  个双      atoms/working_parents/burnout/INTEGRATION/locales/zh-TW/CANONICAL.txt
  SPOT_LEAK 1  财        atoms/gen_x_sandwich/financial_anxiety/INTEGRATION/locales/zh-TW/CANONICAL.txt
  ```

- **No collision:** #5682 is a *repair* PR and this lane is *report + gate*. This lane
  touched none of its files. **The new gate PASSES on #5682 as-is** (verified against its
  head — it only improves), so it will not block that PR.
- **After #5682 merges:** its 7 repaired rows should be dropped from
  `scripts/ci/zh_tw_simplified_baseline.tsv` (the gate prints exactly which). Baseline
  becomes 862. This is the ratchet working as designed.

## The gate (enforcement — CLAUDE.md meta-rule)

`scripts/ci/check_zh_tw_simplified_contamination.py`, wired into:
- `.github/workflows/drift-detectors.yml` → the **Drift detectors** required check
- `scripts/run_production_readiness_gates.py` → gate **34** (`--audit-corpus` ratchet)
- `docs/DATA_DICTIONARY.tsv` → regenerated via `scripts/governance/build_data_dictionary.py`

**It is a DELTA/ratchet gate by deliberate design.** 869 contaminated files already sit on
main; an absolute gate would redden main and block every unrelated PR, get disabled, and
enforce nothing. Instead the 869 are recorded as dated known-debt in
`scripts/ci/zh_tw_simplified_baseline.tsv`, and the gate fails only when a **changed** zh-TW
file gains Simplified characters beyond its baseline.

Proven (executed, not asserted):

| Scenario | Result |
|---|---|
| Whole 5,172-file corpus at `origin/main` | **PASS** (~7s) — main does not redden |
| PR touching no zh-TW atoms | **PASS** (no-op) |
| Real PR #5682 (20 zh-TW files) | **PASS**, named its 7 repairs |
| Newly-introduced Simplified | **FAIL** exit 1 |
| Baselined file worsened | **FAIL** exit 1 |
| `pytest tests/test_zh_tw_simplified_contamination.py` | **34 passed** |

**Do not weaken it.** The baseline may only shrink. Adding a row to silence a red PR is the
bypass it exists to prevent.

## NEXT_ACTION

1. **#5682 lane owner:** merge #5682, then drop its 7 repaired rows from the baseline and
   re-audit the 6-file follow-up set above.
2. **Sequenced repair lane (NOT this lane):** the 869 is debt, not a target. The gate stops
   it growing; it does not shrink it. A repair lane should start at the **42 WHOLE_FILE**
   files (whole passages translated in Simplified — the worst reader-visible damage), which
   are listed first in `zh_tw_simplified_contamination.tsv`. **Tier-1 Claude only — never
   route Qwen at zh-TW.** Each repair shrinks the baseline.
3. **Known false negative** (accepted, documented): rare Simplified forms inside Big5 (e.g.
   极) are not flagged. The rule is precision-tuned; a false positive would reject correct
   Traditional prose. Revisit only with a Taiwan-native review, never by loosening the Big5
   leg.

## Cleanup ledger

- Worktree: none created (`git worktree add` times out on this repo; used the proven
  plumbing-commit path off `origin/main^{tree}` instead).
- Shared tree (`codex/registry-40x14-waystream`, heavy uncommitted churn): **not disturbed**.
  Its staleness would have silently deleted 3 DATA_DICTIONARY rows for files that exist on
  main (including #5696's gate) had the dictionary been regenerated from it — the single
  new row was applied onto `origin/main`'s version instead and verified as +1/−0.
- Scratch files: under the session scratchpad only; nothing in the repo.
- Background jobs: none left running.
