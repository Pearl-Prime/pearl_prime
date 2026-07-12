# MANGA STRUCTURAL COMPOSITION MVP — IMPLEMENTATION CLOSEOUT

**Date:** 2026-07-12  
**Branch:** `agent/manga-structural-composition-mvp`  
**Worktree:** `/Users/ahjan/phoenix_omega_worktrees/manga-structural-composition-mvp`  
**Base:** `origin/main` @ `1529f36839`

---

## STATUS

**COMPLETE (scoped MVP)** — Structural Composition MVP landed as a **separate runtime-enforcement layer** (seated table + standing room). Panel-type taxonomy left intact. Lettering **not** rewired. Universal horizon-ratio law **not** re-canonized.

---

## OBJECTIVE

Implement the strongest Structural Composition MVP pieces as a fail-closed runtime legality layer (support/contact graph, shared transform plan envelope, candidate quarantine, support overlay), bridged additively to `PANEL_TYPE_SYSTEM_V1` without collapsing layers.

---

## FILES_READ

| Path | Result |
|------|--------|
| `docs/PROGRAM_STATE.md`, Pearl GitHub onboarding / governance docs | read (session preflight) |
| `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` | **exists_live** — doctrine singleton |
| `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` | **exists_live** |
| `scripts/manga/generate_assembly_manifest.py` | **exists_live** |
| `scripts/manga/assemble_from_bank.py` | **exists_live** — still calls `bubble_render.render_bubbles_onto_panel` |
| `scripts/manga/panel_planning_rules.py` | **exists_live** |
| `scripts/manga/annotate_l2_composition_legal.py` | **exists_live** |
| `scripts/manga/validate_layer.py` | **exists_live** — compiled safe-zone QC incl. `lettering_safe_zones_clear` |
| `phoenix_v4/manga/chapter/bubble_render.py` | **exists_live** — assembler lettering path |
| `phoenix_v4/manga/chapter/bubble_render_v2.py` | **exists_live** — **not** assembler call path |
| `config/manga/panel_templates/iyashikei.yaml` | **exists_live** |
| `schemas/manga/composition_meta.schema.json` | **exists_live** |
| `scripts/manga/composition_grammar.py` | **exists_live** (G1–G6; horizon G3 remains implementation debt vs checklist) |
| `artifacts/analysis/MANGA_STRUCTURAL_COMPOSITION_MVP_ADD_ENHANCE_REVIEW_2026-07-12.md` | **ABSENT** in this checkout |
| `artifacts/analysis/MANGA_PANEL_TYPE_SYSTEM_V1_2026-07-12.md` | **ABSENT** in this checkout |
| `artifacts/analysis/MANGA_STRUCTURAL_COMPOSITION_MVP_MASTER_PREPROMPT_2026-07-12.txt` | **ABSENT** in this checkout |

### Authority alignment (lane 1)

| Proposed target | Verdict |
|-----------------|---------|
| `config/manga/composition_validation.yaml` | **missing_create_now** → created |
| `config/manga/structural_templates.yaml` | **missing_create_now** → created |
| `config/manga/panel_type_structural_bridge.yaml` | **missing_create_now** → created (bridge) |
| `scripts/manga/structural_composition.py` | **missing_create_now** → created |
| `scripts/manga/plan_panel_layout.py` | **missing_create_now** → created |
| `scripts/manga/validate_scene_assembly_visual.py` | **missing_create_now** → created |
| `schemas/manga/structural_*.schema.json` | **missing_create_now** → created |
| `schemas/manga/composition_meta.schema.json` | **exists_live** — adapted alongside; not replaced |
| `assemble_from_bank.py` lettering | **different_path_adapt** — left on v1; documented honesty |

---

## FILES_WRITTEN

- `config/manga/composition_validation.yaml`
- `config/manga/structural_templates.yaml`
- `config/manga/panel_type_structural_bridge.yaml`
- `schemas/manga/structural_bundle.schema.json`
- `schemas/manga/structural_plan.schema.json`
- `scripts/manga/structural_composition.py`
- `scripts/manga/plan_panel_layout.py`
- `scripts/manga/validate_scene_assembly_visual.py`
- `scripts/manga/tests/test_structural_composition.py`
- `scripts/manga/tests/test_scene_visual_acceptance.py`
- `artifacts/analysis/MANGA_STRUCTURAL_COMPOSITION_MVP_IMPLEMENTATION_CLOSEOUT_2026-07-12.md` (this file)
- `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` (minimal integration notes only)
- `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` (§13 implementation-status notes only)

---

## ACCEPTANCE_LAYER

| Deliverable | Layer |
|-------------|-------|
| Checklist doctrine singleton | SPECCED (operator) — unchanged authority |
| Composition grammar production assembler G-gates | CODE-WIRED (pre-existing) / pilot EXECUTED-REAL; not PROVEN-AT-BAR |
| Structural configs + schemas | **CONFIG-EXISTS** |
| Structural runtime (plan / validate / overlay / quarantine) | **CODE-WIRED** |
| Structural unit/routing tests (synthetic) | **CODE-WIRED** (pytest green) — not EXECUTED-REAL on catalog bank assets |
| Bank-panel EXECUTED-REAL structural proof | **ABSENT** this lane |
| Blind / PROVEN-AT-BAR | **ABSENT** |
| Lettering v2 / compiled safe-zone on assembler path | **ABSENT** (honest: not rewired) |

---

## TESTS_RUN

```
PYTHONPATH=scripts/manga python3 -m pytest \
  scripts/manga/tests/test_structural_composition.py \
  scripts/manga/tests/test_scene_visual_acceptance.py -v
→ 17 passed

PYTHONPATH=scripts/manga python3 -m pytest \
  scripts/manga/tests/test_assemble_from_bank.py -q
→ 5 passed, 4 failed, 4 skipped
```

**Assembler failures note:** `test_z_order_flip_changes_occlusion`, `test_l4_screen_blend_never_darkens`, `test_deterministic_output`, `test_provenance_table_written` fail with pre-existing `chapter composition grammar` rejects on synthetic fixtures. **This lane did not modify `assemble_from_bank.py`.** Failures are recorded as known ambient debt, not regressions from structural MVP files.

Covered structural assertions: missing graph, unknown category, support cycle, unsupported rotation, seated PIP contact (not area ratio), plan hash non-self-referential, renderer hash verify, overlay same transform path, quarantine without verdict, stale verdict refuse, accepted-only refuse.

---

## KNOWN_LIMITATIONS

- Scope only: `seated_table_scene` + `standing_room_scene`.
- `assemble_from_bank.py` does **not** default-consume structural plan envelopes (layer kept separate).
- Review memo / PANEL_TYPE_SYSTEM_V1 analysis artifacts were **absent** from checkout; bridge uses explicit `panel_type_id` keys in config without claiming those analysis files are live.
- No catalog L0 byte-verified EXECUTED-REAL structural overlay run in this closeout.
- Horizon-ratio G3 in `composition_grammar.py` unchanged (checklist still downgrades universal horizon law).

---

## OPEN_BLOCKERS

- Wire optional structural plan consume into assembler behind an explicit flag (next lane) without collapsing into panel-type system.
- Author/attach real bank structural bundles for stillness seated/standing panels → EXECUTED-REAL.
- Restore or land missing analysis anchors (`…ADD_ENHANCE_REVIEW…`, `…PANEL_TYPE_SYSTEM_V1…`) if they are intended SSOT.
- Ambient `test_assemble_from_bank` chapter-grammar fixture failures (pre-existing).

---

## NEXT_ACTION

1. Commit on `agent/manga-structural-composition-mvp` (this closeout).
2. Optional follow-on: `--structural-plan` consume path in assembler + stillness seated/standing EXECUTED-REAL packet.
3. Do not push unless operator requests; do not claim PROVEN-AT-BAR.

---

## Lettering / safe-zone honesty (lane 8)

| Claim | Evidence |
|-------|----------|
| Safe-zone QC exists | `scripts/manga/validate_layer.py` → `check_lettering_safe_zones_clear` |
| Genre-style v2 exists | `phoenix_v4/manga/chapter/bubble_render_v2.py` |
| Live assembler lettering path | `assemble_from_bank.py` imports `bubble_render.render_bubbles_onto_panel` (v1) |
| Structural MVP rewired lettering? | **No** |

