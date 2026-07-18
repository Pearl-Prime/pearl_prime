# Manga Bestseller Story Writing Guide

**Status:** Repo-native manga doctrine
**Scope:** Story architecture, panel planning, writer handoff, and reader-facing QA
**Non-scope:** This guide does not claim that book enrichment automatically flows into manga.

## 1. Core principle

Manga carries transformation through **action, image, consequence, rhythm, and return**. It must not convert self-help prose into speech bubbles.

A reader should be able to enjoy the genre story without knowing a teaching is embedded. The teaching succeeds when it changes what the protagonist notices, chooses, risks, or repairs.

## 2. Genre shell

Every episode must declare one primary genre engine:

- desire or mission
- opposition
- stakes
- escalation rule
- visual promise
- episode hook
- closing propulsion

The genre shell is not decoration. Remove the self-help layer and a functioning story must remain.

## 3. Hook cadence

Required episode rhythm:

1. **Opening image/hook:** a visual question, danger, contradiction, desire, or disruption.
2. **First turn:** the protagonist’s normal strategy produces a cost.
3. **Midpoint pressure:** the strategy is tested under greater consequence.
4. **Choice beat:** the protagonist acts from a changed relationship to the problem.
5. **Closing hook:** consequence, reveal, vow, unresolved relationship, or new threshold.

A chapter ending may be quiet, but it cannot be inert.

## 4. Emotional escalation

Escalation must change at least two of:

- external consequence
- relationship pressure
- identity threat
- bodily activation
- moral cost
- time pressure
- loss of an old coping strategy

Repeating the same feeling at greater volume is not escalation.

## 5. Subtle self-help embed

Approved carriers:

- a choice with visible consequence
- a recurring object whose meaning changes
- an embodied interruption
- a relationship repair
- a failed coping strategy
- a contrast between prediction and event
- an analogy embodied by the setting or action
- a parable embedded as folklore, mission history, or diegetic tale
- a mentor question that changes action rather than delivering a lecture

The embed must be traceable with a `doctrine_id`, but that ID is production metadata—not reader-facing copy.

## 6. Anti-lecture rules

Fail when:

- a character explains the lesson for more than one compact exchange without dramatic resistance;
- narration summarizes what the scene already demonstrated;
- dialogue uses generic instructional framing such as “the lesson is,” “you must understand,” or “here are the steps”;
- the protagonist changes because someone explained the answer rather than because experience forced a choice;
- a teacher character becomes an authorial mouthpiece.

A useful test: remove the explanatory lines. If the teaching disappears entirely, the scene has not embodied it.

## 7. Manga-native metaphor

A metaphor must have:

- a visual source domain;
- a target emotional/mechanistic meaning;
- at least one concrete mapping;
- a changed return later.

Example pattern: a cockpit warning light first reads as proof of danger, later as information that can be checked without surrendering control.

## 8. Manga-native analogy

An analogy clarifies mechanism through action or juxtaposition. It must identify:

- source situation;
- target problem;
- useful correspondence;
- limit of the comparison.

It should shorten understanding, not decorate dialogue.

## 9. Manga-native parable

Parables are sparse and profile-gated. They may appear as:

- local folklore;
- a mission legend;
- a remembered story;
- a contained visual sequence;
- a story told by a character who has something at stake.

Do not label any third-person story a parable. A parable must create a transferable moral pattern and earn its return.

## 10. Teacher mode

Teacher mode is diegetic only.

Allowed vessels:

- mentor encounter
- remembered instruction
- ritual or practice embedded in action
- question that alters a decision
- doctrine carried by a recurring image or rule of the world

Required proof:

- declared mode
- resolved vessel
- vessel beats in story architecture and writer handoff
- no lecture block
- no silent loss between internal architecture and emitted handoff

## 11. Music mode

Music mode is diegetic only.

Allowed vessels:

- rehearsal
- rhythm as tactical coordination
- remembered melody
- sound cue tied to relationship or state change
- silence as contrast
- performance with dramatic consequence

Music must affect story causality. A soundtrack mention alone is not a vessel.

## 12. Panel and chapter contracts

Every planned panel must carry:

- `series_id`
- `episode_id`
- `chapter_id`
- `panel_id`
- `beat_id`
- `doctrine_id` or explicit `none`
- story purpose
- genre function
- emotional delta
- hook/propulsion role
- expected layer role
- lettering locale

Every chapter must prove:

- opening hook
- escalation
- choice/turn
- closing propulsion
- at least one visual carrier of the subtle embed
- no overt lecture failure

## 13. Reader bar

Technical validity is necessary but insufficient. Human blind-read approval must separately judge:

- story coherence
- genre satisfaction
- emotional clarity
- subtlety
- readability
- composition
- desire to continue

No automated score may invent reader approval.
