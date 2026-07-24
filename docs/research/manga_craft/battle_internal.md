# Battle Internal (Internal Battle / Philosophical) — Craft Bible

> Absorbed from PR #295 branch (`claude/manga-12ep-arc-authoring-egnwqf` @ `4c6e2c3d59`), reworked per operator ruling Q-MPU-02 (2026-07-24): #295 itself is never merged; this lane's PR is the landing path.

Touchstones: *Vagabond* (Inoue Takehiko — Musashi's swordsmanship as externalized self-doubt), *Berserk* (Miura Kentaro — contemplative arcs between Guts's revenge-drive and his search for meaning, esp. the Conviction Arc / Birth Ceremony chapters), *Vinland Saga* (Yukimura Makoto — Thorfinn's post-revenge pacifism arc, farmland era), *One Punch Man* (ONE/Murata — Garou's philosophical-nihilist battles staged as monologue-fights), *Homunculus* (Yamamoto Hideo — trepanation-sight as literalized inner combat).

## 1. Market + reader contract

Readers are 16–35, majority-male-skewing but with real crossover (Vinland Saga's farmland arc pulled a broad adult readership beyond its shonen-battle base), who arrive *wanting* a fight and stay for a conviction. The genre's contract is a bait-and-switch the reader has already agreed to: the cover promises a swordsman, a monster-fighter, a rival battle — and the story delivers that expectation's shape (stance, tension, an opponent, an outcome) while the actual stakes are entirely interior (doubt, guilt, a vow under test, the pull back toward violence). Readers will accept an opponent who never lands a physical blow of consequence *only if* the panel grammar makes the internal stakes read as load-bearing as a physical wound would. They will reject two things instantly: (1) a "battle" that turns out to be nothing — all atmosphere, no cost — and (2) a narrator or mentor who explains the metaphor. The metaphor must fight for itself.

## 2. Visual rules / visual grammar

Canonical pacing data (`config/manga/manga_pacing_by_genre.yaml` → `battle_internal:`):
- **words_per_page_range:** 70–110
- **words_per_balloon_max:** 28
- **silent_panel_ratio_range:** 0.20–0.35
- **reaction_shot_frequency:** medium
- **spread_frequency:** rare
- **page_turn_triggers:** vow, betrayal, revelation, realization_beat
- **narration_tolerance:** moderate
- **sfx_usage:** minimal
- **background_density:** sparse_realist
- **reference_corpus:** *Vagabond*, *Berserk* (contemplative arcs)

Additional visual-grammar rules built from those touchstones:

- **Panel count per chapter:** 16–28 pages of a genuinely sparse grid (3–5 panels/page average) — internal-battle chapters run *fewer* panels than external-battle chapters at the same page count, because each panel is asked to hold more psychological weight. Never compensate for a slow scene by cramming more panels; compensate by widening them.
- **The opponent-as-mirror composition:** when the "opponent" is a memory-self, a rival who represents a road not taken, or an externalized doubt, stage them in the same panel geometry a physical duel would use — matched stances, matched eyelines, a shared horizon line — so the reader's body reads it as combat before their mind catches up on the metaphor. Inoue's Musashi-vs-Kojiro panels and mirrored posture between present-Iris and memory-Iris (per this catalog's `battle_internal` worked example, `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/workplace_essay_battle_internal.md` (not yet on main — lands via Lane 06's absorb of the #295 arc plans; re-verify path after that merge)) both use this.
- **Line weight profile:** heavy, brush-worked contour lines during the internal confrontation itself (Inoue's post-vol.10 brush transition, sought specifically to intensify emotional expression beyond what pen line permitted); thin, controlled pen line in the "ordinary world" bracketing scenes. The line-weight shift IS the signal that the internal battle has begun — readers should be able to tell from line quality alone, without dialogue, that the register has changed.
- **Sword/weapon-as-burden staging:** an internal-battle protagonist's weapon (or professional tool — a scalpel, a pager, a stylus) is drawn heavy and effortful, never balletic, when the internal conflict is live; Guts's Dragonslayer is rendered as something that costs strength to lift, not a badge of power. A weapon drawn lightly signals resolved conviction; drawn as burden signals live doubt.
- **Black-fill ratio:** 0.20–0.40, concentrated as *shadow that swallows the opponent-figure* rather than the environment — Berserk's psychological pages use dark/light contrast specifically to stage inner turmoil, not just atmosphere.
- **Silent-panel sequencing:** silent panels cluster in 3–6 panel unbroken runs at the moment of maximum internal stakes (the blow not thrown, the line not said) — this is where the 0.20–0.35 ratio concentrates rather than spreading evenly.
- **Spreads:** reserved almost exclusively for the vow moment or the realization_beat — never for scale/scenery. A battle_internal spread should feel like the floor dropping, not like a splash page.
- **Background register:** sparse_realist per pacing data — background detail recedes to near-nothing at the confrontation's peak (a blank field, a single tree, an empty dojo) so nothing competes with the two figures/postures carrying the scene.

## 3. Pacing + beat conventions

- **Chapter hook family:** *Stance-set.* Open on a body in physical readiness (a hand near a hilt, a breath held, a stance taken) before the reader knows whether a physical or purely internal confrontation is coming — the ambiguity is the hook. Do not resolve which kind of battle it is for at least 2–3 panels.
- **Chapter ending convention:** *Unthrown blow* or *unresolved vow.* The chapter ends at the instant of maximum tension — the blow withheld, the temptation resisted-but-not-yet-integrated, a vow spoken but not yet tested. Never end on a clean physical victory in this lane; a physical win with the internal question still open is the correct chapter-ending shape (Thorfinn beaten and not fighting back is the model).
- **Scene-to-scene transitions:** stance-to-stance visual rhymes (a battle posture from chapter open answered by an identical or inverted posture at chapter close); memory-intrusion cuts with no caption bridge (the memory-self simply appears in-panel, per the pacing table's `realization_beat` trigger); no explanatory time-skip captions — let the reader infer duration from physical state (wound healing, season change, hair grown out).
- **Per-volume arc shape:** a volume-length "duel" that is mostly *waiting* — training, walking, sitting, working — punctuated by 1–3 true confrontation chapters where the internal stakes peak in physically-staged form. The waiting is not filler; per the pacing table's `page_turn_triggers` (vow, betrayal, revelation, realization_beat), each waiting stretch must still land at least one of these per volume, or the volume reads as inert rather than contemplative.
- **Escalation logic across volumes:** the *cost of losing the internal battle* must escalate even though the external stakes may stay flat or even shrink (Thorfinn's farmland arc lowers the external stakes from "war" to "a farm," while the internal stakes — will he revert to violence — rise). This inversion (external stakes down, internal stakes up) is the genre's core structural move and should be planned deliberately, not allowed to happen by accident of a quiet arc.

## 4. Dialogue + narration

- **Register:** spare, often near-silent during the confrontation itself; dialogue outside the confrontation can be fully naturalistic and even mundane (farm talk, training-ground banter) — the contrast between mundane surrounding dialogue and charged confrontation silence is load-bearing.
- **Narration tolerance:** moderate per pacing data. Narration/caption is permitted to name a *stake* ("He had sworn never to draw it again.") but must never name the *resolution* or *lesson* — the panel resolves it, or it stays open.
- **Dialogue-to-narration ratio:** ~55:45 — heavier on narration/caption than most action lanes, because internal stakes need some anchoring text, but never so heavy it becomes essay register (that drift belongs to `graphic_medicine`/`memoir`, not here).
- **Interior monologue:** handled through externalized address — Garou's internal debates staged as if arguing with an imagined opponent; a memory-self who speaks the doubt aloud rather than a thought-caption stating it. Direct first-person thought captions ("I was afraid") are permitted but should be rationed to one per confrontation sequence at most — the visual staging should be doing most of the work.
- **The opponent's dialogue as the protagonist's suppressed voice:** when the opponent is fully metaphorical (a memory, a rival embodying a rejected philosophy), their dialogue should say things the protagonist cannot yet say to themselves. This is the genre's single most useful dialogue technique and its most commonly abused one (see Failure Modes #2).
- **Vow language:** vows are spoken once, in full, and never restated verbatim later — later references gesture at the vow ("You remember what you said.") without quoting it, preserving its weight.

## 5. Character + arc conventions

- **Protagonist archetype:** a capable fighter/professional whose *technical* mastery is not in question — the doubt is never "can I do this," it is "should I / who am I if I do this." Musashi's swordsmanship is never technically in doubt; his self-conception is. This distinction must be maintained — a protagonist who is bad at the external skill collapses the genre into ordinary competence-drama.
- **The mirror-opponent:** a rival, memory-self, or philosophical antagonist who is not defeated so much as *outlasted or integrated*. Garou is the clearest modern example — his physical battles are vehicles for an ideological argument that doesn't resolve in a KO. Kojiro (Vagabond) functions as Musashi's unattainable "pure" ideal rather than a villain.
- **Supporting cast size:** small, 2–5 recurring; often includes at least one character who has *already* resolved the version of the internal battle the protagonist is fighting (Vinland Saga's Ketil-farm elders; a retired teacher; an old rival now at peace) — they function as a lived answer key the protagonist can see but not yet use.
- **Emotional arc per volume:** readiness (brittle) → provocation → the near-relapse (protagonist nearly reverts to the old self/old violence) → a held line (small, costly, not triumphant) → new readiness at a different altitude. Unlike shonen-battle escalation, the "win" is a held line, not a defeated opponent.
- **Body-as-record:** scars, calluses, a specific old wound revisited are used as legible history — the body keeps score where dialogue won't state it (Berserk's scars as "torment endured psychologically," not just battle trophies).

## 6. Failure modes

1. **The battle turns out to be literal after all.** A "purely internal" confrontation that resolves via an actual physical fight with an actual entity cheapens the whole lane — the metaphor must stay a metaphor, or the story has quietly become straight action_battle.
2. **The mentor/narrator explains the metaphor.** Any line of dialogue or caption that states "this fight represents your inner doubt" kills the genre instantly. Trust the stance-mirroring and line-weight shifts to carry it.
3. **Technical incompetence mistaken for internal conflict.** If the protagonist is bad at the skill, the audience reads clumsiness, not doubt. Competence must be visibly intact throughout.
4. **Villain-as-therapist.** The mirror-opponent diagnosing the protagonist's psychology in dialogue (rather than embodying it through posture/action) is the same failure as #2 wearing a costume.
5. **Winning the internal battle permanently in one chapter.** Internal battles that resolve cleanly and never resurface read as false — the genre's contract is that the pull back toward the old self recurs, at lower amplitude, across the whole series.
6. **Escalating only the external stakes.** If tension is manufactured purely by raising physical danger while the internal question stays static, the story has drifted into `action_battle`; per §3, internal stakes must be the escalating axis.
7. **Overusing spreads for scale/spectacle.** A battle_internal spread used for scenery rather than the vow/realization_beat wastes the genre's rarest visual currency (spread_frequency: rare).
8. **Resolving the vow by quoting it back verbatim as a mic-drop line.** Repeating the vow word-for-word as a triumphant callback reads as shonen grammar bleeding into a lane that should resist easy triumph.
9. **No physical cost ever.** Even though the battle is internal, the body must occasionally pay a real, visible price (an old wound reopening, exhaustion, a hand that won't stop shaking) — a purely bloodless internal battle loses the genre's promised weight.

## 7. Series planning implications (48-volume pre-plan)

48 volumes of battle_internal sustains well because the "waiting" pacing (§3) is inherently economical — unlike seinen-psych's catharsis-denial fatigue, this lane's slow stretches read as earned training/recovery time rather than punishment. Shape:

- **4 × 12-volume convictions**, each built around one vow and its full lifecycle: vol 1–3 the vow is formed under provocation; vol 4–8 the vow is tested by rising temptation (the internal stakes climbing per §3's inversion logic, even as external stakes may fall); vol 9–11 a near-total relapse (the closest the protagonist comes to breaking the vow across the whole era); vol 12 the vow holds, at real cost, and the *next* era's provocation is planted in the closing chapter.
- The mirror-opponent for each 12-volume era should be a *different* character or memory-version, so the protagonist is not simply re-fighting the same rival four times — Vinland Saga's shift from revenge-Thorfinn's rivals to farmland-Thorfinn's internal argument with his own violent past is the model for how the "opponent" can mutate era to era while the vow-cycle shape stays constant.
- Volume 48 should not resolve the internal battle into permanent peace — it should show the protagonist able, for the first time, to recognize the old pull *without* the reader needing a caption to confirm it, closing the series on competence at holding the line rather than victory over having a line to hold.

## 8. Panel scaffolding

Per-panel fields (9):

1. `framing` — standard set plus `stance_mirror` (matched or inverted posture against the opponent/memory-self) and `weapon_or_tool_insert` (close on the burden-object)
2. `beat_role` — one of {stance_set, provocation, near_relapse, held_line, vow_formed, vow_tested, mirror_confrontation, realization_beat, aftermath}
3. `dialogue` — ≤28 words per pacing data; can be voiced by the mirror-opponent saying what the protagonist cannot yet say to themselves
4. `caption` — optional, ≤20 words; names a stake, never a resolution
5. `line_weight_register` — brush_heavy (live internal battle) / pen_controlled (ordinary-world bracket) — the visual tell of which mode the chapter is in
6. `background_register` — sparse_realist per pacing data; scales toward near-empty at confrontation peak
7. `body_cost` — integer 0–3 (0 = no visible physical toll, 3 = a real wound/collapse) — must reach ≥1 at least once per confrontation sequence per Failure Mode #9
8. `silence_flag` — boolean; true forbids dialogue AND caption; clusters in 3–6 panel runs at the moment of maximum stakes
9. `sfx` — minimal per pacing data; interior sfx (a heartbeat, a breath, a held creak of leather/grip) permitted, never externalized combat SFX unless the physical plane is genuinely engaged

**Generator constraint:** `silence_flag=true` panels must appear in runs, never isolated singly, when `beat_role` is `near_relapse` or `held_line`; `line_weight_register=brush_heavy` may not appear on a `stance_set` opening panel (the ambiguity of §3's hook depends on withholding the tell until at least panel 3).

## 9. Locale weighting

| Locale | Signal | Rationale |
|---|---|---|
| `ja_JP` | **Primary** | Native register for Vagabond/Berserk/Vinland Saga lineage; seinen craft bar is highest here — genre-authenticity gate must pass against these exact touchstones. |
| `en_US` | **Primary** | Strong crossover pull (Vinland Saga's farmland arc, One Punch Man's Garou arc both broke out with Western readers beyond core shonen-battle fandom); digital-first discovery via "is this really a fight?" discourse clips. |
| `zh_TW` | **Secondary** | Established seinen/action-adjacent readership; philosophical-battle framing tests well alongside wuxia-adjacent internal-cultivation storytelling. |
| `zh_CN` | **Secondary** | Cultivation/martial genre crossover audience receptive to internalized-combat framing; gray-zone distribution per spec D-19 applies as with `dark_fantasy`. |
| `ko_KR` | **Tertiary (rendered + held)** | Webtoon vertical adaptation viable but untested for this specific internal/stance-mirror grammar; requires format-adaptation pass before commit. |

---

*Sources: `config/manga/manga_pacing_by_genre.yaml` (`battle_internal:` entry, ~line 273–291), `config/manga/canonical_genre_list.yaml` (`battle_internal` row, ~line 273, label "Internal Battle / Philosophical", `parent_family: battle`), `config/manga/main_character_interaction_grammar.yaml` (`battle_internal: {quality_gate_checks: [self_or_memory_interaction]}`, line 33), `docs/research/manga_craft/seinen_psychological.md` (structural/formatting template), `docs/research/manga_craft/dark_fantasy.md` (9-section schema confirmation), `docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/arc_plans_all_genres/workplace_essay_battle_internal.md` (not yet on main — lands via Lane 06's absorb of the #295 arc plans; re-verify path after that merge) (`stabilizer_healing` worked example — bench/memory-self staging). WebSearch: "Vagabond swordsman internal psychological battle manga visual technique Inoue" (animeoftheelite.com/vagabond-manga-analysis, yokogaomag.com/editorial/vagabond-takehiko-inoues-mastery-of-expression — brush transition ~vol.10–12, sumi-e technique); "Vinland Saga pacifism arc Thorfinn internal struggle manga panel technique" (tokyomangashelf.com/blog/vinland-saga-review, animenagi.com/thorfinns-pacifism-explained — farmland-arc beating scene, revenge-cycle framing); "One Punch Man Garou psychological battle internal monologue villain arc manga craft" (deltiasgaming.com/article/garou-is-one-of-the-best-written-characters-in-one-punch-man, technosports.co.in — ideological-battle framing, monsterization-as-visual-psychological-breakdown); "Berserk contemplative arcs internal conflict Guts psychological visual technique manga" (animeoftheelite.com/berserk-manga-analysis, cbr.com/berserk-manga-character-development-theme-analysis — shadow/light psychological contrast, Dragonslayer-as-burden, Conviction Arc found-family framing).*
