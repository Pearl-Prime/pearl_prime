# School / Coming-of-Age — Craft Bible

> **Genre slug:** `school_coming_of_age` (Genre Shell #14; pacing key `school` per
> `config/manga/canonical_genre_list.yaml` alias line 307 / `manga_pacing_by_genre.yaml` alias line 498).
> Expanded 2026-07-24 from the M3 Wave-1 stub (manga process uplift Lane 05); the stub's reader
> promise, teacher-mode vessel, and anti-patterns are absorbed into §1, §5, and §6 below.
> Touchstones: *March Comes in Like a Lion* (Umino Chica), *Kimi ni Todoke* (Shiina Karuho),
> *Ao Haru Ride* (Sakisaka Io), *My Love Story!!* (Kawahara Kazune / Aruko), *Keep Your Hands Off
> Eizouken!* (Ōwara Sumito), *Heartstopper* (Oseman — Western adjacent), *A Silent Voice*
> (Ōima Yoshitoki — boundary case with `social_issue`).

## 1. Market Contract

Two overlapping readerships buy this lane. The first is the age-matched reader (12–19) living
the school day the story depicts; the second, larger in Western markets, is the nostalgic adult
(20–35) re-reading their own hallway years with the safety of distance. Both arrive for the same
promise: **a specific school day (or week) where the social weather is the plot.** The reader
remembers being watched, graded, and sorted — and wants one honest moment where the protagonist
chooses a smaller, truer move than the performance the room demands.

This is the catalog's widest Western-locale carrier: `config/manga/locale_genre_allocations.yaml`
gives `school_coming_of_age` a secondary-tier share in en_US (10%), es_US (10%), es_ES (10%),
de_DE (8%), hu_HU (8%) and zh_SG (12%), niche in it_IT (8%), zh_HK (6%), zh_CN/zh_TW (2%). The
en_US citation anchors the why: Gen Alpha burnout research (58% report burnout by age 12;
kids/YA audiobook +48%). Wellness content embeds as *inner* arcs inside school genre — anxiety
lives in the test/performance moment, social anxiety at the lunch table and the club-room door.
It is never the marketed topic and never the caption's vocabulary.

Readers will accept: slow-burn misread-signal cycles, chapters where "nothing happens" except a
seat change, ensemble subplots, seasonal-calendar pacing. They will reject: adult-voice captions
that explain the lesson, therapy vocabulary anywhere, melodrama transplanted from drama genres
(a stakes register above what a school week can hold), and instant friend-group salvation.

## 2. Visual Rules

- **Panels per page:** 4–7, avg 5–6. Shojo-register layered compositions at the romance end
  (borderless, overlapping — `manga_genre_writing_styles_2026_04_04.md` line 148); cleaner
  rectangular grids at the club/vocation end (Eizouken register).
- **Words per page:** 50–85 (canonical contract, `manga_pacing_by_genre.yaml` `school` entry
  lines 244–262). The shojo research baseline runs 50–130 (`manga_genre_writing_styles` line
  146); the school pacing contract deliberately caps the ceiling at 85 — school stories breathe
  in the gaps, and the contract enforces the gaps.
- **Words per balloon (max):** 22 (canonical `words_per_balloon_max`).
- **Silent panel %:** 20–40% (canonical `silent_panel_ratio_range: [0.20, 0.40]`). Higher than
  pure shojo (15–25%) because school stories spend silence on corridors, window light, and the
  beat after an almost-said thing.
- **Dialogue:caption ratio:** 45:55 at the shojo-leaning end (inner monologue dominates —
  `manga_genre_writing_styles` line 152), approaching 60:40 in ensemble comedy scenes. Interior
  monologue is the genre's defining channel; captions belong to the protagonist's present-tense
  interior, never to an adult narrator looking back.
- **Reaction-shot frequency:** high (canonical). The reaction shot is the genre's currency —
  the misread blush, the caught glance, the whole-class turn toward a door.
- **Spread frequency:** rare (canonical). Save the spread for one per volume: festival,
  confession, final match of the school year. A spread spent on an ordinary lunch devalues it.
- **Black-fill ratio:** 0.08–0.20. School runs light — fluorescent classrooms, white shirts,
  daylight corridors. Blacks concentrate in uniform blazers, hair, and the occasional dusk
  rooftop scene; a page trending darker than 0.25 is drifting into a different genre's weather.
- **Screentone convention:** emotion-tone at the shojo end (flower/sparkle fields on
  heightened-feeling panels, used knowingly and sparingly); flat 10–30% dot tone for uniform
  fabric and chalkboards; background-erasure (white-out with tone border) for interior-monologue
  panels. `background_density: moderate`, `sfx_usage: decorative` (both canonical) — SFX are
  hand-lettered accents (ドキ, ガタッ, ざわざわ), never action-genre impact type.
- **Line weight:** clean uniform mid-weight; burst lines almost never. Emotional intensity is
  carried by framing distance and tone, not by line violence.

## 3. Pacing

**Structure:** the school calendar is the metronome. Chapters sit inside terms; terms inside a
school year; the year turns on fixed public pressure points (entrance ceremony, midterms, sports
festival, culture festival, finals, graduation). The calendar does the escalation work that
plot-engines do in other genres — the reader always knows what public test is coming next.

**Chapter hook:** open on the social-weather sign, body first. A seat chart posted. A group chat
that went quiet. The protagonist's hands during roll call. Per the absorbed stub skeleton: the
wound beat is a public or semi-public pressure (exam board, club tryout, group project) that
activates the body's alarm — show the body (hands, throat, posture) before any caption names
anything.

**Page-turn triggers (canonical, `manga_pacing_by_genre.yaml` `school.page_turn_triggers`):**
`almost_confession`, `ambiguous_line`, `arrival`, `misread_signal`. End a page on exactly one of
these; never stack two on the same turn.

**Chapter ending:** close on motion, not a moral — walking on, a door left open, the next
station announced. The kept act (stay one minute longer; ask one real question; leave the
performance smile off for a corridor length) lands 2–4 panels before the close; the close
itself is the world continuing.

**Rhythm within a chapter:** pressure sign → performance attempt → slip/misread → private beat
(corridor, stairwell, club room) → turn (a guard slips for one beat) → kept act → motion close.
The private beat is mandatory; a chapter that stays in public register end-to-end reads as
melodrama. Silence panels sit between dialogue exchanges — school stories breathe in the gaps,
and consecutive non-silent panels should not exceed 6.

*(Lane 03's `arc_cadence` blocks landed 2026-07-24 via `9446b3e74e` (#322): the pacing family's
`arc_cadence` block in `config/manga/manga_pacing_by_genre.yaml` is the quantitative authority
for beat cadence; the rhythm above is the qualitative contract.)*

## 4. Dialogue

**Register:** three distinct channels that must not blur.
- *Classroom-public:* performed, compressed, a little too bright. Politeness forms held even
  between friends when the class is listening.
- *Corridor-private:* shorter sentences, dropped particles, real questions. The register shift
  itself is narrative information — the reader hears the guard drop.
- *Interior monologue:* the dominant channel (shojo inheritance, `manga_genre_writing_styles`
  line 152). Present-tense, somatic, specific: "my ears are hot" not "I was embarrassed." Named
  body-feelings live here and only here — never spoken aloud as topic vocabulary.

**Key dialogue patterns:**
1. **The almost-said thing** — a line cut off by a bell, an arrival, or the speaker's own edit.
   The canonical `almost_confession` trigger in miniature; the unsaid half carries the page turn.
2. **The misread signal** — one character's kindness read as pity, or teasing read as contempt;
   the interior monologue and the spoken line diverge on the same panel.
3. **The deflection joke** — humor deployed exactly where the honest answer should go; the
   reader sees the dodge, the other character may not.
4. **The corridor question** — one real question asked in the private register ("Why did you
   quit, actually?"); answered with less than the full truth, which is still progress.
5. **The unsent message** — a text drafted, shown on-screen, deleted. Modern school stories are
   half-lived on phones; message UI panels are a legitimate dialogue surface (keep to ≤2 per
   chapter or the paper texture of the genre dissolves).

**Adult voices:** minimized and functional. A teacher who *models* ease without naming any
doctrine may speak; an adult who explains feelings may not. No therapy jargon anywhere — the
absorbed stub's rule stands: the topic is enacted, never title-dropped ("my anxiety").

## 5. Character

**Protagonist archetype:** a watcher under social grading — someone fluent in reading the room
and over-invested in managing their own legibility. The engine is the gap between performed
self and private self, and the series' arc is that gap narrowing by small kept acts. Never a
blank audience-surrogate; their specific competence (drawing, shogi, film, cooking) gives the
private self somewhere to live.

**Ensemble:** 4–7 recurring classmates/club members with independent wants. The genre requires
at least one relationship where the protagonist is the *senior* (a junior who watches them),
because coming-of-age is measured by what the protagonist models, not only what they receive.

**The vessel (teacher-mode, from `config/manga/manga_mode_vessels.yaml`):** doctrine enters
through a **peer or club ritual** — a quiet upperclassman, a club-room tea ritual, a teacher who
models ease — never a named brand teacher, never an adult monologue. Wound → turn → renewal, per
the absorbed stub: the turn is a guard slipping for one beat, not a lesson delivered.

**Antagonists:** there are none in the villain sense. Pressure comes from systems (exams,
rankings, tryouts), from social gravity (the group's need for everyone to stay in their
assigned seat), and from the protagonist's own performance habit. A bully, if present, is a
person under the same weather, legible sooner or later as such.

*(MC exemplars pending Lane 04 — when the main-character exemplar checklists merge, this
section feeds from them for named-cast scaffolding.)*

## 6. Failure Modes

1. **Adult therapist monologue in a school setting.** The moment an adult explains the
   protagonist's inner state accurately and kindly, the genre is over. Adults may model; they
   may not diagnose.
2. **Topic title-dropped.** "My anxiety," "my self-worth" in dialogue or caption. The embed
   contract is enactment; vocabulary breaks it.
3. **Instant friend-group salvation.** Belonging arrives in millimeters — a seat saved, a
   nickname, an inside joke — never as a single scene where the group embraces the protagonist.
4. **Stakes inflation.** Transplanting drama-genre stakes (expulsion, death, criminal plots)
   to force tension. The genre's whole wager is that a club tryout can carry a chapter.
5. **Adult-lens nostalgia captions.** Retrospective narration ("I didn't know then how much
   that year would matter") converts present-tense weather into a memoir; that is
   `josei_adult_memoir`'s register, not this lane's.
6. **Over-clean hierarchy resolution.** The class's social order should shift, not dissolve;
   a finale where every clique merges into one friend group reads as false.
7. **Reaction-shot spam.** `reaction_shot_frequency: high` is a license, not a quota — three
   identical blush panels per page flattens the one that matters.
8. **Boke/tsukkomi filler drift.** Ensemble comedy beats are seasoning; when the gag rhythm
   takes over chapter structure, the lane has drifted into `comedy` (gag pacing key).

## 7. 48-Volume Shape

48 volumes = **12 terms across four school-year bands**, each band a register of the same
coming-of-age question asked at a new altitude. Unit of structure: the term (one seasonal
pressure point + its private aftermath).

**Volumes 1–12 (Year One — Finding a Room):** arrival, sorting, the protagonist's performance
habit established and first cracked. Band ends with the first kept act witnessed by someone who
matters and the first term the protagonist doesn't dread returning from.

**Volumes 13–24 (Year Two — Naming Wants):** the private competence goes semi-public (club,
contest, festival role). Misread-signal cycles peak here; the ensemble's independent arcs
thicken. Band ends with the protagonist saying one want out loud, in the corridor register, to
one person.

**Volumes 25–36 (Year Three — The Countdown):** exams and goodbyes make the calendar audible.
Seniors graduate out of the ensemble; the protagonist becomes the upperclassman being watched.
Band ends on graduation staged as weather, not triumph — the corridor walked one last time,
in motion, no moral.

**Volumes 37–48 (The Echo Cohort):** a new first-year enters the club/class the protagonist
now anchors; the series re-runs Year-One beats from the senior's seat. The protagonist's old
performance habit reappears in the newcomer, and the renewal is watching the protagonist do for
them what the quiet upperclassman once did — one beat of modeled ease, never a lecture. Final
volume closes on the school gate at the same camera angle as volume 1, walked through in the
opposite direction.

*(Lane 03's `arc_cadence` block (merged 2026-07-24, `9446b3e74e` #322) is the quantitative
authority on volume-band beat counts; the shape above is the narrative contract.)*

## 8. Panel Scaffolding

Per-panel fields for deterministic generation (9 fields):

1. `framing` — ELS / LS / MS / MCU / CU / over-shoulder / phone-screen-insert / corridor-tracking
2. `beat_role` — one of {social_sign, class_pressure, performance_attempt, misread,
   private_beat, almost_confession, kept_act, silence_gap, motion_close}
3. `social_stakes` — one of {solo, dyad, small_group, class_public, school_public}; drives
   register (§4) and reaction-shot eligibility
4. `body_alarm` — boolean; true requires a somatic detail in art or interior caption (hands,
   throat, posture) and forbids topic vocabulary
5. `setting_register` — one of {classroom, corridor, stairwell, club_room, rooftop, gate_walk,
   home_desk, phone_space}; drives black-fill and tone defaults (§2)
6. `calendar_marker` — null or one of {term_start, midterm, sports_festival, culture_festival,
   finals, graduation}; non-null panels may claim the volume's spread budget
7. `dialogue` — ≤22 words per balloon (canonical); null on silence_gap and motion_close panels;
   register must match `social_stakes`
8. `caption` — interior monologue only, ≤18 words, present-tense somatic; never adult-lens
   retrospective; null when the reaction shot carries the beat
9. `silence_flag` — boolean; true on silence_gap, motion_close, and post-almost-confession
   beats; silence_flag=true on ≥20% of panels (floor of canonical 0.20–0.40 range);
   consecutive non-silent panels ≤6

## 9. Locale Weighting

| Locale | Share / tier (`locale_genre_allocations.yaml`) | Notes |
|---|---|---|
| zh_SG | 12% secondary | Exam-pressure resonance (PSLE/O-level culture); bilingual market reads both en and zh editions |
| en_US | 10% secondary | Gen Alpha burnout anchor (58% by age 12); YA/MG graphic-novel shelf; Heartstopper-adjacent discovery |
| es_US / es_ES | 10% secondary each | School-slice manga established via Viz/Planeta pipelines; same YA shelf logic as en_US |
| de_DE / hu_HU | 8% secondary each | European YA graphic market; school register localizes with minimal cultural translation |
| it_IT | 8% niche | Same shelf, smaller market share |
| zh_HK | 6% niche | Exam-culture resonance; Traditional-character edition shared with zh_TW production |
| ja_JP | (in-genre home market) | Native register; competes against the entire domestic school-manga shelf, so catalog allocation favors other genres — craft bar is highest here |
| zh_CN / zh_TW | 2% niche each | School stories present but crowded; allocation favors cultivation/isekai (CN) and horror (TW) |

## 10. References

*Sources (pinned to origin/main `d55f6f397676a72913078efda87657b29c37babe`):*
`config/manga/manga_pacing_by_genre.yaml` `school:` entry lines 244–262 (words_per_page_range
[50, 85], words_per_balloon_max 22, silent_panel_ratio_range [0.20, 0.40], reaction/spread
frequencies, page_turn_triggers, reference corpus: Ao Haru Ride / Kimi ni Todoke / My Love
Story!!) and alias `school_coming_of_age: school` line 498;
`artifacts/research/manga_genre_writing_styles_2026_04_04.md` §3 Shojo lines 139–202 (metrics
table lines 143–152: words/page 50–130, panels 4–7, silent 15–25%, dialogue:narration 40:60,
inner-monologue dominance; panel design as emotional language lines 168–175) and §1 Shonen
lines 24–78 (contrast register for ensemble/club scenes);
`config/manga/canonical_genre_list.yaml` `school` id line 241 and strategic alias
`school_coming_of_age: school` line 307;
`config/manga/locale_genre_allocations.yaml` lines 75–79 (en_US 10% + Gen Alpha citation),
131–133 (es_US), 187–189 (es_ES), 238–240 (de_DE), 294–296 (it_IT), 340–342 (hu_HU), 384–386
(zh_SG), 538–540 (zh_CN), 599–601 (zh_TW), 648–650 (zh_HK);
`config/manga/manga_mode_vessels.yaml` (teacher-mode vessel contract);
predecessor stub: this file's 2026-era M3 Wave-1 version (reader promise, three-act skeleton,
vessel, anti-patterns — absorbed above);
structural template: `docs/research/manga_craft/supernatural_mystery.md`.
