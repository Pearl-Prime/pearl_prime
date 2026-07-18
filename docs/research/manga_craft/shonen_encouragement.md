# Shonen Encouragement (craft/vocation) — Style Bible

Touchstones: *Blue Period* (Yamaguchi Tsubasa), *Sweat and Soap* (Yamada Kintetsu — josei/seinen craft-encouragement hybrid), *Bakuman*, *Hikaru no Go*, *March Comes In Like a Lion* (Umino Chica), *Chihayafuru*, *Beck*, *Shiori Experience*.

## 1. Market + reader contract
Readers are teens and adults pursuing or nostalgic for a craft — art school, music, go, karuta, fragrance R&D, filmmaking. They show up for *the feeling of practicing*: the humiliations, the micro-technical vocabulary, the moment a discipline clicks. They will reject unearned talent, glossed-over failures, vague sports-manga shouting, and crafts rendered without their actual jargon.

## 2. Visual grammar
- **Panel count per chapter:** 55–90 panels over 25–45 pages.
- **Words per page:** 60–120 (high — technique must be named).
- **Silent-panel ratio:** 20–35%. Silence is used at the *moment of seeing/hearing* (the student finally seeing value, the audience hearing the piece).
- **Black-fill ratio:** 0.20–0.30.
- **Screentone density:** Medium, functional. Tone is used to differentiate *technical inserts* (diagrams, process panels, close-ups of the work itself) from narrative panels.
- **Spread frequency:** 2–3 per volume; reserved for *the work revealed* (the finished canvas, the performance peak, the match point).
- **Reaction-shot frequency:** Medium-high — 3–5 per chapter. Unique to this lane: the *teacher's* reaction shot is as load-bearing as the protagonist's.
- **Line weight profile:** Variable — crisp clean lines on depictions of the discipline (the painting, the music notation, the go board, the fabric), looser lines on everyday scenes. The craft must be drawn with *more* care than the life around it.

## 3. Pacing + beat conventions
- **Chapter length:** 25–45 pages.
- **Chapter hook family:** *Skill gap exposed.* Open on the protagonist encountering a new technique/standard/rival they cannot yet meet. The hook is an aspirational ceiling, not a fight bell.
- **Chapter ending convention:** *Small competence gain* + visible *next gap*. Not "I won"; rather "I figured out this one thing, and I can now see how much I don't know."
- **Scene-to-scene transitions:** Time-skip captions ("one week later", "at the entrance exam"), practice-montage sequences (grid of small panels showing iterative work), and mentor/protagonist cross-cuts.
- **Per-volume arc shape:** Volume = one practice cycle with one exam/showcase. Traditional shape: introduction of challenge → study → local setback → breakthrough insight → showcase → honest assessment. Failures are welcomed; *undeserved* wins are toxic.

## 4. Dialogue + narration
- **Register:** Technical-sincere. Characters use real vocabulary of the craft (in *Blue Period*: "local color," "value study," "gamsaku"; in *Hikaru no Go*: actual sequences and opening names). Inaccuracy is the cardinal wound.
- **Narration tolerance:** Moderate — interior captions during practice, mentor-voice captions during process inserts.
- **Dialogue-to-narration ratio:** ~65:35.
- **Interior monologue:** The protagonist narrates their *technical* thinking in real time ("the light here is cooler than I thought — no, it's not cooler, it's the next color over"). This is the lane's signature move: turning skill acquisition into narrative.
- **Tell-don't-show tolerance:** High for *process* (you must name the technique), low for *emotion* (don't tell us the protagonist loves painting; show them skipping meals).

## 5. Character + arc conventions
- **Archetype grammar:** The late-starting obsessive (Yatora in *Blue Period*), the natural-talent rival, the generous senior, the skeptical teacher, the supportive best friend who is *not* in the craft, the parent-shaped doubt. Deviations: a "chosen one" protagonist breaks the contract; this is the anti-shonen lane for that exact reason.
- **Emotional arc per volume:** Confidence → encounter with true skill → humility → renewed effort → measurable small gain. Crucially, the protagonist *remains behind their goal* at volume's end.
- **Cast density:** Small ensemble (4–8 in the craft cohort, plus family/civilian cast).

## 6. Failure modes
1. Chosen-one talent discovered mid-volume. Breaks the "practice is the point" contract.
2. Glossing the technical vocabulary. Reader literacy in the craft is the primary trust.
3. Antagonists rather than rivals — this lane uses *rivals who are also peers*.
4. Tournament-arc escalation without process panels.
5. Mentor-as-wise-sage with no visible method. Mentors must teach *specifically*.
6. Victory panels without aftermath — the lane requires showing what winning cost.
7. Romance displacing craft in the A-plot. Romance is B-plot or C-plot only.
8. Sports-manga shouting ("I will not lose!!"). Wrong register; encouragement-shonen is quiet.
9. Ignoring money/time/economic reality of the craft — *Blue Period*'s art-prep school cost subplot is the standard.
10. The protagonist becoming the best. They should end the series *mid-career*, still learning.

## 7. Series planning implications (48-volume pre-plan)
48 volumes accommodates a full career arc, which most shonen-encouragement series intentionally *avoid*. Shape:
- **Volumes 1–12: apprenticeship era** (discovery → first formal training → first real test, e.g., entrance exam).
- **Volumes 13–24: mid-apprenticeship** (study abroad / first professional work / early failure).
- **Volumes 25–36: journeyman** (first independent commission / first teaching / crisis of voice).
- **Volumes 37–48: mastery-as-doubt** (the successful adult who still cannot answer the original question).

Each 12-volume era must contain exactly one showcase/exam and one honest failure. Never let a volume end with "now I am good at this"; only "now I can see what I'm still missing." The final volume should loop back to a scene that rhymes with volume 1 — same easel, older hands.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (9):
1. `framing` — standard set plus `technical_insert` (close-up of the work) and `process_diagram`
2. `beat_role` — {skill_gap, practice, micro_gain, technical_insight, mentor_correction, showcase, honest_assessment}
3. `dialogue` — ≤20 words
4. `interior_caption` — technical self-talk permitted
5. `craft_term` — the specific vocabulary word being used/learned in this panel (e.g., "local color", "fifth line hane")
6. `work_shown` — description of the in-diegesis artifact visible in the panel (the painting, the score, the board state)
7. `render_care` — {loose, standard, heightened} — heightened = the discipline's artifact must be drawn with maximum care
8. `mentor_beat_flag` — boolean; true if a mentor reaction or correction is present
9. `gap_residual` — integer 0–3; how much skill gap remains visible at end of panel (volume must not end at 0)

## 9. Three canonical chapter-opening examples

**A. (art school, Blue Period register)**
The first thing the new instructor did was take Yatora's painting down from the wall and lean it against the floor, facing backward, so nobody could see it. "Look at the wall instead," he said. "The wall where your painting was." Yatora looked at the wall. It was white. The instructor waited. A full minute. Two. "Tell me what colors the wall is." Yatora opened his mouth to say "white" and then, thank god, closed it. He looked harder. He saw a warm pink where the skylight hit. He saw a green shadow under the baseboard. He saw that he had been calling a thing white for twenty years and had never once looked at it.

**B. (fragrance R&D, Sweat-and-Soap register)**
Asako had smelled the soap five hundred times and she still could not tell which batch was Monday's and which was Tuesday's. The senior chemist sat across the counter, patient in the way that meant he was not actually patient. "Again," he said. He passed her two blotters. She brought the first to her nose, closed her eyes, and tried to describe what she smelled in the vocabulary they had given her: *top, heart, base. green, aldehydic, musky.* All of it was still shapes in fog. "The left one is older," she said, guessing. He nodded, once. "How much older?" She did not know. He waited. She smelled it again.

**C. (karuta, Chihayafuru register)**
At the club meeting on Thursday, Chihaya arrived forty minutes early because she had read, on the bus, a single sentence in a book about competitive karuta that had kept her awake the whole previous night: *A reader's breath tells you the card before the sound does.* She did not know what that meant. She intended to know by Saturday. She set up her card rows on the tatami, closed her eyes, and listened to the empty club room — the buzz of the light, the traffic outside, her own breathing. She could not hear her own breath. She tried again. She heard it. It was too loud.

## 10. References
- Yamaguchi Tsubasa interviews, *Monthly Afternoon* (Kodansha), *Blue Period* author afterwords vols. 1, 4, 8.
- Umino Chica, *March Comes In Like a Lion* author commentary (Hakusensha).
- Obata Takeshi on *Hikaru no Go* process, *Jump Square* 2003.
- Suenobu Keiko et al. essays in *Shojo Manga! Manga! Manga!* (ed. Toku), craft-narrative chapter.
- Matt Thorn, "The Moto Hagio Interview," *The Comics Journal* #269 — applies to craft-encouragement tradition more broadly.
