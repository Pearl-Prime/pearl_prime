# STORE_SERIES_NAMING_ENGINE_V1_SPEC

Status: REFRESHED SPEC
Classification: KEEP
Source archive: `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`
Source commit: `4e314f94bb906daf0e705501c48a1bf86e7f4b7f`
Source SHA256: `39518d02dbc10a2502f0e0b32ba283476190f4fbf0732cd5cdc7f071780faea1`
GitHub writes: none; current GitHub substrate blocked.

## Research inputs available (2026-07-23)

`artifacts/research/SERIES_TITLES_SUBTITLES_PLATFORM_SEO_RESEARCH_2026-07-23.md` supplies the
platform-mechanics grounding this spec needs before `config/naming/series_taxonomy.yaml` gets
built: per-platform series-metadata objects (KDP Series name/number exact-match rules, Google
Play's genre-conditional series-page display, Apple's series-completeness rule, Audible's
ASIN-inherited series page, Spotify's and Ximalaya's weaker/unverified series taxonomy), the
cross-book keyword-ladder strategy (series name = fixed brand asset, title = distinguishing
keyword, subtitle = platform-specific SEO payload), and series planning/duration guidance. Read
it before implementing the collision manifest or the taxonomy schema below.

## Current Relevance

This spec is still high-value with no substantive concept change. Phoenix needs
store-safe series naming that generalizes beyond one winning title family while
preserving reader promise, author fingerprint, discoverability, and catalog
coherence.

## Reconcile, Do Not Rebuild

Implement as an extension of existing naming machinery:

- `phoenix_v4/naming/generator.py`
- current catalog/store metadata generators
- current author fingerprint and marketing feed systems

Do not create a disconnected title generator or separate marketing taxonomy.

## Refreshed Requirements

The naming engine must:

- produce store-safe series titles and subtitles with deterministic provenance;
- avoid stale W0-only assumptions while retaining proven store learnings;
- preserve topic, persona, promise, tone, and author-brand constraints;
- prevent collisions across current and planned series;
- mark operator-review status before any storefront use.

Suggested future config:

- `config/naming/series_taxonomy.yaml`
- optional collision manifest emitted under `artifacts/qa/`
- tests for collision, forbidden terms, and topic/persona fit

## The four disparate series systems (found 2026-07-23 — read before building the taxonomy)

Investigating "is series naming wired to platform best-practice" found FOUR separate,
unreconciled systems already in the repo. Read this before building
`config/naming/series_taxonomy.yaml` so a fifth parallel system doesn't get added by accident:

1. **Topic-cluster series** — `config/catalog_planning/series_templates.yaml`, canonical
   `series_title`/`series_subtitle` per topic (e.g. `anxiety`), consumed by
   `phoenix_v4/naming/keyword_bank.py:get_keywords()` for every brand's title/subtitle generation.
   Working, wired, unrelated to the other three.
2. **Waystream store-series** — `store_series: {id, name}` on Waystream book-plan YAMLs (730/800
   populated). No canonical generator writes this field — every value is hand/LLM-authored per
   book. A new hard CI gate (`scripts/ci/check_store_series_name_consistency.py`, wired as gate 44
   in `run_production_readiness_gates.py`) now verifies every `store_series.id` maps to exactly one
   distinct name — first run: 0 hard violations across 120 series / 800 plans, but 111 WARN-level
   duplicate-`installment_number` findings (**fixed same day** — see Follow-on below).
3. **The other-37-brands candidate generator** — `phoenix_v4/naming/generator.py`'s
   `generate_store_series_candidates()` / `is_generic_store_series_name()`, plus
   `scripts/catalog/dry_run_store_series_names.py`. Real, tested, merged
   (`spec5-store-series-naming-engine=MERGED`). Explicitly skips Waystream. Dry-run only —
   nothing has ever been applied to a real plan; **32/36 brand names now ratified** — see Follow-on.
4. **A prepublish series-diversity gate suite** — `phoenix_v4/qa/validate_series_diversity.py` +
   `scripts/ci/check_series_metadata_intent.py` (title-similarity, unique `search_intent_id`) +
   `scripts/ci/check_series_content_uniqueness.py`, orchestrated by
   `scripts/ci/run_prepublish_gates.py`. Real, tested — but **not wired into any CI workflow**, and
   it requires a "compiled plan .json" format with a `chapter_slot_sequence` shape that nothing in
   the current spine pipeline produces. Likely orphaned from an earlier pipeline design. Do not wire
   it into CI without first confirming a real producer of that JSON shape exists — it would
   currently pass trivially with 0 plans found, which is worse than not running it at all.

**Also newly wired (2026-07-23):** `scripts/release/build_epub.py`'s `build_epub()` now accepts
optional `series_name`/`series_index` and emits the EPUB3 `belongs-to-collection`/
`collection-type`/`group-position` OPF meta triple when a series name is present — so series
identity travels with the file itself, independent of storefront-dashboard entry. Wired through
`scripts/release/batch_waystream_epubs.py` (reads `plan.store_series.name` /
`plan.installment_number`); `batch_catalog_epubs.py` intentionally NOT wired — its plans carry no
per-book series data in this schema.

**Follow-on (2026-07-23, same day):**
- The 111 WARN-level duplicate-`installment_number` findings from gate 44's first run are fixed:
  `scripts/catalog/fix_store_series_installment_numbers.py` deterministically renumbered 550/800
  Waystream plans across 110/120 series (surgical, single-line diffs — no other field touched).
  Gate 44 now reports 0 WARN on duplicates; the only remaining WARN is the pre-existing "70 plans
  have no store_series" gap, unchanged by this fix.
- System #3's 65 dry-run candidates are **partially ratified** (`OPD-20260723-STORE-SERIES-RATIFY-01`):
  32/36 non-Waystream brands' `series_title` approved, recorded in
  `config/catalog_planning/ratified_store_series_names.yaml`. The dry-run's `series_subtitle` field
  was explicitly **not** ratified — it's a crude illustrative template (hardcoded
  `persona_id="general_readers"`, an article-agreement grammar defect, e.g. "A Adhd Forge series")
  that should not ship verbatim; real per-book subtitles for these brands still come from the
  existing naming engine (System #1). 4 brands (`optimizer`, `qi_foundation`, `spiritual_ground`,
  `stoic_edge`) remain unresolved — every dry-run candidate for them was rejected as generic or a
  cross-brand collision; they need a fresh generation pass before another ratification round.
  **This ratifies a brand-level name only — it does not write `store_series` onto any individual
  book plan** for these 36 brands (they have no per-book series wiring yet, unlike Waystream);
  applying the ratified name to real per-book catalog metadata is a separate, not-yet-scoped lane.

## Acceptance Labels

- `STRUCTURAL_SPEC_PASS`: generated candidates pass schema, collision, and
  forbidden-term checks.
- `OPERATOR_READ_PASS`: operator/editor approves candidate naming families for
  storefront use.
- `PRODUCTION_PUBLIC_RELEASE_AUTHORIZED`: not granted by this spec.
