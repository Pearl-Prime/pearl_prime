# Duration Book-Format Archaeology — 2026-07-07

**Project:** `proj_duration_derivation_v1_20260612`  
**Agent:** Pearl_Research (read-only archaeology)  
**Mode:** Reconcile current authority, old 40k/6h history, and duration contracts for every book-type format in the repo.

---

## Executive summary

The repo **already has a ratified canonical duration system** (`DURATION-DERIVATION-01`, ACTIVE 2026-06-12). Advertised minutes are **derived** from `word_target ÷ tts_wpm` (150) and `word_target ÷ ebook_wpm` (230), with `fill_regime` (`cap | floor | midpoint`) selecting `word_target`. Authority lives in `config/format_selection/format_registry.yaml`, governed by `docs/DURATION_DERIVATION_SPEC.md`. Phase-2 implementation is **landed on main**: registry fields populated, `phoenix_v4/ops/duration_derivation.py` exists, CI guard `check_duration_derivation()` is wired, tests at `tests/test_duration_derivation.py`.

**What changed historically:** Pre-June-2026, `duration_minutes` was hand-set and systematically understated audiobook length (headline: `standard_book` labeled 55 min, real ~143 min). The old 40k/50k+ word ambition targeted **`deep_book_6h`** (T7 "Complete", floor 52k words). Sprint 1 (2026-05-08, PR #939) **proved** a 50,344-word `deep_book_6h` render is achievable in pipeline; an earlier `adi_da` run failed at 4,657 words because the format was not wired. **Bulk catalog today still renders thin (~5k)**; gold depth-fill reaches ~21.5k — neither hits the 52k flagship target without the writing program.

**Plan references vs registry:** 176,595 `runtime_format_id` **plan references** across `book_plans_*` / `series_plans_*` use only **`standard_book_60min`** (122,083) and **`one_hour_book`** (54,512). This counts YAML plan-file rows (including nested `duration:` fields), **not** a clean “books currently shipping on storefronts” metric. The 7-tier ladder formats (`standard_book`, `deep_book_6h`, compacts, etc.) are registry truth but largely absent from auto-generated plan references.

**Flagship caveat (`PROGRAM_STATE.md`):** The one PROVEN-AT-BAR flagship is a **special** `extended_book_2h` cell (~21,012w, gen_z×anxiety). That proves the pipeline can reach ~T5–T6 length for one cell — **not** that the bulk catalog already inhabits the 7-tier ladder or that T7 (52k) is mass-catalog reality.

**Gaps:** Ten atom-native stub formats have `chapter_count_default` only — **cannot honestly advertise duration**. Legacy aliases (`quick_book_15m`, `standard_book_1h`, `deep_book_2h`, …) persist in content banks. No literal `10_day_challenge` format exists; closest repo-owned IDs are `weekly_challenge_pack` (7-day) and structural `F003` Challenge Series.

---

## File inventory read

### Authority stack (mandated)

| File | Role |
|------|------|
| `docs/SESSION_UNITY_PROTOCOL.md` | Session governance |
| `docs/PROGRAM_STATE.md` | Program SSOT; **one proven flagship** at `extended_book_2h` ~21k (special cell, not ladder-wide proof); `deep_book_6h` retired for that cell only |
| `docs/PEARL_ARCHITECT_STATE.md` | `DURATION-DERIVATION-01` cap entry (L3254+) |
| `artifacts/coordination/ACTIVE_PROJECTS.tsv` | `proj_duration_derivation_v1_20260612` active |
| `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` | `ws_duration_derivation_config_build_20260612`, `ws_duration_derivation_ci_guard_20260612` (listed proposed; implementation appears landed) |
| `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` | Routing (no duration-specific row) |

### Primary duration authorities

| File | Role |
|------|------|
| `docs/DURATION_DERIVATION_SPEC.md` | **Canonical derivation rules** (en-US) |
| `docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md` | CJK char-based derivation (PROPOSED) |
| `config/format_selection/format_registry.yaml` | **Canonical per-format SSOT** |
| `config/duration_scorecard.yaml` | `tts_wpm: 150`, `ebook_wpm: 230`, tolerance 10% |
| `artifacts/qa/duration_correctness_audit_20260611/DURATION_CORRECTNESS_REPORT.md` | Grounding audit |
| `artifacts/qa/duration_correctness_audit_20260611/RECOMMENDATIONS.md` | Fix recommendations |
| `artifacts/research/DURATION_FORMAT_UNIVERSE_AUDIT_2026-05-30.md` | Cross-channel format universe |
| `docs/CONTENT_DURATION_MARKETING_PLAN.md` | Marketing duration research |
| `specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md` | CDIS dev spec |
| `docs/sessions/SESSION_HANDOFF_2026-06-13_duration_per_platform.md` | Platform handoff |
| `artifacts/research/duration_per_platform_20260613/DURATION_PER_PLATFORM_PLAN.md` | 7-tier platform routing |
| `artifacts/research/duration_per_platform_20260613/DURATION_GAP_VERIFICATION.md` | Real render vs platform targets |
| `artifacts/research/duration_per_platform_20260613/CONTENT_LENGTH_TARGETS_FOR_WRITING_PROGRAM.md` | Writing-program targets |
| `artifacts/research/duration_per_platform_20260613/PLATFORM_DURATION_SOURCES.md` | Citation sources |

### Old / long-form / 40k trail

| File | Role |
|------|------|
| `docs/BOOK_PLANNING_SYSTEM_SPEC.md` | Plan-layer `duration_fit`; references runtime_format_id |
| `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` | Compact format proposal (now wired in registry) |
| `artifacts/production_run/adi_da_self_worth_full/PRODUCTION_REPORT.md` | Failed 54k/6h attempt (4,657 words) |
| `artifacts/coordination/micro_book_format_differentiation_decision.md` | micro 15 vs 20 differentiation gap |
| `artifacts/coordination/operator_decisions_log.tsv` | OPD rows for duration (see below) |
| `docs/handoffs/HANDOFF_2026-05-08_SPRINT1_AND_TEACHER30S.md` | Sprint 1: 50,344-word `deep_book_6h` PASS |
| `docs/ATOM_NATIVE_MODULAR_FORMATS.md` | Atom-native format word/duration guidance (not in registry) |

### All markdown files with `duration` in path/name (mandated sweep)

```
artifacts/audit/CATALOG_DURATION_AUDIT.md
artifacts/pilots/duration_matrix/RESULTS.md
artifacts/pilots/duration_matrix/RESULTS_V2.md
artifacts/pilots/duration_matrix/RESULTS_V3.md
artifacts/pilots/duration_matrix/SCALING_DELTA.md
artifacts/qa/duration_correctness_audit_20260611/DURATION_CORRECTNESS_REPORT.md
artifacts/qa/duration_correctness_audit_20260611/RECOMMENDATIONS.md
artifacts/qa/duration_ladder_subset_proof_20260615/INDEX.md
artifacts/research/DURATION_FORMAT_UNIVERSE_AUDIT_2026-05-30.md
artifacts/research/duration_per_platform_20260613/CONTENT_LENGTH_TARGETS_FOR_WRITING_PROGRAM.md
artifacts/research/duration_per_platform_20260613/DURATION_GAP_VERIFICATION.md
artifacts/research/duration_per_platform_20260613/DURATION_PER_PLATFORM_PLAN.md
artifacts/research/duration_per_platform_20260613/PLATFORM_DURATION_SOURCES.md
artifacts/research/marketing_sources/sub5_duration_bands.md
docs/CONTENT_DURATION_MARKETING_PLAN.md
docs/DURATION_DERIVATION_SPEC.md
docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md
docs/sessions/SESSION_HANDOFF_2026-06-13_duration_per_platform.md
old_chat_specs/group1/cursor_duration_audit_for_catalog_forma.md
old_chat_specs/group1/cursor_pearl_prime_duration_matrix_qa_p.md
research/2026-03-31_optimal-content-durations-global.md
specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md
```

### Implementation artifacts (discovered)

| File | Role |
|------|------|
| `phoenix_v4/ops/duration_derivation.py` | Derivation pure functions |
| `tests/test_duration_derivation.py` | Unit tests |
| `scripts/ci/pr_governance_review.py` | `check_duration_derivation()` guard |

---

## Current authority stack

```
DURATION-DERIVATION-01 (PEARL_ARCHITECT_STATE.md, ACTIVE)
    └── docs/DURATION_DERIVATION_SPEC.md          ← derivation rules (en-US)
    └── docs/DURATION_DERIVATION_SPEC_CJK_ADDENDUM.md  ← CJK (PROPOSED, deferred)
    └── config/format_selection/format_registry.yaml   ← per-format SSOT
            word_range, fill_regime, cap_word_target?, audiobook_minutes, ebook_minutes
            duration_minutes (DEPRECATED, overwritten with derived audiobook value)
    └── config/duration_scorecard.yaml            ← tts_wpm=150, ebook_wpm=230 (single-sourced)
    └── phoenix_v4/ops/duration_derivation.py   ← loader/derivation functions
    └── phoenix_v4/ops/duration_adherence_scorecard.py  ← measurement (reads same WPM)
    └── scripts/ci/pr_governance_review.py      ← path-level co-change guard
```

**Formula (already answered by authority):**

```
word_target = cap:   cap_word_target || word_range[max]
              floor: round(word_range[min] × 1.04)
              midpoint: round((min + max) / 2)

audiobook_minutes = round(word_target / tts_wpm)    # 150
ebook_minutes     = round(word_target / ebook_wpm)  # 230
```

**Operator-ratified 7-tier marketing ladder** (OPD-20260613-001): Quick Reset ~25m → Mini ~30m → Short ~45m → One-Hour ~1h → Standard ~2.5h → Long-Form ~3.5h → Complete ~6h. **Honesty spine:** advertise real median-render duration; thin renders HARD_FAIL rather than ship false labels.

---

## Old-model timeline

| Era | Model | Status |
|-----|-------|--------|
| Pre-2026-03 | Hand-set `duration_minutes` per format; no word→minute formula in advertising path | **Superseded** by DURATION-DERIVATION-01 |
| 2026-03–04 | Registry calibration PRs; `standard_book` word_range 9k–13k→18k | Evolved into cap-reconciliation |
| 2026-04-12 | `micro_book_15` / `micro_book_20` SKUs with duration delta only (no pedagogical delta) | Authority gap; GTM-deprecated in favor of compact |
| 2026-04-14 | `BOOK_PLANNING_SYSTEM_SPEC` — plan-layer `duration_fit` metadata | **Still live** (planning layer, not advertising) |
| 2026-05-04 | `COMPACT_BOOK_FORMAT_SPECS` — purpose-built 5ch/8ch spines | **Live** in registry; doc header still says "proposal" (stale) |
| 2026-05-06 | AUTO-PLAN-SSOT-01-AMENDMENT — registry chapter counts; Group A stub backfill | **Live** |
| 2026-05-08 | Sprint 1 — `deep_book_6h` 50,344-word production PASS; ceiling 65k→72k | **Proven** for one canary cell |
| 2026-05-17 | OPD-20260517-001 — `standard_book` ceiling 13k→18k (ch 11–12 truncation fix) | **Live**; later raised to 22k |
| 2026-05-30 | `DURATION_FORMAT_UNIVERSE_AUDIT` — compact vs micro, stub inventory | Partially stale (pre-#1550 labels) |
| 2026-06-11 | Duration correctness audit (PR #1510) — systematic label gap quantified | **Grounding evidence** |
| 2026-06-12 | DURATION-DERIVATION-01 ratified; OPD-062/063 | **Current authority** |
| 2026-06-13 | OPD-20260613-001 — 7-tier ladder + `one_hour_book` + CJK rule | **Live** operator decision |
| 2026-06-26 | `standard_book_60min` registered (5,722+ plan files at time of fix; QA KeyError fix) | **Live** in plan-reference SSOT |
| 2026-06-12+ | Phase-2 config + CI guard built | **Landed** (registry + code + tests) |

### Legacy alias namespace (pre-registry IDs, still in content banks)

| Legacy alias | Modern registry mapping | Notes |
|--------------|-------------------------|-------|
| `quick_book_15m` | `micro_book_15` or `compact_book_5ch_15min` | In `config/content_banks/*` runtime_allowlist |
| `quick_book_30m` | `short_book_30` or `compact_book_8ch_30min` | Same |
| `standard_book_1h` | `one_hour_book` or `standard_book_60min` | `one_hour_book` = 8ch/9k; `standard_book_60min` = 10ch/9–12k |
| `deep_book_2h` | `extended_book_2h` | ~2.3h derived (140 min) |
| `deep_book_5h` | **No registry ID** | Gap between T6 (~3.3h) and T7 (~5.8h) |

---

## 40k / 6h archaeology

### What was planned

1. **`deep_book_6h` as the long-form flagship** — registry `word_range: [50000, 72000]`, `fill_regime: floor`, `word_target = round(50000 × 1.04) = 52,000` → derived **347 min audiobook** (~5.8 hr). Comment: "compose retains ~72% → ~52K final (clear 50K floor)."
2. **54,000-word marketing target** — `adi_da` production report: "Target was 54,000 words (6h @ 150 WPM)."
3. **Sprint 1 engineering plan** (HANDOFF 2026-05-08): fix word-count killers (reflection trim, dedup scope, depth-fill starvation, registry ceiling 65k→72k) to clear **≥50,000-word floor**.
4. **Platform strategy** (DURATION_PER_PLATFORM_PLAN §5): T7 "Complete" at **52,000 words** wins Audible 5–7 hr + KDP 150–230 pp simultaneously.

### What actually happened

| Event | Outcome | Evidence |
|-------|---------|----------|
| Sprint 1 canary (`deep_book_6h × anxiety × gen_z × ahjan`) | **PASS, 50,344 words, 12 chapters** | `HANDOFF_2026-05-08_SPRINT1_AND_TEACHER30S.md` |
| `adi_da` self-worth full production | **FAIL gap: 4,657 words** (~30 min) | `PRODUCTION_REPORT.md` — format not wired to pipeline word expansion |
| Duration audit (1,000-book projection) | `deep_book_6h` labels **honest** (+2%); `standard_book` **+161% wrong** | `DURATION_CORRECTNESS_REPORT.md` |
| Bulk JA catalog renders | **~5,000 words** (thin) | `DURATION_GAP_VERIFICATION.md` §1 |
| Gold depth-fill path | **~21,500 words** (~2.4 hr) | Same |
| Catalog plan references | **Zero** `deep_book_6h` / `standard_book` plan refs | Usage sweep below |
| PROGRAM_STATE flagship (one cell) | **`extended_book_2h` at 21,012w** PROVEN-AT-BAR for gen_z×anxiety only; `deep_book_6h` retired for that cell — **not** evidence the whole catalog inhabits the ladder | `PROGRAM_STATE.md` |

### Root causes of the 40k/50k gap (not label math)

1. **Pipeline depth-fill path works** when production chord + Sprint 1 fixes are applied (proven once).
2. **Bulk auto-plan references** target `standard_book_60min` / `one_hour_book` — never invoke `deep_book_6h` fill regime.
3. **Writing-program gap:** OPD-20260613-001 honesty spine requires books to **grow into** T7 via real content depth, not padding.
4. **Early adi_da failure** was a **wiring** problem (section registry rendered ~400 words/chapter regardless of format), not a disproof of the 50k target.

### Cap-creep anti-pattern (documented, now guarded)

`standard_book` ceiling raised **13k → 18k → 20k → 22k** while the 55-min label stayed fixed until DURATION-DERIVATION-01. CI guard now requires registry edits to co-change with the derivation spec.

---

## Operator decisions log — duration-related rows

| OPD | Date | Topic |
|-----|------|-------|
| OPD-20260517-001 | 2026-05-17 | `standard_book.word_range[1]` 13k→18k (ch 11–12 truncation) |
| OPD-20260517-002 | 2026-05-17 | `deep_book_6h` canary CLI choices |
| OPD-122–128 | 2026-05-20 | `deep_book_6h` story/scene/exercise structure issues |
| OPD-20260611-042 | 2026-06-11 | Music-mode priority cell `deep_book_4h` |
| OPD-20260611-062 | 2026-06-12 | `standard_book` label 55→147 min + ceiling 18k→22k + `cap_word_target: 22000` |
| OPD-20260611-063 | 2026-06-12 | CI guard acceptance band ±15% (distinct from scorecard 10%) |
| OPD-20260613-001 | 2026-06-13 | Honest 7-tier ladder + `one_hour_book` + CJK rule + #1550 merge authorization |

---

## Live plan-reference counts by format

**Method:** Scan all `config/source_of_truth/book_plans_*/*` and `series_plans_*/*` for `runtime_format_id:` and `duration:` fields (the latter includes nested chapter-level duplicates — **not** a storefront shipment count).

### `runtime_format_id` (176,595 total)

| format_id | count |
|-----------|------:|
| `standard_book_60min` | 122,083 |
| `one_hour_book` | 54,512 |
| *all other registry formats* | **0** |

### `duration:` field (331,885 total — includes nested chapter-level duplicates)

| duration value | count |
|----------------|------:|
| `standard_book_60min` | 229,708 |
| `one_hour_book` | 102,177 |

**Interpretation:** Auto-generated plan references cluster in the **60–70 minute planning band** (`standard_book_60min`, `one_hour_book`). The 7-tier ladder formats (`standard_book`, `deep_book_6h`, compacts, micros) are registry-ready but **not referenced in book/series plan files**. The one proven flagship (`extended_book_2h` ~21k) is a pipeline proof for a single cell, not proof that plan references or storefront catalog already follow the ladder.

---

## `10_day_challenge` — repo-owned equivalent

**No literal `10_day_challenge` format_id exists** in `format_registry.yaml` or plan files.

| Closest repo-owned ID | What it is |
|---------------------|------------|
| **`weekly_challenge_pack`** | Atom-native stub; registry `chapter_count_default: 8`; `ATOM_NATIVE_MODULAR_FORMATS.md` §G defines **7 episodes** (Day 1–7), 180–480 words/day |
| **`F003` Challenge Series** | Structural format; `chapter_range: [7, 21]`; `typical_runtime: short_book_30` |
| **`ten_things_to_do`** | 10 **items**, not 10 **days** — checklist format, not a challenge calendar |

**Explicit answer:** For a "10-day challenge" product concept, the repo has **no registered runtime format**. The nearest honest mappings are `weekly_challenge_pack` (7-day habit pack, needs `word_range` backfill) or a future format derived from `F003` + `short_book_30` with operator-defined 10-day word budget.

---

## Contradictions / staleness table

| Source | Says | Registry / authority reality | Severity |
|--------|------|------------------------------|----------|
| `DURATION_FORMAT_UNIVERSE_AUDIT_2026-05-30.md` | `standard_book` = 55 min, 9k–18k words | 147 min, 9k–22k, cap 22k | **Stale** |
| `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md` | Audible prefers `standard_book (55 min)` | 147 min; routing should be `deep_book_6h`/`deep_book_4h` | **Stale** |
| `config/catalog_planning/platform_knob_tuning.yaml` | Routes `standard_book` to Audible at `ideal_runtime_hours: 5` | Sub-3hr books routed to 5hr surface | **Stale** (planning SSOT) |
| `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` | Status: proposal, not wired | Compact formats **are** in registry with `compact_chapter_subset` | **Stale header** |
| `docs/RECOGNITION_BANK_SPEC.md` | `quick_book_15m`, `standard_book_1h`, `deep_book_2h` | Legacy aliases; not registry IDs | **Stale** |
| `config/content_banks/*.yaml` | `runtime_allowlist` uses legacy IDs | Modern IDs differ | **Live drift** |
| `artifacts/coordination/micro_book_format_differentiation_decision.md` | micro 15/20 undifferentiated | Compact formats supersede for GTM | **Open** (owner decision pending) |
| `ACTIVE_WORKSTREAMS.tsv` | Config build + CI guard "proposed" | Registry fields + code + tests exist on main | **Stale status** (work likely complete) |
| `DURATION_DERIVATION_SPEC.md` header | Status: PROPOSED Phase-1 | Cap entry ACTIVE; Phase-2 landed | **Header stale** |

---

## Complete format matrix (every book-type runtime in registry)

WPM: audiobook ÷150, ebook ÷230. Status **derived** = `audiobook_minutes`/`ebook_minutes` populated per DURATION-DERIVATION-01.

| format_id | class | chapters | word_range | fill_regime | word_target | ab_min | eb_min | status | plan refs (`runtime_format_id`) | authority | gaps / decisions | recommended plan if missing |
|-----------|-------|----------|------------|-------------|-------------|--------|--------|--------|---------------------------|-----------|------------------|----------------------------|
| `micro_book_15` | first-class runtime (legacy 12-ch squeeze; GTM-deprecated) | 5 | 2,500–4,500 | midpoint | 3,500 | 23 | 15 | derived | 0 | `format_registry.yaml`; COMPACT spec §2 | Deprecate for GTM; redirect to `compact_book_5ch_15min` | Already answered — use compact for new catalog |
| `micro_book_20` | first-class runtime (legacy; GTM-deprecated) | 6 | 3,000–5,500 | midpoint | 4,250 | 28 | 18 | derived | 0 | same | Owner Option A/B/C undecided (`micro_book_format_differentiation_decision.md`) | Redirect to `compact_book_5ch_20min` |
| `short_book_30` | first-class runtime (legacy 12-ch squeeze) | 8 | 4,500–7,500 | midpoint | 6,000 | 40 | 26 | derived | 0 | same | Interim until compact_8ch validated at scale | Prefer `compact_book_8ch_30min` for GTM |
| `one_hour_book` | first-class runtime (T4 ladder) | 8 | 8,000–10,000 | midpoint | 9,000 | 60 | 39 | derived | 54,512 | OPD-20260613-001; registry | Bulk catalog tier; honest 1h label | Already answered |
| `standard_book_60min` | first-class runtime (**catalog workhorse**; not in 7-tier ladder) | 10 | 9,000–12,000 | midpoint | 10,500 | 70 | 46 | derived | 122,083 | registry (2026-06-26 QA fix) | **Not named in OPD 7-tier ladder**; sits between T4 and T5; EPUB alias to `standard_book` | Add explicit ladder slot or document as "Standard-60" SKU; verify render median vs 70 min label |
| `standard_book` | first-class runtime (T5 ladder) | 10 | 9,000–22,000 | cap (`cap_word_target: 22000`) | 22,000 | 147 | 96 | derived | 0 | DURATION-DERIVATION-01; OPD-062 | Gold path ~21.5k; bulk catalog doesn't use this ID | Route $-maker builds here; honesty spine applies |
| `extended_book_2h` | first-class runtime | 14 | 17,000–25,000 | midpoint | 21,000 | 140 | 91 | derived | 0 | registry; PROGRAM_STATE **one-cell** flagship | Proven ~21k for gen_z×anxiety only — not ladder-wide catalog proof; name says "2h", derived 140 min (~2.3h) | Already answered; consider marketing rename to "Long" not "2h" |
| `deep_book_4h` | first-class runtime (T6 ladder) | 16 | 20,000–40,000 | midpoint | 30,000 | 200 | 130 | derived | 0 | registry; OPD-20260613-001 | Name says "4h"; derived 200 min (~3.3h) | Already answered |
| `deep_book_6h` | first-class runtime (T7 ladder) | 20 | 50,000–72,000 | floor | 52,000 | 347 | 226 | derived | 0 | Sprint 1 handoff; OPD-20260613-001 | **Zero plan references**; 52k requires writing program + depth-fill | Content program: flagship Complete tier builds |
| `compact_book_5ch_15min` | compact (T1 Quick Reset) | 5 | 3,000–4,500 | midpoint | 3,750 | 25 | 16 | derived | 0 | COMPACT_BOOK_FORMAT_SPECS | GTM primary for 15-min band | Already answered |
| `compact_book_5ch_20min` | compact (T2 Mini) | 5 | 4,000–5,500 | midpoint | 4,750 | 32 | 21 | derived | 0 | same | GTM primary for 20-min band | Already answered |
| `compact_book_8ch_30min` | compact (T3 Short) | 8 | 5,500–7,500 | midpoint | 6,500 | 43 | 28 | derived | 0 | same | GTM primary for 30-min band | Already answered |
| `five_min_practice` | stub / atom-native | 5 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §A: 350–650 words total | No `word_range`, no fill_regime | `word_range: [350, 650]`, `fill_regime: midpoint`, derive ~3 min ab |
| `pocket_guide` | stub / atom-native | 6 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §B: 10–20 entries × 180–420w | Non-linear; total words = entries × per-entry | Derive total band e.g. `[2000, 8000]` from entry model; or per-entry duration only |
| `ten_things_to_do` | stub / atom-native | 8 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §C: 10 items × 120–260w | 8 chapters vs 10 items mismatch | `word_range: [1200, 2600]` for 10 items; reconcile chapter_count |
| `symptom_to_action_atlas` | stub / atom-native | 8 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §D: 20–60 cards × 90–220w | Card-count variable | Band by card count tiers; block listing until specced |
| `daily_text_audio_companion` | stub / atom-native | 10 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §E: 45–120 sec/day | Subscription SKU; per-day not per-book | Per-day `word_range: [110, 300]`; book = N × day |
| `crisis_cards` | stub / atom-native | 6 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §F: 90–200w/card | Freebie-primary per DFU audit | `word_range` per card set size; block paid duration claims |
| `weekly_challenge_pack` | stub / atom-native (**7-day challenge**) | 8 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §G: 7 days × 180–480w | **Not 10-day**; closest to "challenge" concept | `word_range: [1260, 3360]` for 7-day; add `ten_day_challenge` only if operator approves new ID |
| `faq_audiobook` | stub / atom-native | 8 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §H: 2–4 min/answer, 320–700w | Per-answer duration | Aggregate or per-FAQ derived minutes |
| `myth_vs_mechanism` | stub / atom-native | 8 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §I: 3–6 min/ep, 450–900w | Per-episode | Per-episode derivation |
| `protocol_library` | stub / atom-native | 10 | — | — | — | — | — | **cannot honestly advertise** | 0 | ATOM_NATIVE §J: 120–280w/protocol | Searchable drill catalog | Band by protocol count |

### Legacy aliases (not in registry — must not be used in new config)

| format_id | class | maps to | status |
|-----------|-------|---------|--------|
| `quick_book_15m` | legacy alias | `compact_book_5ch_15min` / `micro_book_15` | stale in content banks |
| `quick_book_30m` | legacy alias | `compact_book_8ch_30min` / `short_book_30` | stale |
| `standard_book_1h` | legacy alias | `one_hour_book` / `standard_book_60min` | stale |
| `deep_book_2h` | legacy alias | `extended_book_2h` | stale |
| `deep_book_5h` | legacy alias | **none** | gap — no 5h tier |

---

## Answers to mandated questions

### 1. What is the CURRENT canonical book-duration system?

**Already answered by authority:** `DURATION-DERIVATION-01` + `docs/DURATION_DERIVATION_SPEC.md`. Registry-derived `audiobook_minutes` / `ebook_minutes` from `word_target` and single-sourced WPM constants in `config/duration_scorecard.yaml`. `format_registry.yaml` is SSOT.

### 2. What older duration models existed, and which are superseded vs still live?

| Model | Status |
|-------|--------|
| Hand-set `duration_minutes` | **Superseded** (deprecated, overwritten with derived value) |
| Legacy alias IDs in content banks | **Stale but live** in YAML allowlists |
| 12-ch spine squeeze for short runtimes (micro/short) | **Live code path** but GTM-deprecated vs compact |
| Plan-layer `duration_fit` object | **Live** (BOOK_PLANNING_SYSTEM_SPEC) — planning metadata, not storefront label |
| 7-tier honest ladder (OPD-20260613-001) | **Live** marketing/GTM framework atop derived minutes |
| CJK char-based derivation | **Proposed** (addendum); not yet blocking en-US |

### 3. What were the old plans for ~40k / 50k+ words, and what happened?

**Plan:** `deep_book_6h` floor at 50k+ words (52k derived target) for 5–7 hr Audible/KDP flagship (T7). Sprint 1 fixed pipeline to hit 50,344 words once. Platform plan (2026-06-13) routes 52k as writing-program priority.

**Outcome:** Engineering path **proven** (Sprint 1 canary + one `extended_book_2h` flagship cell). Plan references **do not use** `deep_book_6h`. Renders cluster at ~5k (thin) and ~21.5k (gold). `adi_da` early failure was unwired format selector, not disproof of target. **52k T7 remains aspirational** for mass catalog — the proven flagship is ~21k `extended_book_2h`, not ladder-wide occupancy.

### 4. Duration contract per book/booklet/modular format?

See matrix above. **12 formats derived**; **10 stubs missing**; **5 legacy aliases** unmigrated.

### 5. Which formats have no honest duration contract today?

All **10 Group A stubs**: `five_min_practice`, `pocket_guide`, `ten_things_to_do`, `symptom_to_action_atlas`, `daily_text_audio_companion`, `crisis_cards`, `weekly_challenge_pack`, `faq_audiobook`, `myth_vs_mechanism`, `protocol_library`.

### 6. Which formats have chapter counts but no `word_range`, derived minutes, or fill regime?

**Same 10 stubs** — chapter_count only per AUTO-PLAN-SSOT-01-AMENDMENT Group A.

### 7. Which docs/specs disagree with registry reality?

See **Contradictions / staleness table** above. Highest-impact: `DURATION_FORMAT_UNIVERSE_AUDIT`, `PLATFORM_ALGORITHM_RESEARCH_2026.md`, `platform_knob_tuning.yaml`, content-bank legacy allowlists.

### 8. Minimum authoritative plan so every book-type format has a duration plan?

1. **Stub backfill ws** — port word targets from `ATOM_NATIVE_MODULAR_FORMATS.md` into registry (`word_range`, `fill_regime`, run derivation); block duration-advertising listings until done (per spec §8).
2. **Ladder amendment** — formally place `standard_book_60min` in the ladder (between T4 and T5) or document explicit alias rules vs `one_hour_book` / `standard_book`.
3. **Legacy alias migration** — replace `quick_book_*` / `standard_book_1h` / `deep_book_2h` in content banks with registry IDs.
4. **Reader migration** — listing builders + scorecard read `audiobook_minutes`/`ebook_minutes`; remove `duration_minutes`.
5. **CJK addendum ratification** — separate measured-render gate before CJK duration claims.
6. **Platform routing config** — reconcile `platform_knob_tuning.yaml` to post-#1550 derived minutes.
7. **Writing program** — T7 52k real renders (content-length, not config) for flagship surfaces.

---

## CURRENT_CANONICAL_BOOK_DURATION_LADDER

Operator-ratified 7-tier ladder (OPD-20260613-001) mapped to registry IDs at **derived** audiobook minutes:

| Tier | Marketing name | Registry format(s) | word_target | Audiobook | Ebook |
|------|----------------|-------------------|-------------|-----------|-------|
| T1 | Quick Reset ~25m | `compact_book_5ch_15min` (primary); `micro_book_15` (deprecated) | 3,750 / 3,500 | 25 / 23 min | 16 / 15 min |
| T2 | Mini ~30m | `compact_book_5ch_20min`; `micro_book_20` (deprecated) | 4,750 / 4,250 | 32 / 28 min | 21 / 18 min |
| T3 | Short ~45m | `compact_book_8ch_30min`; `short_book_30` | 6,500 / 6,000 | 43 / 40 min | 28 / 26 min |
| T4 | One-Hour ~1h | `one_hour_book` | 9,000 | 60 min | 39 min |
| — | **Catalog 60–70m** (not in OPD ladder) | `standard_book_60min` | 10,500 | 70 min | 46 min |
| T5 | Standard ~2.5h | `standard_book` | 22,000 (cap) | 147 min | 96 min |
| T6 | Long-Form ~3.5h | `deep_book_4h` | 30,000 | 200 min | 130 min |
| T7 | Complete ~6h | `deep_book_6h` | 52,000 (floor) | 347 min | 226 min |

**Adjacent format:** `extended_book_2h` (21k words, 140 min) — **one proven flagship cell** per `PROGRAM_STATE.md` (gen_z×anxiety); sits between T5 and T6 but is not proof the catalog inhabits the ladder. Name/mapping is awkward.

**WPM constants:** `tts_wpm: 150`, `ebook_wpm: 230` from `config/duration_scorecard.yaml`.

---

## UNSPECCED_FORMATS

Formats that **cannot honestly carry a duration claim** today:

1. `five_min_practice`
2. `pocket_guide`
3. `ten_things_to_do`
4. `symptom_to_action_atlas`
5. `daily_text_audio_companion`
6. `crisis_cards`
7. `weekly_challenge_pack`
8. `faq_audiobook`
9. `myth_vs_mechanism`
10. `protocol_library`

**Also unspecced as registry IDs:** `10_day_challenge` (does not exist), `deep_book_5h` (legacy alias with no target).

---

## STALE_DOCS_TO_AMEND

| Priority | Document / config | Amendment |
|----------|-------------------|-----------|
| P0 | `config/catalog_planning/platform_knob_tuning.yaml` | Route Audible/Spotify to `deep_book_6h`/`deep_book_4h`; remove 55-min assumptions |
| P0 | `docs/PLATFORM_ALGORITHM_RESEARCH_2026.md` | Update standard_book duration; preferred runtimes |
| P1 | `artifacts/research/DURATION_FORMAT_UNIVERSE_AUDIT_2026-05-30.md` | standard_book 147 min / 9k–22k; note #1550 supersession |
| P1 | `docs/RECOGNITION_BANK_SPEC.md` + `config/content_banks/*.yaml` | Replace legacy runtime_allowlist IDs |
| P1 | `docs/DURATION_DERIVATION_SPEC.md` header | PROPOSED → ACTIVE; note Phase-2 landed |
| P2 | `docs/COMPACT_BOOK_FORMAT_SPECS_2026-05-04.md` §1 Status | proposal → wired |
| P2 | `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` | Mark duration derivation ws complete if verified |
| P2 | Ladder docs / OPD-20260613-001 addendum | Add `standard_book_60min` explicit tier |

---

## MINIMUM_NEXT_WORKSTREAMS

| ID | Owner | Scope | Trigger |
|----|-------|-------|---------|
| `ws_stub_format_duration_backfill` | Pearl_Dev | Add `word_range` + `fill_regime` + derived minutes to 10 Group A stubs from ATOM_NATIVE targets; CI block duration listings | This archaeology report |
| `ws_duration_reader_migration` | Pearl_Dev | Migrate listing builders + `duration_adherence_scorecard.py` to `audiobook_minutes`/`ebook_minutes`; remove deprecated `duration_minutes` | Config build verified complete |
| `ws_legacy_runtime_alias_cleanup` | Pearl_Dev | Content-bank `runtime_allowlist` → registry IDs | Stub backfill or parallel |
| `ws_platform_routing_reconcile` | Pearl_Research | `platform_knob_tuning.yaml` + authority doc per DURATION_GAP_VERIFICATION §3 | Operator review OPD |
| `ws_cjk_duration_measured_render` | Pearl_Prime | One zh + one ko measured render; ratify CJK addendum | Pearl Star available |
| `ws_catalog_t7_writing_program` | Pearl_Prime / writing program | Real 52k-word Complete tier renders for flagship surfaces | OPD-20260613-001 honesty spine |
| `ws_standard_book_60min_ladder_doc` | Pearl_Architect | Formalize 60–70m tier in ladder governance | Operator decision |

---

## CLOSEOUT

**Report path:** `artifacts/research/DURATION_BOOK_FORMAT_ARCHAEOLOGY_2026-07-07.md`

**Blockers:** None — authority exists and Phase-2 implementation is present on main.

**Single best next implementation prompt:**

> **EXECUTE — `ws_stub_format_duration_backfill`:** For each of the 10 Group A stub formats in `config/format_selection/format_registry.yaml` (`five_min_practice`, `pocket_guide`, `ten_things_to_do`, `symptom_to_action_atlas`, `daily_text_audio_companion`, `crisis_cards`, `weekly_challenge_pack`, `faq_audiobook`, `myth_vs_mechanism`, `protocol_library`), read word/duration targets from `docs/ATOM_NATIVE_MODULAR_FORMATS.md`, add `word_range` + `fill_regime: midpoint` (unless cap/floor justified), run `phoenix_v4/ops/duration_derivation.py` to populate `audiobook_minutes`/`ebook_minutes`, add unit tests per format, and add a CI/listing guard that blocks any catalog row advertising duration for formats without `word_range`. Co-change `docs/DURATION_DERIVATION_SPEC.md` §8 per existing guard. Do not invent `10_day_challenge` — document `weekly_challenge_pack` as the 7-day challenge equivalent unless operator approves a new ID.
