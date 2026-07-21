# MANGA A/B/C PREREQUISITE LEDGER

**Date:** 2026-07-12  
**Scope:** `manga-passb-reading-graph`, `manga-spread-layout-solver`, `manga-jlreq-sfx-lettering`  
**Status:** refreshed from live repo-native code + proof roots

---

## Input Truth

Expected prior analysis artifacts named below were **not present** on `origin/main` at execution time:

- `artifacts/analysis/MANGA_ABC_PREREQUISITE_LEDGER_2026-07-12.md`
- `artifacts/analysis/MANGA_PROOF_WAVE_CLOSEOUT_2026-07-12.md`
- `artifacts/analysis/MANGA_GREEN_FINAL_VERDICT_2026-07-12.md`
- `artifacts/analysis/MANGA_GREEN_BLOCKER_LEDGER_2026-07-12.md`

Canonical replacements are established by this wave at those same paths. Existing authority that **was** present and read first:

- `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md`
- `phoenix_v4/manga/chapter/bubble_render_v2.py`
- `phoenix_v4/manga/chapter/cjk_text_shaper.py`
- `phoenix_v4/manga/chapter/page_compose.py`
- `phoenix_v4/manga/chapter/page_frame.py`
- `scripts/manga/render_v5_episode.py`

---

## Deliverable Matrix

| Lane | Code Surface | Test Surface | Proof Root | Honest Status |
|------|--------------|--------------|------------|---------------|
| A | `phoenix_v4/manga/chapter/reading_graph.py` | `tests/manga/test_reading_graph.py` | `artifacts/qa/manga_passb_reading_graph_2026-07-12/` | **EXECUTED-REAL** |
| B | `phoenix_v4/manga/chapter/spread_layout_solver.py` + `page_frame.py` integration | `tests/manga/test_spread_layout_solver.py` + `tests/manga/test_page_frame.py` | `artifacts/qa/manga_spread_layout_solver_2026-07-12/` | **EXECUTED-REAL** |
| C | `phoenix_v4/manga/chapter/jlreq_lettering.py` + `bubble_render_v2.py` + `cjk_text_shaper.py` hardening | `tests/manga/test_jlreq_lettering.py` + `tests/manga/test_bubble_render_v2.py` + `tests/manga/test_cjk_text_shaper.py` | `artifacts/qa/manga_jlreq_sfx_lettering_2026-07-12/` | **EXECUTED-REAL with one partial sub-surface** |

---

## Lane Notes

### A — Pass-B reading graph

- Adds a machine-checkable page reading graph with nodes, edges, reading sequence, and validation issues.
- Validates panel-order and bubble-order backtracking against page geometry and reading direction.
- Proof summary reports `panel_count=4`, `bubble_count=4`, `panel_mismatch_count=0`, `bubble_mismatch_count=0`.

### B — Spread layout solver

- Replaces spread-as-width-doubling with a dedicated solver that chooses splash/standard/double-spread and emits explicit constraints.
- Solver outputs normalized panel assignments, constraint verdicts, and a real facing-page spread geometry.
- Proof summary reports `resolved_page_type=double_spread`, `spread=true`, `valid=true`, `failures=[]`.

### C — JLREQ + SFX lettering

- Adds JLREQ-aware dialogue planning, vertical glyph orientation handling, and SFX placement that avoids occupied bubble regions.
- Integrates planner output into `bubble_render_v2` manifests/layout records and hardens `cjk_text_shaper.py` for non-path font objects.
- Honest partial: vertical+furigana is **not** fully executed as vertical ruby layout yet; runtime labels this as `partial_vertical_furigana_deferred` and falls back safely to horizontal ruby.

---

## Proof Tags

- `manga-passb-reading-graph=pending_branch_head_after_commit`
- `manga-spread-layout-solver=pending_branch_head_after_commit`
- `manga-jlreq-sfx-lettering=pending_branch_head_after_commit`
- `manga-proof-wave=completed`

