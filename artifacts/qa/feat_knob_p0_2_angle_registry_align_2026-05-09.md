# FEATURE-KNOB P0-2 — CatalogPlanner ↔ `angle_registry.yaml` alignment

**Project ID:** PRJ-PEARL-PRIME-FEATURE-UTILIZATION  
**Date:** 2026-05-09  
**Cap:** FEATURE-KNOB-CATALOG-VARIATION-V1-01  
**Audit ref:** PR #960 / `artifacts/qa/feature_knob_utilization_audit_2026-05-08.md`

---

## 1. Before

`_derive_angle` in `phoenix_v4/planning/catalog_planner.py` used only a **hard-coded** `topic_to_domain` map plus `series_templates` persona/domain scoring, then returned **`{topic_id}_general`** with no link to `config/angles/angle_registry.yaml`. Registry vocabulary was effectively **dead** for catalog planning.

---

## 2. After

1. **SSOT first:** `catalog_planner_resolution.topic_angle_map` in `config/angles/angle_registry.yaml` maps catalog `topic_id` → `angle_id` (must exist under `angles:`).
2. **Legacy heuristic second:** unchanged series/domain/persona_affinity selection.
3. **Fallback:** `{topic_id}_general` only if registry + heuristic both miss — **`logging.warning`** + **`last_angle_resolution_meta()`** flags `heuristic_general_fallback`.
4. **Strict mode:** `produce_single(..., angle_strict=True)` → **`AngleResolutionError`** when no registry or series resolution.

---

## 3. Files touched (WRITE_SCOPE)

| Path | Role |
|------|------|
| `config/angles/angle_registry.yaml` | Added `catalog_planner_resolution.topic_angle_map` for core catalog topics |
| `phoenix_v4/planning/catalog_planner.py` | Registry load, meta, `angle_strict`, `_derive_angle` order |
| `tests/phoenix_v4/planning/test_catalog_planner_angle_registry.py` | Hit / fallback / strict / live integration |
| `docs/specs/ANGLE_REGISTRY_SSOT_V1_SPEC.md` | Contract |
| `artifacts/qa/feat_knob_p0_2_angle_registry_align_2026-05-09.md` | This note |

---

## 4. Tests

```bash
PYTHONPATH=. python3 -m pytest tests/phoenix_v4/planning/test_catalog_planner_angle_registry.py -v
```

**Result:** **4 passed**.

---

## 5. Example resolution

- `topic_id=relationship_anxiety` → registry maps to **`HIDDEN_TRUTH`** (live repo integration test).

---

## 6. Follow-up workstream

- **`ws_feat_knob_p0_3`** — explicit `angle_id` per catalog row + row format (out of scope here).
