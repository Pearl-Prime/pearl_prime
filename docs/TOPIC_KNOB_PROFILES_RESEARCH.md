# Topic Knob Profiles — Research Rationale
*Phoenix Omega V4 | Project: proj_state_convergence_20260328*
*Generated: 2026-04-10 | Authority: spine YAML > bestseller research > engine bindings > experience_defaults*

---

## How to Read This Document

Each section records the reasoning behind the knob profile for that topic. The knob values themselves live in `config/knobs/topic_knob_profiles.yaml`. This document explains why. If you need to override a value, read the rationale first — most of the settings here reflect hard constraints from the spine sequencing_rules, which are inviolable.

**Key principle across all 15 topics:** The spine's sequencing_rules establish when exercises, mechanism depth, and practical framing are permitted. Knob settings can never accelerate past those gates. They can slow down (more conservative settings are always allowed); they cannot speed up past the spine's action_timing without breaking the family contract.

---

## Anxiety

**Knob profile rationale:** The anxiety spine's central insight — that recognition must precede mechanism, and mechanism must precede action — maps directly onto the phase_override structure. Story density is set high because the alarm-system reader needs to feel found before they follow anywhere; the bestseller research validates this with Dare's narrative-first approach outperforming the Anxiety and Phobia Workbook's exercise-dense format in audio. Exercise density is held at none through ch1-4 because the spine explicitly forbids any practice before ch05, and emotional temperature is floored at warm because clinical tone activates more alarm in alarm-system readers.

**Two most dangerous combinations:**
1. `exercise_density: high + emotional_temperature: clinical` in ch1-4 — The action-before-legitimacy failure mode. Clinical exercises land as more threat to the alarm reader. This is the most common failure mode in commercially published anxiety books (source: Goodreads review pattern analysis in bestseller research).
2. `mechanism_depth: high + reflection_depth: high` in ch1-2 — Cognitive front-loading before the body feels seen. Spine ch01 forbidden_moves: "Do not explain the mechanism yet." The reader disengages when they are asked to understand before they are recognized.

**Platform routing:** Do not run anxiety in micro_book_15 or serialized formats. Minimum viable unit is short_book_30. Spotify's myth_killer and atomic structures should be avoided — use promise_engine. The 12-chapter trust arc is the architecture; compression of chapters is acceptable but compression of arc phases is not.

**Key research finding that shaped the profile:** "Narrative anxiety books (Dare, First We Make the Beast Beautiful) perform better in audio. Dare specifically was designed for audio-first consumption." (BESTSELLER_QUALITY_BENCHMARK_RESEARCH.md) This finding establishes that story_density: high is not just a reading experience preference — it is the audio-format-viable path for the anxiety topic.

---

## Grief

**Knob profile rationale:** Grief is the most conservatively profiled topic alongside depression. The spine's family contract — "this family must never feel like progress toward resolution" — prohibits any practical framing before ch09 and any exercise before ch09. Megan Devine's It's OK That You're Not OK (Goodreads 4.37) validates this: 70% witness/validation, 10% practice invitation (framed as invitation, not prescription). The spine's action_timing ("first and only real practice arrives in chapter 9 — later than any other family") is directly expressed in the exercise_density: none floor through ch08 and the absolute ceiling on practical_vs_contemplative: contemplative through ch08.

**Two most dangerous combinations:**
1. `exercise_density: medium` in ch1-8 — This is not suboptimal; it is a spine violation. Any exercise before ch09 carries fixing-energy that breaks the family contract. The grief reader is waiting to feel normal. Prescriptive exercises confirm the book wants them to be different than they are, which is the secondary wound grief books most commonly inflict.
2. `pacing_profile: fast + compression: light` at any phase — Audio listener behavior shows grief readers operate at 0.8x-1.0x playback speed and frequently pause to re-listen. Fast pacing removes the absorption time the reader requires. Completion rates crater.

**Platform routing:** Grief must run in standard_book minimum format. No micro, no serialized. Never use myth_killer or atomic structures for grief. On Audible and Apple Books, promise_engine is appropriate; van_der_kolk structure is borderline because it implies trauma processing arc. The witnessing posture is the governing constraint regardless of platform.

**Key research finding:** "The only grief book that didn't make me feel like I was doing grief wrong." (Goodreads reviews for It's OK That You're Not OK, cited in bestseller research) The entire knob profile is oriented around producing this reader response — which requires that every knob setting honor the non-prescriptive, non-forward-momentum posture through ch08.

---

## Burnout

**Knob profile rationale:** Burnout's distinctive constraint is the optimization instinct: the burned-out reader will immediately apply the same productivity drive that caused the collapse to recovery itself. This means early exercises (even small ones) will be scheduled, measured, and tracked — re-activating the burnout mechanism. The spine warns this explicitly. Exercise density is therefore held at none through ch09 (first practice arrives ch10 — very late). The gladwell_spiral narrative structure is chosen because it mirrors the revelatory quality the Nagoski model (NYT bestseller #1) achieves — gradual unfolding of why the reader's self-diagnosis has been wrong — without requiring early chapter payoff.

**Two most dangerous combinations:**
1. `exercise_density: high + pacing_profile: fast` at any phase — The optimization trigger. High exercises with fast pacing reads as productivity content. This is the most common way burnout books fail — prescribing more optimized rest and self-care as the antidote to over-optimization.
2. `practical_vs_contemplative: practical` in ch1-9 — Spine: "Early action chapters would misfire for this reader — they would turn practice into optimization." Practical framing before ch10 is a structural spine violation.

**Platform routing:** Burnout should not run in micro or serialized format. The grief engine (mourning the pre-burnout self) requires sustained narrative arc that episode format cannot hold. On Spotify, use short_book_30 with promise_engine or gladwell_spiral — never atomic.

**Key research finding:** "Nagoski & Nagoski: story:reflection ratio: 60% story, 25% science, 15% exercise." (bestseller research) The bestseller validation for burnout confirms story_density: high and exercise_density: low. The book that outperforms all others on this topic uses less than one-fifth of its content for exercises.

---

## Self-Worth

**Knob profile rationale:** Self-worth requires the most patient structural setup of the shame-engine topics. The scorecard mechanism must be examined at length before any alternative is offered because the reader's shame response will activate if unconditional worth arrives too quickly — it reads as toxic positivity, as content addressed to less self-aware people. mechanism_depth is set high from ch02 onward because making the scorecard visible is the entire work of the first half of the book. Exercise density is held at none through ch08 (first practice at ch09 per spine action_timing) because premature practice gets co-opted by the same performance pattern driving the problem.

**Two most dangerous combinations:**
1. `spiritual_level: high` in ch1-10 — Any "you are enough" or unconditional worth language before the scorecard is fully visible reads as platitude. The spine: "if the book moves toward unconditional ground too quickly — it will register as toxic positivity." The reader is sophisticated and has heard "you are enough" before. It did not land. Early spiritual framing confirms this book is the same as the others.
2. `exercise_density: medium` in ch1-8 — Premature practice is co-opted by the performance pattern. The reader who runs a relentless scorecard will turn any self-worth exercise into another scorecard item. "Did I do the exercise correctly? Did I feel the right things?"

**Platform routing:** Self-worth must run in standard_book minimum. No micro, no serialized. Never use myth_killer (the scorecard is not a myth — it's a mechanism to examine). Use brene_brown structure on all platforms. Spotify: use promise_engine if brene_brown is unavailable.

**Key research finding:** "Brené Brown discloses her own shame research breakdown as method. Impersonal clinical writing underperforms intimate disclosure in Goodreads reviews and completion rates." (bestseller research) teacher_presence: high with author personal disclosure is the trust mechanism for this topic. The reader needs to see the author inside the same shame experience, not explaining it from the outside.

---

## Imposter Syndrome

**Knob profile rationale:** Imposter syndrome's readers are accomplished by any objective measure. The spine explicitly warns that generic confidence-building content will feel beneath them or addressed to less capable people. This drives mechanism_depth: high from ch02 onward (comparison mechanism must arrive architecturally early — the spine calls this "architecturally essential") and emotional_temperature: warm_clinical (the intellectual respect register, not cheerleading warmth). teacher_presence is set to medium because confessional author disclosure reads as motivational if not grounded in mechanism clarity. The spirituality ceiling is hard at secular — no spiritual reframing of imposter syndrome will land for this reader without the cognitive mechanism being fully established first.

**Two most dangerous combinations:**
1. `emotional_temperature: warm + mechanism_depth: low` in ch1-4 — Generic warmth without intellectual rigor reads as content for less capable people. This destroys trust immediately. The book must demonstrate it understands the mechanism better than the reader's private articulation — the comparison mechanism, not generic self-doubt.
2. `exercise_density: medium` in ch1-8 — The over-preparation instinct will co-opt any early exercise. The reader will prepare thoroughly for the exercise, execute it with hyper-vigilance, and use the results as additional evidence of inadequacy or as a new performance to perfect.

**Platform routing:** No micro or serialized format. Gladwell_spiral is the validated structure — the revelatory unfolding of why evidence cannot accumulate matches this reader's intelligence while honoring the mechanism. Never myth_killer: the reader's imposter feeling is not a myth, it's a mechanism.

**Key research finding:** "Books that treat imposter syndrome as a confidence problem solvable by positive affirmation" and "Books that focus on performing confidence rather than building internal security" both listed under What DOESN'T Work. (bestseller research) The entire knob profile is oriented away from confidence content and toward mechanism precision.

---

## Boundaries

**Knob profile rationale:** The boundaries spine requires a late practice arrival (ch09) despite being a topic where readers explicitly come for scripts and practical language. The temptation to deliver scripts early is strong — Tawwab's bestseller uses scripts extensively — but those scripts only land after the reader has felt the alarm on saying no, seen the cost of obeying it, and understood the mechanism that makes limits difficult. story_density: high with scripts as the delivery vehicle is the late-book exercise format. The practical content is real but delayed — medium exercise density in late book, none in early.

**Two most dangerous combinations:**
1. `exercise_density: high` in ch1-8 — The reader has already tried saying no and felt the guilt flood. Scripts before legitimacy reads as advice they have already received and found insufficient. Tawwab's book earns the scripts over 8 chapters of mechanism and legitimacy before delivering them.
2. `spirituality_level: high + narrative_structure: promise_engine` for secular personas — Faith-based boundaries content (TerKeurst, Cloud) serves a distinct audience. Mixing spiritual framing into secular promise_engine breaks trust for secular readers who are not coming from a faith framework.

**Platform routing:** No micro or serialized format. On Audible and Apple Books, late-book exercises should be script-delivery format (audio-native) rather than worksheets. Scripts for difficult conversations work well in audio — listeners replay them.

**Key research finding:** "Set Boundaries, Find Peace: common reader praise: 'The scripts are gold — I actually used one this week.'" (bestseller research) This validates exercise_density: medium in late book (scripts) and zero in early book. The specific timing is the differentiator — all the practical delivery is in the second half of the book.

---

## Depression

**Knob profile rationale:** Depression and grief share the most conservative ceilings in the set. The spine's "lowest intensity opening of any family" requirement drives slow pacing, reflection_depth: none in early chapters, and the absolute floor of exercise_density: none through ch07. The depleted reader cannot "just start" — their capacity is genuinely reduced, and the book must take that seriously as a physical reality. reflection_depth is capped at medium across all phases because heavy reflection asks while the reader is behind the glass land as confirmation they are broken. The van_der_kolk narrative structure is chosen because it matches the body-first, non-prescriptive model that works for this topic (Lost Connections' journalistic narrative outperforms Feeling Good's exercise density in audio).

**Two most dangerous combinations:**
1. `exercise_density: medium` in ch1-7 — Most dangerous combination for depression. Exercises before ch08 are pep-talk energy. The spine explicitly states: "not 'start with something small' as encouragement, but genuinely tiny as a structural requirement." The reader cannot engage medium exercise density. Goodreads pattern: "Workbooks that pile exercises on a reader who may lack the energy to engage them."
2. `reflection_depth: high` in ch1-5 — Meaning-making cannot come before aliveness returns. Offering heavy reflection while the reader is numb is offering food to someone who cannot taste. The response is not engagement — it is more evidence they are broken.

**Platform routing:** Depression must run in standard_book minimum. No micro, no serialized. Audio chapters should be 18-24 minutes at slow pacing. All late-book exercises must be audio-native (somatic, spoken-instruction) not written. Include explicit pause bridges before any exercise. Never use myth_killer or atomic structures.

**Key research finding:** "Feeling Good underperforms in audio because thought record exercises require writing. Lost Connections performs better in audio — its journalistic narrative is designed for listening." (bestseller research) This finding drives narrative_structure: van_der_kolk and story_density: high for depression. The exercise-dense model fails in the primary delivery format.

---

## Courage

**Knob profile rationale:** Courage is the structural outlier — the only topic where the exercise ramp starts early. The spine states: "the first action ask arrives in ch05 — earlier than in any other family in the set." This drives the mid_book phase_override to exercise_density: medium, while all other topics remain at none or low at that point. The reader came for permission to act and the book must give it — but not by dismissing the fear. The mechanism and legitimacy arc (ch1-4) earns the early action ask. Late book rises to exercise_density: high and practical_vs_contemplative: practical_first — the only topic where practical_first appears at any phase.

**Two most dangerous combinations:**
1. `exercise_density: low + pacing_profile: slow` in ch5-12 — This is courage's unique failure mode. After the alarm is legitimized (ch1-4), slow pacing and low exercise density re-licenses the preparation loop. The reader interprets the book as saying "you need more understanding before you act" — which is exactly what they have been saying to themselves for months or years.
2. `practical_vs_contemplative: contemplative` in ch5-12 — Spine: "permission in this family is primarily permission to act rather than permission to feel or be." Contemplative framing past ch05 returns the reader to gathering-readiness mode. This is the opposite of what courage requires.

**Platform routing:** Courage is the most platform-flexible topic. myth_killer is acceptable on Spotify if the alarm mechanism is named in ch1-3. Atomic structure is acceptable if ch05 delivers the first action ask on schedule. The topic can also run in compression: moderate on shorter formats without losing the essential arc.

**Key research finding:** "Daring Greatly: 55% story, 30% research framework, 15% applied practice." "Books that treat courage as a trait rather than a practice" listed under What DOESN'T Work. (bestseller research) Courage = incremental practice maps directly to the rising exercise_density across the book's phases. story_density: high validates the Brené Brown model.

---

## Overthinking

**Knob profile rationale:** The overthinking reader's primary tool — analytical intelligence — is precisely what gets recruited into the problem. This means the book must honor the intelligence that drives the spiral while showing where it is being misused. mechanism_depth: high is the trust-builder for this reader, not warmth alone. The gladwell_spiral narrative structure mirrors the topic and rewards the reader's analytic orientation without triggering the spiral into a meta-spiral. Exercise density is held at none through ch07 because premature tools will be experienced as dismissive (the reader has already tried tools and found they gave the mind something else to think about). spirituality_level ceiling is hard at secular because "just let go" and "accept uncertainty" are in the prohibited terms — spiritual bypass is the category worst-in-class response for this reader.

**Two most dangerous combinations:**
1. `spirituality_level: moderate + practical_vs_contemplative: contemplative` — This looks safe but is not. Spiritual framing of the spiral as something to release or surrender is the exact move the overthinking reader has tried and found impossible. The spine's prohibited terms include "just accept uncertainty" and "let go." These are not just language rules — they reflect a category error the book must not make.
2. `mechanism_depth: low + story_density: low` at any phase — The overthinking reader came because they are intelligent and they know the problem. Low mechanism + low story means concept-light content, which reads as the generic "stop overthinking" advice they have already dismissed.

**Platform routing:** No micro or serialized format. Never myth_killer for overthinking (the reader's belief is not a myth — it's a partially true belief become a trap). gladwell_spiral is strongly preferred on all platforms.

**Key research finding:** `by_topic.overthinking.reader_intent: understand_self; outcome_type: cognitive_clarity` (experience_defaults.yaml) Reader intent is cognitive clarity, not emotional comfort. This makes mechanism_depth: high the primary driver of the knob profile — more so than for any other topic except imposter_syndrome.

---

## Compassion Fatigue

**Knob profile rationale:** The compassion fatigue spine has a unique posture requirement: the book itself must model the receiving it recommends. This drives story_density: high (giving the reader narratives they can inhabit rather than instructions to follow) and teacher_presence: high with author disclosure of personal caring depletion. The predominant market failure in this topic is the workbook format — "the workbook format feels clinical when I'm already depleted" (reader complaint, bestseller research). The knob profile directly corrects this: narrative-first, exercise-light, with the warmth the caregiver has never received modeled through the prose.

**Two most dangerous combinations:**
1. `exercise_density: high` in ch1-7 — The depleted caregiver evaluates any exercise as another thing to give. The book breaks its core posture (receive the reader) the moment it makes demands. Medium or high exercise density in early or mid book reads as the same extractive dynamic the caregiver is already trapped in.
2. `story_density: low + teacher_presence: low` in ch1-5 — Low story + invisible author gives the reader a concept-heavy book that mirrors the transactional care they're already exhausted by. The spine must model the posture: receive the reader the way the reader has never been received. That requires narrative and author presence.

**Platform routing:** No micro or serialized format. Audio exercises must be somatic (not written) with explicit pause bridges. Dense academic text (the dominant format in the existing compassion fatigue market) underperforms in audio — the narrative-first profile is the audio-viable differentiation.

**Key research finding:** "The first book that named what I was experiencing as a nurse/therapist/teacher." (reader praise for compassion fatigue bestsellers) The recognition-first profile (story_density: high, exercise_density: low, teacher_presence: high) directly produces this response.

---

## Social Anxiety

**Knob profile rationale:** Social anxiety readers are hypervigilant about being evaluated — even by a book. Trust is built through precision of scene description in ch1-3, not through warmth or reassurance. The spine explicitly warns: "The book must not tell the reader they are more interesting than they think. That is condescending and will be rejected." This drives teacher_presence: medium (not high) and the prohibition on any reassuring register. story_density: high is the trust vehicle because scene-level precision creates the "finally someone described the inside" recognition that earns the right to proceed. Exercise density is held at none through ch07 — "no exposure instruction before chapter 8" is explicit in the spine.

**Two most dangerous combinations:**
1. `teacher_presence: high + exercise_density: medium` in ch1-7 — High teacher presence with warm energy activates threat detection. This reader is monitoring for being judged even by the author. Cheerful confessional + early exercises reads as "just put yourself out there" advice delivered with more enthusiasm. Precisely what the prohibited terms list addresses.
2. `exercise_density: medium` in ch1-7 — Spine: "No exposure instruction before chapter 8. The false alarm, shame engine, and safety behavior mechanisms must all be fully in place before any exposure is introduced." Premature exposure is experienced as "just do it" advice and rejected.

**Platform routing:** No micro or serialized format. Never myth_killer for social_anxiety (the reader's belief is not a myth — the threat detection is real). Use promise_engine on all platforms including Spotify.

**Key research finding:** Spine trust_curve: "This reader is hypervigilant about being judged — even by a book." This single sentence from the spine drives the entire profile — high story_density for precision recognition, medium teacher_presence (not warm cheerleading), and the longest gap before any exposure instruction of the false_alarm topics.

---

## Sleep Anxiety

**Knob profile rationale:** Sleep anxiety's central paradox — effort is the enemy of sleep — must be established early and held through the entire book. This means the book explicitly cannot offer a better sleep protocol. Any exercise that looks like a technique re-activates the performance orientation the book is designed to dismantle. exercise_density ceiling is low (not medium or high) because even light exercises will be used as sleep performance tactics by this reader. The control-seeking reader reads everything through the lens of "is this another thing I can try?" The knob profile is designed to consistently answer: no, this is understanding, not technique.

**Two most dangerous combinations:**
1. `exercise_density: medium` at any chapter — The #1 failure mode for this topic. Any exercise framed even loosely as a technique re-engages the protocol orientation. Reader's invisible script: "Sleep is the one thing I can't optimize my way into, and that terrifies me more than actual insomnia." Medium exercise density confirms the book is offering more things to try.
2. `spirituality_level: moderate + practical_vs_contemplative: contemplative` in ch1-6 — Spiritual framing before the paradox is named reads as yet another thing to try (try accepting, try surrendering). The control-seeking reader will attempt to control their acceptance. Spiritual + contemplative in early chapters is particularly dangerous for this reader.

**Platform routing:** Sleep anxiety is audio-native (bedtime listening context). Audible and Apple Books are the primary platforms. myth_killer is acceptable on Spotify only if the paradox naming occurs before the myth-kill move. Late-book exercises must be somatic, spoken-instruction only, with slow pacing and deliberate breath points.

**Key research finding:** Invisible script: "I can't sleep because I'm thinking about not being able to sleep, and that spiral is the most honest thing about me." (04_invisible_scripts.yaml) The meta-spiral (thinking about not sleeping) is the precise recognition moment that earns trust. story_density: high anchored in the specific bedtime scene — clock-watching, internal monologue of effort, the irony of trying to stop trying.

---

## Financial Anxiety

**Knob profile rationale:** Financial anxiety is an avoidance and shame pattern. The reader may or may not have real financial problems, but the anxiety operates independently of the facts. This means the shame must be addressed before any financial instruction is possible — not because the instruction is wrong, but because shame is blocking cognition. exercise_density: none floor through ch07 is the direct implication: no financial action before shame is named (ch05 per spine mechanism_timing). The book is explicitly not a personal finance manual, which sets the ceiling on practical content throughout.

**Two most dangerous combinations:**
1. `exercise_density: medium` in ch1-7 — Reader cannot act while shame is unnamed. Any financial exercise before ch08 will either be skipped (shame blocks it) or completed with white-knuckled avoidance (which re-activates the shame). The reader came because they cannot look at their bank account. Asking them to do so before naming the shame is asking them to do the exact thing they cannot do.
2. `spirituality_level: moderate + practical_vs_contemplative: balanced` in ch1-6 — "Abundance mindset" financial frameworks invalidate the real avoidance experience. The reader is not failing to attract abundance — they are unable to look at their bank account because looking feels unsurvivable. Spiritual money frameworks are not merely inaccessible; they actively deny the reader's real experience.

**Platform routing:** Flag all financial_anxiety content for locale-specific content moderation review before publishing to zh-CN platforms. On Spotify, use promise_engine. myth_killer is acceptable only if shame engine is fully named in ch1-5 before the myth is named.

**Key research finding:** "I Will Teach You to Be Rich: Ch. 1 reframes 'rich' as a personal definition rather than a number — immediately reduces shame." Common reader praise: "Finally a money book that doesn't make me feel stupid." (bestseller research) Shame reduction before instruction is the #1 validated move for financial content. The knob profile extends this — shame reduction requires the entire first seven chapters in the financial_anxiety spine.

---

## Financial Stress

**Knob profile rationale:** Financial stress is distinguished from financial anxiety by one crucial fact: the threat response is proportionate to a real threat. This means the profile cannot minimize or reframe the stress — it must honor the real weight first. The spirituality ceiling is the hardest ceiling in the set: spiritual framing at any level above secular is a spine violation before ch11. Consumer language shows readers who are calculating safety margins even when objectively stable, and invisible scripts show readers under real pressure regardless of income. "Abundance mindset" content is not merely ineffective — it actively invalidates the real threat experience and destroys trust.

**Two most dangerous combinations:**
1. `spirituality_level: moderate` in ch1-10 — The most dangerous combination for financial_stress, harder even than for financial_anxiety. The real-hardship reader who is managing real debt, real job threat, or real income shortfall reads any spiritual money framework as evidence the book doesn't understand their situation. This breaks trust before any meaningful content can be delivered. This is the hardest spirituality ceiling of all 15 topics and applies through ch10.
2. `practical_vs_contemplative: practical` in ch1-7 — Spine: "Emotional regulation is prerequisite to practical action, not a supplement to it." The real-hardship reader is often told to "just make a budget" or "just cut expenses" by people who do not understand that shame and overwhelm are blocking cognition. Practical-first framing in early chapters replicates that invalidation.

**Platform routing:** Flag all financial_stress content for locale-specific content moderation review for zh-* locales. promise_engine is the validated structure. If myth_killer is used, ensure the myth is the shame-based belief that the situation is unsurvivable — not the real hardship itself.

**Key research finding:** Invisible scripts: "I make good money and still live like I'm one mistake away from losing everything" AND "I have money but I don't have security, which is the opposite problem but feels just as terrifying." (04_invisible_scripts.yaml) These two scripts, covering both objectively stressed and objectively stable readers, establish that the emotional weight of financial stress operates independently of actual figures. This is the research basis for the hard spirituality ceiling: real-feeling threat cannot be reframed as abundance.

---

## Somatic Healing

**Knob profile rationale:** Somatic healing is built around one non-negotiable spine rule: observation-before-intervention. The reader who has been living at a distance from their body for years must learn to notice before they work with what they notice. This drives the absolute exercise_density: none floor through ch05 and the hard ceiling on exercise_density: low throughout the book (catharsis-seeking is explicitly prohibited by the spine). The van_der_kolk narrative structure is the direct model — body-naming before mechanism, mechanism before practice, practice built through titration not intensity. The promise of dramatic somatic release is prohibited by the spine and must not be implied by any knob setting.

**Two most dangerous combinations:**
1. `exercise_density: medium` in ch1-5 — The most structurally critical constraint for somatic_healing. The spine labels observation-before-intervention "non-negotiable." Any exercise before ch06 breaks the observation orientation: the reader who has been routing around their body will treat early exercises as another form of doing-at-the-body. The exercise will be completed as performance, not as observation — which reinforces the body-distance rather than reducing it.
2. `exercise_density: high` at any chapter — The spine explicitly prohibits the expectation of catharsis or dramatic release. High exercise density implies volume and intensity — the opposite of titration. The reader who has been living at a distance may push through exercises to produce the promised release, exceed their actual capacity, and retreat further from the body than before.

**Platform routing:** No micro or serialized format. Audible and Apple Books are the primary platforms; somatic instructions work well in audio with slow pacing and deliberate breath points. All exercises must be somatic and spoken-instruction only — no written exercises for this topic in audio format. The observation arc (ch1-5) must not be compressed.

**Key research finding:** "The Body Keeps the Score: Ch. 1 names hypervigilance somatically before explaining the nervous system → shifts to exercises in later chapters." 376+ weeks NYT Paperback Nonfiction bestseller list. (bestseller research) This is the direct model: body-naming, then mechanism, then late practice arrival. The single most commercially validated somatic self-help book uses the exact sequence the somatic_healing spine prescribes. narrative_structure: van_der_kolk is the research-backed structural choice.

---

## Cross-Topic Pattern Summary

| Topic | First Exercise Chapter | Spirituality Ceiling | Exercise Density Default | Most Distinctive Knob |
|-------|------------------------|---------------------|--------------------------|------------------------|
| anxiety | ch05 | moderate | medium | pacing_profile: measured |
| grief | ch09 | moderate | low | practical_vs_contemplative: contemplative |
| burnout | ch10 | secular | low | practical_vs_contemplative: contemplative_first |
| self_worth | ch09 | moderate | low | mechanism_depth: high |
| imposter_syndrome | ch09 | secular | low | emotional_temperature: warm_clinical |
| boundaries | ch09 | moderate | medium (late book only) | narrative_structure: brene_brown |
| depression | ch08 | moderate | low | pacing_profile: slow |
| courage | ch05 | moderate | medium → high | exercise_density ramp (earliest of all 15) |
| overthinking | ch08 | secular | low | mechanism_depth: high |
| compassion_fatigue | ch08 | moderate | low | story_density: high |
| social_anxiety | ch08 | secular | medium (late book only) | teacher_presence: medium |
| sleep_anxiety | ch09 | secular | low | exercise_density ceiling: low (all phases) |
| financial_anxiety | ch08 | secular | low | spirituality_level ceiling |
| financial_stress | ch08 | secular (hardest ceiling) | low | spirituality_level: secular (inviolable) |
| somatic_healing | ch06 | moderate | low | exercise_density ceiling: low (non-negotiable) |

**Three topics with secular-only spirituality:** imposter_syndrome, overthinking, sleep_anxiety (reader populations are control-oriented and reject spiritual bypass)

**Hardest spirituality ceiling:** financial_stress (secular floor applies through ch10 — real hardship reader cannot receive spiritual money frameworks without trust collapse)

**Earliest exercise ramp:** courage (ch05 — only topic with mid_book exercise_density: medium)

**Latest exercise arrival:** grief and burnout (ch09 and ch10 respectively — the two most conservative ceilings)

**Observation-before-intervention as non-negotiable spine rule:** somatic_healing only (unique designation; other topics have sequencing constraints but only somatic_healing uses "non-negotiable" language in the spine)
