# Pearl Prime 100% Production Audit — MASTER

**Date:** 2026-07-10  
**Agent:** Pearl_PM  
**Project:** `proj_state_convergence_20260328`  
**Live anchor:** `origin/main` @ `4067366556fedfd99913fbd3806d78af53d32b5a`  
**Supersedes:** none (first books-first 100% audit at this path)  
**Consumes as evidence (does not duplicate):** PR #5295 full-system redundancy sweep; PR #4861 best-path enforcement audit; PR #5206 bestseller conformance audit

---

## 1. Books-First Verdict

**Pearl Prime books are NOT production-ready at catalog scale.**

| Surface | Acceptance layer (live `origin/main`) | Readable sellable artifact? |
|---|---|---|
| Flagship composite regular (`gen_z_professionals × anxiety`, `extended_book_2h`) | **PROVEN-AT-BAR** (OPD-20260707-FLAGSHIP-L4) | Yes — full 12-chapter book; byte-frozen goldens on main |
| Composite regular catalog (Waystream + 26 brands) | **system working** for 4 generalization cells; **path broken** for thin-persona arc-seeded cells | **1 catalog EPUB** assembled + GHL attach (#1947); ~1,519 **listings** ≠ readable books |
| Teacher mode | **CODE-WIRED** + CI gates PASS; per-teacher **EXECUTED-REAL** varies | Teacher-sample EPUBs exist (~138 `.epub` on main incl. samples); no catalog-scale teacher EPUB wave |
| Music mode | **CONFIG-EXISTS** / **CODE-WIRED**; **REAL-MUSICIAN-CONTENT-EMPTY** | Zero music-mode catalog books shipped |
| Localized books (13 non-en-US locales) | **RESEARCHED** + planning pack merged (#5480); **0% atom translation execution on main** | Zero locale-native sellable Pearl Prime catalog EPUBs beyond ja sample EPUBs in brand1_deep tree |

**One-line verdict:** The pipeline **works** and one flagship cell is **PROVEN-AT-BAR**, but **100% production** requires scaling **readable EPUBs + atom depth + translation + proof** across personas/topics/locales — not more listings.

**Top blocker:** Catalog-scale EPUB assembly is blocked on **thin-persona engine-keyed STORY pool gaps** (`educators` / `nyc_executives` → `NO_STORY_POOL` at tuple-viability preflight) plus **~20,773 atom matrix cells at 0 variants** per gap matrix SSOT.

---

## 2. What 100% Production Means

For Pearl Prime **books-first**, 100% production means:

1. **Composite regular mode:** Every production-profile catalog cell that appears in storefront/GHL has a **register-PASS EPUB** that passes Layer 1–3 acceptance (`PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md`) and is attachable to marketing feed — not merely a listing YAML.
2. **Teacher mode:** Each onboarded teacher can compile **≥1 F006 arc** end-to-end with `teacher_mode=true`, coverage gate PASS, no placeholders, and a shipped EPUB proof per priority brand/locale.
3. **Music mode:** Phase A gate in `MUSIC_MODE_V2_PRODUCTION_READINESS_SPEC.md` §4 — first real musician, 6 slot pools at SPEC-739 floor, smoke book + diversity CI PASS + WAV or accepted Phase B deferral.
4. **Atoms:** Phase A en-US matrix per `PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md` — 1,890 cells × ≥3 variants (5,670 atoms minimum); engine-keyed STORY banks for all spine-buildable personas.
5. **Translation:** Phase B–D locale waves — translated atom trees for ja-JP, zh-TW, zh-CN, ko-KR, then extended locales; not skeleton catalog PRs alone.
6. **Formats/durations:** All 22 runtime formats in `format_registry.yaml` have derived duration fields, CI contract PASS, and ≥1 proof render per format family where catalog plans reference them.
7. **Proof:** Layer 4 blind-read for **≥N flagship-adjacent cells** before claiming "bestseller register" at catalog scale; gate-PASS alone is **structurally clear** at most.
8. **Manga:** Not a books launch prerequisite; required only where product bundles books+manga (explicitly **not** blocking book EPUB scale today).

---

## 3. Current Acceptance Layer By Surface

Six-layer manga taxonomy + Pearl Prime scorecard layers used consistently:

| Surface | Layer | Evidence on `origin/main` |
|---|---|---|
| Flagship book | **PROVEN-AT-BAR** | `artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt`; OPD-20260707-FLAGSHIP-L4 |
| Flagship ch1 preview pack | **PROVEN-AT-BAR** (slice) | `artifacts/qa/flagship_current_main_preview_2026-07-09/` |
| Waystream 1st catalog EPUB | **system working** | `artifacts/epubs/way_stream_sanctuary/` (#1923); register PASS, not Layer-4 |
| Waystream 4-cell generalization | **system working** | PROGRAM_STATE Production-Gate row; register-PASS |
| educators/nyc arc-seeded cells | **path broken** | Tuple-viability HARD-FAIL / `NO_STORY_POOL` (#1922) |
| Teacher mode infra | **CODE-WIRED** | `run_teacher_production_gates.py`, E2E smoke tests |
| Music mode | **CONFIG-EXISTS** | V2 spec; test_artist_alpha scaffold only |
| Translation | **SPECCED** / planning merged | #5480 source pack; zero execution on main |
| Manga alarm-is-lying tree | **EXECUTED-REAL** | 386 files on main |
| Manga mecha human-readability | **system working** | #5486 closeout; not PROVEN-AT-BAR |
| Manga catalog grid (1,345 series) | **CONFIG-EXISTS** / listing | 16 authored scripts; R2–R8 8–45% per vision audit |
| Format registry (22 runtimes) | **CODE-WIRED** | Derived durations + `check_format_duration_contracts.py` |
| Storefront | **EXECUTED-REAL** (listings) | Paid download scale **blocked** on asset depth |

---

## 4. Research → Document → Runtime Traceability

See `RESEARCH_TRACEABILITY.tsv` for row-level status.

**Well-grounded chains (complete or near-complete):**
- Persona/topic market fit → catalog planning → book_plans / arcs (`research/2026-03-30_*-persona-topic-market-fit.md` → `PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` → `config/source_of_truth/book_plans_en_us/`)
- Duration derivation → format registry → `phoenix_v4/ops/duration_derivation.py` (`research/2026-03-31_optimal-content-durations-global.md` → `DURATION_DERIVATION_SPEC.md` → `format_registry.yaml`)
- Bestseller acceptance / anti-drift → scorecard + F14 gate (`BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md` → scorecard → `bestseller_craft_gate.py`, beat-line ceiling)
- Manga genre craft → craft bibles → story/config (`docs/research/manga_craft/*` → MANGA specs → `config/manga/`)
- Flagship quality → hand-seam + Layer-4 blind-read → frozen goldens (session evidence → scorecard → CI parity gates)

**Research missing or unbound (production blockers for claiming "research-grounded"):**
- Music mode Phase A **anti-spam diversity thresholds** — spec-only; no standalone research artifact
- Teacher mode **F006 slot voice register** per teacher — doctrine YAML + specs; limited persona-level research binding
- Atom-native modular formats (10 stub runtimes) — `ATOM_NATIVE_MODULAR_FORMATS.md` authority; no per-format consumer research pack
- Non-CJK translation quality contract — checklist merged (#5480) but no locale-family blind-read research baseline
- Catalog-scale **Layer-4 blind-10** protocol — proposed in scorecard; not research-ratified as corpus benchmark

---

## 5. Books: Composite Regular Mode

**Exists on main:**
- Canonical spine path: `run_pipeline.py --pipeline-mode spine --quality-profile production --exercise-journeys` (four-piece chord CI-enforced)
- 1,519 en-US **listings**; 12,138 plannable arc+listing combos post #1913
- 1 Waystream catalog EPUB + GHL paid attach
- Flagship PROVEN-AT-BAR full book
- Production gates F1/F4/F2/F7 on main (#1919)
- July 10 open PRs: #5490 book-path cleanup, #5492 anxiety enrichment contract, #5494 midlife_women arc slice

**Missing:**
- EPUB assembly wave for catalog cells beyond the first Waystream cell
- Thin-persona **engine-keyed** STORY pools (`atoms/<p>/<t>/<engine>/CANONICAL.txt`)
- Binding governance for `false_alarm` on educators/nyc imposter_syndrome arcs
- Catalog-scale Layer-3/4 proof (only flagship has Layer-4)
- `--pipeline-mode` default still `registry` in code (spec drift; #5490 addresses)

**In flight:** #5489 thin-persona canonical atoms; #5490 spine default lock; #5492 enrichment proof; #5494 arc slice

**Blocked:** Operator Q-KENJIN-01 (kenjin active tier); storefront Phase A smoke (5 locales × 4 product types) until asset depth

---

## 6. Books: Teacher Mode

**Exists on main:**
- 12 teachers in registry with doctrine, banks, CI gates (`TEACHER_PRODUCTION_READINESS.md`)
- Coverage gate, synthetic governance, E2E smoke parametrized over teachers
- Teacher-sample EPUBs under `artifacts/epub/` and brand1_deep trees
- `TEACHER_DOCTRINE` atoms for 12 teachers (#1914)

**Missing:**
- F006 slot coverage at production scale (≥20 approved atoms/slot/teacher for 20-chapter arcs) for all teachers
- Catalog-scale teacher-mode EPUB attach pipeline (parallel to Waystream proof)
- Layer-4 blind-read for any teacher-mode book
- Research anchor for teacher-specific register beyond migration plans

**In flight:** None dedicated July 10; teacher bank translation #5501 is localization not teacher-mode compile proof

**Blocked:** Content authoring wall-clock for F006 slot backfill per teacher

---

## 7. Books: Music Mode

**Exists on main:**
- Ratified V1 caps + V2 production-readiness spec
- Wizard/onboarding scaffold, 6 slot pool schema, test_artist_alpha at SPEC-739 floor
- Brand integration + freebie funnel specs

**Missing:**
- Zero real musicians onboarded beyond test scaffold
- Zero music-mode catalog books shipped
- MusicGen Pearl Star Phase B WAV auto-render (deferred V1)
- Diversity CI guard (§5 V2 spec) not landed
- Q-MM-V2-CATALOG-800-RECONCILE-01 operator decision (800 per brand vs system-wide)

**In flight:** None July 10 books PRs

**Blocked:** Pearl_Editor + Pearl_Writer atom authoring for first real musician; PEARL-STAR-JOB-QUEUE ratification for auto-WAV

---

## 8. Manga

**Not a books launch prerequisite.** No book EPUB cell requires manga completion today.

**Merged and viewable on main:**
- April "alarm is lying" series tree (386 files)
- Stillness ep_001 HR-U16 continuity (#5428)
- Mecha native bank + human-readability proof assembly (#5482, #5486) — **system working**

**Not PROVEN-AT-BAR:**
- Entire manga catalog grid (R7 = 5%)
- Blind-10 pro bar (zero series)
- 8 registry locales at zero series
- Stillness post-merge proof re-run (local-only artifacts must not be reported as landed)

**In flight:** Human-readability rules (#5323 merged); mecha operator blind-read not dispatched

---

## 9. Atoms And Translation Coverage

**en-US authoring (live main):**
- Gap matrix SSOT: **20,804 rows**; **~20,773 cells at 0 variants**; 19 at 1; 8 at 2; 3 at 3
- Phase A target: 1,890 cells × ≥3 variants = **5,670 atoms** — **not met**
- Thin-persona: slot-keyed backfill (#1915) without engine-keyed STORY pools → spine HARD-FAIL

**Thin-persona gaps:** `educators`, `nyc_executives` — #5489 open; binding call for `false_alarm` engine

**Locale-variant status (execution on main = ~0%):**

| Locale family | Planning/skeletons | Atom translation execution |
|---|---|---|
| ja-JP | Catalog skeleton PRs open; source pack merged | Pilot PRs #5496, #5501 (not merged) |
| zh-TW | Skeleton PRs + #5499 reconcile | #5499 open |
| zh-CN | Skeleton PRs + #5500 stage-1 | #5500 open |
| ko-KR | Skeleton PRs only | No July 10 execution PR |
| non-CJK (pt-BR, es-US, …) | pt-BR ratified 14th locale | #5495 Wave 1 pilot open |

**Critical distinction:** ~150+ open `feat(catalog): * skeletons` PRs add **listings**, not translated readable books.

---

## 10. Formats And Durations

**Runtime registry:** 22 formats in `format_registry.yaml`; all Group A atom-native + compact formats backfilled 2026-07-07 with derived `audiobook_minutes` / `fill_regime`.

**Duration derivation:** `DURATION_DERIVATION_SPEC.md` → `duration_derivation.py` → registry; WPM from `duration_scorecard.yaml`.

**Proof / gate coverage:**
- CI: `check_format_duration_contracts.py`, production readiness gates
- Flagship proof: `extended_book_2h` PROVEN-AT-BAR
- Waystream proof: `standard_book` / generalization cells register-PASS
- **Gap:** No proof render per atom-native format (10 formats); no deep_book_6h catalog-scale proof post xfail scoping

See `FORMAT_DURATION_READINESS.tsv` per format.

---

## 11. Missing Research / Missing Functions / Missing Content

| Class | Count (approx) | Examples |
|---|---|---|
| Research gaps | **8** | Music diversity thresholds, Layer-4 blind-10 protocol, atom-native format consumer research, ko-KR translation quality baseline |
| Function gaps | **6** | MusicGen Phase B queue class, music diversity CI, `--pipeline-mode` spine default, catalog EPUB batch attach, translation execution pipeline at scale, manga blind-10 harness |
| Content gaps | **5** | ~20,773 atom cells, thin-persona engine STORY pools, real musician banks, teacher F006 slot depth, overthinking stub variants (#5503) |
| Translation gaps | **13** | All non-en-US locale atom trees at ~0% execution on main |
| Proof gaps | **4** | Catalog Layer-4 corpus, teacher-mode Layer-4, music-mode first ship, manga PROVEN-AT-BAR |

---

## 12. Open PRs And In-Flight Lanes

See `OPEN_PR_AND_WORKSTREAM_RECONCILE.tsv`. Summary:

**Books-first merge-now candidates (if green, do not duplicate):** #5489, #5490, #5492, #5494, #5489, #5237 (atom cohesion)

**Translation wave (July 10, do not duplicate):** #5495–#5501, #5497, #5498

**Do NOT merge this lane:** #5295 (owner-gated redundancy), #3166 (operator-gated budget)

**Adjacent audits (evidence only):** #5295, #4861, #5206

**Catalog skeleton flood (~150 PRs):** listings only — **later / not launch-critical** for books-first EPUB proof

---

## 13. Exact Roadmap To 100%

See `EXECUTION_ROADMAP.md`. Books-first sequence:

1. Merge thin-persona + spine-default + enrichment proof PRs (#5489, #5490, #5492)
2. Close engine-keyed STORY pool seeding for educators/nyc (+ binding decision)
3. Run Waystream-scale EPUB loop on next 10–50 proven cells (same CLI as #1923)
4. GHL/marketing attach batch for each real EPUB
5. Atom Phase A en-US tiered backfill (P0 personas/topics per gap matrix)
6. Translation Wave 1 merge + scale (ja-JP, zh-TW, zh-CN pilots → production batches)
7. Teacher-mode F006 slot backfill + one teacher EPUB proof per tier-1 teacher
8. Music-mode Phase A (first real musician) — parallel, post book Wave 1
9. Layer-4 blind-read expansion beyond flagship (10-cell pilot)
10. Manga M1–M3 enforcement + stories-first — **after** book Wave 1 unless operator re-ranks

---

## 14. Immediate Next 10 Actions

1. **merge-thin-persona-5489** — unblock educators/nyc tuple viability  
2. **merge-spine-default-5490** — kill registry-path drift  
3. **merge-enrichment-proof-5492** — anxiety contract-v1 evidence  
4. **dispatch-engine-story-pools** — ≥12 banded variants/cell engine-keyed STORY  
5. **waystream-epub-wave-10** — replicate #1923 CLI on 10 next proven cells  
6. **merge-translation-pilots** — #5496/#5499/#5500/#5501 when green  
7. **atom-p0-backfill** — close P0 gap-matrix tier per SSOT §9  
8. **ghl-attach-batch** — mirror #1947 for each new EPUB  
9. **layer4-pilot-10cell** — blind-read protocol beyond flagship  
10. **operator-q-kenjin-tier** — confirm kenjin active status  

---

## Stale Claims Treated As Evidence Hazards

| Stale claim | Live truth @ `4067366556f` |
|---|---|
| PROGRAM_STATE LAST VERIFIED `41c03d1f8f` | Main advanced; re-verify post-audit merge |
| "186/800 Waystream titles" | **REFUTED** — 800 distinct on main, gate #20 |
| "Localization 0% execution" | Still true for atoms; #5480 planning merged only |
| FULL_SYSTEM_AUDIT on main | **NOT on main** — lives in open PR #5295 only |
| Manga mecha "zero L2" blocker audits | **SUPERSEDED** by #5482/#5486 closeouts |
| "Green PR = production-ready" | **FALSE** — skeleton PRs ≠ EPUBs |
| register_gate PASS = bestseller | **DRIFT** — max structurally clear (Layer 1) |

---

**Audit root:** `artifacts/analysis/PROPRIME_100PCT_PRODUCTION_AUDIT_2026-07-10/`  
**Closeout:** `artifacts/qa/PROPRIME_100PCT_PRODUCTION_AUDIT_CLOSEOUT_2026-07-10.md`
