# Full-genre-coverage exercise: sports + comedy (focus_sprint_workplace, morning_momentum_workplace, career_lift_workplace, optimizer_workplace)

Planning-only output. 4 brands, 2 genres, 48 episodes each (4 arcs x 12
episodes). No chapter scripts, no storyboards, no CI gates run, no git
actions taken. Acceptance layer for all four plans: `authored_candidate`
(structural arc outlines only — no claimed cure, no brand teacher named
in-panel, self-help topic stays subtext throughout).

## Sources consulted

- `docs/research/manga_craft/sports_competition.md` (full craft bible — read
  in full; `sports_competition: sports` alias per
  `config/manga/canonical_genre_list.yaml`)
- `config/manga/canonical_genre_list.yaml` — comedy row (`id: comedy`,
  `alias_of: null`, pacing alias `gag: comedy`)
- `config/manga/main_character_interaction_grammar.yaml` —
  `comedy: {quality_gate_checks: [dyad_or_group_friction]}`
- `docs/research/manga_craft/workplace_drama.md` (adjacent-register
  reference for both comedy brands, since both are workplace-topic; this
  bible explicitly lists `career_lift_workplace` and `optimizer_workplace`
  among its carried brands, touchstones *Aggretsuko* / *Wotakoi*)
- `/tmp/claude-0/-home-user-pearl-prime/6799991e-03f6-596a-af48-5bfdf3651a9e/scratchpad/genre_assignment_37brands.md`
  (master assignment table)
- Existing repo artifacts checked for continuity before drafting (see notes
  per brand below): `artifacts/manga/chapter_scripts/focus_sprint_workplace__aizawa_yuu__ja_JP__adhd_focus__nine_sounds_one_ball/`,
  `artifacts/manga/chapter_scripts/focus_sprint_workplace__jamie_cruz__en_US__adhd_focus__the_whistle_is_not_the_start/`,
  `artifacts/manga/chapter_scripts/morning_momentum_workplace__taro_beck__en_US__burnout__the_second_lap_is_honest/`

## GAP FLAG — no dedicated comedy craft bible

Confirmed per `genre_assignment_37brands.md` line 68-78: comedy has **no
dedicated craft bible** in `docs/research/manga_craft/`. The two comedy arc
plans below are built from (a) `canonical_genre_list.yaml`'s comedy row,
(b) the `dyad_or_group_friction` quality-gate hint (both comedy brands are
structured around a friction pairing/group that must visibly escalate), and
(c) `workplace_drama.md` as an adjacent-register reference (comic-release
cadence, chibi/SD-insert convention, corporate-vs-private register duality)
since both comedy brands here are workplace-topic — plus general
workplace-comedy manga knowledge (*Aggretsuko*, *Wotakoi*-adjacent register:
deadpan absurdism as the pressure valve for institutional/internal-pressure
content). This gap should be treated as unresolved for any future comedy
work beyond this planning exercise — a real comedy craft bible does not
exist yet in this repo.

---

## focus_sprint_workplace

Genre (this exercise): sports | Primary topic: adhd_focus

Continuity: `sports` is this brand's actual established genre (per
`genre_assignment_37brands.md` continuity note), not a reassignment. A real
ja_JP series already exists (`...aizawa_yuu__ja_JP__adhd_focus__nine_sounds_one_ball`,
a basketball story) and a real en_US chapter script already exists
(`...jamie_cruz__en_US__adhd_focus__the_whistle_is_not_the_start`, a track
relay-sprint story: protagonist Rio Santos, vessel "the coach who watches
feet"). This arc plan stays consistent with the existing en_US vessel
(relay sprint, not basketball) rather than inventing a third vessel, per
the ja_JP-inspiration instruction — light thematic inspiration from the
basketball series' ADHD-focus device, distinct cast/vessel already
established in the merged en_US chapter script is honored, not re-invented.

**Arc 1 (ep_001-012):** Rio joins her company-sponsored inter-corporate
relay league (a scrappy logistics-warehouse team, workplace-adjacent per the
sports-brand pattern) as the newest sprinter. Her ADHD-hyperfocus device is
introduced structurally: her mind "leaves the blocks before her body,"
producing false starts and missed cues in practice, but the same wiring
lets her lock onto the baton exchange with tunnel-vision precision once
the handoff zone opens. First meet is a public failure — a dropped baton
in the exchange zone costs the team the heat.

**Arc 2 (ep_013-024):** A genuine losing streak: Rio's exchange timing
stays inconsistent, teammates start requesting a lineup change, and the
team drops from playoff contention. The coach's minimal-speech correction
("watch feet, not the gun") reframes her problem as rhythm, not attention —
she has been trying to force focus instead of finding the cue that
triggers it naturally. A rival relay team (city league favorites) exposes
the flaw directly by out-exchanging her team twice.

**Arc 3 (ep_025-036):** Breakthrough: a named exchange technique (built in
training-arc failure across several episodes before it lands) crystallizes
Rio's hyperfocus into a repeatable pre-cue ritual timed to the incoming
runner's foot strike, not the sound of the gun. She earns the anchor-leg
slot. A semifinal comeback, run on a fumbled first leg by a teammate,
proves the technique under real pressure — physical cost (the exchange
zone bruise, the burned lungs of an all-out anchor leg) stays visible.

**Arc 4 (ep_037-048):** Championship pursuit at the inter-corporate
regional final. Rio confronts the psychological threshold underneath the
attention problem — the fear that her focus is borrowed, not earned, and
will abandon her exactly when it matters most. She becomes the team's
exchange-zone coach-in-training for a new, more scattered recruit,
reversing the mentorship dynamic established in Arc 1. Final episode
closes on the track and baton alone, no characters in frame, per the
genre's graduation-arc convention.

## morning_momentum_workplace

Genre (this exercise): sports | Primary topic: burnout
Note: reassigned from established genre for full-taxonomy coverage exercise
(see genre_assignment_37brands.md)

Continuity check: an existing en_US chapter script
(`...taro_beck__en_US__burnout__the_second_lap_is_honest`) already carries
`genre: sports_competition` with protagonist Niko Alvarez, vessel "the
coach who watches feet," track discipline. This arc plan is written
consistent with that existing artifact and deliberately uses a *different*
track discipline from focus_sprint_workplace's relay-sprint vessel —
distance/endurance running — so the two sports brands read as genuinely
different sports experiences (team handoff-trust sprint vs. solitary
pacing-and-collapse distance running) even though both sit inside
track-and-field.

**Arc 1 (ep_001-012):** Niko, burned out from a punishing first job, joins
his company's early-morning "walk-to-run" wellness club mostly to escape
his desk, not to compete. His burnout shows up as false urgency: he runs
every rep like a crisis, redlining in the first half of every distance and
collapsing in the second ("the second lap is honest" — the lap that
reveals what the first lap was hiding). First race is a public blowup: he
leads at the midpoint and fades to last.

**Arc 2 (ep_013-024):** A losing streak built entirely from the same
pattern — Niko cannot stop running like he's still escaping something, and
the team (now a real competitive club, not just a wellness program) loses
patience with a runner who front-loads every race. A rival distance runner
who has clearly solved pacing becomes an uncomfortable mirror. Halfway
through the arc, Niko's collapse after a race is severe enough that the
coach benches him — the physical cost of burnout-as-running-style is made
undeniable.

**Arc 3 (ep_025-036):** Breakthrough is explicitly a pacing technique, not
a willpower fix: a named negative-split training method that requires
Niko to run the *first* lap slower than feels honest, trusting the body to
have more left than panic tells him. It fails in training for several
episodes before it lands. First win comes from finishing strong instead
of leading early — the opposite of his Arc 1 instinct.

**Arc 4 (ep_037-048):** Championship pursuit at a regional invitational.
Niko's psychological threshold is the fear that pacing himself honestly
means he doesn't care enough — that burnout-running was proof of
commitment. The final race is a team pacing-group event, not a solo
glory leg, and Niko becomes the one who paces a newer, more frantic
recruit through her own first-half redline. Closes on the empty track at
dawn, no characters, per genre convention.

## career_lift_workplace

Genre (this exercise): comedy | Primary topic: imposter_syndrome
Note: reassigned from established genre for full-taxonomy coverage exercise
(see genre_assignment_37brands.md)

Workplace-comedy escalation shape used: **friction/misfit -> escalating
office chaos -> real cost from the chaos -> earned competence/belonging.**

**Arc 1 — friction/misfit (ep_001-012):** A clerical mix-up (two employees
sharing a near-identical name) lands the protagonist in a "Special
Projects" seat several levels above her actual role, and nobody corrects
it — the avoidance-culture office would rather let the error stand than
have the awkward conversation. She spends the arc improvising competence
in real time: mimicking jargon she half-understands, deflecting direct
questions with vague enthusiasm, comic-release chibi-insert panels showing
her internal panic against a calm corporate-register exterior (per
`workplace_drama.md`'s register-duality convention).

**Arc 2 — escalating office chaos (ep_013-024):** Her improvised cover
stories compound. She recruits two friends outside the company as informal
"consultants" to help her fake a real deliverable, and in the process
half-invents a genuinely buzzwordy internal methodology that starts
spreading through the office on its own, adopted by people who take it far
more seriously than she does. Comic set pieces multiply — meetings where
she has to define terms she made up an hour earlier, a rival colleague who
suspects the truth and turns detection into an office game.

**Arc 3 — real cost from the chaos (ep_025-036):** The invented
methodology gets pitched, without her full knowledge, to a real client or
the board as proprietary company IP — the joke has become load-bearing.
The threat is now genuinely costly: a client deal, a teammate's job, or
her own position on the line when the framework is asked to perform under
real scrutiny it was never built for. The comedy register doesn't
disappear here (per `workplace_drama.md` failure-mode warning against
"comedy without consequence") but it sharpens against real stakes.

**Arc 4 — earned competence/belonging (ep_037-048):** She comes clean
about the origin of the framework — but in the process of repairing the
damage, does the real work the invented version gestured at, and a
refined, honestly-built version survives the exposure. She earns her seat
on the team legitimately, not through the mix-up. Closing beat: she is now
the one covering for a newer hire's small honest mistake, choosing
transparency instead of repeating her own Arc 1 pattern.

## optimizer_workplace

Genre (this exercise): comedy | Primary topic: overthinking
Note: reassigned from established genre for full-taxonomy coverage exercise
(see genre_assignment_37brands.md)

Workplace-comedy escalation shape used: **friction/misfit -> escalating
office chaos -> real cost from the chaos -> earned competence/belonging.**
Deliberately distinct comedic engine from career_lift_workplace: this
brand's chaos comes from over-engineering and excess systematization, not
from concealment or fraud — the friction pairing (per the
`dyad_or_group_friction` quality-gate hint) is the protagonist's optimizing
impulse against a team that just wants a decision made.

**Arc 1 — friction/misfit (ep_001-012):** A new "process efficiency" hire
arrives with a genuine gift for systems thinking and no filter for scale —
she builds an elaborate flowchart to optimize the office lunch-order
rotation, complete with weighted variables nobody asked for. Coworkers are
baffled, then amused, then quietly annoyed as the pattern repeats on
smaller and smaller decisions. Comic-release chibi inserts show her
internal decision-tree branching into absurd depth over trivial stakes.

**Arc 2 — escalating office chaos (ep_013-024):** Her optimization systems
multiply and start competing — a color-coded meeting-room protocol here, a
seating-chart algorithm there — and different departments adopt fragments
of her frameworks incorrectly, creating turf wars between teams each
convinced their version is the "real" one. The office overthinking becomes
literally structural: hallway conversations turn into flowchart debates,
per the genre's corridor-micro-scene convention.

**Arc 3 — real cost from the chaos (ep_025-036):** One of her
over-engineered systems fails at the worst possible moment — an
"optimized" client-escalation protocol requires so many approval steps
that a real emergency gets delayed, causing genuine damage (a lost
account, a missed deadline with real consequences for a teammate). The
overthinking that read as charming precision in Arc 1 is now shown costing
something real, sharpening the comedy against visible stakes per
`workplace_drama.md`'s comedy-without-consequence failure mode.

**Arc 4 — earned competence/belonging (ep_037-048):** She learns to
recognize when *not* to optimize — the threshold skill isn't building
better systems, it's restraint. She builds one deliberately lean,
minimal-step process to replace the tangle she created, and the team
credits her as the one who finally simplified instead of adding. Closing
beat: a new hire arrives with the same overthinking instinct she started
with, and she talks them down instead of matching their spiral — earned
belonging shown through the dyad reversing roles.
