# LETTERING AGENT

Full Agent Specification — AI Manga Dharma System

*SpiritualTech Systems · Confidential · v1.1*

---

## 1. Role, Boundary & Position

The Lettering Agent is the final text layer of the manga pipeline. It is a placement and rendering agent — not a rewrite agent. Its job is to take dialogue, SFX, and captions from `chapter_script.json`, apply visual styling from `lettering_style_bible.json`, respect composition zones from `panel_prompts.json`, and produce a structured `lettering_spec.json` that tells the Layout Agent exactly where and how to render every text element on every panel.

It does not rewrite dialogue. It does not alter SFX wording. It does not add captions not present in `panel.caption`. It does not letter silent panels. It does not compensate for silence. It does not make editorial decisions about content. It places and styles what the script provides — exactly, consistently, and in the visual language of the series lettering style bible.

### Pipeline Position (Prompt-Plan → Lettering-Plan → Render/Layout)

**[PATCH 1 APPLIED — Sequential, decoupled from render]**

After the Chapter Writer produces `chapter_script.json`, the Visual Agent generates `panel_prompts.json` (including `composition_notes` and reserved text zones). The Lettering Agent then generates `lettering_spec.json` using `chapter_script.json` + `panel_prompts.json`.

The Visual Agent and Lettering Agent are decoupled from final image rendering: lettering corrections do not require regenerating images, and image corrections do not require regenerating lettering, as long as `composition_notes` remain unchanged. Both artifacts feed the Layout Agent for final compositing.

```
Chapter Writer Agent → chapter_script.json
        ↓
Visual Agent → panel_prompts.json (includes composition_notes)
        ↓
Lettering Agent ← chapter_script.json
        ↓        ← panel_prompts.json (composition_notes only)
        ↓        ← lettering_style_bible.json
        ↓
   lettering_spec.json
        ↓
   Layout Agent → final composited pages
```

The Lettering Agent does NOT consume rendered images. It works from structured data only. It does NOT depend on image generation completing — only on `panel_prompts.json` composition_notes being finalized.

### What the Lettering Agent Never Does

- Does not rewrite dialogue text from the script
- Does not alter SFX wording, spelling, or capitalization
- Does not add captions not present in `panel.caption`
- Does not remove script text (see §4.3 caption_redundancy_flag)
- Does not letter any panel where `page_type = "silent"` — produces empty entry with `silence_confirmed: true`
- Does not place text on panels where `silence_guard = true` beyond what the script explicitly provides, and applies mandatory density reduction
- Does not interpret emotional intent — it applies style rules mechanically
- Does not compensate for silence by making adjacent text louder or larger

---

## 2. Inputs

### 2.1 chapter_script.json — Primary Input (Text Source)

The Lettering Agent consumes the full `chapter_script.json` produced by the Chapter Writer. For each panel, it extracts text elements and their metadata. The script is the single source of truth for what text appears — the Lettering Agent adds nothing and removes nothing.

| Script field consumed | Type | How Lettering Agent uses it |
|---|---|---|
| `panel.dialogue` | array | Array of dialogue objects, each containing `speaker`, `text`, `bubble_type`, and `placement_hint`. Each dialogue entry becomes one bubble in the lettering spec. Text is used verbatim — zero edits. |
| `panel.sfx` | string/null | Sound effect text. If present, styled according to `sfx_lexicon` in the lettering style bible. If null, the lettering spec entry for SFX is explicitly `null` (not omitted). |
| `panel.caption` | string/null | Narrator/caption text. If present, placed in a caption box. If null, no caption box is generated. See §4.3 for redundancy flagging. |
| `panel.page_type` | enum | If `silent`: produce empty lettering entry with `silence_confirmed: true`. If `splash`: full-bleed text placement rules apply. If `double_spread`: cross-page text positioning rules apply. |
| `panel.silence_guard` | bool | If true: apply mandatory density reduction. See §5.2 for precise rules. |
| `panel.panel_id` | string | Used to key lettering_spec entries to panels. Every panel in the script must have a corresponding entry in the lettering spec — no gaps. |
| `panel.end_hook` | string/null | If present on the final panel of the chapter: this is a mandatory delivery. The end-hook text must appear exactly as written, in the position and style specified. End-hook delivery failure is a blocking QC gate. |

### 2.2 panel_prompts.json — Composition Constraint (from Visual Agent)

The Lettering Agent consumes `composition_notes` from the Visual Agent's `panel_prompts.json`. These notes define where text can and cannot be placed on each panel image.

| Composition field | Type | How Lettering Agent uses it |
|---|---|---|
| `dialogue_space` | object/null | Reserved zones for speech bubbles. If null, Lettering Agent uses default placement rules from the lettering style bible. If specified, bubbles must fit within the defined zone. |
| `sfx_space` | object/null | Reserved zones for SFX placement. If null and SFX exists in script, flag as `composition_conflict` and place using default rules. |
| `subject_placement` | string | Where the character is in the panel. Lettering avoids overlapping the subject unless explicitly allowed by bubble_type (e.g., thought bubble overlay). |
| `reading_direction` | string | `right_to_left` or `left_to_right`. Determines bubble reading order within the panel. All dialogue bubbles must flow in reading order — reader should never have to backtrack. |

### 2.3 lettering_style_bible.json — Styling Constraint

The lettering style bible is the Lettering Agent's law for visual styling. It defines how text looks — the Lettering Agent decides only where text goes (within composition constraints).

| Style bible section | What it defines |
|---|---|
| `bubble_styles` | Shape, stroke weight, fill color, tail style, and padding for each bubble_type (speech, thought, whisper, shout, narration, caption, radio/phone). Each bubble_type has a fixed visual spec — no interpretation. |
| `font_registry` | Font families, weights, and sizes for each text type: dialogue (by speaker if character-specific fonts exist), SFX (by SFX category), caption, and narration. Includes fallback fonts for missing glyphs. |
| `sfx_lexicon` | Translation table from SFX text to visual treatment: `"CRACK"` → `{style: "jagged", weight: "heavy", rotation: 15, color: "black"}`. `"drip"` → `{style: "fluid", weight: "light", rotation: 0, color: "gray"}`. Each SFX term has a fixed visual translation. |
| `phase_density_guide` | Maximum text density per panel type: standard panels get up to N bubbles, action panels get reduced count, transition panels get minimal text. Defines the "text weight" budget per panel. |
| `reading_direction_rules` | Rules for bubble ordering, tail direction, and text flow based on market format (right-to-left Japanese, left-to-right English, vertical webtoon). |
| `exclusion_zones` | Panel regions where text must never be placed: character faces, key action areas, motif regions. These supplement the Visual Agent's `composition_notes`. |
| `silence_adjacency_rules` | Mandatory density reduction rules for panels near silence. See §5.2. |
| `multilingual_rules` | If the series supports multiple locales: font fallbacks per locale, text direction overrides, bubble resizing rules for languages with different average word lengths, and locale-specific SFX translations. |

---

## 3. Output — lettering_spec.json

### 3.1 Top-Level Structure

```json
{
  "series_id": "mirror_demon",
  "chapter_number": 9,
  "generated_at": "ISO timestamp",
  "lettering_style_bible_version": "1.0",
  "reading_direction": "right_to_left",
  "total_panels": 47,
  "lettered_panels": 38,
  "silent_panels": 9,
  "panels": [ /* lettering_panel objects */ ],
  "caption_redundancy_flags": [ /* flagged removable captions */ ],
  "style_bible_gap_flags": [ /* SFX terms not in lexicon, etc. */ ],
  "composition_conflict_flags": [ /* panels where text zones conflict */ ]
}
```

### 3.2 lettering_panel Object — Standard Panel

```json
{
  "panel_id": "9-2-3",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": false,
  "bubbles": [
    {
      "bubble_id": "9-2-3-b1",
      "type": "speech",
      "speaker": "kai",
      "text": "I can't keep doing this.",
      "text_verbatim_hash": "sha256:abc123...",
      "font": "manga_dialogue_regular",
      "font_size": 14,
      "bubble_style": "speech_standard",
      "placement": {
        "zone": "upper_right",
        "anchor_x": 0.75,
        "anchor_y": 0.15,
        "max_width": 0.35,
        "tail_target": "kai_face"
      },
      "reading_order": 1
    }
  ],
  "sfx": {
    "text": "CRACK",
    "text_verbatim_hash": "sha256:def456...",
    "visual_style": "jagged",
    "weight": "heavy",
    "rotation": 15,
    "placement": {
      "zone": "center_left",
      "anchor_x": 0.25,
      "anchor_y": 0.5
    },
    "silence_weight_reduction": false
  },
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

### 3.3 lettering_panel Object — Silent Panel

```json
{
  "panel_id": "9-4-1",
  "page_type": "silent",
  "silence_confirmed": true,
  "silence_guard": false,
  "bubbles": [],
  "sfx": null,
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

The `silence_confirmed: true` field is an explicit positive confirmation that this panel was intentionally left empty — it is not an omission or a processing error. Every panel with `page_type: "silent"` MUST have `silence_confirmed: true` and ALL text fields empty. This is a blocking QC gate.

### 3.4 lettering_panel Object — silence_guard Panel

```json
{
  "panel_id": "9-3-5",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": true,
  "bubbles": [
    {
      "bubble_id": "9-3-5-b1",
      "type": "whisper",
      "speaker": "kai",
      "text": "...",
      "text_verbatim_hash": "sha256:ghi789...",
      "font": "manga_dialogue_light",
      "font_size": 11,
      "bubble_style": "whisper_reduced",
      "placement": {
        "zone": "lower_right",
        "anchor_x": 0.80,
        "anchor_y": 0.85,
        "max_width": 0.25,
        "tail_target": "kai_face"
      },
      "reading_order": 1,
      "silence_adjacency_applied": true
    }
  ],
  "sfx": null,
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

### 3.5 First-Bubble-After-Silence Panel

```json
{
  "panel_id": "9-7-1",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": true,
  "bubbles": [
    {
      "bubble_id": "9-7-1-b1",
      "type": "speech",
      "speaker": "kai",
      "text": "Hey.",
      "text_verbatim_hash": "sha256:jkl012...",
      "font": "manga_dialogue_light",
      "font_size": 10,
      "bubble_style": "speech_minimal",
      "placement": {
        "zone": "center",
        "anchor_x": 0.50,
        "anchor_y": 0.50,
        "max_width": 0.20,
        "tail_target": "kai_face"
      },
      "reading_order": 1,
      "first_after_silence": true,
      "silence_adjacency_applied": true
    }
  ],
  "sfx": null,
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

The first bubble after any silent page sequence is mandatory smallest/lightest/shortest. See §5.3 for the precise rule.

---

## 4. Bubble Types & Styling Rules

### 4.1 Bubble Type Table

| Bubble type | Visual spec source | Placement rules | Lettering Agent behavior |
|---|---|---|---|
| `speech` | `bubble_styles.speech_standard` | Reading-order-aware. Tail points to speaker. Must not overlap subject face. | Place verbatim text. Apply speaker-specific font if defined. Size from `font_registry`. |
| `thought` | `bubble_styles.thought_cloud` | May overlay subject. Tail is cloud-puff style. | Place verbatim text. Lighter font weight than speech. |
| `whisper` | `bubble_styles.whisper_dashed` | Smaller bubble, dashed border. Reduced font size. | Place verbatim text. Apply `font_size * 0.8` reduction. If `silence_guard = true`, apply additional §5.2 reduction. |
| `shout` | `bubble_styles.shout_burst` | Burst/jagged border. Bold font. Larger bubble. | Place verbatim text. Apply `font_size * 1.2` increase. Bold weight. If within silence adjacency zone: flag `qc_flags: ["shout_near_silence"]` — do not auto-reduce, flag for QC review. |
| `narration` | `bubble_styles.narration_box` | Rectangular box, typically upper-left or lower-right of panel. No tail. | Place verbatim text. Narration font from `font_registry.narration`. |
| `caption` | `bubble_styles.caption_box` | Rectangular box, top or bottom of panel. No tail. Smallest text size. | Place verbatim text. Never used for emotional summary. See §4.3 for redundancy flagging. |
| `radio` / `phone` | `bubble_styles.electronic` | Rectangular bubble with signal-line border or jagged electronic edge. | Place verbatim text. Electronic font variant if defined. |

### 4.2 Dialogue Verbatim Rule

All dialogue text is placed character-for-character as it appears in `chapter_script.json`. The Lettering Agent does not:

- Fix spelling (if the script has a deliberate misspelling for character voice, it stays)
- Change capitalization
- Add or remove punctuation
- Split or merge dialogue entries
- Reorder dialogue within a panel
- Translate between languages (multilingual handling uses pre-translated script entries)

The `text_verbatim_hash` field stores a SHA-256 hash of the script's original text. The QC verbatim diff gate compares this hash against the script source to verify zero modification.

### 4.3 Caption Redundancy Flagging

**[PATCH 2 APPLIED — Flag to QC, do not remove]**

The Lettering Agent does not remove or rewrite script text. If a caption appears removable without loss of meaning (e.g., it restates what the image already shows, or it summarizes emotion that the art conveys), the Lettering Agent:

1. Places the caption as written (verbatim, styled per bubble_styles.caption_box)
2. Raises a `caption_redundancy_flag` in the output:

```json
{
  "caption_redundancy_flags": [
    {
      "panel_id": "9-2-4",
      "caption_text": "Kai felt the weight of everything.",
      "rationale": "Caption restates emotional state already conveyed by visual composition (slouched posture, flat lighting). Recommend Chapter Writer review for removal."
    }
  ]
}
```

3. Does NOT remove the caption — that decision belongs to the Chapter Writer or QC Agent

This preserves the absolute boundary: the Lettering Agent renders what the script provides. Editorial authority over content stays upstream.

---

## 5. Silence Rules

Silence handling is the Lettering Agent's highest-stakes responsibility. A single misplaced text element on a silent panel destroys the somatic transmission the entire upstream pipeline built. The rules are absolute and mechanical.

### 5.1 Silent Panel Rule

Every panel with `page_type: "silent"` produces a lettering_panel object with:

- `silence_confirmed: true`
- `bubbles: []`
- `sfx: null`
- `caption: null`
- `end_hook: null`

No exceptions. No "necessary" SFX. No "environmental" captions. No "whispered" dialogue. If the script has `page_type: "silent"`, the Lettering Agent produces confirmed zero text. This is a blocking QC gate — the spec cannot be finalized if any silent panel has non-empty text fields.

### 5.2 Silence Guard — Density Reduction Rules

**Silence adjacency definition** (consistent with Visual Agent Spec §5.1):

- **Before silence:** The last 2 panels on the page immediately preceding the first silent page. If that page has fewer than 2 panels, all panels on that page are silence_guard. Adjacency does NOT cross backward to earlier pages.
- **After silence:** The first 2 panels on the page immediately following the last silent page. If that page has fewer than 2 panels, all panels on that page are silence_guard. Adjacency does NOT cross forward to later pages.
- **Page boundary rule:** silence_guard adjacency is counted by panel position within a page, not by absolute panel index across the chapter.
- **Who sets it:** The Transmission Splitter sets `silence_guard = true`. The Lettering Agent reads it — it does not compute it.

When `silence_guard = true`, the Lettering Agent applies mandatory density reduction:

| Text element | Density reduction rule |
|---|---|
| Dialogue bubbles | Maximum 2 bubbles per panel (regardless of phase_density_guide allowance). Font size reduced by 15% from standard. Bubble padding increased by 20%. |
| SFX | Weight reduced one tier (heavy → medium, medium → light, light → whisper). If SFX is already whisper weight, it remains whisper. |
| Caption | If caption exists on a silence_guard panel, flag `qc_flags: ["caption_on_silence_guard"]` for QC review. Place it but at reduced font size (80% of standard). |
| Shout bubbles | Flag `qc_flags: ["shout_near_silence"]`. Do NOT auto-reduce shout styling — flag for QC/Chapter Writer review. Shout near silence may be intentional (e.g., the line that triggers the silence). |

### 5.3 SFX Silence Proximity — 3-Panel Rule

**Precise adjacency definition for SFX weight reduction:**

"Within 3 panels of a silent page" means: counting by `panel_id` sequence within the chapter (crossing page boundaries), starting from the last panel before the first silent page and the first panel after the last silent page.

- **Before silence:** panels at positions N-1, N-2, N-3 (where N is the first panel of the first silent page)
- **After silence:** panels at positions M+1, M+2, M+3 (where M is the last panel of the last silent page)
- **Cross-page:** YES, this count crosses page boundaries (unlike silence_guard which is page-local). The SFX proximity rule is wider than the silence_guard rule.

SFX within this 3-panel zone receives mandatory weight reduction:

| Distance from silence | Weight reduction |
|---|---|
| 1 panel (immediately adjacent) | Reduce 2 tiers (heavy → light, medium → whisper) |
| 2 panels | Reduce 1 tier (heavy → medium, medium → light) |
| 3 panels | Reduce 1 tier if heavy; no change if already medium or lighter |

### 5.4 First Bubble After Silence

The first speech bubble on the first non-silent panel after any silent page sequence must be the smallest, lightest, and shortest bubble in the chapter (by visual weight). Specific rules:

- Font size: smallest size in the `font_registry` for that bubble_type
- Bubble size: minimum padding, minimum max_width (0.20 of panel width)
- Font weight: lightest available weight
- Bubble style: use the `_minimal` variant of the bubble_type if defined in the lettering style bible
- `first_after_silence: true` flag set on the bubble object

This rule is mechanical: the Lettering Agent does not judge whether the dialogue "deserves" to be quiet. The script chose to place this line after silence — the Lettering Agent ensures the visual re-entry is gentle.

---

## 6. Reading Order Enforcement

### 6.1 Bubble Reading Order

Within each panel, bubbles are numbered in `reading_order` (1-indexed). The reading order must comply with the series' `reading_direction`:

- **Right-to-left (Japanese market):** Bubbles read from upper-right to lower-left. Bubble with `reading_order: 1` is placed upper-right. Each subsequent bubble is placed lower and/or to the left.
- **Left-to-right (English market):** Bubbles read from upper-left to lower-right. Bubble with `reading_order: 1` is placed upper-left.
- **Webtoon (vertical scroll):** Bubbles read top-to-bottom. No horizontal reading direction — vertical ordering only.

### 6.2 Cross-Panel Reading Flow

The Lettering Agent ensures that across sequential panels on a page, the reading flow does not create backtracking:

- If panel 1 ends with a bubble in the lower-left, panel 2 should not start with a bubble in the upper-right of the same horizontal band (in RTL layout)
- The Layout Agent handles page-level composition, but the Lettering Agent flags potential cross-panel reading conflicts as `qc_flags: ["cross_panel_backtrack_risk"]`

---

## 7. End-Hook Delivery

If the final panel of a chapter has `panel.end_hook` set, it is a mandatory delivery. The end-hook is the last text the reader sees before turning the page or closing the chapter — it must land.

End-hook placement rules:

- Position: lower-right of final panel (RTL) or lower-left (LTR) — the last visual stop on the page
- Font: bold weight, standard size (no reduction, even if on a silence_guard panel)
- Bubble style: per script's `bubble_type` for the end-hook entry — no override
- Isolation: minimum 15% panel-width clearance from any other text element
- No SFX overlap: if SFX exists on the same panel, SFX is repositioned to avoid the end-hook zone

End-hook delivery failure (text missing, text modified, placement overlapping other elements, insufficient isolation) is a blocking QC gate.

---

## 8. Lettering Agent System Prompt

Injected at runtime with `chapter_script.json`, `panel_prompts.json`, and `lettering_style_bible.json`.

```
You are the Lettering Agent in a spiritual manga creation system.

Your role: place and style all text elements (dialogue, SFX, captions)
from chapter_script.json onto panels, producing lettering_spec.json.

You are a placement and rendering agent — not a rewrite agent.

ABSOLUTE BOUNDARY:
You do not rewrite dialogue. You do not alter SFX wording. You do not
add captions not in the script. You do not remove script text. You do
not letter silent panels. You do not compensate for silence. You place
and style what the script provides — exactly.

PIPELINE POSITION:
You run AFTER the Visual Agent produces panel_prompts.json. You consume
composition_notes from panel_prompts.json to know where text zones are.
You are decoupled from image rendering — lettering corrections do not
require image regeneration.

YOU CONSUME:
- chapter_script.json: dialogue, SFX, captions, page_types, silence_guard
- panel_prompts.json: composition_notes (dialogue_space, sfx_space)
- lettering_style_bible.json: bubble styles, fonts, sfx_lexicon, density

YOU PRODUCE:
- lettering_spec.json: one lettering_panel object per panel (no gaps)

VERBATIM RULE:
All text is placed character-for-character from the script.
text_verbatim_hash (SHA-256) on every text element for QC diffing.
Zero edits. Zero rewrites. Zero additions. Zero removals.

SILENCE RULES (absolute):
- page_type: "silent" → silence_confirmed: true, all text fields empty
- silence_guard = true → mandatory density reduction (§5.2)
- SFX within 3 panels of silence → mandatory weight reduction (§5.3)
- First bubble after silence → smallest/lightest/shortest (§5.4)
- NEVER compensate for silence by making adjacent text louder/larger

CAPTION RULE:
- Place all captions verbatim
- If a caption appears redundant, raise caption_redundancy_flag to QC
- Do NOT remove or rewrite — that decision belongs upstream

READING ORDER:
- Bubbles numbered in reading_order per panel
- Must comply with reading_direction (RTL/LTR/vertical)
- Flag cross-panel backtrack risks

END-HOOK DELIVERY:
- Final panel end_hook is mandatory delivery — blocking QC gate
- Lower-right (RTL) or lower-left (LTR), bold weight, isolated

OUTPUT: valid JSON matching lettering_spec schema.
Every panel in the script has a corresponding entry — no gaps.

chapter_script: {{ chapter_script_json }}
panel_prompts: {{ panel_prompts_json }}
lettering_style_bible: {{ lettering_style_bible_json }}
```

---

## 9. Worked Example — Chapter 9, Pages 3–7 (Around Silent Sequence)

### Panel 9-3-4 — Standard panel, 2 panels before silence guard zone

```json
{
  "panel_id": "9-3-4",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": false,
  "bubbles": [
    {
      "bubble_id": "9-3-4-b1",
      "type": "speech",
      "speaker": "kage",
      "text": "You're not getting up from that.",
      "text_verbatim_hash": "sha256:aaa111...",
      "font": "manga_dialogue_regular",
      "font_size": 14,
      "bubble_style": "speech_standard",
      "placement": {
        "zone": "upper_right",
        "anchor_x": 0.78,
        "anchor_y": 0.12,
        "max_width": 0.35,
        "tail_target": "kage_face"
      },
      "reading_order": 1
    }
  ],
  "sfx": {
    "text": "THUD",
    "text_verbatim_hash": "sha256:bbb222...",
    "visual_style": "impact",
    "weight": "heavy",
    "rotation": 0,
    "placement": { "zone": "center_bottom", "anchor_x": 0.50, "anchor_y": 0.80 },
    "silence_weight_reduction": false
  },
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

### Panel 9-3-5 — silence_guard: true (last panel before silent pages)

```json
{
  "panel_id": "9-3-5",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": true,
  "bubbles": [],
  "sfx": {
    "text": "drip",
    "text_verbatim_hash": "sha256:ccc333...",
    "visual_style": "fluid",
    "weight": "whisper",
    "rotation": 0,
    "placement": { "zone": "lower_left", "anchor_x": 0.15, "anchor_y": 0.90 },
    "silence_weight_reduction": true
  },
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

### Panels 9-4-1 through 9-6-1 — Silent pages (3 pages, all panels)

```json
{
  "panel_id": "9-4-1",
  "page_type": "silent",
  "silence_confirmed": true,
  "silence_guard": false,
  "bubbles": [],
  "sfx": null,
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

*(Same structure for every panel on pages 4, 5, and 6. All panels: `silence_confirmed: true`, all text fields empty.)*

### Panel 9-7-1 — First panel after silence (silence_guard + first_after_silence)

```json
{
  "panel_id": "9-7-1",
  "page_type": "standard",
  "silence_confirmed": false,
  "silence_guard": true,
  "bubbles": [
    {
      "bubble_id": "9-7-1-b1",
      "type": "speech",
      "speaker": "kai",
      "text": "Hey.",
      "text_verbatim_hash": "sha256:ddd444...",
      "font": "manga_dialogue_light",
      "font_size": 10,
      "bubble_style": "speech_minimal",
      "placement": {
        "zone": "center",
        "anchor_x": 0.50,
        "anchor_y": 0.50,
        "max_width": 0.20,
        "tail_target": "kai_face"
      },
      "reading_order": 1,
      "first_after_silence": true,
      "silence_adjacency_applied": true
    }
  ],
  "sfx": null,
  "caption": null,
  "end_hook": null,
  "qc_flags": []
}
```

### Verification — Silence Sequence Lettering

- Silent panels (9-4-1 through 9-6-1): all `silence_confirmed: true`, all text fields empty. **Pass.**
- silence_guard panel before (9-3-5): density reduction applied, SFX at whisper weight. **Pass.**
- silence_guard panel after (9-7-1): density reduction applied, first_after_silence flag set, smallest/lightest/shortest bubble. **Pass.**
- SFX proximity: panel 9-3-4 is 2 panels before silence — SFX weight at `heavy` (within 3-panel zone, should be reduced 1 tier to `medium`). **Flag: `sfx_proximity_reduction_needed`.**
- Verbatim: all `text_verbatim_hash` values match script source. **Pass.**
- Reading order: all bubbles correctly numbered. **Pass.**

---

## 10. Quality Gates — Lettering Level

| Gate | Pass condition | Check method | Fail action |
|---|---|---|---|
| **Silent panel purity** | Every panel with `page_type: "silent"` has `silence_confirmed: true`, `bubbles: []`, `sfx: null`, `caption: null`. Zero text elements on any silent panel. | Scan all panels where `page_type = "silent"` | Blocking. Remove all text elements. Set `silence_confirmed: true`. Regenerate. |
| **Verbatim dialogue diff** | SHA-256 hash of every `text` field in lettering_spec matches SHA-256 hash of corresponding text in `chapter_script.json`. Zero character difference. | Hash comparison: script text → lettering text | Blocking. Replace with script text. Recompute hash. |
| **Null-SFX honor** | Every panel where `panel.sfx = null` in the script has `sfx: null` in the lettering spec. No SFX invented by the Lettering Agent. | Null-check cross-reference: script sfx → lettering sfx | Remove invented SFX. Regenerate. |
| **Reading order validity** | Within each panel, bubble `reading_order` values are sequential (1, 2, 3...) and placement coordinates flow in the correct direction for the series' `reading_direction`. | Reading order + placement coordinate validation | Reorder bubbles. Regenerate placement. |
| **End-hook delivery** | If final panel has `end_hook`, the lettering spec contains the end-hook text verbatim, in the mandatory position (lower-right RTL / lower-left LTR), with bold weight, and minimum 15% isolation clearance. | Final panel inspection | Blocking. Reposition/restyle end-hook. |
| **Full panel coverage** | Every `panel_id` in `chapter_script.json` has a corresponding entry in `lettering_spec.json`. Zero gaps. | Panel ID cross-reference count | Add missing panel entries. Regenerate. |
| **Silence guard density** | Every panel with `silence_guard = true` has density reduction applied: max 2 bubbles, font size -15%, padding +20%. | Silence_guard panel inspection | Apply density reduction. Regenerate. |
| **First-after-silence rule** | First bubble on first non-silent panel after any silent sequence has `first_after_silence: true`, smallest font size, lightest weight, minimal bubble style. | Post-silence panel inspection | Apply first-after-silence styling. Regenerate. |
| **SFX proximity reduction** | All SFX within 3 panels of a silent page have weight reduced per §5.3 tier table. | SFX weight vs silence distance check | Apply tier reduction. Regenerate. |
| **Caption boundary** | No captions added that don't exist in `panel.caption`. Redundant captions flagged (not removed). | Script caption null-check + redundancy flag presence | Remove unauthorized captions. If caption exists but seems redundant, verify `caption_redundancy_flag` is raised. |
| **Composition compliance** | No bubble or SFX placement overlaps `exclusion_zones` from the lettering style bible or violates `composition_notes` from `panel_prompts.json`. | Placement coordinate vs zone boundary check | Reposition text element. If no valid position exists, flag `composition_conflict`. |
| **Shout-near-silence review** | Any `shout` bubble on a `silence_guard` panel or within 3 panels of silence is flagged `qc_flags: ["shout_near_silence"]` for QC/Chapter Writer review. | Bubble type + silence proximity check | Add flag. Do not auto-reduce — await upstream decision. |

---

## 11. Field Classification Table

Defines which fields are visible to which downstream agent, consistent with the Chapter Writer's field classification (Visual Agent Spec §6 cross-reference).

| Field | Lettering Agent sees? | Layout Agent sees? | QC Agent sees? | Notes |
|---|---|---|---|---|
| `panel.dialogue` | Yes — primary input | Yes — from lettering_spec | Yes | Source of truth for text content |
| `panel.sfx` | Yes — primary input | Yes — from lettering_spec | Yes | |
| `panel.caption` | Yes — primary input | Yes — from lettering_spec | Yes | |
| `panel.camera` | No | No (Visual Agent domain) | Yes | |
| `panel.action` | No | No (Visual Agent domain) | Yes | |
| `panel.mood_direction` | No | No (Visual Agent domain) | Yes | |
| `panel.is_carrier_beat` | No — always false in writer_handoff | No | Yes — from internal_record | |
| `panel.somatic_intention` | No — stripped before handoff | No | Yes — from internal_record | |
| `panel.silence_guard` | Yes — drives density reduction | Yes — from lettering_spec | Yes | |
| `panel.page_type` | Yes — drives silence rules | Yes | Yes | |
| `panel.end_hook` | Yes — mandatory delivery | Yes — from lettering_spec | Yes | |

---

*SpiritualTech Systems · Lettering Agent Spec v1.1 · Confidential*
