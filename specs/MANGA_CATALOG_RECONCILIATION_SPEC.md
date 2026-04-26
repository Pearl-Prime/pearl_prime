# Manga Catalog Reconciliation Spec

**Version:** 1.0.0
**Authority:** Pearl_Architect (synthesis) — supersedes the operational layer of `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (Apr 7–12) and aligns the planner / schema / taxonomy / config / generated YAMLs with the strategic refresh in `docs/GENRE_PORTFOLIO_PLAN.md` (Apr 23).
**Date:** 2026-04-26
**Status:** Draft awaiting operator approval before any execution PR opens.
**Inputs:** [docs/MANGA_PIPELINE_AUDIT_2026-04-26.md](../docs/MANGA_PIPELINE_AUDIT_2026-04-26.md) (Phase 1 audit findings); [docs/GENRE_PORTFOLIO_PLAN.md](../docs/GENRE_PORTFOLIO_PLAN.md) (strategic refresh, PR #583); [docs/CJK_CATALOG_PLAN.md](../docs/CJK_CATALOG_PLAN.md) + [docs/US_CATALOG_PLAN.md](../docs/US_CATALOG_PLAN.md) (per-locale strategic plans); [docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md](../docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md) (research feeder).
**Out-of-scope inputs:** `docs/LOCALE_CATALOG_MARKETING_PLAN.md` and `docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md` are **audiobook** plans, not manga. Not touched by this spec.

---

## §1 — Why this spec exists

The Phase 1 audit ([MANGA_PIPELINE_AUDIT_2026-04-26](../docs/MANGA_PIPELINE_AUDIT_2026-04-26.md)) framed the manga catalog as "Apr 7–12 plan, slightly stale, generators ready, ship-or-build decision." Subsequent inspection surfaced three load-bearing strategic plans the audit's docs subagent missed (its grep was bound to `docs/MANGA_*.md` and didn't catch `*CATALOG*` / `*PORTFOLIO*` / `*GENRE*`):

1. **`docs/GENRE_PORTFOLIO_PLAN.md`** (2026-04-23, PR #583) — establishes the **Genre Shell Revenue Gap thesis**: explicit wellness manga ceilings at ~3M copies (Oyasumi Punpun); genre-embedded wellness reaches 7M–70M (Vinland Saga → Berserk); Evangelion (depression as mecha) is a $16B franchise. The strategic conclusion: every brand publishes across multiple genres; wellness content is interior architecture, never the facade. Defines **12 genre shells × 37 brands** with explicit %-by-genre allocations per brand.
2. **`docs/CJK_CATALOG_PLAN.md`** (2026-04-22) — explicitly states the Apr 7–12 catalog plan was **wrong**: "*The initial JP series plan (sections 4–5) was drafted as explicit healing/therapy manga only. This was wrong. Sections 4–5 are now updated to reflect the correct genre mix per `docs/GENRE_PORTFOLIO_PLAN.md`.*"
3. **`docs/US_CATALOG_PLAN.md`** (2026-04-23) — US-specific embedded-wellness plan with format strategy (manga-aisle vs. mainstream-self-help-shelf).

The execution layer — `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (Apr 7–12), the generator's `VALID_GENRES` (Apr 19), the schema enum (Apr 19), the 132 generated `series_plan.yaml`s (Apr 25), the 716 generated `book_plan.yaml`s — was authored or last-touched **before the Apr 23 strategic refresh**. It reflects the pre-correction "explicit healing only" version that the strategic plan explicitly says was wrong.

This spec is the canonical reconciliation: which artifacts are stale, what replaces them, what new genres / brands / craft bibles open, and in what order the work lands.

---

## §2 — The strategic-vs-operational mismatch

### §2.1 — Authority dates

| Layer | File(s) | Date | Authority status |
|---|---|---|---|
| Strategic core | `docs/GENRE_PORTFOLIO_PLAN.md` | **2026-04-23** | **CANONICAL** — supersedes operational catalog |
| Per-locale strategic | `docs/CJK_CATALOG_PLAN.md`, `docs/US_CATALOG_PLAN.md` | 2026-04-22 / 2026-04-23 | CANONICAL — per-locale view of the strategic core |
| Strategic research feeder | `docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md` | 2026-04-10 | KEEP — industry benchmarks (37 brands, 2–5 active series/brand, 14,723 KR titles/year) |
| Operational catalog | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | 2026-04-07 (last touch 2026-04-12) | **STALE — explicitly superseded** by GENRE_PORTFOLIO_PLAN.md per CJK_CATALOG_PLAN.md self-reference |
| Planner allow-list | `scripts/manga/generate_series_plans_from_catalog.py:45–49` | 2026-04-25 (PR #643) | STALE — knows 4–5 of 12 strategic shells |
| Schema enum | `schemas/manga/series_plan.schema.json` | 2026-04-19 | STALE — same 10 strings as planner |
| Taxonomy | `config/manga/manga_taxonomy.yaml` (`last_updated: 2026-04-19`) | 2026-04-19 | PARTIAL — has broader 30+ entries but missing mecha + the explicit shell-as-revenue-tier framing |
| Format routing | `config/manga/format_routing.yaml` | last touched per allow-list | STALE — keyed by current 10 genres |
| Pacing | `config/manga/manga_pacing_by_genre.yaml` | various | STALE — same |
| Generated series_plans | `config/source_of_truth/manga_series_plans/` (132 YAMLs) | 2026-04-25 (PR #643) | **STALE — generated from the stale operational catalog** |
| Generated book_plans | `config/source_of_truth/manga_book_plans/` (716 YAMLs) | 2026-04-25 (PR #646) | **STALE — same** |
| Production artifact | `artifacts/manga/ep_001/` (38 PNG pages, ep_001 of `the_alarm_is_lying`) | 2026-04-26 | KEEP — actual rendered episode; iyashikei lane; valid in any reconciled plan |

### §2.2 — The 12 strategic genre shells vs. the planner's 10 allow-list

| # | Strategic Genre Shell | Revenue tier | Planner allow-list mapping | Status |
|---|---|---|---|---|
| 1 | Iyashikei / Slice-of-Life | Anchor | `iyashikei` | ✅ aligned |
| 2 | **Dark Fantasy** | **Mega** (Berserk 70M, Frieren 30–32M) | — | ❌ missing |
| 3 | Psychological Horror | Large-growing (CAGR 18.74%) | `horror` (partial — combines horror sub-types) | ⚠️ collapse |
| 4 | Supernatural Mystery | Large | — | ❌ missing |
| 5 | Isekai | Mega (digital) | `isekai` | ✅ aligned |
| 6 | Sci-Fi / Cyberpunk | Mid | — | ❌ missing |
| 7 | Psychological Thriller | Mid | — | ❌ missing |
| 8 | Romance / Josei Drama | Large | `shojo`, `webtoon_romance`, `josei_essay_manga` (3 narrow buckets) | ⚠️ fragmented |
| 9 | Workplace Drama / Comedy | Mid | — | ❌ missing |
| 10 | Action / Battle | Large | `shonen` (partial — action≠shonen) | ⚠️ conflated |
| 11 | Sports / Competition | Large | — | ❌ missing |
| 12 | Historical / Period Drama | Mid (Vinland Saga 7M) | — | ❌ missing |
| Bonus A | Cultivation / Martial Arts | (regional anchor) | `cultivation` | ✅ aligned |
| Bonus B | School / Coming-of-Age | (sub-genre) | — | ❌ missing |
| Mega-example | **Mecha** (Evangelion $16B) | (treated as exemplar of "genre shell as revenue multiplier"; not in the 12) | — | OPEN — see §10 OQ-1 |

**Net:** 4 of 12 strategic shells fully aligned; 4 partial/fragmented; 5 missing entirely. Plus 1 bonus aligned, 1 bonus missing, and the mecha question open.

The planner's `manhwa` is regional, not a genre — should be removed and replaced with `genre + locale_origin: kr` modeling.

### §2.3 — Brand-vs-teacher modeling mismatch

| Layer | Abstraction | Count | Authority |
|---|---|---|---|
| Strategic core (`GENRE_PORTFOLIO_PLAN.md`) | **Brands** | **37** (3 flagship + 14 core + 20 niche) | Canonical for catalog allocation |
| Operational catalog (`MANGA_FULL_CATALOG_PLAN.md`) | **Teachers** | 12 | Stale; the only one with executed series plans |
| Generated series_plan YAMLs | **Brand × teacher pair** (e.g., `stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying`) | 132 series total | Generated from teacher-anchored plan |
| Production artifact (ep_001) | `stillness_press` brand × `ahjan` teacher | 1 | KEEP |

These are different abstractions. The flagship brand `stillness_press` (Anxiety · Somatic · Sleep · Josei) is paired with **one** teacher (ahjan) in the generated YAMLs, but the strategic plan treats `stillness_press` as a brand that publishes 16 series across 5 genres (iyashikei 30%, dark_fantasy 25%, psych_horror 20%, supernatural_mystery 15%, isekai 10%) — independent of teacher.

**Reconciliation rule:** brand is the catalog allocation unit; teacher is a content provenance/voice attribute. A given series belongs to **one brand** and **one or zero teachers**. Some brands (`stoic_edge`, `legacy_builder`, `bio_flow`, `longevity_lab`) may not be teacher-anchored at all in the strategic plan.

### §2.4 — Per-locale format mismatch

| Locale | Strategic plan format | Operational catalog format | Mismatch |
|---|---|---|---|
| en_US | Two paths (manga-aisle B&W digest OR mainstream cartoon/doodle) | Format-agnostic per teacher | Strategic adds the path-A/path-B fork |
| ja_JP | B&W tankobon OR webtoon dual-format | Format-agnostic | Strategic adds dual-format strategy |
| zh_TW | Hybrid (manga-page + atmospheric rendering, BD influence) | Format-agnostic | Strategic adds hybrid-render guidance |
| zh_CN | Vertical-scroll tiáomàn (条漫), Korean-influenced | BLOCKED for distribution | Strategic adds rendering-but-not-distributing posture (per audit §8 OQ-4) |
| ko_KR | Vertical-scroll webtoon | Not in operational scope | Strategic adds 5th locale (per audit §8 OQ-1) |

---

## §3 — Canonical decisions

The following rulings are made by this spec. They become governance-binding on merge.

| # | Decision | Rationale |
|---|---|---|
| D-1 | **`docs/GENRE_PORTFOLIO_PLAN.md` is the canonical strategic catalog plan.** | Authored Apr 23; explicit supersession of pre-correction operational catalog. |
| D-2 | **`docs/CJK_CATALOG_PLAN.md` and `docs/US_CATALOG_PLAN.md` are canonical per-locale views.** | Same authoring date; per-locale specialization of D-1. |
| D-3 | **`artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` is RETIRED.** | Explicitly superseded; cannot remain authoritative. Replacement in §7.1. |
| D-4 | **The 132 `series_plan.yaml`s are RETIRED.** | Generated from the retired plan. Re-generation in §7.6. |
| D-5 | **The 716 `book_plan.yaml`s are RETIRED.** | Generated from the retired series plans. Re-generation in §7.7. |
| D-6 | **Brand is the catalog allocation unit.** | Per §2.3. Series belong to brands; teacher is an attribute. |
| D-7 | **Genre is the strategic shell, not the marketing-gift-card label.** | Per §2.2. Each series has exactly one `genre` (one of the 12 shells). The `topic` field carries the wellness substrate, never the genre label. |
| D-8 | **Genre allow-list expands from 10 to 12 strategic shells (plus bonuses), with the planner-internal label normalized.** | See §4. `manhwa` is removed (regional, not genre); `josei_essay_manga` is consolidated into Romance/Josei Drama; new shells added. |
| D-9 | **Mecha is its own genre shell** (independent of the strategic 12), reflecting the Evangelion $16B exemplar's revenue magnitude. | Per audit §8 OQ-5 + the strategic core's repeated mecha-as-revenue-anchor citations. |
| D-10 | **Historical / Period Drama is its own genre shell.** Viking is a setting flavor inside it. | Per §2.2 + `manga_cover_design/09:318` (Vinland Saga as "Historical epic / Viking-era action-drama"). |
| D-11 | **The 37-brand × 12+ shell strategic structure replaces the 12-teacher × 10-genre operational structure** as the source for generators. | Per D-1 through D-7. |
| D-12 | **`MANGA_MODE_SYSTEM_SPEC.md` is RETIRED — moved to `specs/archive/`.** | Per audit §4 + §8 OQ-10. Mode enforcement is distributed across agents; this spec adds no live function. |
| D-13 | **`MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` is REFRAMED — kept and updated to align with the 37-brand × 12-shell anti-homogeneity model.** | Catalog homogeneity is a real risk at 132+ series; the GENRE_PORTFOLIO_PLAN's per-brand %-allocation IS the anti-spam mechanism. The spec should be updated, not retired. Reframing in §7.10. |
| D-14 | **`MANGA_AUTHOR_SYSTEM_SPEC.md` is ARCHIVED — moved to `specs/archive/` with a `DEFERRED_2026_04_26.md` index file.** | Per audit §4 + §8 OQ-10. Not core to current pipeline. Operator can revive when multi-author UI becomes priority. |
| D-15 | **PR #678 (`fix(manga): lettering_from_script v3-schema awareness`) is the immediate gating merge** before this spec's Phase 2 work can ramp. | Per audit §5.5. ep_002 and the entire CJK6 lettering pipeline depend on it. |
| D-16 | **Coordination layer is at `artifacts/coordination/`, NOT bare `coordination/`. Spec execution updates the layer in place.** | Per audit §8 OQ-2 corrected + OQ-8 disposition (iii) executed 2026-04-26. The audit's original claim that `coordination/` did not exist was a path-mismatch error — the actual directory is `artifacts/coordination/` (referenced by `pr_governance_review.py:43,68`). Workstream rows for every Phase 2X.* PR are added to `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; project state lives in `artifacts/coordination/ACTIVE_PROJECTS.tsv` under `proj_manga_catalog_reconciliation_20260426`. |
| D-17 | **`MANGA_FULL_CATALOG_PLAN.md` is replaced by an auto-derived artifact** generated from `GENRE_PORTFOLIO_PLAN.md` + `CJK_CATALOG_PLAN.md` + `US_CATALOG_PLAN.md`. | The catalog stops being a hand-edited Markdown table and becomes the deterministic projection of the strategic docs. Per §7.1. |

---

## §4 — Genre taxonomy reconciliation

### §4.1 — New canonical genre allow-list (post-reconciliation)

```yaml
# Strategic shells (12) + cultivation/martial arts (regional) + mecha + school
VALID_GENRES = (
    # Strategic 12
    "iyashikei",              # Slice-of-life / healing — anchor
    "dark_fantasy",           # NEW — Berserk/Frieren register; trauma + grief shell
    "psychological_horror",   # RENAMED from "horror" — narrower; Mob Psycho register
    "supernatural_mystery",   # NEW — spirit/medium genre; Mushishi/xxxHOLiC register
    "isekai",                 # Self-worth + second-chances; portal fantasy
    "sci_fi_cyberpunk",       # NEW — burnout-as-machine-body; tech-anxiety register
    "psychological_thriller", # NEW — overthinking-as-paranoia; unreliable narrator
    "romance_josei_drama",    # CONSOLIDATED — supersedes shojo + webtoon_romance + josei_essay_manga
    "workplace_drama",        # NEW — Aggretsuko register; burnout/imposter
    "action_battle",          # RENAMED from "shonen" (which was conflated)
    "sports_competition",     # NEW — ADHD/focus + performance anxiety
    "historical_period",      # NEW — includes Viking/Edo/Tang/Roman setting flavors
    # Bonus shells
    "cultivation_martial",    # RENAMED from "cultivation" — explicit Eastern register
    "school_coming_of_age",   # NEW — formative-anxiety + identity register
    "mecha",                  # NEW — Evangelion-tier revenue exemplar
)
```

**Net change:**
- ✅ `iyashikei`, `isekai` — kept verbatim
- 🔄 `horror` → `psychological_horror` (narrower; supernatural_mystery split out)
- 🔄 `shojo` + `webtoon_romance` + `josei_essay_manga` → `romance_josei_drama` (consolidated)
- 🔄 `shonen` → `action_battle` (action ≠ demographic; demographic is a separate field)
- 🔄 `cultivation` → `cultivation_martial`
- ❌ `manhwa` — REMOVED (regional, not genre; replaced by `locale_origin: kr` attribute)
- ➕ 9 new genres added

### §4.2 — Demographic field (new)

The strategic plan's per-brand persona fits (`Adult women 25–55`, `Tech workers`, `Gen Z digital-native`) require a **demographic** field separate from genre. Add to schema:

```yaml
demographic: enum [
    "kodomo",      # children 5–10
    "shonen",      # boys 8–18
    "shojo",       # girls 12–22
    "seinen",      # adult men
    "josei",       # adult women
    "general",     # cross-demographic
]
```

Demographic and genre are orthogonal: a `dark_fantasy` series can be `seinen` (Berserk) or `shojo` (modern shojo dark fantasy) or `general` (Frieren).

### §4.3 — Locale origin field (new)

Replace the regional `manhwa` genre with a series-level `locale_origin` attribute:

```yaml
locale_origin: enum [ "jp", "kr", "tw", "cn", "us" ]
```

A series rendered as `format: color_vertical_webtoon` with `locale_origin: kr` is a manhwa. A series rendered as `format: bw_page_manga` with `locale_origin: jp` is a manga. Format + origin replaces the conflated `manhwa` genre.

### §4.4 — Per-genre supporting config

Each new genre requires entries in:
- `schemas/manga/series_plan.schema.json` `properties.genre.enum`
- `scripts/manga/generate_series_plans_from_catalog.py:45–49` `VALID_GENRES`
- `config/manga/manga_taxonomy.yaml` `genre_families` (with ITE profile, emotional engines, serialization engines, visual grammars)
- `config/manga/format_routing.yaml` `defaults_by_locale_genre.<locale>.<genre>` (per all 4–5 locales)
- `config/manga/manga_pacing_by_genre.yaml` (pacing metrics per `manga_dialogue_system/02:656` table)
- `config/manga/genre_ite_profiles.yaml` (ITE profile reference per `MANGA_GENRE_AGENT_SPEC.md`)
- `docs/research/manga_craft/<genre>.md` (craft bible synthesizing existing dialogue + cover research; pattern: see `docs/research/manga_craft/iyashikei_minimalism.md`)

---

## §5 — Brand-vs-teacher modeling reconciliation

### §5.1 — Canonical brand list (37 brands per `GENRE_PORTFOLIO_PLAN.md`)

The strategic plan defines:

- **Flagship** (14–18 series each, 3 brands): `stillness_press`, `cognitive_clarity`, `digital_ground`
- **Core** (8–10 series each, 14 brands): `sleep_restoration_iyashikei`, `somatic_wisdom_shojo`, `relational_calm_iyashikei`, `healing_ground_healing`, `body_memory_shojo`, `minimal_mind_healing`, `night_reset_healing`, `gentle_growth_healing`, `stabilizer_healing`, `career_lift_workplace`, `high_performer_workplace`, `executive_calm_workplace`, `morning_momentum_workplace`, `optimizer_workplace`, `focus_sprint_workplace`, `heart_balance_shojo`
- **Niche** (4–6 series each, 13+ brands): `trauma_path_healing`, `resilient_parent_social`, `confidence_core_romance`, `relationship_clarity_romance`, `adhd_forge_mystery`, `devotion_path_shonen`, `stoic_edge_battle`, `warrior_calm_cultivation`, `spiritual_ground_supernatural`, `solar_return_isekai`, `legacy_builder_memoir`, `bio_flow_healing`, `longevity_lab_healing`

**Total target series count (strategic):** 3×16 + 14×9 + 13×5 = 48 + 126 + 65 = **~239 series** (one snapshot midpoint).
For 4 locales: ~239 × 4 = **~956 localized series.**
For 14 chapters/series: ~956 × 14 = **~13,384 chapters.**

### §5.2 — Teacher-as-attribute, not as catalog axis

Teachers (ahjan, joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma) become a **provenance attribute** on series and brands:

```yaml
# series_plan.yaml (post-reconciliation)
brand_id: stillness_press
teacher_id: ahjan          # OR null if not teacher-anchored
locale: en_US
genre: iyashikei
demographic: josei
locale_origin: jp           # rendered in JP register even for en_US distribution
topic: anxiety
manga_author: hana_tidecalm
series_slug: the_alarm_is_lying
chapters_target: 14
```

Brands `stoic_edge`, `legacy_builder`, `bio_flow`, `longevity_lab` may have `teacher_id: null` if the strategic plan does not anchor them to a teacher.

### §5.3 — Catalog plan shape

The new generated `MANGA_FULL_CATALOG_PLAN.md` (or its replacement; see §7.1) is a deterministic projection from:
- `docs/GENRE_PORTFOLIO_PLAN.md` (brand × genre allocation)
- `docs/CJK_CATALOG_PLAN.md` + `docs/US_CATALOG_PLAN.md` (per-locale specialization)
- `config/source_of_truth/manga_profiles/` (existing 365 profiles for character-author + teaching cores)
- `docs/research/manga_craft/<genre>.md` (per-genre craft bibles, including the 9 new ones added per §4)

**The catalog plan stops being hand-edited Markdown.** It becomes a generator output.

---

## §6 — Deletion plan

Per CLAUDE.md governance: any single PR deleting >50 files needs explicit owner approval. The 132 + 716 = 848 generated YAMLs cross that threshold by 17×. Operator approval of *this spec* is the explicit owner approval; **but the deletions still segment into batches** to keep each PR reviewable and reversible.

### §6.1 — Deletion segments

| Segment | Files | Count | PR title |
|---|---|---|---|
| **6.1.A — Stale operational catalog plan** | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | 1 | `chore(manga): retire stale operational catalog plan (Apr 7-12) per reconciliation spec` |
| **6.1.B — Retire 3 zero-ref specs** | `specs/MANGA_MODE_SYSTEM_SPEC.md`, `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` *(MOVE not delete; reframed in §7.10)*, `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` | 2 deletes + 1 move | `chore(manga): archive 2 zero-ref specs + reframe BRAND_DNA spec` |
| **6.1.C — 132 stale series_plan YAMLs** | `config/source_of_truth/manga_series_plans/*.yaml` (excluding `_samples/`) | 132 | `chore(manga): retire 132 stale series_plan YAMLs (regenerate per reconciliation spec)` — owner-approved per this spec |
| **6.1.D — 716 stale book_plan YAMLs** | `config/source_of_truth/manga_book_plans/<dir>/*.yaml` | 716 | `chore(manga): retire 716 stale book_plan YAMLs (regenerate per reconciliation spec)` — owner-approved per this spec |
| **6.1.E — Truly orphan code (post-migration only)** | per audit Phase 2A; only after callers are migrated | 2–4 | `chore(manga): prune migrated-orphan scripts (audit Phase 2A — final)` |

**Total deletions across all segments: ~853 files.** All driven by the catalog reconciliation; none ad hoc.

### §6.2 — Files NOT deleted (defended explicitly)

The Phase 2A verification revealed these earlier-flagged candidates as load-bearing. They remain.

| File | Why preserved |
|---|---|
| `phoenix_v4/manga/sdf/stub.py` | `chapter_runner.py:124` imports `attach_sdf_stub_conditioning`; `sdf/__init__.py` re-exports; `tests/test_manga_runner_revision_features.py` uses it. |
| `scripts/manga/run_chapter_production.py` | Registered in `config/pipeline_registry.yaml:42` as `entry_script`; `tests/test_manga_chapter_production_integration.py` exercises it. |
| `scripts/manga/run_chapter_visual.py` | `tests/test_manga_chapter_visual.py` exercises it; documented in `MANGA_PIPELINE_ONBOARDING.md`. |
| `scripts/manga/run_series_setup.py` | `tests/test_manga_series_setup.py`; documented in onboarding. |
| `scripts/manga/manga_character_sheet_stub.py` | `.github/workflows/manga-character-sheet-build.yml:61` invokes it. |
| `scripts/manga/manga_series_pitch.py` | `.github/workflows/manga-series-pitch.yml:38` invokes it. |
| `scripts/manga/run_asset_resolver.py` (manga) | Documented in onboarding; safer to leave until onboarding is updated. |
| `scripts/manga/run_prompt_compiler.py` | Documented in onboarding; safer to leave until onboarding is updated. |
| `phoenix_v4/manga/chapter/visual_from_script.py` (v2) | `lettering_from_script.py` imports it for v2 compat. Re-evaluate after PR #678. |
| `docs/MANGA_MODE_STRATEGY.docx` | Binary; out of scope until §10 OQ-7 (docx → md migration) is decided. |
| `docs/LOCALE_CATALOG_MARKETING_PLAN.md` | **Audiobook plan, not manga.** Out of scope. |
| `docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md` | **Audiobook plan, not manga.** Out of scope. |
| `docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md` | Research feeder for the strategic plan; current. |
| `docs/MANGA_FONT_REGISTRY.md`, `docs/MANGA_CJK_SHAPING.md`, `docs/MANGA_GTM_PLAN.md`, `docs/MANGA_PIPELINE_ONBOARDING.md`, `docs/MANGA_PIPELINE_COMPLETE_GUIDE.md`, `docs/MANGA_IMPLEMENTATION_OUTLINE.md`, `docs/MANGA_CATALOG_VOLUME_AND_ASSETS_HANDOFF_2026_04_17.md` | All KEEP per audit §2.2. |
| All Cohort 1 and Cohort 2 specs not listed above | Per audit §2.3 — most are LIVE or PARTIAL; reframing happens in §7, not deletion. |
| Production artifacts (`artifacts/manga/ep_001/`, `ep_001_strips_en_US/`, `chapter_scripts/`, `panel_prompts/`) | KEEP — actual rendered episode and authored ep_002. The reconciliation does not invalidate the iyashikei lane that ep_001 lives in. |

---

## §7 — Creation / update plan

### §7.1 — Replace the operational catalog plan

**Before:** `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` is hand-edited. Stale.
**After:** `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` is a generator output. Re-runnable.

New script: `scripts/manga/generate_catalog_plan_from_strategic.py`
- Input: `docs/GENRE_PORTFOLIO_PLAN.md` + `docs/CJK_CATALOG_PLAN.md` + `docs/US_CATALOG_PLAN.md` + `config/source_of_truth/manga_profiles/`
- Output: `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (regenerated each run; deterministic)
- CI gate: regeneration on edits to any input doc; PR fails if catalog plan is stale relative to inputs

### §7.2 — Expand `VALID_GENRES` (planner)

Edit `scripts/manga/generate_series_plans_from_catalog.py:45–49` to the new 15-entry tuple per §4.1.

### §7.3 — Expand `genre.enum` (schema)

Edit `schemas/manga/series_plan.schema.json` `properties.genre.enum` to match §4.1.

### §7.4 — Add `demographic` and `locale_origin` fields

Edit `schemas/manga/series_plan.schema.json` to add:
- `demographic: { type: string, enum: ["kodomo", "shonen", "shojo", "seinen", "josei", "general"] }`
- `locale_origin: { type: string, enum: ["jp", "kr", "tw", "cn", "us"] }`

Edit `phoenix_v4/manga/models/validation.py` to validate these fields.

### §7.5 — Expand taxonomy + routing + pacing config

Per §4.4:
- `config/manga/manga_taxonomy.yaml` — add `genre_families` entries for the 9 new genres + reframe `psychological_horror` / `romance_josei_drama` / `action_battle` (split from existing entries). Remove the implicit `manhwa` row.
- `config/manga/format_routing.yaml` — add `defaults_by_locale_genre.<locale>.<genre>` entries for all (4-5 locales) × (15 genres). Use the strategic per-locale format mix per §2.4.
- `config/manga/manga_pacing_by_genre.yaml` — add pacing rows per `manga_dialogue_system/02:656` table.
- `config/manga/genre_ite_profiles.yaml` — add ITE profile entries per genre.

### §7.6 — Re-generate 132 → ~239 (or per-locale ~956) series_plan YAMLs

After §6.1.C deletes the 132 stale, run `generate_series_plans_from_catalog.py` against the regenerated `MANGA_FULL_CATALOG_PLAN.md` from §7.1. Outputs the new strategic-aligned series_plan YAMLs.

**Naming convention update** (per §5.2):
- Old: `{brand}__{teacher}__{locale}__{topic}__{series_slug}.yaml`
- New: `{brand}__{locale}__{genre}__{topic}__{series_slug}.yaml` (teacher captured inside the YAML's `teacher_id` field, may be null)

### §7.7 — Re-generate 716 → corresponding book_plan YAMLs

Run `generate_book_plans_from_series.py` against the new series_plan set. Outputs the new book_plan YAMLs.

### §7.8 — Add 9 new craft bibles (per §4.4)

`docs/research/manga_craft/` currently has 10 lanes (BL, graphic_novel, iyashikei, josei, kodomomuke, seinen_psychological, shojo_romance, shonen_encouragement, webtoon_vertical_drama, webtoon_vertical_romance + index). Add:

| New craft bible | Source research |
|---|---|
| `dark_fantasy.md` | `manga_dialogue_system/02:dark_fantasy_section`, `manga_cover_design/01:dark_fantasy`, `manga_genre_writing_styles_2026_04_04.md` (Berserk/Vinland Saga refs) |
| `psychological_thriller.md` | `manga_dialogue_system/02:psychological_thriller_section`, `manga_cover_design/01:thriller_section` |
| `supernatural_mystery.md` | Research synthesis from existing `horror` + `mystery` cover sections |
| `sci_fi_cyberpunk.md` | `manga_cover_design/04:184` (pixel-art-derived fonts), Evangelion design refs in `cover_design/09` |
| `workplace_drama.md` | `manga_dialogue_system/02:workplace_register`, Aggretsuko refs in `bestseller_pattern_decomposition` |
| `action_battle.md` | `manga_genre_writing_styles_2026_04_04.md` shōnen section + `MANGA_GENRE_AGENT_SPEC.md` |
| `sports_competition.md` | Research synthesis (Coach Ukai Haikyuu refs in `genre_writing_styles:240`) |
| `historical_period.md` | `manga_cover_design/09:Vinland_Saga_section`, `04:1789` (Mecha typography also serves historical) |
| `mecha.md` | `manga_dialogue_system/01:561` (Section 11 Mecha), `manga_dialogue_system/02:238` + `:656` (mecha pacing), `manga_cover_design/01:1643` (Section 11 Mecha cover), `04:1789` (mecha typography) |

Each craft bible follows the iyashikei + shōjo template: market contract, visual rules, pacing, dialogue, character, failure modes, 48-vol shape, panel scaffolding (6–9 fields), locale weighting.

### §7.9 — Update `docs/research/manga_craft/index.md`

Add the 9 new lanes.

### §7.10 — Reframe `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md`

Update — do not retire — to align with the 37-brand × 12-shell anti-homogeneity model. The strategic plan's per-brand %-by-genre allocation IS the anti-spam mechanism. The spec should:
- Reference `GENRE_PORTFOLIO_PLAN.md` brand-portfolio %s as the canonical brand-DNA fingerprint
- Update the anti-spam scoring rubric to operate on per-brand genre-mix divergence and per-genre style/topic divergence across the catalog
- Add per-locale variance check (a brand's en_US portfolio should differ in tone from its zh_CN portfolio per the locale guidance in §2.4)
- Implementation deferred to §7 audit Phase 2 (post-reconciliation; not part of this spec's first PR)

### §7.11 — Update `docs/MANGA_PIPELINE_ONBOARDING.md`

Reflect:
- The new genre allow-list (§4.1)
- The new `demographic` + `locale_origin` fields (§7.4)
- The brand-vs-teacher reconciliation (§5)
- The new craft bibles (§7.8)
- That `MANGA_FULL_CATALOG_PLAN.md` is auto-generated, not hand-edited

### §7.12 — Update `docs/DOCS_INDEX.md`

Add the canonical-anchor tags:
- `docs/GENRE_PORTFOLIO_PLAN.md` — CANONICAL strategic
- `docs/CJK_CATALOG_PLAN.md` — CANONICAL per-locale
- `docs/US_CATALOG_PLAN.md` — CANONICAL per-locale
- `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` (this spec) — CANONICAL governance
- Mark `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` as "auto-generated; do not hand-edit"

---

## §8 — Migration sequence (PR-by-PR)

The work is sequenced to be reversible at each step. Each PR has a single responsibility.

### Phase 2X.0 — Spec lands (this PR)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.0** | Pearl_Architect | This spec lands. No code/config changes. | 1 file: `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` |

### Phase 2X.1 — Schema + planner expansion (no deletions yet)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.1** | Pearl_Dev | Open the genre allow-list + schema enum + add `demographic` and `locale_origin` fields. Backwards-compatible: old genre slugs still validate (transitional). | `scripts/manga/generate_series_plans_from_catalog.py`, `schemas/manga/series_plan.schema.json`, `phoenix_v4/manga/models/validation.py`, `tests/test_manga_schemas.py` |

### Phase 2X.2 — Taxonomy + routing + pacing expansion

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.2** | Pearl_Dev | Update `manga_taxonomy.yaml`, `format_routing.yaml`, `manga_pacing_by_genre.yaml`, `genre_ite_profiles.yaml` for the 15-genre allow-list. | 4 config files |

### Phase 2X.3 — Add 9 new craft bibles

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.3** | Pearl_Research | Synthesize the 9 new craft bibles from existing research (per §7.8 source map). Update `manga_craft/index.md`. | 10 files in `docs/research/manga_craft/` |

### Phase 2X.4 — Build the new catalog plan generator

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.4** | Pearl_Dev | Add `scripts/manga/generate_catalog_plan_from_strategic.py` per §7.1. CI gate to enforce regeneration. | 1 new script + 1 GHA workflow + tests |

### Phase 2X.5 — Retire stale operational catalog (single-file delete)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.5** | Pearl_GitHub | Run the new generator. Output replaces `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (effectively a one-step delete + recreate as auto-generated). | 1 file replaced |

### Phase 2X.6 — Retire stale series_plans (132 deletes + regenerate)

| PR | Owner | Scope | Files | Owner-approval |
|---|---|---|---|---|
| **2X.6** | Pearl_GitHub | `git rm` the 132 stale `series_plan.yaml`s. Re-run `generate_series_plans_from_catalog.py` against the new catalog plan. Commit the new YAMLs. | 132 deletions + ~239 (or ~956 if per-locale) creations | **Operator approval = approval of this spec.** The PR must reference `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` §6.1.C in its body. |

### Phase 2X.7 — Retire stale book_plans (716 deletes + regenerate)

| PR | Owner | Scope | Files | Owner-approval |
|---|---|---|---|---|
| **2X.7** | Pearl_GitHub | `git rm` the 716 stale `book_plan.yaml`s. Re-run `generate_book_plans_from_series.py`. Commit the new YAMLs. | 716 deletions + N creations | **Operator approval = approval of this spec.** PR must reference `§6.1.D`. |

### Phase 2X.8 — Archive 2 zero-ref specs + reframe BRAND_DNA

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.8** | Pearl_Architect | Move `MANGA_MODE_SYSTEM_SPEC.md` and `MANGA_AUTHOR_SYSTEM_SPEC.md` to `specs/archive/` with a `DEFERRED_2026_04_26.md` index file. Update `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` per §7.10 (reframing — kept). | 2 moves + 1 update + 1 new index file |

### Phase 2X.9 — Update onboarding + docs index

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.9** | Pearl_Architect | Update `MANGA_PIPELINE_ONBOARDING.md` and `DOCS_INDEX.md` per §7.11 + §7.12. | 2 doc files |

### Sequence summary

```
PR 2X.0 — spec lands (this PR)
   ↓
PR 2X.1 — schema/planner opens new genres (backwards-compat)
   ↓
PR 2X.2 — config (taxonomy/routing/pacing) supports new genres
   ↓
PR 2X.3 — craft bibles added (research → source-of-truth for prompt compilation)
   ↓
PR 2X.4 — new catalog plan generator built
   ↓
PR 2X.5 — operational catalog plan replaced (1-file)
   ↓
PR 2X.6 — series_plans retired + regenerated (132 → new count)
   ↓
PR 2X.7 — book_plans retired + regenerated (716 → new count)
   ↓
PR 2X.8 — specs archived + BRAND_DNA reframed
   ↓
PR 2X.9 — onboarding + docs index updated
```

**Total:** 10 PRs over Phase 2X. Estimated ~40–80 hours engineering, distributed.

**Critical constraint:** PR 2X.1 must be backwards-compatible (old genres + new genres both validate) so PR 2X.6 can flip the YAMLs without an intermediate broken state. Once 2X.6 lands, PR 2X.10 (out of this spec's scope, future hardening) can remove the legacy genre slugs from the allow-list.

---

## §9 — Acceptance criteria

The reconciliation is complete when **all** of the following hold on `origin/main`:

| # | Criterion | Verifiable by |
|---|---|---|
| AC-1 | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` is auto-generated; the file header includes `<!-- AUTO-GENERATED — do not hand-edit -->` | `head -3 artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` |
| AC-2 | `scripts/manga/generate_series_plans_from_catalog.py:VALID_GENRES` matches §4.1's 15-entry tuple | `python3 -c "from scripts.manga.generate_series_plans_from_catalog import VALID_GENRES; assert len(VALID_GENRES) == 15"` |
| AC-3 | `schemas/manga/series_plan.schema.json` `properties.genre.enum` matches §4.1 + has `demographic` + `locale_origin` | `python3 -c "import json; s=json.load(open('schemas/manga/series_plan.schema.json')); assert len(s['properties']['genre']['enum']) == 15; assert 'demographic' in s['properties']; assert 'locale_origin' in s['properties']"` |
| AC-4 | `config/manga/manga_taxonomy.yaml` has `genre_families` entries for all 15 genres | grep |
| AC-5 | `config/manga/format_routing.yaml` has `defaults_by_locale_genre.<locale>.<genre>` for all 4 locales × 15 genres = 60 entries | grep + count |
| AC-6 | `config/manga/manga_pacing_by_genre.yaml` has pacing for all 15 genres | grep |
| AC-7 | `docs/research/manga_craft/` has 19 craft bibles (10 existing + 9 new) | `ls` count |
| AC-8 | `docs/research/manga_craft/index.md` references all 19 lanes | grep |
| AC-9 | `config/source_of_truth/manga_series_plans/*.yaml` count matches the strategic plan target (no stale 132-from-old-plan) | `find ... | wc -l` matches `generate_catalog_plan_from_strategic.py` output count |
| AC-10 | `config/source_of_truth/manga_book_plans/**/*.yaml` count matches the new series_plan count × ~14 chapters | `find ... | wc -l` |
| AC-11 | `specs/archive/MANGA_MODE_SYSTEM_SPEC.md` exists; `specs/MANGA_MODE_SYSTEM_SPEC.md` does not | `ls` |
| AC-12 | `specs/archive/MANGA_AUTHOR_SYSTEM_SPEC.md` exists; `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` does not | `ls` |
| AC-13 | `specs/archive/DEFERRED_2026_04_26.md` exists with rationale per spec §10 | `ls` |
| AC-14 | `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` references `GENRE_PORTFOLIO_PLAN.md` brand-portfolio %s | grep |
| AC-15 | `docs/MANGA_PIPELINE_ONBOARDING.md` lists all 15 genres + new fields | grep |
| AC-16 | `docs/DOCS_INDEX.md` tags `GENRE_PORTFOLIO_PLAN.md` + `CJK_CATALOG_PLAN.md` + `US_CATALOG_PLAN.md` + this spec as CANONICAL | grep |
| AC-17 | All existing tests continue to pass (no test breakage from the genre/schema expansion) | `pytest tests/ -k manga` |
| AC-18 | `audit_llm_callers` returns 0 violations on every PR in the sequence | CI |
| AC-19 | `pr_governance_review` returns APPROVED on every PR in the sequence | CI |
| AC-20 | The original ep_001 production artifact (`artifacts/manga/ep_001/` 38 PNG pages + 35 webtoon strips) is **untouched** by the reconciliation — its iyashikei lane is preserved end-to-end | `git diff --name-only` excludes `artifacts/manga/ep_001/` |

---

## §10 — Open questions for operator

These decisions are not made by this spec; the operator picks before the relevant PR opens.

### OQ-1 — Mecha as 13th genre or sub-shell?

The 12 strategic genre shells in `GENRE_PORTFOLIO_PLAN.md` cite Evangelion's $16B as the highest-leverage example but do not include mecha as one of the 12. This spec D-9 promotes mecha to its own genre slug. Alternatives:
- (a) Mecha is its own genre. (Spec recommendation; aligns with research depth.)
- (b) Mecha is a sub-genre under sci-fi/cyberpunk (e.g., `sci_fi_cyberpunk` with `style: mecha_cinematic`).
- (c) Mecha is a sub-genre under action_battle.

### OQ-2 — Is `school_coming_of_age` a 14th genre or a sub-shell?

`GENRE_PORTFOLIO_PLAN.md` lists School / Coming-of-Age as a "bonus genre used by specific brands." This spec D-9 promotes it. Alternatives: (a) own genre, (b) demographic (`demographic: shonen` + `style: school_setting`), (c) absorb into romance_josei_drama for romance-school crossovers.

### OQ-3 — How aggressive is the brand-vs-teacher reconciliation?

`GENRE_PORTFOLIO_PLAN.md` defines 37 brands; `MANGA_FULL_CATALOG_PLAN.md` defines 12 teachers. This spec D-6 makes brand the catalog axis and teacher an attribute. Alternatives:
- (a) Drop teacher entirely from series_plan; keep teacher only in `manga_profiles`. (Spec recommendation.)
- (b) Maintain dual-axis modeling with brand as primary, teacher as secondary axis (12 × 37 grid with empty cells where no teacher anchors).
- (c) Reduce brand list; merge brands that are essentially the same teacher × different topic.

### OQ-4 — When to flip the per-genre `demographic` semantics

`shonen` and `josei` are currently genre slugs in the planner; this spec moves them to `demographic`. Alternatives:
- (a) Flip in PR 2X.1 (backwards-compat: old `genre: shonen` validates as `genre: action_battle, demographic: shonen` via translation map). (Spec recommendation.)
- (b) Leave existing slugs as-is; add demographic-as-attribute only for new series. (Creates ongoing dual-modeling burden.)

### OQ-5 — ko_KR as 5th locale?

Per audit §8 OQ-1. The strategic CJK_CATALOG_PLAN explicitly maps KR. This spec defers — assumes 4 locales — but the moment ko_KR is added, the per-locale × 15-genre routing matrix grows from 60 to 75 entries. Operator picks now or in Phase 2X.2.

### OQ-6 — zh_CN distribution stance

Per audit §8 OQ-4. Plans render but distribution is BLOCKED. Spec recommendation: render zh_CN series, hold in `artifacts/manga/` until partnership lands, do not attempt upload. Confirm.

### OQ-7 — `docs/MANGA_MODE_STRATEGY.docx` migration

Per audit §8 OQ-11. Binary docx; not auditable. Recommendation: migrate to Markdown in Phase 2X.9, then potentially prune as redundant with `MANGA_MODE_SYSTEM_SPEC.md` (which §6.1.B archives). Confirm.

### OQ-8 — Coordination layer — RESOLVED 2026-04-26

**Original framing (incorrect):** Per audit §8 OQ-2, `coordination/` does not exist; spec D-16 left it out of scope.

**Correction (2026-04-26 disposition iii):** The coordination layer **exists at `artifacts/coordination/`**, not the bare `coordination/` path. The audit's docs-subagent search was bound to the wrong path. Resolution executed in the same PR that records this correction:
- `proj_manga_catalog_reconciliation_20260426` added to `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- 4 completed workstream rows backfilled in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for PRs #680/#682/#684 and the coordination-sync PR itself
- 7 proposed workstream rows pre-staged for Phase 2X.1..2X.9 (OQ-4 hard-cutover collapses 2X.1+2X.6+2X.7 into one atomic PR; 2X.6 and 2X.7 do not appear as separate workstreams)
- D-16 amended in §3 (this spec)
- Stale `coordination/` references in this spec and in `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` corrected in place

### OQ-9 — Audiobook-named docs that landed in `docs/`

`docs/LOCALE_CATALOG_MARKETING_PLAN.md` (117 KB, audiobook) and `docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md` (audiobook) sit in `docs/` adjacent to manga docs. They are out of scope for this spec but the naming collision is confusing. Operator may want a separate hygiene PR to rename or move them under `docs/audiobook/`. Not done here.

---

## §11 — Out of scope

This spec does not:

- ~~Modify `coordination/` (does not exist; D-16).~~ **AMENDED 2026-04-26:** The coordination layer at `artifacts/coordination/` is updated by this spec's execution per OQ-8 disposition (iii). See D-16 (amended) and §10 OQ-8 (resolved).
- Add a live LLM writer in `chapter_runner` (per audit §7.9 OQ-9 — Tier-1 policy decision).
- Implement the QC gate runner (audit §7.2; separate sprint).
- Implement MQG-01, MQG-03..08 (audit §7.3; separate sprint).
- Implement MDLG-01..05 dialogue gates (audit §7.4; separate sprint).
- Implement the cover pipeline (audit §7.5; deferred per OQ-8).
- Touch any audiobook artifact (`docs/LOCALE_CATALOG_MARKETING_PLAN.md`, `docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md`, `phoenix_v4/audiobook/`, `scripts/audiobook/`).
- Touch any video artifact (`phoenix_v4/video/`, `scripts/video/`).
- Touch the existing ep_001 production artifact in `artifacts/manga/ep_001/`.
- Merge PR #678 (gating but separate; tracked in audit §5.5).
- ~~Open new workstreams in `coordination/workstreams.tsv` (the coordination layer is out of scope).~~ **AMENDED 2026-04-26:** Workstreams are tracked in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; this spec's execution backfills completed workstreams (PRs #680/#682/#684) and pre-stages Phase 2X.1..2X.9 PROPOSED rows. See D-16 (amended).
- Add ko_KR as a 5th locale (deferred to OQ-5).
- Implement BRAND_DNA_ANTI_SPAM (reframed in §7.10; implementation is post-reconciliation).

---

## §12 — Appendix A: file-by-file disposition

### §12.1 — Files DELETED

| Path | Count | Rationale | Deleted in PR |
|---|---|---|---|
| `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | 1 | Replaced by auto-generated version | 2X.5 |
| `config/source_of_truth/manga_series_plans/*.yaml` (excluding `_samples/`) | 132 | Stale; regenerated | 2X.6 |
| `config/source_of_truth/manga_book_plans/**/*.yaml` | 716 | Stale; regenerated | 2X.7 |
| **Total deletions** | **849** | | distributed across 3 PRs |

### §12.2 — Files MOVED

| Path | Destination | PR |
|---|---|---|
| `specs/MANGA_MODE_SYSTEM_SPEC.md` | `specs/archive/MANGA_MODE_SYSTEM_SPEC.md` | 2X.8 |
| `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` | `specs/archive/MANGA_AUTHOR_SYSTEM_SPEC.md` | 2X.8 |

### §12.3 — Files CREATED (new files)

| Path | Purpose | PR |
|---|---|---|
| `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` | This spec | 2X.0 |
| `specs/archive/DEFERRED_2026_04_26.md` | Index of archived specs | 2X.8 |
| `scripts/manga/generate_catalog_plan_from_strategic.py` | New catalog plan generator | 2X.4 |
| `.github/workflows/manga-catalog-plan-regen-check.yml` | CI gate for catalog plan freshness | 2X.4 |
| `tests/test_manga_catalog_plan_generator.py` | Tests for the new generator | 2X.4 |
| `docs/research/manga_craft/dark_fantasy.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/psychological_thriller.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/supernatural_mystery.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/sci_fi_cyberpunk.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/workplace_drama.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/action_battle.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/sports_competition.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/historical_period.md` | Craft bible | 2X.3 |
| `docs/research/manga_craft/mecha.md` | Craft bible | 2X.3 |
| (regenerated catalog plan) `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | Auto-generated | 2X.5 |
| (regenerated) `config/source_of_truth/manga_series_plans/*.yaml` | New series plans | 2X.6 |
| (regenerated) `config/source_of_truth/manga_book_plans/**/*.yaml` | New book plans | 2X.7 |

### §12.4 — Files UPDATED (in-place edit)

| Path | Change | PR |
|---|---|---|
| `scripts/manga/generate_series_plans_from_catalog.py` | Expand `VALID_GENRES` to 15 | 2X.1 |
| `schemas/manga/series_plan.schema.json` | Expand `genre.enum` + add `demographic` + `locale_origin` | 2X.1 |
| `phoenix_v4/manga/models/validation.py` | Validate new fields | 2X.1 |
| `tests/test_manga_schemas.py` | Test new genres + fields | 2X.1 |
| `config/manga/manga_taxonomy.yaml` | Add 9 new genre_families entries; remove `manhwa`; reframe `horror`, `shojo`, `shonen`, `cultivation` | 2X.2 |
| `config/manga/format_routing.yaml` | Add per-locale-genre routing for 15 genres × 4 locales | 2X.2 |
| `config/manga/manga_pacing_by_genre.yaml` | Add pacing for 9 new genres | 2X.2 |
| `config/manga/genre_ite_profiles.yaml` | Add ITE profiles for 9 new genres | 2X.2 |
| `docs/research/manga_craft/index.md` | Add 9 new lanes | 2X.3 |
| `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` | Reframe per §7.10 | 2X.8 |
| `docs/MANGA_PIPELINE_ONBOARDING.md` | Update for new genres + fields + brand model | 2X.9 |
| `docs/DOCS_INDEX.md` | Tag canonical docs + this spec | 2X.9 |

---

## §13 — Closing note

This spec is a **navigation + governance artifact** for Phase 2X. It does not delete or modify code/config in the PR that lands it; it lays out the 10-PR sequence that subsequent work executes against.

The key strategic claim — supported by `GENRE_PORTFOLIO_PLAN.md` with revenue-tier evidence — is that **the manga catalog should be 12+ genre shells × 37 brands**, not 10 narrow genres × 12 teachers. Without this reconciliation, the catalog ships at the iyashikei-only revenue ceiling (~3M per series-anchor) instead of the genre-embedded multiplier (7M–70M).

**Phase 3+ (catalog ramp) is gated on this reconciliation landing.** Shipping the existing 132 series_plans without reconciliation would produce a catalog at the wrong revenue tier.

The original audit's §1 framed the operator's choice as "Path A (ship first) vs Path B (build gates first)." This spec adds a **Path C (reconcile first)** — and argues Path C is required before any catalog ramp regardless of A/B sequencing. Path A on the existing en_US ep_001/ep_002 lane (iyashikei, single brand, single teacher) is unaffected and can proceed in parallel.

**Awaiting operator approval before any PR in §8 opens.**
