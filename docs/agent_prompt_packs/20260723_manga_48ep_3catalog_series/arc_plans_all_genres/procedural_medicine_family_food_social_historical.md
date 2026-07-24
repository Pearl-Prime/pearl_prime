# Full-genre-coverage exercise: procedural + graphic_medicine + family + food + social_issue + historical (minimal_mind_healing, body_memory_shojo, sleep_restoration_iyashikei, heart_balance_shojo, resilient_parent_social, relationship_clarity_romance)

Planning-only output. Structural 4-arc/48-episode outlines. No chapter scripts, no
panel scaffolding, no CI-facing artifacts. Self-help topic stays subtext delivered
through genre mechanics per `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/00_MASTER_DISPATCH_PROMPT.md`
— no teacher-mode lecturing, no brand named in-panel, no claimed cure.
`acceptance_layer` for all six of these outlines is `authored_candidate` at most.

## Craft-bible coverage note (read before using this file)

Per `genre_assignment_37brands.md` and confirmed directly against
`docs/research/manga_craft/`:

- **historical** — dedicated bible EXISTS: `docs/research/manga_craft/historical_period.md`,
  reachable via the `historical_period: historical` alias in
  `config/manga/canonical_genre_list.yaml`. Used directly below (three-era/four-stage
  saga shape, era-force-as-antagonist, grief-across-time, outsider/heir/witness
  protagonist entry points).
- **procedural, graphic_medicine, family, food, social_issue** — **NO dedicated craft
  bible exists** in `docs/research/manga_craft/`. This is a confirmed gap, not an
  oversight in this pass. These five sections were built from
  `config/manga/canonical_genre_list.yaml` row data (labels: "Procedural",
  "Graphic Medicine / Therapeutic Essay", "Family", "Food", "Social Issue / Josei
  Realism"; all five are pacing-only or taxonomy rows with no prose description
  field beyond label + parent_family), `main_character_interaction_grammar.yaml`'s
  `quality_gate_checks` hints (quoted per-brand below), and general
  manga/webtoon genre craft knowledge (procedural = protocol/systems workplace-adjacent
  drama; graphic medicine = Western graphic-medicine tradition, illness/patient-body
  register, *Marbles*/*Cancer Vixen* adjacent; family = multi-generational household
  drama; food = kitchen/restaurant craft-vessel drama; social_issue = a named social
  pressure carried through family/community lens, josei realism register). **A future
  pass should commission real craft bibles for these five genres** — this outline
  should not be read as a substitute for that work.

---

## minimal_mind_healing
Genre (this exercise): procedural | Primary topic: overthinking
Note: reassigned from established genre (psychological_thriller) for full-taxonomy
coverage exercise (see genre_assignment_37brands.md)
Craft-bible gap: no `docs/research/manga_craft/` bible for procedural. Built from
canonical_genre_list.yaml label ("Procedural") + interaction-grammar hint
`quality_gate_checks: [authority_team_or_system_pressure]` + general procedural-drama
craft knowledge.
Vessel: a municipal police bureau's **Missing Persons Cold-Case Review Unit** —
a small, under-resourced desk that reopens files everyone else closed. Protocol,
paperwork, and chain-of-custody are the visible engine; the overthinking topic
lives entirely in how the protagonist works a file, never in named self-help terms.

**Arc 1 (ep_001-012) — Intake:** Protagonist transfers into the Cold-Case Review
Unit and learns its procedural backbone: file protocol, cross-referencing, the
rule that every reopened case needs a second signature. Their compulsive
re-checking and inability to let a detail go reads as a liability to the unit
captain and a strength on the page — closed low-stakes cases turn on the detail
everyone else skipped. Authority pressure established: the captain audits their
case-closure rate.

**Arc 2 (ep_013-024) — The file that won't close:** A reopened case turns out to
intersect the protagonist's own family history (an old, unresolved disappearance
from their childhood neighborhood). System-pressure escalates: the unit's
authority to keep the case open is challenged by a superior who wants it
re-shelved, forcing the protagonist to defend process itself, not just the case.
Team dynamics shift as a partner starts covering for the protagonist's spiraling
re-checks.

**Arc 3 (ep_025-036) — Audit:** Budget cuts threaten the unit; an internal-affairs
review scrutinizes its closure methods, putting the protagonist's obsessive
protocol under formal institutional pressure. A high-visibility case (a
politically sensitive disappearance) forces the team to work under scrutiny while
the protagonist's overthinking nearly derails a live lead through paralysis —
the team's system, not the protagonist alone, has to hold.

**Arc 4 (ep_037-048) — Standard of practice:** The capstone case ties Arc 2's
personal thread to a resolution that is procedural, not miraculous — closure
comes through the unit's process working as designed, with the protagonist's
thoroughness now written into the unit's actual protocol rather than treated as
a personal flaw. The unit survives the audit. The personal case is laid to rest
in a way that is factual and incomplete, not a clean catharsis.

---

## body_memory_shojo
Genre (this exercise): graphic_medicine | Primary topic: somatic_healing
Note: reassigned from established genre (iyashikei) for full-taxonomy coverage
exercise (see genre_assignment_37brands.md)
Craft-bible gap: no `docs/research/manga_craft/` bible for graphic_medicine. Built
from canonical_genre_list.yaml label ("Graphic Medicine / Therapeutic Essay",
`parent_family: essay`) + interaction-grammar hint `quality_gate_checks:
[patient_care_or_family_pressure]` + Western graphic-medicine tradition
(*Marbles*, *Cancer Vixen* adjacent — illness/patient-body register, not shonen
battle-injury recovery).
Vessel: a hospital **orthopedic rehabilitation ward** after a serious accident —
patient-care register throughout: ward rounds, physical therapy sessions, the
patient community in shared rooms. Somatic_healing plays out literally as the
body relearning itself, never narrated as therapy-speak.

**Arc 1 (ep_001-012) — Admission:** Protagonist wakes in the rehab ward after an
accident with a body that no longer moves or feels the way it used to —
dissociation from the body is the entry state. Ward routine (rounds, PT
schedule, roommates) establishes the vessel. Family pressure begins here: family
visits carrying their own fear, wanting a faster "back to normal" than the body
allows.

**Arc 2 (ep_013-024) — Relearning:** Physical therapy becomes the spine of the
arc — small measurable gains (a step, a grip) alternate with plateaus. The ward
community deepens: a fellow patient further along in recovery, one further
behind. Patient-care pressure sharpens as staff push a discharge-readiness
timeline that doesn't match the protagonist's actual pace.

**Arc 3 (ep_025-036) — Setback:** A complication or re-injury forces a return to
an earlier stage of recovery, testing everything built in Arc 2. Family pressure
peaks — a family member pushes the protagonist toward premature independence
(moving home, quitting PT) out of exhaustion, not malice. The ward community
becomes the protagonist's actual support system in this stretch, more than family.

**Arc 4 (ep_037-048) — Discharge:** Functional recovery is reached and framed
explicitly as an ongoing practice, not a finish line — the protagonist leaves
the ward still doing exercises, still adapting. They become an informal
peer-support presence for an incoming patient, closing the vessel loop without
claiming the body is "fixed."

---

## sleep_restoration_iyashikei
Genre (this exercise): family | Primary topic: sleep
Note: reassigned from established genre (iyashikei) for full-taxonomy coverage
exercise (see genre_assignment_37brands.md)
Craft-bible gap: no `docs/research/manga_craft/` bible for family. Built from
canonical_genre_list.yaml label ("Family") + interaction-grammar hint
`quality_gate_checks: [family_pressure]` + general multi-generational
household-drama craft knowledge.
Vessel: a **three-generation household** in one aging house — grandmother,
a working parent, and a child, sharing thin walls and one bathroom. Sleep is the
literal, physical resource the household is short on; each generation loses it
differently (grandmother's insomnia, parent's night-shift exhaustion, child's
nightmares), and the house's shifting configuration across the four arcs is the
escalation engine.

**Arc 1 (ep_001-012) — Under one roof:** The household's baseline is established:
three generations, three sleep patterns colliding in a small house. Family
pressure is ambient — nobody's rested, everybody's short-tempered, small
frictions (who used the good pillow, who woke the baby) stand in for larger
unspoken strain.

**Arc 2 (ep_013-024) — Shift change:** Grandmother's health takes a downward
step, requiring overnight care shifts that reorganize the household's sleep
schedule entirely. Roles renegotiate — the child takes on more, the parent's
work suffers, resentments surface. The house's physical configuration changes
(a room repurposed for care).

**Arc 3 (ep_025-036) — Someone leaves, someone returns:** Housing/eldercare
pressure crests — an adult sibling who left years ago returns home needing a
place to stay, or a family member moves out, forcing a full renegotiation of
who sleeps where and who is responsible for whom. The household nearly fractures
under the strain of too many needs in too little space.

**Arc 4 (ep_037-048) — A rhythm that holds:** The household doesn't return to
its Arc 1 shape — it settles into a new, sustainable configuration (a rotating
care schedule, a repurposed room made permanent) that the family builds
together. Sleep is not "solved," but the house finds a working rhythm the
family actively maintains.

---

## heart_balance_shojo
Genre (this exercise): food | Primary topic: social_anxiety
Note: reassigned from established genre (iyashikei) for full-taxonomy coverage
exercise (see genre_assignment_37brands.md)
Craft-bible gap: no `docs/research/manga_craft/` bible for food. Built from
canonical_genre_list.yaml label ("Food") + interaction-grammar hint
`quality_gate_checks: [family_customer_or_craft_interaction]` + general
kitchen/restaurant-drama craft knowledge (food-making as the vessel, not the
message).
Vessel: a small **family-run neighborhood restaurant** — prep kitchen, counter,
dining room. Craft (knife work, timing, plating) and customer interaction are
the literal mechanics; social anxiety is carried entirely through how the
protagonist moves between the safety of the kitchen and the exposure of the
counter.

**Arc 1 (ep_001-012) — The back of the kitchen:** Protagonist starts working
prep at the family restaurant — chopping, stock, dishes — kept deliberately away
from customers by choice and by family accommodation. Craft interaction
(learning knife work, timing, a mentor figure) is the register; customer-facing
moments are brief and overwhelming when they happen.

**Arc 2 (ep_013-024) — Front of house:** Short-staffed, the protagonist is
pushed to the counter and register, forced into direct customer interaction.
Family pressure intensifies — the restaurant's survival depends on the
protagonist stepping up, and family expectations (implicit comparisons to a more
outgoing sibling or parent) sharpen. Regulars become recurring, low-stakes
practice for connection.

**Arc 3 (ep_025-036) — The rush:** A competitive or crisis pressure hits — a
rival restaurant opens nearby, or a health-inspection scare, or a food festival
the family needs to participate in to survive — forcing the protagonist into
sustained high-visibility work (running a stall, pitching to a crowd) at the
exact moment their anxiety is worst.

**Arc 4 (ep_037-048) — Their table:** The protagonist finds a role that's
authentically theirs — not "cured" of social anxiety but able to work the
counter on their own terms (a signature dish, a quieter way of connecting with
customers). The restaurant stabilizes; craft mastery becomes the vehicle through
which the protagonist connects, on a register they set themselves.

---

## resilient_parent_social
Genre (this exercise): social_issue | Primary topic: burnout
Note: reassigned from established genre (iyashikei) for full-taxonomy coverage
exercise (see genre_assignment_37brands.md); brand name itself ("social"/"parent")
is a strong natural fit for social_issue via a caregiving/parenting-pressure lens.
Craft-bible gap: no `docs/research/manga_craft/` bible for social_issue. Built from
canonical_genre_list.yaml label ("Social Issue / Josei Realism") + interaction-grammar
hint `quality_gate_checks: [family_care_or_authority_pressure]` + general
josei-realism craft knowledge (a specific named social pressure carried through a
family/community lens — here, caregiving/parenting burnout).
Vessel: a **community caregiving network** — an informal co-op of neighbors in
one apartment block sharing childcare and eldercare duties because none of them
can afford or access enough support alone. The network itself, not any one
household, is the vessel; its health rises and falls with the arcs.

**Arc 1 (ep_001-012) — One parent, too much:** Protagonist, a single/overburdened
parent, is introduced at the edge of burnout — juggling work, a child, and an
aging parent with no formal support. The community network is introduced as an
informal, half-functioning safety net of neighbors trading off childcare and
eldercare shifts.

**Arc 2 (ep_013-024) — The system leans in:** Authority pressure intensifies —
a school flags attendance concerns, a workplace refuses schedule flexibility, a
welfare/eldercare agency inspection puts the informal caregiving arrangement
under official scrutiny. The protagonist must formalize what was informal,
under pressure from institutions that don't recognize the network as legitimate
support.

**Arc 3 (ep_025-036) — The network strains:** The caregiving network itself
buckles — a key volunteer burns out and drops off, funding for a shared
resource (a rented shared space, a subsidized meal program) is cut, and family
care pressure compounds as multiple households hit crisis simultaneously.
The protagonist, relied upon by others, has to admit their own burnout in front
of the people depending on them.

**Arc 4 (ep_037-048) — A structure, not a hero:** The network reorganizes around
a sustainable structure (a formalized rotation, shared advocacy with the
authorities that pressured them in Arc 2) with the protagonist as a connector
rather than a sole carrier. Burnout is not eliminated — it's distributed and
made survivable. Authored_candidate resolution: the system works better, no one
claims it's fixed.

---

## relationship_clarity_romance
Genre (this exercise): historical | Primary topic: social_anxiety
Note: reassigned from established genre (iyashikei) for full-taxonomy coverage
exercise (see genre_assignment_37brands.md)
Craft bible used directly: `docs/research/manga_craft/historical_period.md`
(reached via the `historical_period: historical` alias). Following its §7
recommended four-stage/three-era saga shape, scaled from 48 volumes to 48
episodes (era-force-as-antagonist, grief-across-time, outsider/heir/witness
protagonist entry points, per-era social pressure escalating before personal
stakes surface).
Vessel: a provincial **matchmaking household** across three generations of one
family, responsible for brokering courtships and marriages for their town under
strict social protocol (formal introductions, chaperoned meetings, letter
correspondence as the only permitted communication between prospective
partners). Social anxiety is carried entirely through the era's own courtship
mechanics — silence, formal address, the terror of a badly written letter —
never named as an anxiety condition.

**Arc 1 (ep_001-012) — Era One, the founding match (outsider entry):**
Protagonist enters the matchmaking household — as a young relative taking up the
family trade, or an outsider apprenticed into it — and is thrown into her own
first arranged courtship under the household's formal introduction protocol.
The era-force (rigid social codes governing who may speak to whom, and how) is
established as the antagonist before any personal romance is allowed to surface.
Ends on a rupture: the first match fails publicly, at cost to the household's
standing.

**Arc 2 (ep_013-024) — Era Two, the consequences (heir entry):** A generation
forward, or the same protagonist now senior in the household, dealing with the
fallout of Arc 1's failed match rippling through the town's opinion of the
family. A new courtship — this time the protagonist's own, or one she is now
brokering for a sibling/heir — proceeds under heavier scrutiny. The formal
correspondence system (letters, chaperoned meetings) becomes the primary
vehicle for connection, with silence and misread formality standing in for the
anxiety topic.

**Arc 3 (ep_025-036) — Era Three, the reckoning (witness entry):** Convergence
of Arc 1 and Arc 2's consequences — a match brokered years ago resurfaces with
consequences nobody anticipated, and the protagonist, now positioned as an
elder/witness figure in the household, must reckon with what the family's rigid
protocol has cost real people over two generations. The era-force does not
resolve; the household's relationship to it shifts.

**Arc 4 (ep_037-048) — Coda, a quieter household:** A final, small-scale witness
arc. The matchmaking household's role in the town recedes or changes shape; a
young courtship (possibly the protagonist's own child, or the apprentice who
began the saga) is allowed to proceed with slightly more room for honesty than
Era One permitted — not a rejection of the era's forms, but a small, earned
loosening within them. The grief and constraint of the earlier eras is named,
not erased.
