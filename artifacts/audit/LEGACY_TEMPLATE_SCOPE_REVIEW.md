# Legacy Template Packet — Scope Review

**Project:** `proj_state_convergence_20260328`  
**Subsystem:** `core_pipeline`, repo coordination  
**Date:** 2026-04-11  
**Evidence:** PR [#383](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/383) merged to `main` as `acd9c1026034f7902d2fa4c7bc34600e8faaad7a` (squash).

---

## Verification record (2026-04-11)

| Check | Command / artifact | Result |
|-------|---------------------|--------|
| Unit tests (loader + composer) | `PYTHONPATH=. python3 -m pytest tests/test_legacy_template_loader.py tests/test_section_packet_composer.py -v` | **14 passed** (after CI-portable fixture commit on the PR branch) |
| Compile | `python3 -m py_compile phoenix_v4/planning/legacy_template_loader.py phoenix_v4/rendering/section_packet_composer.py scripts/pilot/run_legacy_template_packet_pilot.py` | **OK** |
| Pilot (side pipeline) | `PYTHONPATH=. python3 scripts/pilot/run_legacy_template_packet_pilot.py --topic anxiety --persona gen_z_professionals --teacher ahjan --output-dir /tmp/verify_legacy_pilot/` | **Exits 0**; writes `book.txt`, `section_packet_audit.json`, `word_budget.json` |
| GitHub required checks | Core tests, Release gates, EI V2 gates, Verify governance | **Pass** on merged PR |
| Non-required | Workers Builds: pearl-prime | **Fail** (known non-merge requirement per `docs/GITHUB_OPERATIONS_FRAMEWORK.md`) |

**Pilot honesty:** The pilot **runs successfully** end-to-end, but **output is thin** versus a 6h / 54k target when `template_expand/` chapter bridges and extracted V4 YAML are absent: enrichment + depth dominate; bridge and legacy scaffolds add little or nothing. The committed pilot report (`artifacts/pilot/legacy_template_packet/LEGACY_TEMPLATE_PACKET_REPORT.md`) documents **9,170** packet words vs **54,000** target (**~83% short**), **0/102** sections with legacy YAML, and **standard_book** (not `deep_book_6h`). A local run without `template_expand/` on disk produced **~8.4k** packet words and **no** `bridge` / `legacy_template` in `sources_used` — consistent with “thin until archives and bridges exist in the environment.”

**CI note:** The first push failed Core tests because integration tests assumed `template_expand/chapter_bridges_all.md` and `01_hooks.py` on disk; those paths are **not** tracked in this repo. A follow-up commit on the same PR added **repo-local fixtures** (`tests/fixtures/legacy_template/chapter_bridges_sample.md`, `hooks_wordy.txt`) and pointed tests at them so **Core tests pass in CI** without external trees.

---

## Delivered (PR #383)

| Deliverable | File | Status | Evidence |
|-------------|------|--------|----------|
| Audit doc | `artifacts/audit/LEGACY_TEMPLATE_INGEST_AUDIT.md` | Done | 83 lines |
| Template index | `config/templates/legacy_template_index.yaml` | Done | `schema_version: 1`; **10** `libraries` entries |
| Exercise metadata | `config/exercises/*.yaml` | Done | 3 files (`exercise_metadata_registry.yaml`, `journey_templates.yaml`, `thesis_outcome_map.yaml`) |
| Legacy loader | `phoenix_v4/planning/legacy_template_loader.py` | Done | 380 lines; **11** top-level `def` functions |
| Section composer | `phoenix_v4/rendering/section_packet_composer.py` | Done | 128 lines |
| Pilot runner | `scripts/pilot/run_legacy_template_packet_pilot.py` | Done | Runs anxiety topic; side pipeline only |
| Tests | `tests/test_legacy_template_loader.py` + `tests/test_section_packet_composer.py` | Done | **14** tests; fixtures under `tests/fixtures/legacy_template/` |
| Pilot report | `artifacts/pilot/legacy_template_packet/LEGACY_TEMPLATE_PACKET_REPORT.md` | Done | Gap analysis vs 54k; 0 legacy YAML |

---

## Not delivered (known gaps)

| Gap | Why | What’s needed | Priority |
|-----|-----|---------------|----------|
| V4 template YAML in loader output | Zips not extracted; `template_expand/audiobook_template_v4/` missing | Extract `audiobook_template_v4.zip` → `template_expand/_extracted/v4_therapeutic/…` (or verify layout after extract) | P0 |
| V2 libraries | Same | Extract V2 zips; align loader paths if layout differs | P1 |
| 0/102 legacy sections used | No extracted dirs | Depends on zip extraction + path verification | P0 |
| ~9.2k / 54k words (~83% short) | `standard_book` + thin registry pulls + no scaffolds | `deep_book_6h` or higher per-slot targets + templates + expansion | P1 |
| Exercise journey planner | Out of scope for this PR | New PR: planner consuming the 3 exercise configs | P2 |
| Mainline integration | Explicitly deferred | Wire into `run_pipeline.py` after evidence | P2 |
| `deep_book_6h` in pilot | Pilot used `standard_book` | Add optional `--format deep_book_6h` (or knob) and re-measure vs 54k | P1 |

---

## Questions before the next slice

1. **ZIP extraction:** Should the next PR **commit extracted YAML trees** (large) or document **owner-only extraction** into `template_expand/_extracted/`? The report recommends extract under `_extracted/`; binary size and review load matter.

2. **Exercise journey vs extraction:** **Extraction first** unblocks legacy scaffolds and is the highest leverage for word count; the planner is **parallel** but does not fix zero YAML.

3. **Downstream wiring:** Keep the pilot behind `scripts/pilot/` until **word count + structural quality** justify default pipeline wiring — likely **after** extraction and a `deep_book_6h` comparison run.

4. **Quality bar:** Structural coherence (bridges + scaffolds + depth) may matter as much as raw **54k**; treat **54k** as a format target, not the only merge gate for integration.

---

## Recommended next steps (dependency order)

1. **Extract V4 (and optionally V2) zips** to the documented layout → re-run pilot → measure legacy hit rate and words.
2. **Adjust loader** if on-disk layout differs from `chapter_NN/section_NN/variant_F*.yaml`.
3. **Re-run pilot** with `deep_book_6h` (or equivalent) to compare honestly to **54k**.
4. **Exercise journey planner** (separate PR) using existing exercise YAML.
5. **Wire into main pipeline** only after (3) shows acceptable density and quality.
