# Session Handoff — 2026-04-27

**Topic:** Universal-router doc anchor + catalog/pipeline truth audit
**Owner:** Pearl_GitHub (this session) → next operator session
**Branch worked from:** `claude/recursing-hofstadter-8208da` worktree

---

## §1 — What landed in this session

### PR #733 — `docs(session-unity): add universal router prompt section`

- **Issue:** `docs/agent_brief.txt:8` referenced a section in `docs/SESSION_UNITY_PROTOCOL.md` that did NOT exist on `origin/main`. The earlier Cursor session that tried to land it stalled on a dirty worktree (full diagnosis in `old_chat_specs/group1/cursor_universal_router_documentation_i.md`) and never opened a PR.
- **Fix:** Added "Universal router prompt (prompt-building chats)" section after Quick Reference, pointing at `./agent_brief.txt` as the single source of truth (drift-prevention pattern — no template duplication).
- **SHA:** `6858f64fc08467c0870c3c33feb6c7db381444b4`
- **PR:** https://github.com/Ahjan108/phoenix_omega_v4.8/pull/733
- **State at handoff:** OPEN, MERGEABLE, 8 checks running
- **Diff:** +9 / -1, single file
- **Preflight:** push_guard OK · preflight_push.sh OK · health_check.sh = 341 pre-existing stale-upstream warnings (none introduced by this PR)

### PR (this handoff doc) — `docs(handoff): 2026-04-27 router + catalog/pipeline audit`

- This file. Pure documentation; no code, no deletions.

---

## §2 — Catalog planner state of truth (operator question A)

> "Confirm that global catalog planner for pearl prime uses latest marketing with adjusted manga stuff like mecha, fantasy, horror, etc."

**Short answer:** Pearl Prime *books* and the *manga catalog* are two separate systems. The manga catalog IS aligned with the latest marketing as of 2026-04-26, including mecha + dark_fantasy + psychological_horror + sports_competition + supernatural_mystery + sci_fi_cyberpunk + 9 other shells. Pearl Prime books has no genre dimension by design (persona × topic only).

### §2.1 — Pearl Prime books catalog (audiobooks / wellness self-help)

| Item | Value |
|---|---|
| Latest marketing plan | [docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md](AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md) |
| Math codified | 24 brands × 42 books per brand = **1,008 titles per locale** |
| Brand registry | [config/brand_registry.yaml](../config/brand_registry.yaml) — 28 entries (1 EN flagship + 1 EN secondary + 6 base brands × 4 CJK/SG locale variants) |
| Assembly entry-point | [scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py](../scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py) — locale-iterated |
| BookSpec allocation | [scripts/generate_full_catalog.py](../scripts/generate_full_catalog.py) `--plan-only` |
| Render pipeline | [scripts/run_pipeline.py](../scripts/run_pipeline.py) `--pipeline-mode spine` |
| Genre dimension | **NONE** — persona × topic only (wellness substrate is the content) |
| Cross-locale orchestrator | **DOES NOT EXIST** — each locale is a separate invocation |

### §2.2 — Manga catalog (genre-shell embedded wellness)

| Item | Value |
|---|---|
| Strategic core | [docs/GENRE_PORTFOLIO_PLAN.md](GENRE_PORTFOLIO_PLAN.md) (2026-04-23) — 12 strategic shells × 37 brands |
| Per-locale plans | [docs/CJK_CATALOG_PLAN.md](CJK_CATALOG_PLAN.md) (2026-04-22), [docs/US_CATALOG_PLAN.md](US_CATALOG_PLAN.md) (2026-04-23) |
| Synthesis spec | [specs/MANGA_CATALOG_RECONCILIATION_SPEC.md](../specs/MANGA_CATALOG_RECONCILIATION_SPEC.md) v1.1 (2026-04-26) — operator-approved through OQ-9 |
| Live catalog plan | [artifacts/manga/MANGA_FULL_CATALOG_PLAN.md](../artifacts/manga/MANGA_FULL_CATALOG_PLAN.md) — auto-generated; do not hand-edit |
| Brand registry | [config/manga/canonical_brand_list.yaml](../config/manga/canonical_brand_list.yaml) — 37 brands (3 flagship + 16 core + 18 niche), `last_updated: 2026-04-27` |
| Schema | [schemas/manga/series_plan.schema.json](../schemas/manga/series_plan.schema.json) v2.1.0 — 23-genre enum (10 legacy retained + 13 new strategic per spec §4.1) |
| Genres present (15 strategic) | iyashikei, dark_fantasy, psychological_horror, supernatural_mystery, isekai, sci_fi_cyberpunk, psychological_thriller, romance_josei_drama, workplace_drama, action_battle, sports_competition, historical_period, cultivation_martial, school_coming_of_age, **mecha** |
| Locales wired (5) | en_US, ja_JP, zh_TW, zh_CN, ko_KR — `VALID_LOCALES` at [generate_catalog_plan_from_strategic.py:55](../scripts/manga/generate_catalog_plan_from_strategic.py:55) |
| Locales NOT yet wired (3) | es_LA (Latin America), hu_HU (Hungary), zh_HK (Hong Kong) — operator's earlier 8-market list is partially served (see §2.5) |
| series_plan YAMLs | **1,350** under `config/source_of_truth/manga_series_plans/{locale}/` (refined from 1,410 by PR #727) |
| book_plan YAMLs | **18,900** under `config/source_of_truth/manga_book_plans/` |
| Catalog generator | [scripts/manga/generate_catalog_plan_from_strategic.py](../scripts/manga/generate_catalog_plan_from_strategic.py) — reads strategic docs |
| Series-plan generator | [scripts/manga/generate_series_plans_from_catalog.py](../scripts/manga/generate_series_plans_from_catalog.py) — reads catalog plan |
| Book-plan generator | [scripts/manga/generate_book_plans_from_series.py](../scripts/manga/generate_book_plans_from_series.py) — reads series_plans |

### §2.3 — How the catalog distribution is actually computed (verified by Pearl_Dev mid-session)

The catalog plan generator does NOT just enumerate genres — it allocates per-brand × per-genre series counts via a **4-leg weighted blend** at [generate_catalog_plan_from_strategic.py:122-127](../scripts/manga/generate_catalog_plan_from_strategic.py:122):

| Leg | Weight | Source |
|---|---|---|
| `strategic` | 0.20 | GENRE_PORTFOLIO_PLAN per-brand %-allocations |
| `metadata` | 0.05 | Brand-description tag affinities (`derive_brand_tags()` + `TAG_GENRE_AFFINITY`, 40+ tags) |
| **`market_revenue`** | **0.70 (DOMINANT)** | Sales-evidenced per-genre revenue weights |
| `baseline` | 0.05 | Uniform floor so every genre gets ≥1 |

Per-genre revenue weights ([:148-175](../scripts/manga/generate_catalog_plan_from_strategic.py:148)) are sales-evidenced, e.g.:
- One Piece 530M + Naruto 250M + Dragon Ball 260M + Demon Slayer 150M → `action_battle 1.50`
- Evangelion $16B franchise → `mecha 1.40`
- Berserk 70M + Frieren 30M → `dark_fantasy 1.10`
- Tokyo Ghoul 47M (CAGR 18.74%) → `psychological_horror 0.85`
- Iyashikei `0.25` (loyalty/anchor tier, not revenue)

This means the catalog isn't just "use these genres" — it's revenue-weighted per market, tilted by each brand's metadata tags so every brand's allocation is provably distinct from every other brand's.

### §2.4 — Reconciliation history (manga, recent)

- PR #687 — spec v1.0 → v1.1 (incorporates operator OQ-1..OQ-9 resolutions)
- PR #688 — Phase 2X.1 catalog plan generator
- PR #693 / #694 — brand-metadata-weighted then revenue-weighted genre distribution
- **PR #696** (2026-04-26) — **Phase 2X.4 atomic** (operator-approved "go atomic"): schema v2.0.0 → v2.1.0 + 848 stale YAML deletes + 1,410 series_plan regen
- PR #698 — Phase 2X.4b: 19,740 book_plan regen
- PR #727 — generator spec compliance: per-brand × per-genre % allocations (1,410 → 1,350)
- **PR #734** (mid-session, Pearl_Dev) — TTS hardening: 7 files, sha `4f13134d36`, OPEN. Sample remap stillness_press en-US ElevenLabs → `edge_tts en-US-GuyNeural`; hu_HU ElevenLabs → `edge_tts hu-HU-NoemiNeural`; deletes a stale "ElevenLabs mandatory for hu" hard-rule. Auditor: 0 BLOCK / 0 WARN.

### §2.5 — Locale gap (operator's 8-market list vs what's wired)

| Market | Locale code | Wired in catalog generator? | Notes |
|---|---|---|---|
| USA | `en_US` | ✅ | |
| Japan | `ja_JP` | ✅ | |
| Taiwan | `zh_TW` | ✅ | |
| China | `zh_CN` | ✅ | gray-zone with full AI disclosure (D-19) |
| Korea | `ko_KR` | ✅ | render + held pending Korea AI Act clarity (D-18) |
| Hong Kong | `zh_HK` | ❌ | DeepSeek covers same as zh_TW; needs `VALID_LOCALES` extension + per-locale format mix |
| Latin America | `es_LA` | ❌ | needs `LATAM_CATALOG_PLAN.md` + format mix + translation provider routing |
| Hungary | `hu_HU` | ❌ | Edge TTS covers `hu-HU-NoemiNeural` (PR #734); translation-provider routing not yet picked |

**Pearl_Dev offer on the table:** spawn a Locale Extension agent for es_LA + hu_HU + zh_HK after the 4 doc sweeps. Operator decision needed.

### §2.6 — Confirmation matrix vs the operator's question

| Operator's check | Status | Evidence |
|---|---|---|
| Mecha | ✅ Present | schema enum line 146; catalog plan |
| Fantasy (dark_fantasy) | ✅ Present | schema + catalog + GENRE_PORTFOLIO_PLAN |
| Horror (psychological_horror) | ✅ Present | schema + catalog + GENRE_PORTFOLIO_PLAN |
| Sports (sports_competition) | ✅ Present | schema + catalog + GENRE_PORTFOLIO_PLAN |
| Romance (romance_josei_drama) | ✅ Present | schema + catalog + GENRE_PORTFOLIO_PLAN |
| Latest marketing wired in | ✅ | `generate_catalog_plan_from_strategic.py` reads GENRE_PORTFOLIO + CJK + US plans directly |
| 5 locales (incl. ko_KR) | ✅ | schema + catalog header |

---

## §3 — Pipeline assembler state of truth (operator question B)

> "Confirm that the planner and assembler use 12ch × 10sec × 5variations + bestseller injection and logic."

**Short answer:** 10 sections per chapter is HARD. STORY at sections 2/5/9 is HARD. Bestseller structure assignment is HARD. 12 chapters is SOFT default. **"5 variants per section" is NOT what the code enforces** — read §3.2 below.

### §3.1 — Confirmed structural rules

| Rule | File:Line | Enforcement |
|---|---|---|
| **10 sections per chapter** | [phoenix_v4/planning/beatmap_compile.py:42](../phoenix_v4/planning/beatmap_compile.py:42) | HARD — `SOMATIC_10_SLOT_GRID` for `SOMATIC_FULL_RUNTIME_FORMATS = {standard_book, extended_book_2h, deep_book_4h, deep_book_6h}` |
| **STORY at sections 2/5/9** | [phoenix_v4/planning/story_planner.py:68](../phoenix_v4/planning/story_planner.py:68) | HARD — `SCENE_SECTION_INDICES = (2, 5, 9)`; gated at `enrichment_select.py:901-907` |
| **4-phase narrative arc** | [phoenix_v4/planning/story_planner.py:60](../phoenix_v4/planning/story_planner.py:60) | HARDSHIP ch1-3 / HELP ch4-6 / HEALING ch7-9 / HOPE ch10-12 |
| **12 chapters** | [phoenix_v4/planning/chapter_planner.py](../phoenix_v4/planning/chapter_planner.py) (default) | SOFT — configurable per format_plan; default 12 |
| **Bestseller structure assignment** | [phoenix_v4/planning/chapter_planner.py:196](../phoenix_v4/planning/chapter_planner.py:196) `assign_bestseller_structures` | HARD — SHA256-seeded; 12 structures; max 3 consecutive identical |
| **PIVOT/PERMISSION/TAKEAWAY/THREAD/COMPRESSION beat slot injection** | [phoenix_v4/planning/chapter_planner.py:316](../phoenix_v4/planning/chapter_planner.py:316) `_augment_slots_for_bestseller_structure` + [bestseller_structure_map.py:24](../phoenix_v4/planning/bestseller_structure_map.py:24) `BESTSELLER_BEAT_STEPS` | Slot rows augmented per chapter's assigned bestseller_structure |
| Beat → atom routing | [docs/BESTSELLER_ATOM_ROUTING.md](BESTSELLER_ATOM_ROUTING.md) | PARTIAL — `BookSlotTracker` is a no-op placeholder per BESTSELLER_ATOM_ROUTING.md |

### §3.2 — Important correction: "5 variants per section"

**This is NOT a structural rule the code enforces.** What actually happens:

1. Atom registries (e.g., `registry/{topic}.yaml`) CAN have multiple variants per section type.
2. For each slot in a chapter, **ONE** variant is chosen deterministically via `_deterministic_index(seed_key, len(variants))` at [enrichment_select.py:671](../phoenix_v4/planning/enrichment_select.py:671).
3. For format `extended_book_2h`, up to **5 EXTRA registry-variant chunks** can be appended to the chosen slot's body (`_max_extra_chunks_for_format` at [enrichment_select.py:506](../phoenix_v4/planning/enrichment_select.py:506)+).
4. So "5" exists in code as a chunk-multiplier cap, NOT as a per-section variant count.

**If the intent is to emit 5 fully independent variants per section** (each composed with a separate seed, all five rendered for downstream selection or A/B), that is **a NEW emission mode that does not exist today**. Would require a Pearl_Architect spec PR.

### §3.3 — End-to-end evidence

- Recent artifact: `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/standard_book/budget.json` — 12 chapters × chapter_1 with 10 base slots (HOOK, SCENE, REFLECTION, EXERCISE, SCENE, TEACHER_DOCTRINE, REFLECTION, EXERCISE, SCENE, INTEGRATION) + bestseller-structure metadata.
- Move 4 30-book representative sweep: PASSED 90% per prior session.

---

## §4 — Documentation drift identified (NOT fixed in this session)

I deliberately did NOT delete or modify any of the below — they are either chartered for atomic cleanup elsewhere, or require operator clarification first.

1. **`docs/LOCALE_CATALOG_MARKETING_PLAN.md` — DOES NOT EXIST.**
   The prior session's summary referenced it; PR #686 renamed it to [docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md](AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md). Any future references to the old name should resolve to the new one.

2. **"800 books per brand" — DOES NOT EXIST anywhere in the repo.**
   - Real numbers found: 42 books/brand (audiobook) · 14 episodes/series with 5/9/16 series-per-brand (manga) · 1,000+ books/author capacity ([docs/PEN_NAME_AUTHOR_SYSTEM.md:11](PEN_NAME_AUTHOR_SYSTEM.md))
   - **Action needed:** operator clarify whether 800/brand was a future target proposal, or a misremember.

3. **`scripts/manga/generate_series_plans_from_catalog.py:44-49`** still has `VALID_LOCALES = 4` (no ko_KR) and `VALID_GENRES = 10 legacy slugs`. PR #696 modified this file (added strand heading regex) but the constants themselves I did not verify post-modification. **Action needed:** Pearl_Architect verify constants align with current schema (which is 5 locales + 23-genre enum).

4. **Phase 2X.4 atomic cutover ALREADY HAPPENED** — prior session's notion that it was "ready to author when Pearl_Dev capacity opens" was outdated; PR #696 shipped on 2026-04-26. Update PEARL_ARCHITECT_STATE.md and any blockers/queued lists accordingly.

5. **Pearl Prime cross-locale orchestrator** — does not exist; each locale is a separate `assemble_full_catalog_qa.py` invocation. The prior session's "PR-B worker pool" 3-PR plan addresses this if/when operator wants parallelism.

6. **Worktree contention incident (logged for the record).** During this session a parallel TTS-hardening agent landed its commit on a sibling agent's branch by mistake, then cherry-picked + reset to recover. State was preserved, but the lesson per Pearl_Dev: **all future agent spawns should use `isolation: "worktree"`** so each gets an isolated git worktree. Eliminates the cross-agent file-edit and branch-reset class of bugs.

---

## §5 — Queued work (carried forward)

From prior session, unchanged:

- **Pearl_Dev**: B2 backend pivot PR (adapt R2 scripts to S3-API-backend-agnostic; add 5 B2 entries to `scripts/ci/integration_env_registry.py`; B2 section in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`)
- **Pearl_Dev**: Teacher photo avatars on brand-wizard pages (replace first-initial icons; convert ahjan.HEIC; uses `teacher_pics/`)
- **Pearl_Dev + Pearl_Localization**: New `wizard-teacher.html` step 1 across 4 locales
- **Pearl_Dev**: AGENTS.md at repo root + CLAUDE.md cross-reference
- **Operator decision needed**: spawn Locale Extension agent for `es_LA` + `hu_HU` + `zh_HK` (Pearl_Dev offered)
- **Operator**: WEBTOON Canvas creator account + series setup for ep_001 manual upload
- **Pearl_Architect (if 800/brand was real intent)**: codify per-brand book target reconciling audiobook / manga / author-capacity numbers
- **Pearl_Localization**: Move 5 rolling enhancement (per-persona × topic story_atoms/anchored authoring)
- **Pearl_Prime**: midlife_women master_arcs authoring (`ws_midlife_women_arc_authoring_20260427`)

---

## §6 — Files read this session (audit trail)

- `old_chat_specs/group1/cursor_universal_router_documentation_i.md`
- `docs/SESSION_UNITY_PROTOCOL.md` · `docs/agent_brief.txt` · `docs/DOCS_INDEX.md`
- `docs/GENRE_PORTFOLIO_PLAN.md` · `docs/US_CATALOG_PLAN.md` · `docs/AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md`
- `specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`
- `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`
- `schemas/manga/series_plan.schema.json`
- `phoenix_v4/planning/beatmap_compile.py` · `story_planner.py` · `enrichment_select.py` · `chapter_planner.py` · `bestseller_structure_map.py`
- `scripts/pearl_prime_multilingual/assemble_full_catalog_qa.py`
- `scripts/manga/build_manga_catalog.py` · `generate_catalog_plan_from_strategic.py` · `generate_series_plans_from_catalog.py`
- `config/brand_registry.yaml` · `config/manga/canonical_brand_list.yaml`

---

## §7 — Next session entry point

1. Merge PR #733 if checks pass.
2. Merge this handoff PR.
3. Triage the queued work in §5 — recommended next concrete action: clarify "800/brand" vs the real numbers, then either codify a corrected target (Pearl_Architect doc PR) or pick the next queued item.
