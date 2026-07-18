# Pearl Prime Atom Coverage + EXERCISE Schema Lift — Session Handoff

**Date:** 2026-06-11 (UTC)
**Owner:** Pearl_PM (handoff doc) + Pearl_Architect (cascade originator) + Pearl_Dev / Pearl_Editor / Pearl_Writer / Pearl_Localization / Pearl_GitHub (downstream owners)
**Status:** **Cascade authored end-to-end; 5 PRs OPEN awaiting operator merge; 8 child workstreams pre-staged; 20 operator decisions logged.**

---

## §1. Why this doc exists

A single multi-agent session produced **6 PRs, 4 new cap entries, 1 new canonical SSOT, 8 child workstream rows, 20 logged operator decisions, and a 9-gate Phase A pre-launch matrix**. The cascade is fully governable + executable, but operator-merge has not yet fired. This handoff captures the full session state so the next operator-session (today or later) can resume with zero context-juggling.

**One-line state:** All 5 PRs are MERGEABLE + GREEN per Pearl_GitHub inspection (`artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md`). The critical-path bottleneck is operator clicking merge.

---

## §2. The 6 PRs (1 reference + 5 in stack)

| PR | SHA | Owner | Cap entry | Files | State | Stack |
|---|---|---|---|---|---|---|
| **#1485** | `19ca18344` | Pearl_Architect | `ATOM-100PCT-COVERAGE-SSOT-V1-01` | 9 | OPEN | base |
| **#1486** | `771e714e8` | Pearl_Architect | `EXERCISE-COMPONENT-SCHEMA-LIFT-01` | 5 | OPEN | sibling base |
| **#1488** | `0fa6a3b2e` | Pearl_Architect | AMENDMENT-2026-06-11 (cross-link + A1-A6) | 12 | OPEN | stacked on #1485 + #1486 |
| **#1489** | `4adcdf531` | Pearl_PM | (tracker iter 1; no cap) | 1 | OPEN | standalone off origin/main |
| **#1490** | `1dbe9a972` | Pearl_Architect | `ATOM-100PCT-COVERAGE-SSOT-V1-01-RATIFICATION-2026-06-11` | 14 | OPEN | stacked on all 4 above |
| **Pearl_GitHub inspection** | (no PR) | Pearl_GitHub | (no cap; receipt-only) | 1 doc | working-tree | independent |

**Pearl_GitHub inspection artifact:** [`artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md`](../artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md) (168 lines; receipt-only; not committed). 5 of 5 PRs verdict = **GREEN**.

---

## §3. What each PR ships

### PR #1485 — `ATOM-100PCT-COVERAGE-SSOT-V1-01` (SSOT base)

- **NEW:** [`docs/PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md`](./PEARL_PRIME_ATOM_100PCT_COVERAGE_SSOT.md) — 16-section canonical SSOT for 100% atom coverage
- **NEW:** [`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](../artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv) — 20,803-row machine-readable gap matrix
- **NEW:** [`artifacts/qa/pearl_prime_atom_100pct_summary_20260606.md`](../artifacts/qa/pearl_prime_atom_100pct_summary_20260606.md) — operator-facing summary
- **DEPRECATED-cross-link append** to 4 prior partial audits: `persona_atom_audit.md`, `teacher_bank_audit.md`, `registry_coverage_vs_catalog.md`, `P1_HEALTH_REPORT_2026_04_10.md`
- **APPEND cap entry** `ATOM-100PCT-COVERAGE-SSOT-V1-01` to [`docs/PEARL_ARCHITECT_STATE.md`](./PEARL_ARCHITECT_STATE.md)
- **APPEND 4 ws rows** to [`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`](../artifacts/coordination/ACTIVE_WORKSTREAMS.tsv) + **flip** `ws_atom_gap_fill_20260410` → superseded

### PR #1486 — `EXERCISE-COMPONENT-SCHEMA-LIFT-01` (schema lift)

Closes two drifts in the EXERCISE backstop path:
- **Drift A:** schema v1's `blocks: {setup, instruction, prompt, close}` lost the rich 5-component × {full, lean} shape authored in inbox JSONs (311 items affected; 100% structural loss on ingest)
- **Drift B:** `ab_tady_37` source enum declared valid but ingest script had no source branch (39 items un-ingested)

Files:
- **EDIT** [`specs/PRACTICE_ITEM_SCHEMA.md`](../specs/PRACTICE_ITEM_SCHEMA.md) — v1 → v2; adds parallel `components` field per §2.5
- **EDIT** [`config/practice/validation.yaml`](../config/practice/validation.yaml) — v1 → v2 `components_schema` + per-slot char limits
- **EDIT** [`config/practice/selection_rules.yaml`](../config/practice/selection_rules.yaml) — v1 → v2 `component_variant_by_format` mapping (full for ≥120-min formats; lean for 17 short-form)
- **APPEND cap entry** `EXERCISE-COMPONENT-SCHEMA-LIFT-01` to `PEARL_ARCHITECT_STATE.md`
- **APPEND 2 Pearl_Dev ws rows** to `ACTIVE_WORKSTREAMS.tsv`

### PR #1488 — AMENDMENT-2026-06-11 (cross-link)

Closes 3 governance gaps between #1485 + #1486:
- SSOT not cross-linked to schema lift → APPEND §3 footnote + §12 cross-ref + new §17 AMENDMENT block in SSOT
- Pearl_Editor preservation audit not tracked → APPEND `ws_pearl_editor_exercise_preservation_audit_20260611` to TSV
- A1-A6 acceptance criteria not explicit → APPEND-IN-PLACE to existing `EXERCISE-COMPONENT-SCHEMA-LIFT-01` cap entry

Also appends optional `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` per Q-Atom-INCLUDE-SLOT-07-BACKFILL-WS-01 (a).

### PR #1489 — Pearl_PM tracker iter 1

- **NEW:** [`artifacts/coordination/pearl_prime_atom_phase_a_launch_tracker.md`](../artifacts/coordination/pearl_prime_atom_phase_a_launch_tracker.md) — 247-line tracker with §A banner + §B spec stack snapshot + §C 3-PR merge queue + §D 20 Q-Atom-* decision matrix + §E 8-ws cascade tree + §F 9-gate Phase A pre-launch matrix + §G critical-path bottleneck + §H iter-2 triggers + §I cross-refs

Independent standalone; coordination-only; can merge any time.

### PR #1490 — Q-Atom-* batch ratification

Operator answered all 20 Q-Atom-* via Mode A (recommended defaults) with **1 override**: `Q-Atom-LOCALE-SCOPE-01 = (b) top-3 (en-US + ja-JP + zh-TW)` vs recommended (c) en-US only.

Files:
- **EDIT** SSOT: 21 RESOLVED stamps inline below each Q-Atom + NEW **§18 DECISIONS RESOLVED 2026-06-11** with 20-row decision matrix + material implications
- **EDIT** `PEARL_ARCHITECT_STATE.md`: parent cap status `PROPOSAL → ACTIVE 2026-06-11` + APPEND new `ATOM-100PCT-COVERAGE-SSOT-V1-01-RATIFICATION-2026-06-11` cap entry
- **APPEND 20 OPD rows** to [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv) (OPD-20260611-001 through OPD-20260611-020; 12-col schema)
- **EDIT tracker** §D + §G to reflect post-ratification state

---

## §4. The 20 operator decisions (1 override)

| # | Q-Atom-ID | Chosen option | OPD-ID |
|---|---|---|---|
| 01 | `Q-Atom-PERSONA-SCOPE-01` | (a) keep all 14 + backfill | OPD-20260611-001 |
| 02 | **`Q-Atom-LOCALE-SCOPE-01`** | **(b) top-3 (en-US + ja-JP + zh-TW) — OVERRIDE** | OPD-20260611-002 |
| 03 | `Q-Atom-LOCALE-PHASE-01` | (a) en-US → ja-JP → zh-TW → zh-CN → ko-KR | OPD-20260611-003 |
| 04 | `Q-Atom-VARIANT-CEILING-01` | (a) ≥3 floor + ≤5 ceiling per SPEC-739-THRESHOLD-01 | OPD-20260611-004 |
| 05 | `Q-Atom-PERSONA-KEYED-FALLBACK-01` | (a) BLOCK catalog runs until backfilled | OPD-20260611-005 |
| 06 | `Q-Atom-STORY-BANK-EXPANSION-01` | (b) ≥3 named characters per P×T cell (~630 STORY min) | OPD-20260611-006 |
| 07 | `Q-Atom-TEACHER-BANK-SCOPE-01` | (a) all 13 teachers × all 15 topics complete | OPD-20260611-007 |
| 08 | `Q-Atom-PRIORITY-PERSONAS-01` | gen_z_professionals + corporate_managers + working_parents + first_responders + healthcare_rns + gen_x_sandwich | OPD-20260611-008 |
| 09 | `Q-Atom-PRIORITY-TOPICS-01` | anxiety + overthinking + burnout + boundaries + self_worth + depression | OPD-20260611-009 |
| 10 | `Q-Atom-EXERCISE-BANK-RESOLUTION-01` | (a) strict-canonical for Tier P0 | OPD-20260611-010 |
| 11 | `Q-Atom-MASTER-ARC-INTERACTION-01` | (a) atom requirements independent of arc chapter_count | OPD-20260611-011 |
| 12 | `Q-Atom-CI-GUARD-SEVERITY-01` | (a) HARD FAIL on missing Tier P0 under production-profile | OPD-20260611-012 |
| 13 | `Q-Atom-SSOT-UPDATE-CADENCE-01` | (a) every atom-authoring ws PR auto-updates §9 | OPD-20260611-013 |
| 14 | `Q-Atom-DE-DE-FR-FR-01` | (a) defer per AMENDMENT-2026-06-04.2 (aligned with #02) | OPD-20260611-014 |
| 15 | `Q-Atom-ONE-PATH-SPEC-FILE-01` | (a) wait for ONE-PATH-V1-01 ratification; pair-cycle | OPD-20260611-015 |
| 16 | `Q-Atom-DIRECTIVE-9-VS-CAP-16-01` | (a) accept §3 routing-class split as SSOT canonical | OPD-20260611-016 |
| 16b | `Q-Atom-LEGACY-ATOM-TYPES-01` (pair-vote) | (a) under ONE-PATH-V1-01 D8 alone | OPD-20260611-016 |
| 17 | `Q-Atom-SLOT-07-PRIORITY-01` | (a) breath_regulation first (ab_tady_37 covers it) | OPD-20260611-017 |
| 18 | `Q-Atom-AUDIT-PASS-THRESHOLD-01` | (a) ≥99% items zero-loss | OPD-20260611-018 |
| 19 | `Q-Atom-INCLUDE-PEARL-PM-ITER-3-01` | (b) defer to Pearl_PM's own iter session | OPD-20260611-019 |
| 20 | `Q-Atom-INCLUDE-SLOT-07-BACKFILL-WS-01` | (a) YES — included in PR #1488 | OPD-20260611-020 |

### Material implication of LOCALE-SCOPE override

| Phase | SSOT default | Post-override |
|---|---|---|
| A en-US | 1,890 cells × ≥3 variants | unchanged |
| B ja-JP | 1,890 cells × ≥3 | unchanged |
| C zh-TW + zh-CN | both | **zh-TW only** (≈50% scope reduction) |
| D ko-KR + zh-HK + zh-SG | required | **post-Phase-A optional** |
| E es-* / fr-FR / de-DE / it-IT / hu-HU | required | **post-Phase-A optional** |
| **Phase A launch gate gap rows** | 20,803 (full matrix) | **≈ 653** (P0 + P1 en-US persona-keyed + Class 2 overlay) |

---

## §5. The 8 child workstreams (all status=proposed)

### Dependency tree

```
PR #1485 MERGE ───┬─── ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606
                  │       (Pearl_Editor; Tier P0; ~125 hr; 105 rows)
                  │
                  ├─── ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606
                  │       (Pearl_Writer; Tier P0 + P1; ~665 hr; 548 rows)
                  │
                  ├─── ws_pearl_dev_atom_100pct_ci_guard_20260606
                  │       (Pearl_Dev; CI guard + runtime variant-floor assert)
                  │
                  └─── ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606
                          (Pearl_Localization; Phase B ja-JP; ~982 hr; 803 rows)
                          ─── HARD-gated on en-US Tier P0 + P1 = 0

PR #1486 MERGE ───┬─── ws_pearl_dev_practice_ingest_components_lift_20260610
                  │       (Pearl_Dev; ingest fix + ab_tady_37; 272 v1 → 311 v2 rows)
                  │       └── A1 + A2 verifiable post-merge
                  │
                  └─── ws_pearl_dev_renderer_practice_components_consume_20260610
                          (Pearl_Dev; renderer reads structured components)
                          └── A4 + A5 verifiable post-merge
                          ─── HARD-gated on ingest ws merging first

PR #1488 MERGE + ↑ both Pearl_Dev schema ws's
                  → ws_pearl_editor_exercise_preservation_audit_20260611
                          (Pearl_Editor; A1-A6 end-to-end with per-item evidence)

Operator answered Q-Atom-SLOT-07-PRIORITY-01 = (a) breath_regulation
                  → ws_pearl_editor_slot_07_practice_supply_backfill_20260611
                          (Pearl_Editor + Pearl_Writer; 11 content_types × 8 items = 88 min)
                          ─── HARD-gated on PR #1486 + 2 Pearl_Dev ws's merged
```

### Per-ws table

| # | ws_id | Owner | Blockers | Tier |
|---|---|---|---|---|
| 1 | `ws_pearl_editor_atom_100pct_tier_p0_persona_keyed_20260606` | Pearl_Editor | PR #1485 + Q-Atom-PRIORITY-PERSONAS/TOPICS (resolved) | P0 |
| 2 | `ws_pearl_writer_atom_100pct_tier_p0_engine_atoms_20260606` | Pearl_Writer | PR #1485 | P0+P1 |
| 3 | `ws_pearl_localization_atom_100pct_tier_p2_ja_jp_20260606` | Pearl_Localization | en-US Tier P0+P1 = 0 | P2 |
| 4 | `ws_pearl_dev_atom_100pct_ci_guard_20260606` | Pearl_Dev | PR #1485 + Q-Atom-CI-GUARD-SEVERITY (resolved) | P0 |
| 5 | `ws_pearl_dev_practice_ingest_components_lift_20260610` | Pearl_Dev | PR #1486 | P0 |
| 6 | `ws_pearl_dev_renderer_practice_components_consume_20260610` | Pearl_Dev | ws #5 merged | P0 |
| 7 | `ws_pearl_editor_exercise_preservation_audit_20260611` | Pearl_Editor | ws #5 + ws #6 merged | P0 |
| 8 | `ws_pearl_editor_slot_07_practice_supply_backfill_20260611` | Pearl_Editor + Pearl_Writer | PR #1486 + ws #5 + ws #6 merged | P1 |

---

## §6. Phase A pre-launch gate matrix (9 gates; 9 not-started)

Required for Phase A en-US catalog launch declaration per `CATALOG-800-PER-BRAND-01`:

| # | Gate | Owning ws | State |
|---|---|---|---|
| G1 | Tier P0 atom cells (105 → 0) | ws #1 + #2 + #4 | not-started |
| G2 | Tier P1 atom cells (548 → 0) | ws #1 + #2 (continue) | not-started |
| G3 | A1-A6 acceptance criteria PASS | ws #7 | not-started |
| G4 | `scripts/ci/check_atom_100pct_coverage.py` PASS on main | ws #4 | not-started |
| G5 | ONE-PATH-V1-01 D4 + D8 runtime asserts landed | cross-ref ONE-PATH-V1-01 cap; out-of-scope here | not-started |
| G6 | EXERCISE schema-lift cascade complete | ws #5 + #6 + #7 + (#8 optional) | not-started |
| G7 | `component_variant_by_format` dry-run PASS per format | ws #6 tests | not-started |
| G8 | Move 4 verdict recompute under production-profile | cross-ref ONE-PATH-V1-01 P0-C | not-started |
| G9 | `CATALOG-800-PER-BRAND-01` high-confidence catalog artifact | cross-ref Pearl_Research / Pearl_Marketing existing ws | not-started |

---

## §7. Cap entry registry (4 new + 1 status flip)

All in [`docs/PEARL_ARCHITECT_STATE.md`](./PEARL_ARCHITECT_STATE.md):

| Cap entry | Status | Authority |
|---|---|---|
| `ATOM-100PCT-COVERAGE-SSOT-V1-01` | **ACTIVE 2026-06-11** (was PROPOSAL → flipped per PR #1490) | PR #1485 + #1490 |
| `ATOM-100PCT-COVERAGE-SSOT-V1-01-RATIFICATION-2026-06-11` | ratified | PR #1490 (minor cap entry) |
| `EXERCISE-COMPONENT-SCHEMA-LIFT-01` | ratified | PR #1486 |
| (`PEARL-PRIME-ONE-PATH-V1-01`) | unchanged PROPOSAL | pre-existing; pair-cycle per Q-Atom-ONE-PATH-SPEC-FILE-01 (a) |

A1-A6 acceptance criteria for the EXERCISE cascade are appended to `EXERCISE-COMPONENT-SCHEMA-LIFT-01` per PR #1488 (the merge gate for the 2 Pearl_Dev schema ws's).

---

## §8. Pearl_GitHub batch inspection (5 PRs all GREEN)

Inspection artifact: [`artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md`](../artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md) (168 lines; working-tree-only; not committed).

Summary:
- All 5 PRs: `Verify governance` (ruleset-required) = **PASS**
- All 5 PRs: RULE-0 deletion check = **PASS** (0 file deletions; max 12 line deletions)
- 4 of 5 PRs: Governance review = APPROVED WITH WARNINGS (FALSE-POSITIVE `workstream_conflict` on 11 pre-existing in_progress ws's — same noise pattern as storefront PRs #1448/#1481)
- #1489: Governance = FULLY APPROVED (no warnings)
- All 5 PRs: CI failures are OPD-153 (`Workers Builds: pearl-prime`) and false-positive `scan` on doc-heavy PRs — both non-blocking; non-ruleset-required
- 10 pairwise overlap checks: all CLEAN; cherry-pick chains resolved per prior receipts

**Verdict:** Operator can batch-merge in any order with confidence.

---

## §9. Recommended merge order

1. **#1490 (ratification)** first — smallest atomic; cap flip PROPOSAL → ACTIVE
2. **#1486 (schema lift)** — unblocks Pearl_Dev ingest ws #5 standalone
3. **#1485 (SSOT)** — unblocks 3 parallel #1485-gated ws's (Editor Tier P0 + Writer Tier P0+P1 + Dev CI guard); Pearl_PM iter 2 fires
4. **#1488 (AMENDMENT)** — auto-rebases against #1485 + #1486; A1-A6 lands on main
5. **#1489 (tracker)** — standalone; landing last keeps it reflective of final main state

**Alternative:** any order works; auto-rebase handles cherry-pick adjustments.

---

## §10. Cascade triggers (what fires automatically after each merge)

| Trigger | Auto-dispatch |
|---|---|
| **#1485 merge** | Pearl_PM iter 2 fires + 3 parallel ws dispatch prompts ready: Editor Tier P0 + Writer Tier P0+P1 + Dev CI guard |
| **#1486 merge** | Pearl_Dev ingest ws #5 dispatch ready (re-fire Pearl_Dev prompt; pre-requisite check passes) |
| **Pearl_Dev ingest ws PR merge** | Renderer ws #6 dispatch ready (A4 + A5 verify) |
| **Renderer ws PR merge** | Preservation audit ws #7 dispatch ready (A3 + A6 verify; A1-A6 end-to-end closed) |
| **PR #1486 + ws #5 + ws #6 all merged** | Slot_07 backfill ws #8 dispatch ready (priority breath_regulation per OPD-20260611-017) |
| **en-US Tier P0 + P1 = 0 in gap matrix** | Localization ws #3 dispatch ready (Phase B ja-JP) |

---

## §11. Tracker location + next iter

| | Path | Cadence |
|---|---|---|
| Tracker | [`artifacts/coordination/pearl_prime_atom_phase_a_launch_tracker.md`](../artifacts/coordination/pearl_prime_atom_phase_a_launch_tracker.md) (PR #1489) | DAILY until 5-PR cascade clears; WEEKLY once child ws's execute; DAILY again during pre-launch QA |
| Inspection receipt | [`artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md`](../artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md) | one-shot; receipt-only |
| Decision log | [`artifacts/coordination/operator_decisions_log.tsv`](../artifacts/coordination/operator_decisions_log.tsv) | 20 OPD entries appended; consult schema before further appends |
| Gap matrix | [`artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv`](../artifacts/qa/pearl_prime_atom_100pct_gap_matrix_20260606.tsv) | re-run per ws PR per Q-Atom-SSOT-UPDATE-CADENCE-01 (a) |

**Iter 2 fires on first of:** any PR merges / any new ws PR merges / 48h no-motion / operator-explicit pre-empt.

---

## §12. Resume protocol for next session

**If the operator has NOT yet merged the 5 PRs:**

1. Read this handoff doc end-to-end.
2. Read [`artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md`](../artifacts/coordination/pre_merge_inspection_5pr_batch_20260611.md) for the GREEN-verdict per-PR detail.
3. Click merge on the 5 PRs in §9 order (or any order).
4. Re-fire the pre-staged Pearl_Editor Tier P0 prompt + Pearl_Writer Tier P0+P1 prompt + Pearl_Dev CI guard prompt (queued from earlier operator turn) once #1485 lands.
5. Re-fire the Pearl_Dev ingest ws prompt once #1486 lands (pre-requisite check will pass + the ws executes against v2 schema on main).

**If the operator HAS merged some of the 5 PRs:**

1. Read this handoff doc.
2. Pearl_PM iter 2 (re-fire the tracker iter prompt) captures the merge cascade in `pearl_prime_atom_phase_a_launch_tracker.md` §F gate-state updates.
3. Per §10 trigger table, dispatch the unblocked downstream ws prompts.

**If something has gone sideways:**

- The 5 PRs are designed to merge independently AND in any order. Auto-rebase clean per Pearl_GitHub inspection.
- If a PR is mid-rebase or in a bad state, read `feedback_drift_recovery_git_first` memory — restore by `git checkout <good-sha> -- <path>` rather than fresh-fix.
- The known-good SHAs are the PR HEADs in §2 + the 5 commits' SHAs after merge.
- All 4 PRs that cherry-picked parent content used identical splice patterns in `PEARL_ARCHITECT_STATE.md` (siblings, not competing cap entries) + `ACTIVE_WORKSTREAMS.tsv` (append-only at tail). Receipts confirm clean.

---

## §13. Open follow-ups (for after Phase A en-US launches)

| Item | Owner | Trigger |
|---|---|---|
| Phase B ja-JP locale variant authoring | Pearl_Localization (ws #3) | en-US Tier P0+P1 = 0 |
| Phase C zh-TW locale variant authoring | Pearl_Localization (future ws) | en-US + ja-JP complete |
| Move 4 verdict recompute under production-profile + §13 rubric | Pearl_Architect (cross-ref ONE-PATH-V1-01 P0-C) | ONE-PATH-V1-01 Phase 2 ws lands |
| `PEARL-PRIME-ONE-PATH-V1-01` cap ratification (12 Q-OP-*) | Pearl_Architect | operator answers Q-OP-* on its PR thread |
| `gratitude_practices_v1` promotion to PRODUCTION_READY | Pearl_Editor (tracked under existing `EXERCISE-BANK-RESOLUTION-01`) | separate ws (not in this cascade) |
| Quarterly SSOT refresh + tier delta | Pearl_Architect | per Q-Atom-SSOT-UPDATE-CADENCE-01 (a) — every atom-authoring ws PR triggers auto-update |
| Persona-keyed + teacher-bank EXERCISE atoms lift to 5-component shape | Pearl_Editor (future `ws_pearl_editor_exercise_5_component_atom_lift_2026XXXX`) | operator demand; out of current 8-ws cascade |

---

*Handoff doc v1 — 2026-06-11 Pearl_PM. Cascade is governable end-to-end; operator merge unblocks downstream agents. All files cited in this doc are either landed on main, awaiting merge on the 5 open PRs, or working-tree-only inspection artifacts.*
