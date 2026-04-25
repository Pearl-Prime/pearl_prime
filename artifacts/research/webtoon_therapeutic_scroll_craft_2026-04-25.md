# Therapeutic Scroll Craft Reference for Phoenix Omega
## Date: 2026-04-25
## Author: Pearl_Research (Creative Craft pass)
## Scope: How to make the SCROLL ITSELF therapeutic — concrete, prescriptive techniques for art directors and scriptwriters of Phoenix Omega's manga/webtoon catalog.
## Companion docs: technical-specs research, ja_JP market research, compositing/lettering research (run in parallel by other agents — this doc deliberately does NOT duplicate them).

---

## Executive Summary

**Thesis: The scroll IS the intervention.** Phoenix Omega is not making manga *about* wellness; it is making manga whose form (scroll cadence, panel weight, color, breath, silence) regulates the reader's nervous system in real time. Teachings are passengers riding on a regulating vehicle — not the vehicle itself.

This is grounded in convergent evidence from polyvagal theory (Porges 2022), somatic experiencing (Levine 1997, 2010), broaden-and-build positive emotion theory (Fredrickson 1998–2013), awe-as-vagal-tone research (Monroy & Keltner 2023), iyashikei craft (Ashinano, Urushibara, Yamazaki Kore), Ghibli's "ma" (Miyazaki via ScreenCraft), and webtoon scroll-pacing research (S-Morishita, Smythe/Lore Olympus). Each independently shows that pacing, negative space, and titrated arousal can shift autonomic state. Combine them on a vertical canvas designed for thumb-paced viewing and you get a delivery medium that downregulates by default.

**Top 5 Phoenix techniques to adopt immediately:**
1. **The Long Drop (≥1500px yohaku)** between any high-activation beat and the next narrative beat — non-negotiable somatic pendulation.
2. **The Anchor Panel** — one consistent, recurring "resource" image per series (a teacher's tea bowl, a dappled forest path, a specific window) that returns 3–5 times per episode as a ventral-vagal safety cue.
3. **The Breath Bracket** — every episode opens AND closes with a breath panel (steam, leaves, a slow exhale rendered as ふぅ), bookending the reader's arousal arc.
4. **The Soft Cliffhanger** — emotional anticipation, never tension-spike; episodes must complete the nervous-system cycle (sigh > settle), not interrupt it.
5. **The Awe-Pullback** — once per arc, a single panel that pulls back to vastness (forest canopy, sky, sea, mountain ridge); accommodates the brain into prosocial, vagally-toned, default-mode-quieting awe.

**Operating rule (the "Scroll Therapeutic Test"):** Every Phoenix episode must (a) open with a safety cue inside the first 800px, (b) titrate between activation and ground at least 3 times, (c) close with completion (exhale, settling, integration), (d) pass HRV-style end-state delta — measurable proxy: average reader's last-30-second arousal lower than first-30-second arousal. Test on real readers with HRV apps (Welltory, EliteHRV) before greenlight.

---

## §1 Internal Audit — What Phoenix already has on therapeutic craft

| Asset | Path | Status | Gap this doc fills |
|---|---|---|---|
| Therapeutic positioning across 9 markets | `artifacts/research/therapeutic_manga_wellness_market_research_2026_04_04.md` | Strong: localized framing keywords, stigma map, gap confirmation | Has WHAT (market) and WHO (audience), missing HOW (panel-level craft) |
| Genre writing styles | `artifacts/research/manga_genre_writing_styles_2026_04_04.md` | Strong: 10 genres with metrics tables, dialogue patterns, ma reference, iyashikei principles | Has prose/dialogue craft, missing scroll-pacing pixel formulas + somatic mapping |
| Bestseller decomposition | `artifacts/research/strategic_audit/02_bestseller_pattern_decomposition.md` | Strong: Frieren as proof, iyashikei commercial scale, essay manga pipeline | Missing: how Frieren's pacing decisions become reusable Phoenix techniques |
| Catalog plan | `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md` | Strong: 12 teachers × 4 markets × 12–24 series each; topic tags (anxiety, burnout, grief, social_anxiety, sleep_anxiety, somatic_healing, compassion_fatigue, etc.); style tags include cozy_iyashikei, dark_psychological, hyper_clean_cinematic, webtoon_vertical_romance, social_media_simulacra | Missing: per-teacher signature pacing/palette; per-style somatic checklist |
| Teacher matrix | `config/catalog_planning/teacher_persona_matrix.yaml` | Strong: 12 teachers with allowed engines (shame, false_alarm, overwhelm, spiral, watcher, grief, comparison), peak_intensity_limit=5 baseline | Missing: per-teacher *visual* signature; missing somatic-cue requirement per chapter |
| Manga QA rubric | `artifacts/manga/MANGA_QA_RUBRIC.md` (referenced) | Exists | Missing: scroll-therapeutic test as a gate |
| Reader promises | `artifacts/manga/MANGA_READER_PROMISES.md` (referenced) | Exists | Missing: explicit "you will exit calmer than you entered" promise + how it's delivered |
| Iyashikei craft section | inside genre styles doc §6 | Has 7 core principles (low conflict, slow time, sensory detail, repetition, seasonal anchoring, interior monologue without crisis, rest-as-progress) implicitly | Missing: each principle expressed as a *pixel-height/panel formula* |
| Brand iyashikei specs in `specs/` | none found via glob | **Missing entirely** | This doc supplies the first prescriptive iyashikei + somatic spec |

**Net assessment:** Phoenix has world-class market research and genre theory. It has genre tags applied at series level. **What it lacks is the panel-level, pixel-level, somatic-level craft layer that turns those tags into a regulating reading experience.** This document is that craft layer.

---

## §2 Iyashikei Craft, Codified for Vertical Scroll

Phoenix's genre styles doc names iyashikei with a metrics table (25–60 words/page, 25–40% silent panel, 50:50 dialogue:narration). That is the page-paradigm. Below, the *scroll-paradigm* extension.

### 2.1 The 7 iyashikei techniques translated to scroll-pixels

| Principle | Page-paradigm (existing) | Scroll-paradigm (Phoenix add) |
|---|---|---|
| (a) Low-conflict | Mild inconvenience max (Yokohama Kaidashi Kikō, Aria) | Episode arousal arc must peak ≤ 5/10. Any panel rated >5 must be followed by ≥1500px yohaku. |
| (b) Slow time | Generous white space, gentle pacing | Average vertical pixels per beat ≥ 1200px (vs. 400–600px for action webtoon). |
| (c) Sensory detail | "The way rain sounds different on tin vs. tile" | One specific micro-sensory panel per 4 beats: steam, the lip of a cup, breath fogging glass, hands wrapped on a teacup. |
| (d) Repetition-as-comfort | Same kind moments reappear | Anchor Panel: one image returns 3–5× per episode with ≤10% color shift (mirroring mindful noticing). |
| (e) Seasonal anchoring | "Ah, the hydrangeas — June already" | Per-episode environmental marker (cherry blossom, autumn ginkgo, snow on a rail) at the same scroll-position (e.g., ~30% in) for 3 consecutive episodes, then shift. |
| (f) Interior monologue without crisis | Wondering, observing, savoring | Floating narration boxes (no balloon tail) overlay nature panels, not character close-ups, 60% of the time. |
| (g) Rest-as-narrative-progress | Nothing happens — the something is the rest | Tea Beat (3 panels of steam rising, no dialogue) is a *legal* scene-end; not "filler". |

### 2.2 Frieren as the 2024 commercial proof — what to reuse

Frieren's Japan 2024 sales jumped +99% YoY to ~5M (Oricon ranking year), executing slow-paced, grief-shaped iyashikei-adjacent fantasy ([CBR](https://www.cbr.com/frieren-season-2-ruined-the-manga-perfect-changes/), [Crunchyroll Features Oct 2024](https://www.crunchyroll.com/news/features/2024/10/29/frieren-beyond-journeys-end-processing-grief), [FandomWire](https://fandomwire.com/frieren-beyond-journeys-end-needs-its-excruciatingly-slow-pacing-for-a-simple-reason/)). What it does:
- Quiet frustration carries via extended silences and meaningful glances (not dialogue).
- Grief is rendered as elapsed time, not as monologue. Phoenix's `omote` (grief teacher) and `ren_ashford` series should adopt: render grief as *elapsed scroll distance + small object permanence*, not exposition.
- Pacing allows gaps between intense scenes "similar to Ghibli movies" — Miyazaki's "ma" applied serially. Phoenix translation: every emotional reveal earns ≥2000px of yohaku before any successor beat.

### 2.3 Yokohama Kaidashi Kikō — the canonical recipe

Hitoshi Ashinano devoted whole chapters to brewing coffee, taking photographs, repairing a model engine, with only a few lines of dialogue, sometimes with long stretches of pure graphic content ([SF Encyclopedia](https://sf-encyclopedia.com/entry/yokohama_kaidashi_kiko), [TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/Manga/YokohamaKaidashiKikou), [Wikipedia](https://en.wikipedia.org/wiki/Yokohama_Kaidashi_Kik%C5%8D)). Three reusable mechanics:
1. **The Domestic Ritual Chapter** — entire episode about one small task done attentively. Phoenix: per-series, at least 1-in-7 episodes follows a teacher doing one small task end-to-end (ahjan tying robes, junko folding cloth, master_feung sweeping a courtyard, omote pressing leaves).
2. **The Photograph Not Taken** — Alpha looks but rarely shoots because the contemplation itself is the value. Phoenix: protagonist notices, does not capture; teacher reflects this back ("You don't need to fix it to honor it").
3. **The Idle Travel** — moped wanderings without destination. Phoenix's teacher walks-with-protagonist scenes default to "walking nowhere," not "walking to."

### 2.4 Mushishi — episodic completion as nervous-system completion

Yuki Urushibara's *Mushishi* uses self-contained one-arc episodes; each story closes the loop. This is Phoenix's structural mandate: **episodic, never serialized cliff-on-cliff**. A reader who only reads one episode in their life must exit settled. Cf. Levine on completion (§4): incomplete trauma response is what *causes* dysregulation; episodes must allow nervous-system completion.

### 2.5 Studio Ghibli's *ma* — the cinematic ancestor

Miyazaki, demonstrating on camera by clapping: "The time in between my clapping is ma. If you just have non-stop action with no breathing space at all, it's just busyness" ([ScreenCraft](https://screencraft.org/blog/hayao-miyazaki-says-ma-is-an-essential-storytelling-tool/)). The Spirited Away train scene — Chihiro almost completely still while the train moves — is the canonical example. The audience is invited to feel "being just a small part of a big world" ([Medium / Nayeon Park](https://medium.com/@nayeonpark/ma-the-best-moments-in-a-studio-ghibli-film-are-silent-27210e215b21)). **Pixel translation:** A "Miyazaki ma" on a 1600×4600px scroll canvas equals approximately **2400–3200 vertical pixels** of either pure environment (no character, no text) or character-still-in-environment, no dialogue, with optional small SFX (wind, distant bird).

---

## §3 Vertical-Scroll-as-Breath — pacing-by-pixel

Phoenix's recommended canvas is the industry-standard 1600×4600px webtoon strip ([Clip Studio / Art Rocket](https://www.clipstudio.net/how-to-draw/archives/157055), [S-Morishita Studio](https://www.s-morishitastudio.com/vertical-scrolling-webtoon-format/)). Below, beats translated to pixels with somatic intent.

### 3.1 The pixel-to-emotional-duration table

| Scroll gap | Reader experience | Somatic effect | Phoenix use |
|---|---|---|---|
| 50–100px | Quick continuation, same moment | Neutral; thumb moves smoothly | Tight dialogue exchange |
| 150–300px | Scene breath, minor beat | Mini exhale | Standard transition between two beats |
| 400–600px | Major dramatic pause | Slight orienting response (head still, eyes hold) | Reveal moment, mild "thumb stop" |
| 800–1200px | Sustained pause | Settling; reader's breath naturally slows | Pre-mentor-line beat; pre-truth beat |
| 1500–2000px | Long Drop (Phoenix term) | Parasympathetic tilt; one slow breath fits inside the scroll | After any high-arousal beat; after a difficult emotional reveal |
| 2400–3200px | Miyazaki ma | Two full breaths; reader frequently disengages thumb, looks up, back | Once per episode, mid-arc; awe-adjacent beats |
| 3500px+ | Trance-adjacent / risk of bounce | Some readers exit; others enter near-meditative state | Use only as deliberate finale of a contemplative episode (e.g., last beat before episode end) |

### 3.2 The 8-second rule and how to break it intentionally

Webtoon attention research and the practitioner consensus (S-Morishita; Smythe on Lore Olympus pacing; Matt Reads Comics) converge on: **readers scroll past static images in roughly 2 seconds; complex panels need motion, narrative pull, or a "thumb stop" anchor to slow them**. For purely-still therapeutic panels, the slowing is bought by:
1. **Visual anchor + negative space** (a single small symbol — a teacup, a candle, a breath cloud — in a sea of yohaku).
2. **Repetition with micro-shift** (same image 3–5×, color or value shifts ≤10% between iterations; reader literally slows to detect change → mirrors mindful noticing).
3. **Vertical sound** (onomatopoeia rendered in a soft hand at the edge — ふぅ for breath, さら for breeze — letting the eye trace a sound vertically rather than read horizontally).
4. **Color drift** (background tone shifts from cool to warm across 3 panels — reader feels a temperature change without conscious awareness).
5. **The wait-loaded panel** ("the kettle hasn't whistled yet" — a panel where something is implied to be about to happen but doesn't, multiple beats — reader re-scrolls to check).

### 3.3 Lore Olympus as a non-iyashikei case study in pacing-by-pixel

Smythe explicitly designs Lore Olympus around the vertical scroll's elasticity: panels expand and condense to control pace ([Wikipedia](https://en.wikipedia.org/wiki/Lore_Olympus), [The Mary Sue](https://www.themarysue.com/lore-olympus-on-webtoon/), [All About Romance](https://allaboutromance.com/book-review/lore-olympus-by-rachel-smythe/)). Color symbolism is deliberately therapeutic-adjacent: Persephone's **pink for warmth and kindness**, Hades' **navy for cold and depth**, Hera's **weary yellow**, Zeus's **pompous purple** ([Oreate AI Blog](https://www.oreateai.com/blog/the-colorful-symbolism-of-persephone-in-lore-olympus/a0c7c5e565245d33ec21e32dd8342118)). Phoenix learning: **assign each teacher a 2–3 color signature** that telegraphs their nervous-system register before any text is read.

### 3.4 The "thumb stop" — designing a therapeutic stop, not a shock stop

Mainstream webtoons use thumb stops for shock (a face reveal, a body reveal, a violence beat). Therapeutic webtoons use them for **safety-cue reveals**: a hand reaching to steady another, a window opening to dappled light, a teacher quietly arriving. Phoenix recommendation: per episode, ≥3 thumb stops, ALL of which must be safety-cue stops, not threat-cue stops.

---

## §4 Polyvagal Theory Applied to Panel Design

Stephen Porges' Polyvagal Theory ([Polyvagal Institute](https://www.polyvagalinstitute.org/whatispolyvagaltheory), [PMC: Polyvagal Theory: A Science of Safety, 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9131189/), [Frontiers 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12479538/)) describes three autonomic states:
- **Ventral vagal** — safe, social, present, available for connection.
- **Sympathetic** — fight/flight, mobilized.
- **Dorsal vagal** — freeze/collapse, shutdown.

The relevant operational construct is **neuroception**: continuous nonconscious evaluation of safety cues from face, voice, gesture, posture ([Frontiers 2024 — creative arts and polyvagal theory](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1382007/full)). Manga panels can broadcast safety cues. Phoenix's design rule: **the page itself should test as ventral-vagal-cued by neuroception**.

### 4.1 Panel-level safety cues (broadcast ventral vagal)

| Cue | Rendering | Why it works (Porges) |
|---|---|---|
| Soft eye-contact close-up | 3/4 face, eye-area only, lashes soft, slight squint of warmth | Activates Social Engagement System via face neuroception |
| Prosodic bubble shape | Bubble outline gentle wave/curve (not jagged), tail soft, font rounded | Visual proxy for prosodic voice |
| Open hands | Palms visible, fingers relaxed, no clench | Posture cue: non-defensive |
| Ground-on-earth | Feet/sandals/tabi on grass, wood, tatami; weight visible | "I am grounded" cue mirrors vagal tone |
| Low POV (sitting/cushion view) | Camera 80–110cm off ground | The "view from the cushion" — Zen + therapeutic; reduces threat geometry |
| Shared breath | Two characters in same air, steam from both their cups | Co-regulation cue |
| Predictable panel rhythm | Consistent panel widths within an episode block | Predictability is itself a safety cue |
| Warm-edge palette | Cream off-white background, ochre or peach tint at edges | Limbic system reads warmth as safety (Color Institute, [Theraluxe Home Wellness](https://theraluxe.ca/how-color-psychology-impacts-relaxation-recovery-enhancing-wellness-spaces-through-thoughtful-design/)) |

### 4.2 Sympathetic-deactivating moves (down-regulating mobilization)

- **Slow zoom-out** (3–4 panels widening from face to room to building to sky) — mirrors orienting response that ends fight/flight.
- **Breath panel** (literal: ふぅ rendered, chest rising, shoulders dropping) — cues the reader to mirror.
- **Weighted body language** (character settles heavier into chair / floor across 3 panels) — somatic discharge.
- **Foot-to-earth panel** (close-up: bare foot or sandal touching grass / floorboard) — the ground exists.
- **The settling sigh** — final panel of an arc shows shoulders dropping or hand unclenching; SFX optional.

### 4.3 What NEVER to do (would breach neuroception)

- **Hard-edged jagged bubbles** outside of explicitly-titrated activation beats.
- **Top-down high-angle "looking down" frames** of the protagonist when they are vulnerable (reads as predator POV).
- **Cool fluorescent palettes** during teaching beats (reads as clinical / institutional / unsafe).
- **Aggressive cliffhangers** — these are sympathetic activation; banned at episode-end in Phoenix.
- **Surprise loud SFX** with no buildup — neuroception flips to threat in <300ms; ruins the regulating arc.

### 4.4 Co-regulation: the dyad as the engine

Polyvagal theory: humans co-regulate via dyads broadcasting and receiving safety cues ([Polyvagal Institute](https://www.polyvagalinstitute.org/whatispolyvagaltheory)). Phoenix manga is a dyad: **teacher-character** + **reader**. Therefore the teacher's face, voice (font), gesture, and posture are *the regulator*. If the teacher is drawn dysregulated (tight jaw, jagged speech bubble, narrowed eyes) the reader cannot regulate. Rule: **Teachers must be drawn ventral-vagal in 90%+ of their panels.** The 10% exception is when the teacher is briefly modeling their own pendulation (so the reader sees a regulated nervous system *recover* — itself a teaching).

---

## §5 Somatic Experiencing in Story Structure

Peter Levine ([Ergos Institute SE overview](https://www.somaticexperiencing.com/somatic-experiencing), [Sarah Ross PhD: Resourcing, Pendulation, Titration](https://sarahrossphd.com/resourcing-pendulation-titration-practices-somatic-experiencing/), [The Awake Network on Levine's pendulation lesson](https://www.theawakenetwork.com/peter-levine-pendulation-trauma/)) — translated to scroll.

### 5.1 Pendulation — the spine of every Phoenix episode

Pendulation = natural oscillation between contraction and expansion, between dysregulated and regulated. **Episode design mandate:** an episode's arousal graph must show ≥3 oscillations between activation peaks (sympathetic charge) and ground troughs (ventral vagal safety). Never a flat line. Never a single accelerating ramp. The scroll's vertical axis IS the somatic axis.

Concrete pattern (a 14-beat episode): G – G – A1 – G – A2 – G – A3 – G – Awe – G – Integration – G – Bracket-close-breath. Where G = ground (resource panel), A = activation, and amplitude(A1) < A2 ≤ A3.

### 5.2 Titration — small doses, never overwhelm

Levine: trauma is "too much, too fast, too soon." Phoenix rule: **no high-arousal beat held more than 2 panels** (≤600px scroll) before returning to a ground beat (≥800px scroll). Activation:Ground vertical ratio per episode must be ≤ 1:2.5.

### 5.3 Resourcing — the Anchor Panel

Resource = "any internal or external thing that brings a sense of safety, calm, support" (Sarah Ross PhD). Apply per-series: a designated Anchor Image returns 3–5× per episode. Recommended Phoenix anchors per teacher (see §18 for full table):
- ahjan: dappled forest path, stillness press logo on a worn book.
- joshin: a single round black cushion (zafu) on tatami.
- junko: water reflection in a stone basin (chōzubachi).
- maat: a feather on a brass scale.
- master_feung: a hanging mountain ridgeline, a tea kettle on coals.
- master_sha: lantern light on a quiet bedroom floor.
- master_wu: a pine bough against rocky cliff.
- miki: an open notebook + a phone face-down beside it.
- omote: pressed leaves between book pages.
- pamela_fellows: a window with sheer curtains in late sun.
- ra: the rim of a sun coming over a desert horizon.
- sai_ma: a brass diya / oil lamp + a single jasmine.

The reader learns the anchor across episodes 1–3 and unconsciously scans for it. By episode 7+, the anchor's mere presence shifts arousal downward in <2 seconds — **classical conditioning of safety, deliberately constructed**.

### 5.4 Tracking sensation — body-awareness as story device

Phoenix's interior monologue rule: when narration tracks the protagonist's interior, it tracks **bodily sensation** as often as it tracks thought. Pat Ogden / Janina Fisher's sensorimotor approach distinguishes cognitive, emotional, and *sensorimotor* processing ([Norton: Sensorimotor Psychotherapy](https://wwnorton.com/books/9780393706130), [Fisher PDF](https://janinafisher.com/wp-content/uploads/2023/03/sensorimotor-psychotherapy-trauma.pdf)). Default narration ratio: 40% thought / 30% emotion-named / **30% sensation-named**. Sensation-named examples:
- "My shoulders found themselves up by my ears again."
- "There was a thread of warmth at the base of my throat."
- "My right hand wouldn't open."
- "The air at my hairline cooled when I exhaled."

This trains the reader to track sensation in their own body in parallel — interoceptive co-training (cf. Mindfulness, Interoception, and the Body, [PMC 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6753170/)).

### 5.5 Discharge / completion — episode-ending mandate

Levine: incomplete trauma response stays incomplete and re-fires; nervous-system completion is the goal of healing. Phoenix's translation: **every episode ends in a completion beat, never a cliffhanger-shock.** Acceptable closes: a sigh, an exhale rendered as ふぅ, a hand finally opening, a held breath let go, a settling, a tea sip finished. Forbidden closes: gasps, freeze-frame mid-fall, betrayed-look reveals, "to be continued" with a threat. (Soft cliffhangers — see §13 — are still permitted: emotional anticipation without arousal spike.)

### 5.6 The Pendulation Pair — Phoenix's named technique

Whenever the script needs to depict trauma processing, the pair runs: **one high-activation panel paired with one low-activation panel within a 5-panel window.** The activation panel is held briefly (≤400px). The ground panel is held long (≥1200px). The reader's nervous system experiences titration *as a reading rhythm*. This is the most important named technique in this document.

---

## §6 Positive Psychology Applied — PERMA, savoring, awe, flow

Seligman's PERMA model + Fredrickson's broaden-and-build + Keltner's awe + Csikszentmihalyi's flow = a positive-emotion engine for episode design.

### 6.1 PERMA-coverage rule

Each episode activates ≥1 PERMA element ([Positive Psychology: Broaden-and-Build](https://positivepsychology.com/broaden-build-theory/)):
- **P**ositive emotion (joy, contentment, awe, gratitude, amusement, hope, interest, inspiration, pride, love — Fredrickson's top 10).
- **E**ngagement (flow — protagonist absorbed in something).
- **R**elationships (a moment of co-regulation between two characters).
- **M**eaning (a teacher reflects something back as significant).
- **A**ccomplishment (a small task done attentively — a tea brewed, a letter finished).

Across a 14-episode series, all 5 PERMA elements must appear at least twice, and *positive emotion + relationships + meaning* must appear in every episode.

### 6.2 Broaden-and-build, weaponized for the open and close

Fredrickson: positive emotions broaden cognitive scope and build resources over time ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3122271/), [psu.pb.unizin.org](https://psu.pb.unizin.org/psych425/chapter/broden-and-build-theory-of-positive-emotions/), [Fredrickson 2004 PDF on gratitude](https://peplab.web.unc.edu/wp-content/uploads/sites/18901/2018/11/fredrickson2004.pdf)). The reader's cognitive scope literally widens after a positive-emotion panel. Phoenix design: **frame every episode with a positive-emotion bracket** — the open + close. Activation/grief content sits inside the bracket. The bracket's broadening effect makes the activation content metabolizable.

### 6.3 Savoring panels

Fredrickson on contentment: "sparks the urge to savour and integrate." Phoenix savoring panels: extended scroll on small joys — steam from tea, dappled light, a friend's laugh, the lift of bread crust, the smell of rain on hot stone. Recommend ≥1500px held on each savoring panel, frequently with the protagonist literally still (the reader stills with them).

### 6.4 Strength-spotting — the mentor reflects back

Standard mentor failure mode: oracle delivers wisdom downward. Phoenix's required mode: **mirror, not oracle**. The teacher names the protagonist's strength back to them. Ratio: the teacher describes the protagonist 3× more often than the teacher describes themselves. Lines like "You stayed when most would have left" outnumber lines like "When I was your age I learned…"

### 6.5 Gratitude practice as closing reflection

Per series, ~1-in-3 episodes closes with the protagonist naming what they are grateful for — internal narration, no exposition. Tone: specific, small, sensory. ("The way the cold of the door handle never hurts when I'm holding tea.") Cf. Fredrickson 2004.

### 6.6 Awe — Phoenix's secret weapon

Monroy & Keltner 2023, *Awe as a Pathway to Mental and Physical Health* ([SAGE journal](https://journals.sagepub.com/doi/10.1177/17456916221094856), [Templeton Awe paper](https://www.templeton.org/wp-content/uploads/2018/08/Awe-White-Paper_distribution.pdf)): awe = perceived vastness + need for accommodation; engages five processes (neurophysiology shifts, diminished self-focus, prosocial relationality, social integration, heightened meaning); **linked to increased vagal tone** and reduced default-mode-network activity. This is the single most powerful single-panel technique available to Phoenix.

**The Awe-Pullback panel.** Required at least once per series-arc; ideally once per episode for nature-leaning teachers (ahjan, master_feung, ra, omote). Composition: pull-back to vastness (forest canopy, mountain ridge, sea horizon, night sky, desert dune sea). Scale cue: the protagonist (or her hand, or her sandal) tiny in frame. Hold ≥2400px. No dialogue. This panel is not a pretty break — **it is the most regulating intervention available on a phone screen.**

### 6.7 Flow — the protagonist's vicarious flow becomes the reader's

Csikszentmihalyi: flow = challenge–skill match, clear goals, immediate feedback ([Wikipedia: Flow](https://en.wikipedia.org/wiki/Flow_(psychology)), [Springer 2024 challenge-skill flow analysis](https://link.springer.com/article/10.1007/s10902-024-00846-4)). Per series, ≥2 episodes feature the protagonist in vicarious flow (calligraphy, cooking, gardening, sport, instrument). The reading itself can drift toward flow because the absorbed protagonist + slow scroll + no narrative urgency together meet challenge–skill match for the reader (mild aesthetic challenge at exactly skill-level).

---

## §7 Japanese Aesthetic Principles — applied vocabulary

For each, this section gives: definition, scroll application, cited example.

### 7.1 間 Ma — meaningful empty space/time
- **Definition:** Pauses and intervals that give form to experience ([dans le gris on ma](https://danslegris.com/blogs/journal/ma), [Deeper Japan](https://www.deeperjapan.com/deeper-views/ma-and-modern-minimalism), [The Mindful Word](https://www.themindfulword.org/empty-space/)). McCloud noted that manga's aspect-to-aspect transitions reflect a culture that values "being there over getting there" ([ImageTexT — Construction of Panels (Koma)](https://imagetextjournal.com/the-construction-of-panels-koma-in-manga/)).
- **Scroll app:** ≥2400px of either pure environment or character-still-in-environment, no dialogue. Once per episode minimum for iyashikei series.
- **Example:** Ghibli's Spirited Away train scene; Yokohama Kaidashi Kikō's coffee chapter.

### 7.2 余白 Yohaku / 余白の美 Yohaku no bi — beauty of the unfilled
- **Definition:** The blankness celebrated for itself; not background, but margin where form and emptiness are in mutual balance ([dans le gris on yohaku](https://danslegris.com/blogs/journal/japanese-aesthetics-of-space-ma-yohaku-no-bi-and-the-art-of-subtraction), [Kogei Standard](https://www.kogeistandard.com/insight/serial/editor-in-chief-column-kogei/ma-yohaku/), [japanese-aesthetics.com on yohaku](https://www.japanese-aesthetics.com/article/theEssenceOfJapan/yohaku)).
- **Scroll app:** Per episode, sustain ≥30% of total vertical pixels as yohaku (pure white/cream/parchment with no panel content). Counts include both inter-panel gutter and intra-panel breath.
- **Example:** Frieren's silent walking-through-grass spreads.

### 7.3 物の哀れ Mono-no-aware — pathos of things
- **Definition:** Bittersweet awareness of impermanence; cherry blossoms beautiful *because* they fall ([Stanford Encyclopedia: Japanese Aesthetics](https://plato.stanford.edu/entries/japanese-aesthetics/), [Japanese Aesthetics: The Mono No Aware](https://www.ipl.org/essay/The-Importance-Of-The-Mono-No-Aware-PCA7FGAWU), [Eastern Illinois Studies on Asia: Wabi-Sabi, Mono no Aware, and Ma](https://castle.eiu.edu/studiesonasia/documents/seriesIV/2-Prusinkski_001.pdf)).
- **Scroll app:** Use for grief, transition, change-of-life, or seasonal episodes. Tonal palette: autumn ochre + spring green together inside one episode (passing seasons). Pair: one frame of a thing in bloom, one frame of the same thing fading — within 4 beats.
- **Example:** Frieren's grief processing; omote's pressed-leaves anchor.

### 7.4 侘寂 Wabi-sabi — beauty in imperfection and impermanence
- **Definition:** "Imperfect, impermanent, incomplete"; things in bud or in decay more evocative than things in full bloom (Stanford Encyclopedia; [Medium: Eight elements of Japanese aesthetics](https://medium.com/swlh/using-elements-of-japanese-aesthetics-ed0c2e07ec0e); Leonard Koren, *Wabi-Sabi for Artists, Designers, Poets & Philosophers*, 1994).
- **Scroll app:** Render textures with imperfection — a crack in a teacup, fraying tatami edge, a slightly chipped bowl — and let the camera linger. The protagonist's recovery is wabi-sabi: incompletely healed is the right end-state, not "fully healed."
- **Example:** Yokohama Kaidashi Kikō's quiet decay aesthetic; Mushishi's worn cloth.

### 7.5 幽玄 Yūgen — profound mystery, half-glimpsed
- **Definition:** Literally "dimness"; mythic-feeling depth that resists capture; image makes its point with graceful subtlety, not confrontation (Stanford Encyclopedia; Hermitary on yūgen).
- **Scroll app:** Use for spiritual or numinous beats — the teacher's tradition referenced obliquely (mist, shrine roof half-seen, calligraphy from behind a sliding door). Resist the urge to explain. Lower contrast, more tonal greys, single light source.
- **Example:** Mushishi's Mushi sequences; Mononoke Hime's forest-spirit beats.

### 7.6 無 Mu — emptiness/nothingness
- **Definition:** Buddhist concept of no-thing-ness, used in Zen koans (Mu! the famous reply).
- **Scroll app:** The single pure-white spread. Once per series, an entire panel-equivalent vertical (≥3500px) of nothing — no content, scrolled through. It reads as audacious; it is also the most somatic-resourcing panel possible. Pair with post-anchor settling.
- **Example:** Joshin (zen-koan teacher) is the natural home; *The Anchor* (ahjan series #21) episode 12 is a candidate location.

### 7.7 間合い Maai — interval/distance
- **Definition:** Martial-arts concept of correct distance between bodies; correct spacing in time; right interval ([dans le gris on ma](https://danslegris.com/blogs/journal/ma)).
- **Scroll app:** Panel-to-panel spacing; teacher-to-protagonist spacing within frames. The teacher should occupy correct distance: not so close the reader feels invaded (sympathetic), not so far the reader feels abandoned (dorsal). 1–1.5 character-widths physical separation in 2-shot frames is the sweet spot.
- **Example:** master_wu (martial teacher) embodies maai literally; all other teachers use it metaphorically.

---

## §8 Zen / Contemplative-Art Principles for Panel Composition

### 8.1 Sumi-e — single-stroke ink, three-element composition

Sumi-e principles (asianbrushpainter.com, [Sakuraco](https://sakura.co/blog/sumi-e-in-japan-the-development-of-ink-wash-painting), [Wikipedia: Ink wash painting](https://en.wikipedia.org/wiki/Ink_wash_painting), [Japan Objects](https://japanobjects.com/features/sumie)):
- **One stroke per mark.** No touch-ups. Phoenix translation: hand-drawn line work allowed to keep its commitment-marks; do not over-clean. Imperfection is wabi-sabi (cf. §7.4). For AI-assisted line, prompt models to preserve confident single-pass ink quality, not over-rendered detail.
- **Three-element composition** (heaven–earth–human): three organizational tiers per panel (sky/canopy, mid-ground, foreground figure or object). Phoenix translation: nature-foregrounded scene panels follow the three-tier rule; teacher-foreground portrait panels follow it less strictly.
- **Asymmetric balance.** Buddhist correspondences: heaven/earth, man/nature, gravity/lightness, fullness/emptiness ([Asian Brushpainter](https://www.asianbrushpainter.com/blogs/kb/the-aesthetics-of-ink-and-wash-painting)). Default Phoenix panel composition: 1/3 figure, 2/3 yohaku (rule-of-thirds with bias toward emptiness).
- **Negative space encourages viewer imagination.** Reader supplies what's not drawn — therapeutic recruitment of the reader's nervous system as participant.

### 8.2 The view from the cushion

Zen practice often happens from a low seated position (zafu, tatami). When teaching beats happen, the camera default for Phoenix is **120cm or below ground** — the reader sees the world from a sitting / kneeling height. Effects: humility, gentleness, predator-removal (no top-down angles), legitimacy of stillness.

### 8.3 Tea-ceremony slowness

Chanoyu (tea ceremony) consists of attentive small gestures performed slowly. Phoenix's "Tea Beat" technique (see §16) is a literal application; broader principle: teaching scenes should embody a chanoyu pace — every gesture given its full duration, no compression.

### 8.4 Japanese garden composition principles

Karesansui (dry rock gardens) use: asymmetric balance; borrowed scenery (shakkei — distant mountain enters the frame); sand patterns as still-rhythm. Phoenix translation: episodes set partially outdoors should pull a "borrowed" element from background to mid-ground (a distant temple roof, a far hill, a far-off bell sound rendered as a ghost SFX) — anchoring the small scene inside a larger world.

### 8.5 References
- D.T. Suzuki, *Zen and Japanese Culture*, Princeton/Bollingen, 1959 (rev. ed.).
- Shunryu Suzuki, *Zen Mind, Beginner's Mind*, Weatherhill, 1970.
- Stephen Addiss, *The Art of Zen: Paintings and Calligraphy by Japanese Monks 1600–1925*, Harry N. Abrams, 1989.

---

## §9 Scrollytelling Lessons from Outside Manga

The non-manga scrollytelling field offers transferable mechanics. From [Shorthand: Scrollytelling examples](https://shorthand.com/the-craft/scrollytelling-examples/index.html), [Cornermindscape: The Snow Fall Effect](https://cornermindscape.com/snow-fall-effect-parallax-storytelling-web/), [Maglr: 10 best scrollytelling examples](https://www.maglr.com/blog/best-scrollytelling-examples), and [LinkedIn: Snow Fall and the birth of UX 2.0](https://www.linkedin.com/pulse/snow-fall-birth-ux-20-scrollytelling-so-much-more-bill-shander):

### 9.1 NYT *Snow Fall* (2012) — the founding object
- Multimedia triggered by scroll position; let each era "breathe" by using visual transitions to signal time shifts.
- Phoenix takeaway: position-triggered subtle motion (a leaf falling once across 1500px, a candle flicker that pulses once at scroll-anchor 60%) — used sparingly — is more therapeutic than narratively necessary motion. Each episode gets ≤2 subtle scroll-triggered animations on platforms that support them.

### 9.2 The Pudding
- Pacing-by-letting-each-era-breathe.
- Phoenix takeaway: in retrospective episodes (a teacher's youth, a memory arc), each life-era gets its own pacing block visually distinguished by small palette shift, not text label.

### 9.3 Polygon long-form features
- Long-form scrollytelling that interleaves narrative and informational beats without breaking flow.
- Phoenix takeaway: when teachings are inserted (the polyvagal explanation, the breath instruction), they ride the same scroll cadence — never "now we explain"; always embedded in a panel's narration overlay.

### 9.4 Apple iPhone product pages
- Commercial mastery of scroll pacing — scroll-triggered crossfades, elastic pacing, sticky elements during a "moment."
- Phoenix takeaway: the **sticky-anchor**: when a teaching is delivered, the teacher's portrait can sticky-pin to the right edge for 2–3 panels of student response while the student panels scroll under it. (Platform-dependent; use only where supported, e.g., Naver Webtoon's permitted overlays.)

### 9.5 Robin Sloan tap essays
- Each scroll/tap delivers exactly one new line. Pacing is *enforced*.
- Phoenix takeaway: in deeply contemplative episodes, allow exactly one beat per visible screen height (~700–900px on phone). Forces breath cadence.

---

## §10 Mindfulness-Based Principles in Media

### 10.1 Kabat-Zinn / MBSR
Mindfulness = "awareness that arises through paying attention, on purpose, in the present moment, non-judgmentally" ([Mindful: Jon Kabat-Zinn Defining Mindfulness](https://www.mindful.org/jon-kabat-zinn-defining-mindfulness/), [MBSR Training: Body Scan](https://mbsrtraining.com/mindfulness-body-scan-by-jon-kabat-zinn/), [Wikipedia: MBSR](https://en.wikipedia.org/wiki/Mindfulness-based_stress_reduction)).

Phoenix translation:
- **The Body Scan Episode** — once per series, an episode follows a teacher guiding a body scan. The scroll itself moves toe-up. Pixel allocation: 200–400px per body region, named in narration, accompanied by an interior-sensation panel.
- **Three-minute breathing space → three-minute scroll** — once per series, an episode is exactly the length that takes ~3 minutes to scroll meditatively (≈18,000–22,000px depending on density). Minimal text. Used as reset episode.
- **Mindful seeing as panel rule** — instead of "this happened, then this happened," panels of "this is here" — present-moment notice without progression. Iyashikei is mindful seeing in genre form.

### 10.2 Tara Brach's RAIN model
Recognize, Allow, Investigate, Nurture ([Tara Brach RAIN resources](https://www.tarabrach.com/rain/), [Mindful: Tara Brach RAIN](https://www.mindful.org/tara-brach-rain-mindfulness-practice/)). Phoenix narrative arc template for any episode handling a difficult emotion:
1. **Recognize** — protagonist names what is happening (1–2 panels of interior monologue).
2. **Allow** — protagonist stops fighting it; teacher models allowing.
3. **Investigate** — sensation tracking; "where is this in my body?"
4. **Nurture** — anchor panel; self-compassion; a hand on a chest; a teacher saying "of course this is here."

This four-beat arc is internally pendulating (titration via slowing) and ends in nurture (resourcing). It is the cleanest emotional structure available for therapeutic webtoon episodes.

### 10.3 Body scan adapted to scroll
The classic body scan moves toe-to-head (or vice versa) systematically ([Palouse Mindfulness Body Scan PDF](https://palousemindfulness.com/docs/bodyscan.pdf)). On a 4600px tall canvas, the scroll's vertical axis maps directly to the body's vertical axis — a literal somatic geometry. Phoenix can construct an episode where scrolling down = scanning down the body. Reader's hand-thumb-eye motion mirrors the inward attention.

---

## §11 Trauma-Informed Storytelling

Centered on van der Kolk, *The Body Keeps the Score* (Penguin/Viking, 2014; bestseller in 36 languages — [Wikipedia](https://en.wikipedia.org/wiki/The_Body_Keeps_the_Score)); Pat Ogden & Janina Fisher, *Sensorimotor Psychotherapy: Interventions for Trauma and Attachment* (Norton, 2015 — [Norton](https://wwnorton.com/books/9780393706130)); Daniel Siegel's window of tolerance ([Psychology Tools: Window of Tolerance](https://www.psychologytools.com/resource/window-of-tolerance), [Khiron Clinics](https://khironclinics.com/blog/understanding-the-window-of-tolerance/), [NICABM on Window of Tolerance](https://www.nicabm.com/trauma-how-to-help-your-clients-understand-their-window-of-tolerance/)).

### 11.1 Window of tolerance — never breach the reader's window

Trauma narrows the window. A trauma-informed reader reads with a smaller available range. **Phoenix design rule:** content should be authored to the *narrowest* expected reader window. Practical:
- Never depict graphic violence (panels, no exception in iyashikei/healing imprints).
- Never use sudden loud SFX without buildup.
- Avoid claustrophobic panel structures during trauma-related themes (no compressed multi-panel grids on grief or panic episodes — those need yohaku).
- Use content warnings on episodes touching trauma directly. Phoenix CW format: pre-cover panel, teacher's voice, explicit, soft: "This episode looks at [topic]. It moves slowly. You can stop and come back."

### 11.2 Triggers to avoid

- Graphic violence; suicide depiction (per ko_KR cultural sensitivity; per global trauma-informed standards).
- Sudden high-arousal panels without titration buildup.
- POV-from-above (predator angles) of vulnerable protagonists.
- Saturated reds without therapeutic intent.
- Sustained dark/heavy screentone past 3 panels in trauma episodes.

### 11.3 Rupture and repair as canonical narrative arc

Relational therapy: rupture (a breach in connection) followed by repair (re-attunement). This is a healthier model than victory-defeat for therapeutic series. Each multi-episode arc within a Phoenix series should include at least one rupture-and-repair cycle (teacher and protagonist briefly miscommunicate; both find their way back; the repair is the meaning).

### 11.4 Sensorimotor processing as panel logic

Ogden/Fisher distinguish cognitive, emotional, and sensorimotor levels. Phoenix's narration layer should sometimes drop *below* the cognitive into the sensorimotor — pure sensation captioning, no thinking, no feeling-naming. Example: instead of "I felt afraid," the narration reads "My breath went shallow. My fingertips went cold." This is trauma-informed storytelling at the linguistic level.

### 11.5 References (for the bestseller bibliography)
- Bessel van der Kolk, *The Body Keeps the Score: Brain, Mind, and Body in the Healing of Trauma* (Penguin, 2014).
- Pat Ogden & Janina Fisher, *Sensorimotor Psychotherapy: Interventions for Trauma and Attachment* (Norton, 2015).
- Janina Fisher, *Healing the Fragmented Selves of Trauma Survivors* (Routledge, 2017).
- Peter A. Levine, *Waking the Tiger: Healing Trauma* (North Atlantic, 1997).
- Peter A. Levine, *In an Unspoken Voice: How the Body Releases Trauma and Restores Goodness* (North Atlantic, 2010).
- Daniel J. Siegel, *The Developing Mind* (Guilford, 1999; 3rd ed. 2020).
- Stephen Porges, *The Polyvagal Theory* (Norton, 2011).
- Stephen Porges, *The Pocket Guide to the Polyvagal Theory* (Norton, 2017).
- Deb Dana, *The Polyvagal Theory in Therapy* (Norton, 2018).
- Stanley Rosenberg, *Accessing the Healing Power of the Vagus Nerve* (North Atlantic, 2017).

---

## §12 Color & Light Therapy Applied

### 12.1 Color psychology — operative principles
Warm tones (red/orange/yellow) raise heart rate; cool tones (blue/green/purple) activate parasympathetic rest-and-digest ([Color Institute: Wellness](https://colorinstitute.com/color-psychology-and-wellness-the-healing-power-of-color/), [Villa Healing Center: Calming Colors](https://villahealingcenter.com/calming-colors-psychology/), [CogniFit: Colors that Calm the Mind](https://blog.cognifit.com/colors-that-calm-the-mind-what-psychology-and-cognitive-science-reveal/), [Theraluxe](https://theraluxe.ca/how-color-psychology-impacts-relaxation-recovery-enhancing-wellness-spaces-through-thoughtful-design/)). Earth tones (clay, wood, soil) regulate the limbic system. Lavender, peach, blush, and soft coral lift mood without stress activation. Faber Birren, *Color Psychology and Color Therapy* (1950, reprinted 2013) is the foundational reference.

### 12.2 Phoenix Wellness Palette — the default

| Function | Palette | Hex band (illustrative) |
|---|---|---|
| Page background | Warm cream / parchment | #F7F0E1 – #FAF6EC |
| Default skin warm-light | Soft peach / blush | #F4D7C5 |
| Calm sky / rest | Muted sage / sea | #C2D6CB / #B6CDD2 |
| Warmth / hearth / safety | Ochre / honey | #C9974C |
| Grief / autumn aware | Russet / burnt sienna | #A6614A |
| Awe / vastness | Indigo with warm rim | #2C3E5C with #E8B274 sun-rim |
| Spiritual / yūgen | Soft slate / mist | #9BA4AE |
| Sacred / devotional | Saffron / rose | #E5A856 / #D77F8F |

### 12.3 Light cues — what each light does
- **Backlight** (rim/halo) = transcendence, sacred quality. Use sparingly: for awe panels, mentor reveals.
- **Dappled light** (broken by leaves) = hope, safety, "the world is beautiful." Default for outdoor teaching scenes; ahjan/omote signature.
- **Rim light** (single edge of a face glowing) = identity, becoming. Use during integration beats.
- **Window light / sheer curtain light** = tenderness, interior life. pamela_fellows signature.
- **Lantern / candle light** = vigil, holding, attention. master_sha (sleep) signature.
- **Golden hour** (low warm sun) = nostalgia, comfort, mono-no-aware. Universal closer.
- **Moonlight / blue hour** = inwardness, dreaming. miki + ren_ashford signatures.

### 12.4 Avoid
- Harsh fluorescent (clinical-anxiety reading).
- Saturated red >15% area without therapeutic intent (alarm reading).
- Pure black (pure void; if used, must be deliberate mu — see §7.6).
- Saturation at 100% across multiple panels (visually exhausting; sympathetic).

### 12.5 Seasonal palettes and mono-no-aware
Pair autumn ochre with spring green within a single mono-no-aware episode. The color-change *is* the impermanence. Lore Olympus does similar work with character palette pairing (Persephone pink + Hades navy — [Oreate AI Blog](https://www.oreateai.com/blog/the-colorful-symbolism-of-persephone-in-lore-olympus/a0c7c5e565245d33ec21e32dd8342118)).

---

## §13 Sound-less Sound — Visual Rhythm + ASMR-adjacent design

### 13.1 ASMR-adjacent visual triggers in panel design
Common ASMR triggers — gentle hand movements, tapping, paper sounds, soft repetition, intimate POV ([Healthline: ASMR Triggers](https://www.healthline.com/health/asmr-triggers), [Wikipedia: ASMR](https://en.wikipedia.org/wiki/ASMR), [REM-Fit: Most Common ASMR Triggers](https://remfit.com/blogs/news/the-12-most-common-asmr-triggers)) — translate to:
- **Close-up hands doing small precise tasks** (folding cloth, pouring tea, pressing a leaf into a book). Camera 30–60cm.
- **Hair-rendering as ASMR-adjacent texture** (soft strand-by-strand, even when stylized — a few accent strokes that the eye traces).
- **Page-turn sound rendered visually** (the curl of a corner, faint motion lines).
- **Gentle eye contact**, character looking softly at the *reader* (not at another character) for 1 panel per episode — the most intimate-POV move available.
- **Whisper-bubble** (smaller font, dotted bubble outline, off-center placement) for therapeutic moments of confidentiality.

### 13.2 Visual onomatopoeia for breath
Phoenix breath SFX library:
- ふぅ (fuu) — long out-breath, soft hand
- すぅ (suu) — long in-breath
- はぁ (haa) — release, sigh
- さら (sara) — breeze through grass
- とん (ton) — soft footfall, kettle settling
- ぽつ (potsu) — single raindrop, single tear
- しん (shin) — silence (rendered, paradoxical) — used for mu beats

Position: edge of panel, vertical orientation, low contrast.

### 13.3 Rendered silence
Three blank panels, scroll-with-no-text — **legal as a beat**, not skipped. (Mu — §7.6.) しん positioned once at the side as the only mark.

### 13.4 Frieren's quiet
Frieren's silent moments are not absence of sound design; they are deliberate negative space inviting the reader to supply imagined sound (wind, snow). Phoenix mandate: at least 1 fully-silent beat per episode. Most mainstream webtoons go zero. The presence of even one is a discriminator readers feel.

---

## §14 Narrative Structures That Heal

### 14.1 Replace 3-act with: settle-in / gentle activation / integration

| Traditional Act | Therapeutic Replacement | Pixel/beat budget |
|---|---|---|
| Act 1 — Setup | **Settle-in** — orient reader; safety cue establishment; anchor displayed | 25% of episode |
| Act 2 — Confrontation | **Gentle activation** — the difficulty arrives, titrated | 40% of episode |
| Act 3 — Resolution | **Integration** — the difficulty is metabolized; the reader exhales | 35% of episode |

### 14.2 Episodic over serial — non-negotiable for Phoenix

Mushishi rule: every episode complete in itself. A reader who reads only one episode in a year must finish settled. Series-arc plot exists, but no episode requires the next to feel whole.

### 14.3 Hero's-journey replaced by circle-journey

Maureen Murdock, *The Heroine's Journey* (Shambhala, 1990) — circular structure, return-to-self, integration of opposites; not vanquish-villain ([Heroine Journeys: Murdock's arc](https://heroinejourneys.com/heroines-journey/), [Wikipedia: Heroine's Journey](https://en.wikipedia.org/wiki/Heroine's_journey)). Phoenix series-arcs are circle-return arcs. The protagonist comes home different, not crowned.

### 14.4 Soft cliffhangers — emotional anticipation without spike

A soft cliffhanger is "I wonder if she'll go to the ceremony tomorrow" not "she's about to die." It engages PERMA's *interest* (Fredrickson) without sympathetic activation. The reader returns next week from curiosity, not alarm.

### 14.5 Coming-home as canonical close

Every series ends with a coming-home arc — to the self, to the body, to the place. Not a victory, not a wedding, not an ascension. The protagonist sits where she sat in episode 1 and notices something different. The reader notices it with her.

### 14.6 Narrative therapy parallels
Michael White & David Epston's externalizing-the-problem and re-authoring-conversations ([narrative therapy practice]) — the protagonist treats the difficulty as a thing-with-a-name (the Watcher, the Spiral, the False Alarm — Phoenix already has these "engines" in `teacher_persona_matrix.yaml`). Externalization of the engine is itself trauma-informed.

---

## §15 The Teacher Figure — Mirror, not Oracle

### 15.1 The didactic trap

Teaching characters notoriously turn didactic. The reader resents being lectured. Cf. seinen "philosophical monologues that read as essays" failure mode in Phoenix's existing genre-styles doc.

### 15.2 Mirror mode — reflect, don't deliver

The teacher's primary verbal move is **reflection**: "You said X. What does X want?" or "Your shoulders went up just now." The teacher is rarely the source of new information; she is the *site* where the protagonist hears herself.

### 15.3 Show-don't-tell wisdom

If a teaching is going to land, it lands through:
- **Action**: teacher does the thing being taught, and the protagonist watches.
- **Setting**: tea is brewed; the protagonist's nervous system regulates from the brewing, no words required.
- **Embodied modeling**: teacher visibly is what the protagonist needs to become — not described.

### 15.4 Recurring scene templates (Phoenix's reusable forms)

- **Tea ceremony / shared meal** — slow-pace teaching by ritual.
- **Walk-in-forest / shared walking** — peripatetic dialogue; movement as discharge.
- **Sitting-in-silence** — the teacher does not fill silence; the protagonist must.
- **Demonstration-then-question** — teacher does, then asks "What did you notice?" rather than telling.
- **Reflective letter / scroll** — written object the teacher leaves; protagonist reads alone.

### 15.5 Per-teacher voice signatures

Cross-reference with `teachers/*/README.md` and `config/catalog_planning/teacher_persona_matrix.yaml`. Each teacher should have:
- A speech tempo (slow / measured / brisk / softly-paced).
- A bubble shape (round/cloud/scroll/sutra-card).
- A signature gesture (folded hands; one hand to heart; cup held in both).
- A color signature (§12.2 mapped to teachers — see §18).

### 15.6 References
- Joseph Campbell, *The Hero with a Thousand Faces* (1949).
- Robert A. Johnson, *He / She / We* (HarperOne, 1974/1976/1983).
- Carl Jung, *Memories, Dreams, Reflections* (1961).
- Maureen Murdock, *The Heroine's Journey* (1990).
- Michael White & David Epston, *Narrative Means to Therapeutic Ends* (Norton, 1990).

---

## §16 Concrete Craft Formula Library — 50 Named Techniques

These are usable as craft cards. Each: name • description • when to use • example.

**Pacing / scroll**
1. **The Long Drop** — ≥1500px yohaku with single small symbol. Use after any difficult emotional reveal. Ex: end of Frieren's grief beat.
2. **The Miyazaki Ma** — 2400–3200px of pure environment. Use once per iyashikei episode. Ex: Spirited Away train scene.
3. **Pendulation Pair** — high-activation panel (≤400px) paired with low-activation panel (≥1200px) within 5-panel window. Use in trauma-processing arcs.
4. **The Tea Beat** — three panels of tea steam rising, no dialogue. Use for scene transition in iyashikei episodes.
5. **The Anchor Return** — series-specific image returns 3–5× per episode with ≤10% color shift. Use as resourcing throughout.
6. **The Breath Bracket** — open + close every episode with a literal breath panel. Use in every episode without exception.
7. **The Mu Spread** — full ≥3500px of empty cream with one しん at side. Use once per series. Ex: joshin episodes.
8. **The Wait-Loaded Panel** — a panel that implies sound about to happen but doesn't. Use to slow reader's thumb. Ex: kettle-not-yet-whistling.
9. **The Soft Cliffhanger** — emotional anticipation, no arousal spike. Use at every episode-end. Ex: "tomorrow she might."
10. **The Settling Sigh** — last panel of episode is exhale (ふぅ + shoulder drop). Use to close every episode.

**Polyvagal / safety cues**
11. **The Faint Smile** — eye-area-only close-up, soft smile. Use as episode opener / ventral vagal cue.
12. **The Open Hand** — palm-up, fingers relaxed, single panel. Use mid-episode as safety cue refresh.
13. **Ground On Earth** — close-up of bare foot or sandal touching grass / wood. Use during sympathetic-deactivation moves.
14. **Slow Zoom-Out** — 3–4 panels widening face → room → building → sky. Use after an activation peak.
15. **Co-Breath** — two characters in same air, both with steam/breath rendered. Use during co-regulation beats.
16. **Cushion POV** — camera 80–120cm off ground for entire teaching scene. Use during all formal teaching moments.
17. **Predictable Rhythm Block** — 4 panels of identical width and gutter. Use to lower threat detection in mid-episode.
18. **Warm-Edge Page** — cream page with peach/ochre edge wash. Use as default page treatment.

**Somatic experiencing**
19. **Resource Anchor** — series-specific image (cf. §5.3 table). Use 3–5× per episode.
20. **Sensation Captioning** — narration drops below cognition into pure sensation language. Use during high-affect interior moments.
21. **The Dappled Light Hand** — close-up on character's hand in dappled sun. Use as resource panel anchor (ahjan/omote signature).
22. **The Discharge Yawn** — character yawns or sighs at scene-close, somatic completion visible. Use to close rupture-repair cycles.
23. **The Tracking Window** — internal monologue tracks one bodily location across an arc ("the thread of warmth at the base of my throat"). Use over 5–10 episodes for somatic continuity.
24. **The Pendulation Graph** — invisible structural rule: ≥3 oscillations in arousal per episode. Use as authoring constraint.

**Positive psychology**
25. **The Awe-Pullback** — pull back to vastness; protagonist tiny in frame; ≥2400px hold. Use ≥1× per series-arc.
26. **The Savoring Hold** — extended scroll on a small joy. Use ≥2× per episode.
27. **The Gratitude Close** — protagonist names a small gratitude in interior monologue at episode-end. Use ~1-in-3 episodes.
28. **The Strength Mirror** — teacher names protagonist's strength back to her. Use 3× more often than teacher self-references.
29. **The Flow State Beat** — protagonist absorbed in a small skilled task; reader still with her. Use ≥2× per series.
30. **The PERMA Bracket** — open and close every episode with positive emotion. Use universally.

**Japanese aesthetics**
31. **Yohaku Default 30%** — at least 30% of an episode's vertical pixels are pure empty page. Use as authoring constraint.
32. **Mono-no-Aware Pair** — one frame of bloom + one frame of fade within 4 beats. Use in seasonal / grief / change episodes.
33. **Wabi Texture** — render a chip in the cup, fray in the cloth, crack in the wood; let camera linger. Use in establishing teacher's space.
34. **Yūgen Half-Glimpse** — show only part of a sacred or numinous object. Use during spiritual beats.
35. **Maai Spacing** — teacher 1–1.5 character-widths from protagonist in 2-shot frames. Use as compositional default.
36. **Borrowed Scenery (Shakkei)** — pull a distant element (bell, peak, roof) into background. Use to widen the world subtly.

**Zen / sumi-e**
37. **Single-Stroke Confidence** — preserve the commitment-mark of the line; no over-cleaning. Use in line-art passes.
38. **Three-Tier Composition** — heaven/earth/figure stratum in nature panels. Use for outdoor teaching scenes.
39. **Asymmetric 1/3 Figure / 2/3 Yohaku** — figure occupies 1/3, void 2/3. Use as default panel composition.

**Light / color**
40. **Golden Hour Closer** — final outdoor beat in low warm sun. Use as universal closer.
41. **Backlit Reveal** — rim light on first appearance of teacher in an episode. Use for teacher entry beats.
42. **Lantern Vigil** — single lantern illuminates a sleeping or contemplating figure. Use for sleep / vigil episodes (master_sha signature).
43. **Window-Sheer Tenderness** — diffused light through sheer curtain. Use for interior emotional beats (pamela_fellows signature).
44. **Seasonal Ochre/Green Pair** — autumn + spring on adjacent panels for mono-no-aware. Use in change-of-life episodes.

**Sound-less sound**
45. **Visual Whisper Bubble** — smaller font, dotted outline, off-center. Use for therapeutic confidentiality.
46. **The Held Reader Gaze** — character looks softly at the reader for one panel. Use 1× per episode max.
47. **Rendered Silence** — しん placed alone at panel edge. Use during mu / awe beats.

**Trauma-informed**
48. **Pre-Cover Content Note** — teacher's voice, soft, explicit, before episode 1 panel. Use on episodes touching trauma directly.
49. **Externalize the Engine** — name the difficulty (the Watcher, the Spiral). Use within first 3 panels of any difficulty introduction.
50. **Rupture-Repair Cycle** — within multi-episode arc, teacher and protagonist briefly miss each other; both return. Use ≥1× per series.

---

## §17 What to Avoid

- **Therapy-speak / jargon.** "Ventral vagal" never appears in dialogue. Show, don't lecture. The science is in the design, not the script.
- **Toxic positivity.** Broaden-and-build does not mean "always be happy." Mono-no-aware, grief, allowance of difficulty are central. Avoid relentlessly upbeat tone — feels false, breaks neuroception.
- **Cultural appropriation.** Each tradition is represented with attributable source teachers, citations in afterword, sensitivity reviewers. Maat (Egyptian / Sufi) and ra (solar / Egyptian) need Egyptology + Sufism reviewers; sai_ma (bhakti) needs South Asian devotional reviewers; master_feung / master_wu (Chinese internal arts) need Chinese internal-arts practitioner reviewers; pamela_fellows (Western somatic) is the lowest-risk teacher culturally. Do NOT mash traditions into a generic "wisdom voice."
- **Trauma porn.** No graphic depiction without therapeutic resolution. Imply, externalize, name the engine; do not render.
- **Spiritual bypassing.** Using a teaching to skip emotion is itself a story-engine to *resist*, not endorse. Protagonist sometimes uses the teaching wrong (bypasses) and the teacher gently redirects to the emotion.
- **Generic wellness aesthetic.** Everything-blurry-pastel is *not* therapeutic. Specificity (the chipped cup, the named dappled light, the pressed leaf) is. Avoid "Headspace" sameness; aim for Yokohama Kaidashi Kikō specificity.
- **Aggressive cliffhangers.** Sympathetic activation at episode-end is forbidden in iyashikei imprints; permitted only in seinen/horror imprints with explicit content warning and titrated next-episode opening.
- **High-arousal panels held without titration.** Activation:Ground vertical ratio per episode must be ≤1:2.5.
- **Predator POV** of vulnerable protagonists (top-down high-angle).
- **Saturation overload** (>2 consecutive panels at 100% saturation).
- **Sudden loud SFX** without buildup (neuroception flips threat in <300ms).
- **Therapy-replacement framing.** Phoenix manga is *adjunctive*, not a replacement for clinical care. Front-and-back-matter must include this disclaimer.

---

## §18 Phoenix-Specific Recommendations

### 18.1 Per-episode Scroll Therapeutic Checklist (5 items, gating)

Every episode must pass these to ship:
1. **Safety cue inside first 800px.** (Faint smile / open hand / dappled light / co-breath / tea steam — at least one.)
2. **≥3 pendulation oscillations between activation and ground.**
3. **≥1 explicit somatic cue** (breath panel, ground-on-earth panel, or sensation-captioned narration block).
4. **Anchor Panel returns ≥3 times.**
5. **Ends in completion** (sigh, exhale, settling, gratitude). Soft cliffhanger permitted; arousal-spike cliffhanger banned.

Bonus items (raise quality, not gates):
- Awe-Pullback panel present (required ≥1× per arc).
- Yohaku ≥30% of total vertical pixels.
- ≥1 fully-silent beat.

### 18.2 Per-teacher Visual + Pacing Signatures

| Teacher | Tradition | Signature anchor | Color signature | Pacing signature | Light signature |
|---|---|---|---|---|---|
| ahjan | Buddhism (forest-simplicity) | dappled forest path / Stillness Press book spine | sage + cream + ochre | 1500px ma between beats; long drops common | dappled forest light |
| joshin | Zen | round zafu on tatami | ink black + parchment cream | ≥1 mu spread per series; high yohaku ratio | single shaft of light through shōji |
| junko | Shinto / contemplative | water reflection in stone basin | misty blue-green + plum | 800px ma; gentle rhythm; high relational | morning light on water |
| maat | Egyptian / Sufi | feather on brass scale | warm sand + lapis + gold | balanced symmetric beats; rare; weighted | desert dawn / lantern interior |
| master_feung | Chinese internal arts | mountain ridgeline / kettle on coals | mineral grey + jade + tea-bronze | breath-paced; long ground holds | tea-house warm interior |
| master_sha | Chinese healing | lantern light on bedroom floor | indigo + warm lantern amber | very slow; sleep-pace | lantern, blue-hour |
| master_wu | Chinese martial / spiritual | pine bough on rocky cliff | granite + pine green + steel | sharper pendulation between charge and ground | dawn cliff light |
| miki | Japanese mindfulness (modern) | open notebook + phone face-down | white + matcha green + soft coral | webtoon-fast inside iyashikei-slow frame | indoor desk light, blue hour |
| omote | Japanese body / shiatsu | pressed leaves between book pages | autumn ochre + russet + cream | seasonal-anchored, slow | golden hour |
| pamela_fellows | Western somatic | window with sheer curtain, late sun | blush + warm white + slate | English-cadence pacing, gentle | window-sheer tenderness |
| ra | Egyptian solar | sun coming over desert horizon | sand gold + rim ember + lapis | breath-of-fire-then-rest pendulation | sunrise rim |
| sai_ma | Indian devotional / bhakti | brass diya + jasmine | saffron + rose + sky blue | bhajan-cadence rhythm | oil lamp warmth |

### 18.3 Per-style somatic mapping (Phoenix's existing style tags)

| Style tag (existing) | Add this somatic constraint |
|---|---|
| cozy_iyashikei | Yohaku ≥35%; ≥1 Miyazaki ma; Anchor returns ≥4×; arousal peak ≤4/10 |
| dark_psychological | Pendulation Pair mandatory whenever activation peak ≥6/10; ≥1 awe-pullback per arc; CW required; Anchor returns ≥5× |
| hyper_clean_cinematic | Three-tier sumi-e composition default; predictable rhythm blocks; warm-edge page mandatory |
| webtoon_vertical_romance | Slow burn must include ≥2 co-breath panels per episode; deflection-jokes allowed but ≥1 quiet-after-comedy beat per episode |
| social_media_simulacra | Phone-screen panels must be bracketed by yohaku before and after (titrated activation); ≥1 phone-face-down anchor panel per episode |
| power_progression (shonen) | Permitted only with mandatory Settling Sigh closes; activation peaks must end in discharge, not cliff |
| dark_psychological + horror | Pre-cover content note required; rendered silence ≥2× per episode; awe-pullback at midpoint |

### 18.4 Per-series mandates

- **Series episode 1** must teach the Anchor (introduce it 5+ times).
- **Series episode N (final)** must close in a coming-home beat — protagonist back where they started, noticing differently.
- **Across the season-arc,** ≥1 awe-pullback, ≥1 rupture-repair cycle, ≥1 strength-mirror moment per major arc.
- **Every series** ships with a 1-page reader-facing "How to read this slowly" guide on the inside cover (digital or print).

### 18.5 Catalog-level mandates

- **Per-series 14-episode default** — confirms with existing catalog (most series are 12–16 chapters).
- **Per-series HRV-style pre-test** — sample 10 readers; measure resting HRV before; have them read 1 episode; measure after. Average end-state arousal must be ≤ start-state arousal (positive delta direction toward parasympathetic). Ship gate.
- **Per-imprint guardrails** — Stillness Press (ahjan, joshin, junko, omote, pamela_fellows) is iyashikei-only, dark_psychological banned. A separate imprint hosts seinen/horror Phoenix content with stricter CW / titration rules.

### 18.6 Reader promises (revision recommendation for `MANGA_READER_PROMISES.md`)

Add: **"You will exit calmer than you entered."** Then deliver via the §18.1 checklist.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Therapy-replacement misread | Medium | High (legal/ethical) | Adjunctive disclaimer on every series cover and inside-cover page; refer-to-care callouts at end of trauma episodes |
| Cultural appropriation | Medium | High | Per-tradition sensitivity reviewers (see §17); citation afterword in every series |
| Toxic positivity drift | High | Medium | Mono-no-aware mandate; grief / wabi-sabi / impermanence content required across catalog |
| Iyashikei interpreted as "boring" | Medium | Medium | Specificity over abstraction; Yokohama Kaidashi Kikō standard; reader testing with 10+ HRV-tracked readers |
| Shonen/horror imprint craft contamination | Medium | Medium | Imprint-level guardrails (§18.5); separate QA rubric per imprint |
| HRV testing failure on early episodes | High | Low (informational) | Iterate; treat early failures as expected; gate at series-close, not per-episode |
| Cultural-mistranslation of Japanese aesthetic terms | Medium | Medium | Native-Japanese reviewer for ja_JP releases; aesthetic-terms glossary in style guide |
| Sympathetic-cliffhanger drift toward mainstream | High | High (kills core promise) | Hard ban in Stillness Press imprint; QA gate |
| Reader expectation mismatch | Medium | Medium | "How to read this slowly" inside-cover guide; reader-promise statement |

---

## Citations & References

### Polyvagal & somatic
1. Stephen W. Porges, *The Polyvagal Theory* (Norton, 2011).
2. Stephen W. Porges, *The Pocket Guide to the Polyvagal Theory* (Norton, 2017).
3. Stephen W. Porges, "Polyvagal Theory: A Science of Safety," *Frontiers in Integrative Neuroscience* (2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC9131189/ (accessed 2026-04-25).
4. Polyvagal Institute, "What is Polyvagal Theory?" https://www.polyvagalinstitute.org/whatispolyvagaltheory (accessed 2026-04-25).
5. "Polyvagal theory: a journey from physiological observation to neural innervation and clinical insight," *Frontiers in Behavioral Neuroscience*, 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12479538/
6. "A theoretical exploration of polyvagal theory in creative arts and psychomotor therapies," *Frontiers in Psychology*, 2024. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1382007/full
7. Deb Dana, *The Polyvagal Theory in Therapy* (Norton, 2018).
8. Stanley Rosenberg, *Accessing the Healing Power of the Vagus Nerve* (North Atlantic, 2017).
9. Peter A. Levine, *Waking the Tiger: Healing Trauma* (North Atlantic, 1997).
10. Peter A. Levine, *In an Unspoken Voice* (North Atlantic, 2010).
11. Pat Ogden & Janina Fisher, *Sensorimotor Psychotherapy: Interventions for Trauma and Attachment* (Norton, 2015). https://wwnorton.com/books/9780393706130
12. Janina Fisher, *Healing the Fragmented Selves of Trauma Survivors* (Routledge, 2017).
13. Janina Fisher, "Sensorimotor Psychotherapy in the Treatment of Trauma." https://janinafisher.com/wp-content/uploads/2023/03/sensorimotor-psychotherapy-trauma.pdf
14. Bessel van der Kolk, *The Body Keeps the Score* (Penguin, 2014).
15. Daniel J. Siegel, *The Developing Mind* (Guilford, 1999, 3rd ed. 2020).
16. "Window of Tolerance," Psychology Tools. https://www.psychologytools.com/resource/window-of-tolerance
17. NICABM, "How to Help Your Clients Understand Their Window of Tolerance." https://www.nicabm.com/trauma-how-to-help-your-clients-understand-their-window-of-tolerance/
18. Sarah Ross PhD, "Resourcing, Pendulation and Titration: Practices from Somatic Experiencing." https://sarahrossphd.com/resourcing-pendulation-titration-practices-somatic-experiencing/
19. Somatic Experiencing International. https://traumahealing.org/se-101/
20. The Awake Network, "Peter Levine's 90-Second Lesson on Pendulation." https://www.theawakenetwork.com/peter-levine-pendulation-trauma/

### Positive psychology, awe, flow
21. Barbara L. Fredrickson, *Positivity* (Crown, 2009).
22. Barbara L. Fredrickson, "The Role of Positive Emotions in Positive Psychology: The Broaden-and-Build Theory of Positive Emotions," *American Psychologist* 56(3), 2001. https://pmc.ncbi.nlm.nih.gov/articles/PMC3122271/
23. Barbara L. Fredrickson, "Gratitude, like other positive emotions, broadens and builds," 2004 PDF. https://peplab.web.unc.edu/wp-content/uploads/sites/18901/2018/11/fredrickson2004.pdf
24. Positive Psychology, "Broaden-and-Build Theory of Positive Emotions." https://positivepsychology.com/broaden-build-theory/
25. Martin E. P. Seligman, *Flourish: A Visionary New Understanding of Happiness and Well-being* (Free Press, 2011).
26. Dacher Keltner, *Awe: The New Science of Everyday Wonder and How It Can Transform Your Life* (Penguin, 2023).
27. Maria Monroy & Dacher Keltner, "Awe as a Pathway to Mental and Physical Health," *Perspectives on Psychological Science*, 2023. https://journals.sagepub.com/doi/10.1177/17456916221094856
28. Dacher Keltner & Jonathan Haidt, "Approaching awe, a moral, spiritual, and aesthetic emotion," *Cognition and Emotion*, 2003. https://pubmed.ncbi.nlm.nih.gov/29715721/
29. John Templeton Foundation, "The Science of Awe" white paper. https://www.templeton.org/wp-content/uploads/2018/08/Awe-White-Paper_distribution.pdf
30. Mihaly Csikszentmihalyi, *Flow: The Psychology of Optimal Experience* (Harper & Row, 1990).
31. "Flow (psychology)," Wikipedia. https://en.wikipedia.org/wiki/Flow_(psychology)
32. "Analyzing Skill-Challenge Interaction and Flow State," *Journal of Happiness Studies*, 2024. https://link.springer.com/article/10.1007/s10902-024-00846-4

### Mindfulness, contemplative neuroscience
33. Jon Kabat-Zinn, *Wherever You Go, There You Are* (Hyperion, 1994).
34. Jon Kabat-Zinn, *Full Catastrophe Living* (Delta, 1990).
35. "Mindfulness-based stress reduction," Wikipedia. https://en.wikipedia.org/wiki/Mindfulness-based_stress_reduction
36. "Mindfulness, Interoception, and the Body: A Contemporary Perspective," *Frontiers in Psychology*, 2019. https://pmc.ncbi.nlm.nih.gov/articles/PMC6753170/
37. Tara Brach, *Radical Compassion* (Viking, 2019). RAIN resources: https://www.tarabrach.com/rain/
38. Mindful, "Tara Brach: RAIN." https://www.mindful.org/tara-brach-rain-mindfulness-practice/
39. Mindful, "Jon Kabat-Zinn: Defining Mindfulness." https://www.mindful.org/jon-kabat-zinn-defining-mindfulness/
40. Daniel Goleman & Richard Davidson, *Altered Traits* (Avery, 2017).
41. Center for Healthy Minds, Richard J. Davidson. https://centerhealthyminds.org/about/founder-richard-davidson

### Iyashikei, Frieren, manga craft
42. Phoenix internal: `artifacts/research/manga_genre_writing_styles_2026_04_04.md` (iyashikei §6).
43. Phoenix internal: `artifacts/research/strategic_audit/02_bestseller_pattern_decomposition.md` (Frieren commercial data, iyashikei).
44. Phoenix internal: `artifacts/research/therapeutic_manga_wellness_market_research_2026_04_04.md` (multi-market framing).
45. The Conversation / Phys.org, "Iyashikei healing manga," October 2024 (cited in Phoenix bestseller decomposition).
46. CBR, "Frieren Season 2 Has Officially Ruined the Manga Forever." https://www.cbr.com/frieren-season-2-ruined-the-manga-perfect-changes/
47. Crunchyroll Features, "What Watching Frieren: Beyond Journey's End [helps with grief]," October 2024. https://www.crunchyroll.com/news/features/2024/10/29/frieren-beyond-journeys-end-processing-grief
48. FandomWire, "Frieren: Beyond Journey's End Needs Its Excruciatingly Slow Pacing." https://fandomwire.com/frieren-beyond-journeys-end-needs-its-excruciatingly-slow-pacing-for-a-simple-reason/
49. Wikipedia, *Yokohama Kaidashi Kikō*. https://en.wikipedia.org/wiki/Yokohama_Kaidashi_Kik%C5%8D
50. SF Encyclopedia, *Yokohama Kaidashi Kikō*. https://sf-encyclopedia.com/entry/yokohama_kaidashi_kiko
51. TV Tropes, *Yokohama Kaidashi Kikō*. https://tvtropes.org/pmwiki/pmwiki.php/Manga/YokohamaKaidashiKikou
52. Anime-Planet iyashikei genre tag (referenced in Phoenix bestseller decomposition).
53. Book Riot, "9 Iyashikei Manga to Heal Weary Hearts" (referenced in Phoenix bestseller decomposition).

### Webtoon scroll craft
54. S-Morishita Studio, "Vertical Scrolling Webtoon Format." https://www.s-morishitastudio.com/vertical-scrolling-webtoon-format/
55. Clip Studio / Art Rocket, "Tips for Creating Vertical Scrolling Webtoons." https://www.clipstudio.net/how-to-draw/archives/157055
56. Matt Reads Comics, "The Unique Strengths of Vertical Scroll Webcomics." https://mattreadscomics.com/2020/10/13/vertical-scroll-webcomics-strengths/
57. Wikipedia, *Lore Olympus*. https://en.wikipedia.org/wiki/Lore_Olympus
58. The Mary Sue, "Lore Olympus and Webtoon Finally Helped Me Love Comics." https://www.themarysue.com/lore-olympus-on-webtoon/
59. Oreate AI Blog, "The Colorful Symbolism of Persephone in Lore Olympus." https://www.oreateai.com/blog/the-colorful-symbolism-of-persephone-in-lore-olympus/a0c7c5e565245d33ec21e32dd8342118
60. Scott McCloud, *Understanding Comics* (Tundra, 1993).
61. Scott McCloud, *Reinventing Comics* (HarperCollins, 2000).
62. ImageTexT, "The Construction of Panels (Koma) in Manga." https://imagetextjournal.com/the-construction-of-panels-koma-in-manga/

### Japanese aesthetics
63. Stanford Encyclopedia of Philosophy, "Japanese Aesthetics." https://plato.stanford.edu/entries/japanese-aesthetics/
64. Donald Keene, *The Pleasures of Japanese Literature* (Columbia, 1988).
65. Leonard Koren, *Wabi-Sabi for Artists, Designers, Poets & Philosophers* (Stone Bridge, 1994; rev. 2008).
66. dans le gris, "Ma: The Japanese Aesthetic of Negative Space and Time." https://danslegris.com/blogs/journal/ma
67. dans le gris, "Japanese Aesthetics of Space: Ma, Yohaku no Bi." https://danslegris.com/blogs/journal/japanese-aesthetics-of-space-ma-yohaku-no-bi-and-the-art-of-subtraction
68. Kogei Standard, "The Beauty of Empty Space (Ma / Yohaku)." https://www.kogeistandard.com/insight/serial/editor-in-chief-column-kogei/ma-yohaku/
69. japanese-aesthetics.com, "Yohaku." https://www.japanese-aesthetics.com/article/theEssenceOfJapan/yohaku
70. Deeper Japan, "Ma and Modern Minimalism." https://www.deeperjapan.com/deeper-views/ma-and-modern-minimalism
71. The Mindful Word, "Ma: The Value of Empty Space." https://www.themindfulword.org/empty-space/
72. Eastern Illinois University, "Wabi-Sabi, Mono no Aware, and Ma," *Studies on Asia*. https://castle.eiu.edu/studiesonasia/documents/seriesIV/2-Prusinkski_001.pdf
73. Hayao Miyazaki on "ma," via ScreenCraft. https://screencraft.org/blog/hayao-miyazaki-says-ma-is-an-essential-storytelling-tool/
74. Medium / Nayeon Park, "Ma: The Best Moments in a Studio Ghibli Film Are Silent." https://medium.com/@nayeonpark/ma-the-best-moments-in-a-studio-ghibli-film-are-silent-27210e215b21
75. Cinema Etc., "Studio Ghibli and Moments of Reflection." https://cinemaetceteracom.wordpress.com/2020/04/22/studio-ghibli-and-moments-of-reflection/

### Zen / sumi-e
76. D.T. Suzuki, *Zen and Japanese Culture* (Princeton/Bollingen, 1959).
77. Shunryu Suzuki, *Zen Mind, Beginner's Mind* (Weatherhill, 1970).
78. Stephen Addiss, *The Art of Zen* (Harry N. Abrams, 1989).
79. Asian Brushpainter, "The Aesthetics of Ink and Wash Painting." https://www.asianbrushpainter.com/blogs/kb/the-aesthetics-of-ink-and-wash-painting
80. Sakuraco, "Sumi-e in Japan." https://sakura.co/blog/sumi-e-in-japan-the-development-of-ink-wash-painting
81. Wikipedia, "Ink wash painting." https://en.wikipedia.org/wiki/Ink_wash_painting
82. Japan Objects, "Sumi-e: Japanese Ink Painting." https://japanobjects.com/features/sumie

### Color & light
83. Faber Birren, *Color Psychology and Color Therapy* (1950; reprinted Citadel, 2013).
84. Color Institute, "Color Psychology and Wellness." https://colorinstitute.com/color-psychology-and-wellness-the-healing-power-of-color/
85. Villa Healing Center, "Calming Colors." https://villahealingcenter.com/calming-colors-psychology/
86. CogniFit Blog, "Colors That Calm the Mind." https://blog.cognifit.com/colors-that-calm-the-mind-what-psychology-and-cognitive-science-reveal/
87. Theraluxe, "How Color Psychology Impacts Relaxation & Recovery." https://theraluxe.ca/how-color-psychology-impacts-relaxation-recovery-enhancing-wellness-spaces-through-thoughtful-design/

### Scrollytelling
88. Shorthand, "Scrollytelling Examples." https://shorthand.com/the-craft/scrollytelling-examples/index.html
89. Maglr, "10 Best Scrollytelling Examples to Inspire Your 2026 Content." https://www.maglr.com/blog/best-scrollytelling-examples
90. Cornermindscape, "The Snow Fall Effect — Parallax Storytelling on the Web." https://cornermindscape.com/snow-fall-effect-parallax-storytelling-web/
91. LinkedIn / Bill Shander, "Snow Fall: The Birth of UX 2.0, Scrollytelling, and So Much More." https://www.linkedin.com/pulse/snow-fall-birth-ux-20-scrollytelling-so-much-more-bill-shander
92. UI Deploy, "Complete Scrollytelling Guide 2025." https://ui-deploy.com/blog/complete-scrollytelling-guide-how-to-create-interactive-web-narratives-2025

### ASMR + sensory rhythm
93. Healthline, "ASMR Triggers." https://www.healthline.com/health/asmr-triggers
94. Wikipedia, "ASMR." https://en.wikipedia.org/wiki/ASMR
95. REM-Fit, "12 Most Common ASMR Triggers." https://remfit.com/blogs/news/the-12-most-common-asmr-triggers

### Narrative & heroine's journey
96. Maureen Murdock, *The Heroine's Journey* (Shambhala, 1990). https://maureenmurdock.com/
97. Wikipedia, "Heroine's journey." https://en.wikipedia.org/wiki/Heroine's_journey
98. Heroine Journeys, "Maureen Murdock's Heroine's Journey Arc." https://heroinejourneys.com/heroines-journey/
99. Joseph Campbell, *The Hero with a Thousand Faces* (1949).
100. Michael White & David Epston, *Narrative Means to Therapeutic Ends* (Norton, 1990).

### Phoenix internal references
- `artifacts/research/therapeutic_manga_wellness_market_research_2026_04_04.md`
- `artifacts/research/manga_genre_writing_styles_2026_04_04.md`
- `artifacts/research/strategic_audit/02_bestseller_pattern_decomposition.md`
- `artifacts/manga/MANGA_FULL_CATALOG_PLAN.md`
- `artifacts/manga/MANGA_QA_RUBRIC.md`
- `artifacts/manga/MANGA_READER_PROMISES.md`
- `config/catalog_planning/teacher_persona_matrix.yaml`
- `teachers/ahjan/README.md`
- `teachers/pamela_fellows/A Journey from Mindfulness to An Awakened Heart_ Empowered Living through Embodiment.md`

---

*End of Therapeutic Scroll Craft Reference. This is the creative bible for Phoenix Omega's art directors and scriptwriters: the scroll is the intervention; everything below the title is in service of that single sentence.*
