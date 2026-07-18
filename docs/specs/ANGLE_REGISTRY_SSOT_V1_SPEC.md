# ANGLE_REGISTRY_SSOT_V1 — CatalogPlanner angle resolution

**Cap:** FEATURE-KNOB-CATALOG-VARIATION-V1-01 (Phase 1 P0-2)  
**Audit:** `artifacts/qa/feature_knob_utilization_audit_2026-05-08.md` (PR #960)  
**Authority:** `docs/PEARL_ARCHITECT_STATE.md`

---

## 1. SSOT file

**Path:** `config/angles/angle_registry.yaml`

Top-level keys:

| Key | Purpose |
|-----|---------|
| `angles` | `angle_id` → structural fields (`arc_variant`, `chapter_1_role_bias`, `integration_reinforcement_type`, `framing_mode`, optional `arc_path`) |
| `catalog_planner_resolution` | CatalogPlanner-only mapping (does not replace arc-layer semantics) |

### `catalog_planner_resolution` (v1)

```yaml
catalog_planner_resolution:
  version: 1
  topic_angle_map:
    <topic_id>: <angle_id>   # angle_id must exist under angles:
```

---

## 2. Resolution order (`CatalogPlanner._derive_angle`)

When `series_id` / explicit `angle_id` do not already fix the angle:

1. **Registry SSOT** — `topic_angle_map[topic_id]`; accepted only if `angle_id` exists under `angles:`.
2. **Series heuristic** (legacy) — domain derived from `topic_id`, match `series_templates` entries with `angles`, score by `persona_affinity`.
3. **Fallback** — `{topic_id}_general` with `logging` warning and `last_angle_resolution_meta["heuristic_general_fallback"]=True`, unless `produce_single(..., angle_strict=True)`.
4. **Strict** — if step 1–2 yield nothing and `angle_strict=True`, raise **`AngleResolutionError`**.

---

## 3. Observability

After `produce_single`, callers may read **`CatalogPlanner.last_angle_resolution_meta()`** for:

- `source`: `angle_registry.topic_angle_map` | `series_template_domain_persona` | `topic_general_fallback` | `unresolved_strict`
- `registry_hit`, `series_heuristic_used`, `heuristic_general_fallback`
- `registry_angle_id`, `angle_id`

---

## 4. Follow-up

- **P0-1:** structural variation serialization (separate workstream).  
- **`ws_feat_knob_p0_3`:** explicit `angle_id` per catalog row + row format (depends on this SSOT).  
- No catalog regeneration in this phase.
