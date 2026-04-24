# Kodomomuke Educational / Somatic Encouragement — Style Bible

Touchstones: *Doraemon* (Fujiko F. Fujio), *Chi's Sweet Home* (Kanata Konami), *Shimajiro* (Benesse educational), *Yotsuba&!* (Azuma Kiyohiko — crossover but readable by kids), *Kodomo no Jikan*-era kids' manga, *Anpanman* picture-comic forms, CoroCoro & Chao/Nakayoshi early-elementary titles.

## 1. Market + reader contract
Readers are children 4–11 (plus adult read-alouds), reading alone or with caregivers. Contract: the child leaves every chapter *braver, curioser, or more competent*. Somatic literacy — learning to name body feelings (butterflies, hot face, tired legs, "I'm hungry is different from I'm sad") — is a core modern add. They will reject: condescension, scary cliffhangers, adult irony, moralizing lectures, unclear storytelling, and anything that makes caregivers uncomfortable reading aloud.

## 2. Visual grammar
- **Panel count per chapter:** 25–45 panels over 8–16 pages. Large, clear panels. 2–4 panels per page is typical.
- **Words per page:** 15–50. Furigana on all kanji (in Japanese originals); short sentences in translation.
- **Silent-panel ratio:** 20–35% — but unlike iyashikei, silence is for *comedic beat* or *action reveal*, not contemplation.
- **Black-fill ratio:** 0.10–0.20. Airy, bright.
- **Screentone density:** Low. Bright flat color in color editions; minimal tone in mono.
- **Spread frequency:** 1 per chapter common — a wide action gag, a landscape reveal, or a full-page "feelings" page (new in modern somatic-literacy kodomomuke).
- **Reaction-shot frequency:** Very high — exaggerated, clearly legible facial expressions. Faces do most of the work.
- **Line weight profile:** Bold, consistent, high-contrast. Rounded shapes. Characters readable from a distance (a child holding the book at arm's length must still understand who feels what).

## 3. Pacing + beat conventions
- **Chapter length:** 8–16 pages. Self-contained. Many serials are single-page 4-panel (yonkoma) strips — Chi's original format.
- **Chapter hook family:** *Curiosity or problem posed simply* — "Nobita forgot his homework again" / "Chi can't find her bed" / "Today at school we have a test." Clear, child-scale stakes.
- **Chapter ending convention:** *Resolution + small lesson without naming it as a lesson*. The character regains competence, feels better, or learns. The lesson must be *experienced by the character*, not stated in caption.
- **Scene-to-scene transitions:** Hard cuts with clear location/time markers ("at school", "later"). Children benefit from over-signposted transitions.
- **Per-volume arc shape:** Volume = 6–12 standalone chapters, gently thematic (vol "first day of school", vol "making a friend", vol "feeling scared at night"). No cliffhangers across volumes.

## 4. Dialogue + narration
- **Register:** Simple, warm, age-specific. Sentence length short. Emotional vocabulary is introduced *by characters using it correctly*, modeling for child reader.
- **Narration tolerance:** Low-to-moderate. Narration present but minimal — "The next morning..." style. Letting characters carry the story is preferred.
- **Dialogue-to-narration ratio:** ~80:20.
- **Interior monologue:** Simple, single-line thought bubbles. "I'm scared." "I want to try." Somatic-literacy add: "My tummy feels tight." "My face feels hot." Explicit body-feeling vocabulary is encouraged.
- **Tell-don't-show tolerance:** High and required in measured doses — children are learning to *name* feelings; the form teaches by labeling. The craft is in balancing labeled-feeling (for literacy) with shown-feeling (for narrative pleasure).

## 5. Character + arc conventions
- **Archetype grammar:** The curious/clumsy/kind child protagonist, the wise-but-fallible friend (often animal or tech — Doraemon is the apex), the family adults (warm, imperfect, reliable), the school/neighborhood cohort. No true villains — antagonists are problems (lost item, social conflict, fear) or playful rivals.
- **Emotional arc per volume:** Small wobble → naming the feeling → trying something → small competence gained → feeling named differently at the end. Volume should *model naming*.
- **Cast density:** Small core (3–5) + rotating guests. Cast must be instantly visually distinguishable — children rely on silhouette.

## 6. Failure modes
1. Moralizing captions ("And that's why you should always be kind"). Lesson must live in story, not narrator.
2. Adult irony or sarcasm that sails over children.
3. Real danger without prompt emotional safety signaling. Night scenes, separation beats, etc., must resolve on the same page or chapter.
4. Complicated panel flow — children's reading-order competence is lower; keep Z-pattern or simple vertical.
5. Emotional vocabulary that is too advanced. "Ambivalent" out; "I feel two feelings at once" in.
6. Caregiver-unfriendly content — scatological humor, scary visuals, age-inappropriate themes that adults won't read aloud cheerfully.
7. Unclear character silhouettes — children mis-track who's who.
8. Preachiness about diversity/inclusion that makes the message the subject. Show diverse worlds naturally.
9. Unhappy endings within chapter. Multi-chapter emotional arcs (grief, moving) are permitted but each chapter within must land warmly.
10. Not trusting the child reader — dumbing down subject or feeling. Kids can handle complexity; they cannot handle being patronized.

## 7. Series planning implications (48-volume pre-plan)
48 volumes is typical and often exceeded in kodomomuke (*Doraemon* ran 45+ volumes). Shape:
- **Volumes 1–12:** Ages 5–7 register. Protagonist begins kindergarten / first grade. Themes: separation, friendship, trying new things, naming big feelings.
- **Volumes 13–24:** Ages 7–9 register. Themes: competence, fairness, first disappointment, caring for others, gentle loss (a pet, moving).
- **Volumes 25–36:** Ages 9–11 register. Themes: identity, longer friendship arcs, moral complexity (noticing unfairness), preparing for change.
- **Volumes 37–48:** Ages 10–12 bridge. Themes: leadership of younger kids, revisiting volume-1 themes with competence, saying goodbye.
- Each volume: 6–12 standalone chapters + a "feelings spread" recurring feature teaching one new body-feeling or social-feeling vocabulary word.
- No series-ending doom. Final volume = warm bookend to volume 1.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (8):
1. `framing` — big, clear shots: MS default, CU for feelings, WS for setting. Avoid extreme angles.
2. `beat_role` — {setup, curiosity, wobble, feeling_named, try, small_win, warm_close}
3. `dialogue` — ≤10 words, age-appropriate vocabulary
4. `thought` — single-line thought bubble, optional
5. `feeling_label` — if this panel is the somatic-literacy moment, log the body-feeling word ("tight tummy", "hot face", "quiet inside")
6. `silhouette_id` — which main character silhouette; every main character must be silhouette-distinct
7. `safety_flag` — boolean; true marks chapters or scenes (e.g. nighttime fear, lost-in-store) requiring explicit in-chapter emotional-safety resolution
8. `read_aloud_test` — boolean; if true, the panel's text should be caregiver-friendly read-aloud

## 9. Three canonical chapter-opening examples

**A.**
Mimi's first day of big-kid school started with her *tummy feeling tight*, which was a new feeling, and she didn't know its name yet. She sat at the breakfast table and stirred her rice, and her dad said, "Not hungry?" Mimi shook her head. Her dad sat down next to her and said, "Sometimes when something new is coming, my tummy feels tight too. Is that what's happening?" Mimi thought about it. She put a hand on her tummy. It *was* tight. She nodded. Her dad said, "That's a brave feeling. It means you care."

**B.**
Chi had been looking for her bed for seven whole minutes. Her bed, which had been *right there* by the sunny window, was now not there. Chi sat down where her bed used to be. The sunny spot was still warm. But a warm spot is not a bed. Chi meowed, once, experimentally, to see if her bed would answer. It did not. From the kitchen, Yohei's mom called: "Chi! I washed your bed!" Chi pricked her ears. A wet bed? On purpose? This was a thing? Chi trotted to the kitchen to investigate this emergency.

**C.**
Nobita had forgotten his homework again. This was not unusual. What was unusual was that, today, he had forgotten it *twice* — once at home, and once, somehow, on the walk to school, because he had definitely been carrying something in his hand and now he was not. He stood outside the school gate, patting his pockets, and said to no one in particular, "I am doomed." From inside his backpack, a small round voice said: "Nobita, don't be doomed. Use your words. What is the actual problem?" Nobita unzipped his backpack. "The actual problem is I am going to cry."

## 10. References
- Fujiko F. Fujio afterwords, *Doraemon* Tentōmushi Comics edition (Shogakukan).
- Konami Kanata interview on *Chi's Sweet Home*, *Morning* magazine, 2007.
- Benesse *Shimajiro* editorial guidelines (published curriculum materials).
- Anne Allison, *Millennial Monsters: Japanese Toys and the Global Imagination* (UC Press, 2006) — kodomomuke/ toy ecosystem.
- Laura Miller, "Youth Fashion and Changing Beautification Practices," and the broader *Bad Girls of Japan* volume (Palgrave, 2005) — cultural context on child-reader register norms.
