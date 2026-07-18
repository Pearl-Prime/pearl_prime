# Compositing + Word Bubbles + Lettering Technical Reference for Phoenix Omega
## Date: 2026-04-25
## Researcher: Pearl_Research (parallel agent to /tmp/webtoon_technical_reference.md and /tmp/rakuten_ai_chat_research.md)
## Scope: Compositing craft, lettering craft, multi-language text overlay engineering. **Does NOT duplicate** the WEBTOON technical-spec or Japan-market-economics research running in parallel.

---

## Executive Summary (≈200 words)

Phoenix Omega's "build from layers" production model is **strongly favored by vertical webtoon and weakly fit to traditional B&W page manga**. The reason is structural, not stylistic: webtoon expects flat-color, separable layers, full-color sRGB, mobile-readable type at 12-30 px, and machine-friendly tile heights ≤ 10000 px (LINE Manga Indies spec). Page manga assumes hand-toned screentone, dense ink-line variability, vertical kanji with furigana, and panel layouts whose negative space is integral to pacing — a workflow that punishes layer-stamped composites with visible seams.

Phoenix already has 80% of the bubble layer engineered — `phoenix_v4/manga/chapter/bubble_render.py` (Pillow-based), 9 canonical bubble styles, intensity → font/tail/style mapping, coverage-cap enforcement, and a v2 schema (`schemas/manga/lettering_spec.schema.json`) with `dialogue_lines`, `sfx`, `narrator_caption`, `estimated_bubble_coverage`. **The 20% gap is: (a) no SVG / vector master bubbles (PNG-only output won't survive 2× downscale cleanly), (b) only 4 fonts in `FONT_REGISTRY.yaml` and all `pending`, (c) no per-locale text manifest separation — text is baked at render time, breaking ja_JP/zh_TW/zh_CN/ko_KR localization, (d) no auto-tail-to-mouth speaker geometry, (e) no SFX-on-art layer, and (f) no Source Han Sans / Noto CJK installed.** Recommended pivot: keep webtoon as primary; treat B&W page manga as a secondary "flatten" export from the same layered source.

---

## §1. Internal Audit — What Phoenix Already Does

**Repository: /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924**

### 1.1 Schema layer (lettering)
- `/schemas/manga/lettering_spec.schema.json` (v2.0.0) — `lettering_panels[]` with `panel_id`, `silence_confirmed`, `dialogue_lines[]` (each: `speaker`, `text`, `emotion`, `intensity` ∈ {whisper, calm, normal, excited, shouting, screaming, internal}, `bubble_style` ∈ {round_normal, spiky_emphasis, cloud_thought, square_narration, whisper_dashed, scream_ultra, electronic_sharp, drip_horror, shojo_soft}, `font_override` ∈ {bold_action, light_whisper, italic_internal, all_caps_scream, null}, `tail_style` ∈ {pointer, curved, dotless, broken}, `position_hint` ∈ 8-zone grid, `speech_atom_id`), `sfx[]`, `narrator_caption`, `estimated_bubble_coverage` (0-1).
- `/schemas/manga/lettering_style_bible.schema.json` (minimal — just `fonts: object`).

### 1.2 Render layer (bubble compositing)
- `/phoenix_v4/manga/chapter/bubble_render.py` — Pillow-based, runs **after lettering, before page_compose**. Architecture: Option A (pre-composition), bubbles are stamped onto individual panel PNGs, then page_compose tiles them into row-strips. Public API: `render_bubbles_on_panels(chapter_script, lettering_spec, panel_images_manifest, bubble_style_config, out_dir)` and `render_bubbles_onto_panel(...)`.
- Font resolver tries `fonts/manga/*.ttf|*.otf` first, falls back to `/System/Library/Fonts/Helvetica.ttc`, Liberation, DejaVu, Arial. Sizes per intensity: whisper=10, calm=12, normal=14, excited=16, shouting=18, screaming=22, internal=11 (px).
- Coverage-cap enforcement: `coverage_limit` parameter (default tested at 0.35) — bubbles auto-shrink if total area exceeds cap.
- Zone-to-pixel grid: 8 zones (`top_left`, `top_right`, …, `bottom_center`) with hard-coded fractions in `_ZONE_FRACTIONS`.

### 1.3 Lettering derivation
- `/phoenix_v4/manga/chapter/lettering_from_script.py` — auto-derives lettering_spec from chapter_script writer handoff. Maps `intensity` → `bubble_style`, `font_override`, `tail_style`. Handles both legacy `list[str]` dialogue and v2 `list[dict]` formats.

### 1.4 Page composition
- `/phoenix_v4/manga/chapter/page_compose.py` — composes per-page **horizontal strip** from panel PNGs (row, left-to-right). **Note:** This is **page-format manga layout**, NOT webtoon vertical-strip layout. Webtoon would need a vertical concat. Currently produces `page_001.png`, `page_002.png` … under `out_dir`.

### 1.5 Font registry
- `/fonts/manga/FONT_REGISTRY.yaml` — version 1, 4 fonts ALL marked `pending`:
  - `bangers_display` (Bangers, OFL) — Western display/SFX
  - `patrick_hand_handwritten` (Patrick Hand, OFL) — handwritten dialogue
  - `architects_daughter_note` (Architects Daughter, OFL) — note/caption
  - `noto_sans_jp_body` (Noto Sans JP, OFL) — single Japanese body fallback
- `/scripts/manga/update_font_registry.py` — flips entries to `installed` when files exist on disk.
- **Gap:** No Source Han Sans / Noto Sans CJK Traditional / Simplified / Korean. No SFX-specific Japanese font. No furigana support.

### 1.6 Tests covering bubbles + lettering
- `tests/test_bubble_render.py` — 14 tests: shape coverage (round, spiky, cloud, scream, whisper), caption box, multi-bubble, SFX, manifest immutability, missing-image graceful skip, coverage cap enforcement.
- `tests/test_lettering_spec_v2.py` — schema-roundtrip + str/dict dialogue handling.
- `tests/test_manga_lettering_from_script.py` — intensity → style mapping coverage.
- `tests/test_chapter_production_bubble.py` — end-to-end stage hookup.
- `tests/test_manga_bubble_e2e.py` — image-on-disk verification.
- `tests/test_manga_dialogue_gates.py` — EI MDLG-01..05 dialogue quality gates (engagement, somatic precision, word economy, uniqueness, cohesion). These are **content** gates, not render gates.

### 1.7 What's MISSING (versus industry baseline)
| Capability | Status |
|---|---|
| Vector/SVG master bubbles | **Missing** — PNG-only stamping, edge-blur on rescale |
| Per-locale text manifest separation | **Missing** — text baked at render time, no swap-and-re-export |
| Auto tail-to-speaker-mouth geometry | **Missing** — only zone hint, no character bbox awareness |
| Source Han Sans / Noto CJK installed | **Missing** — only Noto Sans JP listed, status pending |
| SFX-as-separate-art-layer | **Partial** — SFX rendered as text in bubble_render, not as drawn glyphs |
| Furigana support | **Missing** — no schema field, no renderer |
| RTL / vertical kanji rendering | **Missing** — Pillow draws horizontal LTR only |
| Vertical-strip page composer (webtoon) | **Missing** — page_compose.py produces horizontal strips |
| Bubble shape SVG library | **Missing** — shapes hard-coded as Pillow polygons |
| Speaker-aware bubble ordering | **Missing** — placement is zone-hint, no Z-pattern enforcement |

---

## §2. Industry Best Practices — Word Bubbles

### 2.1 Canonical bubble shapes (cross-platform consensus)

Drawing on Blambot's "Comic Book Grammar & Tradition" reference, Todd Klein's blog, and the Wikipedia "Speech balloon" article — the canonical vocabulary is:

| Shape | Function | Phoenix style enum equivalent |
|---|---|---|
| Round/oval, smooth border | Normal speech, neutral | `round_normal` ✅ |
| Spiky/jagged border | Shout, anger, surprise | `spiky_emphasis` ✅ |
| Cloud/scalloped | Internal thought; tail = trailing small bubbles, not pointer | `cloud_thought` ✅ |
| Rectangular caption box | Narration, omniscient narrator | `square_narration` ✅ |
| Dashed border | Whisper, hushed | `whisper_dashed` ✅ |
| Burst (extreme spikes, no tail) | Screaming, explosion-loud | `scream_ultra` ✅ |
| Sharp angular w/ jagged tail | Electronic / phone / radio voice | `electronic_sharp` ✅ |
| Dripping border | Horror, sickness, eerie | `drip_horror` ✅ |
| Soft scalloped (less than thought) | Shojo soft emotion | `shojo_soft` ✅ |
| Wavy border, black-bg w/ white text | Demonic / supernatural / dream | **Missing** |
| Off-panel speech (dotted tail) | Speaker not in frame | **Missing** (tail_style only has pointer/curved/dotless/broken) |
| Singing (musical-note border) | Singing | **Missing** |

**Cite:** Blambot's "Comic Book Grammar & Tradition" page describes CHARACTER (OFF), CHARACTER (WHISPER), CHARACTER (BURST), CHARACTER (WEAK), CHARACTER (SINGING) descriptors — these are all distinct render variants Phoenix's tail_style enum collapses. Todd Klein's *Sandman* lettering for Neil Gaiman uses character-locked bubble styles: Dream gets "wavy-edged bubbles, completely black, with similarly wavy white lettering" (a per-character bubble register Phoenix has no schema for).

### 2.2 Tail (pointer) placement rules

**Manga page:** Tail points to the speaking character's **mouth**, never to the body. If the character is off-panel, the tail crosses the panel border ONLY in the direction of the off-panel character — never into a different panel's interior.

**Webtoon vertical:** Tail rules are **looser** because vertical scroll has no panel-border discipline. Tails frequently cross gutters and even free-float. WEBTOON Canvas tutorials (clip-studio.net, S-Morishita Studio) note that **first speaker on the left, last speaker on the right** (Klein's rule) becomes "first speaker higher in scroll, last speaker lower" — a top-to-bottom reading flow rather than left-to-right.

**Algorithm Phoenix needs:** Given character bbox + dialogue speaker_id → compute mouth position (heuristically: bbox center-x, top 30% of head bbox). Phoenix already has the speaker label in `dialogue_lines[].speaker` and panel images, but no character-bbox detection (would need YOLOv8 face detector or MediaPipe). **NO PUBLIC SOURCE** of an open algorithm publishing exact mouth-locator heuristics for stylized art; manga-image-translator (zyddnys/manga-image-translator) inverts this — it detects existing bubble first, then OCRs.

### 2.3 Bubble color, border, and "AIR"

Comicraft's *Comic Book Lettering: The Comicraft Way* (Starkings & Roshell, 2003, still the industry textbook) defines:
- **AIR** = padding between text and balloon edge. Rule of thumb: **one letter-width** of air on all sides. Phoenix's `bubble_render.py` does not expose AIR as a parameter; it's implicit in the polygon-fitting code.
- **Word arrangement** — pyramidal/diamond text shape (short top, longer middle, short bottom) yields naturally round bubbles. Avoid hyphenation. Phoenix uses `textwrap.wrap` which does NOT enforce diamond shape — text is left-justified rectangle.
- **Default colors:** white fill, thin black border (≈ 1.5-3 px at 600 dpi for print, 2-3 px at 96 dpi web). Reverse (black fill, white text) reserved for inner thoughts of supernatural/villain characters.
- **Webtoon convention:** Often **borderless** white bubbles with a soft drop shadow — the panel-less infinite scroll makes hard borders feel boxy. Phoenix should add a `borderless` bool to the bubble_style enum or as a render-config flag.

### 2.4 Multi-bubble ordering

| Format | Rule |
|---|---|
| Western page comic | Z-pattern: top-left → top-right → bottom-left → bottom-right (Klein) |
| Japanese page manga | Top-right → bottom-right → top-left → bottom-left (RTL) |
| Webtoon vertical | Top → bottom (reading order is just scroll order) |
| Phoenix current | `position_hint` zone-grid only — no enforced order |

**Cite:** Klein's "Lettering Placements" blog post: "When two or more characters are talking in a panel, the first speaker should always be on the left, and the last speaker on the right."

---

## §3. Industry Best Practices — Lettering / Typography

### 3.1 Font categories (Blambot consensus)

Comic typography requires **at least 3** distinct font families per project:
1. **Dialogue font** — clean, readable, high-x-height. e.g., Comicraft's Wildwords, Blambot's Anime Ace, Mighty Zeo, Ground Control.
2. **Narration / caption font** — different weight/style from dialogue, often a serif or condensed sans. Comicraft uses different weights of the same family.
3. **SFX font** — expressive, often hand-drawn or display-weight. e.g., Bangers, Komika, Blambot's Badaboom BB, Plok!

A 4th category is increasingly common in webtoon:
4. **Inner-thought / italic dialogue** — italicized version of the dialogue font (Blambot calls this "Internal Monologue captions … typically italicized").

### 3.2 ALL CAPS vs mixed-case

- **Western mainstream comics:** Dialogue is **ALL CAPS**, with a "crossbar I" used **only** for the personal pronoun "I" and rare acronyms (F.B.I.). This is enforced by Comicraft and Blambot dialogue fonts which only ship uppercase + alternate I-glyphs.
- **Japanese manga (translated to English):** Mixed-case is common but ALL CAPS still acceptable.
- **Webtoon:** **Mixed-case dominates** — Korean original, English localization, and Japanese localization all favor sentence-case on mobile. ALL CAPS is reserved for SFX and shouts only.
- **Phoenix:** `font_override` enum has `all_caps_scream` for screaming intensity — correct for shout. Default dialogue should be sentence-case for webtoon, ALL CAPS for legacy western page comic. **Phoenix has no locale switch for case handling.**

### 3.3 Mobile font sizes

WEBTOON Canvas guideline (cited via S-Morishita Studio "What Font Size do Webtoon Artists Use?" and the "Font size guide/test" Canvas series #719839):
- **Standard dialogue:** 12-30 px on an 800-px-wide canvas.
- **Common production size:** 14 px (S-Morishita reports several pro creators use exactly 14 px).
- **Practical test:** Zoom canvas to phone-width on screen; pick smallest comfortable size.

**Phoenix's current sizes** (whisper=10 .. screaming=22) are within this band but were not derived from a target-canvas reference. If the target canvas is 800 px wide (LINE Manga Indies max), Phoenix's normal=14 is ON spec. **However**, Phoenix renders to whatever panel resolution arrives — if panels arrive at 400 px wide (test fixture), 14 px text becomes proportionally **2× too big**. Phoenix should size text as a **fraction of canvas width** (e.g., normal = 1.75% of canvas width) rather than absolute px.

### 3.4 Kerning, leading, and "AIR"

- **Kerning:** Comicraft / Tom Orzechowski recommendation: use **'Optical' kerning**, not 'Automatic.' Pillow has no optical kerning — it only does metric kerning from font tables. **Phoenix gap:** for production-grade lettering, Phoenix would need to migrate to a vector pipeline (SVG via librsvg/cairosvg, or Skia) OR render text with HarfBuzz directly.
- **Leading:** Lines should breathe — typical 110-130% of font size. Pillow's default ImageDraw.multiline_text uses `spacing` parameter; Phoenix should set this explicitly.
- **AIR (padding):** ~1 letter-width. At 14 px font, ~10 px AIR around text inside bubble.

### 3.5 CJK font choices (production-quality, open-source)

| Locale | Recommended primary | License | Notes |
|---|---|---|---|
| ja_JP | **Source Han Sans JP / Noto Sans CJK JP** (7 weights) | OFL 1.1 | Adobe + Google joint, Iwata supplied JP designs. Industry standard. |
| zh_TW | Source Han Sans TC | OFL | Distinct glyphs from Simplified — TC (Taiwan) ≠ TC (Hong Kong) — Adobe ships separate variant for HK. |
| zh_CN | Source Han Sans SC | OFL | Designed via Changzhou SinoType. |
| ko_KR | Source Han Sans KR | OFL | Designed via Sandoll Communications. |
| ja_JP handwritten/textbook feel | **Klee One** (Fontworks) or **Iansui** (2025 Google Fonts) | OFL | Klee One = humanist textbook script — fits "shojo" or "school slice-of-life" tone. Iansui (2025, by But Ko, derived from Klee One) extends Traditional Chinese + Formosan languages. |
| zh_CN handwritten | LxgwWenKai (霞鹜文楷) | OFL | Open-source Chinese derived from Klee One. |

**Citation density:** Source Han Sans / Noto Sans CJK is the **single most important font family** for Phoenix's CJK localization stack. The Adobe CJK Type Blog (ccjktype.fonts.adobe.com) is the canonical engineering reference. Source Han Sans v2 release notes (Nov 2018) document the variable-weight axis, OTC packaging, and per-locale glyph divergence handling.

**Phoenix action:** Add to `FONT_REGISTRY.yaml`:
- `source_han_sans_jp_*` (Light, Regular, Medium, Bold, Heavy)
- `source_han_sans_tc_*`, `source_han_sans_sc_*`, `source_han_sans_kr_*`
- `klee_one_jp_handwritten`
- A SFX-specific Japanese font (e.g., `mochiy_pop_one` or hand-drawn-style — NO single open-source canonical SFX-japanese font found; commercial options dominate).

### 3.6 AI-generated lettering vs hand vs typed

- **Hand-lettered** (Klein, Roshell): Highest quality, ~$80-200/page rate. Phoenix cannot afford at scale.
- **Typed with pro fonts** (Blambot/Comicraft licenses): 95% of modern digital comics. Phoenix's current pipeline.
- **AI-generated lettering**: Emergent. Comicraft AI vs Blambot Generator comparison (alibaba.com product-insights, 2025) shows readability is comparable to typed-font but **NOT to hand-lettered**. Best for low-cost long-tail.

---

## §4. Sound Effects (SFX)

### 4.1 SFX integration patterns

| Mode | Description | Phoenix-fit |
|---|---|---|
| Drawn-into-art (baked) | SFX is an art element painted on background. Untranslatable without re-render. | **Avoid** |
| Free-floating typed | SFX as text glyphs floating over art. Translatable. | **Phoenix current** (bubble_render renders SFX as text) |
| In-bubble SFX | SFX inside a small "thought-style" bubble. | Rarely used |
| Vector SVG with stylized warp | SFX text warped/rotated/skewed via SVG transform. Translatable. | **Recommended next** |

**Cite:** Korean manhwa SFX (의성어 onomatopoeia, 의태어 mimetic words) — koreanling.com glossary; novel translator's "Korean Manhwa Emotion Sound Effects (SFX) Glossary"; Japanese manga SFX database (gist.github.com/UserUnknownFactor — comprehensive Japanese game/manga SFX→English mapping).

### 4.2 Multi-language SFX policy

Per the noveltranslator.com webtoon-translation guidance and J-En Translations "Manga Translation Pitfalls":
- **Naver / Lezhin official:** Translate SFX into English equivalents (KABOOM, SLAM).
- **Many fan/scanlation:** Leave Japanese kana untouched (ドカン!) with small English gloss in margin.
- **Webtoon Canvas:** Mixed; user preference.

**Phoenix recommendation:** Treat SFX as **per-locale strings** in lettering_spec. Schema gap: current `sfx: array of string` is locale-agnostic. Should become:
```json
"sfx": [
  {"sfx_id": "panel3_crash", "by_locale": {"en_US": "KABOOM!", "ja_JP": "ドカン！", "ko_KR": "콰쾅!", "zh_TW": "轟！", "zh_CN": "轰！"}, "style": "explosion_burst"}
]
```

### 4.3 Onomatopoeia volume gap

Per AJET CONNECT and Capital Linguists localization analyses: **Japanese has ~1,200 distinct onomatopoeia, ~3× English.** Direct 1:1 translation is impossible. Localization strategies:
1. **Conceptual mapping** (ニコニコ → smiling-warmly) — preferred for narration.
2. **Visual+English label** (キラキラ★ → SPARKLE★) — preferred for SFX.
3. **Leave + footnote** — preferred for archival/nostalgia titles.

**Phoenix opportunity:** AI-rendered SFX layer. Render the styled SFX text glyph as a separate transparent PNG per locale; composite at export. This is a **new pipeline stage** Phoenix doesn't have.

---

## §5. Layered Compositing — Pipeline Best Practices

### 5.1 Standard layer order (back to front, industry consensus)

Per Clip Studio Paint webtoon tutorials (clip-studio.net "Converting Your Comic for Webtoon" by MelanciaComics; "Webtoon 101" by 69Michi; "Storyboard and Component" by O_kids) and S-Morishita Studio guides:

```
Layer 0  (bottom)   Background base color
Layer 1             Background detail / 3D-asset render
Layer 2             Mid-ground (props, scenery)
Layer 3             Character base (color flats)
Layer 4             Character lines / shading
Layer 5             Foreground (objects in front of character)
Layer 6             FX / motion lines / sparkles
Layer 7             Tone / screentone (page manga only)
Layer 8             SFX glyphs (typed or drawn)
Layer 9             Speech bubbles
Layer 10 (top)      Bubble text
Layer 11            Caption boxes
Layer 12            Panel borders / gutter (page manga; webtoon often skips)
```

Tutorial consensus: "preferably into folders (SFX, Text, Lines, Colors, etc.), and additional folders for SFX and Balloons, so they don't get lost."

**Phoenix's current layer order** (implicit, not documented):
1. FLUX-generated full-panel image (combines BG + character into one flat layer).
2. Bubble layer stamped via `bubble_render.py`.
3. Page-strip composition via `page_compose.py`.

**Gap:** Phoenix conflates Layers 0-7 into a single FLUX render, which means **character can't be repositioned, BG can't be reused, and translation can't repaint just the text layer**. This is the central architectural penalty.

### 5.2 File format

| Format | Use | Verdict |
|---|---|---|
| **PSD** | Source-of-truth multi-layer master | Industry standard. Phoenix doesn't produce this. |
| **Krita .kra** | Open-source PSD alternative | Roughly equivalent; Krita has Python scripting API. |
| **Layered PNG (multiple files)** | Per-layer transparent PNG export | Phoenix-friendly; no proprietary format. **Recommended.** |
| **Flat PNG-24** | Final delivered file to upload | Phoenix already does this. |
| **JPEG flatten** | Final delivered if size-constrained | LINE Manga: ≤ 2 MB / image. |
| **WebP** | Smaller than PNG, supported by some platforms | Not yet a webtoon platform standard. |

### 5.3 Resolution & color management

- **Source supersample:** Industry rule — work at **2× final output**. For 800-px-wide LINE Manga Indies target, source at 1600 px wide. Downsample with Lanczos at export. Phoenix `bubble_render.py` uses `Image.Resampling.LANCZOS` already in `page_compose.py` — correct.
- **Color:** **sRGB always** for digital webtoon. **Never CMYK** (CMYK is print-only). Phoenix's Pillow pipeline is RGBA — correct.
- **DPI:** ≥ 72 dpi (LINE Manga Indies floor); print needs 300 dpi but Phoenix is digital-only.
- **Anti-aliasing:** Pillow's text rendering at small sizes (≤ 12 px) loses anti-aliasing. Use `ImageFont.truetype` with size ≥ 16 px and downsample, or migrate to a vector pipeline.

### 5.4 Export pipeline (Phoenix-recommended)

```
[FLUX panel render at 1600 px wide, RGBA]  (Layer 0-7 combined)
       ↓
[Apply bubble layer via Pillow] → still 1600 px RGBA
       ↓
[Vertical-strip concat for webtoon] OR [horizontal-strip for page manga]
       ↓
[Downsample to 800 px wide @ Lanczos]
       ↓
[Split into ≤ 10000 px tall segments]  (LINE Manga max)
       ↓
[Export PNG-24 sRGB; verify ≤ 2 MB; if oversize, JPEG q85]
```

---

## §6. Programmatic Compositing Tools

| Tool | Strengths | Weaknesses | Phoenix verdict |
|---|---|---|---|
| **Pillow (PIL)** | Pure Python, in stdlib-ish, already used | No layer model, no PSD I/O, weak text shaping | **Current — keep for raster compositing** |
| **ImageMagick CLI** | Power, scriptable | Subprocess overhead, weak typography | Useful for bulk conversion |
| **Cairo (pycairo)** | Vector + raster, CJK shaping via Pango | Larger dependency tree | **Recommended for vector bubbles** |
| **Skia (skia-python)** | Same engine as Chrome / Flutter; production-grade text shaping incl. CJK; Bézier vector | Big binary, less Pythonic | Top-tier option |
| **Krita Python API** | Full PSD-class compositing inside Krita | Requires Krita runtime; not headless-friendly | Only for human-in-loop |
| **Photoshop Generator API** | Industry standard | Paid, not headless-cloud-friendly | Skip |
| **ComfyUI_LayerStyle** (chflame163/ComfyUI_LayerStyle) | Photoshop-like in ComfyUI; **has LoadPSD node** | ComfyUI-bound; orchestration, not export | **Recommended for layer assembly** |
| **ComfyUI-LayerForge** (Azornes/Comfyui-LayerForge) | Photoshop-like canvas editor; multi-layer, mask, blend, transform; AI background removal | New (2024-2025); ComfyUI-bound | Promising for bubble-on-art assembly |
| **ComfyUI-LayerDivider** (jtydhr88/ComfyUI-LayerDivider) | Generates layered PSDs **inside ComfyUI** (5 layers per region: base, screen, multiply, subtract, addition) | Niche | Useful for tone separation |
| **ImageCompositeMasked** (ComfyUI core) | Built-in overlay node | Basic | Already present |

**Phoenix recommendation:** Standardize on **Pillow for the bubble overlay stage** (existing investment, OFL fonts work, no new dep) **plus Cairo OR Skia for vector master shapes** (for SVG bubble templates that survive arbitrary scale). Adopt **ComfyUI_LayerStyle's LoadPSD** if Phoenix moves to PSD-as-source-of-truth.

---

## §7. Word-Bubble Programmatic Rendering

### 7.1 Drawing libraries

| Library | Bubble shape API |
|---|---|
| Pillow ImageDraw | `polygon()`, `ellipse()`, `rounded_rectangle()`. No native scallop/cloud — must compose from arcs. Phoenix uses this. |
| Cairo | Bézier paths, arc-of-arcs scallops natively; produces SVG and PNG. |
| Skia | Bézier paths; outputs PNG / SVG / PDF. |
| **SVG direct** | Hand-write `<path d="M ... A ...">`; rasterize via cairosvg. **Cleanest option** for scalable shapes. |

### 7.2 Auto-tail-to-mouth algorithm

Public OSS reference: **manga-image-translator (zyddnys/manga-image-translator)** does the **inverse** — bubble detection + OCR for translation. It uses a renderer that "tries to fit the detected text bubble rather than detected textline area." It also exposes `box_threshold`, `unclip_ratio`, configurable OCR, and specific bubble-detection inpainting. **No public Phoenix-style forward-render auto-tail algorithm in OSS.** koharu (mayocream/koharu) is similar — vision+language stack tuned per-page-component.

**Algorithm Phoenix should implement:**
```python
def compute_tail_target(panel_image, speaker_id, character_bbox_manifest):
    bbox = character_bbox_manifest[speaker_id]
    mouth_x = bbox["x"] + 0.5 * bbox["width"]
    mouth_y = bbox["y"] + 0.30 * bbox["height"]   # mouth ≈ 30% from top of head
    return (mouth_x, mouth_y)

def place_bubble_with_tail(bubble_zone, mouth_xy):
    # Bubble center → use position_hint zone
    # Tail: line from bubble_edge to mouth_xy, clipped to panel border
    ...
```

**Prerequisite:** A character-bbox manifest per panel. Phoenix doesn't currently emit this from the FLUX render stage; would need a YOLOv8 face-detection post-step. (Phoenix already trains LoRAs for character lock — see §9 — that pipeline could emit bbox as a side-product.)

### 7.3 Auto-bubble-sizing algorithm

Phoenix already has this (`bubble_render.py:_coverage_ratio` + textwrap), but improvements:
1. Pyramidal/diamond text shape for round bubbles (Comicraft "Word Arrangement" rule).
2. Optical kerning (would require HarfBuzz).
3. Avoid hyphenation (built into textwrap with `break_long_words=False`).
4. Iterative re-fit: render text → measure → grow bubble → re-render (3 passes typical).

### 7.4 Collision detection

Phoenix has zone-grid placement, no actual bbox overlap detection. Industry algorithm:
1. List all bubble candidates with bboxes.
2. Greedy: place by reading order; for each, if bbox overlaps prior or critical-art mask, push toward nearest free zone.
3. If no free zone, shrink bubble or split text across multiple bubbles.

### 7.5 Open-source projects to reference
- **zyddnys/manga-image-translator** — primary reference. Active 2025.
- **mayocream/koharu** — Rust-based, ML-powered, vertical CJK layout aware.
- **georgescutelnicu/Manga-Translator** — Python, smaller, didactic.
- **VincentQQu/manga_text_bubble_detect_translate** — DL bubble detection.
- **Detopall/manga-translator** — YOLOv8 + manga-ocr + deep-translator.

---

## §8. Multi-Language Text Overlay (Critical for Phoenix)

### 8.1 Why separable text layer is a 10× advantage

Phoenix's owner thesis: build once, localize for 5 markets (en_US, ja_JP, zh_TW, zh_CN, ko_KR). **The math:**
- **Baked-text pipeline:** N markets × M panels × $X/render = N·M·X cost. Each new market = full re-render.
- **Separable-text pipeline:** 1 × M base renders + N × M text-layer-only re-overlays. Text overlay cost ≈ 1/100 of full FLUX render. **~50-99× cheaper for 5 markets.**

This is the **single largest engineering win** Phoenix can claim from layered compositing.

**Prerequisite:** The lettering_spec must be locale-keyed at the schema level. Current schema has `text: string` — needs to become `text_by_locale: object` OR the spec must be emitted per-locale and the bubble_render.py invoked once per locale with a stable mask layer.

### 8.2 Reading order: RTL vs LTR vs vertical

| Locale | Reading order | Phoenix support |
|---|---|---|
| en_US | LTR, top-to-bottom | ✅ Pillow default |
| ja_JP page manga | RTL, top-right → bottom-left | ❌ Phoenix has no RTL |
| ja_JP webtoon (smartoon, Piccoma SMARTOON) | LTR (because vertical scroll) | ✅ |
| zh_TW page | RTL traditional | ❌ |
| zh_TW webtoon | LTR | ✅ |
| zh_CN | LTR (modern Mandarin convention) | ✅ |
| ko_KR | LTR | ✅ |

**Webtoon dodges the RTL problem entirely** because vertical scroll has no horizontal reading order. This is another reason Phoenix should privilege webtoon.

### 8.3 Text expansion factors

Per Pairaphrase localization research (2026) and Capital Linguists Japanese manga analysis:
- **English → Japanese:** Often **-30 to -50%** character count (Japanese kanji is denser).
- **Japanese → English:** Typically **+30 to +80%** character count.
- **English → Korean:** Roughly equal or slightly longer (~+10%).
- **English → Simplified Chinese:** **-40 to -60%** (very dense).
- **European languages → English:** -25 to -35%.

**Phoenix implication:** Bubbles must auto-resize per locale. A bubble sized for ja_JP "ドカン!" (3 chars) must grow to fit en_US "KABOOM!!" (8 chars). Phoenix's coverage_limit logic auto-shrinks but does not auto-grow. Schema should record a `bubble_min_size` and `bubble_max_size` per dialogue line.

### 8.4 Vertical text in CJK

- **Traditional manga:** Vertical kanji is canonical. Pillow does NOT shape vertical CJK; would need Cairo+Pango or HarfBuzz with `HB_DIRECTION_TTB`.
- **Webtoon:** **Horizontal** kanji is dominant — koharu (koharu.rs) explicitly targets vertical-CJK-aware rendering as a *legacy support* feature; new webtoon production is horizontal.
- **Phoenix:** Webtoon-first means **horizontal CJK is enough**. Defer vertical support.

### 8.5 Furigana

- **Page manga:** Furigana (small phonetic above kanji) is mandatory for kid-targeted titles, optional for adult.
- **Webtoon:** Mostly drops furigana. (Confirmed by koharu's "Text Rendering and Vertical CJK Layout" doc.)
- **Phoenix schema gap:** No `furigana` field in `dialogue_lines`. Add only if Phoenix expands beyond webtoon to page manga for ja_JP.

### 8.6 Translation-friendly source workflow

**Mandatory rule:** Text layer ALWAYS separate. Never merge into background. This is true for both Phoenix's FLUX-output art (which should not include text) AND for the bubble layer (which should be re-renderable per locale from the spec).

**Phoenix verification:** FLUX text-in-image is a known failure mode for diffusion models. Phoenix should add a **"no FLUX-rendered text" gate** — OCR the FLUX output, fail if any glyphs detected, force re-roll. This is separate from the bubble overlay.

---

## §9. Character Consistency Across Panels

### 9.1 Modern state of the art (2025-2026)

- **IP-Adapter for FLUX** (InstantX/FLUX.1-dev-IP-Adapter, Nov 2024 release): Image reference, but explicitly NOT for fine-grained character consistency.
- **FLUX 2** (Nov 2025): Native support for **up to 10 reference images simultaneously**, "best character and product consistency available in any image model today" (apatero.com).
- **FLUX-MonochromeManga** (dataautogpt3, Hugging Face): Tuned for monochrome manga, improved per-panel consistency without extra prompting.
- **Industry consensus** (siliconflow.com 2026 comics/manga model guide): Character consistency went from "mostly impossible" to "actually workable" between late 2025 and early 2026.

### 9.2 Phoenix-specific path

- Phoenix has **289 character portraits** already.
- LoRA training is **blocked by VRAM PR #623 at 16GB** (per task brief).
- Workaround until LoRA: use IP-Adapter chains with character portrait as reference. FLUX 2 (if Phoenix migrates) accepts up to 10 references — model sheet front/side/back/3-quarter/expressions can all be input simultaneously.

### 9.3 Model sheet → 50 panels with consistent face

**Industry standard (pre-2025):** Train LoRA per character, ~1500 steps, ~50 reference images. ~$5 cloud compute per LoRA.

**Phoenix VRAM-blocked workaround:** IP-Adapter with 4-8 portrait references + prompt-locked character description. Quality is ~70-80% of LoRA at zero training cost.

---

## §10. Background / Object Reuse

### 10.1 Stock libraries used in webtoon production

Per S-Morishita Studio "How do Manhwa and Webtoon Artists make Backgrounds":
- **Acon3D** (acon3d.com) — Korean marketplace; manhwa industry's primary 3D-asset source.
- **Clip Studio Assets** (assets.clip-studio.com) — built-in Clip Studio asset library.
- **DAZ Studio**, **SketchUp** — generic 3D stock.

### 10.2 Photo-basing & photobashing

S-Morishita: "Photobashing combines multiple photos and paints over them, or artists paint over a photographic underlay, keeping only structure and replacing surface detail." Industry-accepted.

### 10.3 Phoenix opportunity

Phoenix has FLUX. Generate a **single** detailed background per scene at 2× resolution; reuse across all panels in that scene with parallax / crop / camera angle. This is the **same** asset-reuse strategy as Clip Studio + Acon3D, but with AI-generated backgrounds.

**Schema gap:** Phoenix needs a `scene_background_id` field at the chapter-script level to link panels sharing a background. Currently each panel has independent FLUX prompt — wasteful and produces visual drift.

---

## §11. Webtoon vs B&W Page Manga — Compositing-Favorability Comparison

| Pipeline element | Webtoon benefit from layered comp | Page manga penalty | Net |
|---|---|---|---|
| Background | ✅ Full-color sRGB BG reused across panels via tile/parallax | ⚠ B&W requires consistent ink-line + tone, harder to layer-blend without seams | **Webtoon wins** |
| Character | ✅ Flat color = clean alpha mask; FLUX output drops onto BG cleanly | ⚠ Hatching/screentone implies pen-pressure variation that flat layers can't fake | **Webtoon wins** |
| Dialogue | ✅ Borderless white bubble + drop-shadow, simple Pillow primitive | ⚠ Tail-to-mouth + RTL reading order + furigana = 3 extra rules | **Webtoon wins** |
| SFX | ✅ Free-floating typed glyph, per-locale | ⚠ Hand-drawn SFX baked into background panel = locked-locale | **Webtoon wins big** |
| Bubble shape | ✅ Forgiving — no hard panel border to clip against | ⚠ Bubble must respect panel border + gutter logic | **Webtoon wins** |
| Narration | ✅ Caption box anywhere in scroll | ⚠ Narration boxes must respect panel reading-order | **Webtoon wins** |
| Gutter | ✅ Vertical white space, infinitely flexible | ⚠ Gutter pacing is part of the storytelling craft, hard to algorithmify | **Webtoon wins** |
| Panel border | ⚪ Optional/often absent | ⚠ Panel border style + bleed are part of the brand | **Webtoon wins** |
| Page composition | ✅ Vertical concat, almost trivial | ⚠ Page layouts are signature of mangaka, not algorithm-friendly | **Webtoon wins** |
| Color | ✅ Native sRGB matches FLUX output | ❌ B&W requires post-process desaturation + screentone, an extra pipeline stage | **Webtoon wins** |
| Resolution | ✅ 800 × N px, N up to 10000 | ⚠ Print 300 dpi A5 = 1748×2480 px per page | **Webtoon wins** |
| Furigana | ✅ Skipped | ❌ Required | **Webtoon wins** |
| Vertical CJK | ✅ Skipped | ❌ Required for ja_JP | **Webtoon wins** |
| Auto-resize per locale | ✅ Bubble grows in unbounded scroll | ❌ Bubble cannot grow past panel border | **Webtoon wins** |

**Net verdict:** **Webtoon is fundamentally better-suited to a "build from layers" production model in every dimension.** Page manga punishes Phoenix's compositing approach in the dimensions Phoenix cares about most: localization, reuse, automation. Phoenix's manga plans should re-baseline on webtoon as primary, with B&W page manga as a *flatten + screentone-filter* secondary export.

---

## §12. Phoenix-Specific Recommendations (Engineering Directives)

### 12.1 Layer-order standardization
Document and enforce 13-layer order in `phoenix_v4/manga/chapter/page_compose.py`:
```
0 BG-base, 1 BG-detail, 2 mid, 3 char-flat, 4 char-line,
5 fg, 6 fx, 7 tone (page-only), 8 SFX, 9 bubble-shape,
10 bubble-text, 11 caption, 12 panel-border (page-only)
```

### 12.2 Source resolution
- Webtoon: render panels at **1600 px wide** (2× LINE Manga Indies 800px); downsample at export.
- Page manga (if produced): render at **3496 px wide** (2× A5 print 300 dpi).

### 12.3 Font choice per locale (add to FONT_REGISTRY.yaml)

```yaml
- id: source_han_sans_jp_regular
  license: OFL
  path: ttf/SourceHanSansJP-Regular.otf
  status: pending
- id: source_han_sans_jp_bold
  license: OFL
  path: ttf/SourceHanSansJP-Bold.otf
- id: source_han_sans_tc_regular
  license: OFL
  path: ttf/SourceHanSansTC-Regular.otf
- id: source_han_sans_sc_regular
  license: OFL
  path: ttf/SourceHanSansSC-Regular.otf
- id: source_han_sans_kr_regular
  license: OFL
  path: ttf/SourceHanSansKR-Regular.otf
- id: klee_one_jp_handwritten
  license: OFL
  path: ttf/KleeOne-Regular.ttf
- id: lxgw_wenkai_zh_handwritten
  license: OFL
  path: ttf/LXGWWenKai-Regular.ttf
- id: anime_ace_dialogue_en
  license: Blambot-free
  path: ttf/AnimeAce-2.0-BB.ttf
- id: badaboom_sfx_en
  license: Blambot-free
  path: ttf/BADABB__.ttf
```

### 12.4 Bubble shape vocabulary (SVG masters)

Create `/assets/manga/bubble_shapes/` with 11 SVG masters:
```
round_normal.svg, spiky_emphasis.svg, cloud_thought.svg, square_narration.svg,
whisper_dashed.svg, scream_ultra.svg, electronic_sharp.svg, drip_horror.svg,
shojo_soft.svg, wavy_dream.svg, off_panel_dotted_tail.svg
```
Each parameterized by (width, height, tail_origin_xy, tail_target_xy). Render via cairosvg → composite via Pillow.

### 12.5 Translation pipeline integration

**Schema migration: lettering_spec.schema.json v3.0.0**

```json
"dialogue_lines": [{
  "speaker": "...",
  "text_by_locale": {
    "en_US": "...", "ja_JP": "...", "zh_TW": "...",
    "zh_CN": "...", "ko_KR": "..."
  },
  "intensity": "...",
  "bubble_style": "...",
  "bubble_min_px": 80,
  "bubble_max_px": 320,
  ...
}],
"sfx": [{
  "sfx_id": "p3_crash",
  "by_locale": {"en_US": "KABOOM!!", "ja_JP": "ドカン！", ...},
  "style": "explosion_burst",
  "render_xy": [0.6, 0.4]
}]
```

### 12.6 Quality gate before upload

New CI gate: `scripts/manga/qc/lettering_overflow_gate.py`
1. For each per-locale render, OCR the text region; verify no clipped characters.
2. Verify bubble bbox does NOT cross critical-art mask (character face).
3. Verify page heights ≤ 10000 px (LINE Manga max).
4. Verify per-image file size ≤ 2 MB; auto-fallback to JPEG q85 if oversize.

### 12.7 Single bubble-rendering library
- **Keep Pillow** for the production pipeline (existing investment, OFL fonts, no new dep).
- **Add cairosvg** as a thin wrapper for SVG bubble masters — `pip install cairosvg pycairo` adds ~12 MB. The performance hit is negligible (bubble layer is text-bound, not pixel-bound).
- **Defer Skia** unless HarfBuzz-quality CJK shaping becomes critical.

### 12.8 No-FLUX-text gate
After every FLUX render, run lightweight OCR (e.g., easyocr or tesseract-en+jp+ko+zh-CN+zh-TW) over the panel; if **any** glyphs detected with confidence > 0.7 in the art layer (before bubble overlay), force re-roll. This prevents diffusion-baked broken text from entering the pipeline.

### 12.9 Webtoon-primary, page-manga-secondary
Reframe Phoenix manga plans: **webtoon is the master format**. Page manga is a downstream transform:
1. Render webtoon vertical strip at 1600×N.
2. For page manga export: split vertical strip into pages, apply screentone filter (Pillow `ImageFilter` + threshold), reflow bubbles for RTL if ja_JP page market.

### 12.10 Per-character bubble-style register (Sandman pattern)
Add `character_bubble_register` to the series asset registry:
```yaml
characters:
  - id: villain_dream
    bubble_default_style: black_fill_white_text_wavy
    font_default: source_han_sans_jp_bold
    font_color: "#ffffff"
    bubble_color: "#000000"
```
Override `bubble_style` per-character at lettering-derive time.

---

## §13. Risk / Gaps

### 13.1 Not publicly documented (tribal knowledge)
- **AIR exact ratio** — Comicraft says "one letter-width" but the precise value (10% of font-size? 14% of bubble-width?) is craft-tradition only, not in any spec.
- **Diamond text-shape word arrangement** rules — taught in Comicraft's book and Klein's blog, not in any algorithmic form.
- **Per-character bubble register** decisions (the Sandman pattern) — purely artistic.
- **Rakuten AI Chat (per /tmp/rakuten_ai_chat_research.md)** confirmed Piccoma SMARTOON specs are NOT publicly documented; LINE Manga Indies is the only public hard-numbers source.

### 13.2 Blocked by Phoenix infra
- **LoRA character lock blocked by 16 GB VRAM** (PR #623). Workaround: IP-Adapter chains.
- **No CJK OCR in CI** — required for the no-FLUX-text gate. Add `easyocr` or `manga-ocr` (kha-white/manga-ocr).
- **No PSD I/O** — would need pyopenpsd or migrate to ComfyUI_LayerStyle's LoadPSD node.
- **No vector text shaping** — Pillow only does bitmap. Production-grade kerning/CJK shaping requires Cairo/Pango or HarfBuzz.

### 13.3 Requires external partnership
- **Custom CJK fonts** — Source Han Sans + Klee One cover most cases. For premium tier, commercial Fontworks / Iwata fonts are a partnership decision.
- **Professional letterer review** — for hero titles, a one-time pass by a Comicraft / Letter Shop NYC pro letterer would calibrate Phoenix's automated decisions. Cost ~$5000-15000 for style guide + 50-issue audit.
- **Korean SFX glossary licensing** — noveltranslator.com has glossaries; for production use, license a curated SFX dictionary.

---

## Citations (URLs accessed 2026-04-25)

### Internal Phoenix files
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/schemas/manga/lettering_spec.schema.json
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/schemas/manga/lettering_style_bible.schema.json
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/phoenix_v4/manga/chapter/bubble_render.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/phoenix_v4/manga/chapter/lettering_from_script.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/phoenix_v4/manga/chapter/page_compose.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/fonts/manga/FONT_REGISTRY.yaml
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/scripts/manga/update_font_registry.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/tests/test_bubble_render.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/tests/test_lettering_spec_v2.py
- /Users/ahjan/phoenix_omega/.claude/worktrees/relaxed-jang-704924/tests/test_manga_dialogue_gates.py

### Industry lettering & typography
1. https://blambot.com/pages/comic-book-grammar-tradition — Blambot "Comic Book Grammar & Tradition"
2. https://blambot.com/pages/the-essential-guide-to-comic-book-lettering — Blambot "Essential Guide to Comic Book Lettering"
3. https://blambot.com/collections/dialogue-fonts — Blambot dialogue fonts catalog
4. https://www.comicbookfonts.com — Comicraft fonts homepage
5. https://www.comicbookfonts.com/Comic-Book-Lettering-The-Comicraft-Way-p/cbl1.htm — Comicraft "The Comicraft Way" book listing
6. https://balloontales.com/the-comicraft-glossary-of-lettering-terms/ — Comicraft Glossary (AIR, Word Arrangement, etc.)
7. https://balloontales.com/ — Comicraft Balloon Tales digital lettering guide
8. https://kleinletters.com/ — Todd Klein homepage
9. https://kleinletters.com/Blog/lettering-placements/ — Klein "Lettering Placements"
10. https://kleinletters.com/Blog/lettering-tips-for-comics-writers/ — Klein "Lettering Tips for Comics Writers"
11. https://kleinletters.com/Blog/preparing-comics-scripts-for-lettering/ — Klein "Preparing Comics Scripts for Lettering"
12. https://en.wikipedia.org/wiki/Speech_balloon — Speech balloon article (shape conventions, Klein/Sandman lettering)
13. https://en.wikipedia.org/wiki/Todd_Klein — Todd Klein bio
14. https://www.designyourway.net/blog/what-font-do-comics-use/ — Comic font categories overview

### Webtoon production
15. https://tips.clip-studio.com/en-us/articles/3751 — Walter Ostlie "Letter Your Webtoon Like a Pro: Balloons, Fonts, and More"
16. https://tips.clip-studio.com/en-us/articles/11562 — MelanciaComics "Converting Your Comic for Webtoon"
17. https://tips.clip-studio.com/en-us/articles/4143 — 69Michi "Webtoon 101 [By an Original WEBTOON creator]"
18. https://tips.clip-studio.com/en-us/articles/10886 — O_kids "Storyboard and the Component"
19. https://tips.clip-studio.com/en-us/articles/11224 — O_kids "Webtoon Background with 3D Model"
20. https://tips.clip-studio.com/en-us/articles/7417 — mannygart "How To Make A WEBTOON: The Ultimate Guide"
21. https://www.s-morishitastudio.com/what-font-size-do-webtoon-artist-use/ — S-Morishita "What Font Size do Webtoon Artists Use"
22. https://www.s-morishitastudio.com/choosing-your-webtoon-comic-fonts/ — S-Morishita "7 BEST Webtoon Fonts for 2025"
23. https://www.s-morishitastudio.com/what-do-webtoon-artists-use-for-backgrounds/ — S-Morishita "How do Manhwa and Webtoon Artists make Backgrounds"
24. https://www.s-morishitastudio.com/how-to-make-webtoon-backgrounds-webtoon-background-tips/ — S-Morishita Webtoon Background Tips
25. https://www.webtoons.com/en/canvas/font-size-guidetest/list?title_no=719839 — WEBTOON Canvas "Font size guide/test"
26. https://www.toonsmag.com/formatting-your-comic-for-mobile-and-web-platform/ — Toons Mag mobile formatting
27. https://fontyouneed.com/fonts/webtoon-fonts-a-creators-guide — Webtoon fonts creator guide

### CJK fonts & typography
28. https://en.wikipedia.org/wiki/Source_Han_Sans — Source Han Sans Wikipedia
29. https://fonts.adobe.com/fonts/source-han-sans-cjk-japanese — Adobe Fonts Source Han Sans JP
30. https://fonts.adobe.com/fonts/source-han-sans-cjk-traditional-chinese — Source Han Sans TC
31. https://ccjktype.fonts.adobe.com/2017/04/source-han-serif-history-development.html — Adobe CJK Type Blog "Source Han Serif History & Development"
32. https://blogs.adobe.com/CCJKType/2018/11/shsans-v2-technical-tidbits.html — Adobe "Source Han Sans v2 Technical Tidbits"
33. https://source.typekit.com/source-han-sans/ — Typekit Source Han Sans introduction
34. https://blog.typekit.com/2014/07/15/introducing-source-han-sans/ — Typekit blog launch announcement
35. https://github.com/adobe-fonts/source-han-super-otc — Source Han / Noto CJK Mega/Ultra OTCs
36. https://github.com/fontworks-fonts/Klee — Klee One repo
37. https://fonts.google.com/specimen/Klee+One — Klee One on Google Fonts
38. https://fontsource.org/fonts/klee-one — Klee One on Fontsource
39. https://github.com/lxgw/LxgwWenKai — LxgwWenKai (Chinese Klee derivative)
40. https://github.com/scriptwide-fonts/scriptwide-kyokasho-cjk — Klee-derivative CJK textbook font
41. https://blog.justfont.com/2024/08/google-fonts-cjk-en/ — justfont "Free Chinese Fonts Recommendations" (2025/06)
42. https://www.freejapanesefont.com/ — Free Japanese fonts directory
43. https://github.com/topics/cjk-font — GitHub cjk-font topic

### Manga translation, OCR, bubble detection
44. https://github.com/zyddnys/manga-image-translator — manga-image-translator (primary OSS reference)
45. https://github.com/zyddnys/manga-image-translator/blob/main/README.md — manga-image-translator README
46. https://hub.docker.com/r/zyddnys/manga-image-translator — manga-image-translator Docker
47. https://github.com/mayocream/koharu — koharu (Rust ML manga translator)
48. https://koharu.rs/explanation/text-rendering-and-vertical-cjk-layout/ — koharu vertical-CJK layout doc
49. https://github.com/georgescutelnicu/Manga-Translator — Manga-Translator (Python)
50. https://github.com/VincentQQu/manga_text_bubble_detect_translate — DL bubble detection
51. https://github.com/Detopall/manga-translator — YOLOv8 + manga-ocr translator
52. https://github.com/meangrinch/MangaTranslator — Manga translation app
53. https://noveltranslator.com/applications/webtoon-translator — Webtoon translator
54. https://noveltranslator.com/applications/korean-to-english-manhwa-translator — KR→EN manhwa translator
55. https://noveltranslator.com/translate-image/glossary/korean-emotion-sfx — Korean SFX glossary
56. https://guide.totus.pro/5397ddfc-0c71-4830-9803-2671edd6c701 — "Webtoon Translation Guide ver.02"
57. https://belindoc.com/translate/manga-translator — Belin Doc AI manga translation

### SFX & onomatopoeia
58. https://gist.github.com/UserUnknownFactor/093a2296c5a4d9ef7b404728ebde94a3 — Japanese game/manga SFX database
59. https://koreanling.com/more-korean-webtoon-onomatopoeia/ — Korean Webtoon Onomatopoeia
60. https://koreanling.com/korean-onomatopoeia-words-with-webtoons/ — Korean Onomatopoeia with Webtoons
61. https://www.japanpowered.com/anime-articles/manga-sound-effect-guide — Japan Powered Manga SFX Guide
62. https://www.acon3d.com/en/product/1000004863 — Acon3D Webtoon SFX collection

### Compositing tools & ComfyUI
63. https://github.com/chflame163/ComfyUI_LayerStyle — ComfyUI_LayerStyle
64. https://github.com/Azornes/Comfyui-LayerForge — Comfyui-LayerForge
65. https://github.com/jtydhr88/ComfyUI-LayerDivider — ComfyUI-LayerDivider
66. https://www.runcomfy.com/comfyui-nodes/ComfyUI_LayerStyle — RunComfy ComfyUI Layer Style guide
67. https://comfyui-wiki.com/en/comfyui-nodes/image/image-composite-masked — ImageCompositeMasked node
68. https://www.tutorialspoint.com/python_pillow/python_pillow_compositing_images.htm — Pillow compositing tutorial
69. https://www.codecademy.com/resources/docs/pillow/image/composite — Pillow .composite() docs

### Character consistency & FLUX
70. https://huggingface.co/InstantX/FLUX.1-dev-IP-Adapter — InstantX FLUX IP-Adapter model card
71. https://comfyui-wiki.com/en/news/2024-11-22-instantx-flux-ipadapter-release — InstantX IP-Adapter release notes
72. https://www.runcomfy.com/comfyui-nodes/ComfyUI-IPAdapter-Flux — ComfyUI IP-Adapter Flux guide
73. https://www.aimodels.fyi/models/huggingFace/flux-monochromemanga-dataautogpt3 — FLUX MonochromeManga
74. https://www.siliconflow.com/articles/en/best-open-source-models-for-comics-and-manga — SiliconFlow "Best Open Source Models for Comics and Manga 2026"
75. https://apatero.com/blog/flux-2-everything-you-need-to-know-2025 — FLUX 2 complete guide
76. https://getimg.ai/guides/guide-to-ip-adapters — getimg.ai IP-Adapter guide

### Localization & text expansion
77. https://www.pairaphrase.com/blog/text-expansion-in-translation — Pairaphrase text expansion 2026
78. https://capitallinguists.com/japanese-translation-in-anime-manga-preserving-japanese-culture/ — Capital Linguists Japanese manga translation
79. https://j-entranslations.com/manga-translation-pitfalls/ — J-En Translations "Manga Translation Pitfalls"
80. https://connect.ajet.net/2020/04/10/anime-and-manga-translations-the-fall-of-localization/ — AJET CONNECT localization analysis
81. https://www.arc-japanese-translation.com/services/comic.html — Arc Communications comic localization
82. https://www.technologyreview.com/2024/12/02/1107562/this-manga-publisher-is-using-anthropics-ai-to-translate-japanese-comics-into-english/ — MIT Tech Review on Anthropic-powered manga translation

### Furigana & vertical CJK
83. https://en.wikipedia.org/wiki/Ruby_character — Ruby character (furigana)
84. https://github.com/typst/typst/issues/1489 — typst ruby/furigana support issue
85. https://asianabsolute.co.uk/blog/cjk-typesetting-challenges-workflows-and-best-practices/ — "CJK Typesetting in 2025"
86. https://helpx.adobe.com/incopy/using/formatting-cjk-characters.html — Adobe InCopy CJK formatting

### Speech bubbles & SVG
87. https://en.wikipedia.org/wiki/Speech_balloon — (re-cited for bubble shape canon)
88. https://blambot.com/pages/comic-book-grammar-tradition — (re-cited)
89. https://svgwg.org/svg2-draft/coords.html — SVG 2 spec coordinate systems
90. https://www.toolsfortexts.com/speech-bubble-generator — Speech Bubble SVG generator (reference)
91. https://commons.wikimedia.org/wiki/File:Speech_bubble.svg — Wikimedia speech bubble SVG
92. https://www.animeoutline.com/how-to-draw-manga-speech-bubbles/ — AnimeOutline manga speech bubbles tutorial
93. https://ilkaperea.com/2019/08/15/meaning-of-speech-bubbles-in-comics/ — "Meaning of Speech Bubbles in Comics"
94. https://tvtropes.org/pmwiki/pmwiki.php/Main/SpeechBubbles — TV Tropes Speech Bubbles
95. https://bookriot.com/speech-bubbles-in-comics/ — Book Riot "Ode to Speech Bubbles"

### Cross-references to parallel research
96. /tmp/rakuten_ai_chat_research.md — parallel agent (Rakuten AI Chat / Japan-market intel)
97. /tmp/webtoon_technical_reference.md — parallel agent (technical specs) [NOTE: file was not yet present at /tmp at time of this audit]
