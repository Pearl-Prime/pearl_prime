# BL / Boys' Love Slice-of-Life — Style Bible

Touchstones: *Given* (Kizu Natsuki), *My Brother's Husband* (Tagame Gengoroh), *What Did You Eat Yesterday?* (Yoshinaga Fumi), *I Hear the Sunspot* (Fumino Yuki), *Our Dining Table* (Noda Ryo), *Doukyuusei* (Nakamura Asumiko).

## 1. Market + reader contract
Readers are primarily adult women (core) plus queer men and nonbinary readers (growing share), 20–45, seeking *emotionally textured queer stories* where intimacy is earned and domesticity/everyday-life carries as much weight as romance. They're here for *tenderness, specificity, and the texture of two lives merging*. They will reject: non-con played romantically, seme/uke caricature, tragic-gay endings, and queer identity treated as plot-contrivance.

## 2. Visual grammar
- **Panel count per chapter:** 45–75 panels over 30–40 pages (magazine standard — *Cheri+*, *Dear+*, *Monthly Action*).
- **Words per page:** 35–80.
- **Silent-panel ratio:** 25–40% — intimacy lives in silences: a hand on a shoulder, a shared kitchen glance.
- **Black-fill ratio:** 0.18–0.30. Hair and clothing provide most blacks.
- **Screentone density:** Medium, restrained. Ornamental tone is used sparingly compared to shojo; more naturalistic.
- **Spread frequency:** 1–2 per volume. Reserved for intimacy peak (first kiss / sex scene opening) OR for ordinary-domestic-tableau beats (Tagame's full-page dinner scene).
- **Reaction-shot frequency:** Medium-high — 3–6 per chapter, often the *other partner's* reaction to the narrator's action.
- **Line weight profile:** Medium, warm. Many contemporary BL artists use sensitive variable-weight brush lines; character designs skew slightly more realistic than shojo.

## 3. Pacing + beat conventions
- **Chapter length:** 30–40 pages.
- **Chapter hook family:** *Domestic particular* — open on a specific shared object or moment: a rice cooker timer, a shared umbrella stand, the guitar case by the door. The hook is *the weight of everyday belonging*.
- **Chapter ending convention:** *Small held moment* — a cup of tea set down, a partner asleep, a door closed gently. Cliffhangers work in BL-thriller subgenres but are wrong for slice-of-life BL.
- **Scene-to-scene transitions:** Domestic-object bridges (the rice cooker in scene A becomes the bowl in scene B), hard time-cuts with caption ("the next week"), kitchen/bedroom spatial jumps.
- **Per-volume arc shape:** Volume = one stage of relationship deepening. *Given* vol 1: recognition and instrument-borrowing; vol 2: band formation and grief reveal; etc. Intimacy beats are distributed across the series — first kiss is rarely volume 1.

## 4. Dialogue + narration
- **Register:** Naturalistic, adult, often quietly funny. Men speaking to men in their own registers — not shojo-heroine-inflected.
- **Narration tolerance:** Moderate. First-person caption narration is common but alternating POV (one chapter his, next chapter his) is the signature tool.
- **Dialogue-to-narration ratio:** ~65:35.
- **Interior monologue:** Calm, often hesitant. A lot of "I didn't know how to say —" followed by action that says it.
- **Tell-don't-show tolerance:** Moderate for interior confusion ("I didn't know what this was yet"), low for emotion labels — the relationship must be shown to deepen.

## 5. Character + arc conventions
- **Archetype grammar:** Two adults (or high-schoolers in the high-school subgenre) with complementary-but-not-opposite emotional profiles. Deviations from seme/uke binary are *positively* marked in modern BL: readers prefer mutual, negotiated intimacy. Tagame's Yaichi-Mike (brother-in-law vs widower) is an exemplar of adult-complementary pairing.
- **Emotional arc per volume:** Proximity → hesitation → small vulnerability shown → small vulnerability received → slightly more integrated daily life. The arc is *merging of routines*, not conquest.
- **Cast density:** Duo primary + a supportive circle of 3–6 (bandmates, coworkers, family). *My Brother's Husband* adds the niece as a crucial third POV — children in BL slice-of-life are a powerful lens and not a taboo.

## 6. Failure modes
1. Non-con or dub-con played as romance. Modern adult BL readers reject this; it is a legacy trope that has retired.
2. Seme/uke role caricature — dominant/submissive body-type shorthand reads as dated.
3. Tragic queer ending (illness/death/closeting as resolution) — the lane's contract is that queer life continues.
4. Homophobia as primary antagonist without specific texture — external homophobia handled abstractly reads as lazy; specific, grounded homophobia (a relative, a coworker) is welcomed.
5. Straight-audience explainer captions ("In Japan, same-sex marriage is..."). Either commit to the audience or don't.
6. Intimacy beats (kiss, sex) without relational preparation — readers feel the skip.
7. Absent domesticity — BL slice-of-life requires *cooking, cleaning, errands* as emotional territory.
8. Equating a sex scene with resolution.
9. Infantilized adult characters for "cute" effect.
10. Ignoring age/power dynamics honestly where they exist (teacher/student, boss/employee — lane now demands acknowledgment, not aestheticization).

## 7. Series planning implications (48-volume pre-plan)
48 volumes far exceeds typical BL slice-of-life length (most run 3–10). Structure:
- **Primary couple arc: volumes 1–12** (recognition → cohabitation → family-integration → quiet crisis → resolution).
- **Volumes 13–24:** secondary couple in the same friend-group (*Given*'s Akihiko/Haruki model).
- **Volumes 25–36:** third couple, possibly intergenerational (*My Brother's Husband* register).
- **Volumes 37–48:** original primary couple aging / adoption arc / the queer life-continuing arc the lane exists to depict.
- Each 12-volume arc must deliver: 1 first-kiss, 1 first-I-love-you, 1 family-integration beat, 1 crisis, 1 resolution. Crucially, no breakups-for-drama; conflicts resolve through communication.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (8):
1. `framing` — CU / MCU / MS / MS-two-shot (core BL frame) / insert / domestic-tableau
2. `beat_role` — {domestic_particular, proximity, hesitation, shown_vulnerability, received_vulnerability, merge_moment, held_silence}
3. `pov` — which partner (alternates by chapter conventionally)
4. `dialogue` — ≤20 words; adult register enforced
5. `interior_caption` — hesitation-inflected, ≤25 words
6. `domestic_object` — the specific object/task in frame (coffee maker, tuning peg, laundry, a letter from family) — required on ≥50% of panels
7. `physical_proximity` — integer 0–5, must be permitted to *hold* (not always trending up)
8. `consent_frame` — for any intimacy panel, the prior panel must establish consent (explicit look, verbal, or settled prior context) — enforcement flag

## 9. Three canonical chapter-opening examples

**A.**
The guitar had been in the umbrella stand for six days. Mafuyu did not know that it had been in the umbrella stand for six days; he only knew that Uenoyama had not mentioned it, and that the rain had stopped on Tuesday, and that the umbrellas no longer needed to stand anywhere in particular. He walked past it on his way to the kitchen. He walked past it on his way back from the kitchen. On the third pass he stopped, put a hand on its case, and said, quietly, to no one: "Okay." Uenoyama, from the other room: "Okay what?" "Nothing." A pause. "Everything."

**B.**
Yaichi had not made breakfast for three people in eight years. He stood at the counter in the pale kitchen light, counting bowls — one for Kana, one for himself, one for Mike, whose name he still, on the third morning, had to think about before saying. Three bowls. Three pairs of chopsticks. Three eggs, because Mike had learned the word for egg on day one and had asked, yesterday, in careful Japanese, whether there were eggs. Kana padded in, rubbing her eye, and said: "Is Uncle Mike awake?" Yaichi said: "Not yet." She sat down, patient, at the third seat.

**C.**
Shiro came home on Friday with a second sea bass, because Kenji had said, on Tuesday, that the sea bass on Sunday had been very good. This was — Shiro reflected, taking the fish out of the paper and laying it on the cutting board — a dangerous precedent. If he bought a second sea bass every time Kenji complimented a fish, there would be no money left for retirement. He made a note, severely, to be more economical. Then he opened the freezer and began removing things to make room, because he had, in fact, also bought a third sea bass for Saturday.

## 10. References
- Tagame Gengoroh, *My Brother's Husband* author afterwords (Futabasha) — on drawing queer family life for a mainstream seinen magazine.
- Kizu Natsuki interview, *Cheri+* 2016, on *Given* and slow-relationship pacing.
- Yoshinaga Fumi, interview in *Eureka* (special BL issue), 2007.
- James Welker, ed., *Queer Transfigurations: Boys Love Media in Asia* (U. Hawaii Press, 2022).
- Mark McLelland, *Boys' Love Manga and Beyond* (UP Mississippi, 2015).
