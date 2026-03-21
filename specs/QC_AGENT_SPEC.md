# QC AGENT

Full Agent Specification — AI Manga Dharma System

*SpiritualTech Systems · Confidential · v1.1*

---

## 1. Role, Boundary & Position

The QC Agent is the final release authority for every chapter in the pipeline. It inspects every upstream artifact — `chapter_script.json`, `panel_prompts.json`, `lettering_spec.json`, and rendered panel images — against the rules defined by every upstream spec. It either clears a chapter for release or blocks it with a structured revision queue.

The QC Agent is not creative. It does not rewrite dialogue. It does not alter visual prompts. It does not redesign lettering. It does not make aesthetic judgments. It enforces rules mechanically, flags violations by severity, applies lossless auto-fixes where permitted, and escalates everything else to the owning agent.

### Pipeline Position

```
Chapter Writer → chapter_script.json ──────────────────┐
        ↓                                               │
Visual Agent → panel_prompts.json ──────────────┐       │
        ↓                                       │       │
Lettering Agent → lettering_spec.json ──┐       │       │
        ↓                               │       │       │
Layout Agent → rendered_pages[] ──┐     │       │       │
                                  │     │       │       │
                                  ▼     ▼       ▼       ▼
                              QC AGENT (inspects all four)
                                  │
                          ┌───────┼───────┐
                          ▼       ▼       ▼
                      CLEARED  BLOCKED  AUTO-FIXED
                          │       │       │
                          ▼       ▼       ▼
                      Release  revision   Re-inspect
                               _queue     after fix
                               .json
```

### What the QC Agent Owns

- Final chapter clearance (release / block decision)
- Gate enforcement across all upstream agents
- Structured issue detection, classification, and severity assignment
- Lossless auto-fix application (where permitted)
- Revision queue generation for upstream agents
- Cross-chapter series memory (continuity facts, forward expectations)
- Gate registry governance (what is enforced and what is not)

### What the QC Agent Never Does

- Does not rewrite dialogue, captions, or any script text
- Does not alter visual prompts or negative prompts
- Does not redesign lettering placement or bubble styling
- Does not make aesthetic judgments ("this panel looks better if...")
- Does not add narrative content, motifs, or characters
- Does not override upstream agent authority — it flags; they fix
- Does not apply auto-fixes that change meaning, are irreversible, or require upstream regeneration
- Does not enforce gates not in the Gate Registry (§8) — if it's not listed, it's not enforced

---

## 2. Inputs

The QC Agent consumes artifacts from every upstream agent, plus the internal_record version of the chapter_script (which contains transmission metadata invisible to rendering agents).

### 2.1 Artifact Inventory

| Artifact | Source agent | What QC inspects |
|---|---|---|
| `chapter_script.json` (writer_handoff) | Chapter Writer | Dialogue verbatim integrity, silence page/panel structure, end-hook presence, page_type assignments, silence_guard flags |
| `chapter_script.json` (internal_record) | Chapter Writer | `is_carrier_beat` true values, `somatic_intention` fields, transmission annotations — used for transmission integrity checks (§6) |
| `panel_prompts.json` | Visual Agent | Style token completeness, prohibited term absence, camera fidelity, character reference injection, silence purity, silence_guard compliance, continuity consistency, no-new-meaning scan, drift detection flags, token budget compliance |
| `lettering_spec.json` | Lettering Agent | Silent panel purity (`silence_confirmed`), verbatim dialogue hash verification, null-SFX honor, reading order validity, end-hook delivery, full panel coverage, silence_guard density reduction, first-after-silence rule, SFX proximity reduction, caption boundary, composition compliance |
| `rendered_pages[]` | Layout Agent / Image Gen | Visual drift measurement against anchor panels, rendered image parameter extraction (contrast ratio, linework weight, shadow coverage) for drift detection |
| `style_bible.json` (writer-facing) | Visual Identity Agent | Version match verification — all downstream artifacts must reference the same `style_bible_version` |
| `style_bible.json` (internal) | Visual Identity Agent | Motif transmission binding cross-reference, anchor panel measured parameters for drift comparison |
| `lettering_style_bible.json` | Visual Identity Agent | Bubble style compliance, font registry compliance |

### 2.2 Internal Record Access

The QC Agent is the only downstream agent (besides the Visual Identity Agent) that sees the `internal_record` version of `chapter_script.json`. This gives QC access to:

- `is_carrier_beat`: which panels carry transmission weight (true values)
- `somatic_intention`: what each beat is meant to achieve somatically
- `transmission_annotations`: upstream notes about teaching-layer integrity

QC uses these for transmission integrity checks (§6) but never exposes them in the `revision_queue.json` — issue descriptions reference panel_ids and observable symptoms only, never internal metadata.

---

## 3. Three-Level Detection Stack

The QC Agent runs three detection levels in order, from fastest/hardest to slowest/softest. Earlier levels run first because they catch blocking issues before slower analysis begins.

### Level 1 — Structural Validation (Fastest)

Deterministic checks that can be computed in a single pass over the JSON artifacts. No rendering required. No cross-chapter state needed.

| Check | What it validates | Fail severity |
|---|---|---|
| Schema conformance | All artifacts match their defined JSON schemas (required fields present, correct types, no extra fields) | BLOCKER |
| Panel coverage | Every `panel_id` in `chapter_script.json` has corresponding entries in `panel_prompts.json` and `lettering_spec.json` — zero gaps | BLOCKER |
| Version match | `style_bible_version` in `panel_prompts.json` and `lettering_spec.json` matches `style_bible.json` | BLOCKER |
| Silent panel purity | Every panel with `page_type: "silent"` has: empty dialogue/sfx/caption in script, `silence_compliance: true` in prompts, `silence_confirmed: true` + empty text fields in lettering | BLOCKER |
| Verbatim dialogue hash | SHA-256 hash of every `text` field in `lettering_spec.json` matches hash of corresponding text in `chapter_script.json` | BLOCKER |
| Style token prefix | Every positive prompt in `panel_prompts.json` begins with the complete `series_style_tokens` in correct order | MAJOR |
| Prohibited term scan | Zero words from `prohibited_style_terms` appear in any positive prompt | MAJOR |
| Camera fidelity | Every `camera_prompt_term` matches the exact `camera_lexicon` translation for the script's camera value | MAJOR |
| Null-SFX honor | Every panel where `panel.sfx = null` in script has `sfx: null` in lettering_spec | MAJOR |
| End-hook delivery | Final panel's `end_hook` text appears verbatim in lettering_spec, in mandatory position, with correct styling | BLOCKER |
| Token budget | Every positive prompt ≤ 120 tokens, every negative prompt ≤ 60 tokens (per Visual Agent Spec §3.4) | MAJOR |
| Reading order validity | Bubble `reading_order` values are sequential within each panel and placement coordinates flow in correct `reading_direction` | MAJOR |
| ID contract | All `character_refs`, `asset_refs`, and motif references use registry IDs, not free-text names (per Visual Identity Agent Spec §10) | MAJOR |

### Level 2 — Cross-Reference Validation (Medium Speed)

Checks that require comparing fields across multiple artifacts or loading continuity state.

| Check | What it validates | Fail severity |
|---|---|---|
| Character reference injection | Every panel with a named character in `panel.subject` has a non-empty `character_refs` entry with `lora_id` in `panel_prompts.json` | MAJOR |
| Continuity consistency | Character `continuity_state` at each panel matches the state after the previous panel. Injuries, outfit, hair, props must be consistent unless a script event changes them. | MAJOR |
| Silence_guard compliance (Visual) | Every panel with `silence_guard = true` in script has core text prohibition subset in negative prompt | MAJOR |
| Silence_guard compliance (Lettering) | Every panel with `silence_guard = true` has density reduction applied: max 2 bubbles, font -15%, padding +20% | MAJOR |
| First-after-silence | First bubble on first non-silent panel after silence has `first_after_silence: true`, smallest/lightest/shortest styling | MAJOR |
| SFX proximity reduction | All SFX within 3 panels of a silent page (chapter-sequential, crossing page boundaries) have weight reduced per Lettering Agent Spec §5.3 tier table | MAJOR |
| No-new-meaning 7-point scan | Visual Agent's 7-point violation checklist (Visual Agent Spec §6): symbolic props, weather changes, extra characters, dramatic effects, off-script characters, emotional escalation, symbolic composition | MAJOR |
| Asset reuse | Every recurring location/prop/motif uses `asset_id` reference, never free-text description | MAJOR |
| Composition compliance | No lettering placement overlaps `exclusion_zones` or violates `composition_notes` | MAJOR |
| Caption boundary | No captions in lettering_spec that don't exist in script. `caption_redundancy_flags` raised where appropriate (not removed) | MINOR |
| Motif schedule | Motifs appear only in their `scheduled_appearances` chapters/pages. No unscheduled motif insertion. | MAJOR |

### Level 3 — Rendered Output Validation (Slowest)

Checks that require analyzing rendered panel images against anchor panels and measured parameters. These run last because they depend on image generation completing.

| Check | What it validates | Fail severity |
|---|---|---|
| Visual drift detection | Every 10th rendered panel: measured parameters (contrast_ratio, linework_weight_px, shadow_coverage_pct, highlight_coverage_pct) compared against nearest anchor panel. Delta must be within `drift_detection.threshold`. | MAJOR |
| Silence visual purity (rendered) | Rendered silent panels contain zero visible text, signage, readable language, symbols, or text-like shapes in the image itself | BLOCKER |
| Character identity (rendered) | Named characters in rendered panels visually match their model sheets. Outfit matches `outfit_id`. Injuries/props visible as specified in continuity_state. | MAJOR |
| Semantic drift scan | Rendered panels near carrier beats do not visually emphasize the carrier beat more than surrounding panels. No unearned spotlight, no special lighting, no compositional centering that adjacent non-carrier panels lack. | See §3.1 |

### 3.1 Semantic Drift Severity — Resolved

**[FIX 1 — Semantic drift severity inconsistency resolved]**

`TRANSMISSION.SEMANTIC_DRIFT` is classified as **MINOR** by default. The QC Agent flags it and logs it in `revision_queue.json` but does not block chapter clearance for a single minor drift instance.

Escalation to **MAJOR** occurs when either:

- **(a) Above threshold:** The drift is measurable — e.g., a carrier-beat panel has contrast ratio > 0.15 higher than adjacent non-carrier panels, or subject scale > 20% larger, or uses a camera angle not used on adjacent panels without script justification
- **(b) Repeated across chapters:** The same carrier_beat pattern (same atom family, same visual emphasis type) has been flagged as MINOR in 2+ previous chapters. Series memory (§7) tracks this. On the 3rd occurrence, auto-escalate to MAJOR.

This resolves the Level 1 "soft fail = major" description vs Gate Registry "MINOR (flag)" inconsistency by making MINOR the default with defined escalation triggers.

---

## 4. Severity Rubric

### 4.1 Severity Levels

| Severity | Definition | Effect on clearance | Auto-fix permitted? |
|---|---|---|---|
| **BLOCKER** | The artifact is structurally invalid, violates an absolute rule (silence purity, verbatim integrity, schema conformance), or would cause a downstream system failure. | Chapter cannot be cleared. No exceptions. | No. Blockers always require upstream agent regeneration. |
| **MAJOR** | The artifact violates a quality gate but is not structurally broken. The violation is detectable in the final output and degrades series quality. | Chapter cannot be cleared unless all majors are resolved or auto-fixed (see §4.3). | Yes, if the fix is lossless, reversible, and does not require upstream regeneration. |
| **MINOR** | The artifact has a quality concern that does not affect structural integrity or reader experience in isolation. Typically flagged for upstream awareness. | Chapter can be cleared with minors present. Minors are logged in revision_queue for future improvement. | Yes, with same constraints. |

### 4.2 Auto-Escalation Rules

| Condition | Escalation |
|---|---|
| Same MINOR issue type appears on 3+ panels in the same chapter | Escalate to MAJOR for all instances in that chapter |
| Same MINOR issue type flagged in 3+ consecutive chapters (series memory) | Escalate to MAJOR going forward until upstream agent addresses root cause |
| A MAJOR issue type appears on 5+ panels in the same chapter | Escalate to BLOCKER — indicates systemic upstream failure, not isolated error |

### 4.3 Auto-Fix Safety Clause

**[FIX 2 — Auto-fixed majors pass condition formalized]**

Auto-fixed MAJOR issues may pass clearance ONLY if ALL of the following conditions are met:

1. **`lossless: true`** — The fix does not discard information. Adding a missing prohibited term to a negative prompt is lossless. Removing a dialogue line is not.
2. **`reversible: true`** — The fix can be undone without upstream regeneration. Appending terms to a negative prompt is reversible. Altering the positive prompt assembly order is not.
3. **`requires_upstream_regen: false`** — The fix does not require the Visual Agent, Lettering Agent, or Chapter Writer to regenerate their output. If it does, it is not an auto-fix — it is an escalation.

If any auto-fix on a MAJOR issue has `lossless: false`, `reversible: false`, or `requires_upstream_regen: true`, the chapter remains blocked and the issue is escalated to the owning agent.

```json
{
  "auto_fix": {
    "fix_id": "fix_9-3-2_prohibited_term",
    "description": "Removed 'illustration' from positive prompt for panel 9-3-2",
    "lossless": true,
    "reversible": true,
    "requires_upstream_regen": false,
    "original_value": "...illustration, clean ink line...",
    "fixed_value": "...clean ink line...",
    "owning_agent": "visual_agent"
  }
}
```

### 4.4 Permitted Auto-Fix Categories

| Auto-fix type | Lossless? | Reversible? | Regen? | Example |
|---|---|---|---|---|
| Add missing prohibited term to negative prompt | Yes | Yes | No | `negative_prompt += ", watercolor"` |
| Remove prohibited term from positive prompt | Yes | Yes | No | Strip "illustration" from positive prompt |
| Add missing silence prohibition terms to negative prompt | Yes | Yes | No | Append full prohibition list to silence_guard panel |
| Correct `style_tokens_applied` array order | Yes | Yes | No | Reorder tokens to match style_bible order |
| Set missing `silence_confirmed: true` on empty silent panel | Yes | Yes | No | Field was omitted, not wrong |
| Fix `reading_order` numbering (sequential gap) | Yes | Yes | No | `[1, 3]` → `[1, 2]` |
| **NOT permitted:** Rewrite dialogue | No | No | Yes | — |
| **NOT permitted:** Change camera_prompt_term | No | No | Yes | — |
| **NOT permitted:** Remove SFX from panel | No | Yes | Yes | — |
| **NOT permitted:** Alter positive prompt assembly | No | No | Yes | — |

---

## 5. Output — revision_queue.json

### 5.1 Top-Level Structure

```json
{
  "series_id": "mirror_demon",
  "chapter_number": 9,
  "qc_run_at": "ISO timestamp",
  "style_bible_version": "1.0",
  "clearance": "BLOCKED | CLEARED | CLEARED_WITH_AUTO_FIXES",
  "summary": {
    "total_issues": 7,
    "blockers": 0,
    "majors": 3,
    "minors": 4,
    "auto_fixed": 2,
    "remaining_blockers": 0,
    "remaining_majors": 1
  },
  "issues": [ /* issue objects */ ],
  "auto_fixes_applied": [ /* auto-fix objects */ ],
  "clearance_decision": {
    "result": "BLOCKED",
    "reason": "1 MAJOR issue not auto-fixable (continuity_consistency on panel 9-5-3)",
    "blocking_issues": ["issue_003"]
  }
}
```

### 5.2 Issue Object

```json
{
  "issue_id": "issue_003",
  "gate": "VISUAL.CONTINUITY_CONSISTENCY",
  "severity": "MAJOR",
  "panel_id": "9-5-3",
  "artifact": "panel_prompts.json",
  "owning_agent": "visual_agent",
  "description": "Character kai has bruised_knuckles_right in continuity_state at panel 9-5-2, but panel 9-5-3 prompt does not include injury in continuity_injections. No healing event in script between these panels.",
  "expected": "bruised_knuckles_right in continuity_injections",
  "found": "no injury reference in prompt",
  "auto_fixable": false,
  "auto_fix_reason": "Requires prompt regeneration by Visual Agent — not a lossless append",
  "escalation_target": "visual_agent",
  "related_issues": [],
  "series_memory_ref": null
}
```

### 5.3 Auto-Fix Object

```json
{
  "fix_id": "fix_001",
  "issue_id": "issue_001",
  "gate": "VISUAL.PROHIBITED_TERM_SCAN",
  "panel_id": "9-2-4",
  "artifact": "panel_prompts.json",
  "description": "Removed 'illustration' from positive prompt",
  "lossless": true,
  "reversible": true,
  "requires_upstream_regen": false,
  "original_value": "clean ink line 0.8pt weight, illustration, screentone shading...",
  "fixed_value": "clean ink line 0.8pt weight, screentone shading...",
  "owning_agent": "visual_agent"
}
```

---

## 6. Transmission Integrity Checks

The QC Agent is the only agent that cross-references the `internal_record` (containing carrier beat flags and somatic intention) against the rendered output. The goal: carrier beats must be invisible. No panel should visually announce "this is the teaching moment."

### 6.1 What QC Checks

| Check | Method | What constitutes a violation |
|---|---|---|
| **Carrier beat visual emphasis** | Compare measured parameters (contrast_ratio, subject_scale, camera_angle) of carrier-beat panels against adjacent non-carrier panels | Carrier panel has contrast > 0.15 higher, subject > 20% larger, or unique camera angle not used by adjacent panels |
| **Carrier beat lettering emphasis** | Compare font size, bubble size, and bubble count of carrier-beat panels against adjacent panels | Carrier panel has largest font or most bubbles on its page without script justification |
| **Motif-carrier alignment** | Cross-reference motif appearances against carrier beats | A motif appears on or immediately adjacent to a carrier beat AND nowhere else in the chapter — suggests deliberate visual "highlighting" |
| **Caption teaching leak** | Scan captions on or adjacent to carrier beats for forbidden phrases (per Chapter Writer QC gates) | Caption text on carrier beat contains: teaching language, wisdom paraphrase, emotional summary, or "the lesson" phrasing |

### 6.2 Transmission Issue Reporting

Transmission issues are reported in `revision_queue.json` using observable symptoms only. The issue description never mentions `is_carrier_beat`, `somatic_intention`, or internal metadata.

```json
{
  "issue_id": "issue_005",
  "gate": "TRANSMISSION.SEMANTIC_DRIFT",
  "severity": "MINOR",
  "panel_id": "9-7-2",
  "artifact": "panel_prompts.json",
  "owning_agent": "visual_agent",
  "description": "Panel 9-7-2 has contrast_ratio 0.62 while adjacent panels 9-7-1 (0.45) and 9-7-3 (0.47) average 0.46. This panel has unusually elevated visual emphasis compared to its neighbors.",
  "expected": "contrast_ratio within 0.10 of adjacent panel average",
  "found": "contrast_ratio delta of 0.16 from adjacent average",
  "auto_fixable": false,
  "escalation_target": "visual_agent",
  "series_memory_ref": "sm_semantic_drift_atom_family_3"
}
```

Note: the issue says "unusually elevated visual emphasis" — not "this is a carrier beat that got too much spotlight." The internal reason is known to QC but not disclosed downstream.

---

## 7. Series Memory — Cross-Chapter State

The QC Agent maintains a `series_memory_update.json` that persists across chapters. This allows detection of patterns that only emerge over multiple chapters (repeating issues, continuity violations, escalation triggers).

### 7.1 Structure

```json
{
  "series_id": "mirror_demon",
  "last_updated_chapter": 9,
  "updated_at": "ISO timestamp",

  "continuity_facts": [
    {
      "fact_id": "cf_kai_scar",
      "type": "permanent_physical",
      "character_id": "kai",
      "description": "Scar on right eyebrow",
      "established_chapter": 1,
      "expected_in_all_chapters_after": true
    },
    {
      "fact_id": "cf_mirror_state_ch9",
      "type": "motif_evolution",
      "asset_id": "mirror_pieces_covered",
      "description": "Cloth half off, reflection increasingly clear",
      "established_chapter": 9,
      "evolution_schedule_ref": "chapters_9_12"
    }
  ],

  "forward_expectations": [
    {
      "expectation_id": "fe_kai_knuckles_heal",
      "type": "injury_resolution",
      "character_id": "kai",
      "description": "bruised_knuckles_right should heal or be addressed by chapter 12",
      "set_at_chapter": 9,
      "deadline_chapter": 12,
      "status": "open"
    }
  ],

  "recurring_issues": [
    {
      "issue_type": "VISUAL.CONTINUITY_CONSISTENCY",
      "occurrences": [
        { "chapter": 7, "panel": "7-4-2", "description": "Kai outfit changed without script event" },
        { "chapter": 8, "panel": "8-2-5", "description": "Kai hair state reset to default without script event" }
      ],
      "count": 2,
      "escalation_status": "warning — one more triggers MAJOR escalation"
    },
    {
      "issue_type": "TRANSMISSION.SEMANTIC_DRIFT",
      "atom_family": "family_3",
      "occurrences": [
        { "chapter": 6, "panel": "6-8-3", "severity": "MINOR" },
        { "chapter": 8, "panel": "8-12-1", "severity": "MINOR" }
      ],
      "count": 2,
      "escalation_status": "warning — 3rd occurrence auto-escalates to MAJOR per §3.1"
    }
  ],

  "fact_types": [
    "permanent_physical",
    "temporary_injury",
    "outfit_change",
    "location_state",
    "motif_evolution",
    "relationship_state",
    "prop_acquisition",
    "prop_loss"
  ]
}
```

### 7.2 Series Memory Rules

- **Forward expectations** are set by QC when it detects a state that should resolve (injuries should heal, props should be used or discarded). If the deadline chapter passes without resolution, QC flags it as MINOR for upstream review.
- **Recurring issues** track how many times the same issue type appears across chapters. Escalation thresholds are defined in §4.2.
- **Continuity facts** are the authoritative cross-chapter continuity source. The Visual Agent initializes `continuity_state` from the style bible at chapter start, but QC validates against series memory to catch facts that span beyond the style bible's scope (e.g., a temporary injury that persists across chapters).

---

## 8. Gate Registry

The Gate Registry is the single source of truth for what the QC Agent enforces. Any gate not in this registry is not enforced. Any new gate must be added to this registry before it takes effect. This prevents scope creep and silent policy additions.

### 8.1 Structural Gates (Level 1)

| Gate ID | Description | Severity | Auto-fixable? |
|---|---|---|---|
| `STRUCT.SCHEMA` | All artifacts match defined JSON schemas | BLOCKER | No |
| `STRUCT.PANEL_COVERAGE` | Every panel_id has entries in all downstream artifacts | BLOCKER | No |
| `STRUCT.VERSION_MATCH` | style_bible_version consistent across all artifacts | BLOCKER | No |
| `STRUCT.END_HOOK` | Final panel end_hook delivered verbatim in correct position | BLOCKER | No |

### 8.2 Visual Gates (Levels 1–3)

| Gate ID | Description | Severity | Auto-fixable? |
|---|---|---|---|
| `VISUAL.STYLE_TOKEN_PREFIX` | Style tokens complete and in order at prompt start | MAJOR | Yes (reorder) |
| `VISUAL.PROHIBITED_TERM_SCAN` | Zero prohibited terms in positive prompts | MAJOR | Yes (remove term) |
| `VISUAL.CAMERA_FIDELITY` | camera_prompt_term matches lexicon translation exactly | MAJOR | No |
| `VISUAL.CHARACTER_REF` | Named characters have LoRA/model_sheet reference | MAJOR | No |
| `VISUAL.CONTINUITY_CONSISTENCY` | Injuries/outfit/hair/props match continuity_state | MAJOR | No |
| `VISUAL.NO_NEW_MEANING` | 7-point violation scan passes (Visual Agent Spec §6) | MAJOR | No |
| `VISUAL.ASSET_REUSE` | All recurring elements use asset_id, not free-text | MAJOR | No |
| `VISUAL.TOKEN_BUDGET` | Positive ≤ 120 tokens, negative ≤ 60 tokens | MAJOR | Yes (trim per §3.4 overflow policy) |
| `VISUAL.DRIFT_DETECTION` | 10-panel interval drift within threshold | MAJOR | No |
| `VISUAL.ID_CONTRACT` | All references use registry IDs per Visual Identity Spec §10 | MAJOR | No |
| `VISUAL.FIVE_BEAT_STRUCTURE` | Silent sequences follow camera progression protocol | MAJOR | No |

### 8.3 Silence Gates (Levels 1–3)

| Gate ID | Description | Severity | Auto-fixable? |
|---|---|---|---|
| `SILENCE.PANEL_PURITY` | Silent panels: zero text in script, prompts, and lettering | BLOCKER | No |
| `SILENCE.PROMPT_PURITY` | silence_compliance panels: zero text terms in positive prompt, full prohibition list in negative | BLOCKER | Yes (add prohibitions to negative) |
| `SILENCE.GUARD_VISUAL` | silence_guard panels: core prohibition subset in negative prompt | MAJOR | Yes (add prohibitions) |
| `SILENCE.GUARD_LETTERING` | silence_guard panels: density reduction applied | MAJOR | No |
| `SILENCE.FIRST_AFTER` | First bubble after silence: smallest/lightest/shortest | MAJOR | No |
| `SILENCE.SFX_PROXIMITY` | SFX within 3 panels of silence: weight reduced per tier table | MAJOR | No |
| `SILENCE.RENDERED_PURITY` | Rendered silent panels: zero visible text/signage in image | BLOCKER | No |

### 8.4 Lettering Gates (Levels 1–2)

| Gate ID | Description | Severity | Auto-fixable? |
|---|---|---|---|
| `LETTER.VERBATIM_HASH` | SHA-256 hash match: script text ↔ lettering text | BLOCKER | No |
| `LETTER.NULL_SFX` | Script sfx=null → lettering sfx=null | MAJOR | Yes (remove invented SFX) |
| `LETTER.READING_ORDER` | Bubble reading_order sequential + correct direction | MAJOR | Yes (renumber) |
| `LETTER.PANEL_COVERAGE` | Every script panel has a lettering_spec entry | BLOCKER | No |
| `LETTER.CAPTION_BOUNDARY` | No unauthorized captions. Redundant captions flagged not removed. | MINOR | No |
| `LETTER.COMPOSITION` | No lettering overlaps exclusion zones or violates composition_notes | MAJOR | No |
| `LETTER.SHOUT_NEAR_SILENCE` | Shout bubbles near silence flagged for review | MINOR | No (flag only) |

### 8.5 Transmission Gates (Levels 2–3)

| Gate ID | Description | Severity | Auto-fixable? |
|---|---|---|---|
| `TRANSMISSION.SEMANTIC_DRIFT` | Carrier-beat panels not visually emphasized beyond adjacent panels | MINOR (default; escalates per §3.1) | No |
| `TRANSMISSION.CARRIER_LETTERING` | Carrier-beat panels not given largest/most text on page without justification | MINOR (default; escalates per §3.1) | No |
| `TRANSMISSION.MOTIF_CARRIER_ALIGN` | Motifs on carrier beats also appear elsewhere in chapter (not exclusive highlighting) | MINOR | No |
| `TRANSMISSION.CAPTION_LEAK` | No teaching language, wisdom paraphrase, or "lesson" phrasing in captions near carrier beats | MAJOR | No |
| `TRANSMISSION.METADATA_LEAK` | Zero internal_record fields (is_carrier_beat, somatic_intention) in any writer-facing artifact | BLOCKER | No |

---

## 9. Chapter Clearance Logic

The QC Agent applies the following decision tree after all gates have run:

```
1. Any BLOCKER issues remaining?
   → YES: BLOCKED. No exceptions. Return revision_queue.
   → NO: Continue.

2. Any MAJOR issues remaining?
   → YES: Are all MAJOR issues auto-fixed?
     → YES: Are all auto-fixes (lossless=true AND reversible=true
             AND requires_upstream_regen=false)?
       → YES: CLEARED_WITH_AUTO_FIXES. Log all fixes.
       → NO: BLOCKED. Auto-fix does not meet safety clause.
     → NO: BLOCKED. Return revision_queue with unfixed MAJORs.
   → NO: Continue.

3. Only MINOR issues remaining?
   → YES: CLEARED. Log minors for series memory.
   → NO (zero issues): CLEARED. Clean pass.
```

### 9.1 Clearance Output

```json
{
  "clearance": "CLEARED_WITH_AUTO_FIXES",
  "cleared_at": "ISO timestamp",
  "chapter": 9,
  "auto_fixes_applied": 2,
  "remaining_minors": 4,
  "series_memory_updated": true,
  "next_chapter_watch_list": [
    "VISUAL.CONTINUITY_CONSISTENCY — 2 occurrences across chapters 7-8, next triggers MAJOR",
    "TRANSMISSION.SEMANTIC_DRIFT — atom_family_3 flagged 2x, next triggers MAJOR"
  ]
}
```

---

## 10. QC Agent System Prompt

```
You are the QC Agent in a spiritual manga creation system.

Your role: final release authority for every chapter. You inspect all
upstream artifacts against all defined gates. You either clear a
chapter for release or block it with a structured revision queue.

You are not creative. You do not rewrite, redesign, or improve.
You enforce rules mechanically.

ABSOLUTE BOUNDARY:
You do not rewrite dialogue. You do not alter prompts. You do not
redesign lettering. You do not make aesthetic judgments. You do not
add narrative content. You do not override upstream agent authority.
You flag violations — owning agents fix them.

AUTO-FIX RULES:
You may apply auto-fixes ONLY if:
- lossless: true (no information discarded)
- reversible: true (can be undone without regen)
- requires_upstream_regen: false
Auto-fixes that fail any condition = escalation, not fix.

THREE-LEVEL DETECTION:
Level 1 — Structural (fastest): schema, coverage, version, verbatim
Level 2 — Cross-reference (medium): continuity, silence guard, no-new-meaning
Level 3 — Rendered output (slowest): drift, rendered purity, identity

SEVERITY:
BLOCKER — always blocks, never auto-fixable
MAJOR — blocks unless auto-fixed (with safety clause)
MINOR — logged, does not block

CLEARANCE:
- Zero blockers AND zero unresolved majors → CLEARED
- Auto-fixed majors pass ONLY if lossless + reversible + no regen
- Minors logged to series memory

TRANSMISSION CHECKS:
- You see internal_record (carrier beats, somatic intention)
- You check that carrier beats are NOT visually emphasized
- You NEVER expose internal metadata in revision_queue
- Issue descriptions use observable symptoms only

GATE REGISTRY:
If a gate is not in the registry, it is not enforced.
No silent policy additions.

SERIES MEMORY:
- Track continuity facts across chapters
- Track recurring issues with escalation counts
- Set forward expectations for state resolution
- Feed next_chapter_watch_list into next QC run

OUTPUT:
- revision_queue.json (issues + auto-fixes + clearance decision)
- series_memory_update.json (cross-chapter state)

chapter_script_handoff: {{ writer_handoff_json }}
chapter_script_internal: {{ internal_record_json }}
panel_prompts: {{ panel_prompts_json }}
lettering_spec: {{ lettering_spec_json }}
style_bible: {{ style_bible_json }}
style_bible_internal: {{ style_bible_internal_json }}
series_memory: {{ series_memory_json }}
rendered_pages: {{ rendered_pages_ref }}
```

---

## 11. Worked Example — Chapter 9 QC Run

### Input Summary

- 47 panels across 12 pages
- 3 silent pages (pages 4–6, 9 panels)
- 2 silence_guard panels (9-3-4, 9-3-5 before; 9-7-1, 9-7-2 after)
- 1 end-hook on final panel (9-12-4)
- 3 carrier beats (internal_record: panels 9-2-3, 9-7-2, 9-10-1)

### Level 1 Results

| Gate | Result | Issues |
|---|---|---|
| STRUCT.SCHEMA | PASS | — |
| STRUCT.PANEL_COVERAGE | PASS | — |
| STRUCT.VERSION_MATCH | PASS | — |
| STRUCT.END_HOOK | PASS | — |
| VISUAL.STYLE_TOKEN_PREFIX | FAIL (1 panel) | Panel 9-8-2: tokens out of order. Auto-fixed. |
| VISUAL.PROHIBITED_TERM_SCAN | FAIL (1 panel) | Panel 9-2-4: "illustration" in positive prompt. Auto-fixed. |
| All other L1 gates | PASS | — |

### Level 2 Results

| Gate | Result | Issues |
|---|---|---|
| VISUAL.CONTINUITY_CONSISTENCY | FAIL (1 panel) | Panel 9-5-3: bruised_knuckles_right missing from continuity_injections. Not auto-fixable — requires Visual Agent regen. |
| SILENCE.GUARD_LETTERING | PASS | — |
| SILENCE.FIRST_AFTER | PASS | — |
| SILENCE.SFX_PROXIMITY | FAIL (1 panel) | Panel 9-3-4: SFX weight "heavy" within 2 panels of silence, should be "medium". Not auto-fixable — requires Lettering Agent regen. |
| LETTER.CAPTION_BOUNDARY | PASS (1 flag) | Panel 9-2-4: caption_redundancy_flag raised. MINOR. |
| All other L2 gates | PASS | — |

### Level 3 Results

| Gate | Result | Issues |
|---|---|---|
| VISUAL.DRIFT_DETECTION | PASS | — |
| SILENCE.RENDERED_PURITY | PASS | — |
| TRANSMISSION.SEMANTIC_DRIFT | MINOR (1 panel) | Panel 9-7-2: contrast_ratio 0.62 vs adjacent avg 0.46. Flagged. series_memory_ref: atom_family_3, occurrence 3 → **AUTO-ESCALATED TO MAJOR** per §3.1(b). |

### Clearance Decision

```json
{
  "clearance": "BLOCKED",
  "reason": "2 MAJOR issues not auto-fixable + 1 auto-escalated MAJOR",
  "blocking_issues": [
    "VISUAL.CONTINUITY_CONSISTENCY panel 9-5-3 (Visual Agent)",
    "SILENCE.SFX_PROXIMITY panel 9-3-4 (Lettering Agent)",
    "TRANSMISSION.SEMANTIC_DRIFT panel 9-7-2 (Visual Agent — 3rd occurrence, auto-escalated)"
  ],
  "auto_fixes_applied": 2,
  "remaining_minors": 1
}
```

---

*SpiritualTech Systems · QC Agent Spec v1.1 · Confidential*
