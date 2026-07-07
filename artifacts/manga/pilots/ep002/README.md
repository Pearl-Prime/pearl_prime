# Manga ep_002 Serialization Proof — 5 lanes

**Update (continuity seeds landed):** the two lanes originally left out below
(`the_blade_that_stopped_trying`, `the_room_reads_you_back`) now have
`config/manga/continuity/stillness_press__en_US__action_battle__series01.yaml` and
`config/manga/continuity/stillness_press__en_US__psychological_thriller__series01.yaml` on disk,
each with a real `next_episode_mandate`. Both `ep_002` scripts have been written against those
mandates and are staged here:

- `the_blade_that_stopped_trying__ep_002.chapter_script.yaml` — TEACHER · action_battle. Carries
  forward the ep_001 home-dojo win, breaks it under a real audience (qualifiers notice + a
  traveling challenger), plants `prefectural_qualifiers` (dated, six weeks) and `brace_tell` (read
  aloud on the page), and seeds `kazu` strictly as a distant, unseen rumor per the mandate.
- `the_room_reads_you_back__ep_002.chapter_script.yaml` — TEACHER · psychological_thriller.
  Reopens the "closed" Hadley case: the throat-tell is reconfirmed real but keyed to an unsolved
  arson, not the charged burglary (`hadley_conviction_wobble`), and introduces `the_ledger` as a
  briefed, ongoing institutional pressure. Voss redirects rather than lectures the method in both
  his lines, per the mandate's forbidden clause.

Neither script repeats its ep_001 shape, neither ends on a clean win/cure, and neither invents
continuity beyond what its seed file specifies — see each script's `craft_notes` for a
line-by-line mandate citation. `config/manga/continuity/*.yaml` for these two lanes were NOT
edited (same scope discipline as the original three: adopting these into the render queue would
require bumping `last_episode_id` to `ep_002` with a fresh `next_episode_mandate` for `ep_003`,
which is shared infra, not this staging lane).


**Status: SPECCED / Tier-1 authored artifacts on disk.** Per the six-layer acceptance taxonomy
these are authored `chapter_script_writer_handoff` scripts, not rendered panels — nothing here
is EXECUTED-REAL or PROVEN-AT-BAR. This is a staging lane, not a catalog addition: no
`scripts/**`, `phoenix_v4/**`, `tests/**`, `.github/**`, or live
`artifacts/manga/chapter_scripts/**` paths were touched.

## Mission

Prove Phoenix can carry forward serial memory, named pressure, rival/motif state, and
unresolved story logic from `ep_001` into `ep_002` — instead of every episode resetting as a
therapeutic one-shot (the drift `SERIAL_ENGINE_SPINES_5VOL.md` names as the batch system's
root failure). No new `ep_001`s were written; no new series were ideated.

## Lane selection — and why this trio, not the one first suggested

The brief asked for one horror/thriller/dark-fantasy lane, one romance/workplace lane, and one
battle/sports/cultivation lane, drawn from the strongest existing pilots. Per the operator's
addendum, lanes were filtered to those where **repo truth already provides both a concrete
`ep_001` artifact and enough serial-spine/continuity intent to write `ep_002` without
guessing** — preferring lanes with a pre-seeded `series_continuity_state` file
(`config/manga/continuity/*.yaml`, each carrying an explicit `next_episode_mandate`) over lanes
that only have narrative potential.

Four continuity-seeded lanes exist today: `stillness_press__en_US__dark_fantasy__series02`
(The Forest Beneath the Skin), `devotion_path_shonen__en_US__cultivation_martial__series01`
(The Mountain Does Not Move), `heart_balance_shojo__en_US__romance_josei_drama__series01`
(Worthy of the Window Seat), and `legacy_builder_memoir__en_US__historical_period__series01`
(The Last Letter Home — not needed for this trio's three slots).

This produced a **stronger, safer trio than the obvious first picks**:

- **Dark fantasy slot:** *The Forest Beneath the Skin* was chosen over *The Blade That Stopped
  Trying* (action_battle) even though Blade has a fuller `SERIAL_ENGINE_SPINES_5VOL.md` V1–V5
  writeup with a named rival (Kazu) already — because Blade has **no continuity-state seed
  file**, and Forest does, with an explicit `next_episode_mandate` (Iron Warden patrol + Marsh
  of the Swallowed Voice). Writing Forest's ep_002 required zero invented continuity; writing
  Blade's would have required guessing what "V2" looks like from prose alone.
- **Romance/workplace slot:** no lane in `SERIAL_ENGINE_SPINES_5VOL.md`'s nine covers
  romance/workplace at all. *Worthy of the Window Seat* (romance_josei_drama, set inside a
  secondhand sheet-music shop — a workplace-adjacent creative-industry setting) is the only
  romance pilot with both a strong genre-native `ep_001` (wave2 README's documented escalation
  engine: shared song, premiere clock, pencil-vs-ink) **and** a continuity seed with a named
  mandate. It is the clearly-stronger — and only defensible — choice for this slot.
- **Battle/cultivation slot:** *The Mountain Does Not Move* was chosen over *The Blade That
  Stopped Trying* for the same continuity-seed reason as above. Blade's V1–V5 spine is richer
  on paper, but Mountain has a machine-readable `next_episode_mandate` (Wei Long collects
  humiliation; autumn_ascent_roll gets terms) that made ep_002 an implementation of existing
  intent rather than an invention.

No lane was marked BLOCKED — all three chosen lanes had sufficient continuity state to write an
honest ep_002.

## Files

1. `the_forest_beneath_the_skin__ep_002.chapter_script.yaml` — TEACHER · dark_fantasy
2. `the_mountain_does_not_move__ep_002.chapter_script.yaml` — TEACHER · cultivation_martial
3. `worthy_of_the_window_seat__ep_002.chapter_script.yaml` — MUSIC · romance_josei_drama

Each script's `craft_notes` field cites the exact `next_episode_mandate` (`must_rebreak`,
`must_plant`, `forbidden`) it satisfies, so a reader can check compliance line-by-line against
`config/manga/continuity/*.yaml` without re-reading the whole chapter.

## Continuation notes per lane

### The Forest Beneath the Skin (dark_fantasy)

- **ep_001 resolved:** Rin met the Vigil (hypervigilance-as-creature) without striking; one
  wall-seam bloomed; she believes meeting works — but only tested in calm, after the storm had
  already passed.
- **What remains unresolved:** the Keeper's own sealed region (his unmet creature); the Iron
  Wardens' doctrine (promised, not yet on-page); the wider map beyond Rin's patrolled ground.
- **What ep_002 deliberately escalates:** the belief is tested in the middle of a REAL storm,
  not a training case — the Vigil returns storm-scaled and the meeting only partially holds
  (the wall pays the cost the creature didn't). The Iron Wardens make first contact mid-breach,
  offering a real, tempting counter-doctrine (reinforcement) rather than a strawman. The Marsh
  of the Swallowed Voice is sighted for the first time — named on the map, entered by no one.
- **Why this is serial, not a second one-shot:** ep_002 ends with Rin's answer to the Wardens
  undecided and the marsh unclaimed — two open institutional/geographic threads a reader must
  return for, not a second closed lesson.

### The Mountain Does Not Move (cultivation_martial)

- **ep_001 resolved:** Shen Yan, struck from the Autumn Ascent roll for forcing a rupture, found
  one unbraced breath at the First Gate's threshold bowl and vowed to climb the whole ladder
  without leaving it.
- **What remains unresolved:** Wei Long's stroll-taunt, unpaid; why the elders bow to Master Ku;
  the Ascent roll's actual reinstatement terms; whether the settling holds under real stakes.
- **What ep_002 deliberately escalates:** an organic crowd (a pilgrimage party, not a staged
  duel) puts Yan's practice under public scrutiny for the first time. Wei Long returns and
  strikes the old rupture point by name — informed cruelty, not generic taunting — and the
  settling genuinely fails: Yan loses the exchange in front of witnesses. The Autumn Ascent
  rumor becomes a dated, named winter exhibition with Wei Long as its confirmed representative
  challenger.
- **Why this is serial, not a second one-shot:** Yan does not win, is not cured, and gets no
  clean lesson delivered twice — Master Ku's one line costs the ladder nothing and the chapter
  closes on a forty-day countdown, not a resolution.

### Worthy of the Window Seat (romance_josei_drama)

- **ep_001 resolved:** Mio and Ren's shared song passed hand to hand in secret margins until she
  played it whole, overheard, and finally hummed it aloud, unhidden, in the open shop.
- **What remains unresolved:** the ALMOST (Ren never finished "It was—"); the premiere in three
  weeks; co-credit undecided; a courier's misread the drawer exchange as romance (press risk).
- **What ep_002 deliberately escalates:** the premiere clock collapses from three weeks to eleven
  days, forcing in a credentialed rival arranger who plays the shared song perfectly and without
  its history — proving "correct" and "heard" are not the same thing. Mio's one attempt to
  defend her bars costs her visibly: sidelined from the credited score, a job-standing bruise
  Saki has to absorb, displaced from the window seat itself.
- **Why this is serial, not a second one-shot:** Ren does not confess, no caption tells Mio she
  is worthy, and the chapter ends on a locked-in "safe" version and a shrinking countdown — the
  only hope is an unconscious hum nobody in-story has noticed yet.

## What was NOT done (scope discipline)

- No `ep_001` was written or altered for any lane.
- No `config/manga/continuity/*.yaml` files were edited — they remain ep_001-state; adopting
  these ep_002 scripts into the render queue would require updating each lane's continuity file
  to `last_episode_id: ep_002` with a new `next_episode_mandate` for ep_003 (not done here, since
  `config/` is shared infra, not a pilot/staging path this lane was scoped to write to).
- No infra, CI, scripts, or test files were touched.
- The action_battle lane (*The Blade That Stopped Trying*) and psychological_thriller lane
  (*The Room Reads You Back*) were deliberately left out of this pass — both have strong
  `SERIAL_ENGINE_SPINES_5VOL.md` writeups but no continuity-state seed file yet. A future ep_002
  pass for either would need a `series_continuity_state` seed authored first (or explicit
  operator sign-off to proceed without one), per the addendum's guardrail against inventing
  around missing continuity.
