# Manga Composition Grammar Spec — bank metadata, grounding math, panel-shot grammar

**Status:** SPECCED, §10 pilot EXECUTED-REAL (v1.0.1 — Pearl_Research 2026-07-07; sibling addendum to `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` §10 per the §15.C.6 doc-split rule; pilot merged as PR #4689)
**Author:** Pearl_Research (composition-grammar research lane)
**Schema version:** 1.0.1
**Taxonomy label (mandatory honesty header):** the scheme is **SPECCED**; the §10 pilot is **EXECUTED-REAL** (PR #4689: gates G1–G6 + §8 derived-BG ops live in the standalone pilot module `scripts/manga/composition_grammar.py`, with `schemas/manga/composition_meta.schema.json`, 3 annotated April sidecars, and byte-verified 4-panel + control artifacts under `assembled/composition_grammar_pilot/`). The production path is NOT wired: `assemble_from_bank.py` integration, the §7 manifest fields, and the §6.2 chapter validator remain ABSENT; nothing is PROVEN-AT-BAR. The research basis is **RESEARCHED** (`artifacts/research/manga_composition_grammar_research_2026-07-07.md` — every external rule in this spec carries a citation there).
**Extends (does not fork):** `MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7 §4/§5/§10/§12, `MANGA_V5_LAYERED_ARCHITECTURE.md` §7/§8, `schemas/manga/assembly_manifest.schema.json`, `scripts/manga/assemble_from_bank.py`. Registered in the Canonical Artifacts Registry as `manga_composition_grammar`.

---

## 1. Problem and scope

**Operator failure signal:** "half a person floating in the middle of a room." A waist-up character cutout pasted into a fully-rendered perspective kitchen at a percent bbox, with no ground contact, no eye-level agreement, no shadow, and nothing in front of her.

That single image contains **two distinct defects**, and the distinction is the core of this spec:

1. **Illegal combination** — a waist-up crop over a full-perspective room background is a combination professional manga essentially never prints. Bust/waist framings conventionally sit on *abstract* background classes (tone, gradient, defocus, emotion-texture, white); full room renders belong to establishing and full-figure shots where ground contact is drawn. The bug is not the half-figure — it is the half-figure *on the wrong background class*.
2. **Legal combination, missing grounding** — even a full-figure over a room plate looks pasted unless the compositor resolves eye-level scale, floor contact, contact shadow, and (ideally) occlusion. §10 of the contract spec (tight-crop → min-scale → centered paste) does none of these; V4's 2/35 operator acceptance was the direct result.

This spec supplies the missing layer between the bank and the assembler:

- **§4** a `composition_meta` metadata schema every banked asset carries;
- **§5** deterministic combination gates (which assets may combine, and the grounding ops a legal combination requires);
- **§6** a panel-shot grammar (story beat → shot type → layer recipe) so scripts deterministically select legal combinations — the "one bank tells many stories" mechanism;
- **§7–§8** additive manifest extensions and derived-background ops for `assemble_from_bank.py`;
- **§9–§10** gap analysis for the build lane and a zero-GPU byte-verifiable pilot.

**Image-first boundary respected (contract spec §1.3):** every rule below is 2D — enums, percent coordinates, one linear formula, PIL ops. No 3D geometry, no camera matrices, no scene graphs. The eye-level line and anchor slots are *metadata about a 2D image*, exactly like `subject_placement_bbox` today.

**Out of scope:** multi-character composites (§15.B cliff unchanged), action genres, GPU rendering of any kind. This spec changes how banked images are *combined*, not how they are *rendered*.

## 2. Where the existing specs stop

| Existing artifact | What it already gives us | Where it stops (the void) |
|---|---|---|
| Contract spec §5 (safe zones, CU/MCU/MS/LS/ELS/ECU/insert) | Per-layer render framing vocabulary + margins — a shot vocabulary fragment | Governs each layer *alone* at render time; says nothing about which framings may combine with which backgrounds |
| Contract spec §7 (19 archetype layer maps) | archetype → layer recipe; some BG awareness (`bg_softfocus` for face archetypes) | Informal; `bg_softfocus` is a prompt string, not a typed BG class; no legality rule |
| Contract spec §10 + `assemble_from_bank.py` | Deterministic paste mechanics, z-order, screen blend, provenance | Min-fit-and-center into a bbox: no eye-level, no ground contact, no shadow, no occluder, no compatibility check of any kind |
| Contract spec §14.B.2/B.3 | Names perspective/scale mismatch as failure modes | Post-hoc *detection* only; no constructive rule to pick compatible assets |
| Contract spec §15.D.3 | "Reusable cinematic grammar" as a future unlock | Explicitly future; this spec is that unlock's first concrete layer |
| V5 spec (§7 decompose) | Geometric coherence *within* one panel by construction | Silent on cross-panel bank reuse rules — when a decomposed subject may sit on a *different* background |
| `assembly_manifest.schema.json` | `archetype`, `beat_type` fields; per-layer bbox + provenance | Fields are informational; layers carry zero composition metadata |
| Bank assets on disk | filename conventions + render-lineage `.provenance.json` | No camera angle, eye-level, crop class, lighting direction, or BG class anywhere |

Live confirmation of the void: manifest `mira_qwen_pulid_character_strip_v2` (2026-07-07) hand-improvises the fix ("ban flat-cream portrait cards; anchored scene / diegetic CU / insert macro / breath closure") with no spec behind it. Hand-discipline that has to be re-derived per session is a missing enforcement layer by this repo's own doctrine.

## 3. Industry basis (four pillars; full citations in the research doc)

1. **Anime layout system (レイアウト).** One layout sheet per cut carries eye-level, vanishing points, character silhouettes, and camera notes; the BG painter and key animator both work FROM it — one geometry, two departments. Angle buckets (aori/fukan/eye-level) gate reuse; the Tezuka-era *bank system* stored cel + background as a **pair** because cross-angle reuse is impossible. Occluders are separate BOOK layers above the cel; contact edges carry kumi-sen registration lines. → our §4 camera block, §5 G2/G5, diegetic pairs.
2. **VN sprite grammar.** Waist-up sprites over backgrounds are *accepted stage grammar* when the BG is built for it: eye-level camera, horizon near sprite eye-line, empty center stage, bottom-anchored sprites at named stage positions, BG defocus/darken on close-ups. The failure modes are exactly ours: camera-height mismatch, lighting mismatch, occupied center stage. → §5 G1 legality + defocus rule, §4 anchor slots.
3. **Film/VFX grounding math.** The horizon-ratio law (Sedgwick): a standing element's image height is *linear* in its feet-Y measured from the horizon — `h_px = (S_m / E_m) · (y_feet − y_horizon)` — zero at the horizon. Plus: contact shadows (two-layer ellipse, concrete opacity/blur numbers), occlusion interleave as the strongest single grounding cue, defringe + black/white-level match as the line-art-applicable integration ops. → §5 G3/G4/G5/G6.
4. **Manga panel grammar.** Corpus + craft consensus: most panels are single-figure with reduced environment (Cohn's Mono dominance); full room renders appear once per scene (establishing, mandatory) then BG class legally drops to abstract because the reader retains the space; emotion beats swap literal BG for a codified manpu vocabulary; ≥1 long shot per spread in pro register. → §6 grammar + scene invariants.

**Recommendation adopted:** no single industry fits whole; the scheme is a synthesis — anime layout discipline for geometry, VN stage grammar for crop×BG legality, VFX math for grounding ops, manga beat grammar for shot selection — under our existing contract-first architecture. Every rule is adopted from a cited source, not invented.

## 4. Asset composition metadata — `composition_meta`

Sidecar JSON per banked asset: `<asset_stem>.composition.json`, sibling to the existing `.provenance.json` (which it complements, never replaces). Authored once per asset (hand-annotation is acceptable and cheap for the current bank; V5 pairs derive most fields by construction). Machine-readable schema to be added at `schemas/manga/composition_meta.schema.json` by the build lane.

### 4.1 Common block (all layer classes)

```yaml
schema_version: "1.0.0"
asset_id: "L0_2b9283d4c387"            # matches bank filename stem
layer_class: L0                        # L0|L1|L2|L3|L4 (contract spec §4)
light:
  azimuth: camera_left                 # camera_left|camera_right|frontal|back|ambient
  temporal_state: dawn                 # dawn|day|evening|night (continuity spec vocab)
style_register: iyashikei_color        # panel_templates template_id
```

### 4.2 L0 background block

```yaml
bg_class: full_render        # REQUIRED — the load-bearing enum:
                             #   full_render     — fully-rendered perspective scene
                             #   partial_motif   — 1–3 signature props / simplified space
                             #   defocus_derived — deterministic blur of a full_render plate (§8)
                             #   tone_gradient   — screentone / gradient / flat fill
                             #   manpu_emotion   — codified emotion texture (§6.1 lookup)
                             #   speedlines_focus— speed/focus lines (non-iyashikei genres)
                             #   white_void | black_void
camera:
  angle_bucket: eye_level    # eye_level|aori (low)|fukan (high)|overhead
  eye_level_y_pct: 42        # horizon height, % of canvas from top — REQUIRED for full_render/partial_motif
  camera_height: seated      # standing|seated|low|overhead (metric hint: ~1.55m|~1.15m|≤0.5m)
ground_plane:
  visible: true
  frame_bottom_depth_m: 1.8  # optional: estimated ground distance at frame bottom
anchor_slots:                # named stage positions where a subject may be seated INTO the scene
  - slot_id: seat_at_table
    kind: seat               # stand|seat|lean
    feet_y_pct: 78           # ground/seat contact line for this slot, % of canvas from top
    center_x_pct: 42
    expected_figure_h_pct: 55   # standing-adult apparent height at this depth (validates G3)
    occluder_crop_bbox_pct: [30, 70, 45, 30]   # optional: region of THIS plate croppable as a BOOK layer (table edge)
```

### 4.3 L2 character block

```yaml
crop_class: waist_up         # full_figure|knees_up|thigh_up|waist_up|bust|face_cu|ecu_fragment|hands|silhouette
                             # (compiles from §5 framing rows: LS→full_figure, MS→knees/thigh, MCU→waist, CU→bust/face, ECU→fragment/hands)
anchor:
  point: waist_line          # feet|seat|waist_line — the y used for grounding
  y_px: 1493                 # anchor y in asset pixels (post-cutout)
eye_y_px: 310                # character eye line in asset pixels
implied_camera:
  angle_bucket: eye_level    # the angle the character was RENDERED at — gates reuse (G2)
  el_crossing: chest         # body landmark the horizon crosses at this render's implied camera height
pose_id: front_portrait_seated_calm   # existing bank vocabulary
figure_height_m: 1.62        # settei height (character_design SSOT)
diegetic_pair: L0_2b9283d4c387        # optional: the L0 this subject was decomposed FROM (V5) — see §4.5
```

### 4.4 L1/L3 object block

```yaml
real_height_m: 0.24          # scale anchor (kettle 24cm, cup 9cm, door 2.03m, table top 0.75m, chair seat 0.46m)
contact_type: table          # floor|table|wall|held|airborne
```

### 4.5 Diegetic pairs — the bank-system rule

A V5 decompose emits subject + background layers from ONE dispatch: they share geometry **by construction**. The bank stores them cross-referenced (`diegetic_pair`), exactly as the anime bank system stored cel+BG as a pair. Compatibility consequences:

- subject over its own pair background: **legal with zero checks** (G2/G3 auto-pass) — geometry is single-sourced;
- subject over a *different* full_render background: full G1–G9 gating applies;
- a **diegetic crop** (the paired composite cropped as one flat image, e.g. `diegetic_cu_tense_kitchen.png`) is a single L0-class asset with `bg_class: full_render`, legal by construction for CU beats — formalizing what the 2026-07-07 manifest hand-did.

## 5. Combination compatibility gates (deterministic)

Gates are numbered G1–G9. Severity classes follow contract spec §12.0: **A = deterministic FAIL** (blocks assembly), **B = heuristic WARN**. All run in `assemble_from_bank.py` (or its manifest generator) *before* pixels move.

### G1 — crop × bg_class legality matrix (class A)

| L2 crop_class ↓ / L0 bg_class → | full_render | partial_motif | defocus_derived | tone_gradient | manpu_emotion | white/black_void |
|---|---|---|---|---|---|---|
| full_figure | **LEGAL+ops** (G3+G4 required, G5 recommended) | LEGAL+ops | LEGAL | LEGAL (pin-up/tobira register — WARN outside chapter-open) | WARN (pin-up) | LEGAL (intro/fashion register) |
| knees_up / thigh_up | **LEGAL+ops** (G3 seat/lean anchor + G4) | LEGAL+ops | LEGAL | LEGAL | LEGAL | LEGAL |
| waist_up | **ILLEGAL** — unless `diegetic_pair` match | LEGAL | **LEGAL (default)** | LEGAL | LEGAL | LEGAL |
| bust | **ILLEGAL** — unless diegetic | LEGAL (prop sliver) | **LEGAL (default)** | LEGAL (default) | LEGAL (emotive) | LEGAL |
| face_cu | **ILLEGAL** (focus conflict) | WARN | LEGAL | LEGAL | LEGAL (default emotive) | LEGAL (peak register) |
| ecu_fragment / hands | ILLEGAL | WARN | LEGAL | **LEGAL (default)** | LEGAL | LEGAL |
| silhouette | LEGAL (any) | LEGAL | LEGAL | LEGAL | LEGAL | LEGAL |

Sources: manga Table B (research doc §2.4); VN bust-over-defocus stage grammar (§2.2). The single most important row is **waist_up × full_render: ILLEGAL** — that row *is* the operator's floating-half-person, made structurally impossible.

**Crop hygiene (class A, per asset):** crop boundaries at torso/waist/thigh/shin/upper-arm only — never at a joint (knee/elbow/neck). Encoded at bank-annotation time in `crop_class` validity.

### G2 — angle-bucket match (class A)

`L2.implied_camera.angle_bucket == L0.camera.angle_bucket` required for full_render/partial_motif combinations (abstract classes exempt). Cross-bucket reuse is forbidden — the bank-system rule. `eye_level_y_pct` agreement within ±8 pct-points is class B (WARN) until calibrated.

### G3 — grounding law (class A when a ground-contact anchor exists)

For a subject placed at an anchor slot on a full_render/partial_motif L0:

```
scale = target_figure_h_px / asset_figure_h_px
target_figure_h_px = (figure_height_m / camera_height_m) × (y_feet_px − y_horizon_px)     # horizon-ratio law
paste: anchor.point (feet|seat) lands ON slot.feet_y_pct; x centered on slot.center_x_pct
```

- Replaces §10's min-fit-and-center **whenever `composition_meta` is present on both sides**; §10 math remains the fallback for legacy unannotated assets (flagged WARN `bbox_legacy`).
- Validity: `y_feet > y_horizon` (subjects never paste above the horizon on a ground plane); computed height must agree with `slot.expected_figure_h_pct` within ±15% (else FAIL — wrong-depth asset).
- Seated subjects: anchor `seat` to the slot's seat line; the horizon must cross the figure at the landmark consistent with `camera_height` (standing camera ≈ eyes/head; seated camera ≈ chest/waist) — class B check.

### G4 — contact shadow contract (class A for floor/seat/table contact on full_render/partial_motif)

Two stacked multiply ellipses under the contact edge, color sampled from the plate's existing shadows (never pure black):

| layer | width | height | opacity | blur |
|---|---|---|---|---|
| core/contact | 0.8–1.0 × subject width at contact | 0.15–0.25 × its own width | 60–90% | ≈1–2% of subject height |
| ambient pool | core × 1.3–1.6 | proportional | 20–40% | ≈5–8% of subject height |

Shadow center directly under contact points, offset toward the shaded side (opposite `light.azimuth`). Deterministic PIL; even a weak contact shadow beats a perfect cutout with none. Applies equally to L3 objects with `contact_type: floor|table`.

### G5 — occlusion interleave / BOOK layer (class B, recommended → promotable per §12.0)

Full-figure and knees-up subjects on full_render L0 SHOULD receive one occluder layer above L2 covering 5–15% of the lower/side silhouette. Deterministic derivation: crop `anchor_slots[].occluder_crop_bbox_pct` from the L0 plate itself, paste above L2 (z=25, between L2 and L3-above). This is the anime BOOK layer; occlusion is the strongest single pictorial grounding cue. Occluders are always separate layers, never baked into L0 or L2.

### G6 — edge + ink-level hygiene (class B)

- `defringe(1–2 px)` on every cutout paste (kills white/AA halo — the #1 line-art paste giveaway) + 1 px anti-alias feather. Exempt: L4.
- Level match: subject's darkest ink and brightest paper must not exceed the plate's range (histogram min/max remap).

### G7 — depth attenuation (class B; distant figures only)

For subjects placed at depth (apparent height < ~40% of a standing figure at frame bottom): thin/lighten linework toward paper-white and reduce interior detail proportionally to normalized depth. Iyashikei rarely needs this; mandatory before any genre with staging depth.

### G8 — light-azimuth consistency (class A given metadata)

`L2.light.azimuth` compatible with `L0.light.azimuth` (exact match, or either side `ambient`). Same key gates L3 objects. This is the existing light-rig doctrine (continuity spec §9) promoted to a *bank-combination* key.

### G9 — scale-anchor sanity (class B)

Where an L0 anchor slot and a known-size L1/L3 object co-locate, implied px/m at that depth must agree within ~10% (door 2.03 m, table 0.75 m, chair seat 0.46 m, adult 1.65–1.8 m).

## 6. Panel-shot grammar — beat → shot → layer recipe

### 6.1 Shot-type enum and recipes

| shot_type | framing row (§5 contract) | legal bg_class | layer recipe | required ops |
|---|---|---|---|---|
| `establishing` | LS/ELS wide | full_render ONLY | L0 (+ full_figure L2 at anchor slot, or figure-in-L0 per ELS rule) + optional L1/L4 | G2,G3,G4; G5 recommended |
| `re_establish` | MS/LS | full_render or partial_motif | L0 + optional L2 knees_up+ | G2,G3,G4 |
| `dialogue_bust` | MCU/CU | defocus_derived (default), tone_gradient, partial_motif | derived-L0 + L2 waist_up/bust | G6; 180°/side-consistency (§6.2) |
| `reaction_emotion` | CU | manpu_emotion, tone_gradient, white_void | manpu-L0 + L2 bust/face_cu | G6; manpu lookup by emotional_state |
| `realization` | ECU/CU | white_void + betaflash-style contrast, tone | L0-void + L2 face_cu/ecu | G6 |
| `insert_object` | ECU/insert | tone_gradient, white_void, or diegetic macro crop | L0-tone + L3 (or diegetic L0 crop alone) | G6, G9 |
| `pillow_ma` | wide/amorphic | full_render scenery (low density) or single-object on white | L0 alone (+L4) — **zero figures** | — |
| `closure_breath` | wide/insert | full_render fragment or defocus | L0 (+L4) | — |
| `diegetic_cu` | CU/MCU | full_render **by construction** | single paired/cropped plate (§4.5) | none (geometry single-sourced) |

Manpu lookup (`reaction_emotion`): `affection→flowers/soft sparkle`, `admiration→sparkle`, `calm-soothe→bubbles/soft gradient`, `realization→betaflash`, `dread/depression→tare-sen vertical drips`, `suspense→kakeami hatch`, `unease→odoro curls`. Iyashikei filter: `forbidden_grammar` in `panel_templates/iyashikei.yaml` still applies (no speedlines etc.); the gentle subset (flowers, bubbles, gradient, white) is the iyashikei-legal manpu set.

### 6.2 Scene-level grammar invariants (chapter validator; class A unless noted)

1. **One `establishing` (full_render) panel opens every scene/location change.** Mandatory.
2. **Abstract BG classes are legal only after the scene's establishing panel** — the reader retains the space; the bank amortizes the room render exactly like a webtoon studio amortizes its 3D set.
3. **Re-establish** (full_render/partial_motif) required after: time jump, location change, or >6 consecutive abstract-BG panels (class B threshold, tune empirically).
4. **≥1 long-shot panel per screen-run** (webtoon scroll equivalent of the per-spread rule; class B).
5. **Speaker side-consistency:** a character keeps their left/right frame side across a dialogue run; flipping sides requires a re-establishing or bridging panel (the 180° rule's single-character projection; `flip_h` in manifests must respect it).
6. **`pillow_ma` panels contain zero figures** (inserting a character defeats the pillow function). Iyashikei's silence-panel ratio (≥50%, existing genre rule) is unchanged and served by this shot type.
7. **Panel-border bleed** stays an emphasis currency — reserve frame-break for peak `reaction_emotion` panels (class B budget: ≤1 per scene).

### 6.3 The 19 iyashikei archetypes mapped (no archetype re-authoring — a lookup column)

`sparse_establishing_wide→establishing` · `morning_routine_sequence→re_establish` · `walking_in_thought_medium→re_establish` · `shared_meal_table_medium→(deferred §15.B)` · `character_quiet_face / character_face_micro_tension→reaction_emotion or diegetic_cu` · `chest_breath_micro→dialogue_bust register` · `tea_beat_close_up / hand_table_micro / dappled_light_hand / phone_notification_macro / food_preparation_overhead→insert_object (hands variants)` · `kettle_steam_macro / seasonal_anchor_object→insert_object` · `window_light_threshold→diegetic_cu (silhouette exception)` · `pet_companion_micro→insert_object` · `long_drop_decompression / miyazaki_ma_pause→pillow_ma` · `pendulation_pair_visual_rhyme→closure_breath pairing`. Build lane adds a `shot_type` field per archetype in `iyashikei.yaml` (additive).

### 6.4 Wiring point

Beat (chapter_script / continuity_state) → `shot_type` (via archetype column) → legal-recipe resolution against the bank's `composition_meta` (G1–G9) → assembly manifest. This slots into the OPD-135 Milestone C manifest generator; `assemble_from_bank.py` enforces the gates at assembly time as defense-in-depth. Fail-closed: no legal combination in the bank → panel enters the render queue (bank gap), never a downgraded illegal paste.

## 7. Assembly-manifest extension (additive-safe)

Panel level: `shot_type` (enum §6.1). Layer level (all optional — absent means legacy §10 behavior + WARN):

```yaml
- layer_class: L2
  asset: <path>
  anchor_slot: seat_at_table          # replaces bbox_pct when composition_meta present
  grounding:
    mode: horizon_scale               # horizon_scale | bbox_legacy
    contact_shadow: auto              # auto | none (auto = G4 recipe)
    occluder: auto                    # auto | none (auto = G5 BOOK derivation)
  bbox_pct: [...]                     # retained for bbox_legacy / L4
```

Derived backgrounds (§8) appear as L0 layers with a `derivation` block. `provenance` stays `REAL|INTERIM`; a deterministic derivation of a REAL plate remains REAL with lineage recorded:

```yaml
- layer_class: L0
  asset: <full_render plate path>
  provenance: REAL
  derivation: { op: defocus, radius_px: 10, darken_pct: 8 }
```

## 8. Derived-background ops (deterministic PIL, zero GPU)

| op | recipe | produces bg_class |
|---|---|---|
| `defocus` | Gaussian blur radius 8–14 px (1080-wide basis) + optional darken 5–12% + desaturate 10–20% | defocus_derived — the default dialogue-bust stage |
| `tone_flat` | flat fill sampled from series palette ± subtle grain | tone_gradient |
| `gradient` | 2-stop vertical gradient from palette | tone_gradient |
| `void` | paper white / ink black | white_void / black_void |
| `manpu` | banked or procedural emotion texture per §6.1 lookup (iyashikei-legal subset) | manpu_emotion |
| `plate_crop` | crop of a full_render plate (macro insert, occluder BOOK, breath fragment) | full_render (fragment) |

Derivation from a REAL plate preserves spatial retention (the blurred kitchen is still *that* kitchen) — strictly better than an unrelated abstract card, and free.

## 9. Gap analysis → build lane

| Delta | Size | Nature |
|---|---|---|
| `composition_meta` sidecar schema + hand-annotation of current bank (5 L0 plates, 19 L2 poses, 2 diegetic CUs) | small | authoring; ~1–2 min/asset by eyeball; no re-render |
| G1/G2/G8 legality gates in assembler + manifest generator | small | pure lookups once metadata exists |
| G3 grounding math (replace min-fit when metadata present) | small | one formula + anchor resolution |
| G4 contact shadow + G6 defringe/level ops | small–medium | deterministic PIL |
| G5 occluder derivation | medium | plate crop + z=25 insertion |
| §8 derived-BG ops | small | PIL |
| §6.2 chapter-level grammar validator | medium | manifest-sequence linting |
| `iyashikei.yaml` shot_type column + manifest schema fields | small | additive config/schema |
| Re-banking need | **none for pilot** | existing April assets suffice; the only *systemic* bank gap is object-free L0 plate variants (already logged, contract spec §8.2) and, later, per-slot pose coverage |
| NOT built | — | no 3D, no camera solver, no ML horizon detector (hand-annotation first; heuristic later if annotation cost bites at scale) |

## 10. Pilot proof plan (cheapest byte-verifiable test; zero GPU; Tier 1)

**EXECUTED-REAL (2026-07-07, PR #4689):** this pilot ran exactly as scoped below — 3 hand-annotated sidecars, 4-panel grammar strip + `waist_up × full_render` control (deterministic G1 FAIL on the control), byte-verified artifacts at `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/composition_grammar_pilot/` (`FINDINGS.md` + `gate_report.json`). Verdict: the grammar holds; no compositor rewrite required; the surgical assembler patch set is FINDINGS.md §"Recommended next patch set". The steps below are retained as the executed protocol.

1. Hand-author `composition.json` for: 1 kitchen plate (`L0_2b9283d4c387` — eye_level_y, `seat_at_table` slot with feet line + occluder crop bbox, light azimuth), 2 L2 cutouts (one full/knees-up seated pose, one waist-up), stove + window crops.
2. Assemble a 4-panel strip with a prototype of the G-ops (standalone script or assembler branch):
   - **P1 `establishing`** — seated figure at anchor slot, horizon-ratio scale, contact shadow, table-edge BOOK occluder;
   - **P2 `dialogue_bust`** — waist-up L2 over `defocus` derivation of the *same* plate;
   - **P3 `insert_object`** — existing stove macro crop (legal as-is);
   - **P4 `reaction_emotion`** — bust over palette tone/gradient.
3. Control: the current naive output (`char_p1` of `mira_qwen_pulid_character_strip_v2` — bbox min-fit paste, no grounding) side-by-side.
4. **Acceptance:** gates G1–G4+G6 pass on P1–P4 and demonstrably FAIL on the control (G1 illegal combo or G3/G4 missing-grounding); operator eyeball confirms the strip reads as staged panels, not stickers. Artifacts byte-verified (>50 KB each) under `artifacts/manga/<series>/assembled/composition_grammar_pilot/` with the standard provenance table.
5. Cost: ~0 GPU-h; a few Tier-1 hours. On pass → wire gates into `assemble_from_bank.py` + manifest generator (M5 lane); on fail → the failing gate's constants (G3 tolerance, G4 opacities, defocus radius) are the tunables, not the architecture.

## 11. Acceptance criteria and non-goals

- This spec reaches **CODE-WIRED** only when G1–G4+G6 run inside `assemble_from_bank.py`/manifest generation with a named entrypoint; **EXECUTED-REAL** only with byte-verified pilot output; **PROVEN-AT-BAR** only via the R7 blind-judge protocol. Label claims accordingly.
- Non-goals: multi-character grammar (§15.B), action-genre BG classes beyond enum reservation, any GPU or model work, any change to render contracts (§5/§8/§9 of the contract spec are untouched).

## 12. Cross-references

- Parent: `docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md` v0.7.1 §10 (marker added pointing here); §12 severity classes reused; §15.D.3 partially realized.
- Sibling: `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` §7/§8 (decomposed layers are this spec's diegetic pairs — the reconciliation the 2026-07-03 audit called for).
- Landed pilot implementation (PR #4689): `scripts/manga/composition_grammar.py` (G1–G6 + §8 ops), `schemas/manga/composition_meta.schema.json`, `scripts/manga/run_composition_grammar_pilot.py`, pilot artifacts + FINDINGS.md.
- Consumers (build lane): `scripts/manga/assemble_from_bank.py`, OPD-135 Milestone C manifest generator, `schemas/manga/assembly_manifest.schema.json`, `config/manga/panel_templates/iyashikei.yaml`.
- Research basis: `artifacts/research/manga_composition_grammar_research_2026-07-07.md` (all external citations).
- Registry: `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv` row `manga_composition_grammar`.

**Version history:** v1.0.0 (2026-07-07) — initial spec from the composition-grammar research lane; status SPECCED. v1.0.1 (2026-07-07) — post-pilot amendment: §10 marked EXECUTED-REAL per PR #4689; taxonomy header updated (pilot module + sidecar schema landed; assembler path still ABSENT).

## 13. Structural Composition MVP — implementation status (2026-07-12)

**Layer separation (mandatory):** `PANEL_TYPE_SYSTEM_V1` = storytelling / camera / crop / bubble taxonomy.
`STRUCTURAL_COMPOSITION_MVP` = runtime legality / support / contact / candidate acceptance.
Do **not** collapse structural rules into panel-type doctrine.

| Path | Role | Layer claim |
|------|------|-------------|
| `config/manga/composition_validation.yaml` | Structural validation profile + THRESHOLD-001 bindings | CONFIG-EXISTS → CODE-WIRED via `structural_composition.py` |
| `config/manga/structural_templates.yaml` | `seated_table_scene` / `standing_room_scene` registry | CONFIG-EXISTS → CODE-WIRED |
| `config/manga/panel_type_structural_bridge.yaml` | Additive `panel_type_id → template/relations/proof` bridge | CONFIG-EXISTS → CODE-WIRED |
| `schemas/manga/structural_bundle.schema.json` | Support/contact graph schema | CONFIG-EXISTS |
| `schemas/manga/structural_plan.schema.json` | Resolved plan envelope (`plan_hash` on envelope, not body) | CONFIG-EXISTS |
| `scripts/manga/structural_composition.py` | Shared transform + graph validation + overlay + render consume | CODE-WIRED |
| `scripts/manga/plan_panel_layout.py` | Plan writer → quarantine `plans/` | CODE-WIRED |
| `scripts/manga/validate_scene_assembly_visual.py` | Quarantine routing + operator verdict promotion | CODE-WIRED |

**Honest non-claims:** This section does **not** claim `assemble_from_bank.py` now consumes structural plans by default.
Lettering: live assembler still calls `bubble_render.render_bubbles_onto_panel` (v1); `bubble_render_v2` exists but is not the assembler call path; compiled safe-zone QC lives in `validate_layer.py`. Structural MVP did **not** rewire lettering.
Universal horizon-ratio acceptance remains **not** canon (checklist SCALE-001); structural MVP uses support/contact graph + shared transform instead.

**Doctrine singleton:** `artifacts/qa/MANGA_CANON_SCENE_ASSEMBLY_CHECKLIST.md` — do not duplicate gate prose here.

