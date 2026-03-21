# AI MANGA DHARMA SYSTEM

Complete Pipeline Specification

**Seven Agents · Two Cross-Cutting Systems · One Production Standard**

*SpiritualTech Systems · Nihala (Ma'at) · Confidential · v1.1*

---

## System Philosophy

This system builds manga that does two things simultaneously: entertains with the emotional mechanics that make manga globally beloved, and transmits spiritual wisdom from 25+ years of Buddhist monastic practice, Sufi heritage, and cross-tradition teaching — without ever stating what it is transmitting.

The single most important design principle, repeated across every agent spec:

> **The reader must never feel taught. They must feel moved. If a teaching can be stated in dialogue, it has failed. If it can only be felt through story structure, it has succeeded.**

This is not a constraint on quality — it is the definition of quality for this system. Every agent's job is to enforce this principle in its own domain: structure, voice, image, letterform, silence, and memory.

---

## Pipeline Overview

The pipeline has two operational modes: **Series Setup** (runs once, before any chapter production) and **Chapter Production** (runs for every chapter). Both modes feed the QC + Consistency Agent, which maintains the series memory that connects all chapters into a coherent arc.

### Series Setup — Runs Once

```
Director Agent (series brief)
        ↓
Visual Identity Agent ─────────────────────────────────────────────
  Outputs: style_bible.json, lettering_style_bible.json,           |
           character_model_sheets[], asset_registry.json,           |
           anchor_panels[], motif_evolution_map                     |
        ↓                                                           |
Genre Agent  ←── Teaching Library ←── Wound Map                     |
  Outputs: genre_blueprint.json (arc, transmission_map,             |
           forbidden phrases, villain_spec, silence_map)            |
        ↓                                                           |
Story Architect Agent ←── genre_blueprint                           |
  Outputs: story_architecture.json (chapter_beat_sheet)             |
           [Transmission Splitter strips carrier annotations]       |
                                                                    |
──────────── All outputs feed Chapter Production ───────────────────
```

### Chapter Production — Runs Per Chapter

```
writer_handoff (clean beat sheet, no carrier annotations)
        ↓
Chapter Writer Agent
  Outputs: chapter_script.json
        ↓                       ↓
  Visual Agent          Lettering Agent
  (runs after Visual      (runs after Visual
   prompts planned)        prompts planned)
        ↓                       ↓
  panel_prompts.json    lettering_spec.json
        ↓                       ↓
  Image Generation              │
        ↓                       │
  panel_images[]                │
        ↓                       ↓
        └────── Layout Agent ───┘
                    ↓
          final_page_composite[]
                    ↓
          QC + Consistency Agent ←── series_memory.json
                    ↓
          revision_queue.json + series_memory_update.json
                    ↓
          chapter_clearance: pass → release | hold → revision loop
```

**Pipeline dependency note (aligned with Lettering Agent Spec v1.1 §1, Patch 1):** The Visual Agent and Lettering Agent are NOT fully parallel. The Lettering Agent runs after the Visual Agent produces `panel_prompts.json` (specifically the `composition_notes` defining text zones). Both agents are decoupled from final image rendering — lettering corrections do not require image regeneration, and image corrections do not require lettering regeneration, as long as `composition_notes` remain unchanged.

---

## Key Artifacts & Data Flow

Every agent communicates through versioned JSON artifacts. No agent passes information verbally or implicitly — all state lives in these documents. The `series_memory.json` is the connective tissue that makes the system aware of its own history.

| Artifact | Produced by | Consumed by | What it contains |
|---|---|---|---|
| `style_bible.json` | Visual Identity Agent | Visual Agent, Lettering Agent, Layout Agent, QC Agent | Style tokens (ordered, immutable), camera/action/mood lexicons (per Visual Agent Spec §2.3), silence visual grammar (parameterized with numeric values per Visual Identity Spec §3.5), prohibited style terms, anchor panel refs, drift thresholds. Two versions: writer-facing (clean) + internal (transmission metadata). Immutable per version — changes require formal migration (§8). |
| `lettering_style_bible.json` | Visual Identity Agent | Lettering Agent | Font system (per-speaker registry), bubble shapes by type, SFX lexicon (text→visual treatment), phase density guide, exclusion zones, silence adjacency rules, multilingual rules. |
| `character_model_sheets[]` | Visual Identity Agent | Visual Agent, QC Agent | LoRA IDs, outfit registry (per-outfit_id), expression range, injury state templates, baseline continuity state. Every named character must have entries before chapter production begins. |
| `asset_registry.json` | Visual Identity Agent | Visual Agent, Lettering Agent, Layout Agent | All named locations, props, motifs with `asset_id` references and anchor panel references. All downstream agents reference by ID only — free-text names prohibited (Visual Identity Spec §10). |
| `anchor_panels[]` | Visual Identity Agent | QC Agent | Reference images + embeddings + measured parameters (contrast_ratio, linework_weight_px, shadow_coverage_pct, highlight_coverage_pct) for all required categories. Ground truth for drift detection every 10 panels. |
| `motif_evolution_map` | Visual Identity Agent | Story Architect, Visual Agent | Per motif: full stage sequence, chapter ranges, visual specs, `asset_id`s, evolution schedule. Motifs embody atoms — never name them in writer-facing artifacts. |
| `genre_blueprint.json` | Genre Agent | Story Architect, Chapter Writer (partial), QC Agent | arc_structure, transmission_map, silence_map, villain_spec, power_system, pacing_map, forbidden_phrases, wound_honor_cutoff, somatic_targets, series_constraints. |
| `story_architecture.json` | Story Architect | Chapter Writer (handoff only), QC Agent (internal) | season_outline (mini-arcs + turning points) + chapter_beat_sheet (one entry per chapter). Transmission Splitter produces two views: writer_handoff (clean) + internal_record (full carrier annotations). Per Story Architect Spec §5, Fix 1. |
| `writer_handoff` | Transmission Splitter | Chapter Writer | Sanitized chapter entry — all `carrier_beat` annotations, atom assignments, `hiding_place` references, and `somatic_target` labels stripped. Chapter Writer never sees transmission architecture. |
| `chapter_script.json` | Chapter Writer | Visual Agent, Lettering Agent, QC Agent | Pages → panels → dialogue / caption / SFX / action / camera / mood / silence. Two versions: writer_handoff (Visual/Lettering consume) + internal_record (QC consumes). Per Chapter Writer Spec §3 + Field Classification Table (Fix 3). |
| `panel_prompts.json` | Visual Agent | Image Gen, Lettering Agent (composition_notes), Layout Agent, QC Agent | One `panel_prompt` per panel: prompt (≤120 tokens), negative_prompt (≤60 tokens), character_refs, continuity_tags, silence_compliance flag, composition_notes, token count. Per Visual Agent Spec §3. |
| `lettering_spec.json` | Lettering Agent | Layout Agent, QC Agent | One `lettering_panel` per panel — populated or `silence_confirmed: true`. Verbatim text with SHA-256 hash. No panel absent. Complete panel coverage mandatory. Per Lettering Agent Spec §3. |
| `final_page_composite[]` | Layout Agent | QC Agent | Release-ready composited page images. Subject to OCR scan for silent panel purity at QC level. |
| `revision_queue.json` | QC Agent | All upstream agents (escalation) | Ranked issues with severity (BLOCKER/MAJOR/MINOR), gate_id, source_agent, precise JSON diffs, auto-fix objects (lossless + reversible + no upstream regen), and chapter_clearance decision. Per QC Spec §5. |
| `series_memory.json` | QC Agent (ongoing) | QC Agent (every chapter) | All series facts: character states, injury states, outfit states, motif stages, location layouts, silence records, transmission checkpoints, forward continuity expectations. Per QC Spec §7. |

---

## Agent Specifications — Summary Cards

Each card summarizes one agent's role, inputs/outputs, and binding rules. Full specifications are in the individual agent spec documents (see Document Index §11).

### 00 — Visual Identity Agent

**Once per series — before chapter production begins**

Produces the complete aesthetic identity of the series. The only agent permitted to make aesthetic decisions, within the bounds of genre_blueprint, market format, and production constraints. Freezes all visual degrees of freedom so every downstream agent becomes constraint-following.

| | |
|---|---|
| **Consumes** | genre_blueprint · Teaching Library atom_list · wound_map · market_format_spec · production_constraints · transmission_requirements |
| **Produces** | style_bible.json (writer-facing + internal) · lettering_style_bible.json · character_model_sheets[] · asset_registry.json · anchor_panels[] (with embeddings + measurements) · motif_evolution_map |
| **Key rules** | style_bible_version is immutable — changes require formal migration (major/minor semver) // Silence visual grammar defined as numeric parameters: contrast_ratio_range, screentone_density_pct, cooling_ramp per beat (§3.5) // Anchor panels stored as image + embedding + measured parameters for drift detection (§6) // Motifs never carry text, symbols, or atom names in writer-facing artifacts (§7.2) // Two versions of style_bible: writer-facing (transmission metadata stripped) + internal (full metadata, QC only) (§9) // All downstream agents reference entities by registered ID only — free-text names prohibited (§10) |
| **Key output** | `style_bible.json` + `anchor_panels[]` |
| **Full spec** | `specs/VISUAL_IDENTITY_AGENT_SPEC.md` (684 lines, v1.1) |

### 01 — Genre Agent

**Once per series — after Visual Identity Agent**

Translates Teaching Library wisdom atoms into genre-native story structures. Defines where each atom hides inside the genre's emotional mechanics. Produces the genre_blueprint that every subsequent agent consumes as primary constraint.

| | |
|---|---|
| **Consumes** | series brief (Director Agent) · Teaching Library (atom candidates, wound map) · market format · audience profile |
| **Produces** | genre_blueprint.json — arc_structure, transmission_map, silence_map, villain_spec, power_system, pacing_map, forbidden_phrases, somatic_targets, series_constraints |
| **Key rules** | Genre emotional contract is non-negotiable — transmission must travel through genre conventions, not replace them // 6-step workflow: Genre Profile → Atom Selection → Hiding Place Assignment → Villain Design → Arc Structure → Forbidden Phrases // Wound must be honored for at least 60% of arc before healing motion begins (wound_honor_cutoff) // Villain designed from protagonist's shadow — integration not defeat is the true resolution // 10 international genres: shōnen, seinen, shōjo, sports, horror, iyashikei, cultivation/xianxia, manhwa, webtoon romance, isekai // Structural embedding always beats dialogue — 4 levels: character SAYS it (failed) → narration EXPLAINS it (weak) → plot DEMONSTRATES it (strong) → structure IS the teaching (transmission) |
| **Key output** | `genre_blueprint.json` |
| **Full spec** | `specs/MANGA_GENRE_AGENT_SPEC.md` (546 lines, v1.1) |

### 02 — Story Architect Agent

**Once per series arc / season**

Expands genre_blueprint phase-level constraints into a chapter-by-chapter beat sheet. The first downstream consumer of genre_blueprint. Decides how the arc unfolds across time — beat by beat, hook by hook — without making any genre or aesthetic decisions.

| | |
|---|---|
| **Consumes** | genre_blueprint.json · series_constraints (chapter count, volumes, cadence) · cast_seed (optional) · setting_seed (optional) |
| **Produces** | story_architecture.json — story_architecture_internal.json (full carrier metadata, QC only) + story_architecture_handoff.json (clean, Chapter Writer only). Per Fix 1: dual-view output. |
| **Key rules** | Transmission Splitter: carrier_beat annotations stripped before handoff — writer sees clean beats only (Fix 1) // No healing motion before wound_honor_cutoff — enforced at beat description level // Every power-up chapter: loss_beat before gain_beat, same chapter // Villain interiority chapter placed before backstory_reveal_chapter // silence_map fully allocated to exact chapter positions before output // genre_hiding_places lookup defined at config/manga/genres/{genre_id}.json (Fix 2) // Forbidden phrase scan applies to plot_beats[], chapter_end_hook, turning_point, AND silence_somatic_target (Fix 3) // Serialization cadence adapter adjusts beat density, silence tolerance, hook frequency per weekly/monthly/volume release (Fix 4) |
| **Key output** | `story_architecture.json` (chapter_beat_sheet) |
| **Full spec** | `specs/MANGA_STORY_ARCHITECT_SPEC.md` (841 lines, v1.1) |

### 03 — Chapter Writer Agent

**Once per chapter**

Expands a single chapter entry from the beat sheet into a complete panel-by-panel script. The first agent to produce actual manga language. Decides how events sound and how they are staged panel by panel — within every upstream constraint.

| | |
|---|---|
| **Consumes** | writer_handoff (sanitized chapter entry — no carrier annotations) · character_bible · style_bible · world_rules · series_forbidden_phrases |
| **Produces** | chapter_script.json — pages → panels → dialogue / caption / SFX / action / camera / mood / silence. Two versions: writer_handoff (downstream) + internal_record (QC). |
| **Key rules** | Characters say less than they know — deflect, attack, go silent rather than narrate their pain // Action contradicts dialogue in the same panel when character is under emotional pressure // If page_type = "silent": ALL panels on that page must be panel_type = "silent" with zero text (Fix 1) // silence_guard set on last 2 panels before + first 2 after silent pages, page-local counting (Fix 2) // Field Classification Table: 14 fields classified by visibility per downstream agent (Fix 3) — Visual gets camera/action/mood, Lettering gets dialogue/SFX/caption, QC gets everything // Silent pages follow five-beat protocol: arrival → stillness → detail → world → return // No text element within two panel positions of a silent page explains the silence // Captions are the highest-risk leak vector — pass/fail examples in spec |
| **Key output** | `chapter_script.json` |
| **Full spec** | `specs/MANGA_CHAPTER_WRITER_SPEC.md` (854 lines, v1.1) |

### 04a — Visual Agent

**Once per chapter (after Chapter Writer, before image generation)**

Translates panel objects from chapter_script into precise, style-locked image generation prompts. A renderer and translator — not a storyteller. Produces one panel_prompt per panel using fixed lexicon translations, never freeform interpretation.

| | |
|---|---|
| **Consumes** | chapter_script.json (writer_handoff) · style_bible.json · character_model_sheets[] · asset_registry.json |
| **Produces** | panel_prompts.json — one panel_prompt per panel with prompt, negative_prompt, character_refs, continuity_tags, silence_compliance flag, composition_notes, prompt_token_count |
| **Key rules** | Prompt assembly order is fixed: style_tokens → camera → subject → action → background → mood → continuity → composition → silence (§3.3) // Token budget: positive ≤ 120 tokens, negative ≤ 60 tokens, with P0–P3 overflow policy (Fix 3) // Lexicons formally defined in style_bible.json under "lexicons" key with explicit fallback behavior (Fix 1) // silence_guard adjacency: last 2 panels on page before + first 2 on page after silence, page-local (Fix 2) // No new meaning: 7-point violation checklist — symbolic props, weather changes, extra characters, dramatic effects, off-script characters, emotional escalation, symbolic composition (Fix 4) // Every named character panel includes LoRA reference // Drift detection every 10 panels vs anchor panels |
| **Key output** | `panel_prompts.json` → Image generation → `panel_images[]` |
| **Full spec** | `specs/VISUAL_AGENT_SPEC.md` (535 lines, v1.1) |

### 04b — Lettering Agent

**Once per chapter (after Visual Agent produces composition_notes)**

Places dialogue bubbles, captions, and SFX on panels. Produces a complete lettering specification from chapter_script text content and Visual Agent composition notes. Placement and rendering only — never rewrites, never adds, never letters silence.

| | |
|---|---|
| **Consumes** | chapter_script.json (text content) · panel_prompts.json (composition_notes only) · lettering_style_bible.json |
| **Produces** | lettering_spec.json — one lettering_panel per panel, including `silence_confirmed: true` empty entries for all silent panels |
| **Key rules** | Text transcribed verbatim from script — SHA-256 hash on every text element (§4.2) // Pipeline is sequential: runs AFTER Visual Agent produces composition_notes, decoupled from image rendering (Patch 1) // Caption redundancy flagged to QC/Chapter Writer — never removed by Lettering Agent (Patch 2) // Silent panels produce explicit `silence_confirmed: true` entries — active assertion, not omission // Every panel_id in the chapter must have exactly one lettering entry // Post-silence first bubble: smallest/lightest/shortest in chapter, `first_after_silence: true` (§5.4) // SFX within 3 panels of silence: weight reduced per tier table, chapter-sequential counting crossing page boundaries (§5.3) // silence_guard density reduction: max 2 bubbles, font -15%, padding +20% (§5.2) |
| **Key output** | `lettering_spec.json` |
| **Full spec** | `specs/LETTERING_AGENT_SPEC.md` (656 lines, v1.1) |

### 05 — Layout Agent

**Once per chapter (after Visual + Lettering + Image Gen complete)**

Composites panel images with lettering spec to produce final pages. Applies panel borders, gutters, page composition, and reading-direction formatting.

| | |
|---|---|
| **Consumes** | panel_images[] (from Image Generation) · lettering_spec.json · style_bible.json (panel border, gutter rules) · page_layout_rules |
| **Produces** | final_page_composite[] — release-ready page images |
| **Key rules** | Panel-first assembly: individual rendered panels → composed pages // Reading direction enforcement: RTL (Japanese), LTR (English), vertical scroll (webtoon) // Page type handling: standard (multi-panel grid), splash (full-bleed), double_spread, silent (special breathing space) // Verifies every panel_id has a lettering entry before compositing — missing entry = pipeline error // Halts on LETTERING.SILENT_PANEL_PURITY blocker — does not composite until cleared // Text overlay z-ordering: background panel → bubbles → SFX → captions |
| **Key output** | `final_page_composite[]` |
| **Full spec** | `specs/MANGA_LAYOUT_AGENT_SPEC.md` (910 lines, v1.0) |

### 06 — QC + Consistency Agent

**Once per chapter — last, after all other agents complete**

The pipeline's immune system. Runs across all agent outputs simultaneously at three detection levels. Determines chapter_clearance (pass/hold), applies lossless auto-fixes, escalates meaning-changing violations upstream, and updates series memory with new facts and forward continuity expectations.

| | |
|---|---|
| **Consumes** | All chapter outputs: chapter_script (writer_handoff + internal_record), panel_prompts, panel_images, lettering_spec, final_page_composite · series_memory.json · genre_blueprint · style_bible (writer-facing + internal) + anchor_panels |
| **Produces** | revision_queue.json · series_memory_update.json · chapter_clearance: pass\|hold · quality_metrics_report |
| **Key rules** | Three-level detection stack, fastest first: Level 1 structural → Level 2 cross-reference → Level 3 rendered output (§3) // Auto-fix ONLY lossless + reversible + no upstream regeneration required — safety clause formalized (Fix 2) // Never auto-fixes meaning-changing content — hold + escalate // Severity: BLOCKER (always blocks) → MAJOR (blocks unless auto-fixed per safety clause) → MINOR (logged) // Semantic drift: MINOR default, auto-escalates to MAJOR on threshold breach or 3rd occurrence (Fix 1) // Gate Registry is single source of truth — any gate not listed is not enforced (§8) // 30 gates across 5 categories: structural, visual, silence, lettering, transmission // series_memory_update creates forward constraints for all future chapters // Transmission integrity: QC sees internal_record but never exposes carrier metadata in revision_queue |
| **Key output** | `revision_queue.json` + `series_memory_update.json` + `chapter_clearance` |
| **Full spec** | `specs/QC_AGENT_SPEC.md` (655 lines, v1.1) |

---

## Two Cross-Cutting Systems

Beyond the individual agents, two systems run across the entire pipeline and bind all agents together.

### The Transmission Splitter

A lightweight processing step between the Story Architect and Chapter Writer. It receives `story_architecture.json` and produces two views from the same data:

- **writer_handoff** — all `carrier_beat` annotations, atom assignments, `hiding_place` references, and `somatic_target` labels stripped
- **internal_record** — full annotations preserved for QC and system memory

**Why it exists:** if the Chapter Writer knows which beat carries the atom, it will be tempted to emphasize it — and that emphasis is exactly how teachings leak into dialogue. The Splitter protects the integrity of the transmission by ensuring the writer writes as a writer, not as a system operator.

The internal_record is never passed to any creative agent. It is consumed only by the QC Agent for transmission checkpoint verification and cold read scheduling.

**Implementation:** The Transmission Splitter is not a separate agent — it is a processing step defined within the Story Architect Spec (§5, Fix 1) and the Chapter Writer Spec (§3). The Story Architect produces both views; the Chapter Writer receives only the handoff view.

### Series Memory

The `series_memory.json` is the living document that makes the system aware of its own history across all chapters. It is updated by the QC Agent after every chapter via `series_memory_update.json` and read by the QC Agent at the start of every new chapter's processing.

It stores three categories of information:

1. **Facts** — character states, injury states, motif stages, location layouts, silence records, transmission checkpoints (with fact_types: permanent_physical, temporary_injury, outfit_change, location_state, motif_evolution, relationship_state, prop_acquisition, prop_loss)
2. **Forward expectations** — constraints created by new facts (e.g., "Kai's bruised_knuckles_right acquired chapter 9 must appear in all future panels until healing event"). Deadline chapters tracked; unresolved expectations flagged.
3. **Recurring issues** — per-chapter QC metrics including silent panel confirmations, end hook text, drift warnings, transmission flags, and auto-escalation counts.

The series memory is what transforms the system from a chapter generator into a series producer — a system capable of maintaining narrative, visual, and transmission coherence across 60+ chapters without human continuity editing.

---

## Silence as a System-Wide Design Principle

Silence is not a feature of individual panels. It is a system-wide design principle that every agent is required to honor in its own domain. This table shows how silence propagates from the genre_blueprint all the way to the final composite.

| Agent | Silence obligation | How enforced |
|---|---|---|
| **Visual Identity Agent** | Define `silence_visual_grammar` with numeric parameters. Define cooling and warming ramps. | Parameterized schema: contrast_ratio_range, screentone_density_pct, line_weight_pt per beat. QC Agent measures against these values. (§3.5) |
| **Genre Agent** | Specify silence_map: exact chapters, page counts, placement triggers, somatic targets. | silence_map is binding input for Story Architect. QC Agent crosschecks allocation. |
| **Story Architect** | Allocate silence_map entries to exact chapter_beat_sheet positions. No unallocated silence. | Pre-check: all silence_map entries chapter-stamped before output. QC Agent verifies completeness. |
| **Chapter Writer** | Execute five-beat silence protocol. No text within 2 panels of silence. No explanation after silence. | silence_guard set on adjacent panels (Fix 2). Silence contamination rules enforced at script QC. (§7) |
| **Visual Agent** | `silence_compliance = true`: zero text-requesting terms in prompt. Full silence prohibition list in negative prompt. Follow five-beat visual protocol. | `SILENCE.PROMPT_PURITY` is BLOCKER in QC. Prohibition list is exhaustive including background signage. (§5) |
| **Lettering Agent** | Silent panels produce `silence_confirmed: true` empty entries — active assertion. Post-silence re-entry: whisper type, minimum size. | `SILENCE.PANEL_PURITY` is BLOCKER. `LETTER.FULL_PANEL_COVERAGE` requires every panel_id accounted for. First-after-silence rule (§5.4). |
| **Layout Agent** | Halt on silent panel purity failure. Do not composite until cleared. Special breathing space for silent pages. | HALT_LAYOUT_UNTIL_CONFIRMED policy from QC Agent blocker issues. |
| **QC + Consistency Agent** | OCR scan final_page_composite for all silent panels. Verify `composite_text_detected = false`. | `SILENCE.RENDERED_PURITY` is BLOCKER. Silence sequence records stored in series_memory. |

---

## Transmission Integrity Chain

The teaching travels from the Teaching Library through every agent in a specific form — each layer encodes it differently, each layer strips the encoding so the next layer only sees story. This is the system's deepest design.

| Layer | Form of transmission | How it stays hidden |
|---|---|---|
| **Teaching Library** | Wisdom atom: core teaching, secular translation, panel_expression, somatic_cue | Source data. Not visible to any creative agent. |
| **Genre Agent** | Hiding place: which genre moment carries which atom (rival = shadow self, power-up = Fana, etc.) | Genre blueprint describes story structure — atom names never appear in writer-facing fields. |
| **Story Architect** | Carrier beat: one story beat per chapter indistinguishable from surrounding plot beats | Transmission Splitter strips all carrier annotations before Chapter Writer handoff. |
| **Chapter Writer** | Script: carrier beat becomes dialogue contradiction, silent sequence, or physical action that carries the somatic cue | Chapter Writer never sees atom assignments. Writes from clean story beats only. |
| **Visual Agent** | Panel: somatic cue rendered visually — lighting temperature, camera angle, body language, silence register | No atom names or teaching labels in any image prompt. Style bible translates mood through numeric parameters. |
| **Lettering Agent** | Typography: bubble size, thought cloud tentativeness, post-silence re-entry weight — all carrying emotional register | Text verbatim from script. Lettering craft rules (small cloud = suppressed thought) documented as craft, not as transmission. |
| **Reader** | Somatic experience: the reader feels something before they can name it | The cold read test: if theme is identified before emotion is felt, transmission has leaked somewhere in the chain. |

---

## The Cold Read Test — Ultimate Quality Gate

Every agent spec ends with a quality gate that cannot be automated: the **cold read test**. A human reader who does not know what teaching is embedded reads the chapter cold. The pass condition is the same across all agents, all levels, all output types:

> **Does the reader feel something before they can name the theme?**
>
> If yes — pass.
>
> If the theme is recognized before the emotion arrives — the transmission has leaked. Return to the agent where the leak occurred.

This test cannot be replaced by any automated scan. Semantic similarity models, forbidden phrase scans, and visual drift detection are necessary but not sufficient. The cold read test is the final verification that the entire chain — from Teaching Library atom to final composite — has done its job.

Schedule cold reads at minimum: end of each arc phase, end of each full chapter. The QC Agent flags `transmission_checkpoints` in series_memory as `cold_read_pending`. When a cold read clears, the checkpoint is marked `confirmed` and the fact is recorded permanently in the series memory.

---

## Alignment Notes — v1.1 Corrections

This summary (v1.1) corrects the following items from the v1.0 draft to align with the coded specs:

1. **Pipeline parallelism corrected:** v1.0 stated Visual Agent and Lettering Agent "run in parallel." The coded Lettering Agent Spec (v1.1, Patch 1) resolves this: Lettering runs AFTER Visual Agent produces `composition_notes`, but is decoupled from image rendering. The pipeline diagram is updated to reflect this sequential-but-decoupled dependency.

2. **Caption removal authority corrected:** v1.0 implied Lettering Agent could remove captions. The coded spec (v1.1, Patch 2) clarifies: Lettering Agent raises `caption_redundancy_flag` to QC/Chapter Writer — it never removes or rewrites script text.

3. **Semantic drift severity resolved:** v1.0 described semantic drift as "soft fail = major" in one section and MINOR in the gate registry. The coded QC Spec (v1.1, Fix 1) resolves this: MINOR by default, auto-escalates to MAJOR on threshold breach or 3rd occurrence across chapters.

4. **Auto-fix safety clause added:** v1.0 allowed "all majors auto-fixed → pass." The coded QC Spec (v1.1, Fix 2) adds: auto-fixed majors pass ONLY if `lossless: true` AND `reversible: true` AND `requires_upstream_regen: false`.

5. **Token budget added:** v1.0 did not specify prompt length limits. The coded Visual Agent Spec (v1.1, Fix 3) adds: positive ≤ 120 tokens, negative ≤ 60 tokens, with P0–P3 overflow policy.

6. **Lexicons formally defined:** v1.0 referenced lexicons without defining schema or fallback behavior. The coded Visual Agent Spec (v1.1, Fix 1) defines: all lexicons in `style_bible.json` under `"lexicons"` key, camera = hard_fail on unknown, action/mood = style_bible_gap_flag.

7. **Field classification formalized:** v1.0 did not specify which fields each downstream agent sees. The coded Chapter Writer Spec (v1.1, Fix 3) adds a 14-field × 4-consumer visibility matrix.

8. **Artifact classification formalized:** v1.0 referenced "writer-facing" without enumerating. The coded Visual Identity Spec (v1.1, Fix 1) adds a formal table: 6 writer-facing artifacts, 4 internal-only artifacts, with stripping rules.

9. **Downstream ID contract added:** v1.0 did not enforce ID-based referencing. The coded Visual Identity Spec (v1.1, Fix 2) mandates: all entities referenced by `character_id`, `outfit_id`, `asset_id`, `anchor_panel_id` only — free-text names prohibited.

10. **3-panel silence adjacency defined:** v1.0 used "within three panels of silence" without defining boundary rules. The coded Lettering Spec (v1.1, §5.3) defines: chapter-sequential counting crossing page boundaries (wider than silence_guard which is page-local).

---

## Document Index

The full specification set consists of 14 documents. This summary is the master reference. The individual specs contain the complete schemas, worked examples, system prompts, and quality gates for each agent.

| # | Document | Filename | Lines | Version | Covers |
|---|---|---|---|---|---|
| 0 | **This document** | `ai_manga_pipeline_summary.md` | — | v1.1 | Full pipeline overview, artifact map, cross-cutting systems, silence system, transmission chain, alignment corrections. |
| 1 | **Visual Identity Agent** | `visual_identity_agent_spec.md` | 684 | v1.1 | style_bible schema, silence grammar parameters, anchor panel system, motif evolution map, drift detection, artifact classification (Fix 1), ID contract (Fix 2). |
| 2 | **Genre Agent** | `manga_genre_agent_spec.md` | 546 | v1.1 | genre_blueprint schema, 6-step workflow, hiding place matrix, forbidden phrases, villain design, silence map, 10 international genres, Japan-ALL. |
| 3 | **Story Architect Agent** | `manga_story_architect_spec.md` | 841 | v1.1 | chapter_beat_sheet schema, bridge logic, phase expansion, transmission scheduling, dual-view output (Fix 1), hiding_places dependency (Fix 2), forbidden phrase scope (Fix 3), cadence adapter (Fix 4). |
| 4 | **Chapter Writer Agent** | `manga_chapter_writer_spec.md` | 854 | v1.1 | chapter_script schema, dialogue craft rules, silence protocol, silent page/panel schema (Fix 1), silence_guard pinning (Fix 2), field classification (Fix 3), high-action example (Fix 4). |
| 5 | **Visual Agent** | `visual_agent_spec.md` | 535 | v1.1 | panel_prompt schema, prompt assembly algorithm, style lock rules, silence visual protocol, lexicon definitions (Fix 1), silence_guard adjacency (Fix 2), token budget (Fix 3), no-new-meaning checklist (Fix 4). |
| 6 | **Lettering Agent** | `lettering_agent_spec.md` | 656 | v1.1 | lettering_spec schema, bubble type specs, SFX craft rules, reading order, pipeline dependency (Patch 1), caption boundary (Patch 2), 3-panel SFX proximity, first-after-silence rule. |
| 7 | **QC + Consistency Agent** | `qc_agent_spec.md` | 655 | v1.1 | revision_queue schema, series_memory schema, three detection levels, severity rubric, 30-gate registry, semantic drift resolution (Fix 1), auto-fix safety clause (Fix 2). |
| 8 | **Layout Agent** | `manga_layout_agent_spec.md` | 910 | v1.0 | Page composition, panel-first assembly, RTL/LTR/webtoon direction, page type handling, text overlay pipeline. |
| 9 | **Text Rendering** | `manga_text_rendering_spec.md` | 1,330 | v1.0 | Panel overlay pipeline, balloon_planner stage, clarity_mode vs manga_authentic_mode, SFX rendering, multilingual rendering, production quality. |
| 10 | **Teaching Library** | `manga_teaching_library_spec.md` | 594 | v1.0 | Wisdom atom schema, 20 seed atoms, 5 seed series concepts, deployment rules, compound pairing, QC review layer. |
| 11 | **Brand DNA & Anti-Spam** | `manga_brand_dna_anti_spam_spec.md` | 603 | v1.0 | 30-brand matrix, visual fingerprinting, content/locale/production mix variation, anti-spam scoring, batch diversity validation. |
| 12 | **Series Bible** | `manga_series_bible_spec.md` | 816 | v1.0 | Per-series reference: 19-page structural formula (COMPRESSION→MA→CHOICE→TONGLEN→AFTER), 5 seed series, motif library, TikTok clip spines, QC rules. |
| 13 | **Production Pipeline** | `manga_production_pipeline_spec.md` | 1,412 | v1.0 | 1,000-book production: batch architecture, agent orchestration, cloud GPU scaling (RunPod/Vast.ai), multi-level QC, 12-week timeline, cost model. |

**Total: 14 documents · 10,436+ lines · 380+ KB**

---

*SpiritualTech Systems · AI Manga Dharma System · Pipeline Summary v1.1 · Confidential*
