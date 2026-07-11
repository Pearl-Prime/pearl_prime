# MANGA LAYOUT AGENT SPECIFICATION

**Canonical singleton** for manga/webtoon/self-help page & strip composition, reading-path grammar, spreads, and format-family routing.

| Field | Value |
|---|---|
| Spec ID | `MANGA_LAYOUT_AGENT_SPEC` |
| Version | `2.0.0-reconcile-2026-07-11` |
| Status | **Authored candidate** (doctrine reconcile; rectangular frame engine is LIVE scaffold, not full grammar) |
| Acceptance layer | authored candidate |
| Workstream | `ws_manga_bubble_page_grammar_reconcile_20260711` |
| Companion singleton | `specs/LETTERING_AGENT_SPEC.md` |
| Human-readability authority (do not weaken) | `artifacts/qa/MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md` |

> **Lineage (RETAIN):** `docs/MANGA_RENDER_LINEAGE_DECISION_2026-05-29.md` retains LETTERING/LAYOUT as the post-render composition layer. This document is the reconciled authority shell for the **layout** half. SpiritualTech v1.0 “Status: Production” overlay-render fiction is demoted to **Appendix H** and is not production law.

---

## 0. Authority, live binding, and honesty rules

### 0.1 What this spec owns (primary)

1. Format-family mode gates (`print_manga_page`, `vertical_scroll_webtoon`, `self_help_illustrated`).
2. Reading-path-driven page/strip grammar (beyond rectangular bbox packing).
3. Panel reading graphs; host for page-aware bubble Pass B.
4. Spread-level composition (recto/verso, page-turn, binding, DPS safety).
5. `+` / T-junction ambiguity-scored lint.
6. Narrative-beat semantics consumed by layout decisions.
7. Page/strip measurement profiles and heuristic labeling.
8. Layout machine gates vs mandatory visual review.

### 0.2 What this spec does not own

- Bubble semantics, JLREQ shaping, SFX semantic pipeline, localization reflow ladder — **primary:** `specs/LETTERING_AGENT_SPEC.md`.
- Panel art generation / layered bank assembly — V5 layered architecture.
- July 9 HR forbidden patterns — remain authoritative.

### 0.3 Live binding (current reality — do not overclaim)

| Capability | Live module / config | Status vs this doctrine |
|---|---|---|
| Rectangular page frame engine | `phoenix_v4/manga/chapter/page_frame.py` + `config/manga/page_grid_templates.yaml` | **partial** — bbox scaffold, not full reading-path grammar |
| Legacy strip compose | `phoenix_v4/manga/chapter/page_compose.py` | **aligned** as thin wrapper / fallback |
| Vertical-scroll composer | `phoenix_v4/manga/chapter/webtoon_compose.py` | **aligned** as separate family (beat gutters) |
| Catalog format enums | `schemas/manga/series_plan.schema.json` | **aligned** routing vocabulary |
| Panel layout templates | `config/manga/panel_layout_templates/*.yaml` | **partial** — catalog/routing; not fully loaded by `page_frame` compose |
| Spread roles / recto-verso | width×2 + `center_gutter_px` only | **partial / missing** planner |
| Panel reading graph | list order only | **missing** as graph |
| `+` junction lint | HR-F13 UNENFORCED | **missing** |
| Layout-owned bubble rasterization | SpiritualTech §7 | **superseded** — LIVE stamps bubbles in lettering v2 **before** compose |

**Honesty rule:** Do not claim the frame engine is a full manga page grammar. Do not claim Layout rasterizes Comic Sans bubbles.

### 0.4 Cross-spec interface

| Decision | Primary owner | Cross-ref |
|---|---|---|
| D1 / D10 Two-pass bubbles | Lettering §3; Layout hosts Pass B (§3.2) | Lettering §3.3 |
| D2 Reading-path page grammar | Layout §4 | Lettering §4 (bubble trail) |
| D3 Precedence | Layout §2 (page application) | Lettering §2 |
| D4 / D16 Format families | Layout §1 | Lettering §10 |
| D6 Junction lint | Layout §6 | optional Lettering disambiguation cues |
| D7 Spreads | Layout §7 | Lettering §10 (binding-safe text) |
| D8 Panel graphs | Layout §5 | Lettering §4 |
| D11 Narrative beats | Layout §8 | Lettering density budgets |
| D15 Gates | Layout §10 | Lettering §11 |

---

## 1. Format families and mode gates (D4, D16)

Treat these as **separate composition families**. Do not inherit print-spread grammar into webtoon, or manga panel grammar into self-help, unless explicitly routed.

### 1.1 `print_manga_page`

- Bounded pages; RTL or configured reading direction.
- Spread composition, recto/verso, center binding, page-turn reveals, double-page safety.
- LIVE composers: `page_frame` / `page_compose` with `bw_page_rtl` / `color_page` catalog templates.
- Schema anchors: `bw_page_manga`, `color_page_manga`.

### 1.2 `vertical_scroll_webtoon`

- Single-axis vertical reading; scroll-distance pacing; mobile readability; tile/export constraints.
- **No inherited print-spread grammar.**
- LIVE composer: `webtoon_compose.compose_episode_strips` + `GUTTER_PX_BY_BEAT`.
- Schema anchor: `color_vertical_webtoon`.
- Template: `config/manga/panel_layout_templates/vertical_scroll_webtoon.yaml`.

### 1.3 `self_help_illustrated` (third family)

- Illustration-led instructional / reflective composition.
- **No assumed RTL panel grammar**, **no assumed print-manga density**, **no assumed webtoon scroll pacing** unless explicitly routed.
- LIVE: catalog/schema + `self_help_illustrated.yaml` routing boundary; **not** a full dedicated grammar engine inside `page_frame` yet.
- Schema anchor: `direct_self_help_illustrated`.

### 1.4 Mode gate rule

Series plans MUST declare format (and master/flatten exports per schema). Layout entrypoints MUST select the family composer explicitly. Webtoon as a mere `reading_direction` enum value is **insufficient** doctrine (supersedes SpiritualTech §5.3 framing).

---

## 2. Precedence ladder (D3) — page/spread application

Same global order as Lettering §2:

1. Explicit artistic override  
2. Narrative beat and emotional intensity  
3. Format-family constraints  
4. Locale constraints  
5. Genre bias  
6. Global fallback  

Genre profiles in `page_grid_templates.yaml` (gutters, borders, max panels) are **biases**, not absolute controllers. A quiet beat inside a shonen series may legally select a calmer profile via (1)–(2).

---

## 3. Composition pipeline and Pass B host (D1, D10)

### 3.1 Layout role (reconciled)

Layout assembles **already-rendered** (and usually **already-lettered**) panel images into pages or vertical strips, validates reading path, hosts **Pass B** bubble correction, and applies finish-order constraints for SFX relative to borders.

Layout does **not** author dialogue. Layout does **not** own Pass A bubble synthesis (Lettering).

### 3.2 Pass B host interface

After family compose:

1. Invoke lettering page-aware validation (`LETTERING_AGENT_SPEC` §3.3 criteria).
2. Allow lettering mutations (nudge/resize/regenerate).
3. As final fallback, permit **template / path substitution** (layout-owned).

**Status:** FUTURE wiring — required by doctrine.

### 3.3 LIVE pipeline (honest)

```
rendered panels
    → lettering v2 stamps bubbles onto panels     [Lettering LIVE]
    → page_frame OR webtoon_compose OR self_help route
    → (Pass B missing)
    → export
```

---

## 4. Reading-path-driven page grammar (D2)

Rectangular bbox templates are a **baseline generator**, not the full grammar.

### 4.1 LIVE baseline

`page_grid_templates.yaml` cells in normalized page space; RTL via `_mirror_cells_rtl`; genre profiles tune gutter/border/margin.

### 4.2 Required grammar primitives (SPECCED / FUTURE)

Beyond rectangles, the layout system MUST be able to represent:

- bleed panels and borderless inserts  
- diagonal cuts  
- blockage columns / vertical segments  
- overlap exceptions  
- genre-weighted asymmetry  
- explicit guiding path across the page  

Research support: readers navigate via hierarchic constituents, blockage, overlap — not fixed Z-path alone. Asian corpus traits (more vertical segments, bleeds) inform defaults, not universal hard law (`source_status: heuristic` unless validated as constraint).

### 4.3 Webtoon path grammar

Vertical family uses scroll-distance, beat gutters, and mobile viewport pacing — not print grid inheritance. LIVE: `webtoon_compose` beat-type gutters are the correct family direction.

---

## 5. Panel reading graphs (D8 — layout half)

**Primary owner: Layout.**  
**Cross-ref:** Lettering §4 for bubble graphs.

Emit an explicit directed graph:

```text
panel_01 -> panel_02 -> panel_03
                       |
                       -> panel_04
```

Validate:

- unambiguous panel order  
- agreement with bubble graph  
- focal subjects support the path  
- no forced backtracking  

List order / `reading_order` integers are serializations, not ambiguity proofs.

---

## 6. Junction lint (D6) — ambiguity-scored, not blanket auto-fail

**Primary owner: Layout.**

`+` (four-way) intersections are **not** automatic hard fails.

Validator MUST assess **reading-order ambiguity**:

| Severity | When |
|---|---|
| `error` | Junction yields two plausible reading orders |
| `warning` | Other cues (size, balloon position, character direction, overlap, saliency) disambiguate |
| allow | Only with explicit `allow_ambiguous_junction: true` for intentional experimental pages |

**Cross-ref HR-F13:** four-way intersection remains a readability concern; today **UNENFORCED** — this section defines the intended gate semantics without weakening HR.

T-junction preference remains a **strong default heuristic**, not an absolute geometric religion.

---

## 7. Spread-level composition (D7)

Print family pages are also composed as **two-page spreads**.

### 7.1 Required planner concepts (SPECCED / FUTURE)

- recto vs verso  
- page-turn reveal placement  
- double-page spreads  
- center-binding loss  
- bleed/trim safety  
- whether face/text/focal object crosses the binding  
- left-page exit / right-page entry direction  
- chapter-open / chapter-close page roles  

Suggested schema extensions (downstream; not edited in this lane’s registry):

```yaml
page_role: setup | escalation | reveal | aftermath | chapter_open | chapter_close
spread_role: independent | paired | double_page
page_side: recto | verso | auto
page_turn_priority: low | medium | high
```

Target modules (FUTURE): `spread_plan.py`, `spread_validate.py`, `config/manga/spread_profiles.yaml`.

### 7.2 LIVE honesty

`page_frame.render_framed_page` may double width and insert `center_gutter_px` (config default **60**, not the historical SpiritualTech **600**). That is **geometry scaffolding**, not a spread planner. Do not equate the two.

**Cross-ref:** Lettering Pass B must respect binding/trim proximity for print families.

---

## 8. Narrative-beat semantics (D11)

Layout solvers MUST NOT decide page architecture from panel count / HOOK/SCENE labels alone.

Each beat SHOULD carry (SPECCED):

```yaml
importance: 0.0–1.0
perceived_duration: instant | short | sustained | timeless
transition: continuous | action_jump | time_jump | location_change
dialogue_load: low | medium | high
speaker_count: 0–n
reveal: none | minor | major
orientation_required: true|false
desired_pace: slow | normal | fast
visual_anchor: character | object | environment | text
```

**LIVE partial:** webtoon `beat_type` → gutter height only. Page grids largely ignore beat semantics — gap to close.

**Cross-ref:** Lettering uses dialogue_load / intensity for density budgets; does not own page template choice.

---

## 9. Measurement profiles and heuristic labeling (D5, D17)

Gutters, bleeds, borders, page pixel sizes, and webtoon segment heights are **profile defaults** unless true technical/export constraints (e.g., Canvas width, file-size hard caps in templates).

Required labeling:

```yaml
source_status: heuristic | technical_constraint
output_profile: <format family + trim/device>
recommended_range: [...]
hard_minimum: null
```

SpiritualTech universal constants (60px gutters, 180px bleed, 5200×7200 page, 1080 webtoon width as “law”) are **demoted to historical heuristics**. Prefer LIVE config values and export-profile files.

---

## 10. Machine gates vs mandatory visual review (D15)

### 10.1 Machine gates (layout)

- panel-order ambiguity score  
- junction ambiguity score (§6)  
- gutter consistency vs transition/beat  
- focal-saliency conflict (objective proxies only)  
- binding/trim violations (print)  
- format-family mode-gate violations  
- export constraints (segment height, file size) when marked `technical_constraint`  

### 10.2 Mandatory visual review

Layout MUST NOT claim “publication-ready / perfection is the baseline” from automation alone. Machine checks + human visual review. Subjective art quality is out of full machine scope.

**Cross-ref:** Lettering §11; HR assembly rules.

---

## 11. Text overlay / finish order (reconciled)

### 11.1 What Layout composites

Prefer compositing **pre-lettered** panel PNGs (LIVE). Layout may still define **finish z-order** for elements applied at page scope (cross-panel SFX, captions that span, crop marks).

### 11.2 SFX z-order contract (cross-ref Lettering §6)

SFX ordering relative to art, panel borders, and balloons MUST be explicit per format profile. Do not treat SFX as just another speech bubble in the page overlay stack.

### 11.3 Superseded claim

SpiritualTech §7 algorithms that had Layout rasterize all bubbles/SFX with example font “Comic Sans MS” are **superseded**. Fonts resolve only via `fonts/manga/FONT_REGISTRY.yaml` under Lettering ownership.

---

## 12. Page types (craft retained, enforcement labeled)

| Page type | Intent | LIVE / SPECCED |
|---|---|---|
| Standard | Multi-panel framed page | LIVE bbox templates |
| Splash | Full-bleed emphasis | LIVE page_type rule partial |
| Silent | Wider gutters / no lettering | partial |
| Double-spread | Spread geometry + future planner | partial geometry only |

---

## 13. Quality gates — layout level (reconciled)

| Gate | Class | Notes |
|---|---|---|
| Format-family mode gate | machine | required |
| Panel reading-graph unambiguity | machine FUTURE | |
| Junction ambiguity | machine FUTURE | not blanket `+` fail |
| Spread binding/trim | machine FUTURE | |
| Beat/profile consistency | machine FUTURE | |
| Pass B invoked for lettered print/webtoon | machine FUTURE | |
| Visual review signoff | human mandatory | |

---

## 14. Implementation pointers (non-runtime this lane)

Preferred Pearl_Dev evolution:

- Keep `page_frame` + `page_grid_templates.yaml` as rectangular generator foundation.
- Add `page_reading_graph.py`, `page_layout_validate.py`, `page_layout_solver.py`.
- Add spread planner/validator + schema fields.
- Keep `webtoon_compose` as the vertical family (do not merge into print grids).
- Wire `self_help_illustrated` as an explicit third composer/route, not a manga grid alias.
- Host Pass B after compose.

See `artifacts/qa/MANGA_BUBBLE_PAGE_LAYOUT_IMPLEMENTATION_MAP_2026-07-11.tsv`.

---

## Appendix H — Historical SpiritualTech layout agent (non-normative)

> **HISTORICAL / NON-NORMATIVE.** Former header `Status: Production` overclaimed. Former §7 text-overlay pipeline and Comic Sans examples are rejected as authority. Former double-spread center gutter **600px** conflicts with LIVE **60px** scaffolding — neither number is universal law; both are heuristics pending profile labeling.

Salvageable ideas: reading-direction tables as **defaults**, silent-page breathing gutters, splash borderless intent, QC checklist structure (reframed under §10).
