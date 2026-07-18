# Vertical Webtoon Drama / Action (Korean format) — Style Bible

Touchstones: *Tower of God* (SIU), *Bastard* (Carnby Kim / Youngchan Hwang — pacing/hook study, not subject), *Sweet Home*, *Noblesse*, *The God of High School*, *Solo Leveling*, *Omniscient Reader*.

Note: We use *Bastard* strictly for its *hook and pacing grammar*, not its thematic content.

## 1. Market + reader contract
Readers are 14–32, mobile-first, action/mystery/thriller-seeking, trained on serialized reveal-based storytelling. They expect *weekly escalation*, *clear power/stakes legibility*, *multi-POV mystery architecture*, and *no slow weeks*. They will reject confusing spatial action, unclear power systems, episodes with no forward motion, and endings that don't sustain long-runner investment.

## 2. Visual grammar
- **Panel count per episode:** 70–140 panels on vertical canvas. Action episodes trend higher.
- **Words per episode:** 150–350 (lower than romance webtoons; action carries more weight).
- **Silent-panel ratio:** 40–60% — action beats are often entirely silent-with-sfx.
- **Black-fill ratio (color-equivalent):** Saturation varies; high-contrast low-light palettes dominate thriller/horror (Bastard, Sweet Home). Key metric: "threat palette dominance" per episode ≥ 40%.
- **Screentone density:** N/A (color). Instead: atmospheric color-gradient fields for mood, harsh high-contrast for reveal/shock.
- **Spread-equivalent:** Megapanels more frequent than romance lane — 3–6 per episode, used for reveals, power displays, threats.
- **Reaction-shot frequency:** Medium — 4–8 per episode, but weighted differently: *the observer's* reaction (the character watching the reveal) carries the audience.
- **Line weight profile:** Heavier, sharper linework; dramatic silhouettes; action frames use motion-streak overlays rather than traditional speedlines.

## 3. Pacing + beat conventions
- **Episode length:** 50–100 screen-views. Cliffhangers mandatory.
- **Chapter hook family:** *Threat introduction or mystery-clue surface* — open on a visible threat (creature silhouette, unknown figure, an object out of place) or a clue the protagonist misses and the reader catches.
- **Chapter ending convention:** *Escalation cliff* — reveal of a new antagonist, new power, new rule, new twist, or the protagonist's visible-to-reader unknown danger one frame behind them. Never a "rest" ending.
- **Scene-to-scene transitions:** Harsh color cuts, POV swaps (Tower of God's constant POV rotation), flash-forward teases, and "someone is watching" panels that reveal observer POV at scene's end.
- **Per-season arc shape:** Season = one "tower floor" / "arc location" / "tournament" / "mission." Classic three-act within season with a mid-season reveal and an end-season power/truth gain.

## 4. Dialogue + narration
- **Register:** Tactical, clipped, informational. Power-system vocabulary matters enormously — readers build wikis. Characters must *name* mechanics.
- **Narration tolerance:** Moderate-high — system-fiction (Solo Leveling) uses captions + UI overlays as primary narration. Classic drama uses less.
- **Dialogue-to-narration ratio:** ~70:30 for pure action; ~50:50 for system-fiction.
- **Interior monologue:** Short, strategic. "If I dodge right, his left is exposed." No lyrical introspection.
- **Tell-don't-show tolerance:** High for power systems (readers *want* the explanation), low for emotion.

## 5. Character + arc conventions
- **Archetype grammar:** The underestimated protagonist with a secret ceiling (Bam, Sung Jin-Woo), the mentor-with-agenda, the loyal companion, the rival-turned-ally, the world-ending antagonist revealed by degrees. Ensemble is the default — even "solo" series rotate POV.
- **Emotional arc per season:** Arrival → testing → early loss → training/power-acquisition → confrontation → pyrrhic win with new mystery surfaced.
- **Cast density:** Large ensemble (15–40 named over a season), with rotation POV. Readers tolerate large casts if introductions are visually distinct.

## 6. Failure modes
1. Unclear power systems. Readers will abandon if rules shift without acknowledgment.
2. Spatial confusion in action (unclear who is where — panel-to-panel 180° violations are deadly in vertical format where the reader can't flip back easily).
3. Slow episodes without a hook end — subscriber drop-off metric.
4. Overexplained mysteries that eliminate speculation fuel.
5. Protagonist invulnerability too early.
6. Static color palette across episodes — kills emotional legibility.
7. Megapanel without reveal payoff at bottom.
8. Romantic subplots that stall the primary action engine.
9. Losing POV discipline — too many POVs in one episode.
10. Ignoring the reader's reconstruction pleasure — this lane lives on the "oh, THAT'S what that was three arcs ago" click.

## 7. Series planning implications (48-volume pre-plan)
Map "volume" to a **season/arc of ~20–30 episodes**. 48 volumes = 48 arcs, which is *Tower of God* / long-runner scale.
- **Macro shape:** 48 arcs as a 4-stage cosmology (like ToG's Floor ascent): arcs 1–12 "ground" / foundation; arcs 13–24 mid-world reveals; arcs 25–36 political/spiritual truth layer; arcs 37–48 endgame ascent.
- Each arc: 20–30 episodes, one major reveal, one new antagonist, one new ally, one new power tier.
- Across all 48: a **central mystery** (who/what/why of the world) that the reader is given a piece of in every third arc. The ending must close the central mystery while leaving ≥1 cosmological ambiguity.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (9):
1. `canvas_slot` — vertical screen-view index
2. `panel_type` — {action, reveal, reaction, establish, megapanel, text_ui/system}
3. `framing` — CU / MCU / MS / WS / aerial / vertigo (tall fall-or-rise)
4. `spatial_anchor` — the orientation anchor (left/right/depth) — mandatory for action panels to prevent 180° violations
5. `dialogue` — ≤15 words; can be absent
6. `sfx` — action sfx can be large & canvas-integrated
7. `power_tag` — if the panel displays a named ability, log it (for system consistency tracking)
8. `hook_tier` — {none, micro, episode-end, arc-end} — episode-end and arc-end require specific reveal types
9. `pov` — whose perspective this panel occupies (rotates deliberately)

## 9. Three canonical chapter-opening examples

**A.**
The door at the top of the stairs had not been there yesterday. Bam was certain of this because yesterday he had stood on this exact landing for two hours, memorizing every door in the corridor, and this one — unpainted, iron, bolted from the *inside* — had not existed. He reached for the handle. Something on the other side of the door exhaled. Not a person's exhale. He withdrew his hand slowly. Behind him, Rak's voice, for once not shouting: "Black Turtle, step back." The door's bolt, from the inside, began to turn.

**B.**
The first scream from the apartment below cut off too cleanly. That was what Hyun noticed — not the scream, but the way it stopped, as if someone had closed a door on it. He sat up in bed. The building's old hallway lights hummed, then flickered, then held. From the floor beneath him: nothing. A full forty seconds of nothing. Then, through his floorboards, a single soft scrape, moving slowly across the ceiling of the apartment below him — which meant, *across his floor*, on the *ceiling side*. Something down there was climbing.

**C.**
The system window opened at 2:14 a.m., directly in front of Jinwoo's face, as he lay on a hospital cot he did not remember being moved to. *[You have met the conditions for secret quest: "Survive."]* He stared at it. The nurse at the station across the hall was asleep. No one else could see the window; he already knew this, because the last eleven windows had also been invisible to everyone else. *[Accept?]* Two buttons. Yes. No. He had learned, six windows ago, that *No* did not work. He pressed Yes.

## 10. References
- SIU creator blog + translator notes, *Tower of God* (Naver / Webtoon).
- Carnby Kim interviews on craft and pacing in thriller webtoons, *Kakao Entertainment* 2019.
- *Solo Leveling* creator/adaptor interview, *Manta* platform press kit 2020.
- Park Joo-ha, "Vertical Scroll Grammar in Korean Webtoons," *Journal of Graphic Novels and Comics*, 2019.
- Scott McCloud, *Making Comics*, ch. 1 — panel-transition taxonomy adapts directly to vertical format.
