# Catalog Four-Market Completion Plan — ja_JP -> ko_KR -> zh_TW -> zh_HK

**Status:** SPECCED (plan authored; no content authoring performed by this lane)
**Generated:** 2026-07-23
**Authority basis:** `artifacts/qa/catalog_four_market_audit_20260723/SUMMARY.md` (live-verified
counts, this session); `docs/CJK_CATALOG_PLAN.md`; `docs/US_CATALOG_PLAN.md`; `docs/PROGRAM_STATE.md`
(Localization + Manga sections, `origin/main` committed version); `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`
(D-18/D-19 distribution-status framework).
**Parent coordination project:** `proj_manga_catalog_reconciliation_20260426` (see
`artifacts/coordination/ACTIVE_PROJECTS.tsv` / `ACTIVE_WORKSTREAMS.tsv`).
**Owner (this document):** Pearl_GitHub / Pearl_Research framing, lane `catalog-four-market-plan`.

**Do not restate any number in this document as fact without re-checking against
`artifacts/qa/catalog_four_market_audit_20260723/SUMMARY.md` Section 2 first** -- that audit is the
sole source of truth for what currently exists on `origin/main`; a pasted operator closeout that
originally proposed this program cited two commit SHAs that do not resolve in this repo's history
and must not be re-cited as provenance for anything in this plan.

## 1. What is actually true today (live-verified, not the closeout's provenance)

| Locale | Text-book plans (tracked) | Manga series plans (tracked) | Manga episode-plan dirs (tracked) | Translated EPUBs |
|---|---:|---:|---:|---:|
| ja_JP | 0 | 269 | 266 | 0 |
| ko_KR | 0 | 266 | 266 | 0 |
| zh_TW | 0 | 274 | 270 | 0 |
| zh_HK | 0 | 0 | 0 | 0 |

This matches the closeout's original numeric claim for these four markets exactly (see audit
Section 3), even though the closeout's own sourcing could not be verified. All four markets are
also at **zero translated EPUBs** -- none of this program's "plans" have produced a sellable
locale-native book yet, for any market, including the three that have manga series plans.

Additionally (found by this lane's own sampling, not previously documented in the closeout): the
existing ja_JP/ko_KR/zh_TW manga "plans" are themselves auto-generated **listing** scaffolds
(`title: TBD`, no chapter script) -- CONFIG-EXISTS layer, not authored stories. "Manga plans exist"
for these three markets should be read as "the allocation-to-listing chain has run", not "there are
manga stories ready to render."

## 2. Governed sequence: ja_JP -> ko_KR -> zh_TW -> zh_HK

The sequence is deliberately staged, not parallel, because each stage either produces the
prerequisite the next stage needs, or exists to prevent a repeat of the "listing-as-story" /
"copy-padding" failure modes this repo has hit before (see CLAUDE.md Manga Vision-Conformance
Doctrine and the title/metadata English copy-through project).

### Stage 1 -- ja_JP

**Goal:** localize the existing English structural plans into real ja_JP text-book plans, and move
the existing 266 ja_JP manga series/episode listings from CONFIG-EXISTS to authored
(`chapter_script_writer_handoff`, >=6 authored panels, no stub markers, per
`scripts/ci/check_manga_story_authored.py`).

**Preconditions before starting content work (verify, do not assume):**
- `book_plans_ja_jp/` is empty on `origin/main` today (0 tracked files) -- Stage 1 text work starts
  from the `book_plans_en_us/` structural convention (title/subtitle/keywords/BISAC/price schema),
  translated, not copied. `check_title_language_conformance.py` (gate 34) already reports ja_JP at
  **0 non-conformant** for the fields it currently checks, so this is a genuinely empty lane, not a
  contaminated one -- there is nothing to clean up before starting.
- Manga: 266 series-level listings exist; a sample episode file
  (`config/source_of_truth/manga_book_plans/adhd_forge_mystery__ja_JP__action_battle__series01/ep_001.yaml`)
  is a stub (`title: TBD -- ep_001`). Story authoring (not this lane's job) must produce real
  `chapter_script_writer_handoff` content per series before any of these 266 can be called "story",
  per CLAUDE.md doctrine item 2 (listing-as-story gate).
- Native Japanese QA: route through the `translate-ja` locale-native agent (per repo convention;
  see `.claude/agents/translate-ja.md`) for both the text-book localization and any manga dialogue
  authoring QA pass. Do not route ja_JP prose through Qwen/Gemma (Tier-2) for anything a human
  reviews before ship -- per CLAUDE.md LLM Tier Policy, ja_JP authored content that ships is
  Tier-1 (Claude Code, operator-present) work, same as English bestseller prose.

### Stage 2 -- ko_KR

**Goal:** same localize-and-author work as Stage 1, but distribution stays **held**.

**Standing constraint (do not lift, not this lane's call):** `distribution_status:
hold_pending_market_clearance` is already live on multiple ko_KR series-plan YAMLs
(`config/source_of_truth/manga_series_plans/ko_KR/spiritual_ground_supernatural__ko_KR__supernatural_mystery__series01.yaml`
and others -- see audit Section 8), per `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` D-18 (Korea AI
Act enforcement clarity expected post-Jan 2027). **Render-and-hold** is the sanctioned pattern:
text/manga authoring and QA may proceed (sunk-cost compute is intentional per D-18's own rationale),
but no ko_KR asset may flip to a `distributed` status or attach to any storefront/GHL feed row until
an operator/legal-tier decision lifts the hold. This plan explicitly does not attempt, recommend, or
schedule that lift.

### Stage 3 -- zh_TW

**Goal:** re-author Chinese structure for Taiwan Traditional -- not a straight port of zh_CN or a
Simplified-to-Traditional character conversion of anything -- and enforce the Readmoo /
direct-upload dedup the market requires.

**Preconditions:**
- zh_TW already has 274 manga series-plan listings and the deepest manga episode-plan footprint of
  any locale in this audit (270 dirs / 3,780 files, edging out even en_US/ja_JP/ko_KR's 266/3,724).
  Text-book plans are at 0 tracked, same gap as ja_JP/ko_KR.
- zh_TW is under **active, heavy translation-QA churn right now** -- this session found a large
  wave of open zh-TW-specific PRs (name-registry conversion, register-rewrite scope correction,
  Simplified-contamination gate, corrupted-batch retranslation: PRs #61/#62/#67/#68/#69/#72/#78/#80/
  #87/#88/#90/#91/#92/#93/#131 at the time of this audit). **Any zh_TW content-authoring work this
  plan schedules must be sequenced behind those in-flight lanes, not run in parallel against the
  same files** -- check `gh pr list --search "zh-TW"` fresh before starting Stage 3 execution; this
  plan does not itself touch any of those files.
- `derive_zh_hk_from_zh_tw.py` already exists in `scripts/localization/` -- Stage 4 (zh_HK) is
  expected to consume zh_TW's *approved* output through this script, not re-author zh_HK from
  scratch. This is why zh_TW must be approved (not just landed) before Stage 4 starts.
- Distribution dedup: zh_TW distribution partners include Readmoo alongside direct-upload channels
  (per `docs/CJK_CATALOG_PLAN.md` §2 TW row: "LINE Comics TW, standalone print"). Before any zh_TW
  asset ships, confirm no duplicate listing exists across the Readmoo-facing and direct-upload
  catalog rows for the same title/subtitle pair -- reuse
  `scripts/ci/check_waystream_catalog_uniqueness.py`'s dedup pattern (title/subtitle/pair
  distinctness) as the template if a zh_TW-specific dedup check needs to be written; do not invent a
  new dedup algorithm from scratch.

### Stage 4 -- zh_HK

**Goal:** derive only after zh_TW is operator-approved (not merely merged) -- HK-specific
re-authoring (Cantonese metadata layer, HK-specific platform partners, local cultural content per
`docs/CJK_CATALOG_PLAN.md`'s HK addendum) plus a distribution approval gate.

**Preconditions:**
- zh_HK is at true zero today: 0 text-book plans, 0 manga series plans, 0 manga episode plans, 0
  EPUBs -- confirmed independently in this audit (Section 2/3), matching the closeout's claim.
- `docs/CJK_CATALOG_PLAN.md`'s HK addendum (2026-04-27) already states the mechanism: "Hong Kong
  (`zh_HK`) shares Traditional Chinese script with TW... Format mix and brand portfolio default to
  TW; per-locale strategic divergence (Cantonese metadata, HK-specific platform partners, local
  cultural content) is a follow-up Pearl_Research deep-research task tracked under the manga catalog
  reconciliation spec." This plan formalizes that follow-up as Stage 4, gated on Stage 3 approval,
  not concurrent with it.
- Do not seed zh_HK book_plans/series_plans by mechanically copying zh_TW files and relabeling the
  locale field -- that is exactly the "copy untranslated/wrong-locale files to make a directory
  count green" failure mode this plan's CI rule (Section 3) exists to block. `derive_zh_hk_from_zh_tw.py`
  already exists for a reason; if it does not yet do proper HK-specific re-authoring (Cantonese
  metadata etc.), that is Stage 4's actual content-authoring work, not something to route around.

## 3. CI-checkable rule: no copy-padding to make a directory count green

**Rule:** No PR may create files under `config/source_of_truth/book_plans_{ja_jp,ko_kr,zh_tw,zh_hk}/`
or `config/source_of_truth/manga_series_plans/{ja_JP,ko_KR,zh_TW,zh_HK}/` (or the corresponding
`manga_book_plans/*__<Locale>__*` episode dirs) whose title/subtitle/body text is byte-identical
English copy-through, or (for zh_TW/zh_HK) Simplified-script content mechanically relabeled as
Traditional, merely to move a materialization count from 0 to non-zero.

**Enforcement -- an existing gate already covers this; do not write a new one.**
`scripts/ci/check_title_language_conformance.py` (mirrored at
`scripts/localization/check_title_language_conformance.py`) is already wired as **gate 34** in
`scripts/run_production_readiness_gates.py` and already detects exactly this failure class:
`english_copy_through` (byte-identical to en-US reference), `ascii_only_in_cjk_locale`, and
`wrong_script` (Traditional-vs-Simplified via opencc + big5/gb2312 codec-encodability, avoiding the
documented false-positive class on script-ambiguous characters -- see
`reference_zhtw_simplified_detection_big5` memory). Per its header comment, ja_JP and ko_KR are
already at 0 non-conformant; zh_TW and zh_HK are part of the in-progress pt_BR/zh_CN/zh_HK/zh_SG/
zh_TW rollout this gate already tracks.

**What this plan adds (not a new script, a usage requirement):** any PR that lands Stage 1-4
content for these four locales MUST run
`PYTHONPATH=. python3 scripts/ci/check_title_language_conformance.py --bootstrap-mode` (or the
non-bootstrap mode once a locale is declared complete) and attach the output to its PR description,
same as the existing gate-34 convention in `scripts/run_production_readiness_gates.py`. If a future
stage needs a check this gate does not cover (e.g., full-body atom-level copy-padding beyond
title/subtitle, or manga panel-dialogue copy-padding), that is a genuine gap and a new,
narrowly-scoped script should be proposed then -- with its own `pytest` test asserting a padded file
is caught and a genuinely-translated file passes -- not invented speculatively here.

## 4. Sequencing rationale (why staged, not parallel)

1. ja_JP first: zero in-flight PR collisions found for ja_JP text-plan or manga-story work at audit
   time (one open PR, #141, adds a *new* series rather than touching the localization gap); cleanest
   lane to start.
2. ko_KR second: same content-authoring shape as ja_JP, but every ko_KR asset must additionally
   carry `hold_pending_market_clearance` until distribution -- sequencing it right after ja_JP means
   the Stage 1 authoring playbook is proven once before adding the hold-state complexity.
3. zh_TW third: highest existing manga-listing footprint (274 series / 270 episode dirs) but also
   the most active, most collision-prone locale in the repo right now (15 open zh-TW PRs at audit
   time). Placing it third gives those in-flight lanes time to land before this program's own zh_TW
   work starts, reducing merge-conflict risk.
4. zh_HK fourth, gated on zh_TW approval: zh_HK's own strategic doc (`docs/CJK_CATALOG_PLAN.md` HK
   addendum) already says HK content should derive from approved zh_TW output via
   `derive_zh_hk_from_zh_tw.py`, not be authored independently -- doing zh_HK before zh_TW is
   approved would mean deriving from an unstable, still-churning source.

## 5. Explicit non-goals of this plan

- **Does not lift the ko_KR `hold_pending_market_clearance` distribution hold.** That is an
  operator/legal-tier call (Korea AI Act enforcement posture) per D-18 -- out of scope here, carried
  forward as a standing constraint.
- **Does not author any ja_JP/ko_KR/zh_TW/zh_HK book or manga content.** This document and the
  accompanying audit are audit-plus-plan only, per this lane's contract.
- **Does not weaken, replace, or duplicate `check_title_language_conformance.py` / gate 34.** This
  plan cites and requires its use; it does not modify it.
- **Does not restate the original closeout's table as fact independent of this lane's own
  re-derivation.** Every number in Section 1 traces to
  `artifacts/qa/catalog_four_market_audit_20260723/SUMMARY.md`, not to the closeout.

## 6. Next actions (for whoever picks up Stage 1)

1. Confirm `book_plans_ja_jp/` and `manga_series_plans/ja_JP/` state is unchanged from this audit's
   snapshot (`git ls-files` counts in Section 1) before starting -- catalog state moves fast in this
   repo (dozens of concurrent agent sessions); re-verify, do not trust this document's numbers past
   their `origin/main` SHA (`0ce62bca0533e3b919f42a668456b60f8d6f716e`).
2. Route ja_JP text-plan localization + manga story-authoring through `translate-ja` (Tier-1,
   operator-present) per CLAUDE.md LLM Tier Policy.
3. Attach `check_title_language_conformance.py` output to the Stage 1 PR per Section 3.
4. Update this plan doc's Section 1 table and `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`'s
   Stage 1 row status when Stage 1 lands, before starting Stage 2.
