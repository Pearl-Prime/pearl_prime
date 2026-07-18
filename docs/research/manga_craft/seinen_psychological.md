# Seinen Psychological — Style Bible

Touchstones: *Oyasumi Punpun* (Asano Inio), *A Silent Voice / Koe no Katachi* (Oima Yoshitoki), *Homunculus* (Yamamoto Hideo), *Blade of the Immortal* interior chapters, *Dorohedoro* emotional interludes, *Happiness* (Oshimi Shuzo).

## 1. Market + reader contract
Readers are 18–40, primarily male-skewing but broad, expecting emotional risk, moral ambiguity, and craft-conscious page construction. They show up to be *destabilized*: the form promises that the floor will drop, that characters will fail themselves, that the ending will not console. They will reject tidy moral takeaways, pure-victim protagonists, and any beat that rhymes with shonen uplift.

## 2. Visual grammar
- **Panel count per chapter:** 50–90 panels over 20–26 pages (Young Magazine / Big Comic standards). Asano runs slightly denser (~100).
- **Words per page:** 40–110 — variable; dialogue-heavy conversation chapters can spike to 160.
- **Silent-panel ratio:** 25–40%. Silence is weaponized; a character's silence inside a conversation is a key move.
- **Black-fill ratio:** 0.25–0.45. Heavy blacks used for interiority, not horror. *Punpun*'s bird-form character is near-solid black as a psychological flag.
- **Screentone density:** Medium-to-high, varied deliberately. Photorealistic background tone overlays (Asano's signature) juxtaposed with flat abstract character forms.
- **Spread frequency:** 1 per 2–3 chapters; reserved for *dissociation* beats or environmental awe (the god-cloud in Punpun, the festival in *Silent Voice*).
- **Reaction-shot frequency:** High — 3–6 CU reactions per chapter, including *non-reaction* faces (the withheld affect) as a deliberate choice.
- **Line weight profile:** Variable within a single page — clean fine lines on backgrounds (often photo-traced), expressive brush on figures during distress.

## 3. Pacing + beat conventions
- **Chapter length:** 20–26 pages, magazine-serialized. Final-volume chapters commonly 40–60.
- **Chapter hook family:** *Dissonance pre-set* — open on something ordinary (a classroom, a family dinner) that the reader knows is wrong because of last chapter's ending. Or: abrupt in-medias-res on a later scene, then drop back.
- **Chapter ending convention:** *Wound-reveal*. A line of dialogue, an object (a notebook, a chair), or a facial beat that reframes the chapter retroactively. Silence ending > cliff ending.
- **Scene-to-scene transitions:** Hard cuts, symbolic-object bridges (a falling petal in one scene becomes falling ash in the next), and *time-skip captions* that understate ("Three years passed.").
- **Per-volume arc shape:** Volume = one psychological phase. *Punpun* volumes are chaptered around the protagonist's life-stage regressions. A seinen-psych volume typically has a mid-volume collapse and a late-volume false-recovery.

## 4. Dialogue + narration
- **Register:** Naturalistic, clipped, sometimes deliberately flat. Profanity is permitted and load-bearing. Dialogue lies; the art tells the truth.
- **Narration tolerance:** Moderate. Third-person or second-person narration (Punpun's "you") is a strong stylistic move when used; if used, must be used throughout.
- **Dialogue-to-narration ratio:** ~75:25.
- **Interior monologue:** Handled via *symbolic substitution* (Punpun's bird form, Homunculus's trepanation-sight) rather than direct thought captions. When thoughts appear, they are fragmentary and unreliable.
- **Tell-don't-show tolerance:** Low when *positive* feelings are involved (never state "he was happy"); higher when the character is lying to themselves — the stated thought and the panel's truth disagree, and that gap is the art.

## 5. Character + arc conventions
- **Archetype grammar:** The dissociated adolescent, the complicit adult, the girl-who-knows, the charismatic predator, the well-meaning bystander. Deviations carry meaning: a confident, integrated lead signals we're watching their decay.
- **Emotional arc per volume:** Stability (brittle) → stressor → *wrong* response → consequence → new brittle stability at lower altitude. The curve spirals down-and-in across a series.
- **Cast density:** Duo to small ensemble (3–7). Psychological seinen uses dyads intensely — one lead + one destabilizer is the classic engine.

## 6. Failure modes
1. Redemption arcs played straight. The lane's contract is that redemption is partial, ambivalent, or refused.
2. Villain monologues explaining the theme. Theme must stay in the gutters.
3. Mental illness aestheticized without consequence — edgy imagery with no follow-through reads as cosplay.
4. Photo-realist backgrounds with photo-realist figures (destroys the symbolic character register Asano pioneered).
5. Victim purity. Seinen-psych leads must be at least partly complicit or the reader disengages morally.
6. Dialogue that tells the reader what a look just told them.
7. Romantic resolution as psychological resolution — they are different systems.
8. Overuse of spreads — each one costs reader currency.
9. Music-reference name-drops as shorthand for interior life (unless, like *Solanin*, the music IS the subject).
10. Resolving the central ambiguity in the final chapter. *Silent Voice*'s restraint in its ending is the model.

## 7. Series planning implications (48-volume pre-plan)
48 volumes of seinen-psych is at the outer edge of sustainability — reader fatigue is real because the form denies catharsis. Shape:
- **4 × 12-volume psychological eras** of one protagonist's life (child / adolescent / young-adult / adult) — the *Punpun* strategy extended.
- Alternate: **8 × 6-volume "case" arcs** (each a different protagonist in a shared fictional city), ensemble structure similar to *Happiness*/*Homunculus* rotation.
- Each 12-volume era must contain exactly one mid-era collapse (vol 6 of the era) and one false-recovery (vol 10). Volume 48 should NOT resolve; it should *rhyme* with volume 1 at a lower altitude.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (8):
1. `framing` — standard set plus `symbolic_substitute` (e.g., bird-Punpun) and `environmental_inference`
2. `beat_role` — {dissonance_hook, destabilizer, withheld_reaction, wound_reveal, symbolic_bridge, collapse, false_recovery}
3. `dialogue` — can contradict `subtext`
4. `subtext` — what's actually true in the panel (authoring intent; not rendered)
5. `caption` — optional, ≤20 words; 2nd-person allowed
6. `background_register` — photoreal / flat / tone-only / empty — controls the Asano-style character/background dissonance
7. `affect_gap` — integer 0–3 measuring distance between stated emotion and true emotion (0 = aligned, 3 = maximum lie)
8. `sfx` — sparse; interior sfx like heartbeat ("DON") permitted

## 9. Three canonical chapter-opening examples

**A.**
The classroom smelled like the classroom. That was the first wrong thing. Somehow he had expected the room to smell different today, as if the building knew. It didn't. The fluorescent hummed, the girl two rows up uncapped a pen, the teacher wrote a date on the board — yesterday's date, which nobody corrected — and outside the window a bird landed on the sill and looked at him exactly the way his father had looked at him last night. He raised his hand. He did not know yet what he was going to ask.

**B.**
You woke up at 4:07 because that is the time you wake up now. You did not always wake up at 4:07. There was a year, when you were twenty-two, when you slept through the night. You do not know which night was the last one. You lie in the dark and try to locate your body. Your left hand, first. Then the right. Then the ribs. You do not find your face. This is fine, you tell yourself, because a face is not a body part, it is a thing other people see.

**C.**
Shouko signed her name at the reception desk and the man behind it flinched — just a fraction, the flinch of someone who has remembered something they were trying not to remember. She pretended not to see it. She had gotten very good at not seeing things. He slid a visitor's badge across the counter without looking up. "Third floor," he said. "He's expecting you." She thanked him in the voice she had practiced for seven years, the one that did not sound like a voice, and the elevator accepted her and closed.

## 10. References
- Asano Inio interview, *Oyasumi Punpun* Shogakukan author afterwords, 2008–2013.
- Oima Yoshitoki interview, Kodansha *Monthly Shonen Magazine*, 2014 (on *A Silent Voice*'s restraint principle).
- Yamamoto Hideo interviews on *Homunculus* in *Big Comic Spirits*, 2003–2011.
- Tom Gill, "Failed Manhood" essays on seinen psychological form, 2012.
- *Manga! Manga!* (Schodt) — seinen and gekiga lineage chapter.
