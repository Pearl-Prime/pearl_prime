# LETTERING AGENT SPECIFICATION

**Canonical singleton** for manga/webtoon speech-bubble semantics, placement, typography, SFX, and localization reflow.

| Field | Value |
|---|---|
| Spec ID | `LETTERING_AGENT_SPEC` |
| Version | `2.0.0-reconcile-2026-07-11` |
| Status | **Authored candidate** (doctrine reconcile; not a claim that all gates are CODE-WIRED) |
| Acceptance layer | authored candidate |
| Workstream | `ws_manga_bubble_page_grammar_reconcile_20260711` |
| Companion singleton | `specs/MANGA_LAYOUT_AGENT_SPEC.md` |
| Human-readability authority (do not weaken) | `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` |

> **Lineage (RETAIN):** `docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md` retains LETTERING/LAYOUT as the post-render text/composition layer. This document is the reconciled authority shell for that layer’s **lettering** half. SpiritualTech v1.1 agent-prompt fiction is demoted to **Appendix H** and is not production law.

---

## 0. Authority, live binding, and honesty rules

### 0.1 What this spec owns (primary)

1. Bubble **semantics** vs **appearance** separation.
2. Panel-local bubble candidate synthesis (**Pass A**) and the lettering half of the **two-pass** contract.
3. Bubble reading-order graph (within and across panels, as lettering metadata).
4. JLREQ-grade typography obligations.
5. Independent SFX semantic/render pipeline (not a bubble variant).
6. Localization reflow ladder.
7. Lettering-side measurement profiles and heuristic labeling.
8. Lettering machine gates vs mandatory visual review.

### 0.2 What this spec does not own

- Page/spread geometry, panel reading graphs, `+` junction lint, format-family routing, narrative-beat → page grammar — **primary owner:** `specs/MANGA_LAYOUT_AGENT_SPEC.md`.
- Layered panel art assembly — `docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` and bank assembly contracts.
- July 9 human-readability forbidden patterns — remain authoritative; this spec must not weaken them.

### 0.3 Live binding (current reality — do not overclaim)

| Capability | Live module / config | Status vs this doctrine |
|---|---|---|
| Panel-first bubble stamp | `phoenix_v4/manga/chapter/bubble_render_v2.py` → `render_bubbles_onto_panel_v2` | **aligned** (Pass A-ish; no multi-candidate solver yet) |
| Genre resting styles | `config/manga/genre_bubble_styles.yaml` | **aligned** (bias, not absolute control) |
| Fonts / locale roles | `fonts/manga/FONT_REGISTRY.yaml` | **aligned** foundation |
| Vertical CJK + furigana | `cjk_text_shaper` / `furigana_renderer` (via v2) | **partial** — not full JLREQ matrix |
| SFX | stamped inside `render_bubbles_onto_panel_v2` | **partial / misleading if called a pipeline** |
| Page-aware bubble reflow (Pass B) | *(absent)* | **missing** |
| Localization reflow ladder | shrink/fit heuristics only | **partial** |
| LLM “Lettering Agent” producing `lettering_spec.json` | SpiritualTech path | **not the live orchestrator** |

**Honesty rule:** Examples and gates below are labeled `LIVE`, `SPECCED`, or `FUTURE`. Do not present `SPECCED`/`FUTURE` as already implemented.

### 0.4 Cross-spec interface (mandatory)

Decisions that require both lettering and layout have **exactly one primary owner** here or in the layout spec, plus a named cross-reference. Interface summaries must not redefine the primary authority.

| Decision | Primary owner | Cross-ref in other spec |
|---|---|---|
| D1 Panel-first + page-aware final correctness | Lettering §3 (Pass A) + Layout §3 (Pass B host) | Layout §3.2; Lettering §3.3 |
| D10 Two-pass bubble solver | Lettering §3 | Layout §3.2 |
| D3 Precedence ladder | Shared table; lettering owns bubble application (§2) | Layout §2 |
| D8 Reading graphs | Layout owns panel graph; Lettering owns bubble graph (§4) | Layout §5 |
| D13 SFX pipeline | Lettering §6 | Layout §7 (z-order / finish) |
| D15 Machine vs visual review | Both (§9 / Layout §10) | — |

---

## 1. Role and pipeline position (reconciled)

The lettering subsystem places and styles **dialogue, narration/captions, and (separately) SFX** onto panel imagery for a declared **format family**, then participates in **page-aware correction** after page/strip composition.

### 1.1 Production path (LIVE-oriented)

```
chapter_script (+ locale text)
        ↓
lettering_from_script / intensity + genre register
        ↓
Pass A: panel-local bubble synthesis  →  bubbled panel PNG + text manifest
        ↓
Layout compose (page_frame | webtoon_compose | self_help route)
        ↓
Pass B: page-aware bubble validate / reflow   [FUTURE — required by this doctrine]
        ↓
SFX finish pass (may span panels)             [FUTURE as independent module]
        ↓
machine lettering QA + mandatory visual review
```

### 1.2 Boundary rules

- Does **not** rewrite dialogue or invent captions absent from script (verbatim rule retained).
- **May** consume rendered panel pixels for speaker/face geometry (LIVE: face cascade in v2). The old claim “Lettering never consumes images” is **superseded**.
- Does **not** own page grid selection, spread roles, or panel reading-path grammar (Layout).
- Does **not** claim publication-ready art quality from machine checks alone (§9).

---

## 2. Precedence ladder (genre biases; does not control)

**Primary owner for bubble application of this ladder: Lettering.**  
**Cross-ref:** Layout §2 applies the same ladder to page/spread choices.

Order (highest wins):

1. Explicit artistic override (per-line / per-page author fields)
2. Narrative beat and emotional intensity
3. Format-family constraints (`print_manga_page` | `vertical_scroll_webtoon` | `self_help_illustrated`)
4. Locale / typography constraints
5. Genre bias (resting register)
6. Global fallback

**LIVE alignment:** `config/manga/genre_bubble_styles.yaml` already documents override → genre-default → intensity. This section elevates that pattern to doctrine and forbids genre from outranking (1)–(4).

Genre research essays and measurement tables are **defaults/recommendations** (`source_status: heuristic`) unless a true technical constraint is named (export width, JLREQ prohibition, trim safety).

---

## 3. Two-pass bubble solver (D1, D10) — primary lettering contract

### 3.1 Decision statement

Bubble **candidate generation stays panel-first**. **Final correctness is page-aware.**

### 3.2 Pass A — panel-local synthesis (primary: Lettering)

**Status:** LIVE foundation in `render_bubbles_onto_panel_v2`; multi-candidate scoring is FUTURE.

Pass A MUST (doctrine):

1. Anchor each dialogue bubble to panel-local coordinates and speaker geometry.
2. Generate one or more candidates per utterance and score at least:
   - speaker association / tail-to-mouth
   - face and hand occlusion
   - reserved negative-space use
   - text fit / coverage budget
   - local reading order
   - tail crossings and bubble crossings
   - panel-boundary safety
3. Emit a text manifest preserving original utterance, locale utterance, geometry, and applied edits.
4. Respect coverage budgets as **profile defaults** (LIVE default `coverage_limit=0.30` is a heuristic hard-ish cap, not universal art law).

### 3.3 Pass B — page-aware correction / reflow (interface)

**Primary orchestration host:** Layout after page/strip assembly (`MANGA_LAYOUT_AGENT_SPEC` §3.2).  
**Lettering owns** the bubble rescoring criteria and permitted mutation ladder.

Pass B MUST rescore:

- page / strip eye path
- unintended bubble priority
- cross-panel alignment and lead-in
- density clustering
- focal-point competition
- trim / binding proximity (print families)
- neighboring-panel confusion

Mutation ladder (lettering): small nudge → resize → local regeneration → request layout template substitution (layout-owned fallback).

**Status:** FUTURE — absence is an honest gap, not a silent pass.

---

## 4. Bubble reading graph (D8 — lettering half)

**Primary owner for bubble order graphs: Lettering.**  
**Cross-ref:** Layout §5 owns panel reading graphs; both graphs MUST agree.

Represent bubble order as an explicit directed graph (not only coordinates):

```text
bubble_01 -> bubble_02 -> bubble_03
```

Validation targets (SPECCED / FUTURE machine gates):

- unambiguous bubble order within each panel
- agreement with panel reading graph
- final bubble in panel N does not visually lead into the wrong next panel
- no mandatory backtracking

Integer `reading_order` fields remain allowed as a serialization of the graph, not a substitute for ambiguity scoring.

**Cross-ref HR:** `MANGA_HUMAN_READABILITY_ASSEMBLY_RULES` §4 (speech-bubble ordering) remains in force.

---

## 5. Bubble semantics vs appearance (D9)

### 5.1 Semantic layer (`utterance_type`)

Independent of genre paint:

`dialogue | thought | narration | whisper | shout | electronic | telepathy | off_panel | aside | interrupted | trailing_off | simultaneous`

Also support (SPECCED): connected balloon chains, continued speech across balloons, shared/overlapping dialogue, interrupted tails, multiple tails, tailless narration, explicit cross-panel balloons, side-scribbles / free-floating asides.

### 5.2 Appearance layer (style register)

Shape, stroke, fill, tail style, font_role, and intensity deformation are **render bindings** for semantics.

**LIVE:** intensity maps + `genre_bubble_styles.yaml` currently fuse semantic cues into appearance. Doctrine requires progressive separation: infer or author `utterance_type` first; let the style register render it. Genre biases resting appearance only (§2).

---

## 6. SFX pipeline (D13) — not a bubble variant

**Primary owner: Lettering (new SFX lane).**  
**Cross-ref:** Layout §7 for z-order relative to art, borders, and bubbles.

SFX MAY:

- sit inside or outside panels
- cross panel borders
- sit behind characters
- become environmental composition
- use warped baselines / custom outlines
- remain untranslated, take glosses, or be replaced per locale policy

Target modules (FUTURE — do not claim LIVE): `sfx_plan.py`, `sfx_render.py`, `sfx_localization.py`, plus `config/manga/sfx_styles.yaml`.

**LIVE honesty:** v2 stamps SFX strings as red display text inside the bubble renderer. That is an **interim stamp**, not the SFX pipeline. Do not model SFX solely as `type: sound_effect` bubbles.

---

## 7. JLREQ-grade typography (D12)

“Vertical CJK supported” is **necessary but not sufficient**.

### 7.1 LIVE foundation

- Vertical CJK block rendering
- Furigana / ruby attachment
- Locale font roles via `FONT_REGISTRY.yaml`
- Publish-time text manifests

### 7.2 Required JLREQ matrix (SPECCED — FUTURE enforcement)

| Obligation | Notes |
|---|---|
| Kinsoku line-start / line-end prohibitions | Hard linguistic constraint where applicable |
| Unbreakable character sequences | Hard where JLREQ requires |
| Punctuation placement + vertical glyph substitution | |
| Small kana / prolonged sound marks | |
| Tate-chu-yoko | |
| Mixed Latin/CJK orientation | |
| Ruby longer than base; ruby collision with neighbors | |
| Emphasis dots / *bouten* | |

Cite W3C JLREQ as the external technical reference. Only true linguistic/technical requirements become hard gates; point sizes and padding remain profile heuristics (§8).

---

## 8. Measurement profiles and heuristic labeling (D5, D17)

Exact measurements (pt sizes, mm gutters inside bubbles, coverage ratios, webtoon spacing borrowed for lettering density) are **profile defaults** unless marked hard.

Required metadata shape for lettering profiles:

```yaml
source_status: heuristic   # or technical_constraint
output_profile: bw_print_b6 | webtoon_canvas_800 | self_help_illustrated | ...
recommended_range: [...]
hard_minimum: null         # set only for true constraints
```

Research figures from deep-research / genre essays remain **recommendations** until promoted with an explicit technical rationale.

---

## 9. Localization reflow ladder (D14)

When translated text does not fit, apply this deterministic ladder (SPECCED; LIVE is partial shrink-to-fit only):

1. Rebreak text  
2. Adjust internal padding within bounds  
3. Expand bubble into reserved space  
4. Alter bubble aspect ratio  
5. Reduce font size to locale/output minimum  
6. Split into connected balloons  
7. Request editorial condensation  
8. **Fail visibly** rather than overflow silently  

Manifest MUST retain: original utterance, translated utterance, applied edit steps, final geometry.

---

## 10. Format-family lettering implications (cross-ref Layout §1)

Lettering MUST branch behavior by format family (Layout owns routing; Lettering owns text behavior):

| Family | Lettering implications |
|---|---|
| `print_manga_page` | RTL/LTR bubble graphs; binding/trim avoidance in Pass B; spread-safe text |
| `vertical_scroll_webtoon` | Single-axis order; mobile density; no print-spread lettering grammar |
| `self_help_illustrated` | Illustration-led; no assumed manga balloon density or RTL panel grammar |

---

## 11. Machine-enforceable gates vs mandatory visual review (D15)

### 11.1 Machine gates (lettering) — objective

Suggested enforceable checks (mix of LIVE / FUTURE):

- bubble-order ambiguity score  
- speaker-tail correctness  
- tail-crossing count (HR-F08 today **UNENFORCED**)  
- face/eye/mouth occlusion (HR-F09 **UNENFORCED**)  
- text overflow / minimum effective size  
- bubble-to-panel area ratio / coverage  
- locale typography violations (JLREQ matrix)  
- reflow-ladder exhaustion → visible fail  

### 11.2 Mandatory visual review

Subjective art quality, emotional register fit, and “feels like manga” judgment are **not** fully machine-enforced. Ship doctrine: machine QA **plus** mandatory visual inspection. Do not claim publication perfection from automated gates alone.

**Cross-ref:** Layout §10; HR assembly rules remain binding for readability defects.

---

## 12. Silence, density, and end-hook (retained craft rules — SPECCED)

The following SpiritualTech craft rules remain **normative intent** for scripts that carry the fields, but are **not** all LIVE-wired in `bubble_render_v2`. Label enforcement honestly:

| Rule | Intent | Enforcement class |
|---|---|---|
| Silent panels get no invented lettering | Preserve ma | SPECCED |
| `silence_guard` density reduction | Protect silence adjacency | SPECCED |
| SFX silence proximity (3-panel) | Avoid SFX shouting into silence | SPECCED |
| First bubble after silence | Soft re-entry | SPECCED |
| End-hook verbatim delivery | Blocking when field present | SPECCED |
| Dialogue verbatim / no rewrite | Always | LIVE intent + SPECCED gate |
| Caption redundancy flagging | Advisory | SPECCED |

Full historical schemas and worked silence examples: **Appendix H**.

---

## 13. Quality gates — lettering level (reconciled)

| Gate | Class | Notes |
|---|---|---|
| Verbatim dialogue hash / no silent rewrite | machine | retain |
| Coverage budget within profile | machine (LIVE partial) | heuristic profile |
| Pass A occlusion / tail scores | machine FUTURE | |
| Pass B page-aware score | machine FUTURE | requires Layout host |
| JLREQ matrix | machine FUTURE | |
| Reflow ladder visible fail | machine FUTURE | |
| HR-F08 / HR-F09 | machine FUTURE | do not weaken HR |
| Visual review signoff | human mandatory | |

---

## 14. Implementation pointers (non-runtime this lane)

Downstream Pearl_Dev lane should extend live modules toward this doctrine without inventing a parallel SpiritualTech agent runtime. Preferred evolution path:

- Keep `bubble_render_v2.py` as Pass A host; add candidate scoring.
- Add `bubble_page_validate.py` / Pass B called from layout compose.
- Split SFX out of the bubble stamp path.
- Extend shaper for JLREQ matrix items.
- Encode reflow ladder in locale lettering profiles.

See `artifacts/qa/MANGA_BUBBLE_PAGE_LAYOUT_IMPLEMENTATION_MAP_2026-07-11.tsv`.

---

## Appendix H — Historical SpiritualTech lettering_spec (non-normative)

> **HISTORICAL / NON-NORMATIVE.** Retained for salvage of silence-field vocabulary and example shapes. Not the live orchestrator. Schema examples that used absolute px with fonts like “Comic Sans MS” in the Layout spec are rejected; fonts resolve only through `fonts/manga/FONT_REGISTRY.yaml`.

### H.1 Former pipeline claim (superseded)

The v1.1 claim that Lettering never consumes images and that an LLM Lettering Agent always emits `lettering_spec.json` for Layout to rasterize bubbles is **superseded** by the LIVE v2 stamp-before-compose path and by §3’s two-pass contract.

### H.2 Salvageable field vocabulary

`silence_confirmed`, `silence_guard`, `first_after_silence`, `caption_redundancy_flag`, `text_verbatim_hash`, `end_hook`, and per-bubble `reading_order` remain useful names for script/lettering manifests when wired.

### H.3 Former system-prompt and Chapter-9 worked example

Treat prior §8–§9 narrative examples as **illustrative craft**, not executable production contracts, until a LIVE test harness asserts them.
