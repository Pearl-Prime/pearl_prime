# Josei Adult Memoir / Autobiographical Manga — Style Bible

Touchstones: *My Lesbian Experience With Loneliness* (Nagata Kabi), *My Solo Exchange Diary* (Nagata Kabi), *Solanin* (Asano Inio — josei-adjacent), *Gorgeous Carat*-era Higuri's essay pages, *Kabi Nagata*'s later works, *Goodnight Punpun* extras, Torikai Akane's diaristic seinen/josei hybrids.

## 1. Market + reader contract
Readers are adults 20–40 navigating stalled adulthood — career drift, estrangement, queerness, depression, sexual shame, caregiving. They're here for *recognition*: someone saying the specific quiet thing they've never heard said aloud. They will reject didacticism, therapy-speak, uplift without earned cost, and anything that reads as performance rather than confession.

## 2. Visual grammar
- **Panel count per chapter:** 60–120 panels over 25–40 pages; dense, because interior monologue needs many small containers. Nagata Kabi runs ~4–6 panels/page.
- **Words per page:** 60–140 (high; this is a talky form).
- **Silent-panel ratio:** 10–20% — lower than most lanes. Silences land harder because they are rare.
- **Black-fill ratio:** 0.18–0.35. Two-tone simplicity is common (Nagata Kabi's near-monochrome pink/gray).
- **Screentone density:** Low. Often one or two tones for the whole chapter. Flat fills > textured shading.
- **Spread frequency:** Rare — 0–1 per volume. A spread here marks a *rupture* (psychotic break, hospital, sex scene, parent confrontation).
- **Reaction-shot frequency:** Very high — 2–4 CU reaction panels per page during confessional beats. The face is the stage.
- **Line weight profile:** Light, even, sometimes deliberately amateur. Confident-crafted linework can feel dishonest in this lane; "diary handwriting" line is the register.

## 3. Pacing + beat conventions
- **Chapter length:** 25–40 pages; episodic chapters can extend to 60. Book-format memoirs often publish as single ~140-page units (Nagata Kabi's standalone model).
- **Chapter hook family:** *Confessional pre-emption.* The narrator states the thing the reader expects to be hidden — "I had never been touched" / "I hadn't eaten in three days" — in the first 1–3 panels. Honesty upfront is the hook.
- **Chapter ending convention:** Small honest reversal or unresolved return — "I did it. It didn't fix anything. I slept." Cliffhangers are wrong-register; so are epiphanies. The ending should feel like a diary entry stopping, not a chapter "closing."
- **Scene-to-scene transitions:** Hard cuts with caption-bridge. A caption ("three days later, I was still in bed") does the time-skip work so the art can stay in close, interior frames.
- **Per-volume arc shape:** Single-volume memoirs: linear with one spine event (the escort visit, the breakdown, the mother call). Multi-volume: serialized journal — each volume a season of the same ongoing life.

## 4. Dialogue + narration
- **Register:** First-person, unguarded, self-interrupting. The narrator corrects themselves mid-thought ("I was happy. No — I was relieved.").
- **Narration tolerance:** Heavy. This is the most narration-dense lane in manga. Captions can occupy 40–60% of a page.
- **Dialogue-to-narration ratio:** ~40:60 — inverted from most manga. Dialogue is used for *others*; captions carry the self.
- **Interior monologue:** Handled in running first-person captions, often bleeding across panels, sometimes with small visible thought-fragments ("...no. not that.") inside panel gutters.
- **Tell-don't-show tolerance:** High and *required*. The lane's contract is that the narrator names the feeling. Refusing to name it reads as repression posturing.

## 5. Character + arc conventions
- **Archetype grammar:** The stalled narrator (late 20s, undereating, underearning), the mother-as-weather, the one friend who shows up, the therapist-shaped absence. A confident, well-adjusted lead signals parody or betrayal.
- **Emotional arc per volume:** Not Baseline→Disruption→Return. Rather: *Avowal → Attempt → Aftermath → Honest assessment that things are only a little different.* The genre resists transformation arcs.
- **Cast density:** Solo lead + 1–3 named others. Cast bloat destroys the interiority.

## 6. Failure modes
1. Epiphany endings — "and then I understood myself" resolves what the form requires to stay open.
2. Pretty art. Clean, polished figure drawing reads as vanity; the honesty register needs visible tremor in the line.
3. Third-person omniscience — the moment captions know something the narrator can't know, the pact breaks.
4. Therapy-manual vocabulary ("attachment styles", "inner child") used sincerely rather than quoted.
5. Romance resolution. A new partner fixing the depression retroactively invalidates the memoir's subject.
6. Using manga speed-lines for emotional peaks — the form needs stillness where shonen uses motion.
7. Comedic chibi deflection on the hard beats (acceptable on throwaway gags; fatal during the confession beat).
8. Caption irony that protects the narrator — readers smell the armor immediately.
9. Preaching to the reader ("and that's why you shouldn't…") — breaks the diary pact.

## 7. Series planning implications (48-volume pre-plan)
48 volumes is *enormous* for this lane; no single memoir sustains it. Options:
- **Diaristic serial** (Nagata Kabi's *Solo Exchange Diary* model expanded): 48 volumes = 48 quarters of a life, each with its own small spine event. Plan a 12-year biographical window.
- **Anthology of memoirs** under a common imprint/voice: 48 distinct first-person memoirs by different character-authors in the same EI lineage.
- **Paired-volume confessions**: 24 two-volume memoirs, each a narrator + their later-life reassessment.

Recommended: the diaristic-serial model with explicit season/year labels, quarterly-volume rhythm, and one *retrospective* volume every 8 (volumes 8, 16, 24, 32, 40, 48) where the narrator reads her own earlier volumes back.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (7):
1. `framing` — CU (default), MCU, MS, insert, empty-room, symbolic (bed, ceiling, phone)
2. `beat_role` — {avowal, recollection, attempt, witness, aftermath, self-correction}
3. `caption` — first-person, ≤30 words, can be multi-sentence
4. `dialogue` — other-voice primarily; narrator speaks aloud rarely
5. `face_state` — neutral / averted / wet / chibi-deflect / closed-eye (explicit because faces do 70% of the work)
6. `tone_flag` — one of {flat, single-screen, cross-hatch, solid-black} — controls ink weather
7. `body_posture` — the lane signals emotion through posture (curled, bed-bound, doorway-hesitating, standing-too-still)

## 9. Three canonical chapter-opening examples

**A.**
I hadn't washed my hair in eleven days. I know because I kept a list on the back of a convenience-store receipt, which is a thing I do when I want to prove to myself that I exist on a calendar. The apartment smelled like me, which is to say it smelled like nothing, which is the smell of a person who has stopped going outside. I told myself I would call my mother today. I had been telling myself that for most of the month. The receipt said: Tuesday. The phone said: 4:12 p.m. I made tea I did not drink.

**B.**
The first time a woman touched my hand on purpose I was twenty-six and I had to leave the restaurant to cry in a stairwell. That isn't a metaphor. I actually did that. I remember thinking, in the stairwell, that I was being ridiculous, and then thinking, underneath that, that I wasn't — that my body had decided, without consulting me, that it had been starving. I went back to the table. I apologized for the bathroom line. She smiled like she knew, and she didn't say she knew, and I have thought about that smile for four years.

**C.**
My mother called on a Thursday, which meant she wanted something. My mother calls on Sundays when she wants nothing and on Thursdays when she wants an answer she has already decided on. I let it ring. I let it ring the second time. On the third ring I answered because I am thirty-one years old and I still have not learned how to not answer. "Are you eating?" she said. I looked at the uneaten rice in the pot. "Yes," I said. "Good," she said. We hung up. I threw the rice out and made new rice.

## 10. References
- Nagata Kabi, *My Lesbian Experience With Loneliness* author notes (East Press / Seven Seas edition).
- Nagata Kabi interview, *The Comics Journal*, 2017 (on drawing as therapy and why the line stays "untrained").
- Asano Inio interview, *Pen Magazine*, 2012, on *Solanin* and the adult-stall register.
- Torikai Akane, *Saturn Return* author afterwords.
- Frederik L. Schodt, *Dreamland Japan* — chapter on josei and the diaristic tradition.
