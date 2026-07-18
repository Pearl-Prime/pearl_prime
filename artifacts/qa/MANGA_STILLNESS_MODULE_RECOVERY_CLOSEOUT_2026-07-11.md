# MANGA STILLNESS MODULE RECOVERY CLOSEOUT — 2026-07-11

**Workstream:** `ws_stillness_module_recovery_20260711`  
**Agent:** Pearl_Dev  
**Live `origin/main` audited:** `4c896efb8ab0038e73906841ab82bb19c47b9eb3`  
**Prior blocker audit:** `artifacts/qa/MANGA_STILLNESS_POSTMERGE_PROOF_RECOVERY_CLOSEOUT_2026-07-11.md` (merged #5526)  
**Acceptance layer:** CODE-WIRED (prerequisite modules + tests on main) — **not** EXECUTED-REAL stillness proof

> **Verdict:** **MERGED module recovery.** Three prerequisite modules were absent from
> `origin/main`, local branches, worktrees, and git history. Authored from authority docs
> + recovered `ARCHETYPE_SHOT_TYPE` map + callsite contracts. No stubs. No asset re-render.
> No proof packet.

---

## Discovery matrix (pre-edit)

| Path | `origin/main` | local / worktrees / history | Disposition |
|------|---------------|-----------------------------|-------------|
| `scripts/manga/panel_planning_rules.py` | ABSENT | ABSENT (never in `git log --all`) | **authored** |
| `scripts/manga/validate_chapter_composition_grammar.py` | ABSENT | ABSENT (HR rules marked §6.2 ABSENT) | **authored** |
| `scripts/manga/annotate_l2_composition_legal.py` | ABSENT | ABSENT (GOVERNED in rules, never shipped) | **authored** |
| Equivalent under other names | `composition_grammar.py` G1–G8 only | partial — not a substitute for planning/chapter/annotate APIs | UNCHANGED |
| Open-PR overlap | none on these module paths | — | — |
| PROGRAM_STATE next manga blocker | stillness post-merge proof re-run | still true; this lane clears module half only | — |

### Blocked callsites (pre-recovery)

- `generate_assembly_manifest.py`: `from panel_planning_rules import shot_type_for_archetype`; `from validate_chapter_composition_grammar import validate_chapter_composition_grammar`
- `assemble_from_bank.load_manifest`: lazy imports of `validate_manifest_composition_planning` + `validate_chapter_composition_grammar`

### Tests added

`tests/manga/test_stillness_module_recovery.py` — 7 tests:
- archetype → shot_type map
- HR-F01 half-person FAIL on full_render
- bust legal on defocus derivation
- HR-U16 FAIL after >6 abstract
- HR-U16 PASS with re_establish
- annotate legality field inference
- annotate sidecar write

**Result:** `7 passed` (`PYTHONPATH=scripts/manga python3 -m pytest tests/manga/test_stillness_module_recovery.py -q`)

---

## Provenance per module

| Module | Source |
|--------|--------|
| `panel_planning_rules.py` | `ARCHETYPE_SHOT_TYPE` recovered from pre-#5428 `generate_assembly_manifest` inline map (`206e6e8d^`); planning checks from HR rules §2–§3 + `G1_MATRIX`; `shared_meal_table_medium→re_establish` for HR-U16 repair archetype |
| `validate_chapter_composition_grammar.py` | Authored from `MANGA_COMPOSITION_GRAMMAR_SPEC.md` §6.2 + HR-U01/U16/U17/F11; Finding dataclass matches assembler callsite |
| `annotate_l2_composition_legal.py` | Authored from HR rules §10 L2 legality extensions |

```
research:  artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md;
           artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md;
           artifacts/qa/MANGA_BLOB_PREVENTION_CLOSEOUT_2026-07-10.md
documents: docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md;
           docs/PEARL_ARCHITECT_STATE.md; specs/AI_MANGA_PIPELINE_SUMMARY.md;
           docs/MANGA_IMPLEMENTATION_OUTLINE.md;
           docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md;
           docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md
builds_on: ws_manga_human_readability_rules_20260709;
           ws_manga_prompt_builder_v3_20260710;
           ws_stillness_postmerge_proof_recovery_20260711
inventory: EXTENDS stillness proof prerequisites only; never REDUCED
```

---

## Exact next action (follow-on stillness lane)

1. Re-render four semantic-gap L2s to **blob-gate PASS** RGBA cutouts (prior locals were blob-FAIL).
2. Run `annotate_l2_composition_legal.py --write` on stillness L2 dir.
3. `generate_assembly_manifest.py` → `assemble_from_bank.py` → honest packet under
   `artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/`.

---

## Required tags

```
manga-stillness-module-recovery=<merge-sha>
manga-stillness-module-recovery-panel-planning=authored
manga-stillness-module-recovery-chapter-grammar=authored
manga-stillness-module-recovery-l2-annotate=authored
manga-stillness-module-recovery-tests=7 passed (tests/manga/test_stillness_module_recovery.py)
manga-stillness-module-recovery-closeout=artifacts/qa/MANGA_STILLNESS_MODULE_RECOVERY_CLOSEOUT_2026-07-11.md
manga-stillness-module-recovery-blocker=none
```

---

## Cleanup ledger

| Item | Action |
|------|--------|
| Hot coordination TSVs / PROGRAM_STATE | untouched |
| Sparse worktree `/tmp/phoenix_stillness_module_recovery_20260711` | disposable after merge |
| Asset re-render / proof packet | deferred to follow-on lane |
