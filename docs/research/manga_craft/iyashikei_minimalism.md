# Iyashikei / Minimalist Healing Manga — Style Bible

Touchstones: *Mushishi* (Urushibara Yuki), *Yokohama Kaidashi Kikō* (Ashinano Hitoshi), *Aria* (Amano Kozue), *Flying Witch*, *Hidamari no Ki*.

## 1. Market + reader contract
Readers are adults (primarily 25–55, skewing female in recent years but historically mixed) who are overstimulated and seeking calibrated low-arousal time. They are showing up for *atmosphere, weather, and the restoration of a nervous-system baseline* — not plot. They will reject: raised voices, cliffhangers, villains, romantic triangles, exposition paragraphs. A single violent panel can lose a reader permanently.

## 2. Visual grammar
- **Panel count per chapter:** 45–80 panels over 20–28 pages; avg ~2.5 panels/page.
- **Words per page:** 18–45 (low). Many pages sit at 0–10.
- **Silent-panel ratio:** 35–55% of pages have at least one wordless panel; ~15–25% of pages are entirely wordless.
- **Black-fill ratio:** 0.10–0.20. Deliberately airy; heavy black reads as threat.
- **Screentone density:** Low-to-medium. Tones used for atmosphere (mist, dusk, water) rather than shadow. Gradient tones on skies dominate.
- **Spread frequency:** 1 spread per 1–2 chapters, almost always an establishing landscape or a quiet character-in-environment shot. Never used for drama.
- **Reaction-shot frequency:** Low for human faces; high for *environmental* reactions (a leaf falling, a cat blinking, tea rippling).
- **Line weight profile:** Uniform medium to light; soft brush or fine nib. Heavy contour lines feel aggressive and are avoided except on foreground foliage.

## 3. Pacing + beat conventions
- **Chapter length:** 20–28 pages. Yokohama Kaidashi ran ~24; Mushishi episodic chapters 40–50 (longer because each is a self-contained story).
- **Chapter hook family:** "Weather/season first." Open on a meteorological or temporal cue (fog, first snow, cicadas stopping), THEN locate the character inside it. The hook is *invitation to a mood*, not a question.
- **Chapter ending convention:** Reflective silence or a small gift returned to baseline — a wordless final panel of landscape, the character walking away small-in-frame, or a food/tea object settling. Never a cliffhanger.
- **Scene-to-scene transitions:** Almost exclusively *bleed* transitions — a nature element (clouds, water, a passing bird) carries the eye from scene A to scene B. Hard cuts are rare; time-skip cards almost never.
- **Per-volume arc shape:** Volume = a seasonal cycle or a thematic bouquet. Each chapter is ~90% standalone; gentle continuity threads (a new neighbor, a plant growing) ripple across 4–8 chapters without becoming "the arc."

## 4. Dialogue + narration
- **Register:** Terse, observational, slightly literary. Full sentences are rare; fragments and sensory nouns dominate ("The smell of wet cedar.").
- **Narration tolerance:** Low to moderate. First-person observational captions are allowed (Mushishi uses them heavily) but are short — 1–2 lines, never paragraphs.
- **Dialogue-to-narration ratio:** ~70:30 dialogue:caption. Pages can run caption-only for atmospheric beats.
- **Interior monologue:** Handled via *environmental correlative* — the character doesn't think "I miss her"; we see the empty second teacup. When interior is stated, it is stated once, quietly, and not repeated.
- **Tell-don't-show tolerance:** Near zero. Emotional labeling ("I was sad") is the cardinal sin. The genre's entire contract is that the reader infers.

## 5. Character + arc conventions
- **Archetype grammar:** The calm observer (teacher, shopkeeper, wanderer, medium), the curious apprentice/child, the elderly keeper-of-knowledge, the animal/spirit companion. Deviations: a visibly angry or ambitious character signals the chapter is about *receiving* them into the baseline, not about their drama.
- **Emotional arc per volume:** Baseline → gentle disruption (a letter, a stranger, a storm) → attunement → return to baseline *at a slightly deeper resonance*. This is the canonical iyashikei curve; a volume that does not return to baseline has failed the form.
- **Cast density:** Solo lead with a small rotating supporting cast (3–6 recurring), plus per-chapter guests. True ensembles are rare.

## 6. Failure modes
1. Raising stakes — introducing a threat that requires resolution breaks the contract.
2. Emotional labeling in caption ("She felt lonely") where a silent panel of the empty chair would do.
3. Overdrawing — heavy blacks, hatching, or dense tone suburbanizes the air out of the page.
4. Symmetric panel grids — iyashikei breathes with irregular panel heights; a page of six equal rectangles reads as institutional.
5. Speech-bubble stacking — more than three bubbles per panel is dialogue-drama grammar, not iyashikei.
6. Using a spread for conflict instead of landscape.
7. Cliffhanger endings — even a soft one ("...who could it be?") poisons the re-read value.
8. Musical/emphatic sfx ("DOKUN", "BAM") — iyashikei sfx are environmental and small ("さらさら", wind).
9. Fast inter-panel time cuts — iyashikei favors same-moment multi-angle beats over compressed time.
10. Resolving mystery. A Mushishi reader wants the mushi to remain partly unknowable.

## 7. Series planning implications (48-volume pre-plan)
48 volumes = 48 seasonal/thematic bouquets, NOT a 48-book epic. Suggested shape:
- **12 × 4-volume seasonal cycles** (spring/summer/autumn/winter × 12 years of a place), OR
- **8 × 6-volume "registers"** (water, wood, hearth, road, harvest, rite, letter, silence), OR
- **48 standalone volumes** linked only by a location (a village, a route, a weather station).

Long arcs should be *demographic* (the child apprentice becomes the elder across volumes 1–48) rather than plot arcs. Avoid series-wide antagonists entirely. A 48-volume iyashikei works the way Ozu's late films work: the same house, the seasons turning.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (keep to 7):
1. `framing` — ELS / LS / MS / MCU / CU / insert / environmental-insert
2. `beat_role` — one of {weather_hook, attunement, gesture, environmental_correlative, breath, closure}
3. `subject` — what's in frame (character + environment element)
4. `dialogue` — ≤12 words or null
5. `caption` — ≤15 words, observational, or null
6. `sfx` — environmental only (wind, water, insect), or null
7. `silence_flag` — boolean; true forbids dialogue, caption, AND non-environmental sfx

Constraint hint for the generator: `silence_flag=true` must appear on ≥35% of panels; consecutive non-silent panels ≤4.

## 9. Three canonical chapter-opening examples

**A. (autumn, riverbank)**
The cicadas had stopped sometime in the night. Alpha noticed it when she opened the café shutters and heard, instead, the river — lower now, narrower, the color of weak tea. She set two cups on the counter out of habit, then smiled at herself and put one back. The first chestnut of the year had fallen onto the step. She picked it up, turned it in her fingers, and placed it beside the register. Nobody would come until afternoon. She sat on the porch and watched the water change its mind about which stones to cover.

**B. (a mushishi wanders in)**
Ginko arrived the way weather arrives: earlier than expected and without apology. The old woman was boiling chestnuts when his shadow crossed her doorway, and she did not look up. "You've come about the child who won't sleep." He set his pack down. "I've come about the light that won't leave her window." Outside, a thin gold seam stood where no lamp should be, hovering at the height of a seven-year-old's eyes. The woman stirred the pot. "Then you know more than I do," she said, "and you should eat first."

**C. (first snow, aria-style canal town)**
The first snow of the year in Neo-Venezia was the wrong kind — wet, large-flaked, gone before it touched the canal. Akari caught one on her glove and watched it resolve itself into a single bead of water. Aria mewed, unimpressed. Above them, the undine song-signal rang from the piazza, soft and deliberate, a sound the city used to tell itself it was still itself. Akari adjusted her oar. The gondola slid forward, leaving a seam of dark water where the snow had been, and for a moment the city smelled exactly like bread.

## 10. References
- Ashinano Hitoshi, author afterwords in *Yokohama Kaidashi Kikō* tankōbon (Kodansha Afternoon KC).
- Urushibara Yuki, interview in *Comic Beam* 2005 (on restraint and the "un-explaining" principle for mushi).
- Amano Kozue, *Aria* Perfect Edition commentary (Tokuma Shoten).
- Thomas Lamarre, *The Anime Machine* (Minnesota UP, 2009) — chapter on atmospheric compositing applies directly to iyashikei panel grammar.
- Paul Gravett, *Manga: Sixty Years of Japanese Comics* — iyashikei section.
