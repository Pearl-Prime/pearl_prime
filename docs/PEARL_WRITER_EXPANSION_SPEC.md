# Pearl_Writer — Thin-Section Expansion (Spine Pipeline)

**Project:** `proj_state_convergence_20260328`  
**Subsystem:** `core_pipeline` (authoring assist, post-stack)  
**Authority:** `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md` (engine purity, persona alignment); `specs/PHOENIX_V4_5_WRITER_SPEC.md` for writer discipline where applicable  
**Status:** Draft contract for implementation (no runtime code in this change)

## Purpose

When the spine pipeline stacks all available layers per section, the mathematical ceiling is high (~548 words/section in the architecture described in `docs/SESSION_HANDOFF_2026_04_12.md`), but real compiles can still land **under the per-section budget** (missing template slice, thin enrichment row, failed injection, beatmap mismatch, etc.). Pearl_Writer expansion is the **bounded prose-development step** that brings a thin stacked section up to delivery length **without breaking teacher atom voice** or arc intent.

## 1. Trigger condition

Pearl_Writer expansion runs **only** when all of the following are true:

1. **Stacked packet exists:** `compose_section_packet` in `phoenix_v4/rendering/section_packet_composer.py` has returned a packet for `(chapter_index, section_index)`.
2. **Injection pass complete:** Legacy template text inside the composer has already passed `resolve_injections` (injection marks resolved or explicitly logged as failed in packet warnings).
3. **Thin section:** Let `target_words` be the beatmap/pipeline target for that section (typically **450** for long-form tiers). Activate expansion when  
   `packet["word_count"] < min(350, target_words - 100)`  
   i.e. default **&lt; 350 words** when `target_words` is 450, or more generally when the packet is more than ~100 words short of target.  
4. **Quality profile allows assist:** Gate on the same `quality_profile` / pipeline flags used elsewhere (e.g. skip in strict regression snapshots unless explicitly enabled).

**Non-triggers:** Placeholder storms, empty teacher id, or missing arc context — those are data/pipeline errors; fix upstream instead of expanding.

## 2. Input contract

Pearl_Writer receives a single **structured request** (JSON-serializable dict), including at minimum:

| Field | Description |
|--------|-------------|
| `packet` | Full return dict from `compose_section_packet` (`text`, `word_count`, `target_words`, `under_target`, `sources_used`, `warnings`, `section_type`, indices). |
| `spine_context` | Topic, persona, teacher, engine, format, arc id / plan hash slice, and any knob/beatmap identifiers needed for determinism. |
| `teacher_voice` | Canonical teacher atom voice envelope: approved TEACHING/QUOTE atoms or a pinned **atom voice digest** (hashes + short excerpts) for this teacher × topic × engine. |
| `layer_preservation` | Ordered list of semantic sections or markers derived from `sources_used` so the model does not collapse layers blindly. |
| `expansion_budget` | Max added words (default `target_words - word_count`, capped e.g. 400). |
| `seed` | Deterministic seed string for any stochastic decoder (e.g. `plan_hash:chapter:section:expansion_v1`). |

Optional: beatmap slot JSON, enrichment slot JSON, exercise phase metadata, and `chapter_flow_report` prior pass for context (read-only).

## 3. Output contract

Pearl_Writer returns:

| Field | Description |
|--------|-------------|
| `text` | Final section prose, **≥ min(450, target_words)** words (or ≥ `target_words` if target &gt; 450). |
| `word_count` | Integer count consistent with pipeline tokenizer (same as `_word_count` in section packet composer unless upgraded atomically). |
| `sources_used_delta` | New sources introduced (should be **empty** unless explicitly allowed, e.g. `pearl_writer:clarifying_bridge`). |
| `layer_map` | Mapping of paragraph or stanza → logical layer (`bridge`, `legacy_template`, `enrichment`, `teacher_atom`, `depth_module`, `journey_intro`, …) so compose/render can audit. |
| `warnings` | Non-fatal issues (e.g. “could not verify atom id X”). |

**Hard rules:**

- Preserve **layer ordering** implied by `compose_section_packet`: bridge → journey intro → legacy → enrichment → teacher → depth.
- Do **not** remove or rewrite existing stacked sentences except for **local coherence glue** (transitions) ≤ 15% of added words, and only when labeled in `warnings`.

## 4. Voice fidelity

- **Teacher atom voice is law:** Expansion must read as the same teacher already selected for the section; use the provided `teacher_voice` corpus as the only stylistic reference.
- **No new claims:** Do not introduce new clinical, spiritual, or mechanistic assertions not present in the stacked packet or pinned atoms. Clarify, exemplify, and bridge only.
- **Persona alignment:** Register, cultural framing, and second-person stance must match persona + topic from `spine_context`.
- **Engine purity:** Output must remain compatible with `clean_for_delivery` and downstream gates (no markdown artifacts, no meta-commentary).

## 5. Quality gate

Expanded sections must pass the **existing chapter flow gate** used for composed chapters:

- Evaluate with `phoenix_v4.quality.chapter_flow_gate` APIs (same as tests in `tests/test_chapter_flow_gate.py` and book render integration).
- If expansion fails the gate, the pipeline must **fall back** to the pre-expansion packet (or mark chapter as failed), log the failure, and emit a structured report row — no silent downgrade.

## 6. Integration point

Order in the spine pipeline:

1. … → `compose_section_packet` (includes injection resolution and `clean_for_delivery` on the stacked body).  
2. **→ Pearl_Writer expansion (this spec)** — runs only if trigger condition holds.  
3. → Chapter / book assembly (`chapter_composer` / `book_renderer` paths).  
4. → **Quality gates** (chapter flow, budget, experience, etc.).

Pearl_Writer is **not** a replacement for enrichment, depth, or legacy template loading; it is a **last-mile length and coherence pass** when those layers still underfill after stacking.

## 7. Pilot plan

| Dimension | Choice | Rationale |
|-----------|--------|-----------|
| Topic | **anxiety** | Richest V2 somatic coverage + existing pilot artifacts under `artifacts/pilot/` family. |
| Format tier | **`deep_book_6h`** (or current catalog id for 6h deep slice) | Worst-case word budget stress; validates 450-word section target. |
| Pipeline mode | **`--pipeline-mode spine`** | Only path where stacked packets + injection resolver apply. |
| Success metrics | Section word histogram (p50/p90), `under_target` rate → ~0, chapter flow pass rate ↑ vs baseline without expansion | Quantitative proof before enabling on all 15 topics. |

## Revision

Bump the `expansion_v1` version suffix in `seed` when changing prompts or post-processing so A/B artifacts remain comparable.
