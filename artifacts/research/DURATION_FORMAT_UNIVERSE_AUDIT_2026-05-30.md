# Duration / Format Universe Audit — 2026-05-30

**Agent:** Pearl_Architect (coordinator) + Pearl_Research + Pearl_Marketing  
**Scope:** Investigative reconciliation — books, podcast, video, audiobook, freebie, manga (research-only)  
**Authority read:** `docs/SESSION_UNITY_PROTOCOL.md`; `config/format_selection/format_registry.yaml`; `docs/PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md` §2; `docs/PEARL_ARCHITECT_STATE.md` (AUTO-PLAN-SSOT-01-AMENDMENT, TEMPLATE-UNIVERSAL-01); `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md`; `docs/ATOM_NATIVE_MODULAR_FORMATS.md`; `docs/CONTENT_DURATION_MARKETING_PLAN.md`; `docs/duration_intelligence_briefing.html`; `config/podcast/podcast_format.yaml`; `config/video/format_specs.yaml`; `marketing_deep_research/`; `artifacts/research/marketing_sources/`  
**Config edits:** NONE (proposals only in companion doc)

---

## Executive summary

Phoenix Omega's duration/format universe spans **four wired registries** (book runtime, podcast, video, freebie spec) plus **research-only tiers** (ebook, manga, locale micro-sessions, guided meditation). The Wave 1 blueprint gaps are real but partially explained:

1. **Short durations (90s/2min/5min/10min)** — researched and partially wired in sibling registries; **10-min Spotify micro-podcast band has no format_id**; **90s TikTok band exceeds video registry cap (60s)**.
2. **`standard_book` = 10 chapters** — ratified 2026-05-06 via AUTO-PLAN-SSOT-01-AMENDMENT using a technical tie-breaker (preserve Python runtime), reconciled with operator's 12-chapter spine intent via TEMPLATE-UNIVERSAL-01 hybrid. **Operator confirmation still needed** (see OPEN_QUESTION_OPERATOR).
3. **Compact vs micro overlap** — same duration bands, **different spine architecture**; compact is engineering-correct + GTM-ready; micro is legacy 12-ch squeeze with known quality failures. **Keep both engineering IDs; deprecate micro for GTM.**

---

## Q1 — Is `standard_book` = 10 chapters operator-ratified or agent drift?

### Verdict: **Hybrid ratification — not pure drift, not pure operator intent**

| Layer | Chapter count | Authority | Ratification |
|-------|--------------|-----------|--------------|
| Topic spine (authoring) | **12** | `registry/{topic}.yaml`; `TEMPLATE-UNIVERSAL-01` | Operator architecture ask reconciled 2026-05-06 |
| `standard_book` auto-plan output | **10** | `format_registry.yaml` `chapter_count_default: 10` | AUTO-PLAN-SSOT-01-AMENDMENT Group B, 2026-05-06 |
| Vestigial tier context | **12** | `RUNTIME_TEMPLATES['standard_book']` in `book_structure_plan.py` | Not auto-plan path; cleanup flagged |

### Evidence chain

1. **Registry historically said 12** — PR #252 incident restore → PR #409 word_range calibration (2026-03-30 / 2026-04-09).
2. **Python auto-plan said 10** — BSG-011 / ACT-011 "Book plan generator" (2026-04-14); `FORMAT_CHAPTER_COUNTS['standard_book'] = 10`.
3. **Pearl_Dev STOP 2026-05-06** — naive registry swap would have silently changed 6 formats including `standard_book`.
4. **AUTO-PLAN-SSOT-01-AMENDMENT (2026-05-06)** — Group B ruling: **prefer Python** (matches current runtime behavior); no spec text in `PHOENIX_V4_5_WRITER_SPEC.md` or `PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` declares chapter_count for divergent formats.
5. **TEMPLATE-UNIVERSAL-01 (same day)** — Option (c) hybrid: 12×10×≥3 universal at **spine layer**; per-format `chapter_count_default` at **auto-plan output layer** via subset (`compact_chapter_subset`) or direct count.
6. **PEARL_PRIME_BOOK_SYSTEM_CANONICAL.md §2** — documents 10 as registry SSOT; explicitly retires "12 chapters per book" canonical claim for **output**, not spine authoring.

### Authority assessment

The 10-chapter value is **architecturally ratified** (cap entry status: ratified) but the **decision mechanism was agent adjudication** ("prefer Python over registry"), not an operator decision log row stating "canonical book = 10 chapters." The operator's mental model of 12 chapters maps correctly to the **spine authoring contract**; the 10-chapter output is a **subset runtime**, not a contradiction if both layers are understood.

### OPEN_QUESTION_OPERATOR — Q1

> **OQ-DFU-01:** Confirm that `standard_book` catalog SKU = **10 chapters / 55 min / 9k–18k words** is the operator-intended default consumer book, with 12-chapter arcs reserved for `extended_book_2h` + F006 structural pairings — OR revert to 12-chapter `standard_book` and re-adjudicate AUTO-PLAN-SSOT-01-AMENDMENT Group B.

---

## Q2 — Compact vs micro: differentiation and redundancy

### Verdict: **Engineering-differentiated; GTM-redundant for 15/20 min bands**

| Format pair | Duration | Chapters | Spine mechanism | Quality evidence | Marketing role |
|-------------|----------|----------|-----------------|------------------|----------------|
| `micro_book_15` | 15 min | 5 (registry) but **12-ch spine forced** | Full 12-ch topic spine | EI 0.4753 FAIL; +43% word overrun (`COMPACT_BOOK_FORMAT_SPECS` §2) | Deprecated catalog |
| `compact_book_5ch_15min` | 15 min | 5 | `compact_chapter_subset: [1,4,7,10,12]` | Purpose-built; PR-D-SPINE-01 wired | Primary short catalog |
| `micro_book_20` | 20 min | 6 | 12-ch spine | +42.5% overrun; 6/12 ch flow fails | Deprecated catalog |
| `compact_book_5ch_20min` | 20 min | 5 | Same subset as 5ch_15 | More words/chapter | Primary short catalog |
| `short_book_30` | 30 min | 8 | 12-ch spine | +15.6% overrun; 4/12 ch flow fails | Interim until compact validated |
| `compact_book_8ch_30min` | 30 min | 8 | `compact_chapter_subset: [1,3,4,6,7,9,10,12]` | Purpose-built | Primary 30-min catalog |

**Differentiation axis:** Compact formats compress the **4-phase narrative arc** (HARDSHIP/HELP/HEALING/HOPE) into fewer chapters with **larger per-chapter word budgets**. Micro/short runtimes reuse the 12-ch spine and squeeze — structurally broken for short bands per `COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md`.

**Recommendation:**

| Action | Formats |
|--------|---------|
| **KEEP (GTM primary)** | `compact_book_5ch_15min`, `compact_book_5ch_20min`, `compact_book_8ch_30min` |
| **DEPRECATE (GTM)** | `micro_book_15`, `micro_book_20` — redirect format selector; retain ID for backward compat |
| **KEEP (interim)** | `short_book_30` until compact_8ch smoke validated at scale |
| **DO NOT MERGE IDs** | Different spine semantics; merging would break `compact_chapter_subset` contract |

### OPEN_QUESTION_OPERATOR — Q2

> **OQ-DFU-02:** Approve GTM deprecation of `micro_book_15` / `micro_book_20` (selector redirect to compact equivalents) — yes/no?

---

## Q3 — Atom-native modular formats: marketing roles

All 10 formats backfilled in registry Group A (AUTO-PLAN-SSOT-01-AMENDMENT) with `chapter_count_default` only — **no `duration_minutes` or `word_range`**. Authority for structure: `docs/ATOM_NATIVE_MODULAR_FORMATS.md`.

| format_id | Duration (doc) | Marketing role | Revenue function | Funnel | Catalog / freebie |
|-----------|----------------|----------------|------------------|--------|-------------------|
| `five_min_practice` | ~5 min (350–650 words) | sample/preview | feeds funnel; brand awareness | awareness | **Both** — app audio unit + lead magnet |
| `pocket_guide` | 180–420 words/entry | catalog_product | sells directly | consideration | Catalog (EPUB/PDF) |
| `ten_things_to_do` | 120–260 words/item | catalog_product | feeds funnel; platform reach | consideration | Catalog + listicle cross-promo |
| `symptom_to_action_atlas` | 90–220 words/card; **60s action** | catalog_product | sells directly; feeds funnel | retention | Catalog (crisis utility) |
| `daily_text_audio_companion` | 45–120 sec/day | catalog_product | feeds funnel | retention | Subscription SKU |
| `crisis_cards` | 90–200 words/card | **freebie_leadgen** | feeds funnel | awareness | **Freebie primary** (`PHOENIX_FREEBIE_SYSTEM_SPEC`) |
| `weekly_challenge_pack` | 180–480 words/day | catalog_product | feeds funnel | retention | Habit program SKU |
| `faq_audiobook` | **2–4 min**/answer | catalog_product; cross_promo | platform reach; feeds funnel | consideration | Catalog + YouTube/podcast export |
| `myth_vs_mechanism` | **3–6 min**/ep | sample/preview | platform reach; feeds funnel | awareness | Social clip source |
| `protocol_library` | 120–280 words | catalog_product | sells directly | retention | Drill catalog SKU |

**SSOT gap:** `five_min_practice` overlaps `podcast_short` (2–5 min) and `exercise_video` (5–15 min). Recommend one canonical micro-practice ID with channel-specific render wrappers.

### OPEN_QUESTION_OPERATOR — Q3

> **OQ-DFU-03:** Confirm `crisis_cards` as freebie-only (not paid catalog row) — yes/no?

---

## Short-duration hunt: 90s / 2min / 5min / 10min

| Target | Research source | Wired home | Status |
|--------|-----------------|------------|--------|
| **90s** | TikTok 60–90s wellness (`research/2026-03-31_optimal-content-durations-global.md` §4.3; `CONTENT_DURATION_MARKETING_PLAN` S4/S5) | `therapeutic_short`: 15–**60s** max (`config/video/format_specs.yaml`) | **GAP** — extend cap to 90s or add `therapeutic_short_90s` |
| **2 min** | Micro-mindfulness <2 min (`research/2026-03-31` §6.8); FAQ atom 2–4 min | `podcast_short`: 120–300s; `faq_audiobook` stub | **Partial** — podcast wired; atom stub only |
| **5 min** | HRV breathing [D:16]; guided meditation tier; WEBTOON 5-min video | `exercise_video`: 300–900s; `five_min_practice` stub; `podcast_short` lower bound | **Partial** |
| **10 min** | Spotify strategy: "3hr audiobooks + daily 10-min micro-podcasts" (`duration_intelligence_briefing.html`); [D:18][D:38] "10 min daily beats 70 min weekly" | **None** — gap between `podcast_short` (2–5) and `podcast_episode` (15–25) | **MISSING** — needs `podcast_micro_10min` or extend `podcast_short` range |

**No `Spotify-10min` format_id exists** in any registry. It is a composite GTM strategy, not a wired format.

---

## Cross-channel format universe

### Books — `config/format_selection/format_registry.yaml`

**Runtime tiers (7 + 3 compact + 10 atom-native):**

| format_id | Duration | Chapters | Word range | In research |
|-----------|----------|----------|------------|-------------|
| `micro_book_15` | 15 min | 5 | 2500–4500 | Y (deprecated path) |
| `micro_book_20` | 20 min | 6 | 3000–5500 | Y (deprecated path) |
| `short_book_30` | 30 min | 8 | 4500–7500 | Y |
| `standard_book` | 55 min | **10** | 9000–18000 | Y |
| `extended_book_2h` | 120 min | 14 | 17000–25000 | Y |
| `deep_book_4h` | 240 min | 16 | 20000–40000 | Y |
| `deep_book_6h` | 360 min | 20 | 50000–72000 | Y |
| `compact_book_5ch_15min` | 15 min | 5 | 3000–4500 | Y |
| `compact_book_5ch_20min` | 20 min | 5 | 4000–5500 | Y |
| `compact_book_8ch_30min` | 30 min | 8 | 5500–7500 | Y |
| Atom-native (×10) | per ATOM_NATIVE doc | 5–10 | **stub** | Y |

**Structural beat maps F001–F015:** production taxonomy only; not GTM SKUs.

### Podcast — `config/podcast/podcast_format.yaml`

| format_id | Duration | Platform | Marketing role |
|-----------|----------|----------|----------------|
| `podcast_episode` | 15–25 min | Spotify, Apple, YouTube Podcasts | catalog_product |
| `podcast_short` | 2–5 min | Spotify, Apple | platform_specific:spotify (daily habit) |
| `podcast_sleep` | 25–45 min | Spotify, Apple | platform_specific:spotify (sleep brands) |
| `podcast_trailer` | 3–5 min | Spotify, Apple | sample/preview |

**Research-only gaps:** `podcast_micro_dose_5-10min`, `podcast_deep_dive_45-60min` — documented in `CONTENT_DURATION_MARKETING_PLAN` S2, not wired.

### Video / audiobook clips — `config/video/format_specs.yaml`

| CLI key | id | Duration | Platform |
|---------|-----|----------|----------|
| `short` | therapeutic_short | 15–60s | YT Shorts, TikTok, Reels, Douyin |
| `mid` | therapeutic_mid | 2–8 min | YouTube, Bilibili |
| `long` | therapeutic_long | 15–30 min | YouTube, Bilibili |
| `motion_comic` | motion_comic | 3–10 min | YouTube, Webtoon |
| `lofi` | lofi_stream | 60–240 min | YouTube |
| `exercise` | exercise_video | 5–15 min | YouTube, TikTok |
| `presentation` | manga_presentation | 1–10 min | YouTube, investor_deck |
| `audiobook` | audiobook_longform | 5–90 min | YouTube, Bilibili |
| `audiobook_short` | audiobook_clip | 30–60s | Shorts, TikTok, Reels |

**Note:** `config/audiobook/` directory does not exist; audiobook GTM = book runtimes + locale plan + video render keys.

### Freebie — `specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md`

16 freebie types (companion_workbook_pdf, somatic_html_tool, assessment_html, mini_audio, checklist_pdf, journal_pdf, identity_sheet_pdf, guided_audio, thirty_day_tracker_pdf, environment_guide_pdf, affirmations_audio, audio_journal_prompts, emergency_kit_html, conversation_scripts_pdf, resistance_mapping_html, accountability_partner_pdf). All: **freebie_leadgen / feeds funnel**.

### Research-only channels (no book registry ID)

| Channel | Key tiers | Source |
|---------|-----------|--------|
| Ebook | short 60–100pp; standard 150–230pp; workbook 80–120pp | `CONTENT_DURATION_MARKETING_PLAN` S2 |
| Manga | micro 3–5 panels; short 12–20; standard 40–60; volume 142–256pp | S3 + `[M]` research |
| Locale audiobook | ko-KR 15–30 min micro-session A/B | `AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md` |
| Guided meditation | 5 / 10 / 15 / 20 min tiers | S2 + [D:16][D:18] |
| Catalog bands | micro 15–30 / mid 45–90 / deep 180–360 min | `brand_archetype_registry.yaml`; `sub5_duration_bands.md` (low confidence %) |

---

## Research vs registry gaps

### In research, NOT in any runtime registry

- Ebook tiers (KDP page-count bands)
- Manga panel/page tiers
- `podcast_micro_dose_5-10min` / `podcast_deep_dive_45-60min`
- `guided_meditation_5min` / `guided_meditation_10min` (standalone IDs)
- Korea Millie 30-min summary; Ximalaya 10–30 min episodic split
- Catalog `duration_strategy` percentage bands (scaffold only in `marketing_deep_research/05_duration_bands_patch.yaml`)

### In registry, NOT in duration marketing research

- F001–F015 structural beat maps
- F008 Micro-Habits Stacking (52 ch)
- F012 Permission Slip Collection (52 ch)
- `extended_book_2h` (marketing "extended" = 5–7 hr band, different semantics)
- Podcast segment taxonomy (cold_open 30–60s, etc.)
- `RUNTIME_TEMPLATES` vestigial chapter_count fields

---

## Marketing source inventory

### `marketing_deep_research/` (8 files)

README, deep-research-report, 01_gtm_identity_patch, 02_emotional_vocabulary_patch, 05_duration_bands_patch (TBD values), 06_cover_design_patch, 07_pricing_topology_patch, 08_kdp_ebook_strategy_patch.

### `artifacts/research/marketing_sources/` (7 files)

MARKETING_RESEARCH_SUMMARY, sub1_gtm_audience_funnel, sub2_emotional_vocabulary, sub5_duration_bands, sub6_cover_design, sub7_pricing_topology.

### Primary research backbone

- `research/2026-03-31_optimal-content-durations-global.md` — [D] 43 sources
- `research/2026-03-31_manga-selfhelp-page-counts.md` — [M]
- `research/2026-03-31_video-platform-production-research.md` — [R]
- `docs/CONTENT_DURATION_MARKETING_PLAN.md` — master strategy
- `docs/duration_intelligence_briefing.html` — executive mirror + Spotify 10-min lead
- `docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md` — locale catalog (replaces missing LOCALE doc)

---

## OPEN_QUESTION_OPERATOR (summary for PR)

| ID | Question |
|----|----------|
| OQ-DFU-01 | Confirm 10-chapter `standard_book` as default catalog SKU vs revert to 12 |
| OQ-DFU-02 | Approve GTM deprecation of `micro_book_15` / `micro_book_20` |
| OQ-DFU-03 | Confirm `crisis_cards` freebie-only (not paid catalog) |
| OQ-DFU-04 | Add `podcast_micro_10min` (600s) for Spotify daily micro-dose band — yes/no? |
| OQ-DFU-05 | Extend `therapeutic_short` cap from 60s to 90s for TikTok Creator Rewards band — yes/no? |

---

## Research gaps (Pearl_Research follow-on)

- No primary-source completion curves for catalog `duration_strategy` % bands (`sub5_duration_bands.md` self-flags low confidence)
- `COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` header still says "not yet wired" — stale vs registry (doc update needed, separate PR)
- Vestigial `RUNTIME_TEMPLATES.chapter_count` triple-source cleanup not scheduled

---

## Companion artifacts

- `artifacts/research/duration_format_marketing_role_matrix_2026-05-30.tsv` — per-format marketing roles
- `artifacts/research/RECOMMENDED_REGISTRY_CHANGES_2026-05-30.md` — proposed config additions (NOT applied)
