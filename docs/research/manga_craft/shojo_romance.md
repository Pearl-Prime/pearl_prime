# Shojo Romance — Style Bible

Touchstones: *Fruits Basket* (Takaya Natsuki), *Kimi ni Todoke* (Shiina Karuho), *Nana* (Yazawa Ai — josei-adjacent), *Ouran High School Host Club*, *Lovely Complex*, *Ao Haru Ride*, *Boys Over Flowers*.

## 1. Market + reader contract
Readers are girls 12–22 and nostalgic adult returnees (late 20s–40s) reading for the *feeling-state of anticipation* — the two-beat delay between a touch and a reaction, the ninety chapters before a confession. They come for emotional gratification paced through delay. They will reject: rushed confessions, unmotivated love-rival contrivances, protagonists with no interior, and cynical endings.

## 2. Visual grammar
- **Panel count per chapter:** 40–70 panels over 35–55 pages (shojo magazine chapters are the longest in mainstream manga — Hana to Yume, Margaret, Betsucomi standard).
- **Words per page:** 50–100 (heavy — shojo is talky and interior).
- **Silent-panel ratio:** 15–30%. Silent beats are used around eye-contact moments and near-touches.
- **Black-fill ratio:** 0.15–0.25. Lighter overall; blacks used for hair (character ID) more than mood.
- **Screentone density:** High and ornamental — flower tones, sparkle tones, gradient emotional fields. The *mood-tone* (bubbles, flowers, stars behind a character) is a primary storytelling tool and not decoration.
- **Spread frequency:** 2–4 per volume. Reserved for *romantic peak* beats: first meeting, first touch, first kiss, the confession. Spreads carry the emotional currency; spending them on action is wrong-register.
- **Reaction-shot frequency:** Very high — 4–8 per chapter, often the love interest's unreadable face. Reaction shots are the primary engine.
- **Line weight profile:** Fine, consistent, with emphasis through tone rather than weight. Eyes drawn large (5–8x realistic) with layered highlight dots; eyes do 60% of the emotional work.

## 3. Pacing + beat conventions
- **Chapter length:** 35–55 pages (monthly magazine); weekly shojo ~28–32.
- **Chapter hook family:** *Proximity beat* — open on the heroine near the love interest in an ordinary circumstance that is about to become charged (shared umbrella, left alone in classroom, school-festival prep). The hook is setup for an almost-touch.
- **Chapter ending convention:** *Almost.* Near-kiss interrupted, confession half-spoken, hand-holding released, letter un-opened. Cliffhangers in shojo are emotional, not plot.
- **Scene-to-scene transitions:** Flower/sparkle bridge tones, time-skip captions ("the next morning"), and *memory-flash* panels (small inset of an earlier look) used to carry emotional continuity across scenes.
- **Per-volume arc shape:** Volume = one relationship-ladder rung. Volume 1: recognition. Volume 2: first misunderstanding. Volume 3: first ally. etc. Major milestones (confession, first kiss) are traditionally *delayed* past reader expectation — Kimi ni Todoke held the first confession until volume 9.

## 4. Dialogue + narration
- **Register:** Interior-voiced, sentimental, specific. Heroine speaks in fragments when near the love interest, completely when narrating.
- **Narration tolerance:** Heavy — first-person heroine narration is the lane's *default* voice. Captions carry the interior.
- **Dialogue-to-narration ratio:** ~55:45.
- **Interior monologue:** Extensive, in borderless or soft-edged caption boxes (distinct from spoken dialogue). Thoughts are often more articulate than speech — that gap is the genre's music.
- **Tell-don't-show tolerance:** Moderate. Naming feelings is permitted *by the heroine*, but the love interest's feelings must remain shown-not-told until a specific reveal chapter.

## 5. Character + arc conventions
- **Archetype grammar:** The earnest, slightly awkward heroine (often undervalued at school), the guarded love interest (cold / princely / kind), the supportive best friend, the rival (often rehabilitated, not villainized), the "second boy" (doomed but loved). *Fruits Basket*'s Tohru defines the modern earnest-heroine template.
- **Emotional arc per volume:** Distance → closeness → misunderstanding → small repair → slightly closer new baseline. A volume without a proximity *gain* fails.
- **Cast density:** Small ensemble (4–8 named recurring). Love triangles are near-obligatory; love quadrangles common.

## 6. Failure modes
1. Confession too early. The form lives on delay; a volume-3 confession drains the engine.
2. Love interest whose interiority is withheld forever (readers turn on him by volume 6 if no POV window opens).
3. Bully-girl rival played flat — modern shojo demands rivals get arcs.
4. Physical assault played as romantic (historical shojo tropes are no longer reader-safe; boys-over-flowers-style roughness reads as toxic to Gen-Z shojo readers).
5. Heroine with no interests outside the romance. Tohru cleans houses; Sawako makes friends; they have lives.
6. Over-serious register with no comedic chibi release — shojo needs the comic panel pressure-valve every 3–5 pages.
7. Missing the flower-tone layer — undesigned emotional backgrounds read as shonen.
8. Resolving all misunderstandings via third-party intervention (protagonists must eventually speak).
9. Male POV that condescends to the heroine.
10. Ending on a wedding/pregnancy when the series' subject was *becoming able to love* — the ending should rhyme with self-authorship, not institution.

## 7. Series planning implications (48-volume pre-plan)
48 volumes = 6–8 multi-volume relationship arcs, NOT one 48-volume courtship (which exhausts readers). Shape options:
- **Primary couple main arc: volumes 1–18** (recognition → confession → early relationship → first real crisis → resolution). Then **volumes 19–30**: side-couple arc with lead couple as mentors. **Volumes 31–42**: generation-next arc (siblings / juniors / children-of). **Volumes 43–48**: reunion/coda arc.
- Alternative (*Fruits Basket* model): **one ensemble, 23 volumes**, then two spinoff series of 12–13 volumes each = 48.
- Each arc must deliver: 1 confession, 1 first-kiss, 1 major misunderstanding, 1 resolution. Never skip a beat; never let two confessions happen within 8 volumes.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (8):
1. `framing` — CU / MCU / MS / over-the-shoulder (crucial for shojo) / insert / mood-field
2. `beat_role` — {proximity_setup, almost_touch, eye_lock, interior_caption, comic_release, delayed_beat, emotional_peak}
3. `dialogue` — ≤15 words; fragmented allowed
4. `interior_caption` — heroine-voice, ≤25 words, soft-border
5. `mood_tone` — {flowers, sparkle, bubbles, gradient, none, darkening} — ornamental tone field
6. `eye_state` — (heroine + LI) independent: wide / averted / half-lid / closed / tearful / unreadable
7. `chibi_release_flag` — boolean; true = comedic SD-style panel (needed every 3–5 pages)
8. `proximity` — integer 0–5 (physical closeness of heroine and LI); must trend upward across volume

## 9. Three canonical chapter-opening examples

**A.**
The umbrella was too small for two people. I knew it was too small for two people because I had been the one who bought it, and I had bought it for one person — specifically, for me, and specifically on a day I did not want to share with anyone. So when Kurosawa-kun stepped under it without asking, our shoulders touched, and I forgot how walking worked. *I'm going to die,* I thought, very calmly. *I'm going to die of an umbrella.* He looked straight ahead. The rain got louder because my heart did.

**B.**
It had been three days since the cultural festival and Sawako had not been able to look Kazehaya in the eye. Not once. Not when he said good morning in the hallway on Monday. Not when he lent her the English handout in fourth period. Not when he smiled at her — a small, patient, *waiting* smile — across the classroom when the bell rang. "Sadako," said Chizuru from the next desk, "your face is doing that thing again." Sawako pressed her hands flat to her cheeks. Her cheeks were hot. Her cheeks had been hot for seventy-two hours.

**C.**
The first thing Tohru learned about the Sohma family was that they did not like to be touched. The second thing she learned was that they were lying. Not on purpose, she thought, wringing out the dishcloth over the sink. Only the way people who have been taught not to want a thing will lie about not wanting it. Shigure passed behind her humming something deliberately cheerful. Yuki passed behind her saying nothing. Kyo slammed the door on the way in. Tohru smiled, because smiling was the only honest answer she had.

## 10. References
- Takaya Natsuki, *Fruits Basket* fan-book interviews (Hakusensha, 2001, 2007).
- Shiina Karuho afterwords, *Kimi ni Todoke* tankōbon vols. 1, 9, 30 (Shueisha Margaret Comics).
- Yazawa Ai, *Nana* author's notes (Shueisha).
- Masami Toku, ed., *International Perspectives on Shojo and Shojo Manga* (Routledge, 2015).
- Jennifer Prough, *Straight from the Heart: Gender, Intimacy, and the Cultural Production of Shojo Manga* (U. Hawaii Press, 2011).
