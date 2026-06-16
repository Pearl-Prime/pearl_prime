# IMPLICIT THERAPEUTIC ENGINE — Dev Spec v1.0

**Last updated:** 2026-03-30
**Status:** Dev spec — pending review

> **Enforcement status (provenance, 2026-05-29):** the `vt_stealth` implicit/explicit-ratio gate (§12) is SPECIFIED here but NOT yet wired into the live authoring pipeline (this spec is pending review / implementation deferred). The genre-first / small-embedded-self-help proportion is currently enforced structurally by `specs/MANGA_STORY_ARCHITECT_SPEC.md` (carrier beats never first/last, embedded among 2–6 others; anti-preachy gates) + `specs/MANGA_TEACHING_LIBRARY_SPEC.md` (atom text withheld from the Chapter Writer). Source framework: `artifacts/research/therapeutic_embed_psychology_framework_2026-05-13.md`.
**Authority scope:** All visual (manga/illustrated), video, and music/soundtrack production pipelines
**Depends on:** `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `specs/MANGA_GENRE_AGENT_SPEC.md`, `config/quality/ei_v2_config.yaml`, `specs/PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.md`, `docs/assembly/SOMATIC_BOOK_BLUEPRINT.yaml`
**Research basis:** `research/2026-03-30_implicit-therapeutic-visual-media.md` (26 source clusters)
**Audience:** Pipeline engineers, visual agents, audio engineers, QC reviewers

---

## Table of Contents

- [§1 Purpose](#1-purpose)
- [§2 Core Principle: Stealth Therapy](#2-core-principle-stealth-therapy)
- [§3 Scope](#3-scope)
- [§4 Therapeutic Visual Grammar (Manga/Illustrated)](#4-therapeutic-visual-grammar-mangaillustrated)
- [§5 Panel Breath Engine](#5-panel-breath-engine)
- [§6 Color Temperature Arc System](#6-color-temperature-arc-system)
- [§7 Fractal Regulation Layer](#7-fractal-regulation-layer)
- [§8 Gutter Therapy System](#8-gutter-therapy-system)
- [§9 Character Arc as Sabido Transmission](#9-character-arc-as-sabido-transmission)
- [§10 Video Therapeutic Engine](#10-video-therapeutic-engine)
- [§11 Soundtrack Therapeutic Engine](#11-soundtrack-therapeutic-engine)
- [§12 EI v2 Integration — Visual Therapeutic Dimensions](#12-ei-v2-integration--visual-therapeutic-dimensions)
- [§13 Genre Agent Integration](#13-genre-agent-integration)
- [§14 Agent-Level Responsibilities](#14-agent-level-responsibilities)
- [§15 QC Gates](#15-qc-gates)
- [§16 Artifact Schema](#16-artifact-schema)
- [§17 CI Enforcement](#17-ci-enforcement)
- [§18 Acceptance Criteria](#18-acceptance-criteria)
- [§19 Non-Goals](#19-non-goals)
- [Appendix A: Research Evidence Map](#appendix-a-research-evidence-map)
- [Appendix B: Pentatonic Mode Reference](#appendix-b-pentatonic-mode-reference)
- [Appendix C: Fractal Dimension Visual Reference](#appendix-c-fractal-dimension-visual-reference)

---

## §1 Purpose

Phoenix Omega's audiobook pipeline already embeds therapeutic mechanisms through arc-first structure, somatic exercises, and recognition-first hooks. The visual (manga/illustrated), video, and music pipelines lack an equivalent system.

This spec defines the **Implicit Therapeutic Engine (ITE)** — a set of production rules, scoring dimensions, and QC gates that embed measurable somatic and psychological therapeutic value into visual, video, and audio content **without any explicit therapy labeling**.

The listener/reader/viewer experiences entertainment. The nervous system experiences regulation.

---

## §2 Core Principle: Stealth Therapy

**The word "therapy" is never used in any consumer-facing output.** Research confirms profoundly negative associations with the label (Taylor & Francis, 2019). Therapeutic mechanisms work better when invisible.

Three rules govern all ITE decisions:

1. **Entertainment-first.** The primary experience is genre entertainment (shonen, iyashikei, romance, horror, etc.). Therapeutic mechanisms are structural, not topical.
2. **Implicit-only.** No didactic wellness language. No breathing instructions in dialogue. No "this will help your anxiety." The reader/viewer/listener never knows.
3. **Measurable.** Every mechanism maps to a physiological pathway with cited research. No vague "feels calming." Specific: panel progression → breathing entrainment → parasympathetic activation → HRV improvement.

### What This Means in Practice

| ✗ Explicit (forbidden) | ✓ Implicit (required) |
|---|---|
| Character says "take a deep breath" | Panel sizes progressively enlarge, reader's breathing slows naturally |
| Chapter titled "Managing Anxiety" | Color palette shifts warm→cool across chapter arc |
| Narrator explains nervous system | Nature fractal backgrounds (FD 1.3-1.5) in resolution scenes activate parasympathetic response |
| Soundtrack labeled "meditation music" | Pentatonic melodies at 66 BPM with 10-second phrases entrain vagal rhythm |
| Video caption: "breathing exercise" | Camera pans at 6 cycles/min; viewer's respiration entrains to visual rhythm |

---

## §3 Scope

### In scope

- Manga panel layout therapeutic grammar (all 10 genres in Genre Agent)
- Color temperature arc system for illustrated content
- Fractal regulation layer for backgrounds/environments
- Gutter width system for emotional processing
- Panel Breath Engine (breathing cue embedding)
- Video camera movement and edit rhythm therapeutic specs
- Soundtrack/music therapeutic production rules
- EI v2 new dimensions for visual/audio therapeutic scoring
- Genre Agent `somatic_targets` expansion
- QC gates for therapeutic compliance
- CI scripts for automated validation

### Explicitly out of scope

- Audiobook text-only pipeline (already governed by `PHOENIX_V4_5_WRITER_SPEC_TTS_v1.3.md` and `SOMATIC_BOOK_BLUEPRINT.yaml`)
- Consumer-facing marketing copy or metadata (no therapeutic claims)
- Clinical outcome measurement or medical claims
- Explicit therapy or wellness labeling of any kind
- VR/AR content (future spec)
- Interactive/game-based content (future spec)

---

## §4 Therapeutic Visual Grammar (Manga/Illustrated)

The Therapeutic Visual Grammar (TVG) defines panel-level production rules that map layout techniques to somatic target states. Every page in the manga pipeline passes through TVG validation.

### §4.1 Panel-State Mapping (Master Table)

| Somatic Target | Panel Technique | Metric | Gate |
|---|---|---|---|
| Parasympathetic activation | Wide borderless bleed panel + nature/fractal BG (FD 1.3–1.5) | ≥1 per chapter in resolution section | WARN |
| Breathing deceleration | Progressive panel enlargement across row (small→med→large) | ≥1 breath sequence per chapter (see §5) | WARN |
| Emotional processing | Widened gutters (≥2x standard width) after high-intensity panels | Gutter width ratio ≥2.0 after any band-4+ panel | BLOCKER |
| Grounding / present-moment | Detailed nature panel with mid-complexity fractals | ≥1 per chapter in integration/resolution slots | WARN |
| Arousal reduction | Cool-palette dominance in resolution panels (see §6) | Color temp ≤4500K equivalent in final 20% of chapter | WARN |
| Bilateral engagement | Panel alternation requiring L→R eye sweep across spread | ≥60% of spreads use asymmetric panel layout | INFO |
| Flow state / absorption | Kishotenketsu page rhythm (intro→development→twist→conclusion) | Page-level 4-beat rhythm score ≥0.6 | INFO |

### §4.2 Panel Size-Emotion Mapping

Panel area as percentage of page correlates with reader dwell time and emotional weight:

| Panel Size (% of page) | Reader Effect | Use For |
|---|---|---|
| 5–15% (small) | Quick read, acceleration, tension | Action beats, rapid sequence, sympathetic activation |
| 15–30% (medium) | Normal reading pace, narrative flow | Dialogue, exposition, story progression |
| 30–50% (large) | Slowed reading, emphasis, weight | Emotional beats, turning points, recognition moments |
| 50–75% (splash) | Full pause, absorption, processing | Resolution, beauty, parasympathetic activation |
| 75–100% (full bleed) | Timelessness, transcendence, breath | Chapter openers/closers, peak moments, integration |

**Rule:** No chapter may have >60% small panels (creates reader fatigue). No chapter may have >40% splash/bleed panels (dilutes impact).

---

## §5 Panel Breath Engine

The Panel Breath Engine (PBE) embeds breathing cues into panel layout rhythm. The reader's breathing naturally adjusts to follow visual flow without any conscious awareness or instruction.

### §5.1 Breath Sequence Definition

A **breath sequence** is a contiguous set of panels across 1–2 rows that implicitly walks the reader through an inhale-hold-exhale-pause cycle:

```
INHALE  → 3–4 panels, progressively increasing size
           Visual content: opening spaces, rising imagery, expanding forms
           Color: warming slightly

HOLD    → 1 wide panel (≥40% page width), stable detailed scenery
           Visual content: nature, architecture, horizon, fractal patterns (FD 1.3–1.5)
           Color: warm-neutral, high brightness
           Reader naturally dwells here (measured: 2.1x dwell time vs medium panels)

EXHALE  → 2–3 panels, progressively decreasing size OR single quiet panel
           Visual content: settling imagery (leaves falling, water calming, breath visible)
           Color: cooling, desaturating

PAUSE   → Wide horizontal gutter (≥3x standard gutter width)
           Reader's eye rests. Corresponds to breathing pause before next cycle.
```

### §5.2 Breath Sequence Placement Rules

| Chapter Section | Breath Sequences Required | Placement |
|---|---|---|
| Opening (first 15% of pages) | 0 | Not required — genre pacing takes priority |
| Conflict/tension (15–60%) | 0–1 | Optional. Place after peak intensity panel if present. |
| Turning point (60–75%) | 1 | Required. Immediately following the turning point beat. |
| Resolution/integration (75–100%) | 1–2 | Required. At least 1 in final quarter. |

**Minimum per chapter:** 1 breath sequence
**Maximum per chapter:** 4 breath sequences (more = pacing drag)
**Genre override:** Iyashikei chapters may have up to 6 breath sequences. Horror chapters may defer to 1 (placed in resolution only).

### §5.3 Breath Sequence Target Rate

The ideal breath sequence maps to approximately **6 breaths per minute** (resonance breathing rate), matching the rhythm that produces maximal HRV improvement:

- Inhale phase: ~4 seconds reader dwell (3–4 small→medium panels)
- Hold phase: ~7 seconds reader dwell (1 wide panel with detail)
- Exhale phase: ~5 seconds reader dwell (2–3 panels decreasing)
- Pause: ~2 seconds (wide gutter)

Total cycle: ~18 seconds. Reader processes ~3.3 breath sequences per minute of reading time. The ratio is intentionally slower than real-time resonance breathing to account for variable reading speeds — the goal is directional slowing, not precise BPM entrainment.

### §5.4 PBE Artifact Schema

The Visual Agent emits a `breath_map` field in `panel_prompts.json`:

```json
{
  "breath_sequences": [
    {
      "page_range": [14, 15],
      "phase_panels": {
        "inhale": ["p14_panel_3", "p14_panel_4", "p14_panel_5"],
        "hold": ["p15_panel_1"],
        "exhale": ["p15_panel_2", "p15_panel_3"],
        "pause_gutter": {"after_panel": "p15_panel_3", "width_multiplier": 3.0}
      },
      "target_state": "parasympathetic_activation",
      "chapter_section": "resolution"
    }
  ]
}
```

---

## §6 Color Temperature Arc System

Color temperature shifts across a chapter arc mirror the somatic regulation journey. The reader's autonomic nervous system responds to palette transitions without conscious processing.

### §6.1 Five-Phase Color Arc

Every chapter follows a 5-phase color temperature arc mapped to its emotional role in the book:

| Phase | Chapter % | Palette | Color Temp Equiv | Saturation | Somatic Effect |
|---|---|---|---|---|---|
| 1 — Hook | 0–10% | Moderate warm (orange-amber) | 3500–4500K | Medium (50–65%) | Engagement without overwhelm |
| 2 — Tension | 10–50% | High warm, red accents | 2500–3500K | High (65–80%) | Sympathetic activation mirrors character state |
| 3 — Turn | 50–65% | Mixed warm-cool, purple/violet | 4500–5500K | Medium (45–60%) | Introspection, processing |
| 4 — Resolution | 65–85% | Cool (blue-green) | 5500–7000K | Low-medium (35–55%) | Parasympathetic activation |
| 5 — Afterglow | 85–100% | Warm-soft (golden hour) | 4000–5000K | Low (30–45%) | Safety, contentment, completion |

### §6.2 Color Arc Enforcement

**WARN gate:** Phase 4 (resolution) must have mean color temperature ≥5500K equivalent AND mean saturation ≤55%. Violation indicates resolution scenes are still in high-arousal palette.

**WARN gate:** Phase 2→4 must show monotonically decreasing saturation (±5% tolerance). Non-monotonic saturation in the resolution arc breaks the regulation progression.

**INFO gate:** Phase 5 saturation should be lower than Phase 1. The chapter ends calmer than it began.

### §6.3 Genre-Specific Overrides

| Genre | Override | Reason |
|---|---|---|
| Horror | Phase 4 may retain cool-dark (low brightness, 15–25%) | Horror resolution is stillness-in-dark, not warmth |
| Iyashikei | All phases shift +1000K warmer, saturation floor 20% | Entire genre operates in parasympathetic-dominant palette |
| Shonen | Phase 2 saturation cap 85% (not 80%) | Higher energy genre needs more arousal headroom |
| Seinen | Phase 3 extended to 50–75% of chapter | Longer introspection arc matches genre pacing |

### §6.4 Color Arc Artifact

The Visual Identity Agent emits `color_arc` in `style_bible.json`:

```json
{
  "color_arc": {
    "phases": [
      {"name": "hook", "pct_range": [0, 10], "temp_range_k": [3500, 4500], "sat_range_pct": [50, 65]},
      {"name": "tension", "pct_range": [10, 50], "temp_range_k": [2500, 3500], "sat_range_pct": [65, 80]},
      {"name": "turn", "pct_range": [50, 65], "temp_range_k": [4500, 5500], "sat_range_pct": [45, 60]},
      {"name": "resolution", "pct_range": [65, 85], "temp_range_k": [5500, 7000], "sat_range_pct": [35, 55]},
      {"name": "afterglow", "pct_range": [85, 100], "temp_range_k": [4000, 5000], "sat_range_pct": [30, 45]}
    ],
    "genre_override": null
  }
}
```

---

## §7 Fractal Regulation Layer

Natural fractal patterns at specific complexity levels activate parasympathetic response and reduce stress by up to 60% (Taylor, UOregon). This layer defines when and how fractal imagery appears in backgrounds.

### §7.1 Fractal Dimension Targets

| Fractal Dimension (FD) | Visual Character | Somatic Effect | Use In |
|---|---|---|---|
| 1.1–1.2 (low) | Sparse, minimal (bare branches, simple waves) | Mild calming, emptiness | Horror silence panels, minimalist scenes |
| 1.3–1.5 (mid) | Rich natural complexity (forest canopy, clouds, flowing water) | **Maximum stress reduction** (peak response) | Resolution panels, hold panels in breath sequences, integration scenes |
| 1.6–1.8 (high) | Dense, busy (urban detail, mechanical patterns) | Stimulating, arousing | Tension scenes, urban environments, conflict |

### §7.2 Fractal Placement Rules

| Chapter Section | Target FD Range | Minimum Coverage |
|---|---|---|
| Hook panels | 1.4–1.6 (moderate, engaging) | Optional |
| Tension panels | 1.5–1.8 (complex, stimulating) | Optional |
| Hold panels (breath sequence) | **1.3–1.5 (mid, peak calming)** | Required in all hold panels |
| Resolution panels | 1.2–1.5 (calming) | ≥50% of resolution BG area |
| Afterglow panels | 1.3–1.5 (mid) | ≥1 full-bleed nature panel |

### §7.3 Fractal Source Categories

Approved fractal sources for backgrounds (all naturally occurring patterns):

| Category | Examples | Typical FD |
|---|---|---|
| Arboreal | Tree canopies, branching patterns, root systems | 1.3–1.5 |
| Aquatic | Rivers, ocean waves, rain on water, waterfalls | 1.3–1.6 |
| Atmospheric | Cloud formations, mist, aurora, sunset gradients | 1.2–1.4 |
| Geological | Mountain ridgelines, rock formations, sand dunes | 1.3–1.5 |
| Botanical | Flower clusters, leaf venation, garden scenes | 1.4–1.6 |
| Cosmic | Star fields, nebulae, galaxy spirals | 1.3–1.5 |

**Forbidden:** Artificial grid patterns, pure geometric tiling, digital noise, glitch effects — these have FD outside therapeutic range and produce discomfort, not regulation.

### §7.4 Visual Agent Prompt Integration

The Visual Agent appends fractal specifications to panel prompts for background-heavy panels:

```
positive_prompt: "... forest canopy with dappled light, natural branching patterns,
  mid-complexity organic detail, soft depth of field"
negative_prompt: "... geometric grid, digital noise, artificial pattern,
  repeating tile, mechanical texture"
```

The `panel_prompts.json` carries a `fractal_target` field:

```json
{
  "panel_id": "p15_panel_1",
  "fractal_target": {
    "fd_range": [1.3, 1.5],
    "source_category": "arboreal",
    "coverage_pct": 80,
    "therapeutic_role": "breath_hold"
  }
}
```

---

## §8 Gutter Therapy System

The gutter (space between panels) is where the reader does emotional processing work. Wider gutters create liminal space; the reader's mind fills the gap unconsciously.

### §8.1 Gutter Width Classes

| Class | Width (relative to standard) | Function | Use After |
|---|---|---|---|
| **tight** | 0.5x | Acceleration, urgency, connected action | Action sequences, rapid dialogue |
| **standard** | 1.0x | Normal narrative flow | Default for all panels |
| **processing** | 2.0x | Emotional digestion space | Band-3 emotional panels, story beats |
| **therapeutic** | 3.0x | Deep processing, implicit pause | Band-4+ panels, post-climax, post-revelation |
| **breath** | 4.0x (horizontal only) | Breathing pause, chapter rhythm reset | End of breath sequence exhale phase (§5.1) |

### §8.2 Mandatory Gutter Rules

| Rule | Gate Level |
|---|---|
| After any band-4+ emotional panel: gutter ≥ `processing` (2.0x) | BLOCKER |
| After any band-5 panel: gutter ≥ `therapeutic` (3.0x) | BLOCKER |
| Between breath sequence and next narrative panel: gutter = `breath` (4.0x) | WARN |
| No `tight` gutters in resolution section (final 25% of chapter) | WARN |
| Maximum 5 consecutive `tight` gutters (prevents reader hyperventilation) | BLOCKER |

### §8.3 Lettering Agent Compliance

The Lettering Agent enforces: **no text elements within therapeutic or breath gutters.** Sound effects, captions, and dialogue bubbles must not bridge or overlap gutters of class `therapeutic` or `breath`. These gutters are sacred processing space.

---

## §9 Character Arc as Sabido Transmission

The Sabido Entertainment-Education methodology (proven across 50+ years of media interventions) provides the character-level framework for implicit therapeutic transmission. This integrates with the existing Transmission Splitter and Teaching Library.

### §9.1 Three Character Roles

Every manga series maps its cast to Sabido roles:

| Role | Function | Therapeutic Mechanism | Mapping to Existing System |
|---|---|---|---|
| **Positive model** | Demonstrates regulation behaviors (breathing, grounding, boundary-setting) through action, never instruction | Social learning theory — viewer mirrors modeled behavior | Maps to Genre Agent `villain_spec.integration_teaching` (inverted: the protagonist IS the teaching) |
| **Negative model** | Shows dysregulation cost through consequences, not lectures | Viewer recognizes own patterns without being told | Maps to `villain_spec.shadow_mapping` |
| **Transitional character** | Represents the audience; uncertain, learns alongside reader; shows realistic struggle | Reader identifies; changes attitude when character changes | New field: `sabido_transitional` in `genre_blueprint.json` |

### §9.2 Sabido Integration Rules

1. **The positive model never explains** what they're doing or why. They just do it. A character who sits quietly by a river after conflict is modeling regulation. A character who says "I'm practicing grounding" is breaking stealth.

2. **The transitional character's arc mirrors the reader's.** Their skepticism, resistance, and eventual shift must feel organic to the genre — not a therapy journey dressed in plot armor.

3. **The negative model's consequences are natural**, not moralistic. Dysregulation leads to relationship loss, missed opportunities, or physical cost — shown through story, never narrated as lesson.

4. **No character references therapy, counseling, meditation, mindfulness, or wellness by name.** These words do not exist in the story world unless the genre is explicitly set in a clinical context.

### §9.3 Genre Agent Output Extension

Add to `genre_blueprint.json`:

```json
{
  "sabido_map": {
    "positive_model": {
      "character_role": "protagonist",
      "regulation_behaviors": ["breath_pause_before_action", "nature_seeking", "silence_choosing"],
      "modeling_method": "action_only",
      "dialogue_prohibition": ["therapy", "mindfulness", "grounding", "regulation", "breathing exercise"]
    },
    "negative_model": {
      "character_role": "antagonist_or_rival",
      "dysregulation_behaviors": ["escalation_without_pause", "isolation_from_nature", "noise_seeking"],
      "consequence_method": "natural_narrative"
    },
    "transitional": {
      "character_role": "companion_or_deuteragonist",
      "arc_phases": ["skepticism", "observation", "tentative_trial", "integration"],
      "reader_identification_score_target": 0.75
    }
  }
}
```

---

## §10 Video Therapeutic Engine

Video content (book trailers, social clips, promotional videos, companion video series) carries therapeutic mechanisms through camera, editing rhythm, and visual composition.

### §10.1 Camera Movement Prescription

Viewers psycho-physiologically simulate camera movement (Frontiers in Neuroscience, 2023). Camera movement = direct nervous system control.

| Camera Technique | Viewer Physiological Effect | Use In |
|---|---|---|
| Slow steady pan (≤5°/sec) | Parasympathetic activation, breathing slows | Resolution scenes, nature establishing shots |
| Slow tracking forward | Immersion, presence, gentle approach | Character introduction, environment entry |
| Static wide shot (≥5 sec hold) | Stillness, contemplation, viewer breathes | Integration moments, beauty beats |
| Slow dolly out | Release, perspective, completion | Chapter/section endings |
| Handheld (mild sway) | Intimacy, embodiment, mild arousal | Emotional dialogue, conflict build |
| Rapid cuts (<2 sec) | Sympathetic activation, tension | Action sequences only. Cap: 15 seconds continuous. |

### §10.2 Edit Rhythm Entrainment

Scene cuts at specific rhythms entrain viewer respiration:

| Target State | Cut Rhythm | BPM Equivalent | Max Duration |
|---|---|---|---|
| Sympathetic activation | 1 cut per 1.5–2.5 sec | 24–40 BPM | 15 sec continuous |
| Neutral engagement | 1 cut per 4–6 sec | 10–15 BPM | No limit |
| Parasympathetic activation | 1 cut per 8–12 sec | 5–7.5 BPM | No limit |
| Deep regulation | Unbroken shot ≥15 sec | <4 BPM | 60 sec (avoid viewer disengagement) |

**Resonance rhythm target:** Edit pattern cycling at ~6 complete tension-release cycles per minute aligns with resonance breathing and maximizes HRV improvement.

### §10.3 Video Structure Template

Every video ≥60 seconds follows this therapeutic arc structure:

```
0–15%    HOOK       Fast/medium cuts. Engagement. Mild sympathetic activation.
15–55%   BUILD      Medium cuts. Narrative progression. Gradual slowing.
55–70%   PEAK       Slowest cuts or single long take. Full emotional weight.
70–85%   RELEASE    Slow pans, nature footage, wide shots. Parasympathetic.
85–100%  RESOLVE    Static or slow dolly-out. Longest unbroken shot. Silence.
```

**Rule:** The final 15% of any video must contain the slowest average cut rhythm in the entire piece. No video ends on high-arousal pacing.

### §10.4 Nature Footage Requirements

Based on the meta-analysis of 31 studies: 5 minutes of nature viewing produces the greatest mood improvement.

| Video Length | Nature Footage Minimum | Placement |
|---|---|---|
| <60 sec | 5 sec | Final 15% |
| 60–180 sec | 15 sec | Release + resolve sections |
| 180–600 sec | 45 sec | ≥2 nature inserts + resolve |
| >600 sec | 90 sec (1.5 min) | ≥3 distributed + extended resolve |

**Nature footage definition:** Landscapes, water, sky, trees, natural light. Must contain fractal patterns (FD 1.3–1.5). No urban, industrial, or artificial environments qualify.

---

## §11 Soundtrack Therapeutic Engine

Music and audio design carry therapeutic mechanisms through tempo, scale, interval, silence, and texture. Every soundtrack element maps to a physiological target.

### §11.1 Master Soundtrack Specification

| Parameter | Specification | Evidence | Gate |
|---|---|---|---|
| **Tuning** | A4 = 432 Hz (preferred) or 440 Hz (acceptable) | Calamassi 2019: -4.79 BPM heart rate at 432 Hz | INFO |
| **Scale** | Pentatonic-dominant melodies. Western major/minor for tension sections only. | Frontiers in Psychology 2024: pentatonic reduces sympathetic activity | WARN if >50% of calming sections use non-pentatonic |
| **Tempo (calming)** | 60–72 BPM | Matches 6 breath cycles/min resonance target | WARN if calming section >78 BPM |
| **Tempo (tension)** | 80–120 BPM | Controlled sympathetic activation | WARN if >130 BPM sustained >30 sec |
| **Phrase length** | 10-second musical phrases in calming sections | Matches Mayer wave rhythm → vagal slowing | INFO |
| **Strategic silence** | ≥1 silence period (8–15 sec) per 5 min of content | Bernardi: silence drops HR/BP below baseline | WARN |
| **Texture** | Instrumental only. No lyrics in calming sections. | Lyrics hinder verbal memory + processing | BLOCKER if lyrics in resolution section |
| **Dynamic range** | ≥12 dB between loudest and softest passage | Prevents listener fatigue; mirrors breathing dynamic | WARN |

### §11.2 Tempo Arc (Soundtrack Structure)

The soundtrack tempo arc parallels the video/chapter structure:

```
HOOK        80–100 BPM    Medium energy. Engagement.
BUILD       72–90 BPM     Gradual deceleration toward peak.
PEAK        60–72 BPM     Slowest tempo. Maximum emotional weight. 10-sec phrases.
SILENCE     0 BPM         8–15 sec. Heart rate drops below baseline.
RELEASE     60–66 BPM     Pentatonic melody. Gentle. Sustained tones.
RESOLVE     54–66 BPM     Fade to ambient texture or silence. Longest held note.
```

### §11.3 Therapeutic Audio Layers

These layers may be embedded in the soundtrack mix at low amplitude (≤-18 dB relative to primary melody):

| Layer | Specification | Evidence | Notes |
|---|---|---|---|
| **Isochronic tones** | 6–10 Hz, depth ≤-18 dB | SciELO 2021: effective in 82% of studies | Optional. Alpha/theta entrainment. No headphones required. |
| **Sub-bass resonance** | 30–40 Hz sustained pad | Felt more than heard. Body vibration awareness. | Optional. Somatic grounding. |
| **Vocal drone** | Sustained humming tone (fundamental + 5th) | Vagal stimulation via vocalization research | Optional. Place in resolution sections only. |

**Consent rule:** Isochronic tones and sub-bass layers are opt-in at the production level (configured in `soundtrack_config.yaml`). They are never mandatory. If regulatory review raises concerns, these layers can be disabled globally without affecting primary content.

### §11.4 Silence as Therapeutic Instrument

Research (Bernardi): 2-minute silence periods between music sections dropped all cardiovascular measures **below baseline** — silence was more regulatory than the music itself.

**Silence placement rules:**

| Context | Minimum Silence | Maximum Silence |
|---|---|---|
| After peak emotional scene | 8 sec | 20 sec |
| Between chapters/sections | 5 sec | 15 sec |
| Video resolve section | Final 3–5 sec must be silence or near-silence (≤-30 dB) | — |
| Manga companion audio | 3 sec between page transitions | 10 sec |

**Rule:** No video or audio content may end on a musical crescendo. All content ends on decrescendo, sustained tone, or silence.

---

## §12 EI v2 Integration — Visual Therapeutic Dimensions

Four new EI v2 scoring dimensions extend the existing 6-module system for visual and audio content.

### §12.1 New Dimensions

Add to `config/quality/ei_v2_config.yaml` under a new `visual_therapeutic` module group:

| Dimension | ID | Range | Weight | Threshold (WARN) | Threshold (FAIL) |
|---|---|---|---|---|---|
| Parasympathetic Activation Potential | `vt_parasympathetic` | 0.0–1.0 | 0.30 | <0.40 | <0.20 |
| Emotional Processing Scaffolding | `vt_processing` | 0.0–1.0 | 0.25 | <0.35 | <0.15 |
| Somatic Regulation Cues | `vt_somatic` | 0.0–1.0 | 0.25 | <0.35 | <0.15 |
| Implicit-Explicit Ratio | `vt_stealth` | 0.0–1.0 | 0.20 | <0.70 | <0.50 |

### §12.2 Scoring Inputs

**`vt_parasympathetic`** (0.0–1.0):
- Fractal imagery density in resolution panels (FD 1.3–1.5 coverage %)
- Cool palette presence in final 25% of chapter (color temp ≥5500K %)
- Wide panel / breathing space ratio (splash + bleed panels / total panels)
- Breath sequence count (§5) normalized to chapter length
- Music tempo in calming sections (deviation from 66 BPM target)

**`vt_processing`** (0.0–1.0):
- Gutter width compliance (processing/therapeutic gutters after high-band panels)
- Sabido character mapping completeness (3 roles assigned)
- Story beats aligned with identification→catharsis→insight→universalization sequence
- Dual hemisphere engagement (text-image integration density per page)

**`vt_somatic`** (0.0–1.0):
- Breath sequence structural validity (inhale→hold→exhale→pause complete)
- Color temperature arc monotonicity in resolution section
- Fractal background presence in hold panels
- Soundtrack tempo arc compliance
- Strategic silence placement compliance

**`vt_stealth`** (0.0–1.0):
- Inverse scoring: higher = more implicit
- Scan dialogue for forbidden terms: therapy, mindfulness, grounding, breathing exercise, meditation, wellness, self-care, healing journey, inner peace, mental health (per §9.2)
- Scan captions/titles for wellness framing
- Check: no character instructs another to breathe/relax/ground
- Check: no narrator/caption explains therapeutic mechanism

**Formula:** `vt_stealth = 1.0 - (explicit_term_count / total_dialogue_tokens) * penalty_weight`
Where `penalty_weight = 100` (even one explicit term severely degrades score).

### §12.3 Composite Score

```
ITE_score = (vt_parasympathetic × 0.30) + (vt_processing × 0.25) +
            (vt_somatic × 0.25) + (vt_stealth × 0.20)
```

**Pass threshold:** ITE_score ≥ 0.50
**Target:** ITE_score ≥ 0.70

### §12.4 Config YAML Extension

```yaml
visual_therapeutic:
  enabled: true
  mode: heuristic
  dimensions:
    vt_parasympathetic:
      weight: 0.30
      warn_below: 0.40
      fail_below: 0.20
      inputs: [fractal_density, cool_palette_ratio, breath_sequence_count, panel_size_ratio]
    vt_processing:
      weight: 0.25
      warn_below: 0.35
      fail_below: 0.15
      inputs: [gutter_compliance, sabido_completeness, beat_sequence_alignment]
    vt_somatic:
      weight: 0.25
      warn_below: 0.35
      fail_below: 0.15
      inputs: [breath_validity, color_arc_monotonicity, fractal_hold_presence, tempo_compliance, silence_compliance]
    vt_stealth:
      weight: 0.20
      warn_below: 0.70
      fail_below: 0.50
      forbidden_terms: [therapy, mindfulness, grounding, breathing exercise, meditation, wellness, self-care, healing journey, inner peace, mental health, calm down, relax your body, take a breath]
      penalty_weight: 100
  composite:
    pass_threshold: 0.50
    target: 0.70
```

---

## §13 Genre Agent Integration

The Genre Agent's existing `somatic_targets` field (§5 of `MANGA_GENRE_AGENT_SPEC.md`) is extended with ITE-specific targets.

### §13.1 Extended somatic_targets Schema

Add these fields to the Genre Agent's 6 existing somatic target types:

```yaml
somatic_targets:
  # Existing targets (unchanged)
  breath_rhythm: { ... }
  panel_silence: { ... }
  character_choice: { ... }
  emotional_vulnerability: { ... }
  ritual_repetition: { ... }
  structural_decay: { ... }

  # NEW: ITE targets
  fractal_regulation:
    min_hold_panels_per_chapter: 1
    fd_range: [1.3, 1.5]
    source_categories: ["arboreal", "aquatic", "atmospheric"]
    placement: "resolution_and_integration"

  color_arc:
    profile: "standard"  # or genre override key
    resolution_temp_min_k: 5500
    resolution_sat_max_pct: 55
    afterglow_sat_max_pct: 45

  breath_sequences:
    min_per_chapter: 1
    max_per_chapter: 4
    required_in_sections: ["resolution"]
    optional_in_sections: ["turning_point"]

  gutter_therapy:
    post_band4_min_class: "processing"
    post_band5_min_class: "therapeutic"
    resolution_tight_forbidden: true

  sabido_roles:
    require_positive_model: true
    require_transitional: true
    dialogue_prohibition_enforced: true

  soundtrack:
    calming_tempo_range_bpm: [60, 72]
    tension_tempo_max_bpm: 120
    scale_preference: "pentatonic"
    min_silence_per_5min_sec: 8
```

### §13.2 Genre-Specific ITE Profiles

| Genre | Breath Seq/Ch | Fractal Density | Color Arc Profile | Silence Budget Overlap | Soundtrack Tempo Floor |
|---|---|---|---|---|---|
| Shonen | 1 | Low (resolution only) | standard | Shared with combat silence | 72 BPM |
| Seinen | 2 | Medium | extended_turn | Additive to existing 35–45% | 60 BPM |
| Shojo | 2 | Medium | standard | Shared with romantic silence | 66 BPM |
| Sports | 1 | Low | standard | Post-match only | 72 BPM |
| Horror | 1 (resolution only) | Low-dark | horror_override | Shared with dread silence | 54 BPM |
| **Iyashikei** | **4–6** | **High (all sections)** | **warm_shift** | **Additive (60–70% total)** | **54 BPM** |
| Cultivation | 2 | Medium | standard | Shared with cultivation silence | 60 BPM |
| Manhwa | 2 | Medium | standard | Additive to existing 35–45% | 60 BPM |
| Webtoon Romance | 1–2 | Medium | standard | Shared with longing silence | 66 BPM |
| Isekai | 1–2 | Medium (new-world scenes) | standard | Shared with wonder silence | 66 BPM |

---

## §14 Agent-Level Responsibilities

### §14.1 Visual Identity Agent

**New outputs added to `style_bible.json`:**

| Field | Type | Description |
|---|---|---|
| `color_arc` | object | 5-phase color temperature arc with genre overrides (§6.4) |
| `fractal_palette` | object | Approved fractal source categories, FD ranges per chapter section |
| `gutter_classes` | object | Width multipliers for 5 gutter classes (§8.1) |
| `breath_visual_grammar` | object | Panel size progression rules for inhale/hold/exhale/pause |

### §14.2 Genre Agent

**New outputs added to `genre_blueprint.json`:**

| Field | Type | Description |
|---|---|---|
| `sabido_map` | object | Three-role character mapping (§9.3) |
| `somatic_targets.fractal_regulation` | object | Per-genre fractal specs |
| `somatic_targets.color_arc` | object | Per-genre color arc profile |
| `somatic_targets.breath_sequences` | object | Per-genre breath sequence rules |
| `somatic_targets.gutter_therapy` | object | Per-genre gutter class rules |
| `somatic_targets.soundtrack` | object | Per-genre soundtrack parameters |

### §14.3 Story Architect

**Extended responsibility:**
- Allocate breath sequence page positions in `story_architecture.json` (alongside existing silence_map allocations)
- Map Sabido transitional character arc phases to chapter beats
- Ensure color arc turning point aligns with narrative turning point (±1 chapter tolerance)

### §14.4 Chapter Writer Agent

**Extended responsibility:**
- Tag panels with `emotional_band` (existing) — ITE uses this for gutter class determination
- Mark panels intended as breath sequence components with `breath_role: inhale|hold|exhale`
- Enforce Sabido dialogue prohibition: no forbidden terms in any character dialogue or caption

### §14.5 Visual Agent

**Extended responsibility:**
- Emit `fractal_target` per panel (§7.4)
- Emit `breath_map` per chapter (§5.4)
- Apply color temperature targets from `color_arc` to panel prompts
- Include fractal source keywords in positive prompts and anti-fractal keywords in negative prompts for therapeutic panels

### §14.6 Lettering Agent

**Extended responsibility:**
- Enforce no text in `therapeutic` or `breath` class gutters (§8.3)
- Validate `silence_confirmed: true` panels have no overlapping text into adjacent therapeutic gutters

### §14.7 Layout Agent

**Extended responsibility:**
- Render gutter widths per class specification
- Validate panel size progression in breath sequences (monotonic increase for inhale, decrease for exhale)
- Ensure breath sequence hold panels are ≥40% page width

### §14.8 QC Agent

**Extended responsibility:** See §15.

---

## §15 QC Gates

New gates added to the existing 30-gate registry. All ITE gates are in a new category: **therapeutic**.

### §15.1 BLOCKER Gates

| Gate ID | Check | Fails If |
|---|---|---|
| T-01 | Post-band-4 gutter class | Gutter after band-4+ panel < `processing` (2.0x) |
| T-02 | Post-band-5 gutter class | Gutter after band-5 panel < `therapeutic` (3.0x) |
| T-03 | Consecutive tight gutters | >5 consecutive `tight` gutters anywhere in chapter |
| T-04 | Stealth vocabulary scan | Any forbidden term (§12.2 `vt_stealth` list) in character dialogue |
| T-05 | Resolution lyrics check | Lyrics present in soundtrack during resolution section |
| T-06 | Video ending arousal | Video ends on cut rhythm <4 sec (high arousal) |

### §15.2 WARN Gates

| Gate ID | Check | Warns If |
|---|---|---|
| T-07 | Breath sequence minimum | Chapter has 0 breath sequences |
| T-08 | Resolution color temp | Mean color temp in resolution section <5500K |
| T-09 | Resolution saturation | Mean saturation in resolution section >55% |
| T-10 | Fractal hold panel | Hold panel in breath sequence lacks fractal BG (FD 1.3–1.5) |
| T-11 | Calming tempo | Calming section soundtrack >78 BPM |
| T-12 | Strategic silence | <8 sec silence per 5 min of audio content |
| T-13 | Pentatonic ratio | >50% of calming sections use non-pentatonic scale |
| T-14 | Phase 2→4 saturation | Non-monotonic saturation decrease in resolution arc |
| T-15 | Tight in resolution | `tight` gutter used in final 25% of chapter |

### §15.3 INFO Gates

| Gate ID | Check | Reports |
|---|---|---|
| T-16 | Bilateral layout ratio | % of spreads with asymmetric panel layout |
| T-17 | Kishotenketsu rhythm | Page-level 4-beat rhythm score |
| T-18 | 432 Hz tuning | Whether soundtrack uses 432 Hz tuning |
| T-19 | ITE composite score | Final ITE_score and per-dimension breakdown |
| T-20 | Sabido role coverage | Which Sabido roles are assigned vs missing |

---

## §16 Artifact Schema

### §16.1 New Artifacts

| Artifact | Producer | Consumers | File |
|---|---|---|---|
| `color_arc` | Visual Identity Agent | Visual, QC | In `style_bible.json` |
| `fractal_palette` | Visual Identity Agent | Visual, QC | In `style_bible.json` |
| `gutter_classes` | Visual Identity Agent | Layout, Lettering, QC | In `style_bible.json` |
| `breath_visual_grammar` | Visual Identity Agent | Visual, Layout, QC | In `style_bible.json` |
| `sabido_map` | Genre Agent | Story Architect, Chapter Writer, QC | In `genre_blueprint.json` |
| `breath_map` | Visual Agent | Layout, QC | In `panel_prompts.json` |
| `fractal_target` | Visual Agent | Layout (prompt), QC | In `panel_prompts.json` per panel |
| `soundtrack_config` | New: Soundtrack Agent | Video Editor, QC | `soundtrack_config.yaml` per series |
| `ite_report` | QC Agent | Human review | `ite_report.json` per chapter |

### §16.2 ITE Report Schema

QC Agent emits `ite_report.json` per chapter:

```json
{
  "chapter_id": "ch_003",
  "ite_score": 0.73,
  "dimensions": {
    "vt_parasympathetic": 0.68,
    "vt_processing": 0.75,
    "vt_somatic": 0.72,
    "vt_stealth": 0.95
  },
  "breath_sequences": [
    {"pages": [14, 15], "valid": true, "phases_complete": 4}
  ],
  "color_arc_compliance": {
    "resolution_temp_k": 5800,
    "resolution_sat_pct": 48,
    "monotonic": true
  },
  "fractal_coverage": {
    "hold_panels_with_fractal": 2,
    "hold_panels_total": 2,
    "resolution_fractal_pct": 65
  },
  "gutter_compliance": {
    "violations": [],
    "tight_consecutive_max": 3
  },
  "stealth_scan": {
    "forbidden_terms_found": [],
    "explicit_instruction_found": false
  },
  "soundtrack": {
    "calming_tempo_avg_bpm": 64,
    "silence_total_sec": 12,
    "pentatonic_ratio": 0.78,
    "lyrics_in_resolution": false
  },
  "gates": {
    "blockers_passed": 6,
    "blockers_failed": 0,
    "warns_passed": 7,
    "warns_triggered": 2,
    "warn_details": ["T-07: only 1 breath sequence (min recommended 2 for seinen)", "T-12: 10 sec silence (close to 8 sec minimum)"]
  }
}
```

---

## §17 CI Enforcement

### §17.1 New CI Scripts

| Script | Input | Checks | Fails Build If |
|---|---|---|---|
| `ci/ite_gutter_check.py` | `panel_prompts.json`, `lettering_spec.json` | T-01, T-02, T-03, T-15, text-in-therapeutic-gutter | Any BLOCKER fails |
| `ci/ite_stealth_scan.py` | `chapter_script.json` (dialogue + captions) | T-04, forbidden term scan | Any forbidden term in dialogue |
| `ci/ite_color_arc.py` | `panel_prompts.json`, `style_bible.json` | T-08, T-09, T-14 | N/A (WARN only) |
| `ci/ite_breath_check.py` | `panel_prompts.json` | T-07, T-10, breath sequence structural validity | N/A (WARN only) |
| `ci/ite_soundtrack.py` | `soundtrack_config.yaml`, audio metadata | T-05, T-06, T-11, T-12, T-13 | T-05 or T-06 BLOCKER fails |
| `ci/ite_composite.py` | `ite_report.json` | T-19, composite score | ITE_score < 0.50 (FAIL threshold) |

### §17.2 CI Pipeline Integration

ITE CI runs as a parallel stage after QC Agent output, before chapter clearance:

```
Chapter Writer → Visual Agent → Lettering Agent → Layout Agent → QC Agent
                                                                    ↓
                                                            ITE CI Scripts (parallel)
                                                                    ↓
                                                            Chapter Clearance
```

ITE BLOCKER failures block chapter clearance. ITE WARN failures are logged in `ite_report.json` and surfaced in human review but do not block.

---

## §18 Acceptance Criteria

### §18.1 Minimum Viable ITE (Phase 1)

- [ ] `style_bible.json` emits `color_arc` and `gutter_classes`
- [ ] Genre Agent emits extended `somatic_targets` with ITE fields for all 10 genres
- [ ] Chapter Writer tags panels with `emotional_band` (existing) and `breath_role` (new)
- [ ] Visual Agent emits `fractal_target` per panel and `breath_map` per chapter
- [ ] Layout Agent renders 5 gutter width classes
- [ ] Lettering Agent enforces no-text-in-therapeutic-gutters
- [ ] QC Agent runs T-01 through T-06 BLOCKER gates
- [ ] `ci/ite_stealth_scan.py` passes on all test chapters (zero forbidden terms)
- [ ] `ci/ite_gutter_check.py` passes on all test chapters
- [ ] One test chapter per genre (10 total) scores ITE_score ≥ 0.50

### §18.2 Full ITE (Phase 2)

- [ ] All 20 QC gates operational (T-01 through T-20)
- [ ] EI v2 `visual_therapeutic` module group active with 4 dimensions
- [ ] Sabido character mapping in `genre_blueprint.json` for all 10 genres
- [ ] Breath sequence validation in CI
- [ ] Color arc validation in CI
- [ ] Soundtrack therapeutic engine operational (§11)
- [ ] Video therapeutic engine operational (§10)
- [ ] All test chapters score ITE_score ≥ 0.70
- [ ] Cold read test: 3 external readers per genre report "felt calmer after reading" without being told about therapeutic mechanisms

### §18.3 Cold Read Validation Protocol

The ultimate ITE quality gate is the **cold read test**: a reader with no knowledge of the therapeutic mechanisms reads a chapter and reports their subjective experience.

**Pass criteria:**
- Reader does not identify any "therapeutic" or "wellness" intent
- Reader reports at least one of: felt calmer, breathing slowed, felt absorbed, lost track of time, wanted to keep reading
- Reader rates entertainment value ≥7/10

**Fail criteria:**
- Reader says "this felt like it was trying to teach me something"
- Reader identifies breathing exercises, meditation, or therapy framing
- Reader reports feeling manipulated or patronized

---

## §19 Non-Goals

1. **No clinical claims.** ITE does not claim to treat, cure, or diagnose any condition. The physiological mechanisms are real (cited), but we never make consumer-facing health claims.
2. **No explicit wellness branding.** Content is not marketed as "therapeutic manga" or "healing videos." Genre comes first in all positioning.
3. **No biometric feedback loops.** We do not measure or adapt to individual reader/viewer physiology in real-time (future consideration for interactive formats).
4. **No replacement for professional care.** ITE content is entertainment that happens to regulate. It is not a substitute for therapy, medication, or clinical treatment.
5. **No mandatory subliminal audio.** Isochronic tones and sub-bass layers (§11.3) are production-level opt-in. They can be globally disabled.

---

## Appendix A: Research Evidence Map

Maps each ITE mechanism to its primary research citation (full citations in `research/2026-03-30_implicit-therapeutic-visual-media.md`):

| Mechanism | Primary Evidence | Effect Size / Key Finding |
|---|---|---|
| Fractal stress reduction | Taylor (UOregon), eye-tracking + fMRI + qEEG | Up to 60% stress reduction at FD 1.3–1.5 |
| Panel size → dwell time → breathing | McCloud 1993, Cohn 2013 | Panel area correlates with reading speed; large panels slow reading |
| Gutter as processing space | Graphic medicine literature, Williams 2012 | Gutters scaffold "agential self" redevelopment |
| Color temp → autonomic response | Valdez & Mehrabian 1994 | Warm = arousal, cool = calming; saturation drives arousal, brightness drives pleasure |
| Iyashikei genre therapeutic effects | Roquet, post-1995 Japan healing boom | Genre-level implicit therapy; Covid pandemic drove mainstream adoption |
| Dual hemisphere engagement | Cohn 2020 PINS model | Sequential art engages both hemispheres; unique bilateral neural activation |
| Camera movement → embodied response | Frontiers in Neuroscience 2023 | Viewers psycho-physiologically simulate camera movement |
| Visual rhythm → breathing entrainment | Nature Communications; Frontiers in Psychiatry | Visual cues at 0.1 Hz entrain respiration → HRV improvement |
| Studio Ghibli therapeutic RCT | JMIR Serious Games 2026 (N=518) | Happiness 5.45 vs 3.58 (p<.001); cortisol reduction |
| Nature viewing → cortisol | Meta-analysis of 31 studies (12 countries) | -0.06 cortisol, -3.82 mmHg systolic; greatest effect in first 5 min |
| Tempo entrainment | Bernardi et al. | 1:4 breathing-to-rhythm ratio; Verdi arias at 6 cycles/min sync CV rhythms |
| Silence > music for regulation | Bernardi et al. | 2-min silence drops HR, BP, respiration below baseline |
| 10-sec phrase → vagal slowing | Cardiovascular entrainment research | Matches Mayer wave rhythm; largest HR/BP excursions → calm |
| Pentatonic → parasympathetic | Frontiers in Psychology 2024 | Decreased electrodermal activity; reduced sympathetic nervous activity |
| Binaural/isochronic tones | SciELO 2021 systematic review | 82% of studies: more effective than control |
| 432 Hz tuning | Calamassi 2019 (N=33) | -4.79 BPM heart rate (p=0.05); modest evidence |
| Lo-fi → alpha brainwaves | Taylor & Francis 2024, Oxford Scientist | "Medicine for anxiety"; alpha state promotion; no lyric interference |
| Sabido methodology | Singhal et al. 2003; 50+ years of EE research | Three-role model proven across telenovelas, radio, film |
| Story → neural simulation | PMC fMRI studies | Amygdala, hippocampus, prefrontal, motor areas activate; story is "felt and simulated" |
| Sesame Street implicit SEL | Meta-analysis: 24 studies, 10,000+ children, 15 countries | Effects persisted into adolescence |
| Flow state → reduced rumination | Boson X study; VIRTUALTIMES project | 6 weeks of gaming reduced self-rumination in depression |

---

## Appendix B: Pentatonic Mode Reference

Preferred scales for calming sections of soundtracks:

| Mode | Notes (C root) | Character | Best For |
|---|---|---|---|
| Major pentatonic | C D E G A | Bright, open, hopeful | Afterglow sections, iyashikei, resolution |
| Minor pentatonic | C Eb F G Bb | Contemplative, grounded, warm | Turning points, emotional processing |
| Japanese (In) | C Db F G Ab | Melancholic beauty, stillness | Seinen, horror resolution, grief scenes |
| Okinawan | C E F G B | Warm, distinctive, island calm | Iyashikei, nature scenes |
| Egyptian/Phrygian | C Db E F G | Exotic, meditative, ancient | Cultivation/xianxia, spiritual scenes |

**Rule:** Major pentatonic is the default for calming sections. Minor pentatonic for emotionally weighted calming. Other modes are genre-specific choices documented in `soundtrack_config.yaml`.

---

## Appendix C: Fractal Dimension Visual Reference

| FD Range | Natural Analog | Visual Density | Panel Use |
|---|---|---|---|
| 1.0–1.1 | Single straight line, bare horizon | Nearly empty | Extreme minimalism, void |
| 1.1–1.2 | Bare winter branches, calm sea | Sparse | Horror, emptiness, isolation |
| **1.3** | **Scattered clouds, gentle brook** | **Moderate-light** | **Breathing hold panels** |
| **1.4** | **Forest canopy, river delta** | **Moderate** | **Peak therapeutic (default target)** |
| **1.5** | **Dense foliage, cumulus clouds** | **Moderate-rich** | **Maximum calming response** |
| 1.6 | Rainforest, coral reef | Rich | Active nature scenes |
| 1.7 | Urban skyline, machinery | Dense | Tension, overwhelm |
| 1.8–1.9 | Pure noise, static | Chaotic | Never used (discomfort) |

**Sweet spot for therapeutic effect: FD 1.3–1.5.** This range matches the fractal complexity of savanna landscapes where human vision evolved — the "fractal fluency" zone.
