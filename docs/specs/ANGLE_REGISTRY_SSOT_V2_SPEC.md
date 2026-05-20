# ANGLE_REGISTRY_SSOT_V2 — CatalogPlanner angle resolution + parent_universal inheritance + journey blocks

**Status:** SUPERSEDES `docs/specs/ANGLE_REGISTRY_SSOT_V1_SPEC.md`
**Effective:** 2026-05-20
**Cap:** FEATURE-KNOB-CATALOG-VARIATION-V1-01 (Phase 2: catalog expansion)
**Authority:** `docs/PEARL_ARCHITECT_STATE.md`
**Catalog source of truth:** `docs/plans/ANGLE_CATALOG_V2_2026-05-20.md`
**Journey schema source:** `docs/plans/OPD-116-117_BOOK_ANGLE_AS_JOURNEY_PLAN_2026-05-20.md`

---

## 1. What changed from v1

| Concern | v1 | v2 |
|---|---|---|
| Total angles registered | 4 (`WRONG_PROBLEM`, `MAP_PROMISE`, `HIDDEN_TRUTH`, `ONE_LEVER`) | **91 named angles** (20 universal + 71 topic-specific) + 4 legacy soft-deprecated |
| Schema version | implicit | top-level `schema_version: 2` |
| Inheritance | none | `parent_universal: <UNIVERSAL_ID>` walks transitively; leaf fields override inherited |
| Display metadata | none | per-angle `display_name`, `core_frame`, `use_when` |
| Deprecation | none | `deprecated: true` + `successor_angle_id` + `deprecation_note` |
| Journey block | none | per-universal `journey: {named_object_by_topic, analogy_lens, core_mantras, layer_progression}` |
| `catalog_planner_resolution.version` | `1` | `2`; map expanded from 4 → 20 topic entries |
| Topic-angle map back-compat | n/a | v2 angles only; pointing the map at a `deprecated: true` angle raises a resolver warning |

Backward compatibility is preserved: v1 readers parse v2 files (additive schema), and the 4 legacy angles still resolve.

---

## 2. SSOT file layout

**Path:** `config/angles/angle_registry.yaml`

```yaml
schema_version: 2
authority: docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md
catalog_source: docs/plans/ANGLE_CATALOG_V2_2026-05-20.md
journey_schema_source: docs/plans/OPD-116-117_BOOK_ANGLE_AS_JOURNEY_PLAN_2026-05-20.md

angles:
  <UNIVERSAL_ANGLE_ID>:          # e.g. SILENT_VERDICT
    arc_variant: ARC_STANDARD_A_v6
    chapter_1_role_bias: destabilization | recognition
    integration_reinforcement_type: problem_inversion | orientation | revelation | mechanism_focus
    framing_mode: debunk | framework | reveal | leverage
    display_name: "The Silent Verdict"
    core_frame: "A judgment narrating in your voice that you've never heard out loud"
    successor_of: WRONG_PROBLEM        # optional — links v2 angle to a deprecated v1 ancestor
    journey:
      named_object_by_topic:
        <topic_id>: <string|null>      # null = TODO Pearl_Editor commission
      analogy_lens: <one of 7>
      core_mantras:
        - "<mantra line>"              # 3-5 lines; "TODO: ..." until Pearl_Editor authors
      layer_progression:
        - layer: 1..5
          phase: definition | pattern_recognition | identity_implications | civilizational_spiritual | transcendence_reintegration
          chapter_range: [<int>, <int>]
          assertion: "<layer-N assertion text>"
          optional_for_topics: [<topic_id>, ...]   # optional; omit = required for all topics

  <TOPIC_SPECIFIC_ANGLE_ID>:     # e.g. PROTECTIVE_ALARM
    parent_universal: USEFUL_SIGNAL    # required; angle_id must exist
    display_name: "The Protective Alarm"
    core_frame: "Anxiety as legitimate alarm misfiring in modern context"
    use_when: "Anxiety topic; reframe symptom as information"
    # Structural fields (arc_variant, framing_mode, chapter_1_role_bias,
    # integration_reinforcement_type) and the journey block are INHERITED from
    # parent_universal. Override any field by declaring it explicitly.

  <DEPRECATED_V1_ANGLE_ID>:      # e.g. WRONG_PROBLEM
    arc_variant: ...             # full v1 structural fields preserved
    framing_mode: ...
    deprecated: true
    successor_angle_id: SILENT_VERDICT
    deprecation_note: "Soft-deprecated 2026-05-20 per Angle Catalog v2. New books should use SILENT_VERDICT."

catalog_planner_resolution:
  version: 2
  topic_angle_map:
    <topic_id>: <angle_id>       # angle_id must exist under angles: AND not be deprecated
```

### 2.1 Valid `framing_mode` values

`debunk | framework | reveal | leverage` — same enumeration consumed by `phoenix_v4/planning/angle_bias.py`.

### 2.2 Valid `analogy_lens` values (per OPD-116-117 §2.5)

`fractal | dimensional_revelation | doorway | machine_slowly_revealed | mythic_recurrence | progressive_compression | book_is_the_angle`

Each universal angle must declare exactly one.

### 2.3 Valid `journey.layer_progression[].phase` values

In order: `definition → pattern_recognition → identity_implications → civilizational_spiritual → transcendence_reintegration` (5 layers, fixed).

---

## 3. Inheritance semantics (the parent_universal walk)

Helper: `phoenix_v4.planning.angle_resolver.resolve_angle_with_inheritance(angle_id, registry, *, allow_legacy=False, topic_id=None) -> dict`.

### 3.1 Algorithm

1. Look up `angle_id` in `angles:`. If missing, raise `KeyError`.
2. If the entry has `deprecated: true` and `allow_legacy=False`, raise `DeprecatedAngleError` (caller should resolve through `successor_angle_id`).
3. Build the parent chain by walking `parent_universal` transitively. Chains **may exceed depth 1** (e.g. `LOYAL_ADAPTATION → PROTECTIVE_ALARM → USEFUL_SIGNAL` yields `chain_depth=2`). Detect cycles; raise `AngleCycleError` if found. If the chain exceeds `max_chain_depth=5`, raise `AngleChainDepthError`.
4. Merge fields from root (universal) down to leaf:
   - Structural fields (`arc_variant`, `framing_mode`, `chapter_1_role_bias`, `integration_reinforcement_type`) inherit downward.
   - `journey` block inherits downward; if a leaf declares `journey`, leaf-level keys override inherited keys, with sub-field merging (e.g., a leaf may override `core_mantras` without restating `layer_progression`).
   - Display fields (`display_name`, `core_frame`, `use_when`) do NOT inherit — they are leaf-defined per the operator's "name + core_frame per angle" principle.
5. Return the merged dict. Provenance metadata is attached as `_resolution_provenance`:
   ```python
   {
     "_resolution_provenance": {
       "leaf_angle_id": "PROTECTIVE_ALARM",
       "parent_chain": ["PROTECTIVE_ALARM", "USEFUL_SIGNAL"],
       "chain_depth": 1,
       "inherited_fields": ["arc_variant", "framing_mode", "chapter_1_role_bias",
                            "integration_reinforcement_type", "journey"],
       "leaf_overrides": ["display_name", "core_frame", "use_when"],
       "is_deprecated": False,
       "successor_angle_id": None
     }
   }
   ```

### 3.2 Worked example

```yaml
USEFUL_SIGNAL:
  framing_mode: reveal
  chapter_1_role_bias: destabilization
  integration_reinforcement_type: revelation
  arc_variant: ARC_STANDARD_A_v6
  journey: { analogy_lens: progressive_compression, ... }

PROTECTIVE_ALARM:
  parent_universal: USEFUL_SIGNAL
  display_name: "The Protective Alarm"
  core_frame: "Anxiety as legitimate alarm misfiring in modern context"
  use_when: "Anxiety topic; reframe symptom as information"
```

`resolve_angle_with_inheritance("PROTECTIVE_ALARM", reg)` returns:

```python
{
  "framing_mode": "reveal",                              # inherited
  "chapter_1_role_bias": "destabilization",              # inherited
  "integration_reinforcement_type": "revelation",        # inherited
  "arc_variant": "ARC_STANDARD_A_v6",                    # inherited
  "journey": { "analogy_lens": "progressive_compression", ... },  # inherited
  "display_name": "The Protective Alarm",                # leaf
  "core_frame": "Anxiety as legitimate alarm misfiring in modern context",  # leaf
  "use_when": "Anxiety topic; reframe symptom as information",              # leaf
  "parent_universal": "USEFUL_SIGNAL",
  "_resolution_provenance": { ... }
}
```

`PROTECTIVE_ALARM` correctly picks up `framing_mode=reveal` from `USEFUL_SIGNAL` without restating it — this is the inheritance contract verified by the test suite.

### 3.2.1 Multi-level parent chains

Topic-specific angles may point at another topic-specific angle (not only at a universal). Example:

```yaml
USEFUL_SIGNAL:          # universal (root)
  journey: { ... }

PROTECTIVE_ALARM:
  parent_universal: USEFUL_SIGNAL

LOYAL_ADAPTATION:
  parent_universal: PROTECTIVE_ALARM
```

`resolve_angle_with_inheritance("LOYAL_ADAPTATION", reg)` walks `LOYAL_ADAPTATION → PROTECTIVE_ALARM → USEFUL_SIGNAL`; `_resolution_provenance.chain_depth` is **2**. The resolver merges root-down the same way as a depth-1 chain. Safety cap: `max_chain_depth=5` (constant in `angle_resolver.py`); longer chains raise `AngleChainDepthError`.

### 3.3 Cycle detection

`parent_universal` chains must be acyclic. If `A.parent_universal == B` and `B.parent_universal == A` (or any longer cycle), `resolve_angle_with_inheritance` raises `AngleCycleError` with the offending chain in the message.

### 3.4 Canonical topic_id enumeration

**Path:** `config/source_of_truth/canonical_topics.yaml` — authoritative list of 20 `topic_id` values used by `journey.named_object_by_topic` and `catalog_planner_resolution.topic_angle_map`.

Every `journey.named_object_by_topic` block in the registry must declare keys **only** from that file. `angle_resolver.py` validates on resolve and raises `InvalidTopicIdError` on mismatch.

### 3.5 Layer-4 optional_for_topics

Each `journey.layer_progression[]` entry may declare `optional_for_topics: [<topic_id>, ...]`. When `resolve_angle_with_inheritance` is called with `topic_id`, layers whose list includes that `topic_id` are **omitted** from the returned `journey.layer_progression`. Omitted field means the layer is **required** for all topics.

Default (all 20 universals, layer 4 / `civilizational_spiritual`): `optional_for_topics: [sleep_anxiety, boundaries, courage]` — civilizational/spiritual lens is skipped for those topics.

---

## 4. Deprecation contract

| Field | Type | Required when |
|---|---|---|
| `deprecated` | `bool` | Set explicitly on the 4 legacy v1 angles |
| `successor_angle_id` | `str` | Required if `deprecated: true`; must point to a non-deprecated v2 angle |
| `deprecation_note` | `str` | Required if `deprecated: true`; human-readable rationale + date |
| `successor_of` | `str` | Optional reverse pointer on the successor (v2) angle, for forensics |

**Resolution behavior:**

- `resolve_angle_with_inheritance(<deprecated>, allow_legacy=False)` raises `DeprecatedAngleError`. Default for new books.
- `resolve_angle_with_inheritance(<deprecated>, allow_legacy=True)` returns the resolved dict with a warning logged. Used for books in flight that carry `legacy_angle_id` in their `BookSpec`.
- `CatalogPlanner._derive_angle` consults `topic_angle_map` first. If the mapped `angle_id` is `deprecated: true`, the resolver logs a warning and still returns it (operator must update the map).

### 4.1 BookSpec back-compat field

`BookSpec` (defined in `phoenix_v4/planning/book_spec.py`, schema unchanged in this PR) gains a sibling optional field on the next planner PR:

```python
legacy_angle_id: Optional[str] = None  # set when the book was authored under v1
```

In-flight books retain `angle_id="WRONG_PROBLEM"` AND set `legacy_angle_id="WRONG_PROBLEM"` so the resolver accepts the legacy lookup. New books leave `legacy_angle_id` unset and use v2 `angle_id` values.

This SSOT does NOT mutate existing BookSpecs; it specifies the back-compat contract that follow-up PRs implement.

---

## 5. Resolution order (CatalogPlanner)

Unchanged in shape from v1; tightened in interpretation.

1. **Explicit `angle_id`** on the catalog row — accepted if it exists under `angles:` (deprecation warning if applicable).
2. **Registry SSOT** — `catalog_planner_resolution.topic_angle_map[topic_id]`; accepted only if `angle_id` exists under `angles:`. If it's deprecated, log a warning AND return it (the operator should update the map to a v2 successor before merging).
3. **Series heuristic** — domain derived from `topic_id`, match `series_templates` entries with `angles`, score by `persona_affinity`. (Series templates point at any `angle_id` in the registry — deprecated or not — by design.)
4. **Fallback** — `{topic_id}_general` with `logging` warning and `last_angle_resolution_meta["heuristic_general_fallback"]=True`, unless `produce_single(..., angle_strict=True)`.
5. **Strict** — if steps 1–3 yield nothing and `angle_strict=True`, raise `AngleResolutionError`.

After resolution, the leaf `angle_id` is passed through `resolve_angle_with_inheritance` so downstream consumers (arc selector, Ch1 biaser, INTEGRATION shaper) see the full merged structural + journey block.

---

## 6. Observability

`CatalogPlanner.last_angle_resolution_meta()` is extended (additive):

```python
{
  # existing v1 keys:
  "source": "angle_registry.topic_angle_map" | "series_template_domain_persona" | "topic_general_fallback" | "unresolved_strict",
  "registry_hit": bool,
  "series_heuristic_used": bool,
  "heuristic_general_fallback": bool,
  "registry_angle_id": <angle_id|None>,
  "angle_id": <angle_id|None>,

  # NEW in v2:
  "inheritance_used": bool,               # True when parent_universal was walked
  "parent_chain_depth": int,              # 0 for universals, 1 for topic-specific
  "is_deprecated": bool,
  "successor_angle_id": <angle_id|None>,  # populated when is_deprecated is True
}
```

---

## 7. Journey content authoring (Pearl_Editor scope, NOT this spec)

This SSOT defines the journey BLOCK STRUCTURE. The actual mantra and assertion strings, plus per-topic `named_object` values, are authored by Pearl_Editor as commissioned per angle × topic × persona (per `docs/plans/OPD-116-117_BOOK_ANGLE_AS_JOURNEY_PLAN_2026-05-20.md` §4 phased rollout).

Until Pearl_Editor commissions land:

- `journey.named_object_by_topic.<topic_id>: null` — resolver treats as "not yet authored"; composer falls back to a generic angle-aware template.
- `journey.core_mantras: ["TODO: Pearl_Editor commission — 3-5 mantras"]` — single-element placeholder list.
- `journey.layer_progression[N].assertion: "TODO"` — composer skips chapter-N callback injection until non-TODO content lands.

The composer (`phoenix_v4/rendering/chapter_composer.py`) gates callback injection on `assertion != "TODO"` so the registry can ship in scaffold form without breaking existing renders.

---

## 8. Acceptance checklist (this PR)

- [x] `schema_version: 2` declared at top of YAML
- [x] 20 universal angles registered with full structural fields + journey scaffolds
- [x] 71 topic-specific angles registered with `parent_universal` pointers
- [x] 4 legacy v1 angles preserved with `deprecated: true` + `successor_angle_id`
- [x] All `successor_angle_id` pointers reference existing v2 angles
- [x] All `parent_universal` pointers reference existing universal angles (no cycles)
- [x] All 20 universals declare an `analogy_lens` from the 7-valid set
- [x] All 20 universals have a `layer_progression` of exactly 5 entries in canonical phase order
- [x] `catalog_planner_resolution.version: 2`
- [x] `catalog_planner_resolution.topic_angle_map` has 20 entries covering catalog topics
- [x] Every `topic_angle_map` target is non-deprecated
- [x] `resolve_angle_with_inheritance` implemented + cycle detected + tested
- [x] Inheritance test: leaf overrides win, missing fields fall through
- [x] All existing v1 tests in `tests/phoenix_v4/planning/test_catalog_planner_angle_registry.py` continue to pass

---

## 9. Out of scope for this PR

Per operator instruction:

- Authoring journey content (mantras, layer assertions, named_object values) — Pearl_Editor commissions
- Atom-level `ANGLE_DEFINITION` / `ANGLE_CALLBACK` files — per OPD-116-117 §3.1 (separate PR)
- `BookSpec.legacy_angle_id` field addition — separate planner PR
- Composer changes for callback injection — separate composer PR
- Chapter planner extension for Ch1 angle definition slot — separate planner PR
- Visual identity per angle (cover art motif, chapter break glyph) — deferred (per Angle Catalog v2 §7 decision 4)

---

## 10. Cross-references

- `docs/plans/ANGLE_CATALOG_V2_2026-05-20.md` — source of truth for 91 named angles, parent_universal mapping, and 3 operator decisions
- `docs/plans/OPD-116-117_BOOK_ANGLE_AS_JOURNEY_PLAN_2026-05-20.md` — journey block design (§2.1 6-step Ch1 intro; §2.2 5-layer return; §2.5 7 dimensional analogies)
- `docs/specs/ANGLE_REGISTRY_SSOT_V1_SPEC.md` — superseded; kept for forensics
- `config/angles/angle_registry.yaml` — the SSOT file this spec governs
- `phoenix_v4/planning/angle_resolver.py` — implements `resolve_angle_with_inheritance`
- `phoenix_v4/planning/angle_bias.py` — unchanged; continues to consume `framing_mode`
- `phoenix_v4/planning/catalog_planner.py` — consumes `catalog_planner_resolution.topic_angle_map`; extension to call `resolve_angle_with_inheritance` lands in a follow-up planner PR
- `tests/unit/planning/test_angle_registry_v2_inheritance.py` — verifies the inheritance contract

---

## 11. Operator decisions captured (per Angle Catalog v2 §7)

1. **Existing 4 angles** — SOFT-DEPRECATE. WRONG_PROBLEM, MAP_PROMISE, HIDDEN_TRUTH, ONE_LEVER kept in registry with `deprecated: true` + `successor_angle_id`. Books in flight retain assignment via `legacy_angle_id`. New books use catalog v2.
2. **Sub-angle journey inheritance** — AUTO-INHERIT from `parent_universal`. Topic-specific angles inherit the parent's journey block by default. Pearl_Editor authors specialization only where it adds reader value.
3. **Domain expansion** — EXPAND NOW. 25 angles added across 5 new clusters (body image, money, addiction, ADHD, divorce). Total now 91 named angles across 15 topic clusters.
4. **Per-angle visual identity** — DEFERRED. Future scope.
5. **`CONCEPT_ARCHITECTURE` naming** — CONFIRMED. Acceptable exception to the strict "adjective + noun" pattern.
