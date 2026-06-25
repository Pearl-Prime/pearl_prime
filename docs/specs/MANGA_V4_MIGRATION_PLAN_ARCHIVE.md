> ⛔ SUPERSEDED 2026-06-25 @ origin/main 196d0540ec746ae0905fb0a23a253cd578266f23 — current manga architecture: docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md. This file is a frozen historical archive of the V4 migration plan; do not treat as active guidance.

# Manga V4 Migration Plan — Historical Archive

**Status:** HISTORICAL ARCHIVE (v1.0.0 — frozen 2026-05-20; Phase D scripts superseded by the forthcoming V5 orchestrator per `MANGA_V5_LAYERED_ARCHITECTURE.md` once it lands via PR #1258)
**Author:** Pearl_Architect (original authorship preserved)
**Schema version:** 1.0.0 (extraction snapshot of V4 spec §13 as of v0.6.1, 2026-05-20)
**Archive rationale:** §4 (Phase D, formerly V4 spec §13.4) is being superseded by V5 (`render_v5_episode.py` replaces V4's `build_layer_render_prompts.py` + `render_layer_inventory.py` + `compose_layered_panel.py` when V5 lands). The rest of this plan remains true as a historical record but is no longer the active migration plan; V5 has its own acceptance criteria. Archiving honors V4 spec §15.C.6 trip-wire + operator 2026-05-20 directive (target <1,800 lines).

**Status note:** This is a frozen historical record. Any future V4 fallback amendments go into the V4 spec proper (`docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md`), not this archive.

---

## 1. Migration Plan (V3.1 → V4) — Validator-First

**Architectural principle (operator-directed, v0.3 critique):** _"Build the validator infrastructure BEFORE expanding archetypes. Validators are what transform the architecture from AI art workflow into contract-governed render system."_

Phases are reordered accordingly: validators are Phase B (was Phase C in v0.2). No archetype authoring proceeds until the validators can verify what's authored.

## 2. Phase A — Spec review (THIS doc, 2026-05-19)
Operator reviews v0.3. Approve V4 spec §5 inheritance + MANGA_CONTINUITY_STATE_SPEC.md §1–§9 continuity + light-rig + cardinality controls + V4 spec §8 inventories + V4 spec §14 failure modes.

## 3. Phase B — Build validator infrastructure (THE FOUNDATION) — V1 = brutally deterministic only

Built **against the spec, not against any series authoring**. Per the v0.4 operator critique, V1 implements ONLY class-A contract validators (V4 spec §12.0) — no model inference, no heuristic thresholds beyond fixed-rule numeric checks. Heuristic / perceptual / narrative scorers come in Phase B.2 after the deterministic core is stable.

**Phase B.1 — Deterministic core (V4 launch dependency):**

Three deterministic foundation scripts, in strict dependency order.

1. **`scripts/manga/compile_safe_zones.py`** (FIRST — foundational)
   - Inputs: V4 spec §5 inheritance YAML (`base_contract` + `framing_contract` + `subject_contract` + `genre_modifier` + `archetype_exception`)
   - Output: flat compiled table (V4 spec §5.7) as `config/manga/compiled/safe_zones.yaml`
   - **Implementation constraint:** fully deterministic. YAML loader + dict merge + override precedence. No AI, no heuristics, no thresholds. Pure data transformation.
   - **Tests:** golden snapshot — input YAML hash → output table hash must be stable across runs. Every cell in v0.3's compiled-view table (V4 spec §5.7) must reproduce from inheritance composition.
   - Why first: V4 spec §5 is the source of truth; the other validators read from `safe_zones.yaml`.

2. **`scripts/manga/contract_to_prompt_compiler.py`** (NEW v0.5 — Phase B.1 step 1.5)
   - Inputs: compiled safe_zone row + character_design + continuity_state + light_rig + style_state + layer type
   - Output: `PromptBundle(positive, negative, parameters, cache_key, provenance)` per V4 spec §5.9
   - **Implementation constraint:** plain `str.format_map(...)` substitution. No LLM. No fuzzy fallbacks. Missing slot data is fatal.
   - **Tests:** golden snapshot — fixed input tuple → stable `(positive, negative)` sha256. Spot-check that injecting the V4 spec §5.5 example contract produces the V4 spec §5.5 example prompt suffix exactly.
   - Why between steps 1 and 2: `validate_layer.py` needs to verify renders against prompts that were generated; without a deterministic prompt compiler, the validator chases a moving target.

3. **`scripts/manga/validate_layer.py`** (THIRD — class-A gates from V4 spec §12.1–§12.5)
   - Inputs: a rendered layer PNG + the layer's declared contract (subject_type, framing, genre, backdrop)
   - **Implements ONLY class-A gates in V1:**
     - `backdrop_corner_check` (4 corner RGB sample, ±5 tolerance)
     - `subject_safe_zone` (non-backdrop bbox vs compiled safe zone from compile_safe_zones.py output)
     - `subject_does_not_touch_edge` (5px clearance check)
     - `rembg_clean_alpha` (post-cutout alpha histogram bimodality)
     - `face_visible_for_face_archetypes` (face detection MAY use a model but threshold is a fixed 0.85; result is binary)
     - `negative_space_in_bbox` (pixel variance check, fixed threshold 0.15)
     - `effect_density` (non-backdrop pixel % within 5–35% range)
     - `lettering_safe_zones_clear` (bbox intersection — pure geometric)
   - Output: list of `ValidationResult` (per V4 spec §12.6). ANY class-A FAIL halts cache write.
   - **Tests:** take the 3 layer-demo Mira renders (sage backdrop) — validator MUST flag them ALL as backdrop_corner_check FAIL. Take synthetic pure-white-bg image with subject in safe zone — validator MUST pass it. Take pure-white-bg with subject touching edge — validator MUST flag.

4. **`scripts/manga/validate_continuity_invariants.py`** (FOURTH — MANGA_CONTINUITY_STATE_SPEC.md §3.A deterministic only)
   - Inputs: panel N continuity_state YAML + panel N+1 continuity_state YAML + archetype IDs
   - **Implements ONLY MANGA_CONTINUITY_STATE_SPEC.md §3.A deterministic invariants in V1:**
     - scene_continuity (string equality + beat_type allow-list)
     - character_identity_continuity (character_design_hash equality)
     - prop_persistence (state ∈ prev_state ∪ reachable-in-1-step set)
     - gaze_target_validity (named target exists in scene/prop state)
     - temporal_continuity (next-step-in-cycle check)
     - expression_dial_bounded_delta (|Δ| ≤ bound by beat_type)
     - light_rig_within_scene (set membership)
   - Output: list of `ValidationResult` per V4 spec §12.6. FAIL on any deterministic violation.
   - **MANGA_CONTINUITY_STATE_SPEC.md §3.B heuristic invariants explicitly NOT implemented in V1** — they live in Phase B.2.
   - **Tests:** synthetic state pairs covering each invariant — each MUST catch the violation it targets, MUST NOT false-positive on valid pairs.

**Phase B.1 definition of done:** all four scripts in `scripts/manga/`, each with a pytest suite exercising pass AND fail cases. Run `pytest scripts/manga/tests/validators/` → green. NO Phase C authoring before B.1 is green.

**Phase B.2 — Heuristic / perceptual / narrative scorers (post-launch hardening):**

Built AFTER B.1 is stable and Phase C has produced enough real renders to calibrate against.
- `validate_layer.py` extended with class-B heuristics (palette_compliance, seam_check)
- `validate_layer.py` extended with class-C perceptual evaluators (identity_distance, pose_match, lighting_rig_coherence)
- `validate_continuity_invariants.py` extended with class-D narrative invariants (emotional_pendulation, tension_arc_coherence)
- Severity is `SCORE` or `WARN` until per-check calibration data shows < 3% false-positive rate; then per-check spec amendment may promote to `FAIL`.

Phase B.2 is NOT a V4 launch blocker. V4 ships with deterministic-only validation; advisory scorers add safety net incrementally.

## 4. Phase C — Schema authoring for ONE series (target: stillness_en_01)
Now the validators exist; authoring is verifiable.
- Author `stillness_en_01.scene_inventory.yaml` (4–6 scenes × ≤4 temporal variants × declared light_rig_id from MANGA_CONTINUITY_STATE_SPEC.md §9 library)
- Author `stillness_en_01.object_inventory.yaml` (8–12 objects × state variants)
- Add `layer_render_contract` to all 19 iyashikei archetypes
- Add `character_pose_inventory` to Mira's character_design
- Hand-author `continuity_state/ep_001/*.yaml` from existing chapter_script
- Author `config/manga/light_rigs/iyashikei.yaml` (~8 rigs K01-K08)
- Every authored file passes its corresponding validator.

## 5. Phase D — Render pipeline scripts (superseded by V5 once it lands)
- New: `scripts/manga/build_layer_render_prompts.py` — emits per-layer prompts from inventory + continuity_state + safe_zones; injects light_rig.prompt_clause
- New: `scripts/manga/render_layer_inventory.py` — renders the L0/L1/L2/L3/L4 cache for a series
- New: `scripts/manga/compose_layered_panel.py` — rembg + PIL composite using V4 spec §10 math
- Modify: `build_panel_prompts_v3.py` → layer mode when archetype has `layer_render_contract`
- Modify: `queue_panel_renders.py` → dispatch layer-renders; route per V4 spec §11 engine map
- Every render output passes `validate_layer.py` before entering cache; every panel composite passes the composite gates.

## 6. Phase E — Validate vs V3.1 baseline
Render `stillness_en_01 ep_001` via V4. Side-by-side vs V3.1 (originally rendering at PID 37394 on 2026-05-19). Operator review.

## 7. Phase F — Catalog rollout
Apply V4 to all `stillness_press` iyashikei series. Author archetype catalogs for the other 7 top-priority genres (separate Phase 2 spec — `MANGA_LAYER_GENRE_EXTENSIONS_SPEC.md`).

## 8. What V3.1 in-flight today still ships
V3.1 single-engine re-render running on 2026-05-19 (PID 37394) ships as V3.1 — better than V3 (no cross-engine drift), worse than V4 (no identity lock, no layer reuse, no continuity invariants, no light-rig coherence). V3.1 is the operational fallback for archetypes V4 doesn't yet cover (V4 spec §15.B).

## 9. Why this order matters (validator-first rationale)

Two failure modes that validator-first prevents:

**Without validators:** I author a `scene_inventory.yaml`, run the prompt builder, get rendered layers — and have no way to know if they're contract-compliant short of eyeballing the output. Errors compound silently. The system reverts to probabilistic prompting (better-than-V3.1 but not deterministic).

**With validators:** every authored input passes a gate before render; every rendered layer passes a gate before composite; every composite passes a gate before delivery. Errors are caught at the boundary they occur. The system is a contract-governed pipeline, which is the entire point of the spec.

---

## Appendix: Cross-spec mapping (former §13.x → new §N)

| Former location (V4 spec §13.x) | New location (this archive §N) |
|---|---|
| §13 intro | §1 |
| §13.1 Phase A spec review | §2 |
| §13.2 Phase B validator infrastructure | §3 |
| §13.3 Phase C schema authoring | §4 |
| §13.4 Phase D render pipeline | §5 |
| §13.5 Phase E baseline comparison | §6 |
| §13.6 Phase F catalog rollout | §7 |
| §13.7 V3.1 in-flight handling | §8 |
| §13.8 Validator-first rationale | §9 |

---

## Version history

- **v1.0.0 (2026-05-20):** Initial extraction from `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §13 per the §15.C.6 doc-split commitment + operator directive 2026-05-20 (target <1,800 lines). Content preserved verbatim; section numbering remapped (former §13.x → §N). References to other V4-spec sections (§5, §8, §10, §11, §12, §14, §15) were prefixed with "V4 spec" for clarity. References to former §6.x continuity-state material were updated to point at `MANGA_CONTINUITY_STATE_SPEC.md §N` (the sibling extracted in the same doc-split pass).
