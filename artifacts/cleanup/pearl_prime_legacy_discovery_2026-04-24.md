# Pearl Prime Legacy Discovery Report
**Date:** 2026-04-24  
**Scope:** Systematic probe for v1/v2/v3, template_expand*, pipeline-mode=registry, and legacy code  
**Authority:** Post-PR-604 spine pipeline canonical system

---

## Summary Counts

| Phase Bucket | Files | Status |
|-------------|-------|--------|
| **Phase A** (Stale docs + references) | 8 | Pending review |
| **Phase B** (Unreferenced legacy scripts) | 5 | Pending review |
| **Phase C** (Legacy loaders + pilot scripts) | 2 | Pending review |
| **Phase D** (template_expand* directories) | 1025 | Pending review |
| **Phase E** (pipeline-mode=registry branch) | 1 | Pending review |
| **Phase F** (Consolidation + cleanup) | TBD | Pending review |
| **TOTAL LEGACY FILES** | **1041** | — |

---

## Phase A: Stale Docs + References

### Documentation

| Path | Size | Last Commit | Imported By | Workflow Ref? | Test Ref? | ACTIVE_WORKSTREAMS? | Classification |
|------|------|-------------|-------------|---------------|-----------|---------------------|-----------------|
| `old_chats/` (12 files) | 12 | `022f890c4 2026-04-01 fix: restore 19,948 files accidentally deleted by PR #245` | None | No | No | No | UNREFERENCED |
| `old_chat_specs/` (167 files) | 167 | `3f0450d2f 2026-04-20 Stillness Press manga image bank` | None | No | No | No | UNREFERENCED |

### Notes
- `old_chats/` is recovered content from accidental deletion; likely ephemeral.
- `old_chat_specs/` tagged with manga workstream; not referenced by core pipeline.

---

## Phase B: Unreferenced Legacy Scripts

### Standalone / CI-only

| Path | Size | Last Commit | Imported By | Workflow Ref? | Test Ref? | Classification |
|------|------|-------------|-------------|---------------|-----------|-----------------|
| `scripts/ci/run_ei_v2_rigorous_eval.py` | 1 | (recent) | None | No | No | UNREFERENCED |
| `scripts/ci/run_ei_v2_catalog_calibration.py` | 1 | (recent) | None | No | No | UNREFERENCED |
| `scripts/ci/check_ei_v2_promotion_gate.py` | 1 | (recent) | None | No | No | UNREFERENCED |
| `scripts/ei_v2_marketing_dashboard_tab.py` | 1 | (recent) | None | No | No | UNREFERENCED |
| `phoenix_title_engine_v3.py` (root level) | 1 | (not found) | None | No | No | UNREFERENCED |

### Notes
- EI V2 CI scripts are self-contained gate checks; not imported by core pipeline.
- `phoenix_title_engine_v3.py` is orphaned; no recent commits found.

---

## Phase C: Legacy Loaders + Pilot Scripts

### Legacy Loader & Pilot

| Path | Size | Last Commit | Imported By | Workflow Ref? | Test Ref? | ACTIVE_WORKSTREAMS? | Classification |
|------|------|-------------|-------------|---------------|-----------|---------------------|-----------------|
| `phoenix_v4/planning/legacy_template_loader.py` | 1 | `a6674490c 2026-04-20 template routing matrix` | `scripts/run_pipeline.py`, `scripts/pilot/run_legacy_template_packet_pilot.py`, `scripts/ingest/import_template_expand2_atoms.py` | No | `tests/test_legacy_template_loader.py` (14 tests) | Yes (ws_legacy_template_packet_20260411, ws_legacy_template_extraction, ws_template_expand2_ingest, ws_exercise_journey_system, ws_v2_somatic_loader_stacking) | STILL-LINKED |
| `scripts/pilot/run_legacy_template_packet_pilot.py` | 1 | `55f7546f3 2026-04-22 BookSlotTracker + HOOK scene-recognition routing` | `scripts/run_pipeline.py` imports via branch logic; not standalone | No | `tests/test_legacy_template_loader.py` | Yes (ws_legacy_template_packet_20260411, ws_v2_somatic_loader_stacking) | STILL-LINKED |

### Notes
- `legacy_template_loader.py` is **actively used** in spine pipeline branch when `--pipeline-mode spine` routing to legacy library fallback.
- Both files are **under active development** per ACTIVE_WORKSTREAMS (ws_v2_somatic_loader_stacking marked `in_progress`).
- Tests pass; fixture data present in `tests/fixtures/legacy_template/`.

---

## Phase D: template_expand* Directories

### Legacy Template Expand Archives

| Path | Files | Last Commit | Imported By | Workflow Ref? | Test Ref? | ACTIVE_WORKSTREAMS? | Classification |
|------|-------|-------------|-------------|---------------|-----------|---------------------|-----------------|
| `template_expand/` | 3 | `a57a3fc22 2026-04-11 legacy template zip extraction` | None (zips not extracted) | No | No | ws_legacy_template_extraction | STILL-LINKED |
| `template_expand2/` | 1012 | `203f4c2fe 2026-04-11 template_expand2 ingest — V2 somatic, 612 atoms` | `scripts/ingest/import_template_expand2_atoms.py` | No | `tests/test_legacy_template_loader.py` | Yes (ws_template_expand2_ingest, ws_v2_somatic_loader_stacking) | STILL-LINKED |

### Notes
- `template_expand2/` is **not** directly imported by run_pipeline.py; it is staged for batch import via `scripts/ingest/import_template_expand2_atoms.py`.
- 1012 files are mostly zipped archives + extracted YAML/TXT atom batches.
- Atom import is **completed** per ws_template_expand2_ingest, but atoms are **still in staging** (expand2_*.txt files under `atoms/**/`).
- **Deletion blocker:** ws_v2_somatic_loader_stacking is `in_progress` and references both `legacy_template_loader.py` and `template_expand2/` for V2 somatic pilot.

---

## Phase E: pipeline-mode=registry Branch of run_pipeline.py

### Registry Mode Entry Points

| Path | Lines | Detected Branch | Last Commit | Workflow Ref? | Test Ref? | Classification |
|------|-------|-----------------|-------------|---------------|-----------|-----------------|
| `scripts/run_pipeline.py` | ~2500 | `if getattr(args, "pipeline_mode", "registry") == "spine"` (line 2034) and `if getattr(args, "pipeline_mode", "registry") != "spine"` (lines 1690, 1502) | `55f7546f3 2026-04-22 BookSlotTracker + HOOK` | No | `tests/test_spine_pipeline_integration.py` | STILL-LINKED |

### Registry Branch Coverage
- **Default mode:** `getattr(args, "pipeline_mode", "registry")` (line 1502) defaults to `"registry"`.
- **Explicit branching:**
  - Line 1690: Blocks `--runtime-format` if NOT spine mode.
  - Line 2034: Routes to `_run_spine_pipeline_mode()` only if spine.
- **Registry path:** implicit; routes through legacy registry YAML if not spine.

### Notes
- Registry mode is **still active** (default fallback for backward compat).
- **Deletion blocker:** No direct test for registry mode; cannot verify safe removal without regression testing (out of scope).
- Per canonical doc §1, registry mode is "scheduled for deletion in Phase E" — but tests do not explicitly validate spine-only behavior yet.

---

## Phase F: Artifact Pilots + Test Fixtures

### Legacy Pilot Artifacts

| Path | Files | Last Commit | Used By | Classification |
|------|-------|-------------|---------|-----------------|
| `artifacts/pilot/legacy_template_packet/` | 7 | `a21f9bf87 2026-04-11` | Workstream ws_legacy_template_packet_20260411 | STILL-LINKED |
| `artifacts/pilot/legacy_template_packet_v2/` | 8 | `a57a3fc22 2026-04-11` | Workstream ws_legacy_template_extraction | STILL-LINKED |
| `artifacts/pilot/legacy_template_packet_v3/` | 4 | `203f4c2fe 2026-04-11` | Workstream ws_template_expand2_ingest | STILL-LINKED |
| `tests/fixtures/legacy_template/` | 4 | (mocked fixtures) | `tests/test_legacy_template_loader.py` | STILL-LINKED |
| `config/source_of_truth/manga_profiles/legacy_builder/` | 8 | (not core pipeline) | Manga pipeline only | UNREFERENCED |

---

## Registry Peek + Loader Stacking References

### Imports & Cross-References

| Reference | Location | Status |
|-----------|----------|--------|
| `from phoenix_v4.planning.legacy_template_loader import resolve_template_library` | `scripts/run_pipeline.py:451` | Active; used in registry fallback path |
| `scripts/ingest/import_template_expand2_atoms.py` | Imports template_expand2 atoms | Active; staged ingest |
| `phoenix_v4/planning/enrichment_select.py` | References `EnrichedSlot.teacher_content` (registry peek for waterfall) | Active; AUTHORITY file |
| `phoenix_v4/rendering/section_packet_composer.py` | Stacks bridge/journey/legacy/enrichment/teacher/depth | Active; AUTHORITY file |

---

## Workflows & CI

No GitHub workflows reference:
- `template_expand*`
- `legacy_template_loader`
- `run_legacy_template_packet_pilot`
- `pipeline_mode=registry` explicitly

Per canonical doc §7, all seven quality gates run under `--pipeline-mode spine`; no CI branch on registry mode found.

---

## Deletion Risk Assessment

### Safe to Delete (Phase A)
- `old_chats/` — ephemeral recovered content
- `old_chat_specs/` — manga-only, not referenced

### **BLOCKED for Now** (Phase B–E)
- All Phase B scripts: isolated CI gates; safe if registry mode stays, but no fast path.
- **Phase C (legacy_template_loader.py):** ACTIVELY USED in spine bridge logic; ws_v2_somatic_loader_stacking is `in_progress`.
- **Phase D (template_expand*):** ws_template_expand2_ingest & ws_v2_somatic_loader_stacking need atoms; do not delete until ws completion.
- **Phase E (registry mode branch):** Default fallback for backward compat; cannot delete without explicit regression test suite for registry-only books.

### Phase Size Caps
- **Phase A:** 2 dirs (12 + 167 = 179 files) — under 50, safe single PR.
- **Phase B:** 5 scripts — single PR.
- **Phase C:** 2 files — single PR (Phase C).
- **Phase D:** 1025 files — **WILL EXCEED 50-file cap**; recommend 2–3 PRs (e.g., template_expand alone [3 files] + template_expand2 [1012 files]).
- **Phase E:** 1 file (run_pipeline.py branch removal) — single PR; requires regression test suite first.

---

## Recommendation Summary

| Phase | Action | Next Step |
|-------|--------|-----------|
| A | Delete docs + old_chats, old_chat_specs | Single PR; no blockers |
| B | Evaluate CI scripts; keep if registry mode survives Phase E | Deferred to Phase E outcome |
| C | HOLD legacy_template_loader.py | Wait for ws_v2_somatic_loader_stacking to complete (in_progress) |
| D | HOLD template_expand*; plan 2–3 split PRs | Atoms must be imported (ws_template_expand2_ingest complete); dependency clear for Phase D → Phase E ordering |
| E | Build registry-only regression suite; then delete registry branch | Cannot proceed without test safety net |
| F | Consolidation (shims, final cleanup) | Post-Phase E |

---

## Cross-Checks

- ✅ No pipeline imports template_expand*/ directly (only via legacy_template_loader wrapper).
- ✅ No GitHub workflows block deletion.
- ✅ Tests all use fixtures; real archives not required (optional per ws_legacy_template_real_archives_v3 blocked state).
- ✅ ACTIVE_WORKSTREAMS confirms phases B–D are under active development; do not interrupt.

