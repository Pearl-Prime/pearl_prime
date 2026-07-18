# US/Western Literary Graphic Novel — Style Bible

Touchstones: *Fun Home* (Alison Bechdel), *Persepolis* (Marjane Satrapi), *This One Summer* (Jillian & Mariko Tamaki), *Maus* (Art Spiegelman), *Are You My Mother?* (Bechdel), *Blankets* (Craig Thompson), *Can't We Talk About Something More Pleasant?* (Roz Chast).

## 1. Market + reader contract
Readers are adults 25–65, book-trade consumers (not monthly-issue collectors), overlapping heavily with literary-memoir prose audiences. They expect *single-volume narrative completeness*, *authorial voice*, *formally self-conscious page design*, and *themes equal to any literary novel*: family, memory, identity, grief, political formation. They will reject genre shortcuts, superhero mannerisms, decompressed pacing, and any suggestion the work doesn't know what it's doing.

## 2. Visual grammar
- **Panel count per page:** 4–12 — high density typical. Bechdel runs ~9; Satrapi ~6; Tamakis ~5; Spiegelman variable (3–20).
- **Words per page:** 150–400 — the densest of all lanes. Literary graphic novels are close to illustrated prose.
- **Silent-panel ratio:** 10–25%. Silence is deliberate and rationed; captions dominate.
- **Black-fill ratio:** Extremely variable by artist — Satrapi's *Persepolis* runs 0.45–0.60 (stark black-and-white), Tamaki/Tamaki's *This One Summer* uses purple monotone ~0.3, Bechdel uses ink-wash grays 0.2–0.3.
- **Screentone density:** Rare. Hand ink-wash, hatching, or flat duotone replace tone.
- **Spread frequency:** 1–3 per book, heavily weighted. A spread in *Fun Home* (the father's obituary notice, e.g.) is a load-bearing authorial move.
- **Reaction-shot frequency:** Low-to-medium. Cartoon-register reaction shots are foreign; the lane prefers contemplative medium shots.
- **Line weight profile:** Artist-signature. Bechdel: precise fine nib; Satrapi: bold, icon-like; Tamakis: loose, atmospheric brush; Spiegelman: scratchy, variable.

## 3. Pacing + beat conventions
- **Book length:** 100–400 pages, single volume. Serialization is rare; the *book* is the unit.
- **Chapter hook family:** *Essayistic pre-frame* — chapter opens with a caption essay, a literary epigraph, or an object/artifact (photograph, letter, diary page) that the chapter will interpret. *Fun Home*'s chapter openings each name a Greek/modernist referent (Daedalus, Proust, Joyce).
- **Chapter ending convention:** *Resonant echo* — a final image or caption that rhymes back to the chapter opening's referent. Book endings favor circularity over resolution.
- **Scene-to-scene transitions:** Associative memory bridges (a photo in one scene becomes the same photo decades later), caption essays bridging time, juxtapositional cuts (Satrapi's history-to-childhood cuts are the canonical move).
- **Per-book arc shape:** Non-linear. Memory spiral, not linear plot. *Fun Home* is organized thematically, not chronologically. The reader is trusted with time.

## 4. Dialogue + narration
- **Register:** Literary, essayistic, allusive. Captions can and should reference literature, history, philosophy.
- **Narration tolerance:** Very high — captions are the primary voice. This lane can sustain 100+ words of caption per page without fatigue.
- **Dialogue-to-narration ratio:** ~30:70 — inverted from most manga. Dialogue is quoted *inside* the narrative essay.
- **Interior monologue:** Is the default mode. The adult narrator looks back at a child self; the distance is the art. Bechdel's adult-voiced analysis of child-self scenes is the template.
- **Tell-don't-show tolerance:** High. Essayistic telling IS the form. The craft is in the *quality* of the telling, not its suppression.

## 5. Character + arc conventions
- **Archetype grammar:** Narrator-author (lightly fictionalized or explicitly autobiographical), parent-as-mystery, formative friend/lover, historical context figure (Satrapi's Uncle Anoosh). The memoir-I is the structural center.
- **Emotional arc per book:** Not a standard arc. Rather: *the construction of a reading* — the narrator assembles evidence about a person, period, or self, and the book arrives at a provisional interpretation. Endings are interpretive, not triumphal.
- **Cast density:** Small (3–8 named). Memory memoirs do not sustain large casts because each figure needs interpretive depth.

## 6. Failure modes
1. Decompressed manga-style pacing — wastes the book format.
2. Captions that merely re-narrate what the art shows (redundancy is the amateur tell).
3. Absent authorial voice — "objective" memoir reads as evasive.
4. Unearned literary referents — name-dropping Proust without doing Proust's work of close observation.
5. Sentimentality unchecked by irony. The lane's literary register requires the narrator's distance.
6. Superhero/action visual vocabulary (speedlines, dynamic angles) — wrong-register.
7. Resolution via epiphany. Literary graphic novels end on complication, not clarity.
8. Treating the graphic novel as "an illustrated book" rather than using the comics form actively — the juxtaposition of word and image must *do work*.
9. Chronological memoir without self-interrogation.
10. Ignoring the material artifact — many works in this lane reproduce photographs, letters, maps; ignoring that tool is a missed affordance.

## 7. Series planning implications (48-volume pre-plan)
48 volumes is *radically* atypical for this lane; single books are canonical. Workable approaches:
- **48-volume memoir cycle of a single life** across decades, each volume a thematic slice (Bechdel's *Fun Home* + *Are You My Mother?* model extended: father-volume, mother-volume, lover-volume, therapist-volume, friend-volume, political-formation-volume…).
- **48 interlinked memoirs** by 48 different character-authors sharing a setting (a town, a decade, a movement).
- **24 double-volumes**, each a memoir plus its later reinterpretation (the author reads her own earlier book back).

Recommended: a **"life in themes" model** — 48 volumes each organized around a single artifact (a house, a letter, a song, a trial, a photograph) rather than a chronological span. This preserves the lane's literary register at scale.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (9):
1. `framing` — CU / MCU / MS / WS / document-insert / archival-reproduction / map / diagram
2. `beat_role` — {essayistic_open, scene_evidence, interpretive_caption, juxtaposition, archival_artifact, resonant_echo}
3. `caption` — essayistic; can run 30–60 words; allusive
4. `dialogue` — quoted, often with quotation marks inside captions rather than in bubbles
5. `referent` — the literary/historical/familial reference this panel engages (explicit, even if indirect in final art)
6. `artifact_reproduction` — if present, description of the real/fictional document rendered (photo, letter, obituary, map)
7. `time_layer` — {present_narration, past_scene, deep_past, hypothetical} — multi-layer time is routine
8. `ink_register` — {hatch, wash, flat, duotone} — artist-signature register, held consistent across the book
9. `page_composition` — at what scale this panel sits within the page grid (important because this lane uses full-page composition as a rhetorical tool)

## 9. Three canonical chapter-opening examples

**A.**
My father's library, which I entered for the first time as an adult in the summer after his funeral, contained one hundred and forty-seven books he had never discussed with me and, on the lowest shelf, a row of volumes arranged by a system I had not noticed as a child but recognized immediately at thirty-three: they were shelved by the age at which he had read them. *The Wind in the Willows*, 1954. *Giovanni's Room*, 1958. *The Charterhouse of Parma*, 1962. It was the first evidence I had that he had lived, chronologically, as a reader. The second piece of evidence, which I found in *Giovanni's Room*, was a photograph.

**B.**
The revolution, when it arrived, arrived on a Thursday, which my mother noted at the time because Thursday was the day she went to the fabric market. She did not go to the fabric market that Thursday. No one went anywhere that Thursday. I was ten. I understood, in the way a ten-year-old understands a thing, that history had entered the apartment and was sitting on the couch with my uncle, drinking tea. My uncle said: "Marji, come here." I went. He said: "Remember this." I remember the tea. I remember that his hand, holding the cup, shook. I remember that no one mentioned that it shook.

**C.**
There is a photograph from the summer I turned thirteen that I have spent twenty-two years not looking at. It is a Polaroid. In it, Windy and I are standing on the dock at Awago, in our one-pieces, and we are not smiling. Not sullen. Not sad. Not smiling. The reason I have not looked at this photograph for twenty-two years is not because I remember the day it was taken — I remember the day it was taken with the kind of clarity I reserve for very few things — but because I do not know, and have never known, which one of us asked the adult to take it.

## 10. References
- Alison Bechdel, *Fun Home* author's commentary (Mariner / Houghton Mifflin).
- Marjane Satrapi interview, *The New Yorker*, 2004, and *The Paris Review* No. 189.
- Jillian & Mariko Tamaki interviews, *The Comics Journal* 2014 (on *This One Summer*).
- Hillary Chute, *Graphic Women: Life Narrative and Contemporary Comics* (Columbia UP, 2010).
- Charles Hatfield, *Alternative Comics: An Emerging Literature* (UP Mississippi, 2005).
