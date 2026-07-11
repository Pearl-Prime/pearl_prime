# Manga Canon Scene-Assembly Checklist

**Status:** canonical singleton (operator-facing)
**Date:** 2026-07-11
**Workstream:** `ws_manga_canon_scene_assembly_checklist_20260711`
**Scope:** visual legality + readability of one layered manga/webtoon **panel**
**Acceptance layer:** authored candidate (SPECCED) — not machine-complete; not PROVEN-AT-BAR
**Format modes covered:** `webtoon_vertical` (primary production master) + `manga_page_grid` (flatten/export overlay) + `universal`
**manga-scene-checklist=artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md**

> This is a fail-closed operator checklist. It is not a render lane, not a script bible, and not a lettering spec.

---

## Authority

| Role | Artifact |
|------|----------|
| **Canonical singleton (this file)** | `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` |
| Superseded prior scene-assembly prose | `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` (pointer only; not equal authority) |
| Live assembler | `scripts/manga/assemble_from_bank.py` |
| Live planner / half-person gate | `scripts/manga/panel_planning_rules.py` |
| Live chapter grammar | `scripts/manga/validate_chapter_composition_grammar.py` |
| Live L2 legality annotation | `scripts/manga/annotate_l2_composition_legal.py` |
| Live manifest gen | `scripts/manga/generate_assembly_manifest.py` |
| Live G2/G3/G4/G8 gates | `scripts/manga/composition_grammar.py` |
| Format master | `config/manga/format_routing.yaml` → `color_vertical_webtoon` master; `bw_page_manga` flatten |
| Positive visual proof | `artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/` |
| Accepted stillness establishing | `…/stillness_ep001_postmerge_honest/panels/ep001_016.png` (`sparse_establishing_wide`) |

**Conflict rule:** governance ownership → live executable code → accepted visual proof + operator verdict → research/older QA. Do not blend contradictions.

**Supersession conflict retained:** prior HR-U02 / assembler `g3_horizon_scale_check` / `plan_horizon_scale_paste` encode a universal horizon-ratio paste law. This checklist **rejects** that as a universal acceptance rule (`SCALE-001`). Until code is retargeted, treat G3 horizon math as **implementation debt**, not canon.

---

## How to use (ordered gates — fail closed)

Run gates **1→9** in order. A later gate may not rescue an earlier hard fail.

1. **PLAN** — primary storytelling job + format mode
2. **L0 / ENV** — readable environment or declared abstract
3. **L2 ELIGIBILITY** — hard filters before any ranking
4. **SCALE** — camera-consistent projection
5. **GROUND** — support / honest crop / real occlusion
6. **OCCLUDE / INTERACT** — nearer-plane truth
7. **TONE / LIGHT / EDGE** — render-band + lighting + contact shadow
8. **READ** — delivery + thumbnail
9. **ACCEPT / REJECT** — record passed/failed rule IDs

**Hard doctrine:** Gates 6–7 may **not** conceal Gate 5 grounding failure, illegal source termination, incompatible camera, wrong scale, or missing support.

---

## Positive / negative mapping (operator verdict)

### Why the true L0/L2/L3 proof is the positive anchor

Inspected: `artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/`
(`L0_background_source.png`, `L2_character_keyed.png`, `L3_foreground_keyed.png`, `true_L0_L2_L3_composite.png`, `proof_sheet.png`)

| Visual fact | Rules |
|-------------|-------|
| L0 hangar reads as physical room: floor plane, railings, mecha scale anchors, depth | ENV-001, L0-001 |
| L2 is full-body standing cutout (boots present), not a bust enlarged into a room | L2-001, CROP-001, GROUND-001 |
| Feet meet floor; soft contact darkening under boots (full-res / proof sheet) | GROUND-002, EDGE-001 |
| L3 rail sits nearer than L2 and occludes lower body honestly | OCCLUDE-001, CROP-003 |
| Lighting/tone read as one scene at full-res (not a sticker) | LIGHT-001, TONE-001 |
| Silhouette + “who/where/what” survive ~400px delivery and ~27% thumb | READ-001 |

**Per-rule evaluability on positive proof (do not invent machine passes):**

| Rule | Result | Note |
|------|--------|------|
| ENV-001 | pass | Readable hangar at delivery width |
| GROUND-001 / GROUND-002 | pass | Full figure + floor contact visible |
| OCCLUDE-001 | pass | L3 rail in front |
| CROP-001 | pass | Source L2 does not terminate in open hangar air |
| LIGHT-001 | pass (operator) | Rim/fill compatible at full-res |
| EDGE-001 | pass (operator) at full_res / proof_sheet; delivery_size softer | Soft contact under boots; no separate PNG required |
| TONE-001 | pass (operator) | No hard matte halo in composite |
| CAMERA-001 | not_evaluable_from_available_evidence | No declared compatibility matrix / class tags on proof |
| SCALE-001 eye-line shortcut | not_evaluable / N/A | Do not force horizon eye-line; camera is not proven eye-height level |
| TRANSFORM-001 | not_evaluable | No transform metadata in proof packet |
| ACCEPT-001 | pass | Operator accepts this packet as current positive bar |

### Why `ep001_016 · establishing · sparse_establishing_wide` works

Path: `artifacts/qa/manga_reading_packets_2026-07-11/stillness_ep001_postmerge_honest/panels/ep001_016.png`

| Visual fact | Rules |
|-------------|-------|
| Wide readable conference room: table, chairs, ceiling grid, glass wall | ENV-001, PLAN-001 (establish) |
| Tiny seated figure at far end; scale matches chair/table; table reflection grounds her | SCALE-001, GROUND-002 |
| Furniture contact shadows / watercolor pools weld chairs to carpet | EDGE-001 |
| Geography answers “where am I?” before later action depends on it | SEQ-001, READ-001 |
| Not a bust pasted into open room air | CROP-001, CROP-004 |

### Why bad stillness room/bust panels fail

| Anchor | Visual reject facts | Rule IDs |
|--------|---------------------|----------|
| `…/panels/ep001_008.png` (`re_establish` / shared_meal_table_medium) | Knees-up figure floats in open kitchen air; source terminates mid-torso; no seat/floor contact; hard L2 lines vs soft L0; lighting ignores window leaf-shadow axis | CROP-001, GROUND-001, GROUND-002, EDGE-001, LIGHT-001, TONE-001, FAIL-EDGE-001, FAIL-LIGHT-001, FAIL-TONE-001 |
| `…/panels/ep001_005.png` (`dialogue_bust` / chest_breath_micro) | Abstract bust over still-readable kitchen (table/chair/window readable even when defocused); jagged sweater termination in open space; no support; lighting axis fights window | CROP-001, CROP-004, GROUND-001, ENV-001+CROP-004, LIGHT-001, FAIL-EDGE-001, FAIL-LIGHT-001 |

**Minimum corrections:** (008) use seated room-capable L2 with pelvis-to-seat contact + contact shadow, or crop as intentional panel-edge / real occluder; (005) put bust on declared abstract/defocus stage **or** use full/knees-up with honest support — never readable room behind unexplained partial figure.

---

## Gate 1 — PLAN

### PLAN-001 — One primary storytelling job
- **format_mode:** universal
- **enforcement:** hybrid · **severity:** hard_fail
- **pass:** panel declares exactly one primary job (establish / action / reaction / detail / consequence / insert / ma) and format mode (`webtoon_vertical` | `manga_page_grid`)
- **reject:** primary job ambiguous; secondary job makes focal action unreadable
- **correct:** rewrite shot plan before asset pick

**Shot-first:** choose purpose before assets. Secondary function allowed only if focal action stays unambiguous.

**No-legal-asset responses (never “closest illegal”):**
1) other legal asset · 2) revise plan · 3) split across panels · 4) author missing asset in render lane · 5) stop with exact coverage blocker.
Forbidden: enlarge bust into room shot; invent clutter to hide missing anatomy; silent close-up swap; semantic similarity overriding legality.

**Text-safe (planning):** identify dialogue/SFX safe zones before final placement; do not cover eyes/faces/interacting hands/primary object unless deliberately approved.

---

## Gate 2 — L0 / ENV

### ENV-001 — Readable physical environment
- **format_mode:** universal
- **enforcement:** operator (classification) / hybrid · **severity:** hard_fail when grounding depends on it
- **Classify at primary delivery size** (not thumbnail). Thumbnail collapse ≠ abstract.
- **pass:** at delivery size, viewer can identify support surface/structure + ≥1 scale/vertical anchor + enough depth to locate L2
- **reject:** filename/prompt used as class; assembler picks thumb as classification source to evade grounding
- **record:** `environment_classification`, `classification_preview`, `delivery_profile_authority`, `support_structure_readable`, `scale_anchor_readable`, `depth_structure_readable`, `result`
- **delivery_profile_authority (live):** `implementation_unbound` for exact CSS/DPI profile; operator inspection uses approved proof dims (stillness 1080×1920; true-layered proof 1024×1536) and ~360–430 CSS px for webtoon overlay

### L0-001 — Environment plate readiness
- **format_mode:** universal
- **enforcement:** hybrid · **severity:** hard_fail
- **pass:** L0 has inferable/known camera class, support structure, depth, lighting band, rendering band, usable staging zone — **or** panel declares abstract/symbolic/silhouette/flat-graphic mode
- **reject:** readable room used as wallpaper behind unexplained partial figure (`CROP-004`)
- **correct:** pick legal plate or declare nonliteral mode

---

## Gate 3 — L2 eligibility

### L2-001 — Composition-legality hard filters before ranking
- **format_mode:** universal
- **enforcement:** machine where sidecars exist (`annotate_l2_composition_legal.py`, `panel_planning_rules.validate_manifest_composition_planning`); else hybrid
- **severity:** hard_fail
- **Hard filters (all must pass):** identity (if required), pose/action, source crop, camera-height class, vertical/horizontal view angle, perspective/lens class (if known), facing/screen direction, physical-support requirement, floor-plane compatibility, continuity state, prohibited-use metadata
- **Only then rank:** expression, semantic closeness, aesthetic, minor lighting, composition preference
- **reject:** any failed eligibility compensated by weighted score; “closest” illegal asset
- **correct:** return to PLAN / author asset

Live code today: crop×bg G1 matrix + half-person forbid in `panel_planning_rules.py`; `room_capable` / `abstract_stage_eligible` from `annotate_l2_composition_legal.legality_fields`. Camera-class matrix beyond angle_bucket: **implementation_unbound**.

---

## Gate 4 — SCALE

### CAMERA-001 — Camera-class compatibility matrix
- **format_mode:** universal
- **enforcement:** machine when matrix+tags exist; else **implementation_unbound** / hybrid
- **severity:** hard_fail
- **pass:** exact class match **or** explicitly allowed pairing for height class, vertical angle, horizontal angle, perspective/lens, floor-plane orientation
- **reject:** implicit adjacency; free-form “close enough”
- **evidence:** `compatibility_matrix_path`, `L0_camera_class`, `L2_camera_class`, `matched_rule`, `result`
- **live:** `g2_angle_bucket` only (`composition_grammar.py`); **no** full compatibility matrix path → record `implementation_unbound`

### SCALE-001 — Camera-consistent projection (no universal eye-line law)
- **format_mode:** universal
- **enforcement:** hybrid · **severity:** hard_fail
- **pass:** `L2.camera_height_class` ↔ `L0.camera_height_class`; view angles compatible; floor contact projects onto support plane when relevant; world height plausible vs L0 anchors; body landmarks follow L0 perspective field
- **Specialized shortcut (only when level floor + untilted camera + camera≈standing eye height):** `abs(L2.eye_line_y - L0.horizon_y) <= configured_eye_height_tolerance` — tolerance authority required (`THRESHOLD-001`)
- **reject:** eyes forced to horizon despite high/low camera; feet fit but proportions contradict room; seated-camera plate + standing-eye L2; low/high-angle body into eye-level room; size contradicts doors/seats/furniture/adjacent figures
- **correct:** re-project with camera model or change assets
- **conflict:** live `g3_horizon_scale_check` / prior HR-U02 are **not** acceptance canon

### THRESHOLD-001 — Tolerance authority
- **format_mode:** universal
- **enforcement:** machine when bound; else documentation
- **severity:** warning for unbound docs; hard_fail when a numeric gate is claimed without authority
- Every numeric/categorical tolerance must name `threshold_name`, `authority_path`, `authority_key`, `current_value`, `units`, `enforcement_status`
- **Do not invent values in this lane.** Missing → `enforcement_status: implementation_unbound`

---

## Gate 5 — GROUND / CROP

### CROP-001 — Source-asset termination
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** artwork/alpha boundary explained by panel edge (`CROP-002`), physical occluder (`CROP-003`), or declared nonliteral mode (`CROP-004`)
- **reject:** source terminates inside open readable environment; shadow/blur/grade/unrelated object used as rescue

### CROP-002 — Intentional panel-edge crop
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** medium/close normally OK; wide OK only if declared, anatomy continues beyond edge, crop serves framing/OTS/entrance/exit, geography+action remain readable
- **reject:** accidental mid-torso cut in open room

### CROP-003 — Physical foreground occlusion
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** nearer-plane object truthfully blocks anatomy; occluder passes `OCCLUDE-001`
- **reject:** same-depth prop pretending to hide missing legs

### CROP-004 — Abstract / symbolic omission
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** panel explicitly declares abstract/symbolic/silhouette/flat-graphic/authorized nonliteral mode
- **reject:** readable physical environment behind unexplained partial source figure

### GROUND-001 — Primary subject grounding
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** in readable wide env, primary subject is complete grounded figure **or** honestly occluded **or** intentional panel-edge crop; secondary/foreground may be panel-cropped if depth/role immediate
- **reject:** chairless hovering knees-up; source termination in open space; cockpit crop without cockpit structure

### GROUND-002 — Support-specific contact
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** standing↔floor; seated↔seat/back/legs; vehicle↔seat/dash/harness/frame; leaning↔wall/rail/table; held object↔hand
- **reject:** missing support “fixed” by contact shadow alone

---

## Gate 6 — OCCLUDE / INTERACT

### OCCLUDE-001 — Nearer-plane truth
- **format_mode:** universal (webtoon overlay: prefer top/bottom L3 entry; do not default left/right framing as standalone rule)
- **enforcement:** hybrid · **severity:** hard_fail
- **pass:** L3 shallower than L2; reads in front; support/held/interaction layers correctly ordered
- **reject:** desk/rail/prop on same depth plane “rescuing” missing anatomy

---

## Gate 7 — TONE / LIGHT / EDGE / TRANSFORM

### LIGHT-001 — Key-light compatibility
- **format_mode:** universal · **enforcement:** hybrid (machine azimuth when sidecars: live G8) · **severity:** hard_fail
- **pass:** compatible key direction/height/contrast/hardness; stylized OK if not contradictory; final grade may unify minor deltas only
- **reject:** clearly opposite axes; grade used to hide incompatible sources → `FAIL-LIGHT-001`

### TONE-001 — Rendering-band verify or normalize
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** verify noop **or** nondestructive normalize into L0 band (AA, edge hardness/contamination, line weight, black density, contrast, screentone, resolution, sharpen, color/gray, premultiply, defringe, color-space/gamma)
- **reject:** soft AA L2 on hard-lined L0; grey/white matte halo; mismatched line/tone frequency; pasted look → `FAIL-TONE-001`
- **manifest:** `tone_normalization.{source_band,target_band,operation,edge_treatment,result}` — **implementation_unbound** in live manifests today

### EDGE-001 — Contact-shadow representation
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** manifest declares `role: contact_shadow` **or** deterministic contact-shadow op on a resolved layer; inspectable: caster, receiver, region, opacity, softness, light relation, order. Separate PNG not required.
- **reject:** undeclared omission when support+style would produce contact; feet/seat/hand hover; wrong-direction blob; generic floating ellipse → `FAIL-EDGE-001`
- **exceptions:** abstract/symbolic/silhouette/flat-graphic/no-readable-support declared
- **live:** `grounding.contact_shadow` + `render_contact_shadow_layer` in assembler — boolean flag, not full inspectable schema

### TRANSFORM-001 — Legal asset transforms
- **format_mode:** universal · **enforcement:** hybrid · **severity:** hard_fail
- **pass:** uniform scale/rotation within declared max; mirror only if no text/scar/asymmetry/handedness/motion/continuity reverse
- **reject:** non-uniform anatomy squash; perspective warp to force incompatible camera; transform making illegal asset “look OK”
- **thresholds:** max scale/rotation → `implementation_unbound`

---

## Gate 8 — READ

### READ-001 — Delivery-size positive gate
- **format_mode:** split overlays below · **enforcement:** operator / hybrid · **severity:** hard_fail
- **Required previews:** (1) intended delivery size (2) diagnostic thumb ≈25–30% working width
- **Webtoon:** also ≈360–430 CSS px wide
- **Page grid:** full page in reading viewport + panel at reproduction size + page thumb
- **pass record:** `location_readable`, `subject_readable`, `body_action_readable`, `focal_beat_readable`, `silhouette_readable`, `result`
- Close-up/abstract reaction may set `location_readable=not_required` when geography already continuous
- **live:** no automated delivery-size gate in assembler → operator until bound

---

## Gate 9 — ACCEPT

### ACCEPT-001 — Explicit pass/fail ledger
- **format_mode:** universal · **enforcement:** operator · **severity:** hard_fail
- **pass:** every applicable rule ID recorded pass/fail/not_evaluable; no silent skips; grounding fails not marked pass because lighting looked nicer
- **reject:** “looks fine” without rule IDs

---

## Sequence / page grammar (minimum for panel-in-sequence)

| ID | Rule | enforcement | severity |
|----|------|-------------|----------|
| SEQ-001 | Establish geography before an action depends on it. Delayed reveal OK if no dependent action. | hybrid | hard_fail |
| CONT-001 | Re-establish after prolonged CU/abstract/reaction/insert when place is lost. | hybrid | hard_fail |
| CONT-002 | Preserve screen direction unless turn/crossing/reverse/re-establish explains change. | hybrid | hard_fail |
| CONT-003 | Preserve continuity state: position, costume, object state/handedness, light dir, injuries, motion dir. | machine where state YAML exists; else hybrid | hard_fail |
| RHYTHM-001 | Avoid repeated crop/angle/scale/placement unless deliberate stillness/comedy/ritual/tension. | operator | warning |
| RHYTHM-002 | Prefer distinct functions: establish/action/reaction/detail/consequence. | operator | warning |
| RHYTHM-003 | Do not force complex interaction into one dishonest layered composite — split panels. | hybrid | hard_fail |

Live chapter hooks: `validate_chapter_composition_grammar.py` + HR-U16 re-establish wiring in `generate_assembly_manifest.py` (subordinate IDs; map to SEQ/CONT family in implementation lane).

---

## Format overlays

### WEBTOON_VERTICAL
- Test ~360–430 CSS px; top→bottom reveal; vertical spacing as timing
- Prefer top/bottom L3 entry; avoid loading both horizontal edges
- Re-establish at scroll-scene transitions (not mechanical once-per-page)
- Text + focal action must survive phone width; reject tone patterns that moiré after mobile resample

### MANGA_PAGE_GRID
- Declared reading direction; focal flow through intended order
- Gaze/motion must not pull backward without purpose
- Balloon safe zones before final crop; faces/hands/objects out of likely balloon zones
- Adjacent panels must not merge into one grey mass; gutters distinct
- B/W balance across page; hierarchy survives full-page view
- Do not re-establish merely because a new page begins

### MONOCHROME_MANGA
- Compatible line-resolution + screentone families across L0/L2/L3
- Reject moiré, crawling tone, mismatched dots, differently softened lines
- Solid blacks preserve focal silhouette; reduce BG detail before sacrificing face
- Test grayscale at final print/digital resolution

---

## Composition failure patterns → rules → minimum fix

| Pattern | Rules | Minimum fix |
|---------|-------|-------------|
| Floating torso in room | CROP-001, GROUND-001/002, FAIL-EDGE-001 | Legal crop/support/occluder or abstract mode |
| White plate halo / keyed mismatch | TONE-001, FAIL-TONE-001 | Defringe/normalize or reject L2 |
| Blobbed BG or figure | READ-001, TONE-001 | Simplify / re-render / contrast fix |
| Unreadable silhouette | READ-001 | Restage / contrast / crop |
| Fake occlusion | OCCLUDE-001, CROP-003 | True nearer occluder or full figure |
| Readable room behind abstract bust | CROP-004, ENV-001 | Abstract stage or room-capable L2 |
| Geometry OK but collaged lighting | LIGHT-001, FAIL-LIGHT-001 | Compatible L2 or relight normalize |
| Line/screentone mismatch | TONE-001, FAIL-TONE-001 | Band normalize or reject |
| Touching plane, no contact shade | EDGE-001, FAIL-EDGE-001 | Declare/apply contact solution |
| Scale via illegal eye-line force | SCALE-001, FAIL-SCALE-001 | Camera-consistent projection |
| Passes working res, fails delivery | READ-001 | Fix for delivery/thumb |
| Conflicting canon docs | (governance) | Single singleton — this file |
| Wrong light axis | FAIL-LIGHT-001 | Replace/relight L2 |
| Tone density off band | FAIL-TONE-001 | Normalize/reject |
| No contact shadow when required | FAIL-EDGE-001 | Add inspectable contact solution |
| Scale contradicts camera | FAIL-SCALE-001 | Re-scale with camera model |

### FAIL-* aliases
- **FAIL-LIGHT-001** → LIGHT-001 reject
- **FAIL-TONE-001** → TONE-001 reject
- **FAIL-EDGE-001** → EDGE-001 reject
- **FAIL-SCALE-001** → SCALE-001 reject

---

## Implementation-unbound register (next Dev lane)

| Gap | Needed |
|-----|--------|
| Full `CAMERA-001` compatibility matrix path | New config authority + validator |
| `THRESHOLD-001` eye-height / transform / tone deltas | Bind from config; stop inventing |
| Replace universal G3 horizon acceptance with camera-consistent projection | First file: `scripts/manga/composition_grammar.py` (`g3_horizon_scale_check`, `plan_horizon_scale_paste`) |
| Manifest `tone_normalization.*` schema | `generate_assembly_manifest.py` + assembler |
| Inspectable EDGE-001 contact-shadow schema (not only bool) | manifest schema + `assemble_from_bank.py` |
| Automated READ-001 delivery/thumb checks | new CI/operator harness |
| Delivery profile CSS/DPI authority | bind from publishing/webtoon config |

**Next implementation lane (exact):**
1. Change `scripts/manga/composition_grammar.py` first (retire universal horizon acceptance; add camera-consistent projection hooks).
2. Enforce rule IDs: `SCALE-001`, `CAMERA-001`, `THRESHOLD-001`, `CROP-001`, `GROUND-001`, `GROUND-002`, `EDGE-001`.
3. Rerun proof packet: `artifacts/qa/manga_true_layered_webtoon_proof_2026-07-10/` + stillness `ep001_008`/`ep001_005`/`ep001_016` regression.

---

## Rule ID index (stable)

PLAN-001, ENV-001, L0-001, L2-001, CAMERA-001, SCALE-001, THRESHOLD-001,
CROP-001, CROP-002, CROP-003, CROP-004, GROUND-001, GROUND-002,
OCCLUDE-001, LIGHT-001, TONE-001, EDGE-001, TRANSFORM-001, READ-001, ACCEPT-001,
SEQ-001, CONT-001, CONT-002, CONT-003, RHYTHM-001, RHYTHM-002, RHYTHM-003,
FAIL-LIGHT-001, FAIL-TONE-001, FAIL-EDGE-001, FAIL-SCALE-001
