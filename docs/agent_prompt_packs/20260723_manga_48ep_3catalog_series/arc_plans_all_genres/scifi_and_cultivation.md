# Full-genre-coverage exercise: sci_fi_cyberpunk + cultivation (digital_ground, qi_foundation_cultivation)

Planning-only structural outlines (4 arcs x 12 episodes = 48 episodes per
brand). No `chapter_script` or `arc_storyboard` files were written; no CI
gates were run; no git actions were taken. Source of truth for this pass:
`docs/research/manga_craft/sci_fi_cyberpunk.md` §7 (48-Volume Shape) and §1
(Market Contract), `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/ASSIGNMENT_MATRIX.tsv`
(`arc_shape_hint` column for `digital_ground`), the existing
`digital_ground__jun_park__en_US__burnout__the_feed_is_louder_than_blood/ep_001.yaml`
listing (protagonist Reno Vale, vessel "the wetware elder / old hacker",
mantra "don't override, settle" — read for continuity, not restated),
`config/manga/canonical_genre_list.yaml` (cultivation row + `taxonomy_fallback`
emotional engines `[aspiration, conviction, mastery]`),
`config/manga/main_character_interaction_grammar.yaml` (`cultivation:
{quality_gate_checks: [rival_teacher_or_self_pressure]}`),
`config/source_of_truth/manga_profiles/brands/qi_foundation_cultivation.yaml`
(reader promise: "You will feel what it is to be rooted. The ground does not
shake if you are the ground."), `config/manga/characters/master_feung.character_design.yaml`
(the brand's locked, in-fiction, non-real-world teacher character), and
`/tmp/claude-0/-home-user-pearl-prime/6799991e-03f6-596a-af48-5bfdf3651a9e/scratchpad/genre_assignment_37brands.md`
(master 37-brand x 25-genre assignment table for the larger exercise this is
one slice of).

**Missing-bible gap (confirmed, cultivation):** `docs/research/manga_craft/`
was listed directly — no `cultivation_martial.md` or any cultivation-genre
file exists on disk (contents: `BL_slice_of_life.md`, `action_battle.md`,
`dark_fantasy.md`, `graphic_novel_us_literary.md`, `historical_period.md`,
`index.md`, `isekai.md`, `iyashikei_minimalism.md`, `josei_adult_memoir.md`,
`kodomomuke_educational.md`, `mecha.md`, `psychological_horror.md`,
`psychological_thriller.md`, `school_coming_of_age.md`, `sci_fi_cyberpunk.md`,
`seinen_psychological.md`, `shojo_romance.md`, `shonen_encouragement.md`,
`sports_competition.md`, `supernatural_mystery.md`,
`teacher_apparatus_per_genre.md`, `webtoon_vertical_drama.md`,
`webtoon_vertical_romance.md`, `workplace_drama.md` — no cultivation entry).
`canonical_genre_list.yaml` only references `cultivation_martial` as a
*pacing-proxy alias id*, not a file that exists. The `qi_foundation_cultivation`
arc plan below is therefore built from `canonical_genre_list.yaml`'s row
description + the interaction-grammar quality-gate hint
(`rival_teacher_or_self_pressure`) + the brand's own locked profile/character
docs + general xianxia/cultivation-genre craft knowledge (power progression
through disciplined practice, sect/circuit politics, rival cultivators,
breakthrough-vs-plateau structure) — **not** a dedicated craft bible, which
does not exist for this genre in this repo.

---

## digital_ground
Genre: sci_fi_cyberpunk | Primary topic: burnout

Continuity: flagship brand, existing `chapter_scripts` listing dir
(`digital_ground__jun_park__en_US__burnout__the_feed_is_louder_than_blood`)
holds one authored pilot episode (Reno Vale, backend engineer inside "the
feed," vessel = an unaugmented old hacker who never gets a lineage name,
mantra "don't override, settle"). That dir is a listing only — this is a
genuinely new 4-arc structure to author into it, not a restatement of ep_001.
Arc shape per `ASSIGNMENT_MATRIX.tsv`: system optimization -> body/identity
cost -> resistance -> re-humanization (mapped onto the craft bible's own
System -> Revelation -> Restructure -> Integration/Rejection macro-cycle).

**Arc 1 — System (ep_001-012):** Reno is a top-percentile engineer inside the
feed's augmentation economy — on-call rotation, cognitive-load overlays,
promotion tracks gated by integration tier. Small, deniable glitches
(a tremor, a notification loop that won't clear, a half-second dropout) get
absorbed as noise because absorbing noise is the job. The arc ends on the
first undeniable anomaly: a mid-shift dissociation episode the feed's own
diagnostics can't explain away, forcing Reno to admit the cost is no longer
theoretical.

**Arc 2 — Body/Identity Cost (ep_013-024):** The toll surfaces as
promotion pressure escalates — a deeper-integration offer dangles against a
worsening tremor, memory gaps, and a growing uncertainty about which thoughts
are Reno's and which are feed-optimized suggestion. The old hacker's "settle,
don't override" practice recurs as a body-based counter-discipline, not
doctrine. A civilian-adjacent colleague who refused augmentation entirely
becomes a visible foil. The arc ends on a forced choice point: accept the
integration upgrade, or risk a health/performance collapse that the system
will read as failure either way.

**Arc 3 — Resistance (ep_025-036):** Reno begins quiet, deniable
non-compliance — micro-refusals, protected analog hours, shielding the
unaugmented colleague from system scrutiny — while still performing enough
competence to avoid flagging. The system's human face partially resolves: a
manager who speaks fluently in latency and throughput metrics, indifferent
rather than cruel, the genre's signature non-villain antagonist. Stakes
personalize as resistance risks real professional and relational cost. The
arc ends on a structural rupture — an incident (outage, health collapse, or
public failure) that makes Reno's private cost impossible to keep private.

**Arc 4 — Re-Humanization (ep_037-048):** Reno redesigns their relationship
to the feed rather than either fully integrating or fully exiting it —
keeping the tools that serve the work, permanently refusing the ones that
required disappearing to use. Supporting characters (the colleague who fully
integrated, the one who fully rejected) are revealed to have been navigating
their own version of the same choice, none of them simply right. The arc
closes on a body-status readout that reads differently than the opening
panel's equivalent — not cured, not victorious, legibly changed. Topic stays
subtext throughout; no brand teacher is named in-panel; acceptance layer
remains `authored_candidate`, not a claimed cure.

---

## qi_foundation_cultivation
Genre: cultivation | Primary topic: somatic_healing

No dedicated craft bible exists for `cultivation` in this repo (see
missing-bible gap note above) — this arc plan is derived from
`canonical_genre_list.yaml`'s row description, the interaction-grammar's
`rival_teacher_or_self_pressure` quality-gate hint, the brand's own locked
profile (`qi_foundation_cultivation.yaml`: reader promise "you will feel what
it is to be rooted"), the brand's existing named in-fiction teacher (Master
Feung — a locked character design, not a real-world teacher, so naming him
in-panel is permitted per the doctrine's real-world-teacher restriction), and
general xianxia/cultivation genre convention. Per the brief, "cultivation" is
kept strictly psychological/somatic: qi, meridians, and cultivation rank map
onto real body-awareness practice (breath, interoception, held tension,
nervous-system regulation), not literal magic mechanics. 4-stage escalation
label (explicit, per instructions): **foundation-building -> plateau/rival
exposure -> breakthrough under real cost -> mastery that changes relationship
to power.**

**Arc 1 — Foundation-Building (ep_001-012):** A new student arrives at Master
Feung's circuit — cultivation rank here is a visible, genre-legible proxy for
how much internal sensation a body can hold without flinching from it. Early
lessons are breath- and stillness-based (qi-sensing as literal
body-scanning), and small, real progress comes fast, seductively fast. The
arc ends on the first plateau: the student stalls at a rank while
faster-advancing peers pull ahead, and the temptation to force progress
through sheer will first appears.

**Arc 2 — Plateau/Rival Exposure (ep_013-024):** A rival cultivator with a
flashier, more forceful technique humiliates the student in circuit ranking
bouts, and circuit-hierarchy pressure (status, sponsorship, a coveted
inner-disciple slot) pushes the student to force qi output past what the body
can actually integrate. The forcing causes a qi deviation — a somatic
crisis (panic, dissociation, a body that stops answering to will) that is the
genre's literalized version of pushing through pain until the system breaks.
Master Feung intervenes not with a lecture but with a practice: sensing
before pushing. The arc ends with the student benched, ranked stalled, and
genuinely afraid of their own practice for the first time.

**Arc 3 — Breakthrough Under Real Cost (ep_025-036):** Recovery forces the
student to locate what the forcing was defending against — an old injury, a
family expectation, a held posture of "I have to be further along than this"
that lives in the body as much as the mind. The rival's forceful technique
begins backfiring too, exposing that their apparent effortless advantage
carried its own hidden cost all along — the genre's rival-as-mirror, not
rival-as-villain. An external circuit-level threat forces the student to act
before they feel ready; the breakthrough that follows comes not from control
but from finally letting a held pattern release, qi moving because the body
stopped fighting itself. The arc ends on a hard-won rank advance that reads
as visibly costly, not triumphant.

**Arc 4 — Mastery That Changes The Relationship To Power (ep_037-048):** The
student's cultivation base is now large enough to dominate circuit rankings
outright — and the arc deliberately does not resolve there. Mastery is
redefined as the capacity to stay regulated under real stakes rather than
raw output; the former rival, now unlearning their own forcing habit,
becomes an ally rather than a defeated obstacle. A circuit-level threat is
resolved through discernment and restraint rather than an escalating power
contest. The arc closes on a technique the student was taught, in Arc 1, to
read as weakness (stillness, yielding, "not advancing") now revealed as the
actual mastery — a closing beat that rhymes with and inverts the opening
lesson. Topic (somatic_healing) stays subtext throughout, carried by
body-practice mechanics rather than named lesson; acceptance layer remains
`authored_candidate`, not a claimed cure.
