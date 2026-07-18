# Phoenix Omega — Whole-System Status Audit

**Date:** 2026-06-12 (dir tag `20260611`) · **Auditor:** Pearl_Architect (system-audit mode) · **Mode:** read-only, evidence-grounded
**Base:** origin/main @ `99ee0ba40` · **Scope:** books · podcasts · manga · audiobooks · video + the atom corpus + CJK
**Honesty mandate:** every coverage % is backed by a measured count, a PR, or a rendered-output count. BUILT / SPEC'D / PROPOSED / BROKEN labelled per component. No inflation.

---

## 0. TL;DR — the one-paragraph truth

Phoenix Omega has, as of 2026-W22, shipped **exactly one real proof-of-life artifact per content type for one brand (stillness_press) for one week** — book EPUB (#1344), podcast 55s MP3 (#1347), audiobook 6.5-min M4B (#1346), manga PDF+WEBTOON (#1349), all at **$0**. That is a genuine milestone (the four-axis pipeline *can* produce real artifacts end-to-end), but it is **proof-of-life, not production**. Catalog-scale output is **0–3% per content type**, and four of the five pipelines have a **broken or unwired last mile**. The atom corpus is **NOT 100%** — but it is **~97.7% on the active en-US axis** (not the 0.1% a worktree gap-matrix implies), and **CJK atom coverage is ~85% for ja-JP/zh-TW — emphatically not "single digits."** The real blockers are **last-mile wiring + the teacher-bank overlay gap + CJK voice/infra (not CJK atoms).**

---

## 1. ATOM COVERAGE — "is it actually 100%?"

### Direct answer: **NO. It is not 100%. The real, intent-weighted number is ~97.7% on the active en-US axis (~93% at the 3-variant floor) — NOT 0.1%, and NOT 100%.**

**Live measurement (main tree @ `99ee0ba40`, measured this session):**

| Axis | Measured | Method |
|---|---|---|
| Total `CANONICAL.txt` on disk | **16,292** | `find atoms -name CANONICAL.txt` |
| en-US base (no `locales/`) | 4,879 | — |
| Under CJK `locales/` | 11,413 | — |
| **en-US Phase-A coverage** (14 personas × 15 core topics × 6 persona-keyed types = 1,260 cells) | **1,231 / 1,260 = 97.7%** (≥1 variant) | direct per-cell `isfile` check |
| en-US at **≥3-variant floor** | **~1,176 / 1,260 = ~93%** | per 2026-06-06 SSOT summary |
| en-US cells empty | **29** (midlife_women 15, educators 7, nyc_executives 7) | direct check |

The 29 empty en-US cells are concentrated in 3 personas; `midlife_women` is *additionally* blocked by `master_arcs = 0` (an arc file, not atoms — `ws_midlife_women_arc_authoring_20260427`).

### ⚠️ Why the "0.1% / 62,409-variant" figure is a measurement artifact — DO NOT use it

A gap matrix `pearl_prime_atom_100pct_gap_matrix_20260606.tsv` + `PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` exist **only in sibling worktrees (`.claude/worktrees/*`), NOT on main** (unmerged, cap `ATOM-100PCT-COVERAGE-SSOT-V1-01`). It reports `current=35 / required=62,409 / coverage=0.1%`. That number is **not the real coverage** for two reasons:

1. **Aspirational denominator.** The 62,409-variant target is a theoretical **13-locale × full-grid** (adds 6 EU locales + zh-HK/zh-SG + variant enrichment). **72% of its rows (14,968 / 20,803, 44,904 variants) are tier P5 = "SOFT / operator-deferred"** per the SSOT itself.
2. **False-zero counter.** Its `current_variants` column reports **en-US = 0 and ja-JP = 0**, while **4,879 en-US and 4,241 ja-JP `CANONICAL.txt` files demonstrably exist on disk** (I read real, fluent ja-JP/zh-TW/zh-CN/ko-KR translations). The matrix's own operator-facing summary contradicts the TSV: it says *"locale coverage is **full** for ja-JP + zh-TW + zh-CN + ko-KR + zh-HK + zh-SG (CJK6)"* and *"~93% en-US Phase-A."* The TSV `current` counter keys on a new contract the 16k existing atoms don't match → it under-counts by ~16,000.

**Honest framing:** against the **active production intent** (en-US Phase-A engine atoms) coverage is **~93–98%**. Against an **aspirational 13-locale enrichment grid**, the *remaining authoring* is ~26,618 estimated hours — but most of that (P5) is explicitly operator-deferred, not "missing from 100%."

### The real atom gap that matters: the teacher-bank overlay (Class-2 types)

Class-2 overlay types (`QUOTE` / `TEACHER_DOCTRINE` / `PERMISSION`) are **0% persona-keyed by design** (per `QUOTE-ATOM-ROUTING-01`, they route via `SOURCE_OF_TRUTH/teacher_banks/`). But the teacher-bank backing is a **near-total gap** (verified per-teacher this session):

- **QUOTE = 0 for ALL 15 teachers** (no `approved_atoms/QUOTE/` dir exists for any teacher).
- **TEACHER_DOCTRINE = 19 for ahjan only**; 0 for the other 14 teachers.
- **CJK-localized teacher atoms exist only for `adi_da`** (95 atoms × 6 CJK locales); the other 14 teachers have **no `approved_atoms_localized/` at all**.

This is the root cause of the **F3 "off-doctrine teacher content overrun"** defect documented in the book acceptance verdict — every teacher-mode book draws teacher-voice content from generic banks. **This, not the persona-keyed engine atoms, is the #1 atom-side blocker for bestseller-grade + CJK books.**

---

## 2. CJK STATUS — "and CJK?"

### Direct answer: **CJK is far stronger than "single digits" for the two flagship locales (ja-JP ~87%, zh-TW ~85% atoms) — but CJK *production* across content types is gated on voice corpora, infra, and teacher-bank localization, not on atoms.**

**CJK atom coverage (Phase-A 1,260-cell grid, measured live):**

| Locale | Coverage | Note |
|---|---|---|
| ja-JP | **1,093/1,260 = 86.7%** | real fluent translations (verified) |
| zh-TW | **1,068/1,260 = 84.8%** | real (localized headings, e.g. 練習 = "exercise") |
| zh-CN | 347/1,260 = 27.5% | partial |
| zh-HK / zh-SG | 76/1,260 = 6.0% each | thin |
| ko-KR | 61/1,260 = 4.8% | thin |
| EU (de/fr/es-US/es-ES/it/hu) | **0%** | not started |

**CJK production by content type (what ships in CJK today vs en-US):**

| Type | CJK today | Gate |
|---|---|---|
| Books | persona-keyed atoms localized (~85% ja-JP/zh-TW); **teacher-bank atoms localized for `adi_da` only** → CJK teacher-mode books can't ship at parity. Also inherits en-US's ~0% trade-pub-readiness. | teacher-bank CJK localization (14 teachers) + en-US craft gates |
| Audiobooks | 4 CJK ch-1 samples rendered (zh-CN/ja-JP/ko-KR) via **CosyVoice2 built-in CJK presets** | the 40 "CJK reference clips" are **all LibriSpeech English stand-ins**; no locale-native corpora on disk → persona-clone CJK voices not real. Needs JVS/CSS10/KSS (licensing not started) |
| Manga | **0 CJK episodes rendered**; ep_001 `text_by_locale` populated but no persisted CJK render | zh_TW/zh_CN `blocked_lora`; ja-JP needs ~366 atoms + LINE Manga connector (not built) |
| Podcasts | **0 CJK episodes** | CosyVoice2 endpoint (`COSYVOICE_URL`) unprovisioned; Edge-TTS fallback would emit English voice for CJK (bug) |
| Video | 5 bespoke JA Starseed MP4s via **macOS `say -v Kyoko`** (a hack) | canonical CosyVoice2 CJK wiring is **docs-only**; `run_voice_synthesis.py` missing |

**⚠️ en-US-model leakage into CJK (flagged):** book/audiobook **duration labels are word-count-based (150 WPM)** — a word model. CJK is **character-based**; word-count duration math is invalid for CJK and the current hand-set labels don't model CJK at all. Any duration-derivation fix (see §3.1) **must be char-aware for CJK**.

**The CJK headline:** for ja-JP and zh-TW the **atoms are ~85% done** — the CJK bottleneck is **voice corpora + CosyVoice2 endpoint + teacher-bank localization + manga LoRA**, i.e. **data/infra-gated, not atom-gated.** Provisioning **one shared CosyVoice2 endpoint** unblocks CJK across podcast + audiobook + video simultaneously.

---

## 3. PER-SUBSYSTEM STATUS (the 5 content types)

> Cross-cutting evidence: Brand-Admin-V2 Phase-2 P0 shipped one real MVP per axis for `stillness_press × 2026-W22`, all $0: book #1344, podcast #1347, audiobook #1346, manga #1349, cron #1348. Path X canon = 37 manga brands; book pipeline 24×13=312; music 38+.

### 3.1 BOOKS / Pearl Prime — **STATUS: PARTIAL** (pipeline runs end-to-end; **~0% ship at trade-pub register today**)

**What's producing:** the `spine` pipeline assembles + renders books end-to-end. May-2026 catalog audit (`artifacts/qa/en_us_catalog_bestseller_audit_2026-05-13.md`): **13% (26/200) reach render**; **87% (174/200) blocked pre-render at the `scene_anchor_density` gate**. Of the 26 rendered, all pass Layer-1 machine gates (ONTGP mean 0.579, range 0.41–0.68).

**The "27/30 bestseller-grade" claim was INFLATED (honesty flag confirmed):** the Move-4 sweep (`artifacts/qa/move4_2026_04_26/assembly_summary.json`) ran under `quality_profile: "draft"`, `gates_hard: false`, and **every book has `release_band: "Reject"`**. The "BESTSELLER" grade in its coverage doc is a loose engine-bank heuristic, not the production scorecard. The acceptance verdict (`ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md`) confirms a book that **passes all Layer-1 gates still FAILS Layer-3 human read 2/3 chapters** (defects F1 templated-mechanism blocks, F2 broken slot fragments, F3 off-doctrine teacher overrun, F4 verbatim closing repeats).

**Coverage:** **~0% trade-pub-shippable today** · 13% reach render · 97.7% have atoms.

**Craft gates — BUILT vs SPEC'D vs PROPOSED:**
- BUILT + wired: `chapter_flow_gate`, `bestseller_craft_gate`, `ei_v2` scorer, `book_quality_gate`, `memorable_line_gate`, `transformation_heatmap`.
- **BUILT but NOT WIRED:** `register_gate.py` (904 lines, detectors F1–F7 + F11 implemented, F8 deferred) — **not imported into `run_pipeline.py`** (`ws_register_gate_implementation_20260518` = PROPOSED).
- **MISSING:** `ship_readiness_aggregator.py` (`ws_ship_readiness_aggregator_20260518` = PROPOSED).
- **PROPOSED (not built):** integration-pacing / dwell-beat craft gate (operator's #1 craft concern; research extends PR #1509), voice-zone gate (C2 Option B, awaiting ratification).
- **SPEC'D (not built):** duration-label derivation fix — `standard_book` "55 min" is really **~2h23m** at 150 WPM; **8/10 formats exceed ±15% tolerance**; `duration_minutes` is hand-set, never computed (`artifacts/qa/duration_correctness_audit_20260611/`). No ws opened.
- **Silent-routing risk:** `scripts/run_pipeline.py` `--pipeline-mode` default is still `registry` (legacy), not `spine` (canonical) — `ws_pipeline_mode_default_flip_to_spine_20260518` = PROPOSED.

**Teacher-bank overlay gap:** QUOTE=0 (all 15), TEACHER_DOCTRINE=19 (ahjan only) — see §1.

**CI:** Core tests GREEN on main @`15b46e37a`; **Release gates FAIL** (phase 3 open, `ws_ci_recovery_release_gates`).

### 3.2 PODCASTS — **STATUS: PARTIAL** (subsystem authority status = "proposed"; **2.7%, 1/37 brands**)

**Producing:** **2 real MP3s** — the same ~55s episode duped to `spotify_podcast/` + `apple_podcasts/` for `stillness_press × 2026-W22`, en-US only. **36/37 brands have only empty `.zip` scaffolds.** (An earlier W15 pilot rendered a full 20-min + 4.75-min episode but those binaries are **not tracked in git**.)

**BUILT vs SPEC'D:**
- BUILT: `assemble_podcast_episode.py`, `render_podcast_audio.py` (Edge-TTS confirmed working, $0), `generate_podcast_feed.py` (RSS), `run_podcast_pipeline.py` orchestrator, `upload_podcast_to_r2.py` (untested — all runs `--skip-upload`).
- **PARTIAL:** weekly package integration creates directory scaffolds but **does not invoke the podcast pipeline per brand**.
- **BROKEN/limited:** `podcast-weekly.yml` cron is **hardcoded to `stillness_press`** (and fires 10:00 UTC, not the spec'd 9:00) — does not loop 37 brands.
- **SPEC'D:** brand-admin API endpoint + UI tab; per-brand credential fields.
- **CJK:** 0 episodes; CosyVoice2 branch exists but `COSYVOICE_URL` endpoint unprovisioned.

**Coverage:** **2.7% (1/37 brands), 1 week, en-US only.**

### 3.3 MANGA — **STATUS: PARTIAL** (**1 episode, 1/37 brands; V4 single-model, NOT V2 multi-model**)

**What's actually RENDERED:** **ep_001 "The Alarm Is Lying"** (stillness_press/ahjan/anxiety) = **35 panels** rendered + composited via **V4 Qwen-Image single-model** (`artifacts/manga/.../composed_v4_qwen/ep_001/`). This is the **only real episode**. The MVP #1349 **reused those V4 panels** ("$0 RunComfy"). Everything else found is character-reference art, covers, **64×64 fixture stubs**, or brand-wizard showcase assets — **not episode panels**.

**Multi-model V2 — mostly PROPOSED:**
- ComfyUI workflow JSONs exist for Qwen-Image (faces), FLUX (bg), Animagine XL 4.0 (panels), PuLID-FLUX (face-lock) — **but no episode has rendered through the layered pipeline.**
- ai-toolkit **LoRA training NOT implemented** (`train_character_lora.py` not committed; Phase C PROPOSED).
- **All 6 V2 phases (A–E) = PROPOSED**, pending operator-go on Phase A (`MANGA-LAYERED-PIPELINE-V2-01`).
- A V4 compositing flaw (only **2/35 panels placed the subject correctly** — no shared L0+L2 coordinate system) triggered a **V5 "Qwen-Image-Layered" pivot, itself feasibility-only** (`MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7).

**CJK manga:** **0 rendered episodes**; zh_TW/zh_CN `blocked_lora` (`ws_zh_manga_blocked_lora_followup_20260511`); ja-JP needs ~366 atoms + a **LINE Manga Indies connector (not built)**. **Pearl_Conductor v3** full-queue (~19-day backlog) is **queued/blocked** on generator-extend (12→37 brands) + 25-brand themes + blocked_lora. **ep_002** gated on a pose-library extension (runnable).

**Coverage:** **2.7% by episode (1/37 brands)**; ~37% of brands have character-reference art only.

### 3.4 AUDIOBOOKS — **STATUS: PARTIAL** (**0.3%, 1/312 books**)

**Producing:** **1 complete M4B** (stillness_press W22, 6.5 min, local CosyVoice2, $0) + **13 chapter-1 showcase samples** (9 brands; en-US/zh-CN/ja-JP/ko-KR) via CosyVoice2 **built-in presets**. The book-comparator pipeline (`run_comparator_loop.py`) is **BUILT but never run against the catalog**; spec status = "pre-production, 11/12, 1 blocker = staging run."

**TTS stack:** CosyVoice2 (local, $0) = de-facto default, **BUILT**. **Inconsistency:** `config/tts/locale_voice_routing.yaml` still routes **en-US → ElevenLabs first** (conflicts with the $0 MVP). **Piper = absent.** Edge-TTS = fallback.

**480 narrator slots = CONFIG ONLY** (`narrator_voice_assignments.yaml`, 100k lines) — **0 rendered via them**; the demo samples used the simpler built-in-preset path. The **40 "CJK reference clips" are all LibriSpeech English stand-ins** (`assets/tts/reference_clips/` doesn't exist on disk); ECAPA pairwise (PR #313) is a repo-level config metric, not per-sample verified.

**Coverage:** **0.3% (1/312 books)** have a packaged audiobook.

### 3.5 VIDEO — **STATUS: PARTIAL / BROKEN** (**0 canonical-pipeline videos; the productionization gap is real**)

**Producing:** **30 real MP4s — but ALL bespoke one-offs**: 21 ahjan "Starseed" YouTube (EN+JA, via macOS `say`), 6 TikTok body-awareness, 2 smoke renders, 1 staging bundle. The **canonical `scripts/video/run_pipeline.py` produces 0 MP4** — `--skip-render` defaults `True` ("Phase 1 = video-only/silent" by design); the 13 pre-render stages emit clean JSON but no video.

**Broken last mile (this is the "needs productionization" the operator flagged):**
- **`run_voice_synthesis.py` is MISSING** — the `--voice` flag calls a non-existent file. Canonical narration (EN *and* CJK) is broken.
- **Upload CI BROKEN:** `video-daily-publish.yml` passes `--brand-suffix SP` but `run_upload.py` has no such arg → never succeeded (zero upload logs).
- **No generation cron** — only a (broken) upload cron; nothing renders on a schedule.
- **No Brand-Admin-V2 video axis** — video was the **one format excluded** from the 4-axis MVP.
- CJK video = bespoke macOS `say`; canonical CosyVoice2 CJK wiring is **docs-only**. Teacher×Manga 30s V1 = **PROPOSED** (script YAMLs only, gated on operator Q1–Q4).

**Coverage:** **0% via the canonical pipeline** (bespoke one-offs only).

---

## 4. The cross-cutting pattern

1. **"MVP-shipped-once" ≠ "producing."** Five real artifacts exist for one brand/week. Catalog-scale = 0–3% everywhere.
2. **Last-mile wiring is the recurring failure mode**, not missing architecture: books (register gate built-not-wired), podcast (cron hardcoded to 1 brand), video (`run_voice_synthesis.py` missing + upload arg mismatch), audiobook (comparator loop never run), manga (`queue_panel_renders.py` uncommitted; ep_001 not published).
3. **The atom corpus is the *least* of the problems** — ~98% en-US, ~85% ja-JP/zh-TW. The bottlenecks are downstream: craft gates, teacher-bank overlay, voice infra, manga LoRA.
4. **CJK is data/infra-gated, not atom-gated** for ja-JP/zh-TW. One CosyVoice2 endpoint unblocks 3 content types.

See `ROADMAP_TO_100.md` for the prioritized path and the system critical path, and `system_coverage.tsv` for the machine-readable matrix.

---

## 5. Evidence index (key paths/counts/PRs verified this session)

- Atom live counts: `find atoms -name CANONICAL.txt` = 16,292; per-locale via `awk` on `/locales/`; en-US Phase-A 1,231/1,260 via per-cell `isfile`.
- Atom samples (real translations): `atoms/gen_x_sandwich/financial_anxiety/PIVOT/locales/ja-JP/CANONICAL.txt`, `atoms/working_parents/grief/STORY/locales/ko-KR/CANONICAL.txt`, `atoms/first_responders/social_anxiety/EXERCISE/locales/zh-TW/CANONICAL.txt`.
- Gap matrix (worktree-only, unmerged): `.claude/worktrees/music-mode-v2-20260611/artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv` + `pearl_prime_atom_100pct_summary_20260606.md` (the "full CJK6 / 93% en-US" prose that contradicts the TSV's `current=35`).
- Books: `artifacts/qa/move4_2026_04_26/assembly_summary.json` (draft profile, all Reject); `artifacts/qa/en_us_catalog_bestseller_audit_2026-05-13.md` (13% render); `ACCEPTANCE_VERDICT_2hr_ahjan_genz_anxiety_2026-05-18.md` (Layer-3 FAIL); `phoenix_v4/quality/register_gate.py` (built-not-wired); `scripts/run_pipeline.py` (`--pipeline-mode` default registry).
- Teacher banks: `SOURCE_OF_TRUTH/teacher_banks/*` — QUOTE=0 all 15, TEACHER_DOCTRINE=19 ahjan only; `adi_da/approved_atoms_localized/` only CJK-localized teacher.
- Podcast: `artifacts/weekly_packages/stillness_press/2026-W22/spotify_podcast/ep01_*.mp3`; `.github/workflows/podcast-weekly.yml` (cron `0 10 * * 1`, hardcoded stillness_press); PR #320, #1347.
- Manga: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/` (35 panels); `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7 (2/35 placement flaw); PR #1349.
- Audiobook: `artifacts/weekly_packages/stillness_press/2026-W22/audiobook/*.m4b`; `artifacts/audiobook_samples/*.mp3` (13); `config/tts/narrator_voice_assignments.yaml` (480, config-only); `config/tts/voice_clone_reference_library.yaml` (40 Libri stand-ins); PR #313, #1346.
- Video: `scripts/video/run_pipeline.py` (`--skip-render` default True; calls missing `run_voice_synthesis.py`); `.github/workflows/video-daily-publish.yml` (`--brand-suffix` mismatch); `artifacts/video/yt_starseed_ahjan_update_20260610/` (21 bespoke MP4s); `artifacts/video/teacher_30s_v1/` (script YAMLs only); PR #354.
