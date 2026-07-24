# Full-genre-coverage exercise: romance + slice_of_life (confidence_core_romance, creative_unfold_social, relational_calm_iyashikei, night_reset_healing)

Planning-only structural outlines (4 arcs x 12 episodes = 48 episodes) for 4 of
the 37 canonical brands, dispatched under the full-taxonomy coverage exercise
in `genre_assignment_37brands.md`. Craft basis:

- **romance** (`confidence_core_romance`, `creative_unfold_social`): per
  `docs/research/manga_craft/shojo_romance.md` (romance maps via the
  `romance_josei_drama: romance` alias) and `ASSIGNMENT_MATRIX.tsv`'s
  `romance_josei_drama` `arc_shape_hint`: **proximity -> rupture -> repair ->
  commitment-ladder**, 4 arcs x 12 episodes.
- **slice_of_life** (`relational_calm_iyashikei`, `night_reset_healing`): **no
  dedicated craft bible exists in this repo** (confirmed — only
  `BL_slice_of_life.md` exists, which is a queer-relationship-specific
  register and not a general fit here). This section works from
  `config/manga/canonical_genre_list.yaml`'s slice_of_life row
  (`pacing_proxy: healing`, `parent_family: slice_of_life`, `must_include:
  yes`), `config/manga/main_character_interaction_grammar.yaml`'s
  `slice_of_life: {quality_gate_checks: [relationship_or_self_interaction]}`
  hint, and `docs/research/manga_craft/iyashikei_minimalism.md` skimmed as an
  adjacent-register reference only (low-arousal, everyday-texture, no
  cliffhangers, baseline-and-return curve) — **explicitly not treated as a
  substitute bible**, since slice_of_life is warmer and more social than
  iyashikei's atmospheric solitude/near-solo-lead register. In its place, a
  bespoke 4-stage **social/relational escalation** is derived below and
  labeled explicitly per brand, honoring the `relationship_or_self_interaction`
  gate and iyashikei's "no raised stakes / no cliffhangers / return-to-baseline"
  guardrails while allowing the social circle itself to visibly widen across
  arcs (which iyashikei's solo-lead form does not require).

Calibration reference (craft density / escalation-without-cure shape):
`artifacts/manga/chapter_scripts/focus_sprint_workplace__aizawa_yuu__ja_JP__adhd_focus__nine_sounds_one_ball/story_architecture_handoff.json`.

Doctrine applied to all four brands per
`docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/00_MASTER_DISPATCH_PROMPT.md`:
arcs escalate materially arc-over-arc; the self-help topic (imposter syndrome
/ social anxiety / sleep) stays subtext and is never named on-panel; no brand
or coaching program is named in-panel; no claimed cure — acceptance_layer
stays `authored_candidate` throughout, not `bestseller register` or
`system_working`. Each brand below is given a distinct concrete vessel and
cast so the two social_anxiety brands (`creative_unfold_social`,
`relational_calm_iyashikei`) do not read as the same story despite sharing a
topic.

---

## confidence_core_romance
Genre (this exercise): romance | Primary topic: imposter_syndrome
Note: this genre assignment matches this brand's existing catalog genre
(`romance_josei_drama` -> romance alias per `ASSIGNMENT_MATRIX.tsv`) — no
reassignment here; included for full-taxonomy coverage completeness per
`genre_assignment_37brands.md`.

Vessel: Iris Kane, 24, just promoted mid-season from assistant to lead sound
designer at a struggling indie theater company. Love interest: Dez Okafor,
the company's reserved stage manager, who trusts her ear before she trusts it
herself. Proximity engine: tech week — long nights alone together in the
sound booth, headphone cable between two chairs.

**Arc 1 (ep_001-012) — Proximity:** The season opens with Iris's promotion
and Dez as her nightly tech-week counterpart; charged incidental closeness
(shared headphones, notes passed across the booth glass) accumulates while
Iris privately routes every compliment on her cue sheet back to luck or her
predecessor's leftover files, never voiced aloud.
**Arc 2 (ep_013-024) — Rupture:** A live mis-cue during opening night — not
career-ending, but public — gives Iris an excuse to hand credit for the
season's best design choices to a colleague; Dez reads her self-erasure as
disinterest in him and pulls back, and the misunderstanding calcifies over
several weeks of clipped, professional-only exchanges.
**Arc 3 (ep_025-036) — Repair:** Dez notices the pattern isn't about him and
starts leaving her unfinished mixes with his notes instead of praise, forcing
her to defend a choice on its merits; Iris takes one deliberately unguarded
step per episode (crediting a cue in a program note, asking for feedback
before the show instead of after), each rung small and earned, never a grand
gesture.
**Arc 4 (ep_037-048) — Commitment ladder:** As the season closes, Iris is
offered a head-designer post at a bigger house that would separate her from
the company and from Dez; the arc's rungs are her accepting authorship of her
own work publicly (a designer talk, her name above the fold on the program)
and the couple choosing to co-author the next chapter together — the ending
beat is a decision to build the next show side by side, not a wedding or
proposal, rhyming with self-authorship per the genre's closeout convention.

---

## creative_unfold_social
Genre (this exercise): romance | Primary topic: social_anxiety
Note: this genre assignment matches this brand's existing catalog genre
(`romance_josei_drama` -> romance alias per `ASSIGNMENT_MATRIX.tsv`) — no
reassignment here; included for full-taxonomy coverage completeness per
`genre_assignment_37brands.md`.

Vessel: Wren Achebe, 23, a bookbinder who has worked mail-order and alone
from her apartment for two years; economics force her into a table at a
shared print-and-bind studio. Love interest: Theo Marsh, the studio's
gregarious resident muralist, who works loudly two presses down and never
once asks her to explain her silence. Distinct vessel from
`confidence_core_romance` (studio/press floor, daylight, group workspace, not
a theater/sound booth) so the two romance brands read as separate stories.

**Arc 1 (ep_001-012) — Proximity:** Wren claims the quietest corner of the
shared studio; small forced proximities (borrowing the guillotine cutter,
Theo relaying a phone message she didn't hear him take) build without either
of them naming it, and Wren's private rule — never stay past the point where
someone might start a conversation — visibly erodes one shared task at a
time.
**Arc 2 (ep_013-024) — Rupture:** A group-show invitation that would put
Wren's name on a gallery wall triggers a hard withdrawal — she cancels, then
avoids the studio for a stretch — and when Theo's response reads to her as
pity rather than understanding, she overcorrects into a colder, more distant
version of herself that undoes several arcs' worth of proximity gain.
**Arc 3 (ep_025-036) — Repair:** Theo stops trying to talk her back into the
room and instead just keeps her table exactly as she left it, no questions,
which becomes the opening she needed; Wren returns in small, load-bearing
increments (one open studio hour, one piece left out where others can see
it) rather than one dramatic re-entrance.
**Arc 4 (ep_037-048) — Commitment ladder:** The gallery show returns as a
live deadline; the rungs are Wren agreeing to show work under her own name,
then attending her own opening, then — the final rung — proposing she and
Theo co-lease a permanent shared table, a commitment that is professional and
romantic at once, again closing on partnership/authorship rather than a
wedding beat.

---

## relational_calm_iyashikei
Genre (this exercise): slice_of_life | Primary topic: social_anxiety
Note: reassigned from established genre (iyashikei) for full-taxonomy
coverage exercise (see genre_assignment_37brands.md) — deliberate, per
operator instruction.

Vessel: Noa Ibarra, late 20s, takes the overnight shift at Blue Hour, a
24-hour laundromat, specifically because it means fewer people to talk to.
Ensemble, not a couple: Mrs. Odell, the laundromat's elderly owner who folds
towels precisely and says little; Cass, a night-shift ER nurse who does her
wash between shifts; Priam, a delivery cyclist who reads paperbacks in the
plastic chairs. Distinct from both romance brands (no romantic engine at
all) and from `night_reset_healing` (laundromat/social-orbit register, not a
bakery/insomnia register). Escalation label: **Solitary Routine -> First
Thread -> Widening Circle -> Reciprocal Belonging** (a bespoke 4-stage
social/relational escalation, not the romance ladder and not iyashikei's
solo-lead baseline-return curve — derived per this brief's instruction to
build a sensible slice_of_life-specific shape).

**Arc 1 (ep_001-012) — Solitary Routine:** Noa establishes the overnight
shift as a controlled, near-silent routine — nods instead of words, headphones
as a boundary — and the arc tracks the machinery of avoidance in loving
specific detail (which dryer she claims, which hour has the fewest people)
without yet cracking it.
**Arc 2 (ep_013-024) — First Thread:** One recurring regular, Cass, becomes a
specific rather than generic presence — a shared small task (watching each
other's machines so neither has to hover) turns into a standing, wordless
arrangement that is the arc's whole escalation: not a friendship declared,
just a thread that now exists where none did.
**Arc 3 (ep_025-036) — Widening Circle:** A broken dryer becomes a shared
minor problem the whole loose orbit works around together (propping the door,
splitting the remaining machines, Mrs. Odell finally telling the story of why
she never replaced it), and the laundromat's regulars start to register as a
recognized, named group rather than parallel strangers.
**Arc 4 (ep_037-048) — Reciprocal Belonging:** Noa shifts from receiving the
group's low-key inclusion to extending it — she's the one who notices a new,
visibly anxious regular hovering by the door and offers the exact same
small, undemanding thread (watch this machine for me?) that once was offered
to her, closing the escalation on reciprocity rather than a cure or a
declared resolution of her anxiety.

---

## night_reset_healing
Genre (this exercise): slice_of_life | Primary topic: sleep
Note: reassigned from established genre (iyashikei) for full-taxonomy
coverage exercise (see genre_assignment_37brands.md) — deliberate, per
operator instruction.

Vessel: Mira Okonkwo-Lund, early 30s, chronic insomniac who takes an overnight
job at Half-Loaf, a bakery near a hospital that starts its bread proofing at
2 a.m. and sells to shift workers coming off ER rounds. Recurring cast: Sol,
the night baker who's run the ovens for eleven years and treats proofing
times as sacred rather than negotiable; Deja, an ER nurse who becomes a
regular at the same hour every week; Awad, the bakery's overnight security
guard next door, who starts drifting over for the first loaf out of the
oven. Distinct vessel from `relational_calm_iyashikei` (a working overnight
kitchen with a shared craft/ritual at its center, not a waiting-room-style
laundromat) so the two slice_of_life brands don't collapse into each other.
Escalation label: **Solitary Routine -> First Thread -> Widening Circle ->
Reciprocal Belonging** (same bespoke 4-stage social/relational shape as
`relational_calm_iyashikei`, applied to a different concrete vessel and a
different primary topic — sleep rather than social anxiety — so the
throughline is the isolation-of-being-awake-when-no-one-else-is, not
avoidance of people per se).

**Arc 1 (ep_001-012) — Solitary Routine:** Mira takes the overnight bakery
job to have somewhere to be during the hours she can't sleep anyway, and the
arc establishes her private, friendless overnight rhythm — the empty walk to
work, the ovens, the walk home as the city wakes — with Sol as background
presence, not yet a relationship.
**Arc 2 (ep_013-024) — First Thread:** Deja's weekly post-shift stop at the
same hour Mira is proofing the second batch becomes a specific, recurring
exchange — starting as a shared complaint about the hour neither of them
should be awake for, becoming the first thread that turns the bakery from a
job into a place Mira is slightly less alone in.
**Arc 3 (ep_025-036) — Widening Circle:** Awad starts drifting over for the
first loaf out of the oven, then bringing his own thermos, and what began as
two isolated regulars becomes a small standing circle around the proofing
hour — the arc escalates by giving this circle a shared minor stake (Sol's
oven acting up, the circle pooling effort to help her through a bad week)
without ever raising it to melodrama.
**Arc 4 (ep_037-048) — Reciprocal Belonging:** Mira starts tending the
starter herself on nights Sol is out, effectively becoming a keeper of the
ritual rather than just an attendee of it, and begins doing for a new,
visibly sleepless customer what the circle once did for her — the arc closes
on Mira's sleep having improved as a side effect of belonging to the 2 a.m.
hour, not as a claimed cure or a stated resolution of her insomnia.
