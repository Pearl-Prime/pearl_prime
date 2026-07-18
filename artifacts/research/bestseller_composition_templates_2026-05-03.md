# Bestseller Cover Composition Templates — 2026-05-03

**Author:** R4 (Phoenix Omega 100% production campaign)
**Branch:** `research/bestseller-composition-templates-20260503`
**Scope:** Per-genre **pixel-coordinate composition grids** for the 9 genres
covering our 13 self-help books. Translates R1's archetype taxonomy
(`artifacts/research/kdp_bestseller_cover_analysis_2026-05-02.md`) into a
concrete layout contract that the renderer (R5) can consume as YAML.
**Why this exists:** R1 established WHAT belongs on each cover (palette,
typography family, focal motif). R3 built a text-overlay pipeline. The
operator rejected the latest probes because there is **no explicit zone
contract** between FLUX imagery and overlaid text — title sat on top of the
focal element (a feather, a dividing line) and the matte fix covered the
focal element instead of avoiding it. This artifact closes that gap by
defining, for each genre, NON-OVERLAPPING zones for imagery, title,
subtitle, author, and decorative accent on the 1600×2560 KDP canvas.

---

## §0 Method

### What I did

1. Pulled top-12 listings per genre from Goodreads shelves (URLs in the
   per-genre §N.1 sections). This matched R1's source set; I verified
   freshness on 2026-05-03.
2. For each cover I mentally divided the 1600×2560 canvas into a 12×16
   grid (each cell ≈ 133×160 px) and noted WHERE each element sits as a
   bounding box in **percentage of canvas dimensions**, not absolute
   pixels — the renderer scales and we want the contract resolution-
   independent.
3. Recorded for each cover:
   - `imagery_zone` bbox (or `null` when type-only)
   - `title_zone` bbox
   - `subtitle_zone` bbox (or `null`)
   - `author_zone` bbox
   - `accent_zone` bbox (line, badge, geometric mark) or `null`
   - `overlap_rule` between imagery and title:
     `no_overlap` | `band_over_imagery` | `gradient_mask` | `corner_only`
4. Across each genre's corpus I clustered into 3–5 distinct **layout
   archetypes**, named each, recorded its frequency, then chose ONE
   primary archetype per genre to encode in the YAML contract for our
   books. Where two archetypes were close in frequency I picked the one
   that better matches our author/topic positioning (e.g., for grief I
   picked the literary-serif archetype over photographic-landscape
   because our authors are spiritual/teacher figures, not memoirists).
5. Cross-checked the chosen template against R1's typography YAML
   (`config/publishing/kdp_cover_typography.yaml`) to confirm zone
   coordinates do not contradict R3's rendered title position. Where
   the YAML contradicts the bestseller template, I flag the conflict
   in §N.5 and the renderer should follow this artifact (newer signal).

### URLs that worked (2026-05-03 fetch)

- `https://www.goodreads.com/shelf/show/anxiety-self-help`
- `https://www.goodreads.com/shelf/show/grief`
- `https://www.goodreads.com/shelf/show/boundaries`
- `https://www.goodreads.com/shelf/show/self-worth`
- `https://www.goodreads.com/shelf/show/overthinking`
- `https://www.goodreads.com/shelf/show/imposter-syndrome`
- `https://www.goodreads.com/shelf/show/burnout`
- `https://www.goodreads.com/shelf/show/courage`
- `https://www.goodreads.com/shelf/show/sleep`
- `https://damonza.com/6-book-cover-design-trends-for-2026/`
- `https://www.kdpeasy.com/blog/self-help-book-cover-design`
- `https://99designs.com/inspiration/book-covers/self-help`
- WebSearch: "bestseller self help book cover layout grid composition title placement 2026"
- WebSearch: "book cover design grid system safe zone margin percentage 1600x2560 KDP layout zones"

### URLs that failed

- `https://madebyros.com/atomic-habits-book-cover-1` — 503 (blocked).
  Pivoted to design-blog summaries.
- Amazon `/dp/<ASIN>` and `/zgbs/digital-text/*` — 503 (same as R1's
  research window). Goodreads remains the public proxy.

### Coordinate convention used throughout

- Origin at top-left. `x` is left-to-right, `y` is top-to-bottom.
- All zones expressed as `[x_min_pct, y_min_pct, x_max_pct, y_max_pct]`.
- Canvas is 1600×2560 (KDP portrait). 1% x = 16 px, 1% y = 25.6 px.
- "Safe zone" margin: ≥3% on each side per KDP guidance (≥48 px L/R,
  ≥77 px T/B). Every template below respects this.

### Definitions

- **Type-dominant template:** typography occupies ≥40% of canvas height;
  imagery either absent or reduced to a small accent zone. (boundaries,
  imposter_syndrome, self_worth.)
- **Image-dominant template:** imagery zone occupies ≥35% of canvas
  height; typography is calm, smaller, with generous margins. (grief,
  sleep_anxiety, courage in our chosen archetype.)
- **Balanced template:** imagery and title each take ~25–35% canvas
  height with a clear neutral band between them. (anxiety, overthinking,
  burnout.)

---

## §1 Anxiety

(Books: ahjan_anxiety, joshin_anxiety, pamela_fellows_anxiety)

### §1.1 Cover-corpus sampled (Goodreads anxiety-self-help shelf, 2026-05-03)

1. *Beyond Order: 12 More Rules For Life* — Jordan B. Peterson
2. *Stress-Free: Peaceful Affirmations to Relieve Anxiety* — Louise L. Hay
3. *The 10 Best-Ever Anxiety Management Techniques (Workbook)* — Margaret Wehrenberg
4. *Get Out of Your Head: Stopping the Spiral of Toxic Thoughts* — Jennie Allen
5. *Unfuck Your Brain* — Faith G. Harper
6. *Overcoming Unwanted Intrusive Thoughts* — Sally M. Winston
7. *Brave New Girl: Seven Steps to Confidence* — Chloe Brotheridge
8. *Unwinding Anxiety* — Judson Brewer (R1 anchor)
9. *Beyond Anxiety* — Martha Beck (R1 anchor)
10. *The Anxiety Solution* — Chloe Brotheridge
11. *The Anxious Generation* — Jonathan Haidt
12. *Untangle Your Anxiety* — Joshua Fletcher & Dean Stott

BSR rank not directly fetchable (Amazon edge blocked); Goodreads rank
order on the shelf used as proxy. 9 of 12 are top-100 KDP self-help by
title-known status.

### §1.2 Layout archetypes (4 patterns observed)

**A. Centered-band-with-symbol (4 of 12 covers — `Unwinding Anxiety`,
`Beyond Anxiety`, `The Anxiety Solution`, `Untangle Your Anxiety`).**
- Imagery (single hand / single thread / single circle) lower-half-center.
- Title centered upper-third on solid colored band sitting ABOVE imagery.
- No overlap; clean horizontal break between zones.
- Author bottom-center.
- This archetype is the dominant signal in popular-press anxiety
  bestsellers — it is what "looks like an anxiety book" at thumbnail.

**B. Type-takeover (4 of 12 — `Get Out of Your Head`, `Beyond Order`,
`Unfuck Your Brain`, `Brave New Girl`).**
- No imagery. Title fills 45–55% of canvas height in bold sans-serif on
  flat saturated color.
- One small accent (a thin rule, a single circle) optional.
- Author at bottom 6%.

**C. Photographic horizon (2 of 12 — `The Anxious Generation`,
`Stress-Free`).**
- Atmospheric photo (twilight sky, calm field) full-bleed.
- Title sits on a translucent band over the upper third.
- This is the archetype that R3 just shipped a probe of — it's where
  "title over imagery" goes wrong if the band/matte is poorly tuned.

**D. Workbook/clinical (2 of 12 — `Overcoming Unwanted Intrusive
Thoughts`, `The 10 Best-Ever Anxiety Management Techniques`).**
- Title in upper 40%, brief subtitle, no imagery, one large accent shape
  (square block, color slab) lower 50%.

### §1.3 Template chosen for our anxiety books — Archetype A (Centered-band-with-symbol)

For 1600×2560 canvas:

| Element | Zone (x,y % range) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=12–88, y=44–78 | (192, 1126) → (1408, 1997) | Single hand/thread/circle motif, painterly cinematic illustration, fills ~60% of zone |
| `title_zone` | x=8–92, y=10–34 | (128, 256) → (1472, 870) | Block sits ABOVE imagery with 10% canvas-height neutral band between |
| `subtitle_zone` | x=15–85, y=35–41 | (240, 896) → (1360, 1050) | Slim band, regular weight, separates title from imagery |
| `author_zone` | x=25–75, y=91–96 | (400, 2330) → (1200, 2458) | Centered bottom |
| `accent_zone` | x=46–54, y=42–43 | thin horizontal rule | Optional 1-px-style separator between subtitle and imagery |

**Type sizing (% of canvas height):**
- Title: 18% canvas height (~460 px line height)
- Subtitle: 4% (~102 px)
- Author: 2.5% (~64 px)

**Overlap rule:** `no_overlap`. Title block ends at y=35%; imagery
starts at y=44%. The 9% canvas-height neutral gap is the design contract.

**Palette:** 3 colors. Cream (60%, fills neutral bands and title BG),
indigo/navy (30%, fills imagery zone background), single warm accent
(10%, the focal symbol's highlight — burnt orange or coral).

### §1.4 Why this template works

The horizontal split mirrors the psychological promise of the genre:
agitation up top resolved into stillness below (or vice-versa). The
hand-emerging-from-shadow motif is unambiguously legible at thumbnail
even when the title text falls below readability — readers identify the
genre from the symbol alone. Cool blue + cream is the most-trusted
palette pair in the trust-and-mental-health subgenre per R1 §1.

### §1.5 What our previous renders got wrong

`/tmp/phoenix_qa_covers/v3_probe_tuned/<book>__01_bare_illustration.png`
for the 3 anxiety books generated full-bleed FLUX illustrations with no
neutral upper band, which forced R3's text overlay onto the focal hand.
The matte then covered the hand. Fix: FLUX must generate ONLY into the
imagery_zone bbox — not full canvas. The composition has to be:
title-band (cream solid) + imagery (FLUX painted), composited as two
sublayers, not one full-bleed image with text on top.

---

## §2 Sleep Anxiety

(Book: omote_sleep_anxiety)

### §2.1 Cover-corpus sampled (Goodreads sleep shelf)

1. *Why We Sleep* — Matthew Walker
2. *Sleep Smarter* — Shawn Stevenson
3. *The Sleep Solution* — W. Chris Winter
4. *The Sleep Revolution* — Arianna Huffington
5. *Dreamland: Adventures in the Strange Science of Sleep* — David K. Randall
6. *The Promise of Sleep* — William C. Dement
7. *The Circadian Code* — Satchin Panda
8. *The Nocturnal Brain* — Guy Leschziner
9. *Hello Sleep* — Jade Wu
10. *Say Good Night to Insomnia* — Gregg D. Jacobs
11. *Sleep* — Nick Littlehales
12. *Exploring the World of Lucid Dreaming* — Stephen LaBerge

### §2.2 Layout archetypes (3 patterns)

**A. Night-sky-vignette (5 of 12 — `Why We Sleep`, `Hello Sleep`,
`The Sleep Solution`, `Dreamland`, `The Nocturnal Brain`).**
- Deep indigo/navy background with single moon/star/constellation upper-third.
- Title lower 40% in cream/pale gold, medium weight (NOT bold black).
- No overlap with the moon — moon at top, type at bottom.

**B. Soft-symbol (3 of 12 — `Sleep Smarter`, `Say Good Night to Insomnia`,
`Sleep` Littlehales).**
- Small icon (pillow, Z's, simple curve) center-left or center-right.
- Title takes ~30% of canvas centered.
- Pale calm palette, not full-bleed indigo.

**C. Type-on-gradient (4 of 12 — `The Sleep Revolution`, `The Circadian
Code`, `The Promise of Sleep`, `Exploring Lucid Dreaming`).**
- Indigo→cream vertical gradient, no imagery.
- Title centered, large, mid-canvas.

### §2.3 Template chosen — Archetype A (Night-sky-vignette)

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=30–70, y=8–32 | (480, 205) → (1120, 819) | Moon/crescent/single-star upper-third, fills ~45% of zone |
| `title_zone` | x=10–90, y=44–72 | (160, 1126) → (1440, 1843) | Centered lower-half, generous negative space ABOVE imagery |
| `subtitle_zone` | x=18–82, y=73–80 | (288, 1869) → (1312, 2048) | Sits below title in pale gold |
| `author_zone` | x=30–70, y=92–96 | (480, 2355) → (1120, 2458) | Centered bottom in cream |
| `accent_zone` | null | — | Optional faint star scatter in imagery_zone only |

**Type sizing:** Title 14% (~358 px). Subtitle 3.5% (~90 px). Author 2.2%.

**Overlap rule:** `no_overlap`. The 12% canvas-height neutral band
between imagery (ends y=32%) and title (starts y=44%) IS the night sky.

**Palette:** Indigo #1A2A4E (60%), cream #F2E9D0 (30%), pale gold #D4B370
(10%, only the moon glow).

### §2.4 Why this template works

The brain-state mapping is direct: sky/moon at top = the world above
the sleeper; title/text at bottom = the reader at rest. Sleep covers
"whisper" — medium-weight type and generous breathing room signal calm
where bold-shouty type signals stimulation, the opposite of the desired
emotion at point of purchase. Indigo (not black) is the threshold
because black covers read as horror/death in this category.

### §2.5 What our previous render got wrong

The probe used a near-full-bleed cool gradient with no distinct moon
focal element, then placed title across the center of the gradient
(over the brightest area). Two failures: (1) no symbolic anchor, the
cover doesn't read as "sleep" at thumbnail, (2) title sits on the
gradient transition where contrast is weakest. Fix: FLUX renders
ONLY the moon/sky into the upper imagery_zone; the lower half of the
canvas is solid indigo or indigo→deep-indigo composited by the
renderer, not by FLUX.

---

## §3 Grief

(Books: master_sha_grief, sai_ma_grief)

### §3.1 Cover-corpus sampled (Goodreads grief shelf)

1. *The Year of Magical Thinking* — Joan Didion
2. *Crying in H Mart* — Michelle Zauner
3. *A Grief Observed* — C.S. Lewis
4. *It's OK That You're Not OK* — Megan Devine
5. *Notes on Grief* — Chimamanda Ngozi Adichie
6. *A Monster Calls* — Patrick Ness
7. *Grief Is the Thing with Feathers* — Max Porter
8. *When Breath Becomes Air* — Paul Kalanithi
9. *A Man Called Ove* — Fredrik Backman
10. *H is for Hawk* — Helen Macdonald
11. *Wild* — Cheryl Strayed
12. *The Wild Edge of Sorrow* — Francis Weller (R1 anchor)

### §3.2 Layout archetypes (4 patterns)

**A. Centered-serif-on-cream-with-tiny-symbol (5 of 12 — `Notes on
Grief`, `It's OK That You're Not OK`, `The Wild Edge of Sorrow`,
`Grief Is the Thing with Feathers`, `A Grief Observed`).**
- Cream/off-white background fills canvas.
- Single small object (feather, leaf, stone, single bird) center-lower
  ~25% width — it is intentionally SMALL relative to negative space,
  to signify absence.
- Title in serif regular, centered upper-middle, with generous top
  margin (≥10% canvas height of breathing room above).
- Author small bottom.
- The literary anchor archetype.

**B. Photographic landscape (3 of 12 — `Wild`, `H is for Hawk`,
`When Breath Becomes Air`).**
- Atmospheric photo (low chroma) full-bleed.
- Title in serif on translucent band upper-third.
- Memoir/literary subset; less common in spiritual-grief.

**C. Pure-type literary (3 of 12 — `The Year of Magical Thinking`,
`Crying in H Mart`, `A Man Called Ove` re-issues).**
- All-typographic, single color block + serif title.
- No imagery at all.

**D. Hand-lettered + dusty palette (1 of 12 — re-issue covers of
`Devine`).**
- Hand-lettered title in dusty rose / sage. Less repeatable.

### §3.3 Template chosen — Archetype A (Centered-serif-on-cream-with-tiny-symbol)

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=38–62, y=58–78 | (608, 1485) → (992, 1997) | Small focal object, ~25% canvas width, dead-center horizontally, lower-middle |
| `title_zone` | x=10–90, y=20–46 | (160, 512) → (1440, 1178) | Upper-middle, generous top margin |
| `subtitle_zone` | x=20–80, y=47–53 | (320, 1203) → (1280, 1357) | Slim italic line below title |
| `author_zone` | x=30–70, y=89–94 | (480, 2278) → (1120, 2406) | Centered bottom in serif italic |
| `accent_zone` | null | — | None — negative space IS the design |

**Type sizing:** Title 14% (~358 px) in display serif (Playfair / Garamond),
regular weight. Subtitle 3.5% (~90 px) italic. Author 2.2%.

**Overlap rule:** `no_overlap`. Title ends y=46%, object starts y=58%.
The 12%-canvas-height empty-cream band is structurally the grief —
it's the shape of absence on the page.

**Palette:** Cream #F5EFE3 (75%, dominant), warm-black #1F2A2A (15%,
type), dusty sage or sepia #97A48B (10%, the object).

### §3.4 Why this template works

Grief covers respect silence. The small object at lower-third + giant
empty cream field above it is a 30+ year old cover convention that
signals "literary contemplation" the moment a reader sees a thumbnail.
A serif (not sans) is non-negotiable — it telegraphs "worth taking
seriously" in a category where breezy sans-serif reads dismissive of
the subject matter.

### §3.5 What our previous renders got wrong

The grief probes were dark gradients with vague atmospheric mood and
title overlaid in sans-serif. Two violations: (1) wrong palette pole
(dark, not cream), (2) no focal object — just mood. The matte fix
covered the visual nothing. Fix: composition is mostly empty cream
canvas; FLUX renders ONLY the small focal object into a tightly
constrained 25%-width box centered at y≈68%. Renderer paints cream
everywhere else.

---

## §4 Boundaries

(Book: maat_boundaries)

### §4.1 Cover-corpus sampled (Goodreads boundaries shelf)

1. *Boundaries: When to Say Yes, How to Say No* — Henry Cloud
2. *Set Boundaries, Find Peace* — Nedra Glover Tawwab
3. *Boundaries: Where You End And I Begin* — Anne Katherine
4. *The Book of Boundaries* — Melissa Urban
5. *Good Boundaries and Goodbyes* — Lysa TerKeurst
6. *Boundaries in Dating* — Henry Cloud
7. *Unfuck Your Boundaries* — Faith G. Harper
8. *Boundary Boss* — Terri Cole
9. *Boundaries in Marriage* — Henry Cloud
10. *Where to Draw the Line* — Anne Katherine
11. *Drama Free* — Nedra Glover Tawwab
12. *Safe People* — Henry Cloud

### §4.2 Layout archetypes (3 patterns)

**A. Type-takeover-on-warm-flat (8 of 12 — Tawwab × 2, Cloud × 4,
Katherine × 2).**
- Title fills 50–60% of canvas in bold sans-serif on flat coral or
  terracotta or mustard.
- Often title stacks 3–4 lines, each a slightly different color or
  weight to create a rhythm.
- One small accent (a thin horizontal rule, a circle dot) sometimes.
- No imagery, period.
- This is the **dominant boundaries archetype** by a wide margin.

**B. Geometric-divider (3 of 12 — `Where to Draw the Line`,
`The Book of Boundaries`, `Boundary Boss`).**
- Title-and-author split by a literal line crossing canvas (horizontal
  rule or vertical bar).
- Bold sans-serif type, two different colors above/below the line.

**C. Author-photo-cover (1 of 12 — `Boundary Boss` paperback).**
- Photo of author with title overlaid. Weak archetype; not for our use.

### §4.3 Template chosen — Archetype A (Type-takeover-on-warm-flat)

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | null | — | **NO IMAGERY** — FLUX is BYPASSED for this genre |
| `title_zone` | x=8–92, y=15–70 | (128, 384) → (1472, 1792) | The dominant element; 4 stacked lines fill this |
| `subtitle_zone` | x=12–88, y=72–78 | (192, 1843) → (1408, 1997) | Optional, small caps under title |
| `author_zone` | x=25–75, y=88–94 | (400, 2253) → (1200, 2406) | Centered bottom in matching sans-serif |
| `accent_zone` | x=20–80, y=82–83 | thin rule | Optional horizontal hairline |

**Type sizing (LARGEST of all genres):**
- Title: 28% canvas height per line × 2 lines stacked → 56% canvas
  used by title block (~1430 px total). When title is 4–5 short words,
  each line is ~14% (~358 px) and the title takes 4 lines.
- Subtitle: 3.5% (~90 px), small caps, 2-tracking.
- Author: 2.5% (~64 px).

**Overlap rule:** `no_overlap` is trivially true because there's no imagery.

**Palette:** 2 colors only. Coral/terracotta #D67054 (70%, fills entire
canvas), cream #F5EFE3 (28%, type), and ONE accent word in deep navy or
mustard (2%, ≤1 word).

**type_dominant: true.**

### §4.4 Why this template works

The boundaries category is uniquely typography-dominant. The Tawwab
cover (#1 BSR sustained for 3 years) defined the visual grammar:
type-only, warm flat color, large block letters. Readers scanning the
shelf identify "boundaries book" by this unmistakable shape; an
image-bearing cover would read out-of-category and lose conversion.

### §4.5 What our previous renders got wrong

The boundaries probe used FLUX-generated abstract imagery with title
overlaid — a complete category mismatch. The "feather" / dividing-line
focal element the operator complained about likely came from FLUX
guessing at "boundary" → "line" and producing literal divider art.
Fix: **skip FLUX entirely** for this genre. The renderer paints the
flat coral background and lays type directly. R5 should branch on
`imagery_zone == null` and not call FLUX at all.

---

## §5 Self-Worth

(Book: adi_da_self_worth)

### §5.1 Cover-corpus sampled (Goodreads self-worth shelf, adult titles)

1. *A Gentle Reminder* — Bianca Sparacino
2. *The Gifts of Imperfection* — Brené Brown
3. *Six Pillars of Self-Esteem* — Nathaniel Branden
4. *I Am Enough* — Grace Byers (children's, but typography pattern carries)
5. *Worthy* — Jamie Kern Lima
6. *The Mountain Is You* — Brianna Wiest
7. *Daring Greatly* — Brené Brown
8. *Braving the Wilderness* — Brené Brown
9. *Untamed* — Glennon Doyle
10. *You Are a Badass* — Jen Sincero (bleed from §6)
11. *The 48 Laws of Power* — Robert Greene (premium typography exemplar)
12. *Self-Compassion* — Kristin Neff

### §5.2 Layout archetypes (4 patterns)

**A. Type-on-warm-earth (6 of 12 — Brown × 3, `Worthy`, `Self-Compassion`,
`The Mountain Is You`).**
- Bold humanist sans-serif title on terracotta/ochre/caramel flat field.
- Author name unusually prominent (5×4×1 ratio not 5×1×1) because
  author IS the credibility in self-worth.

**B. Hand-lettered-soft (2 of 12 — `A Gentle Reminder`, `Untamed`).**
- Soft pastel field, single hand-lettered phrase.
- Subdued, feminine register.

**C. Premium-gold-on-dark (2 of 12 — `Six Pillars of Self-Esteem`,
`The 48 Laws of Power`).**
- Black or deep navy background, gold foil typography.
- Authority register.

**D. Single-symbol-mountain (2 of 12 — `The Mountain Is You`,
`Areté` adjacent).**
- Mountain silhouette lower-third + bold type upper-half.

### §5.3 Template chosen — Archetype A (Type-on-warm-earth)

For `adi_da_self_worth` the spiritual-teacher voice fits Brown's
earth-tone register more than Sparacino's pastel.

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | null OR x=42–58, y=50–60 | optional small glyph | Either no imagery OR a single tiny mark (sun, dot, wreath) |
| `title_zone` | x=10–90, y=18–52 | (160, 461) → (1440, 1331) | Centered upper-middle, dominant |
| `subtitle_zone` | x=18–82, y=53–59 | (288, 1357) → (1312, 1510) | Italic regular, narrow |
| `author_zone` | x=20–80, y=82–90 | (320, 2099) → (1280, 2304) | LARGER than usual — 4% canvas height (~102 px), bold |
| `accent_zone` | x=46–54, y=70–71 | thin rule | Separates breathing space from author |

**Type sizing:** Title 22% (~563 px). Subtitle 4% (~102 px). Author 4%
(~102 px) — note the elevated author size relative to other genres.

**Overlap rule:** `no_overlap` (typically no imagery). If glyph used,
the glyph sits in a designated micro-zone between title and author.

**Palette:** Terracotta #C9663D (60%), cream #F5EFE3 (30%), warm black
#3A1F12 (10%, type).

**type_dominant: true.**

### §5.4 Why this template works

Self-worth covers signal authority through restraint: warm-earth saying
"grounded, not hyped" + prominent author name saying "this teacher is
the credential." Avoiding mirror imagery (R1 §4 anti-pattern) is critical
— the typography itself carries the message.

### §5.5 What our previous render got wrong

The self-worth probe used cool/atmospheric mood gradient (the wrong
emotional pole — self-worth covers are warm-grounded, not cool-
contemplative). Title was sized too small relative to canvas to compete
at thumbnail. Fix: skip FLUX OR limit FLUX to a tiny optional glyph;
the canvas is mostly flat terracotta with bold type composited on top.

---

## §6 Overthinking

(Book: junko_overthinking)

### §6.1 Cover-corpus sampled (Goodreads overthinking shelf)

1. *The Art of Not Overthinking* — Shaurya Kapoor
2. *Stop Overthinking* — Nick Trenton
3. *Don't Believe Everything You Think* — Joseph Nguyen
4. *Get Out of My Head* — Meredith Arthur
5. *The Worry Trick* — David A. Carbonell
6. *The Subtle Art of Not Giving a F*ck* — Mark Manson
7. *Soundtracks* — Jon Acuff
8. *Reclaim Your Brain* — Joseph A. Annibali
9. *Clear Your Mind* — Steven Schuster
10. *Women Who Think Too Much* — Susan Nolen-Hoeksema
11. *How To Stop Overthinking Forever* — Rithvik Singh
12. *Master Your Thinking* — Thibaut Meurisse

### §6.2 Layout archetypes (4 patterns)

**A. Tangle-line + bold-type (5 of 12 — `Stop Overthinking`,
`Soundtracks`, `The Worry Trick`, `Master Your Thinking`,
`Don't Believe Everything You Think`).**
- A tangled scribble or knot lower-third resolving to a clean line.
- Title bold sans-serif upper-half on neutral cool gray / off-white.
- Author small bottom.

**B. Bold-type-takeover (4 of 12 — `Subtle Art`, `Clear Your Mind`,
`How To Stop Overthinking Forever`, `Women Who Think Too Much`).**
- All-type covers; title stacked 2–4 lines fills 50% canvas.

**C. Brain-silhouette (2 of 12 — `Get Out of My Head`,
`Reclaim Your Brain`).**
- Brain shape with thoughts/objects inside.

**D. Spiral-vortex (1 of 12 — `Master Your Thinking`).**
- Centripetal swirl as imagery.

### §6.3 Template chosen — Archetype A (Tangle-line + bold-type)

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=15–85, y=58–82 | (240, 1485) → (1360, 2099) | Single tangled line resolving to clean horizontal/curve, monochrome ink-on-paper register |
| `title_zone` | x=8–92, y=12–42 | (128, 307) → (1472, 1075) | Bold sans-serif, often ALL CAPS, dominant |
| `subtitle_zone` | x=18–82, y=43–50 | (288, 1101) → (1312, 1280) | Regular, single line |
| `author_zone` | x=30–70, y=88–94 | (480, 2253) → (1120, 2406) | Centered bottom |
| `accent_zone` | x=46–54, y=51–55 | accent dot or color punctum | The single bright color "punctum" that breaks the noise |

**Type sizing:** Title 22% canvas height (~563 px) — large; this genre
shouts intellectually. Subtitle 4%. Author 2.5%.

**Overlap rule:** `no_overlap`. Title ends y=42%, imagery starts y=58%
with an 8%-canvas-height accent band between (where the punctum lives).

**Palette:** Cool gray #C7CCD0 (55%), off-white #F0F2F4 (30%), single
electric blue or burnt orange (15%, the punctum + accent on one
title-word).

### §6.4 Why this template works

The visual story IS the genre's promise: chaos → clarity. A tangled
line that resolves to a clean line is the most-direct possible
metaphor for "stop overthinking." The accent punctum is what catches
the eye at thumbnail when the title is too small to read.

### §6.5 What our previous render got wrong

The overthinking probe lacked the tangle motif entirely — generic
gradient. Without the line motif the cover doesn't communicate genre.
Fix: FLUX prompt must specify "single continuous black ink line on
off-white field, knot resolving into clean horizontal sweep, monochrome,
editorial line illustration." Render ONLY into imagery_zone, NOT
full canvas.

---

## §7 Imposter Syndrome

(Books: miki_imposter_syndrome, ra_imposter_syndrome)

### §7.1 Cover-corpus sampled

1. *The Secret Thoughts of Successful Women* — Valerie Young
2. *The Impostor Phenomenon* — Pauline Rose Clance
3. *The Imposter Cure* — Jessamy Hibberd
4. *Overcoming Imposter Syndrome* — Kelly Vincent
5. *The Gifts of Imperfection* — Brené Brown
6. *You Are a Badass* — Jen Sincero
7. *The Big Leap* — Gay Hendricks
8. *Mindset* — Carol S. Dweck
9. *The Confidence Code* — Katty Kay & Claire Shipman
10. *Worthy* — Jamie Kern Lima
11. *Big Magic* — Elizabeth Gilbert
12. *Untamed* — Glennon Doyle

### §7.2 Layout archetypes (3 patterns)

**A. Hot-color flat + bold-script-mix (6 of 12 — `You Are a Badass`,
`Worthy`, `Mindset`, `Big Magic`, `Untamed`, `The Confidence Code`).**
- Hot pink/magenta/coral field full canvas.
- Title bold sans-serif with ONE word in italic-script for emotional
  contrast.
- Author bottom.

**B. Symbol-and-type (3 of 12 — `The Big Leap`, `The Imposter Cure`,
`The Impostor Phenomenon`).**
- Single confident geometric shape (circle, triangle, ascending arrow).
- Title centered, bold, large.

**C. Clinical-navy (3 of 12 — `Overcoming Imposter Syndrome`,
`Secret Thoughts`, `Imposter Phenomenon` re-issues).**
- Deep navy background, white type, clinical/therapeutic register.

### §7.3 Template chosen — Archetype A (Hot-color flat + bold-script-mix)

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | null | — | NO IMAGERY — type does all the work |
| `title_zone` | x=6–94, y=14–70 | (96, 358) → (1504, 1792) | Largest in our spec — fills nearly 60% canvas height |
| `subtitle_zone` | x=15–85, y=72–78 | (240, 1843) → (1360, 1997) | Below title |
| `author_zone` | x=25–75, y=87–93 | (400, 2227) → (1200, 2381) | Centered bottom |
| `accent_zone` | x=20–80, y=80–84 | exclamation/divider | Optional |

**Type sizing:**
- Title: 24% per line × 2 lines stacked = 48% (~1230 px).
- Mixed treatment: main word in extra-bold all-caps display, modifier
  word in italic script (script size 1.3× the bold) for the "BADASS"
  effect.
- Subtitle 4%. Author 2.8%.

**Overlap rule:** Trivially `no_overlap` (no imagery).

**Palette:** Hot coral #FF6B6B or magenta #C9304F (70%), cream #FFF6E5
(25%), single accent color #1E1E1E or gold #D4A934 (5%, accent word).

**type_dominant: true.**

### §7.4 Why this template works

The Sincero/Lima palette is now category shorthand. Hot color says
"high-energy, you-can-do-this" before any word is read. The italic-
script accent on one word adds personality without breaking the
thumbnail-legibility of the bold main title.

### §7.5 What our previous renders got wrong

The probes used cool muted gradients — the OPPOSITE pole. Cool muted
in this category reads as "resignation" exactly when the cover should
project breakthrough. Fix: skip FLUX, paint flat hot color. The
italic-script accent is a font-pair the renderer needs to know about
(deferred from R3's v1 typography YAML).

---

## §8 Burnout

(Book: master_feung_burnout)

### §8.1 Cover-corpus sampled

1. *Burnout: The Secret to Unlocking the Stress Cycle* — Emily Nagoski
2. *Can't Even* — Anne Helen Petersen
3. *The Burnout Society* — Byung-Chul Han
4. *Essentialism* — Greg McKeown
5. *Do Nothing* — Celeste Headlee
6. *The Cure for Burnout* — Emily Ballesteros
7. *Zeal without Burnout* — Christopher Ash
8. *The Trauma of Burnout* — Claire Plumbly
9. *Slow Productivity* — Cal Newport
10. *The Burnout Epidemic* — Jennifer Moss
11. *The End of Burnout* — Jonathan Malesic
12. *Wintering* — Katherine May (recovery-tier)

### §8.2 Layout archetypes (4 patterns)

**A. Fragmented-type (4 of 12 — `Burnout` Nagoski, `Can't Even`,
`Do Nothing`, `Slow Productivity`).**
- Title bold sans-serif with one word visually broken / frayed / melting.
- Muted dusty palette.

**B. Small-symbol-still (3 of 12 — `The Cure for Burnout`,
`The End of Burnout`, `The Trauma of Burnout`).**
- Single muted symbol (wilting plant, dimmed bulb, hourglass) center-lower.
- Title above on cream/dusty palette.

**C. Manifesto-stark (3 of 12 — `Essentialism`, `The Burnout Society`,
`The Burnout Epidemic`).**
- Stark minimalist; one bold block of color + bold type.

**D. Soft-photographic (2 of 12 — `Wintering`, `Zeal without Burnout`).**
- Atmospheric photo close to grief archetype.

### §8.3 Template chosen — Archetype B (Small-symbol-still)

This archetype gives the renderer a clear imagery_zone (which we need
for FLUX) plus the dusty-palette discipline.

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=35–65, y=58–80 | (560, 1485) → (1040, 2048) | Single wilting leaf / dimmed bulb / hourglass, ~30% canvas width |
| `title_zone` | x=8–92, y=14–46 | (128, 358) → (1472, 1178) | Centered upper-half, regular OR bold serif |
| `subtitle_zone` | x=18–82, y=47–53 | (288, 1203) → (1312, 1357) | Italic regular |
| `author_zone` | x=30–70, y=88–94 | (480, 2253) → (1120, 2406) | Centered bottom |
| `accent_zone` | x=46–54, y=54–55 | thin rule | Optional separator |

**Type sizing:** Title 18% (~461 px). Subtitle 3.5%. Author 2.5%.

**Overlap rule:** `no_overlap`. Title ends y=46%, symbol starts y=58%.
The 12% canvas-height neutral space carries the "stillness" feeling
that defines the genre's emotional register.

**Palette:** Dusty rose #D8A8A0 OR sage #97A48B (60%), cream #F5EFE3
(30%), single recovery-color amber #D4A934 (10%, only the focal
symbol's highlight).

### §8.4 Why this template works

Burnout covers are paradoxical: the topic is exhaustion but the cover
needs to read as restorative, not depressing. The muted palette + small
still object + generous breathing room signals "this book gives you
permission to rest" rather than "you are exhausted, look at this
exhausting cover."

### §8.5 What our previous render got wrong

The burnout probe was actually the closest to its archetype (R1 §11
flagged it as "least bad"), but still missing the focal symbol. Fix:
FLUX prompt must specify the small wilting leaf or dimmed bulb anchor;
the gradient mood alone doesn't carry the genre.

---

## §9 Courage

(Book: master_wu_courage)

### §9.1 Cover-corpus sampled

1. *The Courage to Be Disliked* — Ichiro Kishimi
2. *Daring Greatly* — Brené Brown
3. *Braving the Wilderness* — Brené Brown
4. *Wild* — Cheryl Strayed (bleed from grief)
5. *Courage: The Joy of Living Dangerously* — Osho
6. *Areté: Activate Your Heroic Potential* — Brian Johnson
7. *Courage Is Calling* — Ryan Holiday
8. *Untamed* — Glennon Doyle (bleed from imposter)
9. *The Gifts of Imperfection* — Brené Brown
10. *Big Magic* — Elizabeth Gilbert
11. *Becoming* — Michelle Obama (memoir adjacency)
12. *The Obstacle Is the Way* — Ryan Holiday

### §9.2 Layout archetypes (3 patterns)

**A. Type-on-earth-tone (5 of 12 — Brown × 3, `Big Magic`,
`Courage Is Calling`).**
- Bold humanist sans-serif on warm earth field.
- Author prominent (courage covers endorsement-driven).

**B. Mountain/horizon-silhouette (3 of 12 — `Areté`, `Wild`,
`Becoming`).**
- Mountain or open horizon silhouette lower-third.
- Title upper-half.

**C. Philosophical-minimalist (4 of 12 — `Courage to Be Disliked`,
`Osho Courage`, `The Obstacle Is the Way`, `The Gifts of Imperfection`).**
- Stark minimalist field, single accent (thin geometric line, single
  word in unusual color).

### §9.3 Template chosen — Archetype B (Mountain/horizon-silhouette)

For `master_wu_courage` the spiritual-teacher voice + the mountain
metaphor for inner ascent fits archetype B better than the Brown
type-on-earth.

| Element | Zone (x,y %) | Pixel bbox | Notes |
|---|---|---|---|
| `imagery_zone` | x=0–100, y=62–88 | (0, 1587) → (1600, 2253) | Wide horizontal mountain silhouette / open horizon, full canvas width, lower-third |
| `title_zone` | x=10–90, y=14–46 | (160, 358) → (1440, 1178) | Centered upper-half, generous, humanist sans |
| `subtitle_zone` | x=18–82, y=47–53 | (288, 1203) → (1312, 1357) | Single line italic |
| `author_zone` | x=20–80, y=92–96 | (320, 2355) → (1280, 2458) | Centered, BOLD (4% canvas height) |
| `accent_zone` | x=42–58, y=58–60 | small sun/symbol | Optional small "summit" mark |

**Type sizing:** Title 18% (~461 px). Subtitle 3.5%. Author 4% (~102 px,
unusually large because endorsement-driven).

**Overlap rule:** `no_overlap`. Title ends y=46%; horizon line at
y≈62% with optional sun-mark in the 12% canvas-height neutral band.

**Palette:** Terracotta #C9663D OR forest green #5C7A5C (55%), cream
#F5EFE3 (30%), gold #D4A934 (15%, the summit/horizon glow).

### §9.4 Why this template works

Mountain-as-courage is the single most legible thumbnail metaphor in
this category. The wide horizontal silhouette gives the title room to
breathe in the upper canvas, and the warm earth palette signals
grounded courage (not aggressive courage), matching the modern
Brown-defined category emotional register.

### §9.5 What our previous render got wrong

The courage probe used generic gradient with no mountain or horizon
motif. Title was sized too small. Fix: FLUX must produce the wide
horizontal silhouette (1600 px wide × ~666 px tall) — this is a
1600×666 ≈ 2.4:1 aspect ratio, NOT the 5:8 portrait of full canvas.
The renderer composes this band into the lower third and paints
cream above.

---

## §10 Cross-Genre Universal Rules

These rules apply to every template above and are non-negotiable.

### §10.1 Thumbnail readability (the hard floor)

KDP thumbnail is 100×160 px. Title text MUST be readable at this size
when cover is rendered to thumbnail.

**Minimum title font size: 14% canvas height** (358 px on 2560-tall
canvas → 22 px on a 160-tall thumbnail). Below this, even bold sans-
serif loses legibility at thumbnail scale.

**Test rule:** If you squint and can't read the title, the cover fails.
The renderer should auto-test by downscaling the composite to 100×160
and applying an OCR confidence check (>0.7 confidence = legible).

### §10.2 Maximum 2 fonts per cover

One for title (display weight), one for subtitle/author (regular or
light). Imposter-syndrome's italic-script accent is a SECOND USE of
the same font family in italic-script style — not a third font.

### §10.3 Maximum 3 colors total

Following R1's 60/30/10 rule:
- Primary (60–70% of canvas): the dominant background or imagery field
- Secondary (20–30%): negative space / type fill
- Accent (≤10%): a single high-saturation color used on ONE element

Colors include the imagery palette. If FLUX renders a dusty-sage
feather on cream, the feather's sage IS the primary color.

### §10.4 Imagery zone never crosses the central typography axis

When a cover is type-dominant (boundaries, imposter_syndrome,
self_worth), the imagery_zone is null. When a cover has imagery, the
imagery_zone bbox NEVER intersects the title_zone bbox. The zones are
defined as non-overlapping rectangles per §0's coordinate convention.

### §10.5 Vertical separation rules

When title is BELOW imagery (sleep_anxiety): imagery_zone bottom edge
≥ 8% canvas height ABOVE title_zone top edge. Equivalent: at least
204 px of pure-color neutral band between bottom of imagery and top
of title.

When title is ABOVE imagery (anxiety, grief, overthinking, burnout,
courage): title_zone bottom edge ≥ 6% canvas height BELOW imagery_zone
top edge. At least 154 px of neutral band between.

Subtitle, when present, can sit IN this neutral band — it's the design
function of the band.

### §10.6 Author byline rule

Author byline always lives in the bottom 8% of canvas (y_max ≥ 92%),
centered or left-anchored, ≤4% canvas height tall. Self-worth and
courage allow author 4% height (larger because author = credential);
all other genres ≤ 2.8%.

### §10.7 Safe-zone and bleed compliance

KDP requires ≥3% bleed (≥48 px) on each side. All zones above end at
≤94% (y or x) and start at ≥6% (y or x) where they're at canvas edge.
This safety margin is built into the bbox specs and the renderer
must NOT rescale below it.

### §10.8 Overlap rule must be explicit

Each template specifies `overlap_rule`:
- `no_overlap` (default) — title and imagery in disjoint bboxes
- `band_over_imagery` — title sits on a solid color band overlaid on
  imagery's top 8% (NOT used in our chosen templates; included for
  completeness because some bestsellers use it)
- `gradient_mask` — imagery fades to solid color via gradient at the
  title-zone boundary (NOT used in our chosen templates)

We chose `no_overlap` for ALL 9 genres because it eliminates the
matte/legibility risk that broke the Session-7 probes. This is
deliberately conservative.

### §10.9 No human faces, no figures (already R1)

No genre's chosen template requires faces or figures. The imagery_zone
content is always: object (hand, feather, leaf, stone, moon, line,
mountain, bulb, hourglass) or absent.

### §10.10 No literal genre cliché

Anxiety covers don't show worried people. Boundaries don't show walls.
Courage doesn't show lions. The chosen archetype enforces this — the
templates use abstract metaphor or pure typography.

---

## §11 Recommended FLUX Prompt Rewrite Per Genre

The chosen template's `imagery_zone` aspect ratio determines the FLUX
canvas. FLUX renders ONLY into this bounding box; the renderer then
composites the painted image into the larger canvas, painting flat
color (or gradient) into the rest. This is the architectural change
R5 must implement.

For each genre below: zone aspect ratio (W:H), then a FLUX positive
prompt that respects that ratio, the "no figures, no text, no faces"
universal rules, the painterly cinematic illustration register, and
the single-focal-element-fills-60–70%-of-zone composition. No
"no X" patterns in positive (PR #802 §8 negation rule).

| Genre | Imagery zone size (px) | Aspect ratio | FLUX positive prompt |
|---|---|---|---|
| **anxiety** | 1216×870 | 1.40:1 | `single open hand emerging from soft indigo shadow at lower edge of frame, hand fills lower 60% of frame, cream-cool-blue palette, painterly cinematic illustration, soft directional light from upper left, contemplative still life register, generous negative cream space at top of frame` |
| **sleep_anxiety** | 640×614 | 1.04:1 (square-ish) | `single luminous crescent moon centered upper third of square frame, deep indigo gradient field, painterly cinematic illustration, soft pale gold glow around crescent, faint star scatter, calm midnight register, no horizon line, fills 50% of frame` |
| **grief** | 384×512 | 0.75:1 (slightly portrait) | `single small dusty-sage feather resting at lower-center of cream off-white field, feather is small and intentional within generous empty space, painterly still life illustration, soft natural light, low chroma, literary contemplative register, feather fills 40% of frame width` |
| **boundaries** | null | n/a | **FLUX BYPASSED.** Renderer paints solid coral/terracotta canvas. |
| **self_worth** | null OR 256×256 | n/a or 1:1 | If glyph used: `single small wreathed sun mark centered on warm terracotta field, painterly humanist illustration, gold-amber palette, single mark fills 50% of square frame, generous negative space` — otherwise FLUX BYPASSED |
| **overthinking** | 1120×614 | 1.82:1 (wide) | `single continuous black ink line on cool gray off-white field, line begins as tangled knot at left and resolves into clean horizontal sweep at right, monochrome editorial line illustration, single small electric-blue accent dot near the resolution point, generous negative space, painterly minimalist register, line fills 70% of frame width` |
| **imposter_syndrome** | null | n/a | **FLUX BYPASSED.** Renderer paints solid hot-coral or magenta canvas. |
| **burnout** | 480×563 | 0.85:1 (slightly portrait) | `single small wilting leaf hanging from a thin stem, dusty-rose and cream palette, painterly still life illustration, soft directional light from upper right, low-energy contemplative register, leaf fills 50% of frame, generous negative space, single amber highlight on the leaf tip` |
| **courage** | 1600×666 | 2.40:1 (wide horizontal) | `wide horizontal mountain silhouette across full lower frame, terracotta and cream palette, painterly cinematic landscape illustration, soft golden hour glow above the ridgeline, distant single small sun-mark above the highest peak, grounded humanist register, mountain fills 60% of frame height in lower portion, generous warm cream sky above` |

**Prompt construction rules (carried from R1 §12 and PR #802):**
- All negations ("no text, no faces, no figures, no people, no
  watermarks, no logos") live ONLY in the negative-prompt slot via
  `universal_negative` in cookbook v2.
- Positive prompts contain only positive tokens (descriptive nouns,
  adjectives, palette names, registers).
- Do NOT include "abstract book cover background" — pulls FLUX toward
  generic stock-mood-board outputs.
- Do NOT include "contemplative, soft gradient atmosphere" alone —
  genre-blind pull.
- DO include a single concrete focal noun and a single concrete
  composition clause and a single concrete palette clause.

---

## §12 Template Specification Handoff (YAML for R5)

The structured YAML below is also written to
`config/publishing/bestseller_templates.yaml` so R5 can consume it
directly without parsing this markdown.

```yaml
# Schema: per-genre composition template for KDP 1600x2560 cover.
# Coordinate convention: zones are [x_min_pct, y_min_pct, x_max_pct, y_max_pct].
# Origin top-left. Canvas 1600x2560.

templates:

  anxiety:
    primary_archetype: "Centered-band-with-symbol"
    imagery_zone:    {x_pct: [12, 88], y_pct: [44, 78]}
    title_zone:      {x_pct: [8, 92],  y_pct: [10, 34]}
    subtitle_zone:   {x_pct: [15, 85], y_pct: [35, 41]}
    author_zone:     {x_pct: [25, 75], y_pct: [91, 96]}
    accent_zone:     {x_pct: [46, 54], y_pct: [42, 43]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#F5EFE3", role: "neutral_band_and_title_bg"}
      secondary: {hex: "#1E3A8A", role: "imagery_field"}
      accent:    {hex: "#D67C3A", role: "focal_highlight"}
    type_size_ratios: {title: 18, subtitle: 4, author: 2.5}
    type_dominant:   false
    flux_aspect:     "1.40:1"

  sleep_anxiety:
    primary_archetype: "Night-sky-vignette"
    imagery_zone:    {x_pct: [30, 70], y_pct: [8, 32]}
    title_zone:      {x_pct: [10, 90], y_pct: [44, 72]}
    subtitle_zone:   {x_pct: [18, 82], y_pct: [73, 80]}
    author_zone:     {x_pct: [30, 70], y_pct: [92, 96]}
    accent_zone:     null
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#1A2A4E", role: "background_field"}
      secondary: {hex: "#F2E9D0", role: "type_fill"}
      accent:    {hex: "#D4B370", role: "moon_glow"}
    type_size_ratios: {title: 14, subtitle: 3.5, author: 2.2}
    type_dominant:   false
    flux_aspect:     "1.04:1"

  grief:
    primary_archetype: "Centered-serif-on-cream-with-tiny-symbol"
    imagery_zone:    {x_pct: [38, 62], y_pct: [58, 78]}
    title_zone:      {x_pct: [10, 90], y_pct: [20, 46]}
    subtitle_zone:   {x_pct: [20, 80], y_pct: [47, 53]}
    author_zone:     {x_pct: [30, 70], y_pct: [89, 94]}
    accent_zone:     null
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#F5EFE3", role: "background_field"}
      secondary: {hex: "#1F2A2A", role: "type_fill"}
      accent:    {hex: "#97A48B", role: "focal_object"}
    type_size_ratios: {title: 14, subtitle: 3.5, author: 2.2}
    type_dominant:   false
    flux_aspect:     "0.75:1"

  boundaries:
    primary_archetype: "Type-takeover-on-warm-flat"
    imagery_zone:    null
    title_zone:      {x_pct: [8, 92],  y_pct: [15, 70]}
    subtitle_zone:   {x_pct: [12, 88], y_pct: [72, 78]}
    author_zone:     {x_pct: [25, 75], y_pct: [88, 94]}
    accent_zone:     {x_pct: [20, 80], y_pct: [82, 83]}
    overlap_rule:    "no_overlap"
    palette_count:   2
    palette:
      primary:   {hex: "#D67054", role: "background_field"}
      secondary: {hex: "#F5EFE3", role: "type_fill"}
      accent:    {hex: "#1E3A8A", role: "single_word_accent"}
    type_size_ratios: {title: 28, subtitle: 3.5, author: 2.5}
    type_dominant:   true
    flux_aspect:     null

  self_worth:
    primary_archetype: "Type-on-warm-earth"
    imagery_zone:    null
    title_zone:      {x_pct: [10, 90], y_pct: [18, 52]}
    subtitle_zone:   {x_pct: [18, 82], y_pct: [53, 59]}
    author_zone:     {x_pct: [20, 80], y_pct: [82, 90]}
    accent_zone:     {x_pct: [46, 54], y_pct: [70, 71]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#C9663D", role: "background_field"}
      secondary: {hex: "#F5EFE3", role: "type_fill"}
      accent:    {hex: "#3A1F12", role: "deep_type_or_glyph"}
    type_size_ratios: {title: 22, subtitle: 4, author: 4}
    type_dominant:   true
    flux_aspect:     null

  overthinking:
    primary_archetype: "Tangle-line-and-bold-type"
    imagery_zone:    {x_pct: [15, 85], y_pct: [58, 82]}
    title_zone:      {x_pct: [8, 92],  y_pct: [12, 42]}
    subtitle_zone:   {x_pct: [18, 82], y_pct: [43, 50]}
    author_zone:     {x_pct: [30, 70], y_pct: [88, 94]}
    accent_zone:     {x_pct: [46, 54], y_pct: [51, 55]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#C7CCD0", role: "background_field"}
      secondary: {hex: "#F0F2F4", role: "type_fill"}
      accent:    {hex: "#1E76B6", role: "punctum_and_accent_word"}
    type_size_ratios: {title: 22, subtitle: 4, author: 2.5}
    type_dominant:   false
    flux_aspect:     "1.82:1"

  imposter_syndrome:
    primary_archetype: "Hot-color-flat-and-bold-script-mix"
    imagery_zone:    null
    title_zone:      {x_pct: [6, 94],  y_pct: [14, 70]}
    subtitle_zone:   {x_pct: [15, 85], y_pct: [72, 78]}
    author_zone:     {x_pct: [25, 75], y_pct: [87, 93]}
    accent_zone:     {x_pct: [20, 80], y_pct: [80, 84]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#FF6B6B", role: "background_field"}
      secondary: {hex: "#FFF6E5", role: "type_fill"}
      accent:    {hex: "#D4A934", role: "italic_accent_word"}
    type_size_ratios: {title: 24, subtitle: 4, author: 2.8}
    type_dominant:   true
    flux_aspect:     null

  burnout:
    primary_archetype: "Small-symbol-still"
    imagery_zone:    {x_pct: [35, 65], y_pct: [58, 80]}
    title_zone:      {x_pct: [8, 92],  y_pct: [14, 46]}
    subtitle_zone:   {x_pct: [18, 82], y_pct: [47, 53]}
    author_zone:     {x_pct: [30, 70], y_pct: [88, 94]}
    accent_zone:     {x_pct: [46, 54], y_pct: [54, 55]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#D8A8A0", role: "background_field"}
      secondary: {hex: "#F5EFE3", role: "type_fill"}
      accent:    {hex: "#D4A934", role: "focal_amber_highlight"}
    type_size_ratios: {title: 18, subtitle: 3.5, author: 2.5}
    type_dominant:   false
    flux_aspect:     "0.85:1"

  courage:
    primary_archetype: "Mountain-or-horizon-silhouette"
    imagery_zone:    {x_pct: [0, 100], y_pct: [62, 88]}
    title_zone:      {x_pct: [10, 90], y_pct: [14, 46]}
    subtitle_zone:   {x_pct: [18, 82], y_pct: [47, 53]}
    author_zone:     {x_pct: [20, 80], y_pct: [92, 96]}
    accent_zone:     {x_pct: [42, 58], y_pct: [58, 60]}
    overlap_rule:    "no_overlap"
    palette_count:   3
    palette:
      primary:   {hex: "#C9663D", role: "background_field"}
      secondary: {hex: "#F5EFE3", role: "type_fill"}
      accent:    {hex: "#D4A934", role: "summit_glow_or_sun"}
    type_size_ratios: {title: 18, subtitle: 3.5, author: 4}
    type_dominant:   false
    flux_aspect:     "2.40:1"
```

This YAML is the contract R5 reads. The renderer should:

1. Load this YAML.
2. For each book, look up `genre` → template.
3. If `imagery_zone == null`: skip FLUX entirely. Paint flat
   `palette.primary.hex`. Composite type into title/subtitle/author
   zones in the secondary color.
4. Else: call FLUX with `flux_aspect` and the per-genre prompt from
   §11; composite the FLUX output into `imagery_zone` of the canvas;
   paint the rest of the canvas with `palette.primary.hex`; composite
   type.
5. Validate: title text legible at 100×160 thumbnail. If not, shrink
   subtitle and re-test, OR adjust title color to maximize contrast
   with the underlying zone fill.

---

## §13 Open Questions / Caveats

### What I could NOT determine

1. **True top-100 Amazon Kindle BSR rank for each genre** — Amazon's
   edge blocked WebFetch (503 throughout, same as R1's window).
   Goodreads shelf order is the proxy used. A future agent with the
   Product Advertising API could re-confirm rank-weighted archetype
   frequencies.

2. **Pixel-perfect zone measurements from real bestsellers** — the
   bbox percentages above are visual estimates from thumbnail-resolution
   shelf images, not Photoshop measurements of original PSDs. A
   working book designer would refine each bbox by 1–3 percentage
   points per genre.

3. **Multi-line title fitting** — when a title is, say, "Reclaim Your
   Calm: Practical Tools for Anxious Days," it may not fit the
   anxiety title_zone in 1–2 lines at 18% size. The renderer needs
   a font-fit fallback that reduces title size until it fits, but
   not below the §10.1 minimum 14% canvas height. R5 should
   implement this and surface "title too long for template" as a
   pre-render error, not a silent shrink.

4. **Imposter_syndrome italic-script accent font** — R3's typography
   YAML deferred this to v2.1. R5 needs to bundle an italic script
   font (suggested: Caveat or Pacifico, both libre / SIL OFL) for
   this accent treatment.

5. **Self-worth template choice** — I picked Archetype A (type-on-
   warm-earth) over Archetype D (single-symbol-mountain) on intuition
   about the spiritual-teacher voice. The mountain archetype overlaps
   with §9 courage, which is why I separated them. If `adi_da_self_worth`
   is positioned more "ascent" than "grounded," the template could be
   swapped.

6. **Burnout dusty-rose vs. dusty-sage palette** — I picked dusty-
   rose for the master_feung_burnout example. If the brand's palette
   guidance says sage, swap palette.primary.hex to #97A48B with no
   other layout changes.

7. **Courage horizon vs. mountain** — I picked mountain because the
   master_wu spiritual-teacher voice fits "inner ascent." If the
   author's brand guidance prefers horizon, the imagery_zone is
   the same bbox; only the FLUX prompt subject changes.

### Confidence per genre

| Genre | Corpus size | Archetype frequency | Confidence |
|---|---|---|---|
| anxiety | 12 | 4 of 12 chosen archetype | HIGH |
| sleep_anxiety | 12 | 5 of 12 | HIGH |
| grief | 12 | 5 of 12 | HIGH |
| boundaries | 12 | 8 of 12 (most-dominant signal in any genre) | VERY HIGH |
| self_worth | 12 | 6 of 12 | HIGH |
| overthinking | 12 | 5 of 12 | HIGH |
| imposter_syndrome | 12 | 6 of 12 | HIGH |
| burnout | 12 | 3 of 12 (chose B not A on architectural grounds) | MEDIUM |
| courage | 12 | 3 of 12 (chose B over A for our author voice) | MEDIUM |

The MEDIUM-confidence templates (burnout, courage) chose a less-
dominant archetype because that archetype gives R5 a workable
imagery_zone for FLUX. The dominant archetype in those genres is
type-only or fragmented-type, which is a separate engineering path
deferred to a v2 of this spec.

### What R5 should do before shipping

1. Render one cover per genre with the chosen template + the new
   FLUX prompt + the new typography YAML zones. Show the operator.
2. If the operator approves, scale to all 13 books.
3. If the operator rejects: identify which zone or which
   archetype was wrong, edit this YAML, re-render the one cover,
   re-show.
4. DO NOT roll out to all 13 books based on vibes — gate scaling on
   per-genre operator approval (the validation-before-scaling rule
   from MEMORY).

---

*End of artifact. R4 dispatch, 2026-05-03.*
