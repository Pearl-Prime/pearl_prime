# Cover Quality & Differentiation Framework — 2026-05-03

**Author:** R6 (Phoenix Omega 100% production campaign)
**Branch:** `research/cover-quality-and-differentiation-framework-20260503`
**Scope:** Why every cover round so far has shipped covers that read as "AI clip
art" or "pointless abstraction," and the four-layer identity system the
renderer needs to deliver bestseller-grade output that ALSO differentiates
across brand / author / series / individual book.
**Companion artifact:** `config/publishing/cover_identity_system.yaml` (the §9
machine-readable contract — R7 will consume this).

---

## Operator's actual frustration (read this first, in their words, paraphrased)

> "When we try pictures, we get clip-art-looking things. When abstract,
> sizing/strength is off, no point. Every cover can't have the same template
> or feeling. Every author has to have their own vibe. There's gotta be lots
> of differentiation. We need to research what makes a good book cover."

Five rounds have failed because R1–R5 stopped at PER-GENRE archetypes. Per-genre
gives every anxiety book the same hand-from-darkness, every grief book the
same feather. Same brand, same author, same vibe, every time. The 800-book
catalog will look like one giant template fill.

The four missing layers are: **what makes a cover good in absolute terms**
(§0), **brand identity** (§1), **author identity** (§2), **series identity**
(§3), **individual book identity** (§4). This artifact builds all five.

---

## §0 What "good cover" actually means — the objective craft criteria

R1 covered palette, composition archetype, and typography family. Those are
necessary but not sufficient. Five additional criteria separate professional
bestsellers from amateur / AI-generated covers. Each is testable.

### §0.1 Focal clarity at thumbnail

**Definition.** When the cover is shrunk to 100×160 px (the size on Amazon
search results, on a phone, in a Goodreads grid), exactly ONE element is
unambiguously dominant — your eye lands there in under a second, no
hesitation. Sources: Reedsy "How to Design a Book Cover," kdpeasy 2025
"Common Book Cover Design Mistakes," Creative Paramita "Book Cover Thumbnail
That Survives the Amazon Test."

**The professional rule.** A bestseller cover is a logo, not an
illustration. The simpler at thumbnail, the stronger.

**Examples.** *Atomic Habits* — title is the cover; thumbnail = a yellow
rectangle with two bold words. *The Body Keeps the Score* — single black
title on cream, abstract figure mark; thumbnail still parses as "title +
mark." *Untamed* (Doyle) — single hand-lettered title; thumbnail = title.
What works: ≥40% of canvas occupied by ONE element, no second element
competing for attention.

**Why our covers fail this.** Round 1 / Round 4 image-bearing covers had a
focal object (hand, feather, horizon line) that dissolves into atmospheric
goo when shrunk. The eye lands nowhere. The matte panel introduced in Round
3 then COMPETES with the focal object — two attention zones, neither wins.

**Test.** Render the cover at 100×160. If a non-designer can name the genre
and identify the title in ≤2 seconds, it passes. If not, simplify.

### §0.2 Emotional one-word read

**Definition.** A reader passing the thumbnail can name ONE word that
describes the emotional register before they read the title. "Calm." "Fierce."
"Tender." "Edgy." "Ancient." "Awake."

**The professional rule.** A cover is a signal, not a summary.
Bestseller covers commit hard to one emotional register — they refuse to
hedge. AI-generated covers hedge by trying to suggest the whole book; that
produces emotional muddle.

**How bestsellers do it.** *Tiny Beautiful Things* (Strayed): the word is
"tender" — soft pink, hand-lettered, off-center. *The Anxious Generation*
(Haidt): the word is "alarmed" — black + electric red, sans-serif slab.
*The Power of Now* (Tolle, Hay House cover): the word is "still" — single
photographic flower head, generous negative space.

**Our failure mode.** Generic "atmospheric" prompts (the Round 5 abstract
pivot) produced covers whose one-word read is "vague" or "soft" — both are
non-words for a reader picking a book. "Soft" is not an emotion; "tender"
is. Specificity at the emotional register level is what bestsellers commit
to.

### §0.3 Production tells — what cues say "art-directed"

**Definition.** Specific micro-craft signals a reader's eye reads
unconsciously as "this had a real designer." Reedsy's 2026 cover guide and
Damonza's 2026 trends both emphasize that professional polish reads at the
detail level, not the concept level.

The eight production tells:

1. **Hand-lettered or bespoke title type.** Not a font picked from a list.
   Title type is custom-tweaked: kerning fixed character-by-character,
   weight punched on key letters, ligatures inserted. Riverhead and Knopf
   are famous for this.
2. **Single conceptual image.** Not a composite. Not a collage. ONE thing,
   chosen for symbolic compression. The Riverhead house style explicitly
   refuses composite imagery.
3. **Color discipline at exactly 2–3 colors.** Including the "off-white,"
   the title color, and one accent. More than 3 reads as amateur. Fewer
   than 2 reads as flat.
4. **Atmospheric depth-of-field on the focal element.** When imagery is
   used, the focal element has crisp edge sharpness while everything else
   softens. AI generators struggle with this and produce uniform
   sharpness, which reads as "sticker on flat."
5. **Shadow consistency.** Light direction is honored across the whole
   cover. AI generators often place a focal object whose shadow direction
   contradicts the background light source. Readers don't articulate this
   but their eye flags it as wrong.
6. **Off-white or warm white, never pure #FFFFFF.** Pro covers use
   #F8F4EC, #FAF1DD, #ECE6D8 — paper-warm whites. Pure white reads as
   PowerPoint. The 2025 Lit Hub "best book covers" roundup is dominated
   by warm-white, not pure white.
7. **Type sits ON the design, not OVER it.** Title placement uses an
   intentional negative-space zone the imagery LEAVES OPEN, not a matte
   panel pasted over imagery. R3's matte was a tell because it betrayed
   that the imagery and type were generated separately.
8. **Author byline is small and confident.** Bestselling-author covers
   often size the author NAME bigger than the title, but that's only
   when the author IS the brand (King, Doyle, Brown). For our books
   author is small bottom-third and SETS in the same family as title.

### §0.4 The "AI-generated" tell

**Definition.** Visual signals that read as "this was made by a generator,
not a designer." Sources: Damonza 2025 indie-author AI-cover guide,
Creativindie's MidJourney critique, Steve Fenton's "warning signs of an
AI-generated book."

The seven tells our covers have shown:

1. **Atmospheric goo in the imagery zone.** Soft gradients, vague mist,
   unresolved shapes that try to suggest a mood without committing to
   any specific element. This is the "abstract pivot" failure mode from
   Round 5.
2. **Pseudo-photorealism that's almost-but-not-quite a real photo.**
   Schnell at 4 steps produces this consistently — an image that looks
   like a photograph until you look at the edges, where surfaces dissolve
   into AI smudge. flux1-dev at 28 steps largely fixes this, schnell does
   not.
3. **Generic register.** "A serene landscape." "A minimalist composition."
   "A symbolic representation of healing." Prompts at this register pull
   from the median of training data and produce median output —
   competent, generic, forgettable. Not a bestseller.
4. **Focal vagueness.** The cover has imagery but the eye can't decide
   where to land. Two AI-generated rocks, two hands, one mountain plus
   one bird — anything competing for attention.
5. **Composite-without-light-discipline.** Title pasted over imagery
   from a different light source. Matte panels covering the focal
   element they were supposed to clear space for.
6. **Faux-handwritten fonts.** Generators love these because they look
   "warm." They almost always read amateur in the self-help category.
   Bestsellers either use a real serif/sans or a TRUE hand-lettered
   custom title — never a "handwriting" font from Google Fonts.
7. **The schnell smudge.** Specific to our pipeline: 4-step diffusion
   produces a characteristic loss of edge resolution that no prompt
   sophistication can fix. flux1-dev at 28 steps is the floor for
   bestseller-grade output. See §7.

### §0.5 Color discipline — exactly 2–3 colors, including off-white

**Definition.** A bestseller self-help cover uses NO MORE than three
colors total. Per kdpeasy 2026: "Never use more than 3 colors on a self-help
cover — it breaks the minimalist principle that makes this genre's covers
effective." Minimalist covers in this genre outsell busy ones by a
substantial margin (Reedsy / kdpeasy both cite roughly 60%+).

**The 60-30-10 rule (industry standard, repeated across kdpeasy / Reedsy /
Damonza).** Primary occupies 60–70% of canvas (usually the brand body
color). Secondary fills 20–30% (the off-white or paper). Accent is exactly
10% (the signal color — title pop, badge, accent rule).

**Where our covers break this.** Our prompts have not enforced a hard color
budget at the prompt or post-processing level. FLUX returns 5–7 colors
because nothing in the prompt or pipeline tells it not to. The renderer
should enforce a 3-color quantization step before final composition.

### §0.6 Type integration, not type-pasting

**Definition.** Bestseller covers reserve a pre-planned negative-space
zone for type and the imagery is generated INTO that zone reservation. The
type then sits on a clean field, no matte needed.

R4 introduced explicit zone bboxes; that was the right move. The remaining
gap is that the prompt does not tell FLUX "leave the upper third clean
sky." So FLUX fills the zone with cloud detail and we panic-matte it back.
The fix is to make the FLUX prompt aspect-ratio-correct AND to encode the
negative-space reservation in the positive prompt as ATMOSPHERIC
REGISTER, not as "no X."

**Example positive-prompt token that works for an upper-zone reservation:**
`"low horizon line at 70% of frame, vast empty sky above, calm uncluttered
gradient,"` — this LEAVES the upper zone empty without saying "no clouds."

### §0.7 The thumbnail test (mandatory)

**Definition.** Before any cover ships, render at 100×160 px and verify:
(a) title legible, (b) one obvious focal element, (c) emotional register
parseable, (d) ≤3 colors visible, (e) no AI-tells (atmospheric goo,
pseudo-photo edges, conflicting shadows). Failed thumbnails do not ship.

Bestselling self-help covers (Atomic Habits, Body Keeps the Score, Untamed,
Tiny Beautiful Things, The Power of Now, Untangle Your Anxiety, Get Out
of Your Head, Quiet, Boundaries) all pass the thumbnail test trivially.
Our Round 1–5 covers have failed it consistently.

---

## §1 Brand visual identity layer (13 brands)

We have 13 publisher brands in `scripts/release/build_epub.py:TEACHER_BOOKS`,
not the "12 brands" the original brief stated. Each brand has exactly one
author at present; the 800-book future-state has multiple authors per brand.
This section defines each brand's house style by mapping it to a real
publisher whose visual signature is well-documented and matches the brand's
positioning.

**Critical rule:** brands must look DIFFERENT from each other. Two of our
brands cannot both be "atmospheric and contemplative" — that's how Round
1–5 collapsed. Each brand picks ONE inspiration publisher and commits.

### §1.1 Method: how I assigned inspirations

For each brand I read its current `topic` and `lang` from TEACHER_BOOKS, then
mapped its emotional register to a real-publisher house style with a known
visual signature. I picked publishers documented across multiple design
sources (Reedsy, Lit Hub's "best book covers of the decade," PRH's Riverhead
Design Labs feature, the Borzoi/Knopf design archive at UT Austin, Shambhala
public catalog). Where two real publishers fit, I picked the one with the
more distinctive signature, so the brand differentiates harder.

**I did NOT** invent visual signatures. Where I describe a publisher's
signature I describe it from the actual sources cited in this artifact.
Where I extrapolate (e.g., "this register applied to a brand-new fictional
imprint"), I label it as such in §8.

### §1.2 Brand cards

Each card answers: inspiration publisher, palette, motif vocabulary,
typography signature, finish, and the emotional one-word read.

#### Inner Light Press (Ahjan — anxiety / nervous-system)

- **Inspiration:** Sounds True. Atmospheric, contemplative, 80% type / 20%
  imagery on most titles. Sounds True covers commit hard to a single
  photographic or painterly element, often a horizon, dawn, or natural
  threshold.
- **Palette:** `#0E1B33` (deep dusk navy, primary 60–70%), `#FAF1DD`
  (warm cream, secondary 20–30%), `#7AA3C7` (calm sky-blue, accent 10%).
- **Motif pool:** low horizon, dawn light, threshold, single arch, ink-wash
  atmosphere.
- **Typography:** DM Serif Display title in sentence case with generous
  letter-spacing; lowercase author byline in light sans (Inter Light).
- **Finish:** soft matte paper register, slight grain, no gloss.
- **One-word read:** "stillness."

#### Awakening Press (Adi Da — self-worth)

- **Inspiration:** Tarcher (Penguin). Tarcher self-help covers commit to a
  single bold conceptual mark — often a circle, sun, or single iconic
  shape — over a saturated solid color, with serif title in confident
  weight.
- **Palette:** `#3A2E5F` (deep indigo), `#F5EFE3` (parchment), `#E8B765`
  (sunlit gold accent).
- **Motif pool:** sun, single circle, mandorla, ascending line.
- **Typography:** Cormorant Garamond title, all small-caps; author in
  matching serif italic.
- **Finish:** smooth matte with a subtle gold-foil register on accent.
- **One-word read:** "awake."

#### Still Forest (Joshin — Zen anxiety)

- **Inspiration:** Shambhala Publications (Pocket Library line). Spare,
  East-Asian-influenced typography over restrained color, with a single
  ink-wash mark or small calligraphic element.
- **Palette:** `#F8F4EC` (rice-paper warm white), `#1F1F1F` (sumi black),
  `#A23A2A` (vermillion seal accent).
- **Motif pool:** single ink stroke, enso, low pine silhouette, single
  stone, narrow vertical column.
- **Typography:** EB Garamond title in lowercase; vertical author column
  in slim sans (Inter); optional Japanese-style red square seal on accent.
- **Finish:** rice-paper texture, very flat color, no atmospheric haze.
- **One-word read:** "quiet."

#### Zen Clarity (Junko — overthinking)

- **Inspiration:** Penguin Modern Classics minimalist line. Solid-color
  field, single small symbol, generous tracking, exclusively typographic
  hierarchy.
- **Palette:** `#1A4D5C` (deep teal), `#F5F5F0` (paper), `#F2C14E` (mustard
  accent).
- **Motif pool:** single dot, small geometric icon, thin rule, three small
  dots in row, knot motif (overthinking-specific).
- **Typography:** Helvetica Now Display title in sentence case with tight
  tracking; secondary in regular weight.
- **Finish:** flat, slightly satin.
- **One-word read:** "clear."

#### Truth Compass (Ma'at — boundaries)

- **Inspiration:** Riverhead Books. Bespoke hand-set typography that IS
  the cover; restrained two-color plus off-white; single conceptual mark
  if any.
- **Palette:** `#000000` (true black), `#F4ECDC` (warm parchment), `#C9523B`
  (terracotta accent for the "no").
- **Motif pool:** thick rule, single bold square, clean architectural line,
  single bracket, capitalized key word.
- **Typography:** Hand-tweaked Söhne Breit (custom kerning) title; the
  WORD that matters set 30% bigger than rest. Author bottom-third in same
  family, regular weight.
- **Finish:** flat matte; deep ink density on the key word.
- **One-word read:** "firm."

#### Vitality Path (Master Feung — Taoist burnout, zh-CN)

- **Inspiration:** Shambhala Snow Lion / Chinese University Press
  scholarly-but-warm Taoist register: single brushwork mark, warm
  ochre-and-cinnabar palette, slim vertical type column.
- **Palette:** `#7A2E1F` (cinnabar), `#EDD9B2` (aged silk), `#3D5944`
  (deep pine accent).
- **Motif pool:** single bamboo stalk, mountain silhouette, water flow
  line, character seal.
- **Typography:** Source Han Serif (思源宋体) title in vertical column;
  English subtitle in EB Garamond italic; small red seal mark.
- **Finish:** silk-textured paper feel, hand-printed register.
- **One-word read:** "flow."

#### Soul Repair (Master Sha — grief)

- **Inspiration:** Sounds True grief / spiritual-loss register: small
  single object on near-empty cream field, photographic atmospheric
  depth, low-chroma palette.
- **Palette:** `#2A2D3E` (dusk slate), `#F0E9DA` (cream), `#9D8068`
  (warm ash accent).
- **Motif pool:** single feather, single lit candle, distant bird,
  empty chair / threshold, lone leaf.
- **Typography:** Caslon (or near-equivalent) title in sentence case,
  small italic subtitle directly under, author in same family small caps.
- **Finish:** soft photographic depth-of-field on focal object, warm
  matte everywhere else.
- **One-word read:** "tender."

#### Mountain Gate Press (Master Wu — Shaolin courage, zh-TW)

- **Inspiration:** North Atlantic Books / Shambhala martial-arts line:
  bold ink-wash imagery, dark saturated palette, strong vertical
  composition, calligraphic mark.
- **Palette:** `#0F0F12` (forge black), `#D9C9A8` (wheat), `#8E2A1C`
  (battle red).
- **Motif pool:** mountain peak, single training stance silhouette
  (no face), clenched scroll, tiger mark, vertical sword silhouette.
- **Typography:** Adobe Song Std vertical title; English subtitle in
  Inter Bold; small calligraphic 勇 (courage) seal mark.
- **Finish:** sumi ink absorption register, paper grain visible.
- **One-word read:** "fierce."

#### Gen Spark (Miki — imposter syndrome, gen-z register)

- **Inspiration:** Riverhead Design Labs experimental typographic line:
  sliced/cut typography, two saturated colors, no imagery, the type IS the
  cover.
- **Palette:** `#FF5630` (coral red), `#FFF6E5` (off-white), `#1A1A1A`
  (anchor black).
- **Motif pool:** sliced word, doubled word, type-as-shape, type-as-stencil,
  geometric crop.
- **Typography:** GT Sectra Display title, sliced or partially cropped;
  author bottom-third in slim sans Inter.
- **Finish:** flat matte, high-saturation color on coral.
- **One-word read:** "honest."

#### Gentle Wave (Omote — sleep anxiety, somatic)

- **Inspiration:** Sounds True / Storey Publishing somatic-line: soft
  photographic gradient, single small object low in frame, generous
  upper negative space, organic palette.
- **Palette:** `#1B2A3A` (dark room navy), `#E9DFD0` (lamp cream), `#C97C5D`
  (warm clay accent).
- **Motif pool:** single low candle, dim window, single moth, distant
  threshold, slow-river horizon.
- **Typography:** Lora title, lowercase, generous line-height; author
  bottom-third in lowercase Inter Light.
- **Finish:** very low contrast, gentle matte, slight film grain.
- **One-word read:** "soft."

#### Body Wisdom (Pamela Fellows — anxiety, somatic-clinical)

- **Inspiration:** Sounds True clinical-somatic line / Norton popular
  science: single anatomical-structure mark on flat color, confident
  serif title, very few words.
- **Palette:** `#0B3D3D` (deep teal), `#F4EFE6` (clinical cream), `#E2A23B`
  (signal gold accent).
- **Motif pool:** single nerve-tree, single root system, single anatomical
  brain-icon (not photo), single coiled spring, single thread.
- **Typography:** Tiempos Headline title, sentence case; author bottom-third
  in matching serif regular.
- **Finish:** flat matte, slight pencil-line illustration register on
  motif.
- **One-word read:** "grounded."

#### Cosmic Edge (Ra — imposter syndrome, esoteric register)

- **Inspiration:** TarcherPerigee esoteric line: cosmic single circle or
  geometric symbol, deep saturated dark field, gold accent.
- **Palette:** `#0A0E2C` (deep cosmos), `#F4E6BA` (parchment), `#E0B341`
  (gold accent).
- **Motif pool:** single solar disc, single mandala, single eye-as-shape
  (no face), single arc, single triangle of light.
- **Typography:** Trajan Pro title in all caps; author bottom-third in
  matching small caps; optional gold-foil register on title.
- **Finish:** matte deep field with gold-foil accent register.
- **One-word read:** "ancient."

#### Healing Ground Press (Sai Maa — grief)

- **Inspiration:** Hay House (the Louise Hay / Wayne Dyer warm-hopeful
  register): warm palette, single illuminated organic motif (often
  natural light through leaves / flower / hand), inviting serif title.
- **Palette:** `#3F2E2A` (warm earth), `#F5E9D6` (golden cream), `#D89A6E`
  (warm peach accent).
- **Motif pool:** single sun-through-tree, single flower, single warm
  hand-light (no face), single open window, single warm threshold.
- **Typography:** Cormorant Garamond title, italic subtitle, lowercase
  author byline.
- **Finish:** warm photographic light, soft matte, gentle vignette.
- **One-word read:** "warm."

### §1.3 Why this differentiates

If you put 13 thumbnails in a row, no two share the same one-word read,
no two share the same primary palette, and no two share the same motif
pool. The eye can tell at thumbnail size that Truth Compass is not Soul
Repair is not Cosmic Edge. Brand differentiation is solved by COMMITTING
HARDER per brand, not by adding more elements.

---

## §2 Author visual identity layer

Today each brand has one author. The 800-book future has multiple authors
per brand. The author layer must distinguish authors WITHIN brand discipline
WITHOUT breaking brand recognition.

### §2.1 Author signature mechanics (three permitted variations)

Within a brand's palette and motif pool, each author chooses:

1. **Author signature color.** Either the brand's accent color, OR a
   second permitted accent within ±15° hue of the brand accent. The
   author's color appears on every cover that author makes; it's the
   reader's "this is them" signal at thumbnail.
2. **Author motif focus.** Each author leans on 1–2 of the brand's 3–5
   motifs, not all of them. Different author = different motif lean.
3. **Author typography quirk.** A small, persistent variation: italic
   subtitle, lowercase title break, hand-lettered author byline, double
   space before the final word, etc. Brand font family stays. Quirk is
   the author's persistent micro-choice.

### §2.2 Per-author signature cards (current 13)

Because today each brand has one author, each author is also the brand's
default signature. These cards anchor the brand and define the rule for
future author #2 in that brand to differentiate against.

- **Ahjan / Inner Light Press.** Signature color: `#7AA3C7` calm sky-blue.
  Motif focus: low horizon (NOT the threshold or arch). Type quirk: title
  set in 2 lines with line break before the final word.
- **Adi Da / Awakening Press.** Signature color: `#E8B765` sunlit gold.
  Motif focus: single sun / mandorla. Type quirk: title in small-caps,
  author in italic.
- **Joshin / Still Forest.** Signature color: `#A23A2A` vermillion seal.
  Motif focus: single ink stroke. Type quirk: vertical author column on
  right edge.
- **Junko / Zen Clarity.** Signature color: `#F2C14E` mustard. Motif
  focus: knot / continuous-line. Type quirk: title tracking +6%, author
  tracking +12%.
- **Ma'at / Truth Compass.** Signature color: `#C9523B` terracotta.
  Motif focus: thick rule + capitalized key word. Type quirk: ONE word
  in the title set 30% bigger than the rest; that word carries the
  accent color.
- **Master Feung / Vitality Path.** Signature color: `#3D5944` deep
  pine. Motif focus: single bamboo / mountain. Type quirk: vertical
  Chinese title column with English subtitle horizontal beneath.
- **Master Sha / Soul Repair.** Signature color: `#9D8068` warm ash.
  Motif focus: single feather (not the candle, not the chair). Type
  quirk: italic subtitle directly under title, no rule between.
- **Master Wu / Mountain Gate Press.** Signature color: `#8E2A1C`
  battle red. Motif focus: mountain peak silhouette. Type quirk:
  small calligraphic seal mark at upper-right.
- **Miki / Gen Spark.** Signature color: `#FF5630` coral red. Motif
  focus: sliced word as cover. Type quirk: title cropped at right
  edge, finishes off-canvas.
- **Omote / Gentle Wave.** Signature color: `#C97C5D` warm clay. Motif
  focus: single low candle. Type quirk: lowercase title with
  generous line-height.
- **Pamela Fellows / Body Wisdom.** Signature color: `#E2A23B` signal
  gold. Motif focus: single nerve-tree / root system. Type quirk:
  subtitle in regular italic.
- **Ra / Cosmic Edge.** Signature color: `#E0B341` gold accent. Motif
  focus: single solar disc / mandala. Type quirk: all-caps title in
  Trajan Pro.
- **Sai Maa / Healing Ground Press.** Signature color: `#D89A6E` warm
  peach. Motif focus: warm hand-light through tree. Type quirk:
  italic subtitle, lowercase author byline.

---

## §3 Series continuity layer

When an author has multiple titles (or sequels), they share visual DNA
that says "by the same author, in the same arc" without being
interchangeable. Three schemas, ranked by use case:

### §3.1 Schema A — Rotating accent within fixed template

**Template stays constant.** Brand template, brand palette, brand motif
pool, author motif focus, author type quirk — all fixed. The accent COLOR
rotates per book within a permitted accent palette of 3–5 colors that all
sit within ±15° of the brand accent hue.

**Use case.** Best for self-help backlists where each book is an
independent topic by the same author. The reader recognizes the author
shelf at a glance; each book is visually distinct via the accent.

**Example:** if Ahjan publishes books on anxiety, then sleep, then burnout,
the brand sky-blue stays the brand color; the per-book accent rotates
through dawn-rose / lavender / sage / amber. Same horizon. Different
moment of light.

### §3.2 Schema B — Fixed motif at varying scale or composition

**Motif stays constant; scale or framing varies.** Same focal element
appears on every book in the series, but at different scale,
composition, or moment. Useful for trilogies and tightly bound
series where the books are explicitly stages of one journey.

**Example:** Master Wu's first book shows the mountain peak from far below
(facing the climb); book two from halfway up (mid-ascent); book three
from the summit looking back. Same mountain, same brand, same author,
clearly a journey.

### §3.3 Schema C — Numbered visual element (band, ring, accumulating mark)

**A single visual element accumulates across the series.** A band that
fills in (1/5, 2/5, 3/5), a ring that closes, a numbered seal. Useful
for explicit numbered series ("The Boundaries Trilogy: I, II, III").

**Example:** Ma'at's terracotta thick rule on book one extends slightly
on book two, fully on book three — a visual completion arc. Title remains
the dominant element; the rule is the secondary continuity mark.

### §3.4 Selection rule

- Default: Schema A (rotating accent). Most flexible for self-help
  catalogs where books are independent.
- If books are stages of one explicit journey: Schema B.
- If books are an explicit numbered set: Schema C.

R7 should default to Schema A unless metadata explicitly tags a book
as `series_kind: journey` or `series_kind: numbered`.

---

## §4 Individual book vibe layer (the curated 5%)

Even after brand, author, and series constraints, every individual book
needs four specific choices that should be human-curated, not auto-generated.
Generic per-genre prompts have been failing precisely because this layer
was missing — every cover got the same brand+genre fill, which is why the
operator says "every cover can't have the same template or feeling."

### §4.1 The four per-book curated choices

1. **Subject specificity.** Not "a horizon" — *"low horizon at first
   light, single thin dawn line cutting cool dusk."* The exact subject
   choice is what gives the cover its point. Generators cannot pick
   this specificity; humans (or a careful prompt) must.
2. **Title placement variation.** Within the brand's title zone, choose
   exactly where the title sits on this particular cover (upper-third
   center, mid-third left-aligned, lower-third right-aligned). The
   variation gives each book its own breathing.
3. **Mood-specific micro-palette shift.** Brand palette stays. The
   AMOUNTS shift. This book pulls warmer (cream toward butter), or
   cooler (sky-blue toward steel). The micro-shift is the book's
   weather.
4. **Atmospheric register.** One specific register sentence per book:
   *"morning before the alarm, before the noise."* This is the line a
   human writes and the prompt incorporates verbatim. Without it, FLUX
   defaults to "atmospheric goo."

### §4.2 Why this is the human-curated 5%

Brand (§1), author (§2), and series (§3) cover ~95% of the cover spec
deterministically. The remaining 5% is what makes a particular book
feel like ITSELF — the operator's "every author has their own vibe,
every cover has a point." Auto-generating this 5% is what produces
clip-art covers. A small human pass per book — even a 90-second author
brief — is the difference between bestseller-grade and template-fill.

R7 should treat the §4 fields as REQUIRED inputs for cover render. If
any of the four fields is missing, the renderer halts and asks the
operator/author for the value.

---

## §5 Concrete instantiation: our 13 sample books

Each card applies §1–§4 to the existing book. Subject + register strings
are R6's first-pass authorial brief; the operator/author should confirm
or revise per book before shipping.

### ahjan — Inner Light Press — *The Alarm Is Lying*

```
brand: inner_light_press
brand_inspiration: "Sounds True (atmospheric, contemplative, 80% type 20% imagery)"
brand_palette: ["#0E1B33", "#FAF1DD", "#7AA3C7"]
brand_motif_pool: [horizon, dawn_light, threshold, single_arch, ink_wash_atmosphere]
brand_typography: "DM Serif Display title sentence-case generous tracking; lowercase Inter Light author"
author_signature_color: "#7AA3C7"
author_motif_focus: "horizon"
author_type_quirk: "title in 2 lines, line break before final word"
this_book_subject: "low horizon at first light, single thin dawn line cutting cool dusk"
this_book_micro_palette_shift: "warm cream pulled slightly toward butter"
this_book_register: "morning before the alarm, before the noise"
series: null
```

### adi_da — Awakening Press — *You Were Always Enough*

```
brand: awakening_press
brand_inspiration: "Tarcher (Penguin) — single bold conceptual mark on saturated solid color"
brand_palette: ["#3A2E5F", "#F5EFE3", "#E8B765"]
brand_motif_pool: [sun, single_circle, mandorla, ascending_line]
brand_typography: "Cormorant Garamond title small-caps; matching serif italic author"
author_signature_color: "#E8B765"
author_motif_focus: "sun"
author_type_quirk: "title in small-caps, author in italic"
this_book_subject: "single warm sun-disc rising from indigo field, gold edge backlight"
this_book_micro_palette_shift: "gold accent slightly warmer toward amber"
this_book_register: "the moment before you knew, you already were"
series: null
```

### joshin — Still Forest — *Quiet Enough*

```
brand: still_forest
brand_inspiration: "Shambhala Pocket Library — spare East-Asian-influenced typography"
brand_palette: ["#F8F4EC", "#1F1F1F", "#A23A2A"]
brand_motif_pool: [single_ink_stroke, enso, low_pine_silhouette, single_stone, vertical_column]
brand_typography: "EB Garamond title lowercase; vertical Inter author column; optional red seal"
author_signature_color: "#A23A2A"
author_motif_focus: "single_ink_stroke"
author_type_quirk: "vertical author column on right edge"
this_book_subject: "single horizontal ink stroke, sumi black, mid-frame, slight bleed at right"
this_book_micro_palette_shift: "rice-paper warm pulled slightly cooler"
this_book_register: "the room after the door has closed, before the next thought"
series: null
```

### junko — Zen Clarity — *The Loop Breaker*

```
brand: zen_clarity
brand_inspiration: "Penguin Modern Classics minimalist — solid color + single small symbol"
brand_palette: ["#1A4D5C", "#F5F5F0", "#F2C14E"]
brand_motif_pool: [single_dot, geometric_icon, thin_rule, three_dots, knot]
brand_typography: "Helvetica Now Display title tight tracking; regular weight secondary"
author_signature_color: "#F2C14E"
author_motif_focus: "knot"
author_type_quirk: "title tracking +6%, author tracking +12%"
this_book_subject: "single continuous line forming a loose knot in upper-third, mustard color, paper field"
this_book_micro_palette_shift: "teal pulled slightly toward charcoal"
this_book_register: "the same thought, the eighth time, the moment you notice"
series: null
```

### maat — Truth Compass — *The No That Saved Me*

```
brand: truth_compass
brand_inspiration: "Riverhead Books — bespoke hand-set typography, two-color plus off-white"
brand_palette: ["#000000", "#F4ECDC", "#C9523B"]
brand_motif_pool: [thick_rule, single_bold_square, architectural_line, single_bracket, capitalized_key_word]
brand_typography: "Söhne Breit hand-tweaked title; key word 30% larger; bottom-third author"
author_signature_color: "#C9523B"
author_motif_focus: "capitalized_key_word"
author_type_quirk: "ONE word in title 30% bigger, that word in accent color"
this_book_subject: null
this_book_subject_note: "Type-only cover. The word NO set in terracotta, 30% larger than the rest of the title, anchor-left upper-third."
this_book_micro_palette_shift: "parchment slightly warmer"
this_book_register: "the line you draw with your back straight"
series: null
```

### master_feung — Vitality Path — *After Burnout*

```
brand: vitality_path
brand_inspiration: "Shambhala Snow Lion / CUHK Press — Taoist scholarly-warm register"
brand_palette: ["#7A2E1F", "#EDD9B2", "#3D5944"]
brand_motif_pool: [single_bamboo, mountain_silhouette, water_flow_line, character_seal]
brand_typography: "Source Han Serif vertical title; EB Garamond italic English subtitle; small red seal"
author_signature_color: "#3D5944"
author_motif_focus: "single_bamboo"
author_type_quirk: "vertical Chinese title with horizontal English subtitle beneath"
this_book_subject: "single bamboo stalk, mid-frame, leaning slightly with breath wind, silk paper texture"
this_book_micro_palette_shift: "cinnabar pulled slightly toward earth-red"
this_book_register: "the breath that returns when the work has stopped"
series: null
```

### master_sha — Soul Repair — *The Weight of Gone*

```
brand: soul_repair
brand_inspiration: "Sounds True grief register — small single object on near-empty cream field"
brand_palette: ["#2A2D3E", "#F0E9DA", "#9D8068"]
brand_motif_pool: [single_feather, single_lit_candle, distant_bird, empty_chair, lone_leaf]
brand_typography: "Caslon title sentence-case; italic subtitle; small-caps author"
author_signature_color: "#9D8068"
author_motif_focus: "single_feather"
author_type_quirk: "italic subtitle directly under title, no rule between"
this_book_subject: "single small feather mid-frame on cream paper, soft falling shadow, dusk slate sky beyond"
this_book_micro_palette_shift: "cream pulled slightly toward bone"
this_book_register: "the chair across the table, the room where they were"
series: null
```

### master_wu — Mountain Gate Press — *The Way of Courage*

```
brand: mountain_gate_press
brand_inspiration: "North Atlantic / Shambhala martial-arts — bold ink-wash, dark saturated"
brand_palette: ["#0F0F12", "#D9C9A8", "#8E2A1C"]
brand_motif_pool: [mountain_peak, training_stance_silhouette, clenched_scroll, tiger_mark, vertical_sword]
brand_typography: "Adobe Song Std vertical title; Inter Bold English subtitle; calligraphic 勇 seal"
author_signature_color: "#8E2A1C"
author_motif_focus: "mountain_peak"
author_type_quirk: "small calligraphic seal mark at upper-right"
this_book_subject: "single mountain peak silhouette in sumi ink, low horizon, wheat-color sky behind, paper grain visible"
this_book_micro_palette_shift: "battle red pulled slightly toward iron-red"
this_book_register: "the step you take while still afraid"
series: null
```

### miki — Gen Spark — *Who Let Me In*

```
brand: gen_spark
brand_inspiration: "Riverhead Design Labs experimental typographic — sliced/cut typography"
brand_palette: ["#FF5630", "#FFF6E5", "#1A1A1A"]
brand_motif_pool: [sliced_word, doubled_word, type_as_shape, type_as_stencil, geometric_crop]
brand_typography: "GT Sectra Display sliced/cropped; bottom-third Inter author"
author_signature_color: "#FF5630"
author_motif_focus: "sliced_word"
author_type_quirk: "title cropped at right edge, finishes off-canvas"
this_book_subject: null
this_book_subject_note: "Type-only cover. Title set in coral GT Sectra Display, sliced at right edge so 'IN' bleeds off-canvas. Off-white field. Small black author block bottom-third."
this_book_micro_palette_shift: "coral pulled slightly toward sunset"
this_book_register: "the badge you didn't earn that nobody asked you to earn"
series: null
```

### omote — Gentle Wave — *Dark Room, Loud Brain*

```
brand: gentle_wave
brand_inspiration: "Sounds True / Storey somatic — soft photographic gradient, single small object low"
brand_palette: ["#1B2A3A", "#E9DFD0", "#C97C5D"]
brand_motif_pool: [single_low_candle, dim_window, single_moth, distant_threshold, slow_river]
brand_typography: "Lora title lowercase generous line-height; lowercase Inter Light author"
author_signature_color: "#C97C5D"
author_motif_focus: "single_low_candle"
author_type_quirk: "lowercase title with generous line-height"
this_book_subject: "single small low candle, warm clay glow, vast navy room above, soft photographic depth-of-field"
this_book_micro_palette_shift: "lamp cream pulled slightly toward parchment"
this_book_register: "2:47 a.m., the brain too loud to sleep, the candle still"
series: null
```

### pamela_fellows — Body Wisdom — *Wired for Worry*

```
brand: body_wisdom
brand_inspiration: "Sounds True clinical-somatic / Norton popular-science — single anatomical mark"
brand_palette: ["#0B3D3D", "#F4EFE6", "#E2A23B"]
brand_motif_pool: [single_nerve_tree, single_root_system, anatomical_brain_icon, coiled_spring, single_thread]
brand_typography: "Tiempos Headline title sentence-case; matching serif regular author"
author_signature_color: "#E2A23B"
author_motif_focus: "single_nerve_tree"
author_type_quirk: "subtitle in regular italic"
this_book_subject: "single fine-line nerve-tree illustration, warm gold ink, deep teal field, slight pencil register"
this_book_micro_palette_shift: "teal pulled slightly cooler"
this_book_register: "the body deciding before the mind, again"
series: null
```

### ra — Cosmic Edge — *The Proof Was Always You*

```
brand: cosmic_edge
brand_inspiration: "TarcherPerigee esoteric — cosmic single circle, deep saturated dark, gold accent"
brand_palette: ["#0A0E2C", "#F4E6BA", "#E0B341"]
brand_motif_pool: [single_solar_disc, single_mandala, single_eye_as_shape, single_arc, single_triangle_of_light]
brand_typography: "Trajan Pro title all-caps; matching small-caps author; optional gold-foil register"
author_signature_color: "#E0B341"
author_motif_focus: "single_solar_disc"
author_type_quirk: "all-caps title in Trajan Pro"
this_book_subject: "single full solar disc centered upper-third, gold edge ring, deep cosmos navy field"
this_book_micro_palette_shift: "cosmos pulled slightly toward midnight purple"
this_book_register: "the proof you carry, that you keep forgetting is already there"
series: null
```

### sai_ma — Healing Ground Press — *Still Here Without You*

```
brand: healing_ground_press
brand_inspiration: "Hay House warm-hopeful — warm palette, single illuminated organic motif"
brand_palette: ["#3F2E2A", "#F5E9D6", "#D89A6E"]
brand_motif_pool: [sun_through_tree, single_flower, warm_hand_light, open_window, warm_threshold]
brand_typography: "Cormorant Garamond title; italic subtitle; lowercase author"
author_signature_color: "#D89A6E"
author_motif_focus: "warm_hand_light"
author_type_quirk: "italic subtitle, lowercase author byline"
this_book_subject: "single warm hand-shaped light through tree branches, golden cream field, soft vignette"
this_book_micro_palette_shift: "earth pulled slightly toward warm walnut"
this_book_register: "the room they were in, still warm, still yours"
series: null
```

---

## §6 Quality gates the renderer must pass

Every cover must pass these gates BEFORE it ships. Some are automated;
some require a 30-second operator visual check (called out as `manual:
true`). Failed gates halt the render and require re-prompt or human
revision.

```yaml
quality_gates:
  thumbnail_focal_clarity:
    automated: true
    method: "render at 100x160, run saliency map; require single peak >= 1.6x second peak"
  title_legible_at_thumbnail:
    automated: true
    method: "render at 100x160, OCR title; min confidence 0.7"
  color_count:
    automated: true
    method: "k-means cluster final RGB; require <= 3 dominant clusters at >5% area each"
  brand_palette_respected:
    automated: true
    method: "verify dominant cluster centers within delta-E 8 of brand palette hex"
  author_signature_color_present:
    automated: true
    method: "verify >=5% area within delta-E 8 of author signature hex"
  no_ai_atmospheric_goo:
    automated: false
    manual: true
    method: "operator confirms no soft-gradient mush in imagery zone"
  shadow_consistency:
    automated: false
    manual: true
    method: "operator confirms light direction consistent on focal element vs background"
  no_pseudo_photorealism_smudge:
    automated: false
    manual: true
    method: "operator confirms edges crisp; not the schnell 4-step smudge"
  not_interchangeable_with_siblings:
    automated: false
    manual: true
    method: "operator places 4 covers from same brand side-by-side; can name each"
  emotional_one_word_read:
    automated: false
    manual: true
    method: "operator + 1 non-designer name same one-word register"
  warm_white_not_pure:
    automated: true
    method: "verify any white cluster >= #F0EBE0 warmth, not pure #FFFFFF"
```

---

## §7 What to do about schnell vs flux1-dev

This framework's quality assumes **flux1-dev fp8 at 28 steps** as the
floor. Per Stable Diffusion Tutorials' detailed comparison and the
Segmind Flux comparison, schnell at 4 steps cannot reliably render
crisp object edges, coherent depth-of-field, or the production-tell
detail register the framework requires. Schnell's 4-step distillation
introduces the characteristic "schnell smudge" — a soft, half-resolved
texture across the whole image that no prompt sophistication can
override.

flux1-dev at 28 steps with `dpmpp_2m + karras` (the cookbook's current
H1=A engine config) is the correct realization tier. Below that, the
framework cannot deliver bestseller-grade output regardless of prompt
quality.

If hardware constraints force schnell, the renderer must **bypass
imagery entirely** and ship type-only covers (per the §1 brands marked
type-dominant: Truth Compass, Gen Spark, Zen Clarity for some books).
Schnell cannot do photorealistic-leaning imagery at bestseller quality.

**Recommendation for R7:** make `imagery_engine: flux1-dev` a hard
contract. If the engine drops to schnell, the renderer must auto-route
to type-only fallback rather than ship smudge.

---

## §8 Open questions and caveats

### Where I extrapolated, not directly evidenced

- **Hay House visual signature.** Search did not return a designer
  feature article specifying Hay House's house style at the level of
  Riverhead/Knopf documentation. I described the warm-hopeful register
  consistent with public catalog observation (Louise Hay, Wayne Dyer,
  Doreen Virtue covers all share warm earth + golden cream + organic
  motif). Confidence: medium. R7 / operator should confirm before
  treating Healing Ground Press's spec as fixed.
- **Sounds True visual signature.** Same caveat: Sounds True is well
  known as an audio-first publisher; their book covers are documented
  less thoroughly than Riverhead's. The "atmospheric contemplative"
  register I assigned to Inner Light Press / Soul Repair / Gentle
  Wave / Body Wisdom is based on public catalog observation, not a
  designer-feature article. Three of our 13 brands lean Sounds-True;
  if the operator finds that too repetitive at brand level, swap one
  to Storey Publishing (somatic) or North Atlantic (clinical-spiritual).

### What needs operator decisions (not researchable)

- The four §4 per-book curated fields — `this_book_subject`,
  `this_book_micro_palette_shift`, `this_book_register`, and series
  metadata — should be confirmed or revised per book by the actual
  author or operator. The values in §5 are R6's first-pass brief; they
  are NOT authoritative.
- Author #2, #3, ... per brand. The `author_signature_color`,
  `author_motif_focus`, `author_type_quirk` triple needs to be
  assigned per future author. The framework specifies the rule; the
  human picks the values.
- Whether Gen Spark's coral `#FF5630` is too saturated against
  Awakening Press's `#E8B765` and Cosmic Edge's `#E0B341` (three
  warm-yellow-orange-adjacent brands). On a 13-thumbnail row this may
  feel slightly clustered; consider shifting Gen Spark to a magenta
  or electric purple to harden the differentiation.

### What I did not research (out of scope by hard rules)

- Author face references / facial scraping (forbidden by hard rule).
- Direct cover-art reproduction (forbidden by hard rule).
- Paid LLM/image API spend (forbidden by hard rule).
- The actual rendering pipeline integration in
  `scripts/publish/render_kdp_cover.py` (R7's job).

---

## §9 Structured handoff for R7

The full machine-readable handoff lives at
`config/publishing/cover_identity_system.yaml` (delivered alongside this
artifact). That YAML is the contract R7 should consume:

- `brands.<brand_id>` — full §1 spec.
- `authors.<author_id>` — full §2 spec, with `brand_id` foreign key.
- `books.<book_id>` — full §5 spec, with `author_id` foreign key.
- `quality_gates` — full §6 spec.
- `series_schemas` — full §3 spec.
- `engine_floor` — flux1-dev fp8 / 28 steps / dpmpp_2m / karras.

R7 changes the renderer to:
1. Read `cover_identity_system.yaml` for the book being rendered.
2. Compose the FLUX prompt from `brands.X.motif_pool[author.motif_focus]
   + book.this_book_subject + book.this_book_register + brand.palette`,
   not from the per-genre cookbook.
3. Reserve type zones per brand (R4's bestseller_templates.yaml still
   provides geometry).
4. Run all `quality_gates` before declaring success. Fail-closed on any
   gate, with operator surfaced reason.

R6's framework (§0–§4) is the reasoning layer; the YAML is the contract;
the renderer is R7's mechanical translation layer. The operator's `400
high-confidence configs` future-state plugs in by adding new
`books.<book_id>` rows referencing existing brand/author rows + supplying
the four §4 curated fields.

---

## §10 References

- Reedsy. "What Makes a Good Book Cover? Your Guide to Research and Trends." reedsy.com/blog/guide/book-cover-design/
- Reedsy. "How to Design a Book Cover: 10 Dos and Don'ts." reedsy.com/blog/guide/book-cover-design/how-to-design/
- Damonza. "6 Book Cover Design Trends for 2026." damonza.com/6-book-cover-design-trends-for-2026/
- Damonza. "AI Book Covers in 2025: Your Indie Author Decision Guide." damonza.com/ai-book-covers-in-2025-your-indie-author-decision-guide/
- KDPEasy. "Self-Help Book Cover Design: Minimalist Trends for 2026." kdpeasy.com/blog/self-help-book-cover-design
- KDPEasy. "Book Cover Design Principles: The Complete Guide (2025)." kdpeasy.com/guides/book-cover-design-principles
- KDPEasy. "Common Book Cover Design Mistakes (and How to Fix Them) — 2025." kdpeasy.com/guides/book-cover-design-mistakes
- Creative Paramita. "Book Cover Thumbnail That Survives the Amazon Test." creativeparamita.com/book-cover/book-cover-thumbnail-that-survives-the-amazon-test/
- Creativindie. "How to Design a Self-Help or Business Book Cover (2026 Guide)." creativindiecovers.com/how-to-design-a-self-help-business-book-cover/
- Creativindie. "MidJourney AI art for book cover design (how is this legal?)." creativindie.com/midjourney-ai-for-book-cover-design-how-is-this-legal/
- Creativindie. "How to Design a Literary Fiction Book Cover (2026 Guide)." creativindiecovers.com/how-to-design-a-literary-fiction-book-cover/
- Lit Hub. "The 173 Best Book Covers of 2025." lithub.com/the-173-best-book-covers-of-2025/
- Lit Hub. "The Best Book Covers of the Last Decade." lithub.com/the-best-book-covers-of-the-last-decade/
- Penguin Random House. "Behind the Book Covers with Riverhead's Grace Han." global.penguinrandomhouse.com/announcements/behind-the-book-covers-with-riverheads-grace-han/
- Steve Fenton. "The 6 Warning Signs Of An AI-generated Book." stevefenton.co.uk/blog/2025/01/generated-books/
- Stable Diffusion Tutorials. "Flux: Dev vs Schnell vs Pro (Detailed Comparison)." stablediffusiontutorials.com/2025/04/flux-schnell-dev-pro.html
- Segmind. "Flux.1 Comparison: Schnell vs Dev Vs Pro." blog.segmind.com/flux-comparison-schnell-vs-dev-vs-pro/
- Sounds True. "Books on Spirituality, Mindfulness & Personal Growth." soundstrue.com/collections/book-smart-collection
- Shambhala Pubs. "Judging Books by Their Covers: A Defense." shambhala.com/judging-books-by-their-covers-a-defense/
- Penguin Random House. "Shambhala Pocket Library." penguinrandomhouse.com/series/POL/shambhala-pocket-library/
- TarcherPerigee. en.wikipedia.org/wiki/TarcherPerigee
- The Brief AI. "20 Iconic Examples of Book Cover Typography." thebrief.ai/blog/book-cover-typography/
- IngramSpark. "9 Book Cover Design Styles That Stand the Test of Time." ingramspark.com/blog/9-book-cover-design-styles-that-stand-the-test-of-time
- Page Publishing. "Crafting Cohesive Series: A Guide to Consistent Book Covers." pagepublishing.com/crafting-cohesive-series-a-guide-to-consistent-book-covers/
- Spine Magazine. "Creating Cohesive Visual Consistency When Designing a Book Series." spinemagazine.co/articles/creating-cohesive-visual-consistency-when-designing-a-book-series

---

**End of artifact.**
