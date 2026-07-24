# US Illustrated Self-Help — Book Format Category Study

**Date:** 2026-07-24
**Lane:** manga process uplift pack, Lane 02 (Pearl_Research)
**Branch:** `agent/us-illustrated-format-research-20260724`
**Status of parameters downstream:** flips `config/manga/us_illustrated_pilot_cells.yaml` format parameters from ASSERTED → RESEARCHED
**Builds on (does not fork):** `artifacts/research/western_illustrated_styles_2026_04_04.md` (comic-format styles; does NOT cover the illustrated-trade self-help book category), `docs/US_CATALOG_PLAN.md` §3 ("Illustrated Prose Hybrid", 2 comps, no format parameters), `config/manga/us_illustrated_pilot_cells.yaml`, `config/manga/western_cartoon_styles.yaml`
**Sourcing style:** matches `artifacts/research/popular_genre_ranking_2026-05-02.md` — every load-bearing number carries source + access date; confidence rating per section
**Operator ruling honored:** Q-MPU-03 — the US illustrated lane gets BOTH planning frames; this study is the BOOK-format primary deliverable, with a short secondary section on serialized illustrated wellness (§6). The lane must not inherit manga episode framing; planning-contract implications are flagged for Lane 06 in the handoff, not specced here.

`NEW-ARTIFACT-JUSTIFIED: dedicated US illustrated-self-help category study absent (confirmed 2026-07-24 inventory — no artifacts/research/*illustrated*self*help* on origin/main @ d55f6f39)`

---

## 0. What this study answers

`config/manga/us_illustrated_pilot_cells.yaml` routes five en_US pilot cells to
`master_format: direct_self_help_illustrated`, but no page-count, trim, art:text,
words-per-page, color-mode, or price parameters existed anywhere in config or research —
the format was asserted, not researched. This study derives those parameters from a
17-title US-market comp corpus and feeds them back into the config with per-row
confidence (§5).

Category definition used throughout: **illustrated-trade self-help** = books shelved in
Self-Help / Inspiration / Humor whose illustration is structural (the page does not work
without the art), sold through general trade (not comic shops), read left-to-right,
book-shaped (not serialized episodes). Five sub-format classes emerged from the corpus
and are used for all norms and recommendations:

| Class | Name | Definition | Corpus rows |
|---|---|---|---|
| A | Gift / inspiration illustrated | full-page art IS the page; text is aphoristic | 1, 2, 10, 11, 17 |
| B | Doodle-humor strip collection | strip/panel cartoons, humor register | 4, 5, 7, 12, 15 |
| C | Graphic-memoir essay hybrid | alternating text blocks and drawings, essay chapters | 3, 6, 13 |
| D | Graphic-medicine explainer | clinical topic rendered as continuous comic explainer | 8, 14 |
| E | Illustrated-prose idea book | text-dominant prose with structural spot art | 9, 16 |

Art:text classes: **FP** full-page-art dominant; **ST** strip/panel cartoon; **SP**
spot-art punctuating text; **HY** hybrid (alternating text blocks and drawings).
Word-count classes: **micro** <5k total; **light** 5–15k; **medium** 15–30k; **heavy** >30k.

---

## 1. Comp-title corpus (17 titles)

### 1a. Physical format parameters

Confidence: page counts, trims, and list prices marked with a source are HIGH (publisher
or bibliographic record). Art:text class and words/page are informed estimates from
format descriptions and reader-facing samples — MED confidence unless noted.

| # | Title (Author) | US imprint, yr | Cls | Pages | Trim (in) | Color | Art:text | Words/page (est.) | Word class | US list |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The Boy, the Mole, the Fox and the Horse (Charlie Mackesy) | HarperOne, 2019 | A | 128 (unpaginated) [S1][S1d] | ~9.8 × 7.6 class (est.) | Color (ink+wash) | FP | 10–35 | micro | $22.99 HC [S1c] |
| 2 | Big Panda and Tiny Dragon (James Norbury) | Mandala/Insight Eds., 2021 | A | 160 [S2] | 6.7 × 8.2 [S2] | Color (watercolor) | FP | 10–40 | micro | $19.99 HC [S2b] |
| 3 | Hyperbole and a Half (Allie Brosh) | Touchstone/S&S, 2013 | C | 384 [S3] | 5.5 × 8.2 [S3] | Color (digital) | HY | 100–200 | heavy | $19.99 PB class (band) |
| 4 | Adulthood Is a Myth (Sarah Andersen) | Andrews McMeel, 2016 | B | 112 [S4] | ~8 × 8 sq. class (est.) | B&W + gray | ST | 5–25 | micro | $9.99–14.99 PB (band) |
| 5 | Quiet Girl in a Noisy World (Debbie Tung) | Andrews McMeel, 2017 | B | 184 [S5] | ~7 × 9 class (est.) | B&W | ST | 10–40 | light | $14.99–16.99 PB (band) |
| 6 | Am I There Yet? (Mari Andrew) | Clarkson Potter/PRH, 2018 | C | 192 [S6] | 6.5 × 8.5 [S6] | Color (watercolor) | HY | 60–150 | medium | $21.99 HC [S6] |
| 7 | The Worrier's Guide to Life (Gemma Correll) | Andrews McMeel, 2015 | B | 112 [S7] | ~7 × 9 class (est.) | Color | ST | 10–40 | micro | $12.99–14.99 PB (band) |
| 8 | Anxiety Is Really Strange (Haines/Standing) | Singing Dragon/JKP, 2018 | D | 32–80 (sources conflict; LOW) [S8] | comic-album class | Color | ST/FP | 40–90 | light | ~$14.95 PB (band) |
| 9 | Steal Like an Artist (Austin Kleon) | Workman, 2012 | E | 160 [S9] | 6 × 6 [S9] | B&W + spot | SP | 80–150 | light–medium | $14.99 PB [S9] |
| 10 | The Crossroads of Should and Must (Elle Luna) | Workman, 2015 | A | 176 [S10] | ~7 × 9 class (est.) | Color | FP/HY | 30–80 | light | $20.00 HC [S10] |
| 11 | milk and honey (Rupi Kaur) | Andrews McMeel, 2015 | A | 208 [S11] | ~5 × 7.8 class (est.) | B&W line | FP | 20–60 | light | $14.99 PB orig. class [S11] |
| 12 | Heart and Brain (Nick Seluk) | Andrews McMeel, 2015 | B | 144 [S12] | ~7 × 9 class (est.) | Color | ST | 10–40 | micro | $16.99 PB [S12] |
| 13 | Marbles: Mania, Depression, Michelangelo, and Me (Ellen Forney) | Gotham/Penguin, 2012 | C | 248 [S13] | ~6 × 9 class (est.) | B&W | HY | 80–180 | medium–heavy | $18–20 PB (band) |
| 14 | The Illustrated Happiness Trap (Harris/Aisbett) | Shambhala, 2014 | D | 176 [S14] | 5 × 7.75 [S14] | B&W cartoon | ST | 60–120 | medium | $16.95 PB [S14] |
| 15 | Introvert Doodles (Maureen "Marzi" Wilson) | Adams Media/S&S, 2016 | B | 176 [S15] | ~7 × 8 class (est.) | Color | ST | 10–40 | light | $15.99–16.99 HC (band) |
| 16 | No Hard Feelings (Fosslien/West Duffy) | Portfolio/PRH, 2019 | E | 304 [S16] | 5.875 × 8.25 [S16] | 2-color art | SP | 200–300 | heavy | $29.00 HC [S16] |
| 17 | All Along You Were Blooming (Morgan Harper Nichols) | Zondervan, 2020 | A | 182 [S17] | ~7 × 9 class (est.) | Color | FP | 20–60 | light | $19.99 HC class (band) |

### 1b. Positioning + market signal per comp

| # | Title | Shelving (retail category) | Market signal |
|---|---|---|---|
| 1 | Boy/Mole/Fox/Horse | Self-Help / Inspiration; gift | >250K US copies by Jan 2020 [S1d]; USA Today list debut #20 [S1d]; 2019 B&N Book of the Year + Waterstones Book of the Year [S1d]; #1 selling book of 2020, Nielsen BookScan UK TCM, >1M copies, longest-running Sunday Times hardback #1 [S1b] |
| 2 | Big Panda & Tiny Dragon | B&N: Self-Help & Relationships → Inspiration → Affirmations & Inspiration [S2b] | UK Sunday Times bestseller; franchise line (journal, sequels) [S2c] |
| 3 | Hyperbole and a Half | Humor / Memoir-essay | #1 NYT bestseller at launch; ~700K+ copies (internal `docs/US_CATALOG_PLAN.md` §3, compiled 2026-04-23) |
| 4 | Adulthood Is a Myth | Humor / Comics | Series "millions of copies worldwide," 20+ languages [S4b]; Goodreads Choice winner 2016/2017/2018 [S4b] |
| 5 | Quiet Girl in a Noisy World | Humor / Graphic Memoir | Backlist evergreen for introvert/anxiety audience (qualitative) |
| 6 | Am I There Yet? | PRH: Art; Self-Improvement & Inspiration [S6] | Instagram-native author (~1M followers at launch); NYT bestseller claim on jacket (not independently verified — LOW) |
| 7 | Worrier's Guide to Life | Humor / Self-Help crossover | Anxiety-humor category anchor; named register comp in `config/manga/western_cartoon_styles.yaml` |
| 8 | Anxiety Is Really Strange | Graphic Medicine (explicit shelving term) | Highly Commended, BMA Book Awards 2018 [S8b] |
| 9 | Steal Like an Artist | Self-Help / Creativity | >1M copies, 30+ languages, NYT bestseller [S9b]; 10th-anniversary deluxe HC reissue (franchise durability) [S9b] |
| 10 | Crossroads of Should and Must | Self-Help / Motivation | Started as a viral Medium essay → Workman book (essay-to-book pipeline) [S10b] |
| 11 | milk and honey | Poetry / gift-inspiration crossover | 1M copies by Feb 2017 (PRNewswire) [S11b]; >6M global, best-selling poetry book of the 21st century, >100 consecutive weeks on NYT list [S11] |
| 12 | Heart and Brain | Humor | Webcomic (The Awkward Yeti) → AMP collections; 3+ volumes [S12] |
| 13 | Marbles | Graphic Medicine / Memoir | Category-defining graphic-medicine memoir (bipolar); reviewed as such by graphicmedicine.org [S13b] |
| 14 | Illustrated Happiness Trap | Self-Improvement; Psychology [S14] | Cartoon retrofit of a >1M-copy ACT self-help brand (The Happiness Trap) — the ONLY successful retrofit found (see §3 negative finding) |
| 15 | Introvert Doodles | Humor / Self-Help crossover | Instagram-native (@introvertdoodles) → Adams Media; spawned activity-book series [S15b] |
| 16 | No Hard Feelings | Business; Self-Improvement; Psychology [S16] | WSJ bestseller claim (jacket); workplace-emotions illustrated hybrid anchor |
| 17 | All Along You Were Blooming | Christian gift / Inspiration | Instagram-native author (millions of followers); graduation-gift positioning [S17] |

---

## 2. Format norms (derived from corpus)

Confidence: HIGH for page/price/binding bands (sourced rows); MED for words-per-page and
art-density bands (estimates on sourced structure).

### 2a. Page-count bands — derived, per class

| Class | Band observed | Typical target | Rows |
|---|---|---|---|
| A gift/inspiration | 128–208 | **128–176** | 1 (128), 2 (160), 10 (176), 17 (182), 11 (208) |
| B doodle-humor strips | 112–184 | **112–144** | 4 (112), 7 (112), 12 (144), 15 (176), 5 (184) |
| C graphic-memoir essay | 192–384 | **192–256** | 6 (192), 13 (248), 3 (384 outlier) |
| D graphic-medicine explainer | 32–176 | **80–176** | 8 (32–80), 14 (176) |
| E illustrated-prose idea book | 160–304 | **160–224** | 9 (160), 16 (304 outlier) |

The prompt's prior guesses ("gift 96–160? trade 192–256?") were close but not exact:
the gift band's center of gravity is 128–176 (not 96), and 192–256 holds for the
graphic-essay class only.

### 2b. Words-per-page and total word mass

| Class | Words/page band | Total word mass | Implication for authoring |
|---|---|---|---|
| A | 10–60 | **micro–light (1.5–8k)** | aphorism + scene-beat writing; every line is display text |
| B | 5–40 | **micro–light (1–6k)** | gag/beat writing; captions + hand-lettering |
| C | 60–200 | **medium–heavy (15–40k)** | genuine essay prose interleaved with art |
| D | 40–120 | **light–medium (5–20k)** | explainer prose in comic frames + endnotes |
| E | 80–300 | **medium–heavy (15–50k)** | full prose manuscript; art punctuates |

### 2c. Art density per page

| Class | Art density | Norm |
|---|---|---|
| A | 90–100% of pages carry art; ~50%+ are full-page art | art IS the page; text hand-lettered into art |
| B | 100% strip/panel; 1 strip or 1–4 panels per page | white margin frame; humor timing via panel spacing |
| C | 40–70% of page area art on art pages; text blocks alternate | drawings interrupt and pay off prose |
| D | 100% comic pages; diagrammatic inserts | body-diagram and metaphor visuals |
| E | 1 spot/diagram per 1–3 pages | chart-joke or diagram per idea beat |

### 2d. Chapter / section structure conventions

| Class | Convention | Corpus evidence |
|---|---|---|
| A | NO chapters, or 4–8 loose movements (seasons, times of day) | Boy/Mole continuous; Big Panda organized by seasons; Blooming by themes |
| B | Unchaptered strip flow, or 4–6 thematic chapters | Adulthood unchaptered; Introvert Doodles themed sections |
| C | 10–18 discrete essays / memoir arc chapters | Hyperbole 18 essays; Marbles memoir arc |
| D | Single continuous explainer + science endnotes | Anxiety Is Really Strange endnotes |
| E | 6–10 numbered principles/aspects | Kleon 10 principles; No Hard Feelings 7 workplace aspects |

### 2e. Trim, color, binding norms

- Trim clusters: **squarish small (6×6 – 8×8)** for classes B/E-compact; **6.5×8.2 – 7×9**
  for A/B/C standard; **5×7.75 – 5.9×8.25** for D/E prose-leaning. Deliberately DISTINCT
  from manga digest (5×7.5) and US comic trade (6.63×10.19) — shelving signal is
  "trade book," not "comic." (Derived; HIGH conf. on sourced trims 6×6, 6.7×8.2, 6.5×8.5, 5×7.75, 5.875×8.25.)
- Color: B&W does NOT suppress sales in this category (milk and honey B&W >6M [S11];
  Sarah's Scribbles B&W millions [S4b]; Quiet Girl B&W). Color signals the GIFT sub-format
  (watercolor/wash classes A), not commercial viability. MED conf. (derived).
- Binding: class A breakouts are HARDCOVER at $19.99–22.99 (rows 1, 2, 10, 17); classes
  B/C/D are paperback-original at $12.99–19.99; class E splits (PB idea book $14.99 /
  HC business $29). HIGH conf.

### 2f. Price bands vs. format (correlation with rank where derivable)

- **$19.99–22.99 HC gift** is where the two category-defining breakouts sit (Boy/Mole
  $22.99 [S1c]; Big Panda $19.99 [S2b]). Premium >$25 appears only on the business-shelved
  hybrid (No Hard Feelings $29 [S16]) with a lower velocity ceiling — no >$25 title in the
  corpus has a reported 7-figure unit count. MED-HIGH conf.
- **$14.99–16.99 PB** is the volume shelf for strip/doodle and B&W gift (milk and honey
  original PB class [S11]; Heart and Brain $16.99 [S12]; Illustrated Happiness Trap
  $16.95 [S14]).

---

## 3. Market signal (category level)

- **Category tide (Circana BookScan via PW):** US self-help print units **+14.7% in 2025**,
  led by *The Let Them Theory* (2.8M copies, the #1 selling book of 2025 at BookScan
  outlets); overall print market 762.4M units (+0.3%) [S18]. Self-help was a "bright spot"
  in H1 2025 [S19] after posting steep declines in H1 2024 [S20] — the category is
  hit-driven and volatile, but the 2025 tide is strongly positive.
- **Gift-illustrated ceiling is category-defining:** Boy/Mole was the #1 book of 2020 in
  the UK TCM outright [S1b] and >250K US copies within 3 months of launch [S1d]. An
  illustrated aphorism book can be the biggest book in the market, not a niche.
- **B&W poetry-gift ceiling:** milk and honey >6M global, >100 consecutive NYT weeks [S11][S11b].
- **Instagram → book is the standing acquisition pipeline** for this category: Sarah's
  Scribbles (Tumblr/Instagram → AMP, millions sold [S4b]), Introvert Doodles [S15b],
  Mari Andrew [S6], Morgan Harper Nichols [S17], Worry Lines (2 books: Ten Speed 2021,
  AMP 2024 [S21]). Publishers buy proven audiences, not proposals.
- **NEGATIVE finding — no illustrated retrofits of prose blockbusters:** search for
  illustrated/gift editions of Mark Manson's *Subtle Art* / *Everything Is F\*cked*
  found only box sets — no illustrated edition exists [S22]. The one successful retrofit
  in the corpus (*Illustrated Happiness Trap* [S14]) required a full cartoon re-authoring
  by a second creator (Aisbett), not decoration of existing prose. **Implication for
  Phoenix: born-illustrated wins; do not plan "illustrated editions" of existing prose
  catalog as the lane's mechanism.** MED-HIGH conf.

---

## 4. Recommendations per pilot cell

For each of the 5 cells in `config/manga/us_illustrated_pilot_cells.yaml`. Comp evidence
line-cited to §1 rows; confidence explicit per row.

| Cell (brand / working title) | Class | Pages (target, band) | Trim (in) | Color | Art:text | Words/page | Binding, US price | Structure | Comp evidence | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| `stillness_press` / *The Alarm Is Lying* (anxiety, doodle_humor_essay) | B | **128** (112–144) | 7 × 9 class | B&W + 1 spot color | ST 70:30 | 10–40 (total 3–5k) | PB $14.99–16.99 | 4–6 thematic chapters | rows 4, 7 (anxiety-doodle anchors, 112pp); 5 (introvert-anxiety 184pp); Worry Lines [S21] | **HIGH** — deepest comp base in corpus |
| `digital_ground` / *Notification-Free Zone* (burnout, workplace_doodle) | B (+E notes) | **144** (128–160) | 7 × 9 class | Flat color (2–4 tone) | ST 70:30 | 10–50 (total 3–6k) | PB $16.99 | 4–6 thematic chapters + micro-glossary | row 12 (Heart and Brain 144pp $16.99 [S12]); row 16 (workplace-emotions shelving crossover [S16]) | **HIGH** |
| `cognitive_clarity` / *Thought Loops: A Field Guide* (overthinking, confessional_essay) | C | **208** (192–256) | 5.5 × 8.2 – 6.5 × 8.5 | Duotone or color | HY 50:50 | 80–160 (total 18–28k) | PB $17.99–19.99 (HC $21.99 viable) | 12–16 discrete essays | rows 3 (essay hybrid ceiling [S3]), 6 (192pp, 6.5×8.5, $21.99 HC [S6]), 13 (248pp memoir [S13]) | **MED-HIGH** — class solid; word-mass target rests on estimated words/page |
| `healing_ground` / *The Midday Reset* (somatic_healing, warm_illustrated_essay) | A | **144** (128–160) | 6.7 × 8.2 | Full color (watercolor/wash) | FP 80:20 | 10–40 (total 2.5–5k) | HC $19.99–22.99 | No chapters; 4–8 time-of-day movements | rows 1 (128pp, $22.99, category #1 [S1]), 2 (160pp, 6.7×8.2, $19.99 [S2]), 17 (182pp gift [S17]) | **HIGH** — strongest breakout comps in corpus |
| `calm_student` / *Before the Exam* (exam_anxiety, ya_campus_doodle) | B (+D inserts) | **128** (112–144) | 7 × 9 class | 2-color or full color | ST 70:30 + explainer spreads | 15–50 (total 3–6k) | PB $14.99 | 4–6 chapters tracking exam arc + calm-technique spreads | rows 4 (student-age crossover readership [S4b]), 8/14 (anxiety-explainer inserts [S8][S14]), 15 [S15] | **MED** — no direct exam-anxiety illustrated-trade comp found; YA graphic wellness runs full-GN format instead (e.g. Telgemeier *Guts*), an adjacent but different format |

Cross-cell rule derived from §2/§3: none of the five cells should exceed the light word
class except `cognitive_clarity` (class C is the only researched home for medium word
mass), and only `healing_ground` should be hardcover-first.

---

## 5. Config feed-through

`config/manga/us_illustrated_pilot_cells.yaml` gains, per cell, a `format_parameters`
block sourced to this study (anchor `#4-recommendations-per-pilot-cell`) with
`provenance: RESEARCHED`, plus registry-level `format_parameters_status: RESEARCHED`
and `format_study` pointer. Schema-safety verified against the consumer
`scripts/ci/check_western_lane_format.py` (reads only `brand_id`, `topic`,
`series_plan_stub` and registry `lane`/`master_format`/cell count — additive keys pass).
`docs/US_CATALOG_PLAN.md` gains a dated addendum pointing here (edit in place, no fork).

---

## 6. Secondary: serialized illustrated wellness in Western markets (Q-MPU-03)

Short evidence capture only — the book-category study above remains the primary frame.

- **The Western wellness serial lives on Instagram/Tumblr, not on webtoon platforms.**
  Every serialized-origin comp in the corpus built its audience on Instagram or Tumblr
  strips and then collected to print: Sarah's Scribbles (Tumblr 2011 → AMP 2016 [S4b]),
  Deep Dark Fears (Tumblr → Ten Speed Press 2015, 101-comic collection + sequel *The
  Creeps* [S23]), Worry Lines (@worry__lines → Ten Speed 2021 + AMP 2024 [S21]),
  Introvert Doodles [S15b], Mari Andrew [S6], Morgan Harper Nichols [S17].
- **WEBTOON Canvas wellness self-help exists only at hobbyist scale.** Canvas search
  surfaces small educational strips (e.g. "Mental Health Matters!", 4-panel advice
  comics; "Heart Therapy: Stories of Student Mental Health") with no breakout Western
  wellness serial and no print pipeline found [S24]. Wellness content that succeeds on
  WEBTOON does so embedded in genre fiction (the `docs/US_CATALOG_PLAN.md` §2 embedded
  thesis), not as direct illustrated self-help.
- **Korean "illustrated essay" crossover validates the serial-adjacent essay format:**
  *I Decided to Live as Me* (Kim Suhyun) — an illustrated life-guide essay — sold >1M
  copies internationally and reached US trade via Penguin (Anton Hur translation) [S25].
  This is a book-format import, further evidence the category's center is book-shaped.
- **Planning-frame implication (flagged for Lane 06, not specced here):** the serialized
  frame for this lane should model an *Instagram strip cadence feeding a book collection*
  (strip = atom, book = 112–144pp collection per §2a class B), NOT webtoon episode
  framing. Episode-shaped planning contracts do not fit any comp found.

---

## 7. Confidence summary

| Section | Confidence | Weakest link |
|---|---|---|
| §1a physical params | HIGH (sourced rows) / MED (est. trims, words-page) | row 8 page count (32 vs 80 conflict) |
| §1b market signal per comp | MED-HIGH | row 6 NYT claim unverified |
| §2 norms | HIGH bands / MED word-mass + art density | words/page are estimates |
| §3 category signal | HIGH (Circana-via-PW numbers) | 2020 UK volume figures unpublished (lockdown gap) |
| §4 recommendations | HIGH ×3, MED-HIGH ×1, MED ×1 | calm_student comp gap |
| §6 serialized secondary | MED | Canvas negative finding is search-based, not exhaustive |

---

## Sources (all accessed 2026-07-24)

- [S1] OpenLibrary, ISBN 9780062976581 (HarperCollins, 128pp, 2019): https://openlibrary.org/isbn/9780062976581.json
- [S1b] The Bookseller, "Mackesy's title tops the 2020 sales chart" (Nielsen BookScan UK TCM #1 2020; >1M copies; longest-running Sunday Times hardback chart-topper; Platinum, 2020 Nielsen Bestseller Awards; 2020 UK volume figures unpublished due to lockdown reporting gaps): https://www.thebookseller.com/news/mackesys-boy-mole-fox-and-horse-tops-2020-chart-1232513
- [S1c] US list price $22.99 HC from retail listings of ISBN 9780062976581 (HPB/Walmart): https://www.hpb.com/the-boy-the-mole-the-fox-and-the-horse/P-15458546-NEW.html
- [S1d] Wikipedia, "The Boy, the Mole, the Fox and the Horse" (>250,000 US copies per Washington Post 2020-01-16; USA Today debut #20 2019-10-31; 2019 B&N + Waterstones Book of the Year; US pub HarperOne 2019-10-22; 128pp unpaginated): https://en.wikipedia.org/wiki/The_Boy,_the_Mole,_the_Fox_and_the_Horse
- [S2] S&S distribution listing + retail metadata, ISBN 9781647225124 (Mandala Publishing 2021, 160pp, 6.7 × 8.2 in): https://www.simonandschuster.com/books/Big-Panda-and-Tiny-Dragon/James-Norbury/9781647225124
- [S2b] Barnes & Noble product page (HC $19.99; shelved Self-Help & Relationships / Inspiration / Affirmations & Inspiration): https://www.barnesandnoble.com/w/big-panda-and-tiny-dragon-james-norbury/1139310650
- [S2c] S&S, Big Panda and Tiny Dragon Hardcover Journal (franchise line): https://www.simonandschuster.com/books/Big-Panda-and-Tiny-Dragon-Hardcover-Journal/James-Norbury/9798886636819
- [S3] OpenLibrary, ISBN 9781451666175 (Touchstone/S&S 2013, 384pp, 8.2 × 5.3 × 1.1 in): https://openlibrary.org/isbn/9781451666175.json
- [S4] Andrews McMeel Publishing (2016, 112pp PB): https://publishing.andrewsmcmeel.com/book/adulthood-is-a-myth/ + OpenLibrary ISBN 9781449474195
- [S4b] Wikipedia, "Sarah's Scribbles" + S&S series page (series sold millions worldwide, 20+ languages; Goodreads Choice 2016/2017/2018; Tumblr 2011 origin): https://en.wikipedia.org/wiki/Sarah%27s_Scribbles
- [S5] Andrews McMeel Publishing (2017-11-07, 184pp): https://publishing.andrewsmcmeel.com/book/quiet-girl-in-a-noisy-world/ + OpenLibrary ISBN 9781449486068
- [S6] Penguin Random House product page (Clarkson Potter 2018-03-27, 192pp, 6-1/2 × 8-1/2, $21.99 HC, categories Art; Self-Improvement & Inspiration): https://www.penguinrandomhouse.com/books/557582/am-i-there-yet-by-mari-andrew/
- [S7] OpenLibrary ISBN 9781449466008 (AMP 2015, ~103–112pp): https://openlibrary.org/isbn/9781449466008.json
- [S8] Foyles listing (32pp, £7.99) + OpenLibrary ISBN 9781848193895 (32pp, JKP 2018) — conflicts with the ~80pp comic-album class reported elsewhere for the "…Is Really Strange" series; LOW conf.: https://www.foyles.co.uk/witem/fiction-poetry/anxiety-is-really-strange,steve-haines-sophie-standing-9781848193895
- [S8b] BMA Book Awards 2018 Highly Commended — via retailer copy (Foyles/Amazon listing).
- [S9] Workman/retail metadata (2012, 160pp, 6 × 6 in, PB $14.99): https://austinkleon.com/steal/ + https://www.amazon.com/Steal-Like-Artist-Things-Creative/dp/0761169253
- [S9b] Wikipedia, "Steal Like an Artist" + Kleon site (>1M copies, 30+ languages, NYT bestseller; 10th-anniv deluxe HC): https://en.wikipedia.org/wiki/Steal_Like_an_Artist
- [S10] Hachette Book Group (Workman) listing (176pp, HC illustrated $20.00): https://www.hachettebookgroup.com/titles/elle-luna/the-crossroads-of-should-and-must/9780761184881/
- [S10b] Elle Luna, "The Crossroads of Should and Must," Medium (viral essay origin, 2014): https://medium.com/@elleluna/the-crossroads-of-should-and-must-90c75eb7c5b0
- [S11] S&S/AMP listing, milk and honey (208pp trade PB; >6M copies global; best-selling poetry book of the 21st century; >3 years on NYT list, >100 consecutive weeks): https://www.simonandschuster.com/books/Milk-and-Honey/Rupi-Kaur/9781524892876 + https://www.andrewsmcmeel.com/rupi-kaur-and-andrews-mcmeel-publishing-announce-the-release-of-a-10th-anniversary-collectors-edition-of-milk-and-honey/
- [S11b] PRNewswire, "Sales of #1 New York Times Best Seller Milk and Honey by Rupi Kaur Reach One Million Copies" (Feb 2017): https://www.prnewswire.com/news-releases/sales-of-1-new-york-times-best-seller-milk-and-honey-by-rupi-kaur-reach-one-million-copies-300399800.html
- [S12] Andrews McMeel Publishing, Heart and Brain (2015-10-20, 144pp, PB, list $16.99): https://publishing.andrewsmcmeel.com/book/heart-and-brain-the-awkward-yeti/
- [S13] Strand/PW/retail metadata (Gotham Books, Nov 2012, 248pp PB): https://www.publishersweekly.com/9781592407323
- [S13b] Graphic Medicine review of Marbles (category shelving evidence): https://www.graphicmedicine.org/comic-reviews/marbles/
- [S14] Penguin Random House product page, The Illustrated Happiness Trap (Shambhala 2014-03-11, 176pp, 5 × 7-3/4, PB $16.95, categories Self-Improvement & Inspiration; Psychology): https://www.penguinrandomhouse.com/books/234929/the-illustrated-happiness-trap-by-russ-harris-bev-aisbett/
- [S15] OpenLibrary ISBN 9781507200018 (Adams Media, 2016-12-02, 176pp, hardcover): https://openlibrary.org/isbn/9781507200018.json
- [S15b] S&S Introvert Doodles series page (Instagram origin; activity-book series spinoffs): https://www.simonandschuster.com/books/Introvert-Doodles/Maureen-Marzi-Wilson/Introvert-Doodles/9781507200018
- [S16] Penguin Random House product page, No Hard Feelings (Portfolio 2019-02-05, 304pp, 5-7/8 × 8-1/4, HC $29.00, categories Business; Self-Improvement & Inspiration; Psychology): https://www.penguinrandomhouse.com/books/564051/no-hard-feelings-by-liz-fosslien-and-mollie-west-duffy/
- [S17] Retail/bibliographic metadata, All Along You Were Blooming (Zondervan 2020, 182pp, HC; graduation-gift positioning): https://www.amazon.com/All-Along-You-Were-Blooming/dp/0310454077
- [S18] Publishers Weekly, "Print Book Sales Rose Slightly in 2025" (self-help +14.7% 2025; The Let Them Theory 2.8M copies #1 of 2025; total print 762.4M units +0.3%): https://www.publishersweekly.com/pw/by-topic/industry-news/financial-reporting/article/99417-print-book-sales-rose-slightly-in-2025.html
- [S19] Library Journal infoDOCKET / Circana, "U.S. Book Market Holds Steady in the First Half of 2025" (self-help a bright spot H1 2025): https://www.infodocket.com/2025/07/17/new-data-from-circana-bookscan-u-s-book-market-holds-steady-in-the-first-half-of-2025-results-and-highlights/
- [S20] Publishing Perspectives / Circana BookScan H1 2024 (memoir + self-help steepest adult-nonfiction declines H1 2024): https://publishingperspectives.com/2024/07/circana-bookscan-us-prints-january-june-print-market/
- [S21] Worry Lines: This Book Is for You (Ten Speed Press, 2021) + Worry Lines: You're Doing Really Well Given the Circumstances (Andrews McMeel, 2024); @worry__lines Instagram origin: https://publishing.andrewsmcmeel.com/book/worry-lines/ + https://www.worrylines.net/
- [S22] Search for Mark Manson illustrated/gift editions returns box sets only — no illustrated edition exists (negative finding): https://en.wikipedia.org/wiki/Everything_Is_F*cked
- [S23] Deep Dark Fears (Fran Krause, Tumblr webcomic → Ten Speed Press 2015, 101-comic collection; sequel The Creeps 2017): https://www.amazon.com/Deep-Dark-Fears-Fran-Krause/dp/1607748150 + https://bleedingcool.com/2015/09/29/fran-krauses-deep-dark-fears-hits-the-shelves-today
- [S24] WEBTOON Canvas mental-health search surface (hobbyist-scale strips; no breakout wellness serial found): https://www.webtoons.com/en/canvas/mental-health-matters/list?title_no=751250 (representative)
- [S25] I Decided to Live as Me (Kim Suhyun; >1M copies internationally; Penguin edition tr. Anton Hur): https://www.penguinrandomhouse.ca/books/744569/i-decided-to-live-as-me-by-kim-suhyun-translated-by-anton-hur/9780143138228 + https://www.scmp.com/lifestyle/arts-culture/article/3289179/korean-author-kim-su-hyun-being-true-yourself-her-hit-guide-gets-english-version
