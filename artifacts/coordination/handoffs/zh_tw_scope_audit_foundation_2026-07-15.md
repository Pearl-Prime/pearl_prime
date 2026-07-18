# HANDOFF — zh-TW Scope Audit Foundation (Lane 02)

**Agent:** Pearl_Localization · **Date:** 2026-07-15 · **Type:** REPORT-ONLY
**Measured at:** `b748f706327f500d414f60a1b967c70783b94538` (== `origin/main`)
**Artifact:** `artifacts/qa/zh_tw_scope_audit_20260715/`

## Answers to the four lane questions

| # | Question | Answer |
|---|---|---|
| 1 | Production zh-TW files needing Tier-1 Claude | **5** (pack said 99 — stale) |
| 2 | Non-production deferred | **36** (pack claim VERIFIED EXACT) |
| 3 | Landed zh-TW files containing Simplified | **869** on main; **862** after #5682 |
| 4 | What #5682 owns | 52 files, 20 zh-TW paths — see `pr5682_owned_files.txt` |

## Delta on the pack's "99" — do not reconcile back

PR **#5693** merged 2026-07-15T11:04:54Z; its merge commit `b748f706` **is** current
`origin/main`. It landed 94 of the 99 via Tier-1 Claude. `99` was the pre-#5693 baseline
(`3755 − 3656`). The pack snapshot (`8956e222`) predates the merge.

The **5** remaining are **not translatable**: all `nyc_executives`, all blocked on a
defective *English* source (prose body == next header string; headers skip/duplicate).

## Downstream lane impacts (read before dispatching)

- **Lane 03 (zh-TW production Claude completion): NO TRANSLATABLE WORK REMAINS.**
  Its premise ("99 production files") is void. The residue is 5 files that are
  **Pearl_Writer-blocked**, not translation-blocked. Recommend lane 03 → close as
  superseded by #5693, or re-scope to "Pearl_Writer authors ~50 English variants for
  5 nyc_executives atoms, then a 5-file zh-TW follow-up". **Do NOT dispatch a translator.**
- **Lane 04 (Simplified contamination audit):** target set is ready — filter
  `zh_tw_scope_matrix.tsv` on `status == LANDED_SIMPLIFIED_CONTAMINATED` (869).
  Exclude the 20 `OWNED_BY_5682_DO_NOT_TOUCH` paths while #5682 is open.
  Work the `WHOLE_FILE` (42) tier first — highest reader impact per file.
  **Do not act on `REVIEW_VARIANT_ONLY` (1,651)** — those are legitimate Taiwan usage.

## Collision boundary with PR #5682 (OPEN/CLEAN)

Every path in `pr5682_owned_files.txt` is do-not-touch while the PR is open. Measured
against the PR head: it script-fixes **7** zh-TW files (matches its title), but **6** of its
files stay Simplified after merge (placeholder-class, not script-class) — re-audit those
6 after it lands. Net contamination post-merge: **862**.

## Method notes (reuse these)

- **Scope rule is repo-grounded**, not invented: `scripts/ci/report_translation_coverage.py`
  L34–36 (`BESTSELLER_SLOTS` + `ENGINE_DIRS`), docstring cites `PEARL_PRIME_100_PERCENT_DEV_PLAN §5`.
  It reproduces the repo tool's own `3750/3755 remaining=5`.
- **Detector reused**, not greenfielded, from the prior lane's `zhtw_qa.py`:
  Simplified iff `s2t(ch) != ch` **AND** `ch` is not Big5-encodable. Calibrated against a
  known-good and two known-contaminated landed files before use.
- **Gotcha:** `report_translation_coverage.py` reads the **working tree** — a dirty branch
  yields a false baseline. Always measure from a clean worktree at `origin/main`.

## Open risk — enforcement gap

The Big5 detector is **still not a CI gate**. 869 contaminated files sit on `main` and
nothing prevents more from entering. Per the "memory is recall, not enforcement" doctrine,
this audit is recall only. Promoting the detector to a gate is the durable fix and is
recommended as the next mechanism-level action.

## NEXT_ACTION

1. Merge this audit PR; treat `zh_tw_scope_matrix.tsv` as the SSOT for lanes 03/04.
2. Re-scope or close lane 03 (no translatable work) — route the 5 to **Pearl_Writer**.
3. Lane 04 works the 869 minus the 20 #5682-owned, `WHOLE_FILE` tier first.
4. Promote the Big5 detector to a CI gate (`scripts/ci/check_zh_tw_script.py` + Drift
   detectors) so contamination cannot re-enter `main`.
