# Session Handoff — Series Titles/Subtitles SEO Research → Pipeline Wiring (2026-07-23)

## TL;DR for the next session

Three PRs from this session are open and **BLOCKED on a fast-moving `main`**, not on their own
content — all governance/tests specific to their diffs pass clean. Rebase/re-push each to pick up
a fresh CI run now that `main`'s Core-tests/DATA_DICTIONARY blocker is fixed (PR #133, merged).
Start there. Everything below is context for why these PRs exist and what's still open.

| PR | Branch | Content | Status at session end |
|---|---|---|---|
| [#95](https://github.com/Pearl-Prime/pearl_prime/pull/95) | `agent/series-titles-subtitles-seo-research-20260723` | Research doc | OPEN, blocked on stale main-red CI |
| [#104](https://github.com/Pearl-Prime/pearl_prime/pull/104) | `agent/store-series-consistency-epub-metadata-20260723` | New CI gate + EPUB metadata | OPEN, blocked on stale main-red CI |
| [#120](https://github.com/Pearl-Prime/pearl_prime/pull/120) | `agent/store-series-installment-renumber-and-ratify-20260723` | 550-file renumber + ratification | OPEN, blocked on stale main-red CI + a **new, unrelated** zh-CN parse-sweep regression (see below) |

## Session narrative

1. **`/piper` request** — operator asked for a Pearl_Research prompt on book/audiobook series
   titles+subtitles, how subtitles drive SEO per platform, and series-planning/duration best
   practices. Authored a paste-ready EXECUTE prompt grounded on existing repo research
   (`PLATFORM_ALGORITHM_RESEARCH_2026.md`, `bestseller_titles_seo_covers_research.md`,
   `PODCAST_PLATFORM_MARKETING_RESEARCH.md`) and the open `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`.
2. **Operator: "execute this now"** — ran the prompt myself instead of handing it off. Produced
   `artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md` (web-researched,
   cited) covering per-platform series-metadata mechanics (Amazon KDP, Google Play, Apple Books,
   Audible/ACX, Spotify, Ximalaya) and series planning/duration. Landed as **PR #95** via the
   git-plumbing pattern (temp index off `origin/main^{tree}` — the shared working tree was stale/
   under heavy load, `git status` was timing out at ~488 load average from concurrent sessions).
3. **Operator: "are we wired to do series titles/subtitles best in pipeline?"** — investigated the
   actual code. Found series naming is real DATA in places but none of the platform-SEO mechanics
   from the research were wired: no exact-match name-consistency check, no EPUB collection metadata,
   and (bigger finding) **four disparate, unreconciled series-naming systems** already in the repo
   (see "The four systems" below).
4. **Operator approved a build lane** — used Plan Mode (two Explore-agent research rounds + one Plan
   agent to pressure-test the design) to scope exactly what to build vs. what to flag-not-build.
   Implemented and landed as **PR #104**:
   - `scripts/ci/check_store_series_name_consistency.py` (gate 44 in
     `run_production_readiness_gates.py`) — hard-fails if a `store_series.id` maps to >1 distinct
     `store_series.name`. First real run: **0 hard violations** across 120 series / 800 Waystream
     plans, but **111 WARN-level duplicate-`installment_number` findings** (fixed in a later PR,
     see below).
   - `build_epub()` in `scripts/release/build_epub.py` now accepts `series_name`/`series_index` and
     emits the EPUB3 `belongs-to-collection`/`collection-type`/`group-position` OPF meta triple.
     Wired through `batch_waystream_epubs.py`; `batch_catalog_epubs.py` intentionally left unwired
     (no equivalent per-book series data in that schema).
   - `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md` updated with the four-systems reconciliation note.
5. **Operator: "what next?"** — reported that all 3 required checks failing on both open PRs
   (Core tests, Drift detectors, Release gates) were pre-existing, main-wide, unrelated to either
   PR: a manga test regression (`test_story_excellence_gate.py::test_pass_fixtures[battle_en_us_genalpha]`)
   and a stale `docs/DATA_DICTIONARY.tsv`.
6. **Operator supplied PR #102** (a fix for exactly those two issues) and gave two more directives:
   **approve** ratifying the 65 dry-run series-name candidates from the earlier
   `spec5_store_series_naming_engine` lane, and **fix** the 111 WARN duplicate-installment findings.
   - Verified PR #102's relevance (confirmed file-for-file match to the two blockers). It was later
     auto-closed as superseded by **PR #133 (merged, `f42bc64f`)**, which landed the same manga fix
     without #102's unrelated social-media scope-creep — see "Open thread" below.
   - Investigated the 111 WARN findings before touching anything: they are **not** a data-entry bug.
     110/120 Waystream series deliberately bundle multiple internal topic-threads under one
     reader-facing series name (e.g. "Worth & Limits — for Managers" spans
     boundaries+imposter_syndrome+self_worth) — a real, correct product design — but each thread was
     numbered independently 1..N, so they collided once displayed together on one series page.
     Built `scripts/catalog/fix_store_series_installment_numbers.py` (deterministic renumber, sorted
     by original-number/topic/engine, surgical single-line diffs) and ran it: **550/800 plans
     renumbered across 110/120 series**. Gate 44 now reports 0 duplicate-installment WARNs.
   - Investigated what "ratify" should concretely mean before writing anything: the dry-run's
     `brand_series_plans.yaml` source turned out to be a **manga-planning file** being reused just
     for its brand→topic mapping; ratifying into it would conflate manga and book-series concepts.
     Instead created a new, clearly-scoped `config/catalog_planning/ratified_store_series_names.yaml`
     recording **32/36 non-Waystream brands' `series_title`** (first accepted dry-run candidate per
     brand) + `OPD-20260723-STORE-SERIES-RATIFY-01` in `operator_decisions_log.tsv`. Explicitly did
     **not** ratify the dry-run's `series_subtitle` field — it's a crude template (hardcoded
     `persona_id="general_readers"`, an article-agreement grammar defect, e.g. "A Adhd Forge
     series") not fit to ship verbatim; real subtitles still come from the existing naming engine.
     4 brands (`optimizer`, `qi_foundation`, `spiritual_ground`, `stoic_edge`) remain unresolved —
     every dry-run candidate for them was rejected as generic/collision.
   - Both landed together as **PR #120** (555 files — 550 mechanical renumbers + 5 real files;
     flagged the size proactively in the PR body; governance review passed it).
7. **Checked PR #120's CI** — found a NEW `parse-sweep` failure not present on #95/#104. Traced it
   before assuming anything: the flagged file
   (`atoms/entrepreneurs/compassion_fatigue/watcher/locales/zh-CN/CANONICAL.txt`, an empty
   `RECOGNITION v02` stub block) doesn't exist at all at my PR's parent commit and my diff never
   touches `atoms/` — it only exists on the live `origin/main` tip, which had moved past my parent
   via unrelated concurrent merges (the repo has pt_BR conformance batches and manga PRs merging
   every ~20 minutes right now). **Confirmed not caused by any PR from this session.**

## The four series-naming systems (read `STORE_SERIES_NAMING_ENGINE_V1_SPEC.md` §"four disparate
series systems" for full detail — this is the single most important thing to internalize before
touching series naming again)

1. **Topic-cluster series** (`config/catalog_planning/series_templates.yaml`) — working, wired,
   feeds every brand's title/subtitle generation via `keyword_bank.py`. Untouched this session.
2. **Waystream `store_series`** — on book-plan YAMLs, 730/800 populated, hand/LLM-authored, no
   canonical generator. Now has a consistency gate (this session) and clean installment numbering
   (this session). Still: 70/800 plans have no `store_series` at all (not fixed, not urgent).
3. **The other-37-brands candidate generator** (`generate_store_series_candidates()` +
   `dry_run_store_series_names.py`) — real, tested, merged, dry-run-only. **32/36 brand names now
   ratified** (this session). 4 brands unresolved. Subtitles from this generator are NOT ratified
   (quality issue, see above) — do not ship them.
4. **The orphaned prepublish diversity-gate suite** (`validate_series_diversity.py` +
   `check_series_metadata_intent.py` + `check_series_content_uniqueness.py`, orchestrated by
   `run_prepublish_gates.py`) — real, tested, but not wired into any CI workflow, and expects a
   "compiled plan JSON" shape that nothing in the current spine pipeline produces. **Do not wire
   this into CI** without first confirming a real producer of that JSON shape exists.

## Open threads for the next session (priority order)

1. **Rebase/re-push #95, #104, #120** now that #133 is merged (fixes Core-tests/DATA_DICTIONARY).
   They should go green on those three checks after a fresh CI run. `parse-sweep` on #120 may also
   need re-checking — it may already be clear if whatever introduced the zh-CN stub has been fixed
   by another concurrent merge by the time you read this; re-verify, don't assume either way.
2. **`atoms/entrepreneurs/compassion_fatigue/watcher/locales/zh-CN/CANONICAL.txt`** has a stub
   `RECOGNITION v02` block on live `main` — real defect, different subsystem (CJK translation
   content), not investigated further. Someone should fix or flag it.
3. **4 unresolved brand series names** (`optimizer`, `qi_foundation`, `spiritual_ground`,
   `stoic_edge`) — need a fresh `generate_store_series_candidates()` pass (different seed, or a
   curated `_TOPIC_SERIES_LEXICON` entry in `generator.py`) since all 3 original candidates each
   were rejected as generic/collision.
4. **70/800 Waystream plans have no `store_series`** — not investigated; unclear if intentional
   (standalone one-offs) or a gap. `check_store_series_name_consistency.py`'s WARN output names them.
5. **Applying ratified brand names to real per-book catalog metadata** — the ratification in
   `ratified_store_series_names.yaml` is name-only. These 36 brands have no per-book `store_series`
   wiring at all (unlike Waystream); building that (schema + generator + gate) is a separate,
   not-yet-scoped lane.
6. **System #4 (orphaned prepublish suite)** — if anyone wants real series-diversity/title-similarity
   enforcement in CI, the logic already exists and is well-tested; it just needs a real producer of
   the "compiled plan JSON" shape it expects, or a rewrite to consume the source-of-truth YAML shape
   instead.
7. **`config/naming/series_taxonomy.yaml`** (the spec's original suggested artifact) still doesn't
   exist. Read the four-systems note and the platform-SEO research doc fully before building it —
   the goal should be reconciling the four systems, not adding a fifth.

## Key artifacts from this session

- `artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md` — the research
- `scripts/ci/check_store_series_name_consistency.py` — gate 44
- `scripts/catalog/fix_store_series_installment_numbers.py` — renumber tool (idempotent, re-runnable)
- `config/catalog_planning/ratified_store_series_names.yaml` — 32 ratified brand series names
- `docs/specs/session_mining_batch_20260718/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md` — updated,
  read this first for full context
- `OPD-20260723-STORE-SERIES-RATIFY-01` in `artifacts/coordination/operator_decisions_log.tsv`

## Working-tree hygiene note (learned the hard way this session, twice)

The shared working tree at `/Users/ahjan/phoenix_omega` runs many concurrent sessions; `git status`
can time out entirely under load (~488 load average observed this session), and hot files
(`CANONICAL_ARTIFACTS_REGISTRY.tsv`, `operator_decisions_log.tsv`, and even code files like
`build_epub.py`/`run_production_readiness_gates.py`) can be **stale in the local working tree
relative to `origin/main`** even on a freshly-fetched branch — editing them in place risks silently
regressing another session's concurrent work. Before editing any hot/shared file, diff it against
`git show origin/main:<path>` first; if stale, rebuild from the live `origin/main` copy before
editing. Land via the plumbing pattern (temp index off `origin/main^{tree}`, explicit `git add`
paths only, gate on `git diff --cached --stat origin/main` showing exactly the intended file list)
rather than `git checkout -b` + normal commits — safer on this tree and doesn't require a working
`git status`.
