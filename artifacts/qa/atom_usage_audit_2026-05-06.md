# Atom Usage Audit — 2026-05-06

**Status:** F2 fix shipped this PR. F3 + F7 deferred to Pearl_Architect.

## 1. Inventory summary

- Total `CANONICAL.txt` entries: **~8,051** (per `artifacts/qa/atom_inventory_2026-05-06.tsv`)
- Layout: `atoms/<persona>/<topic>/<slot>/CANONICAL.txt`
- 14 personas; ~16 topics each; 12 canonical slot types (HOOK, SCENE, STORY, REFLECTION, TEACHER_DOCTRINE, EXERCISE, INTEGRATION, PIVOT, PERMISSION, TAKEAWAY, THREAD, QUOTE)
- Inventory TSV columns: `persona`, `topic`, `slot`, `file`

## 2. Code-path inventory

See `artifacts/qa/atom_load_path_inventory_2026-05-06.tsv` for the complete row-level scan. Key sites:

| File | Symbol | Role |
|---|---|---|
| `phoenix_v4/planning/registry_resolver.py:51` | `_TEACHER_OVERLAY_TYPES` | Frozenset of section types that get teacher-mode overlay |
| `phoenix_v4/planning/registry_resolver.py:56` | `_PERSONA_OVERLAY_TYPES` | Frozenset of section types that get persona-mode overlay (HOOK, SCENE, STORY) |
| `phoenix_v4/planning/registry_resolver.py:61` | `_TEACHER_TYPE_MAP` | Maps registry section_type → on-disk teacher-bank dir name list |
| `phoenix_v4/planning/registry_resolver.py:429` | `_TEACHER_TYPE_MAP.get(sec_type, [sec_type])` | Lookup site — F2 fix applies here |
| `phoenix_v4/planning/chapter_plan.py:8` | `VALID_SLOT_TYPES` | Validation set for chapter slot plans |
| `phoenix_v4/planning/enrichment_select.py:35` | `_TEACHER_TYPE_MAP` import | Re-exported for enrichment selection |

## 3. Coverage matrix

12 canonical slots × 14 personas × ~16 topics. Every persona-topic-slot tuple either has a CANONICAL.txt + locale variants, or is below threshold (handled by SPEC-739-THRESHOLD-01 floor = 3 variants).

## 4. Findings

### F1 — `deep_book_6h` merge dropped 9/12 slot types (P0) — **FIXED prior session**

The `_merged_persona_atoms_deep_6h` helper in `phoenix_v4/planning/enrichment_select.py` previously dropped slot types not explicitly listed. Already fixed in a prior session and shipped to origin/main. Reference: this is now reachable via `git log` for that helper's history.

### F2 — `TEACHING` ghost atoms (P1) — **FIXED THIS PR**

**Problem:** Some teachers (notably `ahjan`) author teacher-bank section files under the directory name `TEACHING/` rather than `COMPRESSION/` or `REFLECTION/`. The pre-fix `_TEACHER_TYPE_MAP["TEACHER_DOCTRINE"]` only listed `["COMPRESSION", "REFLECTION"]`, so the slot-lookup in `registry_resolver.py:429` (`_TEACHER_TYPE_MAP.get(sec_type, [sec_type])`) never tried `TEACHING/`. Result: ~100 ahjan TEACHING/CANONICAL files were unreachable via slot lookup → "ghost atoms" (existed on disk but never loaded).

**Fix (this PR):** One-line addition — `"TEACHING"` appended to the alias list for `TEACHER_DOCTRINE`:

```python
_TEACHER_TYPE_MAP = {
    "TEACHER_DOCTRINE": ["COMPRESSION", "REFLECTION", "TEACHING"],
    ...
}
```

Plus a 3-line comment block above the map explaining why the alias exists (so a future maintainer doesn't strip it as dead).

**Verification:** Pre-fix the slot lookup for `TEACHER_DOCTRINE` returned only `COMPRESSION/CANONICAL` + `REFLECTION/CANONICAL` content for ahjan. Post-fix it also reaches `TEACHING/CANONICAL`. Ghost-atom count for TEACHING-named teacher-bank files drops to 0.

### F3 — `QUOTE` atoms unrouted (P2) — **DEFERRED**

`atoms/<persona>/<topic>/QUOTE/CANONICAL.txt` files exist (~9 affected) but no entry in `_TEACHER_TYPE_MAP`, no membership in `_PERSONA_OVERLAY_TYPES`, no membership in `_TEACHER_OVERLAY_TYPES`. They never load.

**Routing question:** Should QUOTE be a persona-mode overlay (like HOOK/SCENE/STORY) or a teacher-mode overlay, or its own pool? Architectural decision — DEFERRED to Pearl_Architect 7-cap-entry batch under cap entry **QUOTE-ATOM-ROUTING-01**.

### F4-F6 — informational

- F4: `atoms/midlife_women/anxiety/{COMPARISON,GRIEF,OVERWHELM,SHAME}/CANONICAL.txt` exists; arc-routing decision pending under `proj_pearl_prime_bestseller_rebase_20260425`.
- F5: SCENE atoms only present for some persona×topic combos — by design (SCENE is optional pool, not a required slot per Writer Spec §3).
- F6: 14 personas × ~16 topics × 12 slots ≠ exactly 8,051; the gap is below-threshold tuples that don't need ≥3 variants per SPEC-739-THRESHOLD-01.

### F7 — first-match vs union pool semantics (P3) — **DEFERRED**

`_TEACHER_TYPE_MAP` lookup behavior in `registry_resolver.py:429`:

```python
for dir_name in _TEACHER_TYPE_MAP.get(sec_type, [sec_type]):
    # accumulate? or first-match?
```

Current implementation iterates and accumulates, but the contract isn't documented. Should the multi-alias case (now `["COMPRESSION", "REFLECTION", "TEACHING"]` for TEACHER_DOCTRINE) union all matching atoms across directories, or first-match by author preference?

Architectural decision — DEFERRED to Pearl_Architect 7-cap-entry batch under cap entry **TEACHER-POOL-SEMANTICS-01**.

## 5. Ghost atom counts

| Period | Count | Slots affected |
|---|---|---|
| Pre-this-PR | ~109 | TEACHING (~100, F2) + QUOTE (~9, F3) |
| Post-this-PR | 9 | QUOTE (F3) only — pending Architect ruling |

## 6. Test verification

- `pytest tests/test_enrichment_select.py` — pass (existing tests cover the merge helper)
- `pytest tests/test_pilot_feature_parity.py` — pass
- `pytest tests/test_book_qa_pipeline_integration.py` — pass
- LLM tier audit (`audit_llm_callers --fail-on-violation`) — clean (0 violations)

## Deferrals (named for Pearl_Architect 7-cap-entry batch)

- **F3 / QUOTE-ATOM-ROUTING-01** — Pearl_Architect rules; Pearl_Dev applies
- **F7 / TEACHER-POOL-SEMANTICS-01** — Pearl_Architect rules; Pearl_Dev applies (or close-not-needed)
