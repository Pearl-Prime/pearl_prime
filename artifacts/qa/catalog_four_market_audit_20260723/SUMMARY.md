# Catalog Four-Market Materialization Audit — 2026-07-23

**Base SHA (origin/main at audit time):** `0ce62bca0533e3b919f42a668456b60f8d6f716e`
**Branch:** `agent/catalog-four-market-plan-20260723`
**Agent:** Pearl_GitHub (lane `catalog-four-market-plan`)
**Scope:** re-derive per-locale catalog materialization state for all 14 registered markets,
live, from `origin/main` git-tracked state only — correcting or confirming a pasted operator
closeout whose two cited "delivered" commit SHAs do not resolve in this repo's history.

## 0. Headline finding

The closeout's **numeric table is accurate** once re-derived correctly (see Section 2) — but its
**provenance was not**: no PR, commit, or branch on `origin/main` corresponds to the deliverable
it claims, and this session found no way to independently confirm the two commit SHAs it cited
(see Section 4). This audit re-derives every number from scratch via `git ls-files` on a clean,
`origin/main`-based branch and does not restate the closeout's table as fact anywhere without this
independent confirmation sitting next to it.

## 1. Method

For each of the 14 registered markets (`config/localization/locale_registry.yaml` -> `all_locales`),
three counts were derived via `git ls-files <path>` on this branch:

1. **Text-book plans** -- `config/source_of_truth/book_plans_<locale>/*.yaml` (the convention used
   for en_US Listings per `docs/PROGRAM_STATE.md`, and mirrored per-locale for all 14 markets).
2. **Manga series plans** -- `config/source_of_truth/manga_series_plans/<Locale>/*.yaml` (the
   allocation -> series-plan layer driven by `config/manga/locale_genre_allocations.yaml`, per
   `docs/specs/MANGA_100PCT_PRODUCTION_ROADMAP_2026-07-03.md` M2/M7).
3. **Manga (episode) book plans** -- `config/source_of_truth/manga_book_plans/<brand>__<Locale>__<genre>__seriesNN/ep_*.yaml`
   (a deeper, auto-generated per-episode listing layer, distinct from and downstream of item 2).

A fourth column, **translated EPUBs**, was derived from `git ls-files artifacts/epubs/`.
**Every count in Section 2 is `git ls-files`, not `find`/`ls`** -- see Section 5 for why that
distinction matters.

## 2. Live-verified 14-market table (supersedes the closeout's 4-market table)

| Locale | Text-book plans (tracked) | Manga series plans (tracked) | Manga book-plan dirs / files (tracked) | Translated EPUBs (tracked) |
|---|---:|---:|---:|---:|
| en_US | 32,401 | 273 | 266 / 3,724 | 0 (90 EN-only EPUBs exist; no locale variants) |
| zh_CN | 1,500 | 268 | 266 / 3,724 | 0 |
| zh_TW | **0** | 274 | 270 / 3,780 | 0 |
| zh_HK | **0** | **0** | 0 / 0 | 0 |
| zh_SG | 900 | 0 | 0 / 0 | 0 |
| ja_JP | **0** | 269 | 266 / 3,724 | 0 |
| ko_KR | **0** | 266 | 266 / 3,724 | 0 |
| es_US | 4,720 | 0 | 0 / 0 | 0 |
| es_ES | 31,920 | 0 | 0 / 0 | 0 |
| fr_FR | 32,000 | 390 | 0 / 0 | 0 |
| de_DE | 30,282 | 0 | 0 / 0 | 0 |
| it_IT | 13,420 | 0 | 0 / 0 | 0 |
| hu_HU | 14,480 | 0 | 0 / 0 | 0 |
| pt_BR | 32,000 | 0 | 0 / 0 | 0 |

**Total tracked EPUBs on `origin/main`:** 90, all under `artifacts/epubs/way_stream_sanctuary/` or
`artifacts/epubs/warrior_calm/` -- zero locale-specific subdirectories exist anywhere in the tree.
Zero locale-native sellable EPUBs exist for any of the 14 markets at any scale -- consistent with
`docs/PROGRAM_STATE.md`'s Localization row ("zero locale-native sellable Pearl Prime catalog
EPUBs at scale").

Non-CJK text-plan counts (es_US 4,720 / es_ES 31,920 / de_DE 30,282 / it_IT 13,420 / hu_HU 14,480 /
fr_FR 32,000 / pt_BR 32,000) are uneven and do not cleanly bucket into "0 or full" -- this audit
did not investigate why (out of scope: audit + plan only, this lane is scoped to the
ja_JP / ko_KR / zh_TW / zh_HK four-market question) but flags it as a real, open discrepancy for a
future lane, not something to be smoothed over.

## 3. Diff against the closeout's claimed 4-market table

| Cell | Closeout claim | Live re-derivation (this audit) | Match? |
|---|---|---|---|
| ja_JP manga plans | 269 | 269 (`manga_series_plans/ja_JP`, tracked) | Match |
| ja_JP text plans | missing (0) | 0 (`book_plans_ja_jp`, tracked) | Match |
| ko_KR manga plans | 266 | 266 (`manga_series_plans/ko_KR`, tracked) | Match |
| ko_KR text plans | missing (0) | 0 (`book_plans_ko_kr`, tracked) | Match |
| zh_TW manga plans | 274 | 274 (`manga_series_plans/zh_TW`, tracked) | Match |
| zh_TW text plans | missing (0) | 0 (`book_plans_zh_tw`, tracked) | Match |
| zh_HK | neither | 0 manga series plans, 0 text plans, 0 manga book-plan dirs | Match |

**Conclusion: the closeout's 4-market numeric table is correct** when scoped to git-tracked state
on `origin/main`. This is a genuinely useful, re-derivable finding. What is **not** verified is the
closeout's sourcing -- no commit matching its claimed delivery exists on `origin/main` (Section 4).
This audit's authority is the live `git ls-files` derivation in Section 2, run independently of the
closeout.

### Qualitative depth-check (not in the closeout, added here)

Even where "manga plans" exist (ja_JP/ko_KR/zh_TW), a sampled `manga_book_plans` episode file --
`config/source_of_truth/manga_book_plans/adhd_forge_mystery__ja_JP__action_battle__series01/ep_001.yaml` --
reads:

```
title: 'TBD -- ep_001'
localized_titles:
  ja_JP: TBD -- ep_001
```

with no chapter script attached. This is an auto-generated **listing** scaffold
(`# Auto-generated by scripts/manga/generate_book_plans_from_series.py -- do not hand-edit.`), not
an authored story. Per the CLAUDE.md manga doctrine ("a `series_plan` is a listing, not a story"),
the honest layer for ja_JP/ko_KR/zh_TW's "manga plans" -- at least for the sampled series -- is
**CONFIG-EXISTS**, not CODE-WIRED or EXECUTED-REAL. This audit sampled one series per locale, not
an exhaustive sweep; a full authored-vs-listing census across all ~266-274 series per locale is out
of scope for this lane.

## 4. Commit-SHA provenance check

The task briefing states the closeout arrived with two "delivered" commit SHAs that a prior
investigation found do not resolve via `git cat-file -t`. The literal SHA strings were not
reproduced in this lane's own prompt, so this audit cannot re-run `git cat-file -t <sha>` against
them directly. What this audit does confirm independently:
- `gh pr list --search "four market"` -> zero results.
- `gh pr list --search "catalog"` / `"zh_HK"` / `"ja_JP"` -> no PR proposes or claims a
  ja_JP/ko_KR/zh_TW/zh_HK four-market completion delivery; matches are unrelated content/translation
  lanes (see Section 6).
- No branch, tag, or commit message found via `git log --all --oneline | grep -i "four.market"`
  on this fetch of `origin`.

Whatever the two closeout SHAs pointed to, **nothing matching the closeout's claimed deliverable
exists on `origin/main` today**. Treat the closeout's SHAs as unverified pending someone re-checking
the literal strings against `git cat-file -t`.

## 5. Note on shared-checkout vs. isolated-worktree hygiene (process finding, not a data finding)

Mid-audit, this session briefly explored via the repo's shared main checkout
(`/Users/ahjan/phoenix_omega`, a separate `git worktree` entry from this lane's isolated worktree)
before catching the error and redoing every count from this branch's own isolated worktree. That
shared checkout currently carries a sibling session's **uncommitted** work (an in-progress edit to
`docs/PROGRAM_STATE.md`'s Manga section and an untracked
`artifacts/qa/MANGA_VISION_CONFORMANCE_AUDIT_2026-07-22.md`, both corresponding to open, unmerged
PR #74 -- "docs(qa): manga vision-conformance re-audit 2026-07-22"). None of that affects this
audit's numbers: every count in Section 2 was (re-)derived from `git ls-files` on this lane's own
clean, `origin/main`-based branch, which carries no such modifications. It is flagged here only as
a process note -- multiple concurrent agent sessions sharing one physical checkout is a known repo
hazard -- and this lane's own output should not be miscredited to or blamed on that sibling
session's unmerged draft. For what it's worth, PR #74's draft locale-plan counts for
ja_JP/ko_KR/zh_TW/zh_CN/fr_FR/en_US (269/266/274/268/390/273) match this audit's
independently-derived counts exactly -- unsurprising, since both read the same underlying tracked
files, but noted as consistent.

## 6. Open PR / workstream overlap check

- `gh pr list --search "catalog"`, `--search "four market"`, `--search "zh_HK"`, `--search "ja_JP"`
  -- no PR proposes a four-market completion program. PR #74 (manga vision re-audit, open -- see
  Section 5) and a large wave of zh-TW name-registry / register-rewrite / retranslate PRs
  (#61/#62/#67/#68/#69/#72/#78/#80/#87/#88/#90/#91/#92/#93/#131) are all **content-authoring /
  translation-QA** lanes, not catalog-plan or manga-plan materialization lanes -- no direct
  collision with this lane's audit-plus-plan deliverable.
- Existing coordination project: `proj_manga_catalog_reconciliation_20260426` (status `active`,
  `artifacts/coordination/ACTIVE_PROJECTS.tsv`) already owns manga catalog reconciliation
  authority docs (`docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md`,
  `docs/GENRE_PORTFOLIO_PLAN.md`, `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`) -- this lane adds a
  workstream row under that existing project rather than starting a new one (see
  `docs/specs/CATALOG_FOUR_MARKET_COMPLETION_PLAN.md` and the `ACTIVE_WORKSTREAMS.tsv` update).

## 7. Existing stub/untranslated-copy gate found (no new script written)

Per the lane contract, before authoring a new `check_no_untranslated_copy_padding.py`, this audit
searched for an existing equivalent. **One already exists and is already CI-wired:**
`scripts/ci/check_title_language_conformance.py` (mirrored at
`scripts/localization/check_title_language_conformance.py`), wired as **gate 34**
("Title/subtitle language conformance") in `scripts/run_production_readiness_gates.py` (line 1034).
It detects:
- `english_copy_through` -- locale string byte-identical to the en-US reference string,
- `ascii_only_in_cjk_locale` -- a CJK-script locale title/subtitle with zero CJK/Kana/Hangul
  codepoints,
- `wrong_script` -- zh-TW/zh-HK strings that fail a Traditional-required opencc + big5 check, and
  the zh-CN/zh-SG Simplified-required mirror,

scoped to `book_plans_<locale>` and the `manga_series_plans/<locale>` title field (manga
`title: TBD` is explicitly allowed by its own spec, S4.5 of
`docs/specs/WORLDWIDE_PLAN_COMPLETENESS_V1_SPEC.md` -- TBD is a listing placeholder, not
copy-through). Per its own header comment, ja_JP/ko_KR/de_DE/es_ES/es_US/fr_FR/hu_HU/it_IT are
already 0 non-conformant; pt_BR/zh_CN/zh_HK/zh_SG/zh_TW rollout is in progress. This audit cites
and reuses this gate rather than duplicating it -- see the plan doc's CI rule section for how it's
invoked for the four-market program.

## 8. Standing constraint carried into the plan (not lifted here)

`config/source_of_truth/manga_series_plans/ko_KR/*.yaml` shows `distribution_status:
hold_pending_market_clearance` live on multiple ko_KR series (e.g.
`spiritual_ground_supernatural__ko_KR__supernatural_mystery__series01.yaml`,
`warrior_calm_cultivation__ko_KR__dark_fantasy__series02.yaml`,
`night_reset_healing__ko_KR__dark_fantasy__series01.yaml`), per
`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` D-18 (Korea AI Act enforcement clarity, post-Jan
2027). This audit does not touch or recommend lifting that hold -- it is an operator/legal-tier
call, out of scope for this lane -- and it is carried forward as a standing constraint in the plan
doc.

## 9. Proof root / representative commands

All commands were run from this lane's own isolated worktree
(`/Users/ahjan/phoenix_omega/.claude/worktrees/agent-a44a14eb8ebd93d42`) on branch
`agent/catalog-four-market-plan-20260723` (base `origin/main`
`0ce62bca0533e3b919f42a668456b60f8d6f716e`):

```
git ls-files config/source_of_truth/book_plans_<locale>/
git ls-files config/source_of_truth/manga_series_plans/<Locale>/
git ls-files "config/source_of_truth/manga_book_plans/*__<Locale>__*"
git ls-files artifacts/epubs/
git ls-files scripts/ci/check_title_language_conformance.py
grep -n "check_title_language_conformance" scripts/run_production_readiness_gates.py
grep -rl "hold_pending_market_clearance" config/source_of_truth/manga_series_plans/ko_KR/
gh pr list --search "catalog" / "four market" / "zh_HK" / "ja_JP"
gh pr view 74 --json state,title
```
