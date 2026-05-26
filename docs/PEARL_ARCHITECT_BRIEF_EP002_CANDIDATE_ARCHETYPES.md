# Pearl_Architect Brief — ep_002 Candidate Iyashikei Archetypes

**Status:** BRIEF for operator decision (not execution)
**Author:** Pearl_Architect, 2026-05-26
**Trigger:** ep_002 beatsheet draft (PR #1316, commit `436cea37b`) surfaced **3 candidate-new archetypes** not present in `config/manga/panel_templates/iyashikei.yaml`. Each needs a binary operator decision: **DEFINE** as new archetype, or **DOWNGRADE** to closest existing archetype.

**Audience:** the operator (decision-maker) + whichever agent spawns next (executor).

**Authority cross-refs:**
- ep_002 beatsheet: `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_002/_extracted_beatsheet.yaml`
- ep_002 chapter_script: `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_002.yaml`
- Genre panel_template: `config/manga/panel_templates/iyashikei.yaml`
- Per-archetype scene context: `config/manga/panel_templates/iyashikei.scene_context.yaml`
- Generator design notes: `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` (§3 dispatch table — read this before editing the generator)
- Craft authority: `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md`
- Generator (to be extended): `scripts/manga/continuity_state_generator.py` (see `ARCHETYPE_DISPATCH` table)
- Validator: `scripts/manga/validate_continuity_invariants.py`

**Scope of decisions in this brief:** archetype catalog ONLY. The 8 new scenes (street_sidewalk, office_lobby, office_elevator, office_waiting_area, office_meeting_room, office_corridor, office_stairwell, office_rooftop), the multi-character generator extension, and the ~12 new pose_ids are sibling open-items tracked separately in the beatsheet WRITER NOTES block. This brief only resolves whether each of three new archetypes is supported in the iyashikei catalog.

---

## §0 The 3 candidates at a glance

| Candidate | ep_002 beats | What it visually is | Closest existing | Recommended |
|---|---|---|---|---|
| `elevator_interior_micro_tension` | b11 (×1) | Enclosed vertical-motion interior; protagonist standing facing camera; faceless extra in frame | `character_face_micro_tension` | **DOWNGRADE → `character_face_micro_tension`** with scene-specific composition clause |
| `secondary_character_face_close` | b17, b22 (×2) | CU of Dr. Morimoto across the meeting table; calm professional | `character_quiet_face` (with subject_actor binding) | **DEFINE** — secondary-character CU is a real composition register and ep_002+ will repeat it |
| `typographic_caption_card` | b24 (×1) | Near-black panel, thin light frame, caption strip only; no scene, no character | (none — `sparse_establishing_wide` is the current placeholder per design notes OPEN-5) | **DEFINE** — meta archetype, tiny implementation cost, structural correctness |

**Total work if all 3 DEFINED:** ~3 days agent + 0.5 day operator review (see §3).

---

## §1 Candidate: `elevator_interior_micro_tension`

### Usage in ep_002

**Beat b11** — Mira enters the office elevator. The chapter_script reads: "Tight interior — elevator. Mira and one other person (back to camera, faceless extra). The numbers ticking up. Mira's jaw tightens fractionally." V3.1 panel ep002_011 confirms: medium standing shot, enclosed verticals, faceless extra rendered as back-of-head silhouette upper-right. The composition register is **enclosed-with-stranger** — a tight space + faceless social presence triggering an activation register.

Dial movement: 0.4 → 0.5 (+0.1, within micro bound). The activation is small. The space does the work, not the face.

### The decision tree

**Option A — DEFINE as new archetype `elevator_interior_micro_tension`.** Required work:
1. Add an archetype block to `iyashikei.yaml` (somatic cluster — it's an activation register tied to spatial enclosure).
2. Add a `scene_context_clause` to `iyashikei.scene_context.yaml` that names the elevator interior directly.
3. Add an `ARCHETYPE_DISPATCH` entry in `scripts/manga/continuity_state_generator.py`.
4. Add a row to design notes §3 dispatch table.
5. Add tests for happy path (single elevator beat) + edge case (back-to-back elevator beats — forbidden? probably yes).
- **Time estimate:** 1 day Pearl_Author.
- **Reusability beyond ep_002:** thin. Elevators recur in modern slice-of-life but no other stillness_press ep currently scripts one. Cross-genre rollout (Milestone D) is unlikely to need this specific archetype; "tight space with stranger" is a broader composition register that `character_face_micro_tension` + per-scene composition clause can cover.

**Option B — DOWNGRADE to `character_face_micro_tension`.** Substitution mechanics:
- Closest fit: `character_face_micro_tension` (somatic cluster, MCU/CU framing, subject_type `character_face_only`, EMITS `v41_per_axis_edge_resolved` boilerplate, dial-activation register).
- What's lost: the elevator-specific framing (vertical numbers ticker, enclosed walls, faceless extra). These are scene-context details the `office_elevator` scene_inventory entry can carry on its own `scene_specific_composition_clause` (per V4 spec). The archetype-level composition_tokens stay generic ("subtle tension in brow or jaw, soft window light, the smallest signal of activation"), but the scene clause adds "enclosed elevator interior, polished metal walls visible, faceless extra figure back-to-camera upper-right." Visual proof: V3.1 ep002_011 already reads as a medium-tension portrait with elevator context behind — the existing archetype's composition tokens accommodate this with zero loss.
- One subtle compromise: `character_face_micro_tension` is CU framing per `iyashikei.yaml` row (`framing: CU`, subject_placement_bbox [22, 12, 78, 88]). The ep_002 beatsheet pose for b11 is `medium_standing_facing_camera` (MS, not CU). The downgrade requires either (a) accepting CU re-framing of the elevator panel — V3.1 shows MS, so this would be a re-render — or (b) authoring a parallel `character_medium_micro_tension` archetype (which is a less generic broader fix than the elevator-specific candidate).

**Recommended default: B — DOWNGRADE.**

Rationale: the activation signal at b11 IS face-and-body tension. The elevator is a scene_context attribute, not an archetype-level composition register. We already have a tier 2 mechanism for scene-specific composition (the `scene_specific_composition_clause` on scene_inventory entries) that exists exactly for this case. Adding a one-off archetype for a single beat in a single episode burns implementation effort and dispatch-table cognitive load for no cross-episode reuse. The MS-vs-CU framing mismatch is real but more cheaply fixed by accepting CU re-framing OR by promoting `character_face_micro_tension` to allow CU-or-MS framing per beat — which is a single-line schema change.

If a future episode brings back the elevator with a real composition twist (e.g., a doors-opening reveal that needs the framing to do narrative work the face can't), redefine then. Don't speculate.

### If Option A (define) — implementation checklist

1. **Add to `iyashikei.yaml`** (append under CLUSTER 2: SOMATIC):

```yaml
  elevator_interior_micro_tension:
    cluster: somatic
    framing: MS                       # medium standing shot (not CU)
    beat_role: gesture                # activation-onset gesture
    beat_type:
      primary: micro
      secondary: standard             # if scene-transitioning into elevator
    aspect_hint: portrait_4_5
    subject_placement_bbox: [25, 8, 75, 95]   # standing figure dominates vertical
    eye_flow_anchor: chest_and_face
    eye_flow_anchor_detail: "jaw tension + enclosed verticals behind"
    composition_tokens:
      - "medium standing shot inside an elevator interior"
      - "enclosed vertical walls of polished metal"
      - "elevator-floor indicator numbers visible upper frame"
      - "faceless second figure back-to-camera in frame corner"
      - "subject facing camera with subtle jaw tension"
      - "soft enclosed lighting (no window source)"
      - "cream and cool-neutral palette"
      - "no exaggerated reactions; the space registers the tension"
    typical_pairing:
      preceded_by: [sparse_establishing_wide, walking_in_thought_medium]
      followed_by: [hand_table_micro, chest_breath_micro]
    bestseller_exemplars:
      - "March Comes in Like a Lion — Rei in Tokyo subway/transit beats"
      - "Komi Can't Communicate — closed-space tension beats"
    engine_routing: qwen_image_pulid
    engine_routing_rationale: "FACE close enough to MS that identity matters; enclosed interior + face = qwen + PuLID"
```

2. **Add to `iyashikei.scene_context.yaml`**:

```yaml
  elevator_interior_micro_tension:
    subject_type: character_full_figure   # standing figure, not face-only — full body in frame
    scene_context_clause: "enclosed elevator interior — polished-metal vertical walls on both sides, floor indicator numbers panel visible in upper-frame edge, faceless second figure back-to-camera in one corner, soft cool enclosed lighting"
    attached_props_clause: "no held props; the elevator interior itself is the second visual register"
    cutout_policy:
      cutout_engine: toonout
      model: u2net_human_seg
      keep_attached_props: []
      alpha_matting: true
      alpha_matting_foreground_threshold: 240
      alpha_matting_background_threshold: 10
      character_extraction_coverage_min_pct: 0.55
      background_bleed_max_pct: 10        # elevator interior wraps subject; verticals legitimately at edges
```

3. **Add dispatch in `scripts/manga/continuity_state_generator.py`** (`ARCHETYPE_DISPATCH` table):

```python
def _dispatch_elevator_interior_micro_tension(beat, prev_panel, scene_context):
    return {
        "default_pose_id": "medium_standing_facing_camera",
        "default_hand_state": "relaxed_open",
        "required_fields": [],          # no extra archetype-specific fields
        "emits_v41_edge_resolved": False,   # MS not CU, doesn't trigger v41 boilerplate
        "subject_type": "character_full_figure",
        "on_frame_default": True,
    }
```

4. **Update `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` §3** — add row:

| Archetype | Count (ep_002) | Default `pose_id` | Default `hand_state` | Special fields | `subject_type` |
|---|---|---|---|---|---|
| `elevator_interior_micro_tension` | 1 | `medium_standing_facing_camera` | `relaxed_open` | none | `character_full_figure` |

5. **Tests in `scripts/manga/tests/test_continuity_state_generator.py`** — happy path: single elevator beat with on_frame=true generates pose_id from default. Edge: archetype + chest_breath beat back-to-back (allowed transition? document expected).

6. **Time estimate:** 1 day Pearl_Author + 0.5 day operator review.

### If Option B (downgrade) — substitution map

- **Substitute archetype:** `character_face_micro_tension`.
- **Beatsheet amendment required:** in `_extracted_beatsheet.yaml`, change `b11.archetype: elevator_interior_micro_tension` → `b11.archetype: character_face_micro_tension`.
- **Visible compromise:** loses MS framing on the render (gets CU). The elevator interior gets carried by the `office_elevator` scene_inventory entry's `scene_specific_composition_clause` (which the operator must author anyway to backfill OPEN-A — see beatsheet WRITER NOTES). On the rendered output, V3.1 panel ep002_011's elevator context is preserved at scene-clause level; the framing tightens from MS to CU.
- **V3.1 visual proof of plausibility:** V3.1 panel ep002_011 is already MCU-ish — there's no full body, the lower half is cut off by the panel frame. CU re-render would tighten further. Composition register (enclosed verticals, faceless extra) is preserved by scene context.

### Risk if neither is done

Generator raises `ArchetypeNotImplementedError` on b11 at forward-gen time. Forward-gen of ep_002 to 32 continuity_state YAMLs blocks at panel 11. Renders 1-10 work; 11 onward fail (because the generator processes beats sequentially and bails on first unknown archetype). Validator never sees a generated panel YAML for 11+ to gate on.

---

## §2 Candidate: `secondary_character_face_close`

### Usage in ep_002

**Beats b17 and b22** — both close-ups on Dr. Morimoto across the meeting table. Chapter_script b17: "Close on Dr. Morimoto. Speaking. Calm, professional. Not warm, not cold." Chapter_script b22: "Dr. Morimoto across the table. Not impatient. Just waiting. Soft beige jacket, glasses catching the window light." Both panels are POV-from-Mira shots — Mira is off-frame, Dr. Morimoto is the on-frame subject. V3.1 panels ep002_017 and ep002_022 both confirm CU framing on Dr. Morimoto.

**Conflict to resolve:** the chapter_script's `main_characters[1]` writer-note says Dr. Morimoto "speaks 3 lines total, never close-up." But the actual panel descriptions for b17 and b22 ARE close-ups, and V3.1 rendered them as close-ups. The beatsheet reconciles by trusting the panel descriptions over the high-level writer-note. Operator should confirm: writer-note was aspirational shorthand for "Dr. Morimoto is not a focal character," not a literal rule.

Dial movement: Dr. Morimoto's expression_dial is held at 0.2 (calm professional baseline) on both beats. Mira's dial doesn't apply (she's off-frame).

### The decision tree

**Option A — DEFINE as new archetype `secondary_character_face_close`.** Required work:
1. Add archetype block to `iyashikei.yaml` (somatic cluster).
2. Add scene_context_clause to `iyashikei.scene_context.yaml`.
3. Add dispatch entry — **this is the cross-cutting one** (see §4): the dispatch needs to bind the subject to a *secondary* character (Dr. Morimoto), not the protagonist. This requires the generator's multi-character semantics to be at least partially defined first.
4. Update design notes §3.
5. Tests (happy path + multi-character interaction).
- **Time estimate:** 1.5 days Pearl_Author (extra 0.5 day for multi-character subject_actor wiring).
- **Reusability beyond ep_002:** **high.** Every multi-character episode after ep_002 (ep_003 mother, ep_004+ Kenji, any antagonist scenes) will need a "secondary-character close-up" register. This is the foundational multi-character somatic archetype.

**Option B — DOWNGRADE to `character_quiet_face`.** Substitution mechanics:
- Closest fit: `character_quiet_face` (somatic cluster, CU framing, subject_type `character_face_only`, breath beat_role, micro beat_type, EMITS `v41_per_axis_edge_resolved`).
- What's lost: identity-binding. `character_quiet_face` was authored as the protagonist's somatic-grounding archetype — its composition_tokens reference "an early-30s East-Asian-coded woman with a soft round face, long brown hair side-parted, double-eyelid almond eyes, cream knit sweater, small jade pendant on leather cord." These tokens visually describe Mira specifically. Using this archetype for Dr. Morimoto means either (a) overriding 6+ composition_tokens per beat (heavy operator burden), or (b) the renderer ignores the tokens (Qwen would visualize the prompt-described Mira, not Morimoto). PuLID face-conditioning would still target Morimoto IF the dispatch knew to lock to Morimoto's reference sheet, but the archetype-default composition tokens fight the PuLID signal.
- Critical compromise: `character_quiet_face` routes to `qwen_image_pulid` and the PuLID reference is currently the protagonist's reference sheet. Downgrading requires per-beat reference-sheet override — a generator extension that's structurally equivalent to multi-character semantics anyway.
- V3.1 visual proof of plausibility: V3.1 ep002_017 and ep002_022 DO render Dr. Morimoto as a CU — but only because V3.1 was a hand-authored prompt run, not a forward-gen run. The downgrade-via-override path WOULD be implementable, but is materially the same effort as defining the new archetype, with worse downstream code clarity.

**Recommended default: A — DEFINE.**

Rationale: this is the foundational multi-character somatic archetype. Every multi-character episode from ep_003 onward will use a variant of "secondary character CU across the table / room / threshold." Defining it now (a) creates the clean dispatch pattern multi-character semantics need to plug into, (b) gives Dr. Morimoto + Mother + Kenji a shared register that can be parametrized by `subject_actor: <character_id>`, (c) avoids the technical-debt of "use protagonist archetype with overrides" pattern that will break composition_tokens. The 0.5 extra day of work pays off across 7+ episodes.

The dispatch can be parametrized: `secondary_character_face_close` takes a `subject_actor` field (the character_id whose face is shown) rather than hardcoding to Dr. Morimoto. Single archetype, many secondaries.

**Caveat:** this DEFINE is gated on the multi-character generator extension (per beatsheet WRITER NOTES OPEN-7 / OPEN-7-A). If the operator hasn't yet committed to the multi-character extension, defer this DEFINE to coincide with that workstream. Either:
- (i) DEFINE the archetype + ship multi-character extension as a single Pearl_Author / Pearl_Architect joint workstream (Milestone B step 2), OR
- (ii) DOWNGRADE for ep_002-only and DEFINE in Milestone B step 2 when multi-character extension lands.

The brief recommends (i): the archetype IS the multi-character extension's load-bearing first user. Don't ship the extension without its first concrete archetype.

### If Option A (define) — implementation checklist

1. **Add to `iyashikei.yaml`** (append under CLUSTER 2: SOMATIC):

```yaml
  secondary_character_face_close:
    cluster: somatic
    framing: CU                       # close-up of secondary
    beat_role: gesture                # what the secondary contributes — pacing/recognition
    beat_type:
      primary: micro
    aspect_hint: square_1_1
    subject_placement_bbox: [22, 12, 78, 88]
    eye_flow_anchor: eyes
    eye_flow_anchor_detail: "secondary character's eyes — addressed-to-protagonist gaze"
    composition_tokens:
      - "close-up of the secondary character"
      - "subject identity is parametrized via subject_actor field"
      - "neutral-soft professional expression by default"
      - "soft window light"
      - "no exaggerated reactions"
      - "POV-from-protagonist composition — protagonist implied off-frame"
      - "cream and warm-neutral palette appropriate to the scene"
    parametrized_fields:
      - field: subject_actor
        type: character_id
        required: true
        semantics: "the character_id (from stage_characters) whose face fills the frame; PuLID reference sheet binds to this character's character_design.reference_sheet"
    typical_pairing:
      preceded_by: [sparse_establishing_wide, character_face_micro_tension]
      followed_by: [character_quiet_face, character_face_micro_tension]
    bestseller_exemplars:
      - "March Comes in Like a Lion — Hina-Akari close-ups on Rei"
      - "Komi Can't Communicate — Tadano/Najimi reaction beats across Komi"
      - "Sweetness & Lightning — Inuzuka-on-Tsumugi close-ups"
    engine_routing: qwen_image_pulid
    engine_routing_rationale: "FACE close-up; identity-critical; PuLID locks to subject_actor's reference sheet (not protagonist's)"
    forbidden_pairing:
      - "must not appear back-to-back with same subject_actor more than 2x (avoid talking-head montage anti-pattern)"
```

2. **Add to `iyashikei.scene_context.yaml`**:

```yaml
  secondary_character_face_close:
    subject_type: character_face_only         # face-only L2 cutout
    scene_context_clause: "POV-from-protagonist framing — secondary character's face occupies the frame with breathing room on all sides; soft warm-neutral wall texture or scene-appropriate background behind; window-light suggestion; subject does not touch frame edges"
    attached_props_clause: "secondary character's face is the panel; small wardrobe accents (collar, glasses, eyewear) per the character_design reference sheet"
    cutout_policy:
      cutout_engine: toonout
      model: u2net_human_seg
      keep_attached_props: []
      alpha_matting: true
      alpha_matting_foreground_threshold: 240
      alpha_matting_background_threshold: 10
      character_extraction_coverage_min_pct: 0.50
      background_bleed_max_pct: 5
      bleed_tolerance_rationale: "matches character_quiet_face — same framing register, different subject identity"
      pulid_reference_binding: "per-beat: PuLID reference_sheet_path resolves from subject_actor character_id, not from stage_characters[0]"
```

3. **Add dispatch in `scripts/manga/continuity_state_generator.py`** — the multi-character-aware variant:

```python
def _dispatch_secondary_character_face_close(beat, prev_panel, scene_context):
    # Validate parametrized field
    subject_actor = beat.get("subject_actor")
    if not subject_actor:
        raise BeatsheetError("secondary_character_face_close requires subject_actor field")
    if subject_actor not in beat.get("stage_characters", []):
        raise BeatsheetError(f"subject_actor={subject_actor} not in stage_characters")
    return {
        "default_pose_id": "face_close_seated_calm",
        "default_hand_state": "relaxed_open",
        "required_fields": ["subject_actor"],
        "emits_v41_edge_resolved": True,
        "subject_type": "character_face_only",
        "on_frame_default_for_subject_actor": True,
        "on_frame_default_for_protagonist": False,    # POV-from-protagonist
        "pulid_reference_binding_from": "subject_actor",
    }
```

4. **Update `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` §3** — add row (and add a §3.1 note that this is the first parametrized archetype):

| Archetype | Count (ep_002) | Default `pose_id` | Default `hand_state` | Special fields | `subject_type` |
|---|---|---|---|---|---|
| `secondary_character_face_close` | 2 | `face_close_seated_calm` | `relaxed_open` | **REQUIRES `subject_actor` (character_id)** + EMITS `v41_per_axis_edge_resolved` boilerplate | `character_face_only` (subject = subject_actor, not protagonist) |

5. **Tests in `scripts/manga/tests/test_continuity_state_generator.py`** — three cases:
   - happy: beat with subject_actor=dr_morimoto generates panel with Dr. Morimoto on_frame=true, Mira on_frame=false.
   - missing subject_actor: raises BeatsheetError.
   - subject_actor not in stage_characters: raises BeatsheetError.
   - back-to-back same subject_actor 3x: WARN (per forbidden_pairing).

6. **Time estimate:** 1.5 days Pearl_Author + 0.5 day operator review.

### If Option B (downgrade) — substitution map

- **Substitute archetype:** `character_quiet_face` with per-beat composition_tokens override + per-beat PuLID reference override.
- **Beatsheet amendment required:** in `_extracted_beatsheet.yaml`, change `b17.archetype` and `b22.archetype` → `character_quiet_face`. Add `b17.subject_actor: dr_morimoto` and `b22.subject_actor: dr_morimoto` as override fields that the generator + downstream prompt builder will need to interpret.
- **Visible compromise:** composition_tokens for `character_quiet_face` describe Mira (jade pendant, cream sweater, long brown hair). Without explicit per-beat token overrides, Qwen would render Mira's wardrobe on Dr. Morimoto's face. Operator must either override 6+ tokens per beat OR accept visual rendering bleed.
- **V3.1 visual proof:** V3.1 ep002_017 and ep002_022 DO render Dr. Morimoto, but only because they were hand-authored prompt runs. The downgrade path requires either operator burden per-beat (token overrides) OR a generator extension that's already 80% of the DEFINE work.

### Risk if neither is done

Generator raises `ArchetypeNotImplementedError` on b17 and b22. Plus, the multi-character semantics that this archetype is the first user of remain undefined — meaning every multi-character beat in ep_002 (b16-b22, b25) is also at risk. This archetype is the canary; resolve it and the multi-character workstream gets a concrete first user to design against.

---

## §3 Candidate: `typographic_caption_card`

### Usage in ep_002

**Beat b24** — chapter_script reads: "Black panel — ALMOST black, very thin frame of light at the edges. Caption strip across the middle." `narrator_caption_by_locale.en_US: "It's not danger. It's just steam."` V3.1 panel ep002_024 confirms: a near-black field with thin light edge-frame, caption strip "It's not danger. It's just steam." No character, no scene, no L2 cutout, no L0 environment. The panel is **typographic-meta** — the page itself is the medium.

This is structurally identical to the pattern flagged in design notes OPEN-5: ep_001's b35 (episode card / outro) used `sparse_establishing_wide` as a placeholder for typographic-only content, with the recommendation: "add a `meta` cluster archetype `typographic_episode_card` with subject_type: null, cutout_policy: null, that explicitly skips rendering and emits the outro lettering only."

b24 is the same kind of beat in mid-episode form. The two should be unified under a single `typographic_caption_card` archetype that takes a caption-style parameter (mid-episode caption-strip vs end-episode card).

### The decision tree

**Option A — DEFINE as new archetype `typographic_caption_card` (META cluster).** Required work:
1. Add archetype block to `iyashikei.yaml` (new **meta** cluster — joins `pendulation_pair_visual_rhyme` as the second meta archetype).
2. Add a stub scene_context entry (subject_type: null, cutout_policy: null) — most of the entry is "no L0, no L2, lettering pipeline handles render."
3. Add dispatch — trivial: emits `character_state: null/empty`, `prop_state: {}`, no light_rig (or `K_neutral_dark`).
4. Update design notes §3.
5. Tests (caption-card panel generates correct empty-shape YAML).
6. **Bonus refactor:** retroactively rename `iyashikei.yaml`'s OPEN-5 recommendation from `typographic_episode_card` to `typographic_caption_card` and parametrize via a `caption_style` field (`mid_episode_strip` vs `end_episode_card`). Update ep_001 b35 to use the unified archetype.
- **Time estimate:** 0.5 day Pearl_Author (smallest of the three).
- **Reusability beyond ep_002:** **high.** Every iyashikei episode has at least one typographic caption beat (mid-episode or end-card). Stillness Press anxiety series uses these as therapeutic "frame the recognition" beats — they're a load-bearing iyashikei device. ep_003+ will need this.

**Option B — DOWNGRADE to `sparse_establishing_wide` (the current ep_001 b35 placeholder pattern).** Substitution mechanics:
- Closest fit: `sparse_establishing_wide` (environmental cluster, ELS framing, subject_type null, cutout_policy null). Used as placeholder in ep_001 b35.
- What's lost: structural correctness. `sparse_establishing_wide` IS a renderable archetype with composition_tokens like "wide establishing shot of an environment, soft directional light from upper-window, atmospheric stillness." Downstream prompt builder will (a) try to render an environment, (b) the downstream lettering pipeline will overlay the caption on top of an environmental render. The rendered output won't match the chapter_script's "ALMOST black, very thin frame of light at the edges" intent — instead it'll be a soft kitchen / lobby establishing shot with a caption pasted over it.
- Workaround: the operator can author a `scene_specific_composition_clause` for a hypothetical `caption_card_void` scene that says "near-black field, thin edge-light only." But this conflates archetype semantics (does the panel render anything?) with scene semantics (what does the panel render?), and the prompt builder's pipeline assumes archetype determines render-or-not. The hack works but breaks the abstraction.
- V3.1 visual proof: V3.1 ep002_024 was rendered as a true near-black caption card. Forward-gen via downgrade would NOT reproduce this — it would produce a soft establishing shot. The downgrade visibly breaks for this beat.

**Recommended default: A — DEFINE.**

Rationale: smallest implementation cost of the three (0.5 day), highest abstraction-payoff, fixes the ep_001 b35 OPEN-5 placeholder, and prevents a known visual-failure mode (forward-gen producing soft-establishing where the script asks for near-black caption-only). The META cluster is the right home — `pendulation_pair_visual_rhyme` already lives there as the precedent for "archetype that doesn't render L0/L2." This is the cleanest decision in the brief.

### If Option A (define) — implementation checklist

1. **Add to `iyashikei.yaml`** (append at end, in or extending the META cluster):

```yaml
  typographic_caption_card:
    cluster: meta
    framing: META                     # not directly renderable as image
    beat_role: closure                # or attunement when mid-episode strip
    beat_type:
      primary: micro
      secondary: standard             # if used as end-episode card with scene transition
    aspect_hint: any                  # caption-card aspect dictated by composer, not archetype
    subject_placement_bbox: meta_n_a
    eye_flow_anchor: caption_center
    composition_tokens:
      - "near-black field with thin frame of light at the edges"
      - "caption strip across the center"
      - "no character, no scene, no environment"
      - "typographic register only"
      - "the page itself is the medium"
    parametrized_fields:
      - field: caption_style
        type: enum
        values: [mid_episode_strip, end_episode_card]
        required: true
        default: mid_episode_strip
      - field: caption_text_source
        type: enum
        values: [narrator_caption_by_locale, episode_card_text]
        required: true
        default: narrator_caption_by_locale
    typical_pairing:
      preceded_by: [character_quiet_face, character_face_micro_tension]
      followed_by: [character_quiet_face]
      uniqueness: "limit 1-2 mid_episode_strip per episode; end_episode_card is once-per-episode at episode close"
    bestseller_exemplars:
      - "March Comes in Like a Lion — chapter-break caption pages"
      - "Mushishi — interstitial narrator-only pages between scenes"
    engine_routing: meta_n_a
    engine_routing_rationale: "no L0/L2 render; downstream lettering pipeline composes the caption-card layout directly"
```

2. **Add to `iyashikei.scene_context.yaml`** — stub entry making explicit that there's no render:

```yaml
  typographic_caption_card:
    # META archetype — no L0 / no L2 / no L3. Downstream lettering pipeline
    # composes a typographic caption-card layout directly. Generator emits
    # an empty-shape continuity_state YAML (no character_state, no prop_state,
    # no scene_state.light_rig_id) and the caption text from the chapter_script
    # narrator_caption_by_locale slot.
    subject_type: null
    scene_context_clause: null
    attached_props_clause: null
    cutout_policy: null
    render_directive: "typographic_only — render via lettering pipeline, not via L0/L1/L2/L3 stack"
```

3. **Add dispatch in `scripts/manga/continuity_state_generator.py`**:

```python
def _dispatch_typographic_caption_card(beat, prev_panel, scene_context):
    caption_style = beat.get("caption_style", "mid_episode_strip")
    if caption_style not in ("mid_episode_strip", "end_episode_card"):
        raise BeatsheetError(f"typographic_caption_card.caption_style={caption_style} not in [mid_episode_strip, end_episode_card]")
    return {
        "default_pose_id": None,
        "default_hand_state": None,
        "required_fields": ["caption_style"],
        "emits_v41_edge_resolved": False,
        "subject_type": None,
        "on_frame_default": False,
        "skip_character_state_emission": True,
        "skip_prop_state_emission": False,    # preserve prop_state inheritance for continuity
        "skip_scene_state_light_rig": True,
        "render_directive": "typographic_only",
    }
```

4. **Update `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` §3**:

| Archetype | Count (ep_002) | Default `pose_id` | Default `hand_state` | Special fields | `subject_type` |
|---|---|---|---|---|---|
| `typographic_caption_card` | 1 | (n/a — meta) | (n/a) | **REQUIRES `caption_style` ∈ {mid_episode_strip, end_episode_card}** + skips L0/L2 render | `null` |

And mark OPEN-5 in §6 as **RESOLVED** by this archetype. Retroactively update ep_001 b35 in `_extracted_beatsheet.yaml` to use `typographic_caption_card` with `caption_style: end_episode_card`.

5. **Tests** — two cases:
   - happy: beat with `caption_style: mid_episode_strip` generates a panel YAML with empty character_state, preserved prop_state, no light_rig_id, render_directive: typographic_only.
   - invalid caption_style: raises BeatsheetError.

6. **Time estimate:** 0.5 day Pearl_Author (including the OPEN-5 retroactive cleanup).

### If Option B (downgrade) — substitution map

- **Substitute archetype:** `sparse_establishing_wide` (per ep_001 b35 precedent).
- **Beatsheet amendment required:** in `_extracted_beatsheet.yaml`, change `b24.archetype: typographic_caption_card` → `b24.archetype: sparse_establishing_wide`. Author or override a `scene_specific_composition_clause` somewhere (no good home for it — the scene is the meeting_room but the panel isn't IN the meeting_room visually).
- **Visible compromise:** ep002_024 will forward-gen as a soft kitchen/meeting-room establishing shot with caption overlaid — directly contradicting the chapter_script's "ALMOST black" directive. The visual breakage is real and not cosmetic.
- **V3.1 visual proof:** V3.1 ep002_024 IS a near-black panel. Forward-gen via downgrade would NOT match V3.1. Round-trip test (if it were run) would fail at b24.

### Risk if neither is done

Generator raises `ArchetypeNotImplementedError` on b24. Plus, ep_001 b35 retroactive cleanup stays open (the OPEN-5 placeholder remains structurally broken). Every future episode with a mid-episode caption strip or end-card is also blocked.

---

## §4 Cross-cutting concerns

### 4.1 Multi-character semantics — `secondary_character_face_close` is the canary

`secondary_character_face_close` is the **load-bearing first user** of the multi-character generator extension flagged in beatsheet WRITER NOTES OPEN-7 / OPEN-7-A. If the operator chooses A (DEFINE) for this candidate, the multi-character extension is on the critical path. If the operator chooses B (DOWNGRADE), the multi-character extension can defer — but ep_002 forward-gen will still need it for the other 7 multi-character beats (b16, b18, b19, b20, b21, b25 — every beat that stages Dr. Morimoto alongside Mira even when only one is on_frame).

**Practical implication:** the multi-character extension is needed for ep_002 forward-gen *regardless* of this candidate's decision. The only thing the decision controls is whether `secondary_character_face_close` is the extension's first concrete archetype, OR whether `character_quiet_face` (with subject_actor override) is the extension's first concrete archetype. The former is cleaner. The latter is more constraining (forces composition_tokens override to be a first-class mechanism, which is a worse abstraction).

**Recommended sequencing:** treat `secondary_character_face_close` DEFINE + multi-character extension as a single workstream (Milestone B step 2). Do not ship one without the other.

### 4.2 New pose_ids

`elevator_interior_micro_tension` introduces `medium_standing_facing_camera`. `secondary_character_face_close` introduces `face_close_seated_calm`. Both are flagged as CANDIDATE pose_ids in the beatsheet WRITER NOTES NEW POSE_IDS section. Neither archetype's DEFINE work touches the pose library; the pose library extension is sibling work to this brief.

If the operator DOWNGRADES both candidates 1 and 2, the new pose_ids still need to be added to the pose library — they're tied to the beats, not the archetypes. So this concern is orthogonal to this brief's decisions.

`typographic_caption_card` introduces **no** new pose_ids (it's the META archetype with subject_type null). Good.

### 4.3 Scene inventory entries

Sibling work, not in scope for this brief. The 8 new office scenes need scene_inventory backfill regardless of the archetype decisions (beatsheet OPEN-A through OPEN-H). The archetype DEFINE work does NOT touch scene_inventory.

### 4.4 Conflicts between candidates

**No direct conflicts.** Candidate 1 (`elevator_interior_micro_tension`) and Candidate 2 (`secondary_character_face_close`) both belong to the somatic cluster but address different beats with different subjects — they compose. Candidate 3 (`typographic_caption_card`) is the meta cluster and is structurally orthogonal.

**One indirect dependency:** if both Candidate 1 and Candidate 2 are DEFINED, the dispatch table grows by 2 entries and §3 of design notes grows by 2 rows. If both are DOWNGRADED, the dispatch table doesn't grow but the existing `character_face_micro_tension` and `character_quiet_face` archetypes get used in ways they weren't authored for (MS framing in case 1; non-protagonist subject in case 2). The downgrades push semantic strain into the existing archetypes; the defines push implementation cost into the catalog. Pick your poison.

### 4.5 Multi-character semantics summary

The single highest-leverage decision in this brief is whether `secondary_character_face_close` is DEFINED. That decision drags multi-character extension scoping with it. Make this decision deliberately.

---

## §5 Operator decision template

Fill in below and paste back to the parent agent:

```markdown
ep_002 CANDIDATE ARCHETYPE DECISIONS (per docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md)

- [ ] elevator_interior_micro_tension: ___ DEFINE / DOWNGRADE
  - If DOWNGRADE: substitute → character_face_micro_tension (recommended)
  - If DEFINE: confirm 1-day Pearl_Author allocation

- [ ] secondary_character_face_close: ___ DEFINE / DOWNGRADE
  - If DOWNGRADE: substitute → character_quiet_face + per-beat subject_actor override
  - If DEFINE: confirm 1.5-day Pearl_Author allocation + multi-character extension joint workstream

- [ ] typographic_caption_card: ___ DEFINE / DOWNGRADE
  - If DOWNGRADE: substitute → sparse_establishing_wide (per ep_001 b35 precedent — known visually broken)
  - If DEFINE: confirm 0.5-day Pearl_Author allocation + ep_001 b35 retroactive cleanup

OPEN-7 / multi-character extension:
- [ ] Approve concurrent multi-character generator extension workstream (Milestone B step 2): yes / no
```

---

## §6 Spawn template — for the parent agent

When the operator returns decisions, the parent agent acts as follows.

### For each DEFINE branch — spawn Pearl_Author with this brief

> You are Pearl_Author working Milestone B step 2 of the manga V5.1 catalog rollout. Define the new iyashikei archetype `<archetype_name>` per the implementation checklist in `docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md` §<N>. Edit (a) `config/manga/panel_templates/iyashikei.yaml` to add the archetype block, (b) `config/manga/panel_templates/iyashikei.scene_context.yaml` to add the scene_context entry, (c) `scripts/manga/continuity_state_generator.py` to add the dispatch function and register it in `ARCHETYPE_DISPATCH`, (d) `docs/PEARL_AUTHOR_BEATSHEET_DESIGN_NOTES.md` §3 to add the dispatch table row, and (e) `scripts/manga/tests/test_continuity_state_generator.py` to add the happy-path + edge-case tests listed in the brief. Run the round-trip test on ep_001 to confirm no regression. Commit with message `manga V5.1 Milestone B step 2 — define <archetype_name> archetype`. Do not modify the ep_002 beatsheet.

### For each DOWNGRADE branch — single Edit on beatsheet

The parent agent makes a single Edit to `artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/continuity_state/ep_002/_extracted_beatsheet.yaml` per the substitution map in the relevant §. Add a comment line citing `docs/PEARL_ARCHITECT_BRIEF_EP002_CANDIDATE_ARCHETYPES.md` and the operator decision date. No agent spawn needed.

### For `secondary_character_face_close` DEFINE — joint workstream

If the operator approves the multi-character extension concurrent workstream, the parent agent spawns Pearl_Architect + Pearl_Author as a coordinated pair: Pearl_Architect drafts the multi-character extension spec patch to `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md` (relational_field.implied_partner_position semantics, per-character character_state shape, active_entities list ordering convention) while Pearl_Author implements the archetype + dispatch. They merge as a single PR.

---

## §7 Summary

Three candidate archetypes surfaced by ep_002 beatsheet:

1. **`elevator_interior_micro_tension`** — recommend **DOWNGRADE** to `character_face_micro_tension`. Low reuse value, scene-context can carry the elevator semantics. Skip the dispatch-table bloat.
2. **`secondary_character_face_close`** — recommend **DEFINE**, paired with multi-character extension as joint workstream. High reuse value across all multi-character episodes. The cleanest first user of the multi-character extension.
3. **`typographic_caption_card`** — recommend **DEFINE** (META cluster). Smallest implementation cost (0.5 day), highest abstraction payoff, fixes ep_001 b35 OPEN-5 placeholder, prevents known visual-failure mode at b24.

**Total work if both DEFINEs land:** 2 days Pearl_Author + multi-character extension workstream (separately scoped). If all 3 DEFINEs land: 3 days Pearl_Author + multi-character extension.

**Critical sequencing:** `secondary_character_face_close` DEFINE is gated on multi-character extension. Either ship as joint workstream or DOWNGRADE for ep_002-only and DEFINE later when extension lands. Do not stack DEFINE on undefined extension.

End of brief.
