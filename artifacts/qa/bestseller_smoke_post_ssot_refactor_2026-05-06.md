# Bestseller Smoke — AUTO-PLAN-SSOT-01 Refactor Verification (2026-05-06)

**Refactor branch:** `agent/auto-plan-ssot-refactor-20260506`
**Cap entries:** AUTO-PLAN-SSOT-01 + AUTO-PLAN-SSOT-01-AMENDMENT (both on origin/main as of #884 + pending #891)
**Purpose:** Verify the registry-driven `chapter_count` SSoT refactor preserves all chapter-count behavior across 20 runtime formats and produces no regression on the gen_z×anxiety bestseller smoke.

## 1. Pre/post-refactor `chapter_count` snapshot

```diff
$ diff /tmp/pre_refactor_chapter_counts.json /tmp/post_refactor_chapter_counts.json
(no output — zero diff)
```

All 20 runtime formats produce **identical chapter counts** before and after the refactor:

| Format | Pre (Python `FORMAT_CHAPTER_COUNTS`) | Post (registry `chapter_count_default`) |
|---|---:|---:|
| `micro_book_15` | 5 | 5 |
| `micro_book_20` | 6 | 6 |
| `five_min_practice` | 5 | 5 |
| `pocket_guide` | 6 | 6 |
| `ten_things_to_do` | 8 | 8 |
| `short_book_30` | 8 | 8 |
| `symptom_to_action_atlas` | 8 | 8 |
| `daily_text_audio_companion` | 10 | 10 |
| `crisis_cards` | 6 | 6 |
| `weekly_challenge_pack` | 8 | 8 |
| `faq_audiobook` | 8 | 8 |
| `myth_vs_mechanism` | 8 | 8 |
| `protocol_library` | 10 | 10 |
| `standard_book` | 10 | 10 |
| `extended_book_2h` | 14 | 14 |
| `deep_book_4h` | 16 | 16 |
| `deep_book_6h` | 20 | 20 |
| `compact_book_5ch_15min` | 5 | 5 |
| `compact_book_5ch_20min` | 5 | 5 |
| `compact_book_8ch_30min` | 8 | 8 |

**Verdict:** behavior-preserving. AUTO-PLAN-SSOT-01-AMENDMENT Group B tie-breaker (prefer Python) was the right call — runtime values unchanged.

## 2. Pytest sweep

```
$ PYTHONPATH=. python3 -m pytest \
    tests/test_chapter_flow_gate.py \
    tests/test_generate_book_plan.py \
    tests/test_knob_apply.py \
    tests/test_enrichment_select.py \
    -v

================== 110 passed, 2 skipped in 61.27s (0:01:01) ===================
```

One pre-existing test (`test_load_runtime_format_standard`) was updated to the post-amendment value (10 vs prior 12); rationale documented inline. Two new tests added in `tests/test_generate_book_plan.py`:
- `test_format_chapter_counts_compact_entries_present` — adapted to use `get_format_chapter_count` helper.
- `test_chapter_count_reads_from_registry_ssot` — proves the SSoT contract: monkeypatched registry loader returns 42, helper returns 42, callers receive 42; also asserts `FORMAT_CHAPTER_COUNTS` attribute is genuinely removed from the module.

## 3. Bestseller canary (`scripts/canary/run_bestseller_canary.py`)

```json
{
  "exit_code": 0,
  "overall_status": "PASS",
  "evidence_dir": "/Users/ahjan/phoenix_omega/.claude/worktrees/tender-lewin-875e3c/artifacts/canary/20260505T210640Z"
}
```

**Status: PASS.** Receipt's primary smoke gate satisfied.

## 4. Full bestseller smoke — gen_z_professionals × anxiety × compact_book_8ch_30min

Per `HANDOFF_bestseller_smoke_post_852_856_2026-05-04.md` §11 Appendix repro command (verbatim).

| Gate | Result |
|---|---|
| Pipeline exit code | **0** |
| `book.txt` produced | yes (39,247 bytes) |
| `plan.json` produced | yes |
| **Chapter flow gate** | **PASS (0/8 failed)** — 8 chapters as expected for `compact_book_8ch_30min` |
| Bestseller craft gate (advisory) | PASS — overall ONTGP score 0.63 |
| EI V2 | **PASS** — composite 0.67 |
| Editorial report | WARN — thesis drift 0 chapters, ONTGP 0.63, flow 1.00 |
| Memorable lines | 5 / 8 chapters with ≥2 quotable lines |
| Transformation arc | PASS |
| Book pass gate | PASS |
| Pearl Prime book quality gate | **Pass (fail=0 hold=0)** |

**Verdict: PASS** — chapter_count = 8 (expected), all hard gates green. The original bestseller smoke handoff §Finding 1 (REJECT, 13 chapters) was fixed by PR-Beta #886 (PR-D-SPINE-01 declarative-P3 wiring); this refactor preserves that fix. Refactor is behavior-preserving for the most-tested smoke path.

**Known scope deferral (not a refactor regression):** EXERCISE fallback to `library_34` on all 8 chapters reflects #887 atom-backfill's deliberate scope (HOOK/INTEGRATION/PIVOT covered for `gen_z_professionals × anxiety`; EXERCISE deferred to multi-source resolution per SPEC-739-VALIDATOR-MULTISOURCE-01). Tracked separately under `ws_pr_d_wires_resume_20260505` (W5/W6/W7 deferred per current Pearl_Dev session scope).

## 5. Opportunistic mwp × anxiety run

Per receipt: `millennial_women_professionals × anxiety` run "if low-cost." Hit unrelated content gap:

```
EnrichmentGapError: No enrichable content for slot TEACHER_DOCTRINE
  (topic=anxiety chapter=2 slot_index=5).
  Sources tried: persona=False, registry=False, teacher=False.
```

This is a TEACHER_DOCTRINE content-coverage gap for the `mwp × anxiety` matrix per the SPEC-739-VALIDATOR-MULTISOURCE-01 cap entry's known-deferred-9-section-types open question (`STORY/HOOK/REFLECTION/INTEGRATION/COMPRESSION/PIVOT/PERMISSION/TAKEAWAY/THREAD` — `TEACHER_DOCTRINE` is multi-source-aware in the validator but the runtime pipeline may still strict-resolve). **Not a refactor regression**: chapter_count for `standard_book` was set to 10 per Group B (matched the pre-refactor Python value), so chapter-count behavior unchanged; the failure is content-side.

Tracked: same separate ws as #4 above (`ws_pr_d_wires_resume_20260505`).

## 6. Verdict

The AUTO-PLAN-SSOT-01 refactor is behavior-preserving:
- Zero diff on chapter_count snapshots across all 20 runtime formats.
- 110 / 110 unit tests pass (0 failed, 2 pre-existing skipped).
- `run_bestseller_canary.py` returns exit 0 / `overall_status=PASS`.
- HANDOFF §11 spec smoke (gen_z×anxiety×compact_book_8ch_30min) passes with all hard quality gates green; chapter_count=8 (expected for compact format, matches pre-refactor behavior).

The Python `FORMAT_CHAPTER_COUNTS` constant has been removed; `get_format_chapter_count(runtime_format)` reads from `config/format_selection/format_registry.yaml:runtime_formats[*].chapter_count_default` via an `lru_cache(maxsize=1)`-cached `_load_format_registry()` helper. The registry is now the single source of truth.

## 7. Files changed in this refactor PR

| File | Change | Lines |
|---|---|---:|
| `config/format_selection/format_registry.yaml` | 6 Group B `chapter_count_default` updates + 10 Group A backfills | +30 / −5 |
| `phoenix_v4/planning/book_structure_plan.py` | Remove `FORMAT_CHAPTER_COUNTS` dict (24 lines); add `get_format_chapter_count` + `_load_format_registry` helpers (~40 lines); replace 1 lookup site | net ~+15 |
| `tests/test_generate_book_plan.py` | Adapt 1 test to `get_format_chapter_count`; add 1 SSoT-contract test | +35 / −10 |
| `tests/test_knob_apply.py` | Update `test_load_runtime_format_standard` value pin (12 → 10) per Group B | +5 / −1 |
| `artifacts/qa/bestseller_smoke_post_ssot_refactor_2026-05-06.md` | This document | +145 |
