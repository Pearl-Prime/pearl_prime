# Cover Design Intelligence Gap — 2026-05-04

**Author:** R8 (cover-design diagnosis pass, post-R7 wiring)
**Scope:** Why the operator's "strange / basic / no reason for being" complaint is structurally true even after R6/R7 shipped. What the design-intent ladder actually is, where the current pipeline sits ON it, and the methodology gaps that no amount of further yaml tuning will close.
**Posture:** Skeptical of R6 — the 4-layer framework is *necessary but not sufficient*. The real failure is upstream of typography and of identity overlays: the pipeline never models a reader's category-recognition decision at all.
**Sample failures used:** `artifacts/pipeline_examples/maat/cover_maat_boundaries.png` and `artifacts/pipeline_examples/manga_covers/joshin_cover_anxiety.png` — both 1024×1024 PNGs from an April 2026 commit that predate R5/R6/R7. They are however representative of what the architecture WILL still produce after R7, because R7 only fixes **layer 4 (book) and layer 6 (PIL composite)** of an 8-rung ladder, and the gibberish-title and missing-title failure modes both originate at rungs 0–2.

---

## Executive verdict (read first)

The operator is correct. The covers are "strange" not because of palette or typography, but because **the pipeline never executes the design decisions a real designer makes BEFORE opening Photoshop**. R1, R3, R4, R5, R6, R7 all added craft layers downstream of typography. None of them added the decision a designer makes in minute 0, which is: *what category does this book sit in, who else is on the shelf, and what visual contract have those readers learned to expect.* That decision is structurally absent from the pipeline. R6's 4-layer system (brand × author × series × book) is orthogonal to the decision a reader makes when scanning Amazon search results — the reader does not know your brand exists. The reader knows the **category**.

The single change with the highest leverage is not typography, not FLUX-engine tier, not motif yaml — it is **a category-anchor module that picks 3–5 comp bestsellers per (topic × locale) before any prompt is constructed and forces every downstream decision to mirror their visual contract first, then differentiate inside it**. Phase 1.

---

## Q1. Why do real bestsellers' covers "work" — the design-intent ladder

What follows is the explicit reasoning chain a category-aware indie or trad designer runs to produce a cover that, in <2 seconds of scan time, tells a stranger (a) what category, (b) what problem it solves, (c) why this book vs. its 50 shelfmates, (d) whom for. Each rung cites the published source where it's named explicitly; rungs marked "informal practice" reflect designer interview consensus rather than a single canonical text.

### Rung 0 — Pick the comp shelf BEFORE the cover.

The first decision is not a design decision. It is a category decision. Per Reedsy's guide to genre research, the designer/author starts at the Amazon Best Seller pages for the book's narrowest sub-category and pulls the top 10–20 covers that are CURRENTLY ranking. These are the comp shelf. (Reedsy: "Indie Author Book Cover Design — Research Phase.") Per Stuart Bache's "familiarity theory" interview with Joanna Penn: a designer's first move is to look at what's working in your genre because, as Bache puts it, ["people tend to buy things that they're used to."](https://www.thecreativepenn.com/2018/11/05/book-cover-design-tips-with-stuart-bache/) Per 100 Covers' service description: their team explicitly spends time browsing bestsellers in a genre to determine how to "blend in with bestsellers while still achieving a unique and creative look" — blending IN comes first, distinctiveness second.

The output of rung 0 is a 3-to-5-cover comp set saved as a reference. Not a mood board. A category contract. The fields the designer harvests from each comp:
- title-zone proportions (top vs. bottom vs. centered),
- title family (serif slab vs. sans display vs. script),
- title-vs-subtitle ratio,
- focal element archetype (single object vs. type-only vs. portrait vs. environment),
- color count (true k=2 vs. k=3 vs. k=4),
- accent palette (where the eye lands),
- byline weight (small vs. brand-the-author).

Source citations for rung 0:
- [Reedsy: Indie Author Book Cover Design — What Works in 2022](https://selfpublishingadvice.org/indie-author-book-cover-design-what-works-in-2022/) — "granular research into your specific subgenre(s)" is named as stage 1.
- [Reedsy: How to Design a Book Cover — 10 Dos and Don'ts](https://reedsy.com/blog/guide/book-cover-design/how-to-design/) — "DO: Signal your genre to readers" is dos rule 1.
- [Stuart Bache (interview, Creative Penn)](https://www.thecreativepenn.com/2018/11/05/book-cover-design-tips-with-stuart-bache/) — "look at what works in your genre."
- [100 Covers homepage](https://100covers.com/) — service starts with bestseller browsing.

### Rung 1 — Decide the cover's communication primary.

Per Reedsy DO #3 "Decide what to communicate," the designer picks ONE communicative goal before sketching: either a concrete plot/topic element (the *what*) or an abstract mood/promise (the *how it feels to read*). Both are valid; you do not get both. Picking both produces a cover that hedges.

Source: [Reedsy 10 Dos and Don'ts, rule 3](https://reedsy.com/blog/guide/book-cover-design/how-to-design/).

This is the rung that selects between "a feather" (object-as-symbol-for-the-promise) and "single bold word THE" (type-as-promise). It is NOT the rung that chooses the feather vs. the candle — that's rung 5.

### Rung 2 — Title comes before the cover.

Per Derek Murphy's 7 Unbreakable Rules, rule 4 ("Title is Integral"): the title must clearly indicate book type before any cover work begins. If the title is weak/oblique, the cover has to compensate via straplines and explicit category iconography. Per Murphy rule 5, **straplines** (subtitles or genre lines) are the formal repair mechanism for an evocative-but-unclear title. ([DIY Book Covers — Derek Murphy 7 Unbreakable Rules](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/))

Practically this means rung 2 has TWO sub-decisions:
- **2a:** Is the title category-clear on its own? If yes, cover can be evocative. If no:
- **2b:** The subtitle must carry the category and the promise. Per the indie self-help title pattern documented by Self-Publishing School and Reedsy: **main-title = the WHAT** (evocative, short, memorable, often metaphorical), **subtitle = the HOW + audience + outcome** (problem-promise-outcome with category keywords for Amazon search). Bestseller examples that follow this rigorously: *The Mountain Is You: Transforming Self-Sabotage Into Self-Mastery* (Brianna Wiest), *Master Your Emotions: A Practical Guide to Overcome Negativity and Better Manage Your Feelings* (Thibaut Meurisse), *Untangle Your Anxiety: A Guide To Overcoming An Anxiety Disorder By Two People Who Have Done It*. The current Phoenix book *The No That Saved Me — A Practical Guide to Setting Boundaries and Finding Peace* IS structurally correct at this rung. The failure mode for boundaries is downstream.

Sources:
- [Derek Murphy 7 Rules](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/)
- [Self-Publishing School: book title ideas](https://self-publishingschool.com/book-title-ideas-choose-perfect-title-book/)
- Reedsy Self-Help Title Patterns (search-result distillation; Reedsy does not host a single named "framework" doc, hence informal practice).

### Rung 3 — The blink test (the reason the pipeline must care about thumbnail size).

Per Murphy rule 3 ("Blink Test"): the cover must communicate genre and basic story elements within ~1 second of viewing. Per BookBub's "5 Ways Your Cover Hurts Sales," genre misalignment (rule 2) costs the most money — the cover functions as a "billboard" using established genre signals. Per Reedsy DO #1 "Signal your genre to readers." Per Creative Paramita's thumbnail-test rule, a cover gets <2 seconds at thumbnail and must pass with one focal point, one emotional read, and a legible title.

Concrete implementation: render at 100×160 px; a non-designer must name the category and read the title in ≤2 seconds. R6 §0.7 already adopts this; the gate is in `cover_quality_gates.py`. The PROBLEM is that the gate is a *post-render* check, not a pre-render contract — by the time the gate runs, the FLUX prompt already committed.

Sources:
- [Derek Murphy 7 Rules — Blink Test](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/)
- [BookBub: 5 Ways a Book Cover Could Hurt Sales](https://insights.bookbub.com/ways-book-cover-hurt-sales-fix/)
- [Reedsy 10 Dos](https://reedsy.com/blog/guide/book-cover-design/how-to-design/)
- Creative Paramita "Book Cover Thumbnail That Survives the Amazon Test" (cited in R6 §0.1).

### Rung 4 — Hierarchy is decided BEFORE imagery.

Per Murphy rule 7 ("Hierarchy"): for a non-celebrity author, title is 100% weight, author byline ~50% weight. Per Reedsy DO #4 ("single focal point"): one element wins the cover. Per KDPEasy's 2026 self-help ruleset: the title occupies "at least 40-50% of the cover's visual space" and the cover uses ["Never use more than 2 fonts"](https://www.kdpeasy.com/blog/self-help-book-cover-design). Per the BookBub failure list, a cover that hedges across multiple competing focal points (#1 lack of professionalism + #2 genre misalignment) is the #1 selling-killer.

The sub-decisions a real designer makes at rung 4:
- Is the cover **type-led** (no imagery, all-type) or **image-led** (one focal object) or **portrait-led** (a face) or **environment-led** (a horizon)? Picked from the comp shelf at rung 0.
- If type-led: which word in the title carries the punch? ONE word, set 1.3–1.5× the rest.
- If image-led: where does the focal element live (upper third / centered / lower third)? Determined by where the comp shelf places it.
- Title proportion: 40–60% of cover height total (KDPEasy 2026 rule).
- Author proportion: ~50% of title weight (Murphy rule 7).
- Subtitle: 25–40% of title weight, separate visual lane (KDPEasy: never on top of title).

Sources:
- [Derek Murphy 7 Rules — Hierarchy](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/)
- [Reedsy 10 Dos — single focal point](https://reedsy.com/blog/guide/book-cover-design/how-to-design/)
- [KDPEasy: Self-Help Book Cover Design 2026](https://www.kdpeasy.com/blog/self-help-book-cover-design)
- [BookBub: 5 Ways a Cover Hurts Sales](https://insights.bookbub.com/ways-book-cover-hurt-sales-fix/)

### Rung 5 — Pick the focal element from the comp shelf's vocabulary.

Only NOW does the designer decide a feather vs. a candle vs. a horizon line vs. a typeset capital "N". The picking is constrained by rung 0's comp shelf — you pick from the SAME visual vocabulary the bestsellers in your sub-category use. You do not import a feather-quill-on-Greek-key-border because that's not in the comp set for self-help boundaries; that's in the comp set for pop classics / oracle decks / new-age.

This is also the rung where R6's 4-layer differentiation applies (brand × author × book), but it applies INSIDE the comp shelf's visual contract. R6 swaps the order: it picks brand identity first and then strains to make brand identity look like a category. The reader doesn't reward that.

Source: informal practice, but consistent across the [Stuart Bache interview](https://www.thecreativepenn.com/2018/11/05/book-cover-design-tips-with-stuart-bache/) and [Derek Murphy rule 1 (Membership)](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/) and [Reedsy DO #1](https://reedsy.com/blog/guide/book-cover-design/how-to-design/).

### Rung 6 — Color discipline and the 60-30-10 rule.

Per KDPEasy: ["Use your primary color for 60-70% of the cover, a neutral (white, black, or gray) for 20-30%, and an accent color for 10%."](https://www.kdpeasy.com/blog/self-help-book-cover-design) Maximum 3 colors total. Per Reedsy DO #6 ("strong contrast and lighting") and DO #7 ("test different color schemes"). Per BookBub's "professionalism" rule, weak color discipline reads as amateur regardless of the rest.

The 60-30-10 must be enforced AT THE PROMPT level (negative prompt: limit color count) AND AT POST-PROCESSING (k-means quantization gate). R6 already proposes this; `cover_quality_gates.py` checks the post-processing side. Neither the FLUX prompt builder nor the PIL renderer currently enforce it as a pre-render contract.

### Rung 7 — Production tells (what cues say "art-directed").

R6 §0.3 nails this. Eight tells, all real, all sourced. The relevant ones for our pipeline:
- **Hand-tweaked title type** vs. font-pick (we're at font-pick).
- **Single conceptual image** vs. composite (we composite by default — feather + compass + wings + Greek key on Maat).
- **2–3 colors total** (we have 5+).
- **Off-white not pure white** (R6 added this gate).
- **Type sits ON design, not OVER it** (R5 fixed the matte-panel band-aid).
- **Author byline small/confident** (we currently render "Maat" as accent gold, larger than appropriate).

### Rung 8 — Validate with category readers.

Per Reedsy DO #10: feedback comes from **active readers of your sub-genre**, not from designers, friends, or the author. Per BookBub: covers that pass internal review but fail with the genre's actual audience are the #1 silent killer. This is the rung that says "show 4 covers from the same brand to a non-designer; can they name each?" R6 §6 named gates marked `manual: true` capture this. The PROBLEM is the manual gates are an opt-in step, not a blocking step.

---

### Summary of the ladder (cite-checkable):

| Rung | Decision | Canonical source |
|---|---|---|
| 0 | Pick comp shelf (3–5 bestsellers in sub-category) | Reedsy guide; Stuart Bache; 100 Covers |
| 1 | Pick communication primary (concrete vs. abstract) | Reedsy DO #3 |
| 2 | Title carries category OR subtitle does | Murphy rules 4, 5 |
| 3 | Blink test at 1-2s thumbnail | Murphy rule 3; BookBub rule 2; Reedsy DO #1 |
| 4 | Hierarchy: title 100, author 50, subtitle 30 | Murphy rule 7; KDPEasy; Reedsy DO #4 |
| 5 | Pick focal from comp-shelf vocabulary | Murphy rule 1; informal |
| 6 | 60-30-10 color, ≤3 colors, off-white not pure | KDPEasy; Reedsy DO #6, #7 |
| 7 | Production tells (single image, custom type) | Reedsy; Damonza; Steve Fenton |
| 8 | Validate with category readers | Reedsy DO #10; BookBub |

---

## Q2. Diagnose the two failing covers — defect list keyed to the ladder

### Cover A — `artifacts/pipeline_examples/maat/cover_maat_boundaries.png`
*Topic: BOUNDARIES (modern self-help). Visible: feather quill + golden compass + winged shield + Greek-key border + royal navy + gold. Title visible: "No That Saved Me" (the leading "The" is missing — clipped or wrapped to invisibility). No subtitle visible. No author byline. No publisher mark. Square 1024×1024 (not KDP 1600×2560).*

| Rung failed | Specific defect | Severity |
|---|---|---|
| **0 (comp shelf)** | The visual vocabulary (Greek key border, winged sun, antique compass, feather quill on royal navy) is from the *new-age oracle / classical antiquity / pop-mythology* shelf, not the *self-help boundaries* shelf. Cloud / Townsend's *Boundaries*, Nedra Glover Tawwab's *Set Boundaries Find Peace*, Henry Cloud's *Necessary Endings* all use type-led or simple-object-on-flat-color. Comp set was never consulted. | Architectural |
| **1 (communicative primary)** | The cover hedges: it tries to be both "ancient wisdom mood" (mythology imagery) AND "modern self-help promise" (the title's structure). Reader cannot tell which contract it's signing. | High |
| **2 (title→category)** | Title "The No That Saved Me" IS a working evocative title — but the cover renders only "No That Saved Me," dropping or wrapping the leading "The." The result reads as gibberish ("No that saved me?") because the title-fitting algorithm broke the syntactic unit. Subtitle ("A Practical Guide to Setting Boundaries…") which would carry the category for the reader is **absent from the rendered output**. Without the subtitle the cover loses its single most reliable category signal. | Critical |
| **3 (blink test)** | At thumbnail size: focal hierarchy is ambiguous (title vs. compass vs. wings all compete). One-word emotional read is "ancient" — wrong for a 2026 self-help boundaries book where the correct read is "firm" or "honest" or "decisive." | Critical |
| **4 (hierarchy)** | Title is 2 lines on a square canvas; the compass-with-wings is roughly equal visual weight; Greek-key border occupies ~15% of the frame and competes for attention. There is no single focal point. Author byline absent — reader doesn't know whose book this is. | Critical |
| **5 (focal from comp vocab)** | Feather + compass + wings + Greek key are FOUR symbols on one cover. R6 §0.3 production-tell #2 explicitly bans composite imagery: bestsellers use ONE thing. | High |
| **6 (color discipline)** | Royal navy + gold + cream off-white + Greek-key dark navy + the brown of the feather + black of the compass. By eye, 5+ visible colors. Violates 60-30-10 and the ≤3-color rule. | High |
| **7 (production tells)** | The Greek key border and ornate metallic compass-with-wings read as STOCK CLIP-ART, the AI-tell #1 R6 §0.4 catalogues. Title type is a generic font pick (likely Times-bold), not hand-tweaked. | High |
| **8 (validate with category reader)** | A reader who reads boundaries self-help books would not pick this up. They'd skip to the next thumbnail. | Critical |

**Root structural pattern:** the cover was generated as if it were a *Truth Compass brand* artifact (where the brand inspiration in R6 §1 names Riverhead-style typographic-led design with terracotta accents), but the actual rendered output uses a totally different visual register (mythology/oracle). This implies the brand-aesthetic layer was *named* in yaml but **not enforced by whatever generator produced this file**. The file predates R6/R7 — it's an April 2026 artifact — but the architectural issue WILL persist if upstream rungs aren't filled in.

### Cover B — `artifacts/pipeline_examples/manga_covers/joshin_cover_anxiety.png`
*Topic: ANXIETY (Joshin / Still Forest / Zen). Visible: beautiful sumi-e painting of Mt. Fuji, lone seated figure under a pine, low sun. A few kanji top-left ("安". 安 reads "peace"/"calm"). Small red hanko stamp bottom-left. NO English title. NO subtitle. NO author byline. NO publisher mark. Square 1024×1024.*

| Rung failed | Specific defect | Severity |
|---|---|---|
| **0 (comp shelf)** | The comp shelf for English-language self-help anxiety includes *Untangle Your Anxiety*, *Hope and Help for Your Nerves*, *DARE*, *The Anxiety and Phobia Workbook*, *First, We Make the Beast Beautiful*. None are sumi-e-style art prints. The only category where this composition would belong is *Zen art books / Japanese-aesthetics decor books / meditation gift books* — adjacent categories with a totally different reader. | Architectural |
| **1 (communicative primary)** | The cover commits HARD to "abstract atmospheric mood" — but anxiety self-help readers buy on "concrete promise of relief" (Reedsy DO #3). The communicative primary is wrong for the category. | Critical |
| **2 (title→category)** | **The cover has no English title at all.** This is a complete pipeline failure — the title text never made it onto the canvas. The hanko/kanji top-left are the only typography and they are illegible to an English reader. Reedsy DO #1 (signal genre) and Murphy rule 4 (title is integral) are both violated absolutely. | Catastrophic |
| **3 (blink test)** | Reader at thumbnail size sees a meditation art print. Cannot identify the genre, cannot read the title, cannot identify the author. Fails ALL three blink criteria. | Catastrophic |
| **4 (hierarchy)** | Hierarchy is "Mt. Fuji is 100, lone figure is 60, kanji is 5, hanko is 5." For a *book cover*, the title MUST be 100. There is literally no title block. | Catastrophic |
| **5 (focal from comp vocab)** | Sumi-e Mt. Fuji landscape is gorgeous and from a coherent visual tradition — just not the comp tradition for this category. (It would be correct on the comp shelf for a meditation gift book, e.g. Shambhala Pocket Library — but Phoenix's Still Forest brand spec in R6 §1.2 is "single ink stroke / enso / low pine silhouette," not full landscape composition.) | High |
| **6 (color discipline)** | Sumi-e on cream — actually passes 60-30-10 (cream + black ink + small red hanko). This rung is OK. | OK |
| **7 (production tells)** | Beautiful production — but the cover doesn't contain a book title, so its production polish is wasted. | OK on imagery, fails on integration |
| **8 (validate with category reader)** | Anxiety self-help reader: skip. Meditation art print buyer: maybe. WRONG audience. | Critical |

**Root structural pattern:** the FLUX imagery pass produced a beautiful image, the typography compositing pass *never ran*. The cover was saved without title overlay. This is a pipeline integration failure — Stage 1 (imagery) shipped, Stage 2 (PIL composite) was either skipped or failed silently. R6/R7 should fix this for new renders, but only if the typography step fails closed (raises rather than saves an imagery-only file).

---

## Q3. Where in the pipeline does each defect originate

The actual pipeline (verified against the code) has these stages:

1. **Title generation** — manually authored in `scripts/release/build_epub.py:TEACHER_BOOKS` (line 56–96). Static dict. Per-book title + subtitle + author + publisher + topic + lang. **No category-comp resolution. No problem-promise-outcome generator. No category-keyword check.**
2. **Subtitle generation** — same dict; static. (`build_epub.py:56`)
3. **Author / brand identity selection** — TEACHER_BOOKS author/publisher fields. R6/R7 added `cover_identity_system.yaml` overlay (`render_kdp_cover.py:156–185`).
4. **FLUX imagery prompt construction** — `scripts/publish/render_imagery_for_template.py` reads `bestseller_templates.yaml::flux_subject` and `cover_identity_system.yaml::books.<id>.this_book_subject`. There is no per-genre comp-title vocabulary list; just a hand-curated subject string per book.
5. **FLUX render** — same module + `scripts/video/flux_client.py`.
6. **PIL text composite** — `scripts/publish/render_kdp_cover.py:746–960`. R5/R7. This is where R7 wired in the identity-system overlay (`_apply_identity_overrides`, line 658).
7. **Quality gates** — `scripts/publish/cover_quality_gates.py`. Six automated gates (focal clarity, OCR title legibility, ≤3 colors, brand-palette ΔE, signature-color presence, warm off-white). R7. **Five "manual" gates from R6 §6 are not automated and not blocking.**
8. **Output** — saved to `artifacts/pipeline_examples/<id>/cover_<id>_FINAL.png` per `render_kdp_cover.py:1019`.

### Defect → originating stage

| Defect (from Q2) | Originating stage | File:line / specifics |
|---|---|---|
| Maat: visual vocabulary from wrong shelf (oracle, not boundaries) | **Stage 4** (FLUX prompt) AND **Stage 0 (missing)** — the prompt was generated by an ad-hoc upstream pass with no comp-shelf check; no module exists that says "for topic=boundaries, the comp vocabulary forbids feather-quill / Greek-key / winged compass." `render_imagery_for_template.py:69+` reads `flux_subject` from the template yaml; for boundaries (which is `imagery_zone: null`) the FLUX pass should NOT have run at all. The artifact predates R7 wiring; the defect is that **nothing in the stack rejects the resulting image as off-category.** | Architectural — needs new module |
| Maat: title gibberish ("No That Saved Me") | **Stage 6** — `render_kdp_cover.py::_fit_font_to_box` (line 349). The greedy wrap (`_wrap_to_width`, line 327) shrinks until "The No That Saved Me" fits, which can yield a wrap point between "The" and "No"; if "The" lands on a separate line and the line-height computation drops it off the title_zone bbox, only "No That Saved Me" renders. **Note however: the file is 1024×1024, not the renderer's 1600×2560 output, so this specific render did not come from `render_kdp_cover.py`.** It came from an earlier pipeline (likely `scripts/image_generation/generate_kdp_all_formats.py:_overlay_typography` — line 270+, which uses the same greedy `_wrap_text` logic at line 252). The structural fault — wrapping a title without preserving syntactic units — is shared. | Critical |
| Maat: subtitle missing | **Stage 6** — same renderer; subtitle never composited. The 1024×1024 generator (`generate_kdp_all_formats.py`) DOES draw subtitles (line 547). For this cover the subtitle was either skipped because of a config gap or rendered off-canvas. | High |
| Maat: author missing | **Stage 6** — same — `generate_kdp_all_formats.py` does draw author at line 554. Lost in this specific render's config. | High |
| Maat: 5+ colors | **Stage 4** (FLUX prompt) — no negative-prompt color budget. **Stage 7** color gate (`cover_quality_gates.py::gate_color_count_le_3`, line 198) DOES catch this AT POST-RENDER but it's a post-hoc check, not a re-render trigger. | High — gate exists but is non-blocking |
| Maat: composite imagery (4 symbols on one cover) | **Stage 4** — FLUX prompt did not say "ONE symbol only." The negative prompt at `generate_bestseller_covers.py:232` lists "busy, cluttered" but not the structural "more than one focal element." | High |
| Joshin: no English title at all | **Stage 6** — the typography composite step never ran on this image. The 1024×1024 file is from the imagery pass alone. There is no fail-closed gate that says "if title is empty in the rendered output, halt." | Catastrophic |
| Joshin: visual register doesn't match Phoenix's own Still Forest brand spec | **Stage 4** — the FLUX prompt drifted from the brand spec. R6 §1.2 names Still Forest's motif pool as `[single_ink_stroke, enso, low_pine_silhouette, single_stone]`; this cover's motif is "Mt. Fuji landscape with seated figure," which is OFF spec. The prompt didn't reference R6's motif pool. | Architectural |

### Is R6's `cover_identity_system.yaml` actually being applied?

Verified against code: **partially.** `render_kdp_cover.py::_apply_identity_overrides` (line 658) does layer brand palette → template, signature color → subtitle, type quirk → title case. But:

1. The identity overlay is only invoked when the caller passes `--identity-book` (CLI flag at line 1081, conditional at line 822). The default render path does NOT apply identity. The batch path (`_run_batch`, line 1005) does NOT pass `book_id`. So **R7 wiring is conditional, not default**.
2. The overlay does not feed into the **FLUX prompt builder** at all (Stage 4). Stage 4 is `render_imagery_for_template.py` and it reads `cover_identity_system.yaml::books.<id>.this_book_subject` directly — but only the `this_book_subject` string. The brand's `motif_pool`, the author's `motif_focus`, and any of R6's category-positioning fields are NOT consumed by the prompt builder.
3. There is no `genre_comp_vocabulary` field in the yaml for FLUX to honor; R6's framework is brand/author/book centric and has no category-comp anchor.

### Does `cover_quality_gates.py` validate the four reader-readability tests?

Cross-checking the four R8 readability tests (genre clarity, promise clarity, hierarchy, audience match) against the six implemented gates:

| Reader test | Gate that covers it | Coverage |
|---|---|---|
| Genre clarity (the cover signals self-help-boundaries to a self-help-boundaries reader) | None | **0%** — there is no gate that compares the cover's visual register to the comp shelf for the topic. |
| Promise clarity (a stranger can name what the book promises) | `gate_title_ocr_legibility` only checks luminance contrast at thumbnail; doesn't read the title text or check the subtitle promise. | **15%** — title legibility ≠ promise legibility. |
| Hierarchy (one focal point) | `gate_focal_clarity_thumbnail` checks per-quadrant variance ≥ 1.6× | **70%** — variance is a proxy for hierarchy, not perfect, but real. |
| Audience match (the right reader would pick this up) | None | **0%** — requires category-reader validation, which is the manual gate not enforced. |

**Net: ~22% of the design-intent ladder's reader-readability tests are gated by code today.** The remaining 78% live in either the manual gates (which don't block) or are absent entirely.

---

## Q4. Methodology gaps — what's missing

For each gap I name: **what** module is missing, **where** it slots into the 8 stages, **inputs** it needs, **output contract**, and the **design framework** it operationalizes.

### MG-1. Category-anchor module — the rung 0 that's missing

**What.** A module `scripts/publish/category_anchor.py` (proposed) that, given (topic, locale, format), returns a structured comp-shelf record with the visual contract harvested from the top 5 currently-ranking covers in that Amazon sub-category.

**Where.** New stage 0, runs before stages 1–6. Its output is consumed by stages 1, 2, 4, 5, 6, 7.

**Decision-time inputs.**
- `topic` (e.g. "boundaries", "anxiety", "grief")
- `locale` (en, ja-JP, zh-CN, etc.)
- `format` (kdp_ebook, audiobook, social_thumb)
- Optionally: a curated comp-shelf yaml that operator pre-populates (because live Amazon scraping is out of scope/legally fragile).

**Output contract.**
```yaml
category_anchor:
  topic: boundaries
  locale: en
  comp_set: [<5 comp covers>]
  visual_contract:
    layout_archetype: type_led | image_object_led | portrait_led | environment_led
    title_zone_pct: {x: [10,90], y: [12,42]}        # where bestsellers place title
    title_family: serif_slab | sans_display | script | hand_lettered
    title_to_subtitle_ratio: 3.2
    title_to_author_ratio: 2.8
    focal_archetype: single_capitalized_word | single_object | none
    accent_palette: [#hex, #hex]
    color_count_target: 2
    forbidden_motifs: [oracle_iconography, mythology_symbols, classical_borders]
    required_signals: [problem_solution_subtitle, author_byline_present]
  blink_test_targets:
    - one_word_register: firm | tender | clear | calm | fierce | …
    - category_recognition_seconds: ≤ 2
```

**Reference framework.** Reedsy "Indie Author Book Cover Design — Research Phase"; Stuart Bache's familiarity theory; 100 Covers' bestseller-browse process; Murphy rule 1 (Membership). This is rung 0 of the ladder, currently absent.

**Why this is the highest-leverage missing module.** Without it, every downstream rung optimizes locally — perfect typography for the wrong category still loses readers. The Maat cover failed Q2 rungs 0, 1, 4, 5, 7, 8 — most of those failures cascade from the absent comp shelf.

---

### MG-2. Title-syntactic-fitter — preserve the leading article

**What.** A wrapping algorithm that respects syntactic units. "The No That Saved Me" must NEVER wrap such that "The" is dropped or isolated to a phantom line that gets clipped.

**Where.** Stage 6, replacing the greedy `_wrap_to_width` in `render_kdp_cover.py:327` and `generate_kdp_all_formats.py:_wrap_text:252`.

**Decision-time inputs.** Title string, font, max width, max height. Optionally: explicit line-break hints from the title spec (e.g. `"The No That Saved Me"` could carry an author-supplied line break: `"The No\nThat Saved Me"`).

**Output contract.** A line list with the guarantee that no syntactic unit (article + noun, preposition + noun, "is" + complement) is split across a line break. If no wrap satisfies, raise `TitleTooLongForTemplateError` (already exists at line 117) and surface the failure.

**Reference framework.** Stuart Bache: hand-tweaked title type. Riverhead house style: title typography is a designer decision, not an automated one. There is no public framework for this; it's craft. The mitigation is to add author-supplied line break hints to `cover_identity_system.yaml::books.<id>.title_linebreak`.

---

### MG-3. Pre-render reader test — fail before FLUX, not after

**What.** A pre-render contract validator that, given the planned (title, subtitle, author, comp-shelf, focal-archetype, color-budget), returns pass/fail BEFORE any FLUX call. Specifically checks: (a) is the title category-clear OR does the subtitle carry the category, (b) is the focal archetype on the comp shelf, (c) is the color budget ≤3, (d) is the type-led/image-led decision consistent with the comp shelf.

**Where.** Between stages 3 and 4. Output becomes a hard gate.

**Decision-time inputs.** category_anchor record (from MG-1) + book metadata + planned imagery prompt + planned typography spec.

**Output contract.** `{passed: bool, blocking_failures: [...], warnings: [...]}` with structured failure reasons. Blocking failures halt the render and surface to operator.

**Reference framework.** Murphy "Blink Test"; Reedsy DO #1 + DO #4; BookBub "5 Ways" failure modes #1 (professionalism) and #2 (genre misalignment). This converts post-hoc gates into pre-render contracts.

---

### MG-4. FLUX-prompt builder that consumes category vocabulary

**What.** Replace the current `bestseller_templates.yaml::flux_subject` (a hardcoded string per genre) with a builder that composes the prompt from: `category_anchor.visual_contract` + `cover_identity_system.yaml::books.<id>.this_book_subject` + `forbidden_motifs` (negative prompt).

**Where.** Stage 4. Replaces `render_imagery_for_template.py`'s prompt-string lookup.

**Decision-time inputs.** category_anchor (MG-1), book identity (existing R6 yaml), brand motif_pool (existing R6 yaml), author motif_focus (existing R6 yaml), the engine config (flux1-dev / 28 / dpmpp_2m / karras, per H1=A decision in the operator's MEMORY.md).

**Output contract.** A FLUX prompt + negative_prompt pair where:
- positive prompt anchors on the comp shelf's focal_archetype + brand motif_focus,
- negative prompt enumerates `forbidden_motifs` AND a hard color-budget constraint AND "no text, no letters, no typography" (which Steve Fenton calls the "AI text smudge" tell — generators cannot reliably render readable text yet, so the renderer's PIL composite stage MUST own all titling).

**Reference framework.** R6 §0.6 "Type integration"; Damonza 2025 AI-cover guide on what FLUX should and should not do; Steve Fenton "warning signs of an AI-generated book."

---

### MG-5. Category-reader validation gate (the manual gates upgraded)

**What.** Operationalize R6 §6's manual gates by either (a) staffing a small panel of category readers and routing covers through them as a blocking step, OR (b) accepting a multi-cover side-by-side test that the operator runs at fixed cadence with a non-designer panelist, OR (c) at minimum, surfacing the manual gates as a **mandatory operator visual check before the cover ships to KDP**, with a click-to-pass UI step that's recorded in `artifacts/cover_validation_log/`.

**Where.** New stage 8. Blocks publish, not render.

**Decision-time inputs.** Cover, comp-shelf, category sample. Reader's name + topic (for audit).

**Output contract.** `cover_validation_record.yaml` with timestamp, panelist, pass/fail per manual gate, free-text comment, decision.

**Reference framework.** Reedsy DO #10 (feedback from genre readers); BookBub failure mode #2 (genre misalignment is the silent killer); R6 §6 already proposes these but as `manual: true` advisory.

---

### MG-6. Title-and-subtitle generator that knows the category

**What.** A title/subtitle generator (or operator-curated template engine) that emits, per (topic × persona × locale): an evocative WHAT-title (≤6 words, syntactic unit-respecting, lineable in 2–3 lines at the renderer's title_zone) PLUS a HOW-subtitle (problem-promise-outcome with category keywords for Amazon SEO). This is **NOT** an LLM call — Tier policy bans paid LLM APIs and Tier 2 (Gemma/Qwen) is for unattended pipelines. Operator-present (Tier 1 / Claude Code) writes them and parks them in `cover_identity_system.yaml::books.<id>.{title, subtitle}` as today, but with a **schema gate that validates the title-subtitle pair against the rung 2 sub-decisions (2a: category-clear title? 2b: category-carrying subtitle?).**

**Where.** Stage 1 (title) + Stage 2 (subtitle), with a new validator gate before the rest of the pipeline runs.

**Decision-time inputs.** topic, locale, persona, category_anchor (MG-1), 1–2 comp-bestseller subtitles for that sub-category.

**Output contract.** A validated (title, subtitle) pair where subtitle structure matches problem-promise-outcome AND contains the category's primary keyword (e.g. "boundaries" must appear in the subtitle for a boundaries book; "anxiety" must appear for an anxiety book).

**Reference framework.** Self-Publishing School / Reedsy: the [main-title=what, subtitle=how/why pattern](https://self-publishingschool.com/book-title-ideas-choose-perfect-title-book/); Murphy rules 4 + 5 (title is integral, straplines repair).

---

### MG-7. Type-rendering production-tells layer (titling polish)

**What.** Per R6 §0.3 production tell #1, bestseller covers use hand-tweaked title type — kerning fixed character-by-character, weight punched on key letters, custom ligatures. The current renderer uses `font.set_variation_by_axes` (line 237) which gets you a weight axis but no per-character kerning. A production-tells layer would, at minimum: (a) per-genre custom kerning table for the title font, (b) optional one-letter weight bump (the "key word" Truth Compass calls out in R6 §1.2 — for "The NO That Saved Me," NO renders 1.3× and in accent color), (c) optical kerning pass for problematic pairs (To, Wo, Av, etc.).

**Where.** Stage 6, inside `_draw_text_with_shadow` (line 389).

**Decision-time inputs.** Title string, brand typography spec (from R6 yaml), accent color, key-word index (NEW field needed in `cover_identity_system.yaml::books.<id>.key_word_index`).

**Output contract.** Rendered title block where the key word is visually punched (size + color), with corrected per-character kerning.

**Reference framework.** R6 §0.3; Riverhead house style (PRH "Behind the Book Covers" Grace Han feature); The Brief AI "20 Iconic Examples of Book Cover Typography." Note: this is craft territory, not framework territory — diminishing returns past a competent baseline.

---

### MG-8. Pipeline integration tests with golden references

**What.** Per-brand × per-topic golden-reference covers that are checked into git (current `artifacts/pipeline_examples/` is a stale demo cache, NOT a regression set). Every PR that touches the renderer or yaml runs a small batch and diffs against goldens; significant divergence triggers a manual review gate.

**Where.** CI, between stages 7 and 8.

**Decision-time inputs.** A subset of representative books × locales × formats. Ideally one per (brand × type-dominant flag).

**Output contract.** Pixel-diff report; flag covers that drift > N% from golden.

**Reference framework.** Standard test-driven design discipline; R6 §6 manual gates are the current substitute and they're insufficient.

---

## Q5. Recommended phase plan

Ordered by leverage. The operator picks which phases to authorize.

### PHASE 1 — Category-anchor module (MG-1) + pre-render reader test (MG-3)

**Rationale.** MG-1 alone fixes Q2 rungs 0, 1, 5, 8 across both failing covers. It is the missing rung 0 — without it everything downstream optimizes for the wrong shelf. Pairing it with MG-3 (pre-render gate) ensures defects are caught BEFORE FLUX spend, not after.
**Risk if skipped.** All future covers continue to be brand-pretty but category-wrong. The Truth Compass terracotta + Riverhead-typography spec keeps producing covers that don't read as "self-help boundaries" to a self-help-boundaries reader.
**Size.** Medium (one new module, one yaml schema extension, one gate). ~400–600 lines.
**Prerequisites.** Operator must pre-curate the comp-shelf yaml — 13 brands × ~5 topics × en/ja/zh-CN ≈ 200 (topic, locale) cells, with 5 comp covers per cell (image references + harvested fields). This is the human-authored data layer the pipeline currently lacks; live Amazon scraping is out of scope. **Operator is the prerequisite, not a tool.**

### PHASE 2 — Title-syntactic-fitter (MG-2) + title-and-subtitle generator validator (MG-6)

**Rationale.** Fixes the Maat "No That Saved Me" gibberish (MG-2) and the structural risk that titles lacking a category-keyword in the subtitle ship anyway (MG-6). Both are small, both are bug-fix-shaped, both have known designs.
**Risk if skipped.** Continued title-rendering gibberish on titles with leading articles ("The No…", "The Way of…", "The Body Keeps…"). Titles that don't carry the category keyword in the subtitle remain category-orphan.
**Size.** Small (refactor `_wrap_to_width` to be syntax-aware, add a yaml schema validator). ~150–250 lines.
**Prerequisites.** None for MG-2. MG-6's validator depends on MG-1's category_anchor for the subtitle keyword check.

### PHASE 3 — FLUX prompt builder consumes category vocabulary (MG-4)

**Rationale.** Replaces hardcoded `flux_subject` strings with a category-anchor-aware prompt builder. Closes the path that sent the Joshin cover to "Mt. Fuji landscape" instead of "single ink stroke / enso." Closes the path that allowed Maat's mythology imagery in the first place.
**Risk if skipped.** The brand/author/book identity layers stay in yaml but never reach the FLUX prompt. R7's wiring remains brand-aesthetic-only on the typography side; FLUX continues to drift.
**Size.** Medium. New prompt builder module replacing the current string lookup. Refactor of `render_imagery_for_template.py`. ~300–500 lines.
**Prerequisites.** PHASE 1 (depends on category_anchor). Engine tier flux1-dev / 28 steps / dpmpp_2m / karras (already H1=A in MEMORY.md).

### PHASE 4 — Manual-gate operationalization (MG-5)

**Rationale.** Reedsy DO #10 and BookBub failure mode #2 both name "category-reader feedback" as the silent killer. R6 §6 has the gates; they need to actually block publish. Cheapest version: an operator click-to-pass UI before KDP upload, recorded in an audit log. Most expensive version: a paid 5-reader panel per cover. Phase 4 picks the cheapest version that's better than zero.
**Risk if skipped.** Covers that pass automated gates but fail with category readers continue to ship. The 800-config catalog amplifies this.
**Size.** Small (a CLI gate + a yaml log; no panel infrastructure). ~100–200 lines.
**Prerequisites.** None.

### PHASE 5 — Production-tells layer (MG-7) + golden-reference regression set (MG-8)

**Rationale.** Polish + safety net. The production-tells (custom kerning, key-word punch) take competent covers to bestseller-grade. The golden references prevent silent regressions when yaml or renderer code changes. Both are low-risk additions with diminishing returns.
**Risk if skipped.** Covers feel "competent template-fill" rather than "designed." Regressions land silently between PRs.
**Size.** Medium total (kerning tables per font ~150 lines; golden reference setup ~200 lines + ~50 reference covers).
**Prerequisites.** All earlier phases — these are the polish layer.

---

## §A. Where I push back on R6

R6 is good research and fixes real things. But it has two structural blind spots that bear on the operator's complaint:

1. **R6 starts from brand identity, not from category.** The 4 layers are brand × author × series × book. None of those are the layer the *reader* uses. The reader uses category. Without an explicit category layer ABOVE brand, brand identity becomes a *closed system* that can drift away from category convention without any pressure to come back. Truth Compass-as-Riverhead is a coherent brand vision; that vision shipped a cover with a feather-quill on Greek key on royal navy on a *boundaries* book. Brand without category is decorative.

2. **R6's quality gates run after FLUX, not before.** Six automated gates + five manual gates, all post-render. The defects this catches are the cheap defects — color count, off-white, focal variance. The expensive defects (wrong category, wrong promise, wrong audience) survive automated gates because those gates are visual-statistics-based, not category-semantic. The fix is pre-render contracts, which means MG-3 (and the category-anchor module that feeds it).

R6 is correct that the four production layers exist. But the layer above all of them — the comp shelf — is missing, and most of the operator's "strange / no reason" complaint cashes out as that absence.

---

## §B. The gibberish title + missing title — a final note

The two specific failures the operator surfaced (Maat title gibberish + Joshin title missing) have *immediate* fixes that don't require any of the architectural work above:

- **Maat:** add `key_word_index` to `cover_identity_system.yaml::books.maat`, add line-break hint in title field, fix `_wrap_to_width` to be syntactic-unit-aware. ~1 day.
- **Joshin:** verify that `render_kdp_cover.py` is fail-closed when the typography composite step has no title to draw — currently `render_kdp_cover.py:794` already raises if title is empty, so the issue is that an UPSTREAM step (the imagery-only generator) shipped without invoking the composite step at all. Fix: route ALL final covers through `render_kdp_cover.py`, never publish raw imagery. ~1 day.

These two day-scoped fixes will eliminate the surface-level WTF the operator is reacting to. They will not, however, eliminate the structural cause — covers will still be brand-pretty and category-wrong. The phase plan above is the structural fix.

---

## §C. References

### Design framework sources

- [Reedsy — How to Design a Book Cover (10 Dos and Don'ts)](https://reedsy.com/blog/guide/book-cover-design/how-to-design/)
- [Reedsy — What Makes a Good Book Cover? (Research and Trends)](https://reedsy.com/blog/guide/book-cover-design/)
- [Reedsy / Self-Publishing Advice — Indie Author Book Cover Design 2022](https://selfpublishingadvice.org/indie-author-book-cover-design-what-works-in-2022/)
- [Derek Murphy — 7 Unbreakable Rules of Professional Book Cover Design (DIY Book Covers)](https://diybookcovers.com/the-7-unbreakable-rules-of-professional-book-cover-design/)
- [Stuart Bache — interview on The Creative Penn (Joanna Penn)](https://www.thecreativepenn.com/2018/11/05/book-cover-design-tips-with-stuart-bache/)
- [The Creative Penn — Find a Book Cover Designer (resource hub)](https://www.thecreativepenn.com/bookcoverdesign/)
- [BookBub — 5 Ways a Book Cover Could Hurt Sales](https://insights.bookbub.com/ways-book-cover-hurt-sales-fix/)
- [BookBub — Cover Reveal Checklist](https://insights.bookbub.com/cover-reveal-checklist/)
- [KDPEasy — Self-Help Book Cover Design: Minimalist Trends for 2026](https://www.kdpeasy.com/blog/self-help-book-cover-design)
- [100 Covers — service description](https://100covers.com/)
- [Self-Publishing School — Compelling Book Title Ideas](https://self-publishingschool.com/book-title-ideas-choose-perfect-title-book/)
- [Creativindie — How to Design a Self-Help / Business Book Cover](https://www.creativindiecovers.com/how-to-design-a-self-help-business-book-cover/)
- [Lit Hub — Best Book Covers of 2025](https://lithub.com/the-173-best-book-covers-of-2025/)
- [PRH — Behind the Book Covers with Riverhead's Grace Han](https://global.penguinrandomhouse.com/announcements/behind-the-book-covers-with-riverheads-grace-han/)
- [Steve Fenton — 6 Warning Signs of an AI-Generated Book](https://stevefenton.co.uk/blog/2025/01/generated-books/)
- [PRINT Magazine — 100 Best Book Covers of 2024](https://www.printmag.com/book-covers/100-of-the-best-book-covers-of-2024/)

### Phoenix internal sources

- `artifacts/research/cover_quality_and_differentiation_framework_2026-05-03.md` (R6, 1027 lines)
- `artifacts/research/kdp_bestseller_cover_analysis_2026-05-02.md` (R1)
- `artifacts/research/bestseller_titles_seo_covers_research.md` (R6 companion)
- `config/publishing/cover_identity_system.yaml` (R6 yaml, R7 wiring target)
- `config/publishing/bestseller_templates.yaml` (R4)
- `config/publishing/kdp_cover_typography.yaml` (R3)
- `scripts/publish/render_kdp_cover.py` (R5, R7)
- `scripts/publish/render_imagery_for_template.py` (Stage 4)
- `scripts/publish/cover_quality_gates.py` (R7)
- `scripts/image_generation/generate_kdp_all_formats.py` (the older 1024×1024 generator that produced the failing samples)
- `scripts/image_generation/generate_bestseller_covers.py` (the parallel older generator)
- `scripts/release/build_epub.py` (TEACHER_BOOKS dict — title/subtitle source)
- `artifacts/research/manga_cover_design/` (parallel manga research, not consumed in en pipeline today)

---

**End of artifact.**
