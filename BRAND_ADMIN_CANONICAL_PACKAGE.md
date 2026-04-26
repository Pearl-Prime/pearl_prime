# Brand Admin & Investor Materials — Canonical Package

Last updated: 2026-04-27

## Pipeline scope (READ FIRST)

This package governs **TWO distinct pipelines** which were intentionally separated
under operator decision **Path X** (2026-04-27, see `docs/PEARL_ARCHITECT_STATE.md`
BR-CANON-01 Path X cap entry). They share branding surfaces but have independent
brand registries, content engines, and revenue models. Cross-linking only — no
convergence is implied.

| Pipeline | Brand count | Authoritative registry | Generator path |
|---|---:|---|---|
| **Book** (Pearl_Prime) | 24 archetypes × 13 lanes = **312** | `config/brand_registry.yaml` (28-row locale-keyed seed) → `config/brand_management/global_brand_registry.yaml` (312 derived) | `scripts/brand_management/generate_global_registry.py` |
| **Manga** (Pearl_Brand catalog) | **37** brands | `config/manga/canonical_brand_list.yaml` (Path X canon) | `scripts/manga/derive_manga_lane_table.py` (deferred — see §Manga section below) |

The two registries do **NOT** share rows; they govern different content, different
distribution channels, and different revenue tiers. The 37 manga brands are
**not** a subset, superset, or transform of the 24 book archetypes.

## Canonical files

| File | Purpose | Audience |
|------|---------|----------|
| `brand_onboarding_hub.html` | Central entry point and brand directory | All brand admins (start here) |
| `us_brand_admin_v32_briefing.html` | V3.2 systems deep-dive, US market | US brand administrators |
| `jp_brand_admin_v32_briefing.html` | V3.2 systems + manga variants, bilingual EN/JP | JP brand administrators |
| `writer_v32_quick_reference.html` | Technical V3.2 field reference card | Writers and content producers |
| `PHOENIX_OMEGA_INVESTOR_DD.xlsx` | Investor due diligence workbook | Investors and business stakeholders |

## Rules

1. Do not create parallel or replacement versions of these files.
2. Improve in place when updates are needed.
3. The workbook's "Data Provenance" sheet explains which values are repo-backed, estimates, assumptions, or external.
4. All HTMLs are static, framework-free, and WordPress-safe.

## Where the numbers come from

The investor workbook contains four kinds of data:

- **REPO-BACKED** (green text): Verifiable from repo code, config, specs, or docs. Source path given.
- **ESTIMATE** (orange text, yellow background): Derived from a planning model. Reasonable but not verified by sales data.
- **ASSUMPTION** (red text, yellow background): Pre-revenue projection. Scenario modeling only.
- **EXTERNAL** (blue text): Sourced from third-party research or platform terms. Citation given.

Key facts: the system is pre-revenue. "2,160+ books" is a target (24 brands x 90), not a production count. All revenue figures are scenario projections. $0 COGS is accurate (auto-narration pipeline is repo-verified).

## Book pipeline brand count (Pearl_Prime)

**Canonical:** 24 brands × 90 books = **2,160 books target**.

Source registries (book pipeline only — DO NOT modify from manga-side work):

- `config/brand_registry.yaml` — 28-row locale-keyed seed (Pearl_Prime book registry)
- `config/brand_management/global_brand_registry.yaml` — 312 entries = 24 spiritual archetypes × 13 lanes (the *expanded view* of the 24-archetype seed across the 13-lane locale matrix)

The book pipeline's 24/312 framing is unchanged from prior canon and is independent of the manga catalog.

## Manga pipeline brand count (Pearl_Brand)

**Canonical:** **37 manga brands** per `docs/GENRE_PORTFOLIO_PLAN.md` and `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (PR #682).

Source registry (manga pipeline only):

- `config/manga/canonical_brand_list.yaml` — 37 brands (3 flagship + 16 core + 18 niche), each with demographic, primary_topic, secondary_topics, and notes per the GENRE_PORTFOLIO_PLAN ##### headers
- `config/manga/manga_brand_series_plan.yaml` — per-brand series allocation (consumer of the canonical list)

The 37 figure governs:

- Manga catalog reconciliation (`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` D-1..D-20)
- Genre portfolio strategy (`docs/GENRE_PORTFOLIO_PLAN.md` 12 strategic genre shells × per-brand allocation)
- Manga catalog plan generator (`scripts/manga/generate_catalog_plan_from_strategic.py`)
- Forthcoming manga lane table generator (`scripts/manga/derive_manga_lane_table.py` — deferred this pass; lane semantics TBD per Pearl_Brand judgment, see Open Question below)

**Cross-link to book pipeline:** the manga 37 are *not* derived from the book 24 archetypes and *not* a subset/superset of the book 312 expanded view. They are an independent canon governing the manga distribution channel only.

**Pearl_Brand also owns dashboard surfaces** under DASH-02 (operator decision 2026-04-27, ratified in `docs/PEARL_ARCHITECT_STATE.md`). Dashboard surfaces governed by Pearl_Brand: `brand_admin.html`, `brand_admin_weekly_os.html`, `brand-wizard-app/public/brand_admin.html`, and the `dashboard/` subsystem itself.

### Manga lane table — Open Question (deferred)

The book pipeline's 24×13=312 expansion uses *spiritual archetype × locale lane* semantics. The manga pipeline's lane semantics are **NOT** the same — manga distribution channels (Shonen Jump-style weekly serialization, LINE Manga bi-weekly, Naver/Kakao webtoon, Crunchyroll/Netflix licensing) align differently than the book locale matrix. The lane table generator (`scripts/manga/derive_manga_lane_table.py`) is deferred until Pearl_Brand has finalized:

1. Manga lane primitives (genre × demographic × distribution-channel? or genre × demographic × locale?)
2. Whether teacher-brand mapping (currently in `config/catalog_planning/teacher_brand_lane_assignments.yaml`) maps cleanly to the 37, or needs its own re-derivation
3. Whether `manga_brand_series_plan.yaml`'s 13 currently-planned brands need expansion to all 37 or whether 13 is a deliberate Phase-1 subset

Sketching this script in <30 lines is not feasible without that decision; deferring per Path X scope discipline.

## Authority

This package was created under lane `brand_admin_and_investor_enhancement` from `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md` section 4.

Path X separation ratified by operator 2026-04-27. See `docs/PEARL_ARCHITECT_STATE.md` BR-CANON-01 Path X cap entry for the architecture decision; see `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` for the manga reconciliation governance.
