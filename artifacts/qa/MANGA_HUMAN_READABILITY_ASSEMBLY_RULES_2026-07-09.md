# Manga Human Readability Assembly Rules — 2026-07-09

**Lane:** research-to-rules (not render)  
**Status:** authored candidate (SPECCED; partial code wiring — see §12 drift table)  
**Acceptance layer:** authored candidate — not system-working until HR-WIRE-* gates land  
**Authority stack:** external craft/comics theory (cited inline) → `MANGA_COMPOSITION_GRAMMAR_SPEC.md` → operator half-person rule (2026-07-09) → repo pipeline audit  
**Companion JSON:** `artifacts/qa/manga_human_readability_rules_2026-07-09.json`

---

## Executive summary

A human can read a sequential manga image when four subsystems agree:

1. **Where to look** — panel/page eye-flow and balloon order match reading direction.
2. **Where the body is** — crop class, horizon, anchor slot, contact shadow, and occluder tell the reader the figure occupies space.
3. **What beat this is** — shot type + bg_class + panel size communicate calm, dialogue, action, or reveal.
4. **What must never happen** — floating torsos, angle/light mismatch, balloon occlusion of faces, or abstract BG before establishing.

The repo already encodes (1)–(2) partially in `composition_grammar.py` + `panel_planning_rules.py`. Gaps: chapter-level grammar (§6.2), bubble placement vs composition, genre overlays, and fail-closed wiring in manifest gen + assembler load path.

---

## 1. Universal rules for readable sequential image assembly

### 1.1 Spatial grounding (figure-in-space)

| Rule ID | Rule | Deterministic enforcement | Sources |
|---|---|---|---|
| HR-U01 | **Establish before abstract.** Every new scene/location opens with at least one `full_render` establishing panel before any abstract bg_class (`defocus_derived`, `tone_gradient`, `manpu_emotion`, void). | Chapter validator: first panel at location must be `shot_type=establishing` + `bg_class=full_render`. | Craft consensus (Clip Studio, Boords); Cohn Mono/Macro corpus; spec §6.2 inv.1 |
| HR-U02 | **Horizon-ratio scale on room plates.** Full-figure / knees-up / thigh-up on `full_render` must paste via G3: feet/seat anchor below `eye_level_y_pct`, scaled by `(figure_height_m / camera_height_m) × (y_feet − y_horizon)`. | `composition_grammar.g3_horizon_scale_check`, `plan_horizon_scale_paste`. | Sedgwick horizon law; anime layout; spec §5 G3 |
| HR-U03 | **Contact shadow mandatory on ground contact.** Any figure with floor/seat/table contact on readable L0 gets G4 two-ellipse shadow under contact edge, color sampled from plate (never pure black). | `render_contact_shadow_layer` + gate G4. | VFX compositing (Pixel Monkey, CSP); spec §5 G4 |
| HR-U04 | **Occluder BOOK layer when lower body hidden.** Knees-up / full-figure on room SHOULD receive L0 crop occluder (table edge, counter, booth) above L2 covering 5–15% of silhouette. | G5 `paste_occluder_from_slot` when `grounding.occluder=true`. | Anime BOOK layer doctrine; spec §5 G5 |
| HR-U05 | **Angle-bucket match.** L2 `implied_camera.angle_bucket` must equal L0 `camera.angle_bucket` on readable backgrounds. | G2 fail-closed. | Anime bank-system / cel+BG pair rule; spec §5 G2 |
| HR-U06 | **Light azimuth compatibility.** L2 and L0 `light.azimuth` must match or either is `ambient`. | G8 fail-closed. | Continuity spec §9; spec §5 G8 |
| HR-U07 | **Defringe every cutout.** 1–2px alpha shrink on L2 paste (G6). | `defringe_cutout`. | Line-art paste hygiene; spec §5 G6 |
| HR-U08 | **Look space / lead room.** Character gaze direction must leave ≥15% canvas width on the look side; subject not centered when looking off-frame. | Planner: set `anchor_slot.center_x_pct` + manifest `flip_h` to preserve lead room. | Rule of thirds; storyboard guides (Gugu, Clip Studio) |
| HR-U09 | **180° speaker side consistency.** Active speaker keeps same left/right frame side across a dialogue run; side flip requires re-establish or bridging panel. | Chapter validator inv.5; manifest `flip_h` audit. | Klein, Rivkah camera conventions; spec §6.2 inv.5 |
| HR-U10 | **Shot variety rhythm.** No more than 3 consecutive panels at same crop band without a wider or insert break. | Chapter validator (class B). | Daredevil page craft (Rivkah); storyboard shot-type alternation |
| HR-U11 | **Abstract close-stage bottom anchor.** Bust/waist/face on abstract BG must bottom-anchor (`feet_y_pct` / `bust_bottom_y_pct` ≥ 75%) so missing lower body is explained by crop, not by floating. | `dialogue_bust_paste` + `DEFAULT_ABSTRACT_STAGE_SLOT`. | VN sprite stage grammar; spec §6.1 |
| HR-U12 | **Spatial retention on dialogue.** Dialogue/reaction busts default to `defocus` derivation of the *same* room plate, not unrelated tone card. | Manifest `_l0_derivation` for `dialogue_bust`/`reaction_emotion`. | VN defocus stage; spec §8 |
| HR-U13 | **Scale-anchor sanity.** Co-located door (~2.03m), table (~0.75m), chair seat (~0.46m), adult (~1.62m) agree within ±10% at anchor depth. | G9 (class B). | Interior scale refs; spec §5 G9 |
| HR-U14 | **Provenance honesty.** Every manifest layer REAL or INTERIM; INTERIM never presentable as final. | `assemble_from_bank.validate_manifest`. | Contract spec §4; stub-as-done CI |
| HR-U15 | **Panel eye entry.** Primary subject or action focal point lands in upper third for vertical webtoon panels; reader scrolls into subject, not empty ceiling. | Planner archetype bbox + anchor_slot vertical band. | ImageTexT koma construction; webtoon scroll UX |

### 1.2 Panel-to-panel continuity

| Rule ID | Rule | Enforcement |
|---|---|---|
| HR-U16 | **Re-establish triggers.** After location change, time jump, or >6 consecutive abstract-BG panels → require `re_establish` on `full_render` or `partial_motif`. | Chapter validator §6.2 inv.3 |
| HR-U17 | **≥1 long-shot per screen-run** (webtoon scroll equivalent of per-spread rule). | Chapter validator §6.2 inv.4 (class B) |
| HR-U18 | **Closure between units.** Do not jump over panel groups; gutters imply pause (Cohn assemblage: smooth paths > broken paths). | Page layout composer |
| HR-U19 | **Motion direction consistency.** Left-to-right action must not reverse screen direction without cutaway/re-establish. | Chapter validator + action genre overlay |
| HR-U20 | **Insert objects carry narrative weight.** ECU inserts (hands, cup, phone) use `tone_gradient` or diegetic macro — never readable full room behind hands-only crop. | `panel_planning_rules` abstract-shot check; manifest derivation |

### 1.3 Speech and lettering readability

| Rule ID | Rule | Enforcement |
|---|---|---|
| HR-U21 | **Reading order inside panel.** For en_US LTR: balloons top→bottom, left→right; first speaker left when possible. For ja_JP RTL manga: top-right first, then left, then down (see bubble zone sequence). | `bubble_render._default_zone_sequence` |
| HR-U22 | **Tail to mouth.** Balloon tail terminates ~50–60% of distance to speaker mouth/head; never points at body or empty space. | `bubble_render._draw_tail_pointer` + validator |
| HR-U23 | **No face occlusion.** Balloons must not cover eyes, mouth, or primary expression real estate. | Bubble validator (NOT YET WIRED) |
| HR-U24 | **Coverage ceiling.** Total balloon area ≤30% of panel (`coverage_limit` default). | `bubble_render._coverage_ratio` |
| HR-U25 | **Silence is readable.** `pillow_ma` and narrator-only panels: zero dialogue balloons; optional caption strip only. | Shot recipe + chapter validator inv.6 |
| HR-U26 | **SFX do not replace gesture.** SFX placed off-center; must not compete with dialogue zones or faces. | `bubble_render` SFX scatter positions |

---

## 2. Forbidden patterns

| Rule ID | Pattern | Why unreadable | Current repo status |
|---|---|---|---|
| HR-F01 | **Floating half-person in room** — bust/waist/face_cu over `full_render` via center bbox paste, no occluder, no diegetic pair | Reader cannot locate body in space; breaks manga CU convention (abstract BG only) | FAIL in `panel_planning_rules` (tests pass); **NOT wired** in `generate_assembly_manifest` / `assemble_from_bank.load_manifest` |
| HR-F02 | **Top-floating torso** — bbox y < 22% on room plate | Implies character hanging from ceiling | FAIL in planning rules |
| HR-F03 | **Abstract BG before establishing** | Reader has no spatial model | **UNENFORCED** — §6.2 chapter validator absent |
| HR-F04 | **Scene-contaminated bust** — cup/table/chair baked into L2 alpha on abstract stage | Props imply room that bg_class denies | FAIL in `l2_asset_has_scene_contamination` |
| HR-F05 | **Post-hoc defocus salvage** — blur readable room instead of manifest derivation at plan time | Hides illegal combo; still wrong if structure nonsensical | Operator rule: derivation at manifest gen |
| HR-F06 | **Angle-bucket mismatch paste** | Figure reads as pasted sticker | G2 FAIL when sidecars present |
| HR-F07 | **Missing contact shadow on grounded figure** | Hovering sticker effect | G4 FAIL when grammar path active |
| HR-F08 | **Balloon crosses another tail** | Ambiguous speaker order | **UNENFORCED** in bubble_render |
| HR-F09 | **Balloon covers face** | Expression lost | **UNENFORCED** |
| HR-F10 | **>30% balloon coverage** | Art suffocated | Partially enforced (shrink/skip) |
| HR-F11 | **Character in pillow_ma panel** | Defeats silence/ma function | Spec §6.2 inv.6 — **UNENFORCED** |
| HR-F12 | **Cross-genre asset salvage** — iyashikei bust pasted into mecha hangar | Wrong scale, wrong register, wrong crop×bg | Quarantined invalid proofs |
| HR-F13 | **Four-way panel intersection** (page layout) | Eye-flow ambiguity | Page composer — **UNENFORCED** at assembly lane |
| HR-F14 | **Speedline wall** — dense lines on every panel | Nothing emphasized | Genre overlay for action |
| HR-F15 | **Crop at joint** — knee/elbow/neck cut line | Uncanny, breaks figure coherence | Bank annotation validity |

---

## 3. Crop / room legality matrix

Derived from G1 matrix (`composition_grammar.py`) + operator half-person rule.

### 3.1 Matrix (L2 crop × L0 bg_class)

| crop_class ↓ / bg_class → | full_render | partial_motif | defocus_derived | tone_gradient | manpu_emotion | white/black_void |
|---|---|---|---|---|---|---|
| full_figure | **LEGAL+G3+G4** (+G5 rec) | LEGAL+ops | LEGAL | LEGAL | WARN | LEGAL |
| knees_up / thigh_up | **LEGAL+G3+G4** | LEGAL+ops | LEGAL | LEGAL | LEGAL | LEGAL |
| waist_up | **ILLEGAL*** | LEGAL | **LEGAL (default dialogue)** | LEGAL | LEGAL | LEGAL |
| bust | **ILLEGAL*** | LEGAL (prop sliver) | **LEGAL (default)** | LEGAL | LEGAL (emotive) | LEGAL |
| face_cu | **ILLEGAL*** | WARN | LEGAL | LEGAL | LEGAL (default) | LEGAL |
| ecu_fragment / hands | **ILLEGAL** | WARN | LEGAL | **LEGAL (default insert)** | LEGAL | LEGAL |
| silhouette | LEGAL | LEGAL | LEGAL | LEGAL | LEGAL | LEGAL |

\* **Exceptions (only legal half-person on readable room):**
- `diegetic_pair` match (V5 decomposed subject+plate)
- `diegetic_cu` single plate (geometry single-sourced)
- Explicit **solid diegetic occluder**: `grounding.occluder=true` + L0 `occluder_crop_bbox_pct` + named `anchor_slot`

### 3.2 When bust/waist crops are legal vs insane

| Context | Legal? | Reader inference |
|---|---|---|
| Dialogue/reaction on defocus of same room | **YES** | "We're still in the kitchen; camera moved closer" |
| Dialogue on tone/manpu/void | **YES** | "Emotional register, not literal space" |
| Bust bottom-anchored on abstract stage slot | **YES** | "Close-up portrait; lower body out of frame by convention" |
| Waist-up behind table edge occluder | **YES** | "Character seated/standing behind counter" |
| Diegetic pair / diegetic_cu | **YES** | Single-render geometry |
| Bust center-pasted on full kitchen with floor visible | **NO — insane** | Reader asks "where are her legs?" |
| Face CU on establishing wide | **NO** | Scale/register conflict |
| Hands ECU on full room | **NO** | Use tone_gradient or diegetic macro |
| Mecha cockpit bust borrowed from iyashikei kitchen bust | **NO** | Cross-genre spatial lie |

### 3.3 Room shot readability checklist

A room panel is readable when ALL hold:

1. Horizon visible and consistent (`eye_level_y_pct` stable within scene)
2. Floor plane readable OR explicitly occluded (not ambiguous mid-air paste)
3. Figure scale matches depth (G3 ±15%)
4. Contact shadow present (G4)
5. At least one depth cue: occluder, overlap, or perspective lines
6. Lighting direction matches figure (G8)
7. For establishing: figure ≤40% frame height OR full environment dominates

---

## 4. Speech-bubble ordering rules

### 4.1 Universal

| Order | Rule |
|---|---|
| 1 | Plan balloon zones **before** final art composition (Klein, Woodman-Maynard) |
| 2 | In-panel order follows reading direction; en_US: TL→TR→BL→BR; ja_JP manga: TR→TL→BR→BL (`bubble_render._default_zone_sequence`) |
| 3 | First speaker on **left** (en_US) or **right** (ja_JP) when possible — avoids zigzag |
| 4 | Vertical stack: upper balloon read before lower in same column |
| 5 | Tail points to mouth; 50–60% termination distance (Blambot) |
| 6 | No crossed tails |
| 7 | Off-panel speech: tail butts panel border or tailless balloon |
| 8 | Thought balloons: dotted tail to head (not mouth) |
| 9 | Narrator caption: full-width top strip, below-safe for scroll entry |
| 10 | Whisper/internal: smaller font, dashed border, lower coverage |

### 4.2 Emotional register → bubble shape

| Register | Shape | Size vs panel |
|---|---|---|
| calm/normal | round | small–medium |
| excited | round/spiky | medium |
| shouting/screaming | spiky/scream | large (still ≤ coverage limit) |
| internal | cloud/italic | medium, offset from speaker |
| electronic | sharp rectangle | compact |
| horror | drip (placeholder) | irregular |

---

## 5. Page / panel eye-flow rules

### 5.1 Within a page (when multi-panel pages exist)

Based on Cohn & Campbell assemblage principles + Z-path:

1. **Grouped areas > non-grouped** — align panel edges to form readable chunks
2. **Smooth paths > broken paths** — avoid 4-way intersections (T-cut offset instead)
3. **Do not jump over units** — complete a row/column group before crossing
4. **Do not leave gaps** — ambiguous gutters break flow
5. **Z-path default** (LTR) / mirrored (RTL) — deviations need balloon trails or size emphasis
6. **Large panel = slow time**; small panel = fast time
7. **Vertical gutter narrow** = simultaneous; **horizontal gutter wide** = time pass
8. **Bleed panel** = peak emphasis (≤1 per scene, class B budget)

### 5.2 Vertical webtoon strip (primary Phoenix format)

1. Reader enters panel from **top** — place focal subject in upper-middle third
2. Scroll momentum carries eye **down** — dialogue balloons above faces when possible
3. Gutters between strip panels: beat-type-aware (`webtoon_compose` — not in bank assembler)
4. Page-turn hook (hiki-goma): bottom panel unresolved → next panel payoff
5. **Ma panels** (wide, low density) after tension blocks

### 5.3 Eye guidance hierarchy (where to look 1st, 2nd, 3rd)

| Priority | Signal |
|---|---|
| 1st | Highest contrast / largest face / motion focal point |
| 2nd | Speech balloon in reading-order position |
| 3rd | Secondary character reaction or insert detail |
| 4th | Background establishing context (already encoded if establishing ran) |

Motion lines and radial speed lines redirect to impact center (MediBang, Multic action guide).

---

## 6. Genre overlays

### 6.1 Iyashikei (healing / stillness)

| Parameter | Convention | Planner implication |
|---|---|---|
| Panel density | Low; ~3–5 tiers; generous white | Prefer `pillow_ma`, `insert_object`, `closure_breath` |
| Silence ratio | ≥50% panels without dialogue; ~1 silent : 3 dialogue | Chapter validator |
| BG class flow | establishing → defocus/tone/manpu; minimal full_render repeats | G1 + §6.2 |
| Manpu subset | flowers, bubbles, soft gradient — no speedlines | `iyashikei.yaml forbidden_grammar` |
| Bubble size | Small relative to panel; unhurried | `coverage_limit` ≤0.25 optional |
| Ma / stillness | Wide scenery, zero figures, object inserts | `pillow_ma` zero-figure invariant |
| Pacing | Decompress time; linger on cup, light, breath | Large panel slots for `miyazaki_ma_pause` |
| Crop preference | Bust/reaction on abstract; room shots full-figure or occluded seated | Asset bank: `clean_bust_abstract`, `room_seated_knees_up` |

### 6.2 Mecha

| Parameter | Convention | Planner implication |
|---|---|---|
| Establishing | Hangar/cockpit/threshold wide; scale anchors (mech height refs) | Native L0+L2 bank required — **no cross-genre bust salvage** |
| Cockpit dialogue | Medium bust acceptable **with** console occluder + seated anchor | `seated_cockpit` diegetic pair spec |
| Scale | Pilot small vs mech; G3 critical | `figure_height_m` + mech silhouette in L0 |
| BG class | `full_render` for establishing; defocus for cockpit dialogue | Same G1 matrix |
| Action density | Low in cockpit; high in battle exterior (different profile) | Separate action overlay |
| Angles | Low angle (aori) for mech dominance; eye-level for cockpit | G2 enforcement |
| Bubbles | Technical callouts rectangular; sparse in cockpit | `electronic_sharp` style |

### 6.3 Psychological thriller

| Parameter | Convention | Planner implication |
|---|---|---|
| Panel rhythm | Wide atmospheric → tight approach → held reveal → reaction | Sequence template in planner |
| Shadow | Heavy blacks, negative space, partial face | L0 `light.temporal_state`, high contrast |
| Crop | Face CU, ECU eyes, silhouette threshold | Abstract manpu minimal; tone/void OK |
| BG | Claustrophobic partial_motif; readable establishing once | `at_desk_tense` occluder poses |
| Bubbles | Short lines; internal monologue cloud; whisper | Lower coverage |
| Pacing | Delay reveal; reaction panel after beat | Scroll distance / gutter width |
| Forbidden | Comedic manpu, bright iyashikei palette on tension beat | Genre filter on manpu lookup |

### 6.4 Battle / action

| Parameter | Convention | Planner implication |
|---|---|---|
| Panel shape | Naname (oblique) cuts for motion; avoid 4-way joins | Page composer (future) |
| Size | Large panels for impact; staccato small panels for exchange | Strip gutter shrink |
| Speed lines | Sparse default; dense only on impact (L4 layer) | `speedlines_focus` bg_class |
| Screen direction | Maintain 180° rule across cuts | Chapter validator |
| Crop | Full-figure and dynamic silhouette; ECU impact frames | No bust-on-room |
| Bleed / break | Panel border break ≤1/scene for peak hit | class B budget |
| Ma beat | Required rest panel after extended action (Yu Yu Hakusho pattern) | `pillow_ma` or wide insert |

### 6.5 Workplace

| Parameter | Convention | Planner implication |
|---|---|---|
| Register | Grounded realism; medium shots dominate | `grounded_realism` style_resolution |
| Space | Office/desk occluder grammar | `anchor_slot` with desk occluder |
| BG flow | establishing office → defocus for dialogue | Standard G1 |
| Bubble | Professional, medium size; avoid scream shapes | Default round |
| Density | Moderate; clarity over spectacle | 4–6 panels/page equivalent |

### 6.6 Mystery

| Parameter | Convention | Planner implication |
|---|---|---|
| Structure | Setup → tension space → reveal panel → reaction | Panel sequence schema |
| Clues | Edge placement, partial occlusion in busy panels | L3 insert + tight crop |
| Light | Noir ratio; shadow hides, light reveals | L0 lighting metadata |
| Pace | Slow wide → accelerate tight → hold reaction | Invert iyashikei calm |
| Bubbles | Minimal on approach; single balloon on reveal | Planner dialogue budget |
| Forbidden | Premature full reveal in thumbnail panel | Script beat gating |

---

## 7. Somatic pacing rules

Somatic pacing = how the reader's body feels time passing through image rhythm.

| Rule ID | Rule | Mechanism |
|---|---|---|
| HR-S01 | **Ma (間) panel** — figure-free or near-silent wide/object panel after dialogue or tension | `pillow_ma`, `insert_object`, `closure_breath` |
| HR-S02 | **Silence ratio** — iyashikei ≥50% non-dialogue panels | Chapter validator |
| HR-S03 | **1:3 silent:dialogue** hard ratio option for healing register | Planner beat template |
| HR-S04 | **Decompression** — same action spans more panels = slower somatic time | More panels, larger crops |
| HR-S05 | **Compression** — small angular panels = adrenaline | Action overlay |
| HR-S06 | **Held reaction** — after reveal, one panel on hands/back/still face before next beat | Thriller/mystery template |
| HR-S07 | **Breath panels** — chest/breath micro (`dialogue_bust`) without dialogue text | Visual-only readability |
| HR-S08 | **Scroll distance** — webtoon empty gutter before climax increases anticipation | `webtoon_compose` gutter_px |
| HR-S09 | **Calm vs tense palette** — desaturated/defocus = calm; high contrast + speedlines = tense | L0 derivation + L4 |
| HR-S10 | **End on unresolved beat** — bottom panel hooks scroll/page turn | hiki-goma pattern |

---

## 8. Layered-compositing rules

### 8.1 Z-order (contract §4)

`L0 (0) < L1 (10) < L3-below (15) < L2 (20) < L3-above (30) < L4 (40) < BOOK occluder (25 between L2/L3)`

### 8.2 When character cutout CAN be placed on background

ALL must pass:

1. G1 legality for crop×bg (or diegetic pair auto-pass)
2. G2 angle match (if readable BG)
3. G8 light match
4. Resolved `anchor_slot` OR abstract stage slot OR diegetic pair
5. For readable BG: G3 scale + G4 shadow (+ G5 occluder if lower body hidden)
6. G6 defringe
7. Asset `provenance=REAL` for presentable output
8. No scene contamination on abstract stage

### 8.3 When character cutout CANNOT be placed

- Any HR-F01–F07 condition
- Missing sidecar on readable combo without legacy bbox fallback flagged WARN
- INTERIM asset in production manifest (presentable path)
- Cross-genre asset without genre tag match

### 8.4 Derivation rules (same plate retention)

| Derivation | Use | Produces |
|---|---|---|
| defocus | dialogue/reaction in same room | defocus_derived |
| tone_gradient | insert_object, hands, object beat | tone_gradient |
| void | realization peak | white/black_void |
| plate_crop | diegetic macro, occluder BOOK | full_render fragment |

---

## 9. Planner vs assembler vs validator rules

| Concern | Planner (`panel_planning_rules`, manifest gen, continuity) | Assembler (`assemble_from_bank`, `composition_grammar`) | Validator (CI, chapter lint, bubble QA) |
|---|---|---|---|
| Shot type selection | archetype → shot_type; genre overlay | reads manifest `shot_type` | chapter §6.2 sequence |
| crop×bg legality | **must reject illegal combos upstream** | G1 fail-closed at paste | audit CLI, continuity |
| L0 derivation choice | defocus/tone/manpu per shot | applies derivation ops | manifest lint |
| Asset selection | pick legal L2 class from bank metadata | loads assets | bank gap map |
| anchor_slot assignment | seat/table/occluder/abstract stage | `resolve_anchor_slot` | planning audit |
| Horizon scale | ensure room-capable crop + slot exist | G3 paste math | G3 gate report |
| Contact shadow | `grounding.contact_shadow: true` | G4 render | gate report |
| Occluder | `grounding.occluder: true` + bbox | G5 paste | visual check |
| Bubble placement | reserve zones in archetype bbox; speaker side | `--bubbles` pass | coverage + occlusion lint |
| Eye-flow / page layout | beat templates, gutter hints | strip stack only (minimal) | page composer |
| Genre overlays | profile + style_resolution | none (manifest-driven) | genre-specific CI profiles |
| Fail-closed | omit illegal panels → bank_gaps | raise on G1/G2/G3/G8 FAIL | BLOCK merge |

**Critical drift:** closeout docs claim planner validation in `generate_assembly_manifest` and assembler `load_manifest` — **not present in current code**. Validation exists in `panel_planning_rules.py` + `audit_assembly_manifest_planning.py` only.

---

## 10. Asset bank metadata requirements

Every L0/L2 REAL asset MUST carry `.composition.json` sidecar (`composition_meta.schema.json` + extensions):

### L0 required

- `bg_class`, `camera.angle_bucket`, `camera.eye_level_y_pct`, `camera.camera_height`
- `ground_plane.visible`
- `light.azimuth`, `light.temporal_state`
- `anchor_slots[]` with `slot_id`, `feet_y_pct`, `center_x_pct`, `expected_figure_h_pct`
- optional `occluder_crop_bbox_pct` per slot

### L2 required

- `crop_class`, `anchor.point`, `anchor.y_px`, `eye_y_px`
- `implied_camera.angle_bucket`
- `figure_height_m`, `pose_id`
- optional `diegetic_pair`

### L2 legality extensions (in use, schema drift)

- `abstract_stage_eligible: bool` — clean bust for defocus/tone stage
- `room_capable: bool` — may appear on full_render with G3
- `scene_contamination: bool` — baked prop geometry in alpha
- `pose_context: string` — seated_cockpit, hands_insert, etc.
- `attached_props_allowed: bool` — for hands/ECU insert shots

### Bank gap classes (stillness ep_001, 2026-07-09)

| Class | Count | Status |
|---|---|---|
| clean_bust_abstract | 12 | REAL |
| hands_insert | 4 | REAL |
| diegetic_pair | 1 | REAL |
| room_seated_knees_up | 0 | QUEUED |
| room_full_figure | 0 | QUEUED |
| mecha/thriller L2 | 0 | SPECCED only |

---

## 11. Repo examples that violate rules

| Example | Violation | Status |
|---|---|---|
| `artifacts/qa/invalid_proof/stillness/mira_pulid_character_strip.yaml` | HR-F01 floating bust on full_render | Quarantined |
| `artifacts/qa/invalid_proof/stillness/demo_alarm_metaphor_6p.yaml` | HR-F01, HR-F05 bbox salvage | Quarantined |
| `artifacts/qa/invalid_proof/mecha/mecha_real_layer_proof_mix_2026-07-09.yaml` | HR-F12 cross-genre bust | Quarantined |
| `composition_grammar_control.yaml` | HR-F01 intentional | Negative control — must FAIL |
| L2 assets `L2_2ecbdc633003` etc. | HR-F04 scene contamination | Metadata quarantine |
| Any manifest using bbox_legacy without sidecars | HR-F01 risk (WARN only) | Legacy path in assembler |
| `generate_assembly_manifest.py` without planning call | Illegal combos can enter manifest | **Active drift** |
| `assemble_from_bank.load_manifest` without planning call | Illegal combos reach PIL | **Active drift** |
| Bubble pass without face-occlusion check | HR-F09 | **Active gap** |

### Valid proofs (reference)

- `composition_grammar_pilot.yaml` + assembled outputs
- `ep_001_from_continuity.yaml` (when generated with defocus + clean bust selection)
- `demo_alarm_metaphor_6p_REAL_pilot.yaml`
- `assembled/halfperson_rule_proof_2026-07-09/`

---

## 12. Repo drift table

| Area | Status | Notes | Action |
|---|---|---|---|
| `composition_grammar.py` G1–G6 | **GOVERNED** | Matrix, paste ops, gates | Extend G7/G9; promote G5 to FAIL for room knees-up |
| `panel_planning_rules.py` | **GOVERNED** | Half-person, contamination, abstract stage | Single source for ARCHETYPE_SHOT_TYPE |
| `assemble_from_bank.py` grammar path | **PARTIAL** | G1–G6 when sidecars present | Wire `validate_composition_panel_planning` in `load_manifest`; kill silent bbox_legacy |
| `generate_assembly_manifest.py` | **WEAK** | Derives defocus; duplicates shot map | Import shot map from planner; call planning validator; add `_select_*` L2 helpers per closeout |
| `audit_assembly_manifest_planning.py` | **GOVERNED** | Batch lint CLI | Promote to CI required check |
| `annotate_l2_composition_legal.py` | **GOVERNED** | Bank metadata repair | Roll to all series |
| `bubble_render.py` | **WEAK** | Zones, coverage; no face check | Add occlusion validator; composition-aware zones from anchor |
| §6.2 chapter validator | **ABSENT** | Spec'd not built | New `validate_chapter_composition_grammar.py` |
| `validate_continuity_invariants.py` | **PARTIAL** | Claimed half_person check | Verify/wire `half_person_room_scale_planning` |
| `composition_meta.schema.json` | **DRIFT** | Missing legality extension fields | Add abstract_stage_eligible, room_capable, scene_contamination |
| `ARCHETYPE_SHOT_TYPE` | **DUPLICATE** | manifest gen + planner | Delete from `generate_assembly_manifest.py` |
| `render_v4/v5_episode.py` | **DRIFT** | No prompt_authority unification | Genre path fragmented |
| `queue_panel_renders.py` | **LEGACY** | No ledger | Deprecate → render_request_ledger |
| Page layout / webtoon_compose | **PARTIAL** | Not in bank assembler strip | Beat-aware gutters elsewhere |
| `style_resolution.py` | **orthogonal** | Genre→style only | Not readability enforcement |

### Delete or rewire

| Path | Verdict |
|---|---|
| `scripts/manga/queue_panel_renders.py` | Rewire to ledger or deprecate |
| `ARCHETYPE_SHOT_TYPE` in `generate_assembly_manifest.py` | Delete — import from `panel_planning_rules` |
| Invalid proof manifests outside `artifacts/qa/invalid_proof/` | Quarantine or delete |
| bbox_legacy as default compositor path | Rewire — FAIL when composition_meta absent on L0+L2 pairs |
| Post-hoc defocus without manifest derivation | Delete salvage pattern |

---

## 13. Operator memo

### What a human reader needs to understand the image instantly

1. **Where am I?** — establishing panel already gave the room; later panels may abstract but retain recognition.
2. **Who is speaking?** — balloon order + tail + speaker side.
3. **How close is the camera?** — crop class matches bg_class register (room vs portrait stage).
4. **Where is the body?** — feet line, shadow, occluder, or abstract bottom-anchor explains missing parts.
5. **How should I feel?** — panel size, silence, manpu/tone, light ratio.

### Top 10 rules

1. Establish the room before abstract close-ups.
2. Never float bust/waist on readable floor without occluder or diegetic pair.
3. Anchor figures to horizon math, not bbox center.
4. Contact shadow always on grounded paste.
5. Match camera angle bucket across L0/L2.
6. Defocus the *same* plate for dialogue, not a random card.
7. Balloons follow reading order; first speaker on correct side.
8. Tails point to mouths; don't hide faces.
9. Ma/silence panels have no figures/dialogue clutter.
10. Shot variety — alternate wide, medium, close, insert.

### Top 10 anti-patterns

1. Center-pasted torso in kitchen (floating half-person).
2. Abstract bust before establishing shot.
3. Cup/table baked into bust alpha on tone stage.
4. Angle mismatch (aori figure on eye-level room).
5. Missing shadow on seated figure.
6. Balloon covering eyes.
7. Cross-genre asset paste (stillness bust in mecha hangar).
8. Speedlines on every panel.
9. Pillow panel with character inserted.
10. bbox_legacy salvage when grammar metadata exists.

### Next implementation lane

1. Wire `validate_composition_panel_planning` into `generate_assembly_manifest.py` (skip illegal → bank_gaps) and `assemble_from_bank.load_manifest` (fail-closed).
2. Implement §6.2 chapter validator as CI gate.
3. Extend `composition_meta.schema.json` with legality fields; dedupe ARCHETYPE_SHOT_TYPE.
4. Add `bubble_composition_validator.py` (face occlusion, tail cross, reading order).
5. Dispatch queued room-scale L2 renders; annotate mecha/thriller banks.

---

## 14. Source appendix (evidence-backed)

| Source ID | Topic | URL / path | Evidence note |
|---|---|---|---|
| SRC-COHN-2013 | Panel assemblage / eye-flow | https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00186/full | Empirical reading-order strategies; smooth paths > broken paths |
| SRC-COHN-VLL | External compositional structure | https://visuallanguagelab.com/P/2017.JGNC.NCJAMDRYKP.pdf | Z-path foundation; hierarchic panel grouping |
| SRC-NATSUME | Koma time segmentation | https://www.japanesestudies.org.uk/ejcjs/vol21/iss2/holt_fukuda.html | Panel size = time compression/release; RTL entry |
| SRC-MCCLOUD | Closure across gutters | https://benargon.com/comic-panel-tools-techniques/ | Reader fills gutter; panel-to-panel continuity |
| SRC-MATTGODDEN | Manga layout grammar | http://www.mattgodden.com/2015/09/02/manga-panel-design-theory/ | Edge-to-edge gutter recursion; avoid 4-way grid |
| SRC-KLEIN-BALLOON | Balloon placement | https://kleinletters.com/BalloonPlacement.html | Left speaker first; no crossed tails; reading trail |
| SRC-KLEIN-WRITERS | Lettering flow | https://kleinletters.com/Blog/lettering-tips-for-comics-writers/ | LTR then down; natural eye flow across page |
| SRC-BLAMBOT | Balloon tails / butting | https://blambot.com/pages/comic-book-grammar-tradition | Tail 50–60% to mouth; off-panel butting |
| SRC-SHOOTER | Balloon unobtrusiveness | https://storytelling.jimshooter.com/lettering/ | No face cover; short straight pointers |
| SRC-COMICORY | Placement craft | https://www.comicory.com/blog/comic-book-lettering | Top-of-panel entry; avoid balloon-over-face |
| SRC-VN-SPRITES | Abstract stage crops | https://vnpaths.com/how-to-create-visual-novel-sprites/ | Waist/thigh bust convention on transparent stage |
| SRC-CSP-COMPOSITION | Shot type selection | https://tips.clip-studio.com/en-us/articles/8486 | Bust vs full shot communicates register + space |
| SRC-INGTHING | Defocus intimacy | https://ingthing.dev/sprites-camera-action-osas/ | Same-plate defocus retains spatial model |
| SRC-INTERNAL-COMP-GRAMMAR | Repo G1–G8 matrix | `docs/specs/MANGA_COMPOSITION_GRAMMAR_SPEC.md` | Deterministic crop×bg + paste ops |
| SRC-INTERNAL-HALFPERSON | Operator half-person rule | `artifacts/qa/MANGA_HALFPERSON_RULE_CLOSEOUT_2026-07-09.md` | Fail-closed upstream planning evidence |
| SRC-INTERNAL-WEBTOON | Lettering gap analysis | `artifacts/research/webtoon_compositing_lettering_2026-04-25.md` | Bubble zones, coverage, face-occlusion gap |

---

## Closeout tags

```
manga-human-rules=artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md
manga-human-rules-json=artifacts/qa/manga_human_readability_rules_2026-07-09.json
manga-human-rules-governed=composition_grammar,panel_planning_rules,audit_assembly_manifest_planning,annotate_l2_composition_legal,audit_asset_bank_composition,assemble_from_bank_grammar_path_partial,bubble_render_coverage_partial
manga-human-rules-drift=generate_assembly_manifest,assemble_from_bank_load_manifest,chapter_validator_6_2,bubble_face_occlusion,composition_meta_schema_extensions,ARCHETYPE_SHOT_TYPE_duplicate,bbox_legacy_warn_only,render_v4_v5_prompt_authority
manga-human-rules-delete-or-rewire=queue_panel_renders,ARCHETYPE_SHOT_TYPE_in_generate_assembly_manifest,bbox_legacy_default_path,invalid_proof_manifests_outside_quarantine,post_hoc_defocus_salvage
manga-human-rules-next-action=Wire validate_composition_panel_planning fail-closed into generate_assembly_manifest + assemble_from_bank.load_manifest; implement §6.2 chapter validator + bubble face-occlusion gate
manga-human-rules-blocker=none
```
