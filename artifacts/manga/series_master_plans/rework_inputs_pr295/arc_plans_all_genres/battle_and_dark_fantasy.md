# Full-genre-coverage exercise: battle + dark_fantasy (stoic_edge_battle, warrior_calm_cultivation, trauma_path_healing, healing_ground_healing)

Planning-only structural outlines (4 arcs x 12 episodes = 48 episodes per brand).
No chapter_script or arc_storyboard files were written; no CI gates were run;
no git actions were taken. Source of truth for this pass:
`docs/research/manga_craft/action_battle.md` §7 (48-Volume Shape) and §1 (Market
Contract, `stoic_edge_battle` citation), `docs/research/manga_craft/dark_fantasy.md`
§7 (48-volume shape) and §1 (Market contract), `config/source_of_truth/manga_story_strategies/action_battle_strategies.yaml`,
`config/source_of_truth/manga_story_strategies/dark_fantasy_strategies.yaml`, and
`/tmp/claude-0/-home-user-pearl-prime/6799991e-03f6-596a-af48-5bfdf3651a9e/scratchpad/genre_assignment_37brands.md`
(master 37-brand x 25-genre assignment table for the larger exercise this is one
slice of).

**Craft-resource note (corrects the dispatch brief for this slice):** the master
assignment doc's "craft-resource availability" section flags checking whether
`dark_fantasy_strategies.yaml` exists as an open question. It does exist (5
strategies: grief, despair, meaning, perseverance, loss; `grief -> strategy_01`,
"The One Who Stays Behind" — the Frieren-register long-memory device). Both
brands below use it as their grief throughline, differentiated by vessel (see
each brand's note) rather than by strategy substitution, since both brands
share `grief` as `primary_topic` per the assignment table.

**Topic-coverage note (battle side):** `action_battle_strategies.yaml`'s
`topic_strategy_map` covers `courage, anger, self_doubt, protecting_others,
resolve` — `courage` (stoic_edge_battle) is a direct hit (`strategy_01`, "The
Strike Before the Fear Lands"). `burnout` (warrior_calm_cultivation) is not a
listed topic. Per the dispatch doctrine's fallback (work from the bible's
topic-carrying description when no direct strategy exists), `warrior_calm_cultivation`
adapts `strategy_02` ("The Fire That Protects, The Fire That Burns" — anger's
device of a technique that wins by consuming its own wielder) as the closest
structural analog: redlining a finite output to win is anger's device and
burnout's mechanism alike, and the arc's turn (banking the fire instead of
suppressing or maximizing it) maps directly onto sustainable-pacing recovery
from burnout without ever naming "burnout" in-panel.

**Dark-fantasy 4-stage compression note:** the craft bible's SS7 48-volume
shape is 5 uneven stages (vols 1-6 / 7-18 / 19-30 / 31-42 / 43-48). This
program's fixed 4x12 episode grid requires an explicit compression, done
identically for both dark_fantasy brands below: **Wound Introduction (ep
001-012)** = bible vols 1-6 + first third of the Long Compression; **The Long
Compression (ep 013-024)** = bible vols 7-18; **The Naming (ep 025-036)** =
bible vols 19-30; **The Carried Weight (ep 037-048)** = bible vols 31-42
merged with the Long Aftermath (vols 43-48) — identity rebuilt AND the
"what it means to continue" close land in the same final arc rather than a
separate fifth block.

---

## stoic_edge_battle
Genre (this exercise): battle | Primary topic: courage
Note: reassigned from established genre for full-taxonomy coverage exercise (see genre_assignment_37brands.md). Vessel: ritual one-on-one blade duels on floating platform-arenas (the "Still Point" dueling tradition) — literal fighting-world register, distinct from warrior_calm_cultivation's energy-circuit sparring below. Craft throughline: `action_battle_strategies.yaml` `courage -> strategy_01`, "The Strike Before the Fear Lands" (courage as the strike thrown while the hands are still shaking, never a pep-talk).

**Arc 1 — Inciting Fight / Training Arc (ep_001-012):** A duelist raised in the Still Point tradition — composure as the whole style, never raise your voice or your guard until it's already too late to be afraid — is thrown into a duel far above her sanctioned rank and loses badly, guard folding on the first real pressure. A retired champion takes her on, teaching not fearlessness but the single-committed-movement discipline of striking before the shake finishes arriving. Closes recognizably different, not at the ceiling.

**Arc 2 — Rival / Escalation Arc (ep_013-024):** She enters the formal dueling league; a rival duelist who never trembles at all — flawless, cold, unbeaten — mirrors and needles her, contempt with an undercurrent of respect. Ensemble duelists each face their own version of the freeze-at-the-edge wound. The league's bracket structure becomes a mirror of the cast's fears, not just a ladder to climb; closes on an upset that surprises her own self-image.

**Arc 3 — Revelation Arc (ep_025-036):** The Still Point order is revealed to select and discard duelists who show visible fear early, quietly burying promising fighters' careers rather than teaching them to hold a trembling guard — the tradition she trusted has been grading out exactly what she had to learn to keep. Her mentor's own buried failure in the tradition surfaces. Moral complexity enters without breaking the genre's optimism.

**Arc 4 — Reckoning / Final Confrontation Arc (ep_037-048):** The league's undefeated champion — the rival's mirror taken to its worst extreme, a duelist who no longer feels anything at all rather than one who fights through feeling it — becomes the final opponent. Every scar from arcs 1-3 is present in how she stands. Victory is earned by a guard that holds while visibly shaking, not by finally becoming fearless; the ceiling she inherited from the order is broken, not erased.

---

## warrior_calm_cultivation
Genre (this exercise): battle | Primary topic: burnout
Note: reassigned from established genre for full-taxonomy coverage exercise (see genre_assignment_37brands.md). Vessel: internal-energy sparring circuits (qi-output combat, redlining vs. banked-flame technique) — distinct fighting world from stoic_edge_battle's blade duels above; battle-genre tournament mechanics, not cultivation-genre power-grinding. Craft throughline: `burnout` has no direct `action_battle_strategies.yaml` entry (see file-level topic-coverage note); adapts `anger -> strategy_02`, "The Fire That Protects, The Fire That Burns," treating redlined qi output as the same device as consuming rage.

**Arc 1 — Inciting Fight / Training Arc (ep_001-012):** A prodigy wins early sparring matches by pushing her qi output past every sanctioned limit — spectacular, and it works, until it doesn't: a bout ends with her collapsed, unable to stand, having burned through reserves she didn't know had a bottom. A circuit elder takes her on, teaching the banked-flame discipline (breath and circulation control) instead of raw maximal output. Closes with her first sparring win using banked output — smaller, but she's still standing after.

**Arc 2 — Rival / Escalation Arc (ep_013-024):** She enters the regional qi-circuit tournament; a rival who has always fought on banked, sustainable output humiliates her early by simply outlasting her old habits. Ensemble teammates each carry their own version of running on empty for others' sake. The tournament bracket becomes a mirror of who can still stand in the third round, not just who hits hardest in the first; closes with her circuit reputation upended by an opponent she underestimated.

**Arc 3 — Revelation Arc (ep_025-036):** The circuit itself is revealed to profit from burning out young fighters fast and replacing them — sponsors favor spectacular redlined bouts over sustainable careers, and her elder's own body carries decades of the cost the circuit never warned its fighters about. Moral complexity enters: the system that trained her to bank her flame is the same system that profits when other fighters don't.

**Arc 4 — Reckoning / Final Confrontation Arc (ep_037-048):** The circuit's reigning champion — a fighter who has fully burned through himself chasing an unbeaten streak, running on fumes and calling it strength — is the final opponent, the shadow of who she almost became in Arc 1. Every training scar from arcs 1-3 shapes her stance now. Victory is earned through pacing and banked reserve outlasting his redline, not through outmatching him in raw output; she carries the sustainable practice forward rather than returning to "normal."

---

## trauma_path_healing
Genre (this exercise): dark_fantasy | Primary topic: grief
Note: reassigned from established genre for full-taxonomy coverage exercise (see genre_assignment_37brands.md). Vessel: a mobile, longevity-adjacent grief register — a war survivor who outlived her entire company walks a pilgrim road between old battlefields, ferrying grieving travelers past the graves. Distinct from healing_ground_healing's stationary, single-loss register below. Craft throughline: `dark_fantasy_strategies.yaml` `grief -> strategy_01`, "The One Who Stays Behind" (the Frieren-register device: grief as the slow accumulation of empty chairs, never resolved within a chapter, only carried differently).

**Arc 1 — Wound Introduction (ep_001-012):** Establish the protagonist as the last living member of a mercenary company wiped out in a war now generations gone; she walks the long road between ruined waystations, tending graves and guiding grief-stricken travelers past them. Each episode costs something that cannot be returned — a companion's memory that's started to fade, a stranger's grave she cannot properly mark. The world's cruelty is structural: the road is long precisely because the war never really stopped costing people.

**Arc 2 — The Long Compression (ep_013-024):** New traveling companions attach themselves to her over these episodes, and the road's dangers begin to fall on them instead of just on her — one major, irreversible loss lands. A warlord-adjacent authority that mass-produces the war dead she's spent her life ferrying is revealed, with a coherent (if monstrous) logic: ending resistance quickly is its own mercy.

**Arc 3 — The Naming (ep_025-036):** She cannot undo what the road has already cost her, but starts naming it aloud for the first time — teaching her newer companions how to grieve instead of suppress. The antagonist's worldview earns genuine consideration even as she keeps opposing it. Small, hard-won acts of meaning-making appear: a proper name finally carved into a stone that has waited generations for one.

**Arc 4 — The Carried Weight (ep_037-048):** She acts from what she's named rather than from raw wound-reaction, confronting the antagonist not to win a war but to stop the machine that keeps producing graves for her road to carry. The world isn't healed — the dead remain dead — but her relationship to the weight changes. Closes on an image that rhymes with the opening wayside marker at a deeper key: she's still walking the road, but for the first time, not alone in carrying it.

---

## healing_ground_healing
Genre (this exercise): dark_fantasy | Primary topic: grief
Note: reassigned from established genre for full-taxonomy coverage exercise (see genre_assignment_37brands.md). Vessel: a stationary, single-specific-loss register — a warden bound to one cursed battlefield-turned-graveyard where her sibling died defending it, and where the improperly-buried dead do not stay down. Distinct from trauma_path_healing's mobile, decades-of-cumulative-loss register above. Craft throughline: also draws on `dark_fantasy_strategies.yaml` `grief -> strategy_01` (grief carried, not resolved) but grounds it in one named death and one fixed place rather than an outlived generation.

**Arc 1 — Wound Introduction (ep_001-012):** Establish the protagonist bound to the ground since her sibling died defending it; the ground itself is restless — improperly laid dead surface and wander. Her early duties as warden cost something irreversible each time: a haunting she cannot fully lay to rest, a stranger she must turn away from digging where digging isn't safe. The place's cruelty is structural — it was consecrated to heal the war-dead and was never finished.

**Arc 2 — The Long Compression (ep_013-024):** Word of the ground's healing reputation spreads; refugees and pilgrims arrive wanting to bury their own dead there, forcing impossible choices about who the ground can hold. She takes on more of the dead's unfinished business than one warden can carry, and a faction seeking to harvest or weaponize the ground's restless dead — led by someone whose own grief has curdled into wanting to erase death itself — is revealed.

**Arc 3 — The Naming (ep_025-036):** She begins to separate tending the ground from being consumed by it, and names her sibling's death aloud to another person for the first time in the series. The antagonist's reasoning — that erasing death, however violently, is its own mercy — earns real consideration even as it terrifies her. A found-family warmth grows among the ground's regular pilgrims.

**Arc 4 — The Carried Weight (ep_037-048):** The final confrontation forces a choice about what the ground is for: erasing grief, or holding it. She acts from her named relationship to the place rather than raw duty, and though the ground is not "healed" — the dead remain, the war's damage remains — her role in it changes: from lone sentinel to the one who teaches newer wardens how to tend it. Closes on an image that rhymes with the opening graveside kneel at a deeper resonance — she can finally leave it without fearing she'll forget.
