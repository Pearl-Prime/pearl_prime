# Manga Catalog Reconciliation Spec

**Version:** 1.1.0 (refresh — incorporates OQ-1..OQ-9 resolutions; locale scope expanded 4→5; deletion sequence collapsed to atomic per OQ-4)
**Authority:** Pearl_Architect (synthesis) — supersedes the operational layer of `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (Apr 7–12) and aligns the planner / schema / taxonomy / config / generated YAMLs with the strategic refresh in `docs/GENRE_PORTFOLIO_PLAN.md` (Apr 23).
**Date:** 2026-04-26 (v1.1 refresh)
**Status:** Operator-approved through OQ-9. Phase 2X.1 atomic PR ready to author when Pearl_Dev capacity opens.
**Inputs:** [docs/MANGA_PIPELINE_AUDIT_2026-04-26.md](../docs/MANGA_PIPELINE_AUDIT_2026-04-26.md) (Phase 1 audit findings); [docs/GENRE_PORTFOLIO_PLAN.md](../docs/GENRE_PORTFOLIO_PLAN.md) (strategic refresh, PR #583); [docs/CJK_CATALOG_PLAN.md](../docs/CJK_CATALOG_PLAN.md) + [docs/US_CATALOG_PLAN.md](../docs/US_CATALOG_PLAN.md) (per-locale strategic plans); [docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md](../docs/MANGA_SERIES_PORTFOLIO_RESEARCH.md) (research feeder); [docs/MANGA_MODE_STRATEGY.md](../docs/MANGA_MODE_STRATEGY.md) (business strategy + market analysis, migrated from docx per OQ-7).
**Out-of-scope inputs:** `docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md` and `docs/AUDIOBOOK_TITLE_AND_CATALOG_MARKETING_SYSTEM.md` are **audiobook** plans, not manga. Not touched by this spec. (Naming aligned to AUDIOBOOK_ prefix per OQ-9 PR #686.)

**Changelog:**
- **v1.0.0** (2026-04-26) — Initial spec landed via PR #682.
- **v1.0.1** (2026-04-26) — D-16 amended; stale `coordination/` refs corrected per OQ-8 disposition (iii) PR #685.
- **v1.0.2** (2026-04-26) — Audiobook doc references updated to AUDIOBOOK_ prefix per OQ-9 PR #686.
- **v1.1.0** (2026-04-26) — Refresh incorporating OQ-1..OQ-6 operator resolutions: mecha = own genre (OQ-1 a), school_coming_of_age = own genre (OQ-2 a), brand wins teacher-as-attribute (OQ-3 a), hard cutover with delete-old-stuff (OQ-4 c), ko_KR added as 5th locale rendered+held (OQ-5 b), zh_CN gray-zone distribution with full AI disclosure (OQ-6 c). Deletion sequence collapsed: 2X.1+2X.6+2X.7 fold into one atomic PR. New D-18, D-19, D-20 added.

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
| D-3 | **`artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` is RETIRED.** | Explicitly superseded; cannot remain authoritative. Replacement in §7.1. Deleted atomically in 2X.1 per D-20. |
| D-4 | **The 132 `series_plan.yaml`s are RETIRED and atomically replaced.** | Generated from the retired plan. Re-generation in §7.6 — folded into 2X.1 atomic PR per D-20. New count: ~1,110 series (37 brands × 5 locales × ~6 series/locale). |
| D-5 | **The 716 `book_plan.yaml`s are RETIRED and atomically replaced.** | Generated from the retired series plans. Re-generation in §7.7 — folded into 2X.1 atomic PR per D-20. |
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
| D-18 | **ko_KR is added as the 5th locale, rendered now, distribution held pending Korea AI Act enforcement clarity.** Routing matrix grows from 4×15=60 cells to **5×15=75 cells**. | Per OQ-5 disposition (b). Translation pipeline (Tier-2 Qwen) and CJK font registry already support KR. Render-and-hold uses sunk-cost compute; ready-to-ship the moment Korea AI Act rules clarify (post-Jan 2027 enforcement window). `distribution_status: hold_pending_market_clearance` flag added to schema. |
| D-19 | **zh_CN distribution is GRAY-ZONE-WITH-DISCLOSURE, not held.** zh_CN series push to Bilibili Comics + Kuaikan Manhua + Tencent Comics with explicit AI-disclosure metadata. | Per OQ-6 disposition (c). Adds `R-zh_CN-distribution: HIGH` to risk register: account termination possible under PRC Generative AI Service Measures (2023; algorithm filing + watermarking + identity verification required). New scripts `scripts/publish/zh_cn_release_*.py` per platform. Per-account standing tracking required. Operator accepts platform-termination risk for 400M+ reader reach. |
| D-20 | **Deletion sequence is ATOMIC** — 2X.1 (schema/planner) + 2X.6 (132 series_plan deletion) + 2X.7 (716 book_plan deletion) collapse into a single atomic PR. No backwards-compatibility window. | Per OQ-4 disposition (c) "hard cutover with delete-old-stuff". Avoids 5-week red-CI window that backwards-compat (option a) would have caused; operator chose strict typing over CI tolerance. Schema flips strict the moment YAMLs regenerate. |

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
For **5 locales** (en_US + ja_JP + zh_TW + zh_CN + ko_KR per D-18): ~239 × 5 = **~1,195 localized series.**
For 14 chapters/series: ~1,195 × 14 = **~16,730 chapters.**

Distribution-state breakdown (per D-18 + D-19):
- **Distributed**: ~239 × 4 (en_US + ja_JP + zh_TW + zh_CN) = ~956 localized series. zh_TW + zh_CN both push (zh_CN gray-zone with disclosure per D-19). en_US KDP + Canvas-when-policy-clear; ja_JP KDP + LINE Manga Indies.
- **Rendered + held**: ~239 × 1 (ko_KR) = ~239 localized series. Held until Korea AI Act enforcement posture clarifies (post-Jan 2027). `distribution_status: hold_pending_market_clearance`.

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

### §6.1 — Deletion segments (collapsed per D-20)

Per OQ-4 disposition (c) hard cutover, segments 6.1.A + 6.1.C + 6.1.D **collapse into a single atomic PR (2X.1)**. The schema/planner flip and the YAML deletion happen in the same commit so CI never sees a stale-YAML/new-schema mismatch.

| Segment | Files | Count | PR | Notes |
|---|---|---|---|---|
| **6.1.A — ATOMIC: stale catalog plan + 132 series_plans + 716 book_plans + schema flip** | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` (stale; replaced) + `config/source_of_truth/manga_series_plans/*.yaml` (excluding `_samples/`; 132 deleted, ~1,110 created) + `config/source_of_truth/manga_book_plans/<dir>/*.yaml` (716 deleted, ~16,730 created) + `scripts/manga/generate_series_plans_from_catalog.py` (VALID_GENRES 10→15) + `schemas/manga/series_plan.schema.json` (genre.enum + demographic + locale_origin + distribution_status) + `phoenix_v4/manga/models/validation.py` + `tests/test_manga_schemas.py` | 849 deletes + ~17,840 creates | **2X.1** | `feat(manga): catalog reconciliation atomic — schema/planner flip + 848 stale YAML retire + regenerate (5 locales × 15 genres)` — owner-approved per this spec D-3/D-4/D-5/D-20 |
| **6.1.B — Archive 2 zero-ref specs + reframe BRAND_DNA** | `specs/MANGA_MODE_SYSTEM_SPEC.md` (moved to specs/archive/), `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` (moved), `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` (updated, kept) | 2 moves + 1 update + 1 new index | **2X.5** (renumbered) | `chore(manga): archive 2 zero-ref specs + reframe BRAND_DNA spec` |
| **6.1.C — Truly orphan code (post-migration only)** | per audit Phase 2A; only after callers are migrated | 2–4 | (future, post-2X) | `chore(manga): prune migrated-orphan scripts (audit Phase 2A — final)` |

**Total deletions in atomic 2X.1: ~849 files.** All driven by the catalog reconciliation; none ad hoc. CLAUDE.md mass-deletion rule satisfied via D-20 + this spec acting as explicit owner approval.

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
| `docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md` | **Audiobook plan, not manga.** Out of scope. |
| `docs/AUDIOBOOK_TITLE_AND_CATALOG_MARKETING_SYSTEM.md` | **Audiobook plan, not manga.** Out of scope. |
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

### §7.6 — Re-generate 132 → ~1,195 series_plan YAMLs (atomic per D-20)

**Folded into the 2X.1 atomic PR per D-20.** After deleting the 132 stale, run `generate_series_plans_from_catalog.py` against the regenerated `MANGA_FULL_CATALOG_PLAN.md` from §7.1. Outputs the new strategic-aligned series_plan YAMLs.

**Naming convention update** (per §5.2):
- Old: `{brand}__{teacher}__{locale}__{topic}__{series_slug}.yaml`
- New: `{brand}__{locale}__{genre}__{topic}__{series_slug}.yaml` (teacher captured inside the YAML's `teacher_id` field, may be null)

**Locale fan-out per D-18:** ko_KR is included from regen day one. ko_KR series get `distribution_status: hold_pending_market_clearance` automatically; zh_CN series get `distribution_status: gray_zone_disclosed` per D-19.

### §7.7 — Re-generate 716 → ~16,730 book_plan YAMLs (atomic per D-20)

**Folded into the 2X.1 atomic PR per D-20.** Run `generate_book_plans_from_series.py` against the new series_plan set. Outputs the new book_plan YAMLs (5 locales × ~239 brands × ~14 chapters/series).

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

## §8 — Migration sequence (PR-by-PR) — collapsed to 7 PRs per D-20

The work is sequenced to be reversible at each step. Each PR has a single responsibility, except the atomic 2X.4 which is intentionally non-reversible (per OQ-4 hard cutover; D-20).

### Phase 2X.0 — Spec lands (already merged: PR #682; refresh in this v1.1 PR)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.0** | Pearl_Architect | v1.0 spec landed at PR #682 (7d93ae6c); v1.0.1 corrections at PR #685 (8a8578ba); v1.0.2 audiobook ref updates at PR #686 (1f4f8a28); v1.1 refresh (this PR) — incorporates OQ-1..OQ-9 resolutions and collapses sequence per D-20. | `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` |

### Phase 2X.1 — Build catalog plan generator (was old 2X.4)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.1** | Pearl_Dev | Add `scripts/manga/generate_catalog_plan_from_strategic.py` per §7.1. Add `.github/workflows/manga-catalog-plan-regen-check.yml` CI gate. Tests against fixture strategic-doc inputs. **Generator must NOT yet write** `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` — that happens in 2X.4 atomic. This PR builds the tool only. | 1 new script + 1 GHA workflow + tests |

**Workstream:** `ws_manga_phase_2x_4_catalog_generator` (proposed; ID kept stable per coordination convention even though phase number renumbered v1.0→v1.1).

### Phase 2X.2 — Taxonomy + routing + pacing config (5 locales × 15 genres = 75 routing cells)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.2** | Pearl_Dev | Update `config/manga/manga_taxonomy.yaml`, `config/manga/format_routing.yaml`, `config/manga/manga_pacing_by_genre.yaml`, `config/manga/genre_ite_profiles.yaml` for the 15-genre allow-list across **5 locales** (en_US/ja_JP/zh_TW/zh_CN/ko_KR per D-18). Adds `distribution_status` semantics: `distributed` (default) / `gray_zone_disclosed` (zh_CN per D-19) / `hold_pending_market_clearance` (ko_KR per D-18). | 4 config files |

**Workstream:** `ws_manga_phase_2x_2_taxonomy_routing_pacing` (proposed).

### Phase 2X.3 — Add 9 new craft bibles

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.3** | Pearl_Research | Synthesize the 9 new craft bibles from existing research (per §7.8 source map). Update `docs/research/manga_craft/index.md`. Independent of 2X.1/2X.2/2X.4 (docs-only; doesn't gate anything). | 10 files in `docs/research/manga_craft/` |

**Workstream:** `ws_manga_phase_2x_3_craft_bibles` (proposed).

### Phase 2X.4 — ATOMIC: schema flip + replace catalog plan + delete 848 stale YAMLs + regenerate (was old 2X.1+2X.5+2X.6+2X.7)

| PR | Owner | Scope | Files | Owner-approval |
|---|---|---|---|---|
| **2X.4** | Pearl_Dev | **Single atomic PR per D-20.** (a) Flip `VALID_GENRES` 10→15 in `scripts/manga/generate_series_plans_from_catalog.py:45–49`. (b) Flip `genre.enum` + add `demographic` + `locale_origin` + `distribution_status` in `schemas/manga/series_plan.schema.json`. (c) Update `phoenix_v4/manga/models/validation.py`. (d) Run `generate_catalog_plan_from_strategic.py` (from 2X.1) to produce new `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`. (e) `git rm` 132 stale series_plan YAMLs + 716 stale book_plan YAMLs. (f) Run `generate_series_plans_from_catalog.py` against new catalog plan to emit ~1,195 series_plans. (g) Run `generate_book_plans_from_series.py` to emit ~16,730 book_plans. (h) Update `tests/test_manga_schemas.py` for new shape. All in **one commit**. | 4 code files + 1 catalog plan replaced + 132+716 = 848 YAMLs deleted + ~1,195 + ~16,730 = ~17,925 YAMLs created | **Operator approval = approval of this spec D-3/D-4/D-5/D-20.** PR must reference `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md` §3 D-20 + §6.1.A in its body. **Will trigger CLAUDE.md mass-deletion rule (>50 files); spec acts as explicit owner approval.** |

**Workstream:** `ws_manga_phase_2x_1_schema_atomic` (proposed; ID kept stable from v1.0 spec; phase number renumbered to 2X.4).

**Why this is non-reversible:** Per OQ-4 disposition (c), the operator chose strict typing over CI tolerance. Once 2X.4 lands, the legacy 4-locale × 10-genre shape is gone. Any pre-2X.4 branch with old-shape YAMLs becomes unmergeable to main without rebasing onto post-2X.4. This is the intended design.

### Phase 2X.5 — Archive 2 zero-ref specs + reframe BRAND_DNA (was old 2X.8)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.5** | Pearl_Architect | Move `specs/MANGA_MODE_SYSTEM_SPEC.md` and `specs/MANGA_AUTHOR_SYSTEM_SPEC.md` to `specs/archive/` with a `specs/archive/DEFERRED_2026_04_26.md` index file. Update `specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md` per §7.10 (reframing — kept; aligned to GENRE_PORTFOLIO_PLAN per-brand %-allocation as anti-homogeneity mechanism). | 2 moves + 1 update + 1 new index file |

**Workstream:** `ws_manga_phase_2x_8_archive_specs` (proposed).

### Phase 2X.6 — Update onboarding + docs index (was old 2X.9)

| PR | Owner | Scope | Files |
|---|---|---|---|
| **2X.6** | Pearl_Architect | Update `docs/MANGA_PIPELINE_ONBOARDING.md` (15 genres + new fields + 5-locale brand model + distribution_status semantics) and `docs/DOCS_INDEX.md` (CANONICAL tags for GENRE_PORTFOLIO_PLAN + CJK_CATALOG_PLAN + US_CATALOG_PLAN + this spec + MANGA_MODE_STRATEGY.md). | 2 doc files |

**Workstream:** `ws_manga_phase_2x_9_onboarding_docs_index` (proposed).

### Sequence summary

```
PR 2X.0 — v1.0 spec landed PR #682 → v1.1 refresh (this PR)
   ↓
PR 2X.1 — catalog plan generator built (Pearl_Dev)
   ↓
PR 2X.2 — taxonomy/routing/pacing for 15 genres × 5 locales (Pearl_Dev)
   ↓
PR 2X.3 — 9 craft bibles added (Pearl_Research; can run in parallel with 2X.2)
   ↓
PR 2X.4 — ATOMIC: schema/planner + 848 YAML deletes + regen 17,925 YAMLs (Pearl_Dev)
   ↓
PR 2X.5 — specs archived + BRAND_DNA reframed (Pearl_Architect)
   ↓
PR 2X.6 — onboarding + docs index updated (Pearl_Architect)
```

**Total:** 7 PRs over Phase 2X (1 spec + 6 execution). Estimated ~40–80 hours engineering, distributed.

**Critical constraint:** 2X.1 (generator) and 2X.2 (config) must both land before 2X.4 (atomic). 2X.4 is non-reversible per D-20. No backwards-compat window — schema flip and YAML regen happen in the same commit; CI never sees a stale-YAML/new-schema mismatch because the deletion + regeneration are atomic.

**Workstream ID note:** the 7 pre-staged workstream rows in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` (added in PR #685) keep their original IDs for stability. The phase numbers in this spec section refer to merge-order-when-executed, not to the workstream ID. The mapping is:
- `ws_manga_phase_2x_1_schema_atomic` → spec phase 2X.4 (atomic)
- `ws_manga_phase_2x_2_taxonomy_routing_pacing` → spec phase 2X.2
- `ws_manga_phase_2x_3_craft_bibles` → spec phase 2X.3
- `ws_manga_phase_2x_4_catalog_generator` → spec phase 2X.1
- `ws_manga_phase_2x_5_replace_catalog_plan` → ABSORBED into spec phase 2X.4 atomic; row will be marked completed when 2X.4 merges
- `ws_manga_phase_2x_8_archive_specs` → spec phase 2X.5
- `ws_manga_phase_2x_9_onboarding_docs_index` → spec phase 2X.6

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

## §10 — Open questions for operator — ALL 9 RESOLVED 2026-04-26

All 9 open questions from v1.0 of this spec have been answered by the operator. OQ-7, OQ-8, OQ-9 were executed via PRs #684, #685, #686. OQ-1..OQ-6 are captured here as decisions that the Phase 2X execution PRs (2X.1..2X.6) implement.

### OQ-1 — Mecha as 13th genre or sub-shell? — RESOLVED (a) own genre

**Disposition:** **(a) Mecha is its own genre.** Promoted to slot #15 in `VALID_GENRES` per §4.1. Spec D-9 stands.

**Rationale:** the strategic plan cites Evangelion ($16B franchise) as the highest revenue-tier exemplar precisely because the mecha shell does distinctive work. Folding it into sci-fi/cyberpunk would lose the Genre Shell Revenue Gap signal. Cost (one routing cell per locale + one craft bible) is small.

**Implementation:** carried into 2X.4 atomic + 2X.3 craft bible (`docs/research/manga_craft/mecha.md`).

### OQ-2 — School / Coming-of-Age as own genre or sub-shell? — RESOLVED (a) own genre

**Disposition:** **(a) `school_coming_of_age` is its own genre.** Promoted to slot #14 in `VALID_GENRES` per §4.1.

**Rationale:** operator chose the explicit-genre treatment over the orthogonal-`life_stage`-modifier alternative (b). Means brands that target formative-anxiety contexts get a clean catalog cell; cost is one more routing cell per locale + one more craft bible.

**Implementation:** carried into 2X.4 atomic + 2X.3 craft bible (`docs/research/manga_craft/school_coming_of_age.md`).

### OQ-3 — Brand-vs-teacher reconciliation aggressiveness — RESOLVED (a) brand wins

**Disposition:** **(a) brand wins; 37 brands as the catalog allocation unit; teacher becomes a body attribute (`teacher_id` field, may be `null`).** Spec D-6 stands.

**Rationale:** filenames drop teacher from path, gaining `ls config/source_of_truth/manga_series_plans/{brand}__*` discoverability. Teacher attribution stays canonical via `teacher_id` in YAML body. Brands without teacher anchors (e.g., `legacy_builder_memoir`, `bio_flow_healing`) get `teacher_id: null` cleanly.

**Implementation:** carried into 2X.4 atomic. Filename convention: `{brand}__{locale}__{genre}__{topic}__{slug}.yaml`.

### OQ-4 — Demographic flip timing — RESOLVED (c) hard cutover

**Disposition:** **(c) hard cutover with delete-old-stuff. No backwards-compatibility window.** D-20 codifies this. Schema flip + 132+716 YAML deletion + regenerate happen in **one atomic PR (2X.4)** — no intermediate state where old-shape YAMLs exist alongside new-shape schema.

**Rationale:** operator chose strict typing over CI stability. Original spec recommended (a) backwards-compat with a 5-week migration window; operator overrode with stricter approach. Atomic deletion sidesteps the red-CI period.

**Implementation:** the 10-PR sequence in v1.0 spec collapses to 7 PRs in v1.1; old 2X.1 (schema, no deletes) + 2X.5 (catalog plan replace) + 2X.6 (132 deletes + regen) + 2X.7 (716 deletes + regen) all fold into the single atomic 2X.4 per D-20.

### OQ-5 — ko_KR as 5th locale? — RESOLVED (b) render + hold distribution

**Disposition:** **(b) ko_KR added as 5th locale; rendered now, distribution held pending Korea AI Act enforcement clarity (post-Jan 2027).** D-18 codifies. Routing matrix grows 4×15=60 cells → **5×15=75 cells**.

**Rationale:** translation pipeline (Tier-2 Qwen) and CJK fonts already support KR. Render-and-hold uses sunk-cost compute; ready-to-ship the moment Korea AI Act rules clarify. Not aggressive Path A (which would risk AI Act enforcement); not (c) skip (which would abandon the 170M-MAU webtoon-native audience).

**Implementation:** ko_KR added to `VALID_LOCALES` + format_routing.yaml (2X.2) + atomic regen includes ko_KR (2X.4). New `distribution_status: hold_pending_market_clearance` flag.

### OQ-6 — zh_CN distribution stance — RESOLVED (c) gray-zone with full AI disclosure

**Disposition:** **(c) zh_CN distribution attempts via Bilibili Comics + Kuaikan Manhua + Tencent Comics with full AI-disclosure metadata.** D-19 codifies.

**Rationale:** operator chose maximum reach (~400M Mandarin readers) over conservative render-and-hold. Accepts platform-termination risk under PRC Generative AI Service Measures (2023; algorithm filing + watermarking + identity verification required).

**New risk:** `R-zh_CN-distribution: HIGH` added to risk register. Mitigations: per-platform account-standing tracking; graceful re-routing if a platform terminates; explicit `distribution_disclosure: ai_assisted_full` on every series.

**Implementation:** zh_CN series get `distribution_status: gray_zone_disclosed` (2X.2 config) + new operational scripts `scripts/publish/bilibili_comics_release.py`, `scripts/publish/kuaikan_release.py`, `scripts/publish/tencent_comics_release.py` (out-of-spec; future workstreams under this project but not part of 2X.1..2X.6).

### OQ-7 — `MANGA_MODE_STRATEGY.docx` migration — RESOLVED (a) executed via PR #684

**Disposition:** **(a) Migrated to `docs/MANGA_MODE_STRATEGY.md`** (343 lines / 20.7 KB; 9 tables / 68 rows preserved inline). Verdict: KEEP as strategic complement to `specs/MANGA_MODE_SYSTEM_SPEC.md` — NOT redundant. The two documents are explicitly cross-referenced; docx covers business strategy + market analysis (market opportunity, regional strategy, Gen Z/Alpha demographics, monetization tiers, archetype × teacher fit, risk register), spec covers technical architecture.

**Status:** ✅ DONE PR #684 merge SHA `8aaa46aafd81046fe9c5b1702f803e2bbab61c6e`.

### OQ-8 — Coordination layer — RESOLVED 2026-04-26

**Original framing (incorrect):** Per audit §8 OQ-2, `coordination/` does not exist; spec D-16 left it out of scope.

**Correction (2026-04-26 disposition iii):** The coordination layer **exists at `artifacts/coordination/`**, not the bare `coordination/` path. The audit's docs-subagent search was bound to the wrong path. Resolution executed in the same PR that records this correction:
- `proj_manga_catalog_reconciliation_20260426` added to `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- 4 completed workstream rows backfilled in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` for PRs #680/#682/#684 and the coordination-sync PR itself
- 7 proposed workstream rows pre-staged for Phase 2X.1..2X.9 (OQ-4 hard-cutover collapses 2X.1+2X.6+2X.7 into one atomic PR; 2X.6 and 2X.7 do not appear as separate workstreams)
- D-16 amended in §3 (this spec)
- Stale `coordination/` references in this spec and in `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` corrected in place

### OQ-9 — Audiobook-named docs in `docs/` — RESOLVED (a) executed via PR #686

**Disposition:** **(a) Renamed in place with `AUDIOBOOK_` prefix.** `docs/LOCALE_CATALOG_MARKETING_PLAN.md` → `docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md`; `docs/TITLE_AND_CATALOG_MARKETING_SYSTEM.md` → `docs/AUDIOBOOK_TITLE_AND_CATALOG_MARKETING_SYSTEM.md`. Plus 12 inbound reference updates (56 total replacements across specs/, docs/, config/) using negative lookbehind to avoid double-prefixing. Frozen historical context in `de_chats_to_analyze/`, `old_chat_specs/`, `artifacts/research/`, `artifacts/audit/` left untouched.

**Status:** ✅ DONE PR #686 merge SHA `1f4f8a28fc0e09163b4a88653074114c337ca1ea`.

---

## §11 — Out of scope

This spec does not:

- ~~Modify `coordination/` (does not exist; D-16).~~ **AMENDED 2026-04-26:** The coordination layer at `artifacts/coordination/` is updated by this spec's execution per OQ-8 disposition (iii). See D-16 (amended) and §10 OQ-8 (resolved).
- Add a live LLM writer in `chapter_runner` (per audit §7.9 — Tier-1 policy decision; separate workstream).
- Implement the QC gate runner (audit §7.2; separate sprint).
- Implement MQG-01, MQG-03..08 (audit §7.3; separate sprint).
- Implement MDLG-01..05 dialogue gates (audit §7.4; separate sprint).
- Implement the cover pipeline (audit §7.5; deferred per audit-§8 OQ-8).
- Touch any audiobook artifact (`docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md`, `docs/AUDIOBOOK_TITLE_AND_CATALOG_MARKETING_SYSTEM.md`, `phoenix_v4/audiobook/`, `scripts/audiobook/`).
- Touch any video artifact (`phoenix_v4/video/`, `scripts/video/`).
- Touch the existing ep_001 production artifact in `artifacts/manga/ep_001/`.
- Merge PR #678 (gating but separate; tracked in audit §5.5).
- ~~Open new workstreams in `coordination/workstreams.tsv` (the coordination layer is out of scope).~~ **AMENDED 2026-04-26:** Workstreams are tracked in `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`; this spec's execution backfills completed workstreams (PRs #680/#682/#684/#685/#686) and pre-stages Phase 2X workstream rows. See D-16 (amended) + §10 OQ-8 (resolved).
- ~~Add ko_KR as a 5th locale (deferred to OQ-5).~~ **AMENDED 2026-04-26 v1.1:** ko_KR IS added as 5th locale per D-18 (OQ-5 resolved (b) render+hold). Routing matrix grows to 5×15=75 cells.
- Implement BRAND_DNA_ANTI_SPAM (reframed in §7.10; implementation is post-reconciliation).
- Build zh_CN distribution scripts (`scripts/publish/bilibili_comics_release.py`, `scripts/publish/kuaikan_release.py`, `scripts/publish/tencent_comics_release.py`). Per D-19 / §10 OQ-6 (c), zh_CN gray-zone distribution is approved-in-direction but operational tooling lands in **separate workstreams** under `proj_manga_catalog_reconciliation_20260426`, not as part of 2X.1..2X.6.
- Add cover gate execution timing decision (per audit §7.5 + spec §10 OQ-7 from v1.0; deferred until cover pipeline workstream opens).

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
