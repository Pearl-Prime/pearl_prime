# Serial Engine Spines — 5-Volume Opening Arcs from the Iconic Pilots

**Status: SPECCED** (six-layer taxonomy). These are authored serialization spines, not
stories — no episode beyond the existing pilots is authored by this document. A spine
row never enters the render queue (`check_manga_story_authored.py` still requires a full
`chapter_script_writer_handoff` per episode).

**Purpose.** The pilots are gold; the batch catalog is generic. Cause (verified on-page,
see §11): the batch writer stamps one healing cadence (wound → turn → renewal, resolve,
end-card) onto every genre, every episode, forever. That makes every series a
therapeutic-one-shot generator. This document converts each iconic pilot's already-working
genre engine into a **renewable serial engine** — a 5-volume opening arc (1 volume = 10
chapters per `config/manga/manga_brand_series_plan.yaml`) that escalates according to its
own shell, not the healing cadence.

**The one conversion rule.** In every pilot, the protagonist's turn resolves in ep_001.
A serial keeps the pilot's *mechanism* and makes it renewable: the settled state is not a
cure, it is a skill that every new context breaks in a new way. Each lane's spine names
(a) the renewable unit, (b) the escalation axis native to its shell, (c) the recurring
set-piece pleasures, (d) the rival/relationship/system pressure, (e) the binge mechanism.
Mode discipline is preserved throughout: teacher lanes never gain a soundtrack; music
lanes never gain a doctrine line — at any scale of escalation.

Source pilots (all Tier-1 authored; render gated except partial flagship assembly):

| Lane | Pilot | Mode | File |
|---|---|---|---|
| iyashikei flagship | The Alarm Is Lying (eps 1–10) | teacher (engine: false_alarm) | `artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/` |
| iyashikei (tea-house) | The House That Warms the Cup | teacher | `pilots/wave1/the_house_that_warms_the_cup__ep_001.chapter_script.yaml` |
| dark_fantasy | The Forest Beneath the Skin | teacher | `pilots/the_forest_beneath_the_skin__ep_001.chapter_script.yaml` |
| psychological_thriller | The Room Reads You Back | teacher | `pilots/wave1/the_room_reads_you_back__ep_001.chapter_script.yaml` |
| action_battle | The Blade That Stopped Trying | teacher | `pilots/wave1/the_blade_that_stopped_trying__ep_001.chapter_script.yaml` |
| sports_competition | The Beat Beneath the Lane | music | `pilots/wave1/the_beat_beneath_the_lane__ep_001.chapter_script.yaml` |
| supernatural_mystery | The Half a Lullaby | music | `pilots/wave1/the_half_a_lullaby__ep_001.chapter_script.yaml` |
| sci_fi_cyberpunk | The Frequency They Filtered Out | music | `pilots/wave1/the_frequency_they_filtered_out__ep_001.chapter_script.yaml` |
| school_coming_of_age | The Song the Year Was Set To | music | `pilots/wave1/the_song_the_year_was_set_to__ep_001.chapter_script.yaml` |
| mecha | The Cockpit Remembers the Song | music | `pilots/the_cockpit_remembers_the_song__ep_001.chapter_script.yaml` |

---

## 1. Flagship iyashikei — THE ALARM IS LYING (stillness_press · teacher · false_alarm)

**Extracted engine.** One false alarm per episode, timestamp titles ("Tuesday, 6:47 AM"),
micro-scale realism, the tea beat and jade-LED through-line as regulating ritual. The
10 authored episodes are a closed loop (ep_010 mirrors ep_001 six weeks later).

**Shell law.** Iyashikei must NOT escalate stakes. It intensifies by *widening the circle
and deepening the season* — more nervous systems, more precious dailiness, never bigger
explosions. The serial conversion opens the ep_010 loop instead of closing it.

- **V1 — "Six Weeks" (EXISTS: eps 1–10).** Mira meets her own alarm across contexts
  (email, meeting, night waking, lunch invite). Keep as-is; it is the volume-1 gold master.
- **V2 — "Other People's Alarms."** Mira starts *seeing* the same lie in other bodies —
  the new hire who over-prepares, the manager's Sunday-night emails, her mother's
  compulsive weather-checking. Iyashikei tension: witnessing without fixing (you cannot
  tell someone their alarm lies; you can only be still near them, the way the reader
  learned from Mira). Volume close: the new hire notices Mira's stillness the way the
  reader noticed it in V1.
- **V3 — "The Alarms That Tell the Truth."** The honest complication: some alarms are
  not lying — a real deadline; her mother's small-but-real health scare (kept off-page,
  iyashikei-scale). The practice matures from *the alarm is lying* to *ask the alarm what
  it is for*. Deepening, not stakes.
- **V4 — "The Dark Mornings."** The year turns; winter removes the ritual's cues — 6:47
  is now black, the dappled-light hand panel arrives with no light. The ritual must be
  rebuilt when its scaffolding vanishes. Travel episode, sick episode (practicing while
  ill), and a second nervous system in the apartment — two alarms, one kettle.
- **V5 — "Tuesday, 6:47 AM (One Year Later)."** ep_001 replayed a year on, ensemble
  threaded through the same morning. Succession without teaching: Mira has become
  someone's Okami without ever saying a doctrine line. Final image renews the hook —
  the alarm still fires. It always will; that is why the series can run forever.

**Set-piece pleasures.** The tea beat every episode; timestamp title cards; the jade LED;
the "catalogue of alarms" — each episode names a false alarm the reader recognizes from
their own life (the *oh, that's me* collection pleasure).
**Pressure.** No rival (shell-illegal). Pressure = seasons, other bodies, and true alarms.
**Binge mechanism.** Collection + ensemble accrual + ritual return. Aria/Yotsuba model:
readers return to a place, not a plot.

---

## 2. Dark fantasy — THE FOREST BENEATH THE SKIN (teacher · Keeper + living land)

**Extracted engine.** The body as a dark-fantasy realm; a somatic pattern is a creature
that cannot be cut, only met. The Vigil (hypervigilance) is chapter one of a bestiary.
Walls are bracing; meeting is the only combat that works.

**Shell law.** Dark fantasy escalates by *depth and age* — older regions, older wounds,
a war of doctrines about walls. The map gets darker as it gets truer.

- **V1 — "The Warden Who Would Not Sleep."** The Vigil arc expanded: meeting is not
  one-and-done — the Vigil returns with every storm, and each meeting is fresh (kills the
  one-shot at the root). The realm's map introduced: the Marsh of the Swallowed Voice,
  the Ember Fields, the Glass Orchard, the Deep Root. Close: an **Iron Warden** patrol
  offers Rin a stronger wall — and their armor is magnificent.
- **V2 — "The Marsh of the Swallowed Voice."** Creature: the Choir Under the Water — the
  unsaid words, speaking in bubbles. Rin must un-dam streams her own walls diverted;
  meeting the marsh floods old ground (memory returns — cost, not victory). The Iron
  Wardens are *draining* the marsh as public works. First doctrinal clash: meeting vs
  draining.
- **V3 — "The Borderlands."** Where Rin's realm touches another's — the beloved/friend
  whose Ember Fields ignite hers at the shared march. Creature: the Smolder-Hound, which
  burns hotter the more it is smothered. Co-regulation as border-craft; revealed: every
  person is a realm, every relationship a border, and the Long Storm in Rin's childhood
  is when the first wall went up.
- **V4 — "The Iron March."** Inside the rival order: Commander Sela's fortress-realm is
  perfect and utterly numb — no weather, no birdsong; and the blight (realm-death that
  walls cause) is already inside because a walled realm cannot feel infection arrive.
  Rin enters to meet what Sela cannot, riding with the Vigil — her alarm, converted from
  monster to mount, the series' emblem image.
- **V5 — "The First Wall."** The Deep Root: the original wound the whole wall-system was
  built around — including the region the *Keeper* has kept sealed (the teacher's own
  unmet creature: The Quiet). Rin goes where the teacher cannot; the doctrine outgrows
  its teacher without betraying it. Walls fall realm-wide — which frees the whole
  bestiary. The next era's premise, in the last panel: weather returns.

**Set-piece pleasures.** Bestiary reveals (each un-cuttable in a new way); meeting scenes
as stillness boss-fights (the "fight" is staying); wall-fall blooms (barricade → blossom);
Keeper koans; map pages that fill in volume by volume.
**Pressure.** The Iron Wardens (system: a whole civilization of bracing, and it *works*
until it dies); Sela as rival warden; the Keeper's sealed region as relationship debt.
**Binge mechanism.** Bestiary collection + map completion + order-war + the first-wall
mystery.

---

## 3. Psychological thriller — THE ROOM READS YOU BACK (teacher · the body confesses)

**Extracted engine.** Read the witness, not the lawyer: the body confesses before the
mouth. Case structure with a method that can be stressed, jammed, and turned inward.

**Shell law.** Thrillers escalate by *adversary competence and method inversion* — each
case attacks the method at a new failure point, ending with the method aimed at the
people who taught it.

- **V1 — "The Tell."** The Hadley conviction wobbles: his tell was real but pointed at a
  *different* crime. First method lesson at serial scale: the body confesses to ITS
  truth, not to your theory. Establishes case-per-volume rhythm, the amber-lamp grammar,
  and the bureau's new toy: a behavioral-analytics unit ("the Ledger") whose model is
  replicable, admissible — everything Mara's instrument is not.
- **V2 — "The Still Man."** The null case: a suspect with no tells. Resolution: a body
  that never flinches has rehearsed — stillness *is* the tell — and the confession is
  read from the ensemble of bodies around him. Mara beats the Ledger's model by one
  beat but cannot show her work. First institutional bruise.
- **V3 — "The Mirror."** An adversary who reads bodies too — and plays Mara's own tells
  back at her, feeding her false alarms until her instrument jams. She must learn to
  tell her *alarm* from her *read* (the hypervigilance interior deepened honestly,
  never named). Voss benched by the software rollout; Mara alone.
- **V4 — "The Instrument Breaks."** The case adjacent to her own history — why she scans
  exits (seeded V1–V3 as the one tell she never examines). All noise, until she does to
  herself what Voss did to Hadley's footage: mutes herself and watches the witness.
  Rival thaw: the Ledger flags her blind spot; data and body become complementary
  instruments.
- **V5 — "The Witness Who Taught Me."** Voss's cold case — the one that taught him the
  method; his tell has been on the page since ep_001 (the coffee he never finishes).
  Mara reads the one body she never let herself watch. Method handed on; close on an
  open loop: a new case file, and *her* throat moves at the photo.

**Set-piece pleasures.** Muted-footage readings renewed per case in a new channel (muted
video; a phone call's breathing; a deposition where the tells are in the typos);
interrogation stillness duels; amber lamp vs white room; the notebook sketch that closes
every case (a new tell drawn like evidence — a collectible).
**Pressure.** The Ledger (system: replicability vs instrument); the Mirror (rival who
weaponizes her method); Voss (relationship debt, unread).
**Binge mechanism.** Thriller-native case cliffs — each volume's case closes but its
implication opens the next; method-vs-model war; drip-fed origin.

---

## 4. Action battle — THE BLADE THAT STOPPED TRYING (teacher · the settled strike)

**Extracted engine.** The settled body strikes truer than the braced one; doctrine earned
in DEFEAT. Opponents are forcing-modalities; power-ups are subtractions.

**Shell law.** Battle manga MAY escalate classically — ladder, tournament, style war,
succession — but this engine inverts the shonen power curve: every arc Jun *gives
something up*. The unbracing ladder is the power system.

- **V1 — "The Strike You Cannot Force."** The settled strike is fragile: it works in the
  home circle and shatters under crowd and stakes (new context = new brace — the serial
  conversion in one line). Prefectural qualifiers vs crude forcing styles (rage bull,
  fear counter-fighter, showboat). Close: Tessen-ryū — the school of iron — and its
  prodigy **Kazu** demolish a friend in one braced strike. The doubt that fuels V2: is
  settling only for people who were already fast?
- **V2 — "The School of Iron."** Tournament arc vs Tessen. Jun loses the final to Kazu —
  not because settling fails, but because *pain re-braces her mid-bout* (the honest
  escalation of the interior). Doctrine earned in defeat, at serial scale. Revealed: the
  Sensei and the Iron Master shared one teacher; the two styles are two griefs from one
  deathbed.
- **V3 — "The Settling Under Pain."** Inverse training arc — she trains by doing less;
  the body learns to unclench *around* injury. Mid-arc: the Sensei collapses; his
  stillness is now real frailty, and the hardest unbracing is shown, not said: the
  master settling into being helped. Kazu's accumulating fractures surface — his brace
  is billing him.
- **V4 — "The Invisible Art."** System pressure made structural: federation scoring
  rewards visible power; settling looks like doing nothing — judges literally cannot
  score her art. Tessen absorbs dojos. Jun must win so cleanly that stillness becomes
  visible: the one-strike matches, pages going silent before a single cut.
- **V5 — "The Two Roads."** Kazu's body gives out mid-final; Jun refuses the forfeit road
  and the succession duel comes instead: the Iron Master himself — whose iron was built
  ON a settledness he abandoned, and who, facing Jun, re-finds it. The final bout is two
  settled fighters: pure timing, one breath, one strike — the series thesis in a single
  page. Close: Kazu joins the settling road, injured but alive to it; the dojo passes to
  Jun — an inheritance of tempo, not power. Open loop: nationals; the styles beyond.

**Set-piece pleasures.** One-breath duels (silent pages, then one strike); brace-tell
close-ups (shoulders/jaw/grip as fight-reading); training-by-subtraction sequences; the
water-level stances.
**Pressure.** Kazu (rival whose winning style is killing him); the Iron Master (doctrine
war with family roots); federation scoring (system that cannot see the art); the
Sensei's decline (relationship).
**Binge mechanism.** Ladder + rivalry + style-war + the injustice engine of an art the
scoreboard cannot see.

---

## 5. Sports — THE BEAT BENEATH THE LANE (music · the inner four-count)

**Extracted engine.** The stride has a tempo; forcing scatters it; the race turns when
the beat re-finds itself. Team chant = shared pulse. MUSIC MODE: no coach may ever say
the lesson — every arc must be *scored*, never explained.

**Shell law.** Sports escalates by meet ladder + rhythm problems: each race breaks the
beat in a new way, and the chant's ownership passes through the ensemble.

- **V1 — "The Tempo She Lost on the Line."** After the pilot's win, expectations arrive —
  the fraud-feeling's sequel: now the beat must perform on demand. Race problems: heats
  where the team's hum is out of earshot; a false start that resets her pulse. Volume
  close: an individual 100m — no relay, no chant, no team. Can the beat exist solo? It
  can: thin, but hers.
- **V2 — "The Click-Track Girl."** Rival: **Sana**, an anchor engineered to a lab
  click-track — a beat that is perfect and not hers (the pilot's closing line, made into
  a person). The program mandates wearables; running to the click scatters Rei worse
  than fear ever did (forcing, externalized). Mid-recurrence, volume-scale: she races
  with dead headphones and finds the four-count under the click's ghost.
- **V3 — "The Broken Chord."** Leg two goes down; new runner **Mika** cannot join the
  hum — Rei watches her own imposter year from the outside, and music-mode law forbids
  telling her anything. The exchange zone becomes the engine's crucible: a handoff is
  two beats briefly one. Resolution, scored: Rei taps the four-count on the baton itself
  before the exchange — the beat conducted through the object. The chant reborn in a
  new key.
- **V4 — "The Loud Stadium."** Nationals: stadiums that drown the hum; a night race; a
  rain race where footfall sound vanishes — the beat, half-heard until now, must become
  fully *felt*. Sana's click cracks in the rain; beatless in the call room, she sits
  near Rei — who does the only legal act: taps the four-count on the bench, audible to
  anyone. The reader watches the rival's foot decide.
- **V5 — "The Anchor's Anchor."** Trials final, everything stacked: solo seeding,
  drowned chant, click-runners, and the seniors' last race as this chord. The final
  exchange in silent pages — four counts across four panels. Close: next season, Mika
  leads the hum; a first-year taps a four-count she never heard the origin of. The beat
  outlives its bodies — music-mode's legacy, wordless.

**Set-piece pleasures.** Exchange-zone beat-transfers; the beat-motif lettering states
(steady / scattered / syncopated — a visual score readers learn to read); call-room
quiet; the tunnel hum.
**Pressure.** Sana (borrowed-beat rival); the quantified-pace program (system); Mika and
the chord (ensemble/succession).
**Binge mechanism.** Meet ladder + rival duel + a readable visual score system — any
panel tells you who owns their beat right now (collectible literacy).

---

## 6. Supernatural everyday — THE HALF A LULLABY (music · the unfinished song)

**Extracted engine.** Hauntings are unfinished songs; laying to rest = completing, not
banishing. The ribbon on Suzu's wrist is her own held grief — the series arc hiding in
the pilot's costume design.

**Shell law.** Escalates by *musical form and age* — each case is a new unfinished FORM,
songs get older and larger (child → house → town → sea), and the price of finishing
rises: you must carry a song to complete it.

- **V1 — "The Note It Could Not Reach."** Case grammar established across village cases:
  a lullaby one note short; a fisherman's call with no answering line; a duet missing a
  voice. Suzu's ledger: every finished song hummed once at the sea — except her own,
  never. Close: the Clearers' Guild auditor **Bram** arrives — salt-orthodox, and
  literally tone-deaf: he banishes because he cannot hear. (Also the Guild's economics:
  banishing is repeat business; finishing is permanent.)
- **V2 — "The House With Two Songs."** Two spirits whose songs interlock in dissonance —
  a marriage, each holding the other's unsaid apology; finishing one alone worsens the
  other. She must carry both at once; the first physical cost on-page (her hum cracks;
  the ribbon-hand trembles). Bram witnesses a true finishing and files it as
  coincidence — his quiet crisis begins.
- **V3 — "The Town That Silenced Its Song."** Scale jump: a town banned its festival
  song after a disaster — collective grief suppressed by ordinance — and now every house
  hums a broken variant. The Guild bids a mass banishment; Suzu reconstructs the
  original melody from fragments door to door (song-reconstruction as detection). The
  festival sung whole once; the Guild's biggest contract voided; the hunt for her
  method becomes official. Bram hears one note.
- **V4 — "The Clearer Who Could Not Hear."** Bram's case: a silence-haunting — someone
  who died never having been listened to; the ghost is a held silence and no melody
  reaches it. The completion is a *rest*: a fermata held over silence (music-mode
  legal — a rest is music). Bram's deafness reframed as the misfiled gift: he holds
  silence better than anyone. The rival becomes the counterpart: clearer of silences.
- **V5 — "The Ribbon."** Her own song — the torn first page of the ledger, the half a
  lullaby someone once sang over *her*. The engine's final inversion: a clearer cannot
  finish her own song; it must be sung over her — Bram holds the silence, and the town
  she saved hums the answering line. The ribbon goes into the sea for real (the pilot's
  closing image, earned at series scale). Open loop: a two-clearer practice — song and
  silence — and the sea itself is humming something very old.

**Set-piece pleasures.** The song-form bestiary (canon, call-and-response, round, rest);
completion panels (broken motif line closing into an arc — the signature render, renewed
per form); the sea-ledger hums; cold-to-warm palette turns per house.
**Pressure.** The Guild (system: orthodoxy + economics); Bram (rival → counterpart);
the ribbon (the protagonist's own case, deferred).
**Binge mechanism.** Case forms + Guild war + Bram counter-arc + the ribbon mystery +
a growing songbook (finished melodies as collectible backmatter).

---

## 7. Sci-fi cyberpunk — THE FREQUENCY THEY FILTERED OUT (music · the analog tone)

**Extracted engine.** One warm analog tone under the scrubbed feed; tuning beats
out-processing; slowness the system cannot model. Run/heist structure native.

**Shell law.** Cyberpunk escalates by *product ladder* — each corporate Filter update
scrubs deeper (ambient → dead spots → speech cadence → inner prosody), and the fight is
typographic: hand-lettered warmth vs monospace flattening.

- **V1 — "The Tone Beneath the Static."** Between runs, Vex maps dead spots; the tone
  surfaces differently in each (speaker hum, elevator cable, a fridge). The corp
  ("Clarion") flags her telemetry — a runner who *slows down* mid-crisis breaks their
  models — and reads her calm not as threat but as product opportunity. Her peace is IP.
- **V2 — "The Update."** Filter 2.0 ships; infrastructure "renewal" bricks the busted
  speakers and the dead spots go silent. But her re-found breath persists: she discovers
  she can *be* a dead spot — carry the quiet into full-noise zones, hum through blown PA
  systems mid-run. Hunter assigned: **Cadence**, a fully-optimized runner with zero
  analog left — what Vex was becoming.
- **V3 — "The Other Listeners."** The network arc: strangers stop mid-crosswalk when her
  carried tone passes; the unplugged colony in the filter shadows (music-mode: they
  never preach — their market simply has no ads and one kettle whistling). Archive
  heist: the Filter's origin — noise-cancellation trained on a master recording that
  included a heartbeat; the tone is the residue of what the founder built the Filter to
  stop hearing. First Cadence duel: overclocked pursuit vs an unforced walk — prediction
  cannot model unhurried tempo. She escapes at strolling pace.
- **V4 — "The Runner With No Pulse Left."** Cadence catches her — and crashes in the
  kill-box: burnout as system failure, the forced-sync bill paid on-page. Vex does the
  only legal move: holds the tone beside her. Cadence's HUD shows a pulse she has only
  ever read; now she feels it. Defection — not to Vex's side, but to her own body.
  Clarion escalates: Filter 3.0 ships *inside* neural augments, mandatory OTA; across
  the city, dialogue lettering flattens to monospace — the horror rendered purely
  typographically.
- **V5 — "The First Broadcast."** The run of runs: the corp tower's cold archive, the
  original heartbeat recording. She cannot out-fight the tower, so she jacks the ad-grid
  and broadcasts — not the recording — her own unfiltered breath, live, with the
  founder's heartbeat underneath: completing the song he built an industry to silence.
  The Filter dies by its own off-switch. Honest cyberpunk coda: the city doesn't heal,
  it just gets *human*-noisy again; the dead spots stay sacred; Vex still runs jobs.
  Open loop: a startup pitches "Filter, but ethical."

**Set-piece pleasures.** Dead-spot discoveries (each a found-sound sanctuary with its own
tone-texture); static-parting panels; walking-speed chases; the lettering-state grammar —
typography as the battleground, readable panel to panel.
**Pressure.** Clarion's update ladder (system); Cadence (hunter → mirror); the founder's
grief (the mystery with a body in it).
**Binge mechanism.** Run structure + update-ladder dread + hunter duel + source mystery +
a typographic world-state readers track like a score.

---

## 8. School — THE SONG THE YEAR WAS SET TO (music · the year-song)

**Extracted engine.** One piece per year carries the club's growing-up; phrase-gaps are
the members' silences; the empty room is where the true sound lives. The pilot compressed
a whole year into ep_001 — the serialization move is to DE-COMPRESS.

**Shell law.** School escalates by the calendar — welcome concert, training camp, culture
festival, regionals, graduation — across three school years (5 volumes), with cast
rotation as the engine of renewal.

- **V1 — "First Year."** ep_001 re-lived at serial pace: joining; the first gap; the
  training camp where night practice is sanctioned solitude; the senpai whose own phrase
  has a hairline crack nobody notices (V2 seed); a culture-festival half-step (she plays
  inside the ensemble's shadow). The pilot's showcase is the volume FINALE — the trailer
  becomes the season.
- **V2 — "Second Spring."** New first-years, including **Aya** — technically perfect and
  empty (plays the way the rival school sounds). Mio is now the one watched-up-to:
  terror, inverted. The year-song must be chosen — the hard piece (to be measured by) vs
  the true piece (to grow inside). System pressure lands: merger with the orchestra club
  = supervised practice always; the empty room, scheduled out of existence. Mid-volume:
  Mio plays the condemned room one last time and is overheard by accident — being
  overheard unwatched vs performing watched, the engine's finest distinction, staged.
- **V3 — "The Regional Stage."** Rival school Seika head-to-head; the rubric rewards
  precision — the scoring system cannot hear aliveness (school's version of the
  invisible art). The club loses, playing alive; a Seika player cries in the corridor
  after winning — her first feeling in years, caused by the losers' performance. The
  club room is saved when the recording quietly circulates the student body: the world
  answers slightly. Not victory — permission.
- **V4 — "Third Year."** Mio leads, and her silence returns in leader's clothing: she
  arranges everyone's parts so no one is ever exposed — armoring the club. Aya names it
  the only way music-mode allows: "your arrangements have no gaps" — and the new
  first-year's phrase has nowhere to land; the year-song sounds finished and dead. The
  gap, re-learned as a *placed* thing: composition as pedagogy, never stated. Seika's
  cracked player transfers in; the chord enriches.
- **V5 — "The Song Handed Down."** The final year-song is written, not chosen — each
  member a phrase; Mio writes the rests. At the graduation showcase a first-year freezes
  exactly as ep_001 Mio — and Mio does not coach her (music-mode law): she dims the
  stage lights for the girl's phrase, making the hall an empty room. Five volumes of
  craft in one silent act. Last page: the worn club pin left on the sill for whoever
  comes. The club continues without her.

**Set-piece pleasures.** Empty-room nocturnes (the lane's tea-beat); seasonal strips
(cicadas/leaves — the pilot's montage grammar as recurring transitions); the
missing-phrase panel where the score holds a visible hole; the festival ladder; each
volume's year-song as an "album drop" readers hum.
**Pressure.** Seika (institutional mirror); the room-in-peril (system: the right to be
unwatched); Aya and the first-years (succession).
**Binge mechanism.** Year-cycle ladder + cast accrual + rival-school arc + the annual
song. The most naturally renewable shell in the catalog.

---

## 9. Mecha — THE COCKPIT REMEMBERS THE SONG (music · the sync-song)

**Extracted engine.** Machines answer, never obey; the link is a duet, not a command;
forced sync burns pilots out ("static scars"). Kessler doctrine = institutional forcing.

**Shell law.** Mecha escalates by war ladder + tech-doctrine war + enemy mystery — and
this engine's version of the mystery is musical: the war itself is an unresolved chord.

- **V1 — "Static."** Aoi and Sable prove out; the corps responds by trying to *extract*
  the hum — record it, install it in other units. The copied song fails in every other
  cockpit: a song is not a file (the music-mode thesis in mecha grammar). Rival
  introduced: **Riva**, Kessler's protégé-daughter, the force-sync poster ace — publicly
  flawless, hands shaking after every sortie. The misfit squad forms: each unsyncable
  unit answers a different key (one machine answers only percussion; one answers only
  silence).
- **V2 — "The Choir of Broken Units."** Salvage-yard arc: rebuilding a lance from
  "unsalvageable" machines by finding each one's song — machine-song discovery as the
  renewable case unit. War escalates: enemy jammer fields scramble ALL sound — and the
  squad syncs by felt pulse alone, hands on the hull. When sound is taken, the song
  persists as vibration and breath: the engine deepened under its own terms.
- **V3 — "The Ace's Static."** Riva's unit seizes mid-battle — the force-sync bill due.
  Rescue; collapse; the slow re-learning with a machine she must *ask* — her father's
  doctrine breaking in her body, never in dialogue. Kessler doubles down: Sable
  scheduled for decommission as an "unreplicable anomaly" — the corps would rather lose
  consistently than win unscalably.
- **V4 — "The Songs Over the Ridge."** The reveal: a downed enemy unit is humming — and
  its intervals are kin to Sable's. Behind the lines: the enemy "hive" is a
  graveyard-choir of first-generation machines holding one endless unresolved loop — a
  war-long held note. Kessler's history surfaces: he was the other pilot of the original
  duet; his doctrine was born the day the song failed him. The antagonist's brace given
  its wound.
- **V5 — "The Duet."** Sable's hum is half of a duet; the other half is the enemy
  flagship — the previous pilot pair, one dead, one machine gone over the ridge carrying
  the unfinished half. Final battle = completing the war's song mid-battlefield: Aoi and
  Riva fly the two halves while both fleets fire. When the duet completes, the machines
  on both sides stand down *themselves* — instruments refusing to be played wrong once
  they have heard it: machines answer, never obey, at war scale. Kessler's surrender is
  one breath, not a speech. Open loop: demobilization — what is a singing war-machine
  for, in peace? The hangar's last panel is already becoming a conservatory, and the
  machines are humming songs nobody taught them.

**Set-piece pleasures.** Machine-song discoveries (a new unit's sync scene per arc);
jam-field silent battles; hull-touch pulse panels; the night-hangar choir shot (every
unit's light pulsing its own tempo); per-machine hand-lettered motifs — readers identify
machines by their lettering voice.
**Pressure.** Kessler doctrine (system + family); Riva (rival → second voice); the
decommission order (the machine's life at stake); the enemy chord (mystery).
**Binge mechanism.** War ladder + machine-song collection + ace rivalry that resolves as
a duet + the doctrine war with a family core.

---

## 10. Cross-lane craft rails (what keeps nine serials from re-flattening)

1. **The rival converts per shell, never repeats.** Iron Warden (doctrine order), the
   Ledger (institutional model), Kazu (body paying interest), Sana (borrowed beat), Bram
   (deaf to the medium), Cadence (optimized empty), Seika (institutional polish), Riva
   (family doctrine). Flagship iyashikei has NO rival — shell-illegal.
2. **System pressure is always the genre's own institution**, never a generic boss:
   scoring rubrics, guild economics, filter updates, federation judging, decommission
   orders, room scheduling. The wellness interior stays interior.
3. **Escalation = the engine stressed under its own terms**, not raised stakes-in-general:
   take the sound away (mecha V2), jam the instrument (thriller V3), remove the cues
   (flagship V4), externalize the forcing (sports V2).
4. **Set-pieces are renewable rituals, not repeated scenes** — each lane has a signature
   render (completion panel, static-parting, one-breath strike, beat-lettering state)
   that returns in a NEW form every volume. That is the binge contract.
5. **Mode XOR at serial scale.** Teacher lanes: the vessel may decline, fail, or be
   surpassed, but no motif ever carries an arc. Music lanes: rivals defect, ensembles
   grow, but nobody ever says the lesson — resolutions are scored, dimmed, tapped, or
   held as rests.
6. **Volume 5 always reopens.** Every lane's last beat renews the hook instead of curing
   it: the alarm still fires; the bestiary is freed; her throat moves at a new photo;
   nationals wait; the first-year taps the count; the sea hums; a new Filter is pitched;
   the pin waits on the sill; the machines hum unwritten songs.

## 11. What the batch system currently loses from the pilots (verified on-page)

Compared file pair: `pilots/wave1/*.yaml` (gold) vs
`chapter_scripts/calm_student_school__mina_cho__en_US__anxiety__the_bell_is_not_a_verdict/ep_001.yaml` (batch).

1. **Beat grammar flattened.** Batch: every panel `beat_type: micro`; no `mode_beats:`
   block. Pilots: full beat vocabulary (establishing / failure / opening_motif /
   mid_recurrence / turn / close) — the escalation shape inside an episode.
2. **Vessel genericized.** Batch: "Upperclassman", "face optional",
   `teacher_id: brand_teacher_unresolved`. Pilots: a vessel with a *mechanism* (warm the
   cup before the leaves; mute the audio and watch the body; the comb missing one
   tooth). The mechanism IS the commercial hook; the batch keeps the label and loses
   the mechanism.
3. **Interchangeable pressure.** Batch scene text literally reads "a clash, a meeting, a
   cold room, a feed spike, a bell" — one sentence serving all genres. This is the
   flattening the serialization mandate exists to kill.
4. **Template leakage.** Batch scenes contain the formula's stage directions ("The
   vessel does one small genre-native act — a chair pulled out, a foot placement
   corrected...") — un-renderable disjunctions where the pilots have drawable specifics.
5. **No serial memory.** Batch episodes are closed one-shots with an end card; no rival,
   no B-cast, no open loop, no motif state. Nothing binds ep_001 to ep_002 but the
   series_id string.
6. **Music-mode collapse.** The batch sample lane has no representation of motif-state
   lettering (the music pilots' signature render instructions) at all.
7. **Discipline erosion.** Pilots pin palettes to beats (`turn_palette: pages 4-5 only`);
   batch: "genre-led; see craft_notes". Pilots confine dialogue to inflection points;
   batch narrates doctrine in captions ("It knew first." every episode).

## 12. Minimum next writing files (after this spine)

Per lane, in order — nothing else is needed to start proving the engines:

1. **ep_002 chapter script** (`chapter_script_writer_handoff`, Tier-1 authored) — the
   anti-one-shot proof episode. Each lane's ep_002 must (a) re-break the settled state in
   a new context per its V1 row above, and (b) plant the volume pressure (Iron Warden
   patrol / Hadley wobble / Kazu / Sana's splits / Bram's arrival / Clarion flag / the
   senpai's crack / the extraction lab). If ep_002 re-runs wound→turn→renewal to a clean
   cure, the lane is still a one-shot generator — reject it.
2. **Series continuity seed** per series (per `docs/specs/MANGA_CONTINUITY_STATE_SPEC.md`,
   `config/manga/continuity/`): recurring cast sheet (rival + vessel state), set-piece
   registry, and — for music lanes — **motif state** (what condition the motif is in at
   each episode's close), so no future writer resets a motif that has progressed.
3. **`manga_brand_series_plan.yaml` volume-arc rows** for these series: `mode:` (XOR),
   `volume_arcs: [v1..v5]` one-line loglines from this doc, and the rival/pressure
   registry — so the batch selector can never again pick a generic pressure for a lane
   that has a named one.

Flagship exception: `the_alarm_is_lying` already has V1 authored (eps 1–10); its next
file is **ep_011** ("Other People's Alarms" opener), not ep_002.
