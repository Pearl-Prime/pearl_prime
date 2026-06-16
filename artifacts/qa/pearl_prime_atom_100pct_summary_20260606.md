# Pearl Prime — Atom 100% Coverage Summary (operator-facing)

**Date:** 2026-06-06
**Canonical SSOT:** [`docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md`](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md)
**Gap matrix (data):** [`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](./pearl_prime_atom_100pct_gap_matrix_20260606.tsv)

---

## Status (one paragraph)

Pearl Prime is at **~93% atom coverage for Phase A en-US persona-keyed types** (HOOK / COMPRESSION / REFLECTION / INTEGRATION / STORY / EXERCISE — 1,176 of 1,260 cells filled across 14 personas × 15 topics) but at **~0% persona-keyed for Class 2 overlay-routed types** (QUOTE / TEACHER_DOCTRINE / PERMISSION_GRANT — 0 of 210 P×T cells carry all 3 persona-keyed, as expected per `QUOTE-ATOM-ROUTING-01` retire-as-orphan ratification). Class 2 coverage instead flows through `SOURCE_OF_TRUTH/teacher_banks/` where it has its own 24-slot gap (QUOTE = 0 for 12 of 13 teachers; TEACHING = 0 for same 12). Locale coverage is full for ja-JP + zh-TW + zh-CN + ko-KR + zh-HK + zh-SG (CJK6) but **0** for de-DE, fr-FR, es-US, es-ES, it-IT, hu-HU per `pearl_prime_audit_2026-06-06.md` axis A6. Total gap-matrix row count = **20,803**. Authoring estimated hours total = **~26,618 hr** spread across 6 priority tiers.

---

## Top 10 Critical Gaps (Tier P0 + leading P1 — block Phase A en-US gold-reference book production)

1. **TEACHER_DOCTRINE overlay backing — 12 of 13 teachers × 15 topics × ≥3 variants** — `teacher_banks/<teacher>/doctrine/` + `teacher_banks/<teacher>/approved_atoms/TEACHING/`. Currently teacher-bank `TEACHING/` carries 0 atoms for 12 teachers (only ahjan has 100). HARD-blocks teacher-mode book assembly.
2. **QUOTE overlay backing — 12 of 13 teachers × 15 topics × ≥3 variants** — `teacher_banks/<teacher>/approved_atoms/QUOTE/`. Currently 0 atoms for 12 teachers; ahjan has 9 (below the 12-atom slot baseline).
3. **PERMISSION_GRANT overlay backing — same 12 teachers × 15 topics × ≥3 variants** — runtime canonical location is `teacher_banks/<teacher>/approved_atoms/PERMISSION/` (not the persona-keyed `PERMISSION_GRANT/` dir).
4. **midlife_women master_arcs = 0** — atoms exist for 15/15 topics but no master_arcs file = no catalog runs can ship for this persona; per `system_size.md` A6 (`ws_midlife_women_arc_authoring_20260427` already proposed; reinforced as Tier P1 blocker here).
5. **educators 7-topic gap** — burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing → 7 topics × 6 persona-keyed types × ≥3 variants = **126 atoms minimum**.
6. **nyc_executives 7-topic gap** — same 7 topics × 6 types × ≥3 variants = **126 atoms minimum**.
7. **gen_z_student 3-topic gap** — compassion_fatigue, financial_anxiety, financial_stress × 6 types × ≥3 variants = **54 atoms minimum**.
8. **EXERCISE strict-canonical backfill** — per `EXERCISE-BANK-RESOLUTION-01` Option 1, ~60-120 atoms for 10 bestseller-grade combos to unblock `ws_exercise_strict_canonical_production_20260506` (currently proposed; pair-lands with EXERCISE atoms or production smoke breaks per `pearl_prime_audit_2026-06-06.md` §3 #10).
9. **STORY named-character bestseller bank expansion** — per `BESTSELLER-INJECTIONS-MANDATORY-01` named-character STORY at sec 2/5/9, target ≈ 630 STORY engine variants minimum (≥3 named characters per 210 P×T cells) → currently 1,375 atoms but unevenly distributed; 34-cell short for educators + nyc_executives + gen_z_student gaps + midlife_women arc-block.
10. **CI guard runtime variant-floor assertion** — Tier P0 won't actually gate at runtime until `ws_runtime_variant_floor_assertion_20260606` lands (~5-line PR per `pearl_prime_audit_2026-06-06.md` §3 #7). Without it, missing cells silently proceed under production-profile.

> Full top-N list: see [SSOT §9](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md#9-gap-matrix--data--pearl_prime_atom_100pct_gap_matrix_20260606tsv) + the gap-matrix TSV ordered by priority_tier + estimated_hours.

---

## Per-tier breakdown

| Tier | Definition | Rows | Hours | Gate |
|---|---|---:|---:|---|
| **P0** | Phase A en-US gold-reference (6 priority personas × 6 priority topics × Class 2 overlay types) | 105 | ~125 | HARD — runtime fail-fast for Phase A launch |
| **P1** | Phase A en-US full breadth (14 personas × 15 topics) | 548 | ~665 | HARD — non-priority catalog launches |
| **P2** | Phase B ja-JP locale variants | 803 | ~982 | HARD — ja-JP catalog launch |
| **P3** | Phase C zh-TW + zh-CN | 2,550 | ~3,180 | HARD — zh catalog launch |
| **P4** | Phase D ko-KR + zh-HK + zh-SG | 1,829 | ~2,329 | HARD — ko + extended-CJK catalog launch |
| **P5** | Extended locales + variant enrichment | 14,968 | ~19,337 | SOFT — operator-tier per Q-Atom-LOCALE-SCOPE-01 |
| **Total** | — | **20,803** | **~26,618** | — |

---

## NEXT_ACTION (operator pick)

1. **Answer Q-Atom-* (16 questions; recommended defaults in SSOT §12).** Pearl_Architect will fold operator answers into a follow-up cap entry + ws scope tightening.
2. **Merge this PR.** Cap entry `ATOM-100PCT-COVERAGE-SSOT-V1-01` + the 4 child ws rows (proposed status) become the Phase A launch gate under `CATALOG-800-PER-BRAND-01`.
3. **Spawn child ws's** per [`SSOT §11`](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md#11-authoring-ownership-matrix) and [`§10`](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md#10-prioritization-tiers):
   - Pearl_Editor → `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` (Tier P0 + EXERCISE + QUOTE + TEACHER_DOCTRINE + PERMISSION_GRANT backing)
   - Pearl_Writer → `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606` (Tier P0 + P1 HOOK / COMPRESSION / REFLECTION / INTEGRATION / STORY)
   - Pearl_Localization → `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606` (Phase B ja-JP; gated on Phase A complete)
   - Pearl_Dev → `ws_pearl_dev_atom_100pct_ci_guard_20260606` (CI guard + runtime variant-floor assertion)
4. **Pearl_PM** tracks Tier P0 + P1 + P2 progress as the Phase A launch gate per `CATALOG-800-PER-BRAND-01`.
5. **Quarterly SSOT refresh** — re-run `python3 scripts/qa/build_atom_gap_matrix.py` (Pearl_Dev ws spec) on schedule to keep §9 current.

---

*Operator-facing summary v1. SSOT canonical: [docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md](../../docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md). Cap entry: `ATOM-100PCT-COVERAGE-SSOT-V1-01`.*
