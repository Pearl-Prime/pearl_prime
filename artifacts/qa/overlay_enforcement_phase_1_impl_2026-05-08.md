# Overlay enforcement Phase 1 — implementation notes

**Full session record (git incidents, failed tasks, recovery):** [`overlay_enforcement_phase_1_session_record_COMPLETE_2026-05-08.md`](./overlay_enforcement_phase_1_session_record_COMPLETE_2026-05-08.md)

**PROJECT_ID:** PRJ-PEARL-PRIME-Q-GATES  
**Cap:** PER-CHAPTER-OVERLAY-ENFORCEMENT-V1 (Pearl_Architect state entry PER-CHAPTER-OVERLAY-ENFORCEMENT-V1-01)  
**PR stack:** Builds on Sprint-1/YELLOW ITEM-1 (PR **#941**) refrain allowlist wiring; aligns with sibling PR intent **#947** (gates / Prime Q). ITEM-2 entry remains in YAML (explicit `todo` unchanged).

## What shipped (Phase 1 only)

| Area | Change |
|------|--------|
| Schema | Each allowlist row supports `overlay_rule` (`none` default) and `overlay_param` (empty map default). All **43** production entries explicitly set `overlay_rule: none` + `overlay_param: {}`. |
| Loader | `_load_refrain_allowlist()` normalizes unknown `overlay_rule` strings to `none`; coerces `overlay_param` to `{}` when absent or non-map. |
| Gate | `_repeated_phrase_violations` adds optional kwargs for tests (`allowlist`, `chapter_texts`, `compression_chapters_1based`). Implements structural rules when `overlay_rule` ≠ `none`: `density_ceiling`, `presence_floor`, `drift_detection`, `absence_guard`. |
| Reporting | Each violation dict includes `rule_fired` ∈ {`book_wide_cap`, `overlay`}, mirrored `rule` string (`book_wide_cap` or `overlay:<kind>` per overlay spec shorthand), optional `chapter`, and kind-specific diagnostics (`overlay_rule_kind`, limits, excluded class, structural class). Book-wide offenders include `chapter: null` for stable sorting. |

Back-compat reasoning: production allowlist Phase 1 only enables the overlay evaluator after the unchanged book-wide 4–6 gram counting pass; overlay loop skips every loaded entry because `overlay_rule` is uniformly `none`, so **no new overlay violations appear** until Phase 2 assignments.

Minor output delta vs pre-Phase-1: metrics `repeated_phrase_violations` rows now expose `rule_fired`, `rule`, and `chapter` (nullable) alongside existing keys.

## Presence / absence semantics (12-ch backbone)

- **opening**: chapter index 1.  
- **mid**: indices 4–8 inclusive (when manuscript has those chapters).  
- **presence_floor**: fails a structural class only when **at least one applicable chapter exists** but none contain the exact allowlist phrase (word-token aligned with gate tokenization `[a-z0-9']+`).  
- **climax**: indices 9–10 when present.  
- **absence_guard** + `compression_chapters`: uses caller-supplied `compression_chapters_1based`; production orchestration wires this in Phase 2+.

## Validation performed (this session)

- **pytest:** `tests/quality/test_overlay_enforcement.py` (**10 cases**: book-wide cap + four overlay kinds + compression hook + overlay none regression + composition + invalid enum fallback) plus `tests/test_book_quality_gate.py` — PASS.  
- **Reference manuscript smoke:** `artifacts/qa/_scratch_pp_ahjan_genz_anxiety/deep_book_6h/book.txt` via `evaluate_book_quality(..., runtime_format_id='deep_book_6h')` → `repeated_phrase_violations` capped slice length **20**, **all `rule_fired=book_wide_cap`**, zero `overlay` hits (consistent with Phase 1 defaults). Phase 2 should re-run the curated 50 344 w reference corpus cited in PER-CHAPTER spec if word count must match that artefact exactly.  
- **`scripts/ci/audit_llm_callers.py`:** scoped scan on changed paths `{ phoenix_v4/quality/book_quality_gate.py, tests/quality/, config/quality/refrain_allowlist.yaml }` → **violation_count: 0** (full-repo audit may time out locally on very large trees; CI runs the authoritative scan).  
- **Production readiness gates 1–7:** `scripts/run_production_readiness_gates.py` was **not captured to completion locally** within wall-clock limits (upstream steps such as coverage/pipeline dominate). **Pearl_Dev / Pearl_GitHub should run the bundle in CI/preflight** after push; Phase 2 revalidation remains required regardless.

## HANDOFF_NEXT

- **Pearl_Architect:** ratify per-entry Phase 2 `overlay_rule` + `overlay_param` table (overlay spec section 6) before Prime enables non-`none` rows.  
- **Pearl_Dev (Phase 2):** Assign overlay types per overlay spec section 6 + validate reference renders; Phase 3 (ITEM-2 removal) only after drift/cap proves `your nervous system` without masking.
