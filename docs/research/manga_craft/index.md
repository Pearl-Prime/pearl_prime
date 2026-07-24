# Manga / Webtoon / Graphic Novel Craft Style Bibles

Per-lane style bibles for 48-volume series planning and deterministic panel-level script generation. Each lane file follows a standard 10-section schema (market contract, visual grammar, pacing, dialogue, character, failure modes, 48-volume implications, panel scaffolding fields, three canonical opening examples, references).

## Lanes

1. **[iyashikei_minimalism](iyashikei_minimalism.md)** — Healing/slice-of-life josei register (Mushishi, Yokohama Kaidashi Kikō, Aria). Low-arousal atmospheric work; volumes are seasonal cycles, not arcs.
2. **[josei_adult_memoir](josei_adult_memoir.md)** — Diaristic autobiographical manga (Nagata Kabi, Asano's *Solanin*). Caption-dense confessional; resists transformation arcs.
3. **[seinen_psychological](seinen_psychological.md)** — Adult psychological drama (Punpun, *A Silent Voice*). Moral ambiguity, withheld resolution, symbolic-substitution grammar.
4. **[shojo_romance](shojo_romance.md)** — Relationship-ladder romance (Fruits Basket, Kimi ni Todoke). Delay engine; long proximity arcs with ornamental mood-tone fields.
5. **[shonen_encouragement](shonen_encouragement.md)** — Craft/vocation manga (Blue Period, Sweat and Soap, Hikaru no Go). Technical-vocabulary honesty; practice as narrative engine.
6. **[webtoon_vertical_romance](webtoon_vertical_romance.md)** — Korean vertical-scroll romance (Lore Olympus, True Beauty). Color-mood-field storytelling, episodic hook cadence, season cliffs.
7. **[webtoon_vertical_drama](webtoon_vertical_drama.md)** — Korean vertical-scroll action/mystery (Tower of God, Bastard pacing). System-fiction captions, POV rotation, arc-per-season escalation.
8. **[BL_slice_of_life](BL_slice_of_life.md)** — Adult queer slice-of-life (Given, My Brother's Husband). Domestic-particular grammar; mutual-intimacy register; homophobia handled with specificity.
9. **[graphic_novel_us_literary](graphic_novel_us_literary.md)** — Western literary memoir graphic novels (Fun Home, Persepolis, This One Summer). Essayistic captions, non-linear memory, single-book completeness.
10. **[kodomomuke_educational](kodomomuke_educational.md)** — Children's encouragement + somatic-literacy (Doraemon, Chi's Sweet Home). Warm resolution per chapter, named body-feelings, caregiver-friendly read-aloud register.

### Phase 2X.3 strategic-shell additions (per spec §4.1 + OQ-1/OQ-2 resolutions)

11. **[dark_fantasy](dark_fantasy.md)** — Berserk / Frieren register (Genre Shell #2; Mega tier per `GENRE_PORTFOLIO_PLAN.md`). Carries grief, trauma recovery, perseverance, identity under extreme pressure, meaning-making. Adult seinen primary; josei crossover (Frieren-tent).
12. **[psychological_thriller](psychological_thriller.md)** — Death Note / Monster / Mob Psycho register (Genre Shell #7). Carries overthinking-as-paranoia, unreliable narrator = imposter syndrome, obsession loops. `cognitive_clarity` brand persona.
13. **[supernatural_mystery](supernatural_mystery.md)** — Mushishi / xxxHOLiC / Natsume's Book of Friends register (Genre Shell #4). Carries grief (unfinished business), generational trauma, spirit/human boundary. `stillness_press` brand carries somatic content inside this shell.
14. **[sci_fi_cyberpunk](sci_fi_cyberpunk.md)** — Akira / Ghost in the Shell / BLAME! register (Genre Shell #6). Carries burnout (machine-body metaphors), digital anxiety, identity (human vs system). `digital_ground` persona — "the developer who optimized everything except themselves."
15. **[workplace_drama](workplace_drama.md)** — Aggretsuko / Wotakoi register (Genre Shell #9). Carries burnout, imposter syndrome, social anxiety, financial anxiety. 6 workplace brands live here (`career_lift`, `high_performer`, `executive_calm`, `morning_momentum`, `optimizer`, `focus_sprint`).
16. **[action_battle](action_battle.md)** — Naruto / Demon Slayer / Vinland Saga register (Genre Shell #10; renamed from former `shonen` slug — demographic ≠ genre). Carries courage, resilience, somatic body-as-tool, perseverance.
17. **[sports_competition](sports_competition.md)** — Slam Dunk / Haikyuu register (Genre Shell #11). Carries ADHD hyperfocus, performance anxiety, imposter syndrome at peak moments, financial pressure around athletic careers.
18. **[historical_period](historical_period.md)** — Vinland Saga / Vagabond / Bride's Story register (Genre Shell #12). Carries grief across time, legacy and self-worth, courage in context, honor vs authenticity. Viking is a setting flavor inside this genre, not its own.
19. **[mecha](mecha.md)** — Evangelion / Gundam / Knights of Sidonia register (Genre Shell #15; mega-example tier per spec D-9; Evangelion $16B franchise). Carries depression-as-mecha, scale-as-mortality, identity vs machine. `cognitive_clarity` brand 15% allocation.

### M2/M3 lane closure (2026-07-23)

20. **[cultivation_martial](cultivation_martial.md)** — Soul Land / A Record of a Mortal's Journey
    to Immortality / Battle Through the Heavens register. Progression-fantasy power-tier ladder;
    primary tier in `zh_CN` (18% share, largest single genre in that locale's allocation),
    secondary in `zh_TW` (8%). Carries face/reputation stakes alongside raw power progression —
    the genre's key divergence from Japanese shonen escalation grammar. This closes the last gap
    among the 15 `VALID_GENRES` slugs consumed by `generate_catalog_plan_from_strategic.py`
    (all others already resolve to an existing bible via `config/manga/canonical_genre_list.yaml`
    aliases; `cultivation_martial` → `cultivation` had no bible file until this entry).

### M3 Wave-1 stub expansions (2026-07-24, manga process uplift Lane 05)

The three M3 Wave-1 stub bibles (~2 KB each) are now full 10-section bibles at the standard bar.
(The earlier note that `school_coming_of_age` landed as a stub via `#4614` is superseded by row 23.)

21. **[isekai](isekai.md)** — Re:Zero / Mushoku Tensei / Frieren-adjacent register (`fantasy_adventure` family; pacing key `fantasy`). Second-chance recovery shell: permission to begin again without erasing the old-world wound. Carries burnout (zh_CN 12% primary allocation via the burnout→isekai recovery shell) and self-worth (no resume follows you).
22. **[psychological_horror](psychological_horror.md)** — Uzumaki / Higurashi / The Summer Hikaru Died register (pacing key `horror`; own `top_8_deep` drawing-tradition block, distinct from the deferred `horror` genre id). "The mind betrays" — dread before it can be named. The CJK flagship shell (ja_JP / zh_TW / zh_HK 14% primary each); carries anxiety-as-entity and somatic trauma as a house that remembers; highest therapeutic-susceptibility readership in the catalog.
23. **[school_coming_of_age](school_coming_of_age.md)** — March Comes in Like a Lion / Kimi ni Todoke / Eizouken register (Genre Shell #14; pacing key `school`). Social weather as plot; the widest Western-locale carrier (secondary tier in en_US, es_US, es_ES, de_DE, hu_HU, zh_SG). Carries anxiety (test/performance moment) and social anxiety (lunch table, club door) as inner arcs.

### Phase 2X.4 essay-family additions (absorbed 2026-07-24 from PR #295 branch, reworked per Q-MPU-02)

24. **[comedy](comedy.md)** — Gintama / Nichijou / Azumanga Daioh / Daily Lives of High School Boys register (`gag` pacing alias per `canonical_genre_list.yaml`). Boke/tsukkomi comedic engine; episodic-cumulative structure rather than escalating-stakes.
25. **[battle_internal](battle_internal.md)** — Vagabond / Berserk (contemplative arcs) / Vinland Saga (pacifism arc) / One Punch Man (Garou) register (`canonical_genre_list.yaml` id `battle_internal`, label "Internal Battle / Philosophical", `parent_family: battle`). Carries purely psychological/internal conflict externalized through stance-mirroring, weapon-as-burden staging, and line-weight shifts — never literalized into an actual second combatant.
26. **[social_issue](social_issue.md)** — A Silent Voice / Princess Jellyfish / Blue Period register (`canonical_genre_list.yaml` id `social_issue`, label "Social Issue / Josei Realism"). Carries a real, named social pressure (eldercare, single parenthood, housing precarity, disability/exclusion) through a family/community lens via institutional-object inserts; resolves toward redistributed load, never a solved system.
27. **[essay](essay.md)** — Broader reflective/confessional register (Nagata Kabi's diaristic work, Yamada Murasaki's *Talk to My Back*, Taniguchi Jiro's *The Walking Man*). Any subject, not only memoir-of-crisis; gated on `self_or_artifact_interaction` — a recurring recognizable modern artifact (search history, voice memo, receipts) stands in for a second character. `parent_family: null` per `canonical_genre_list.yaml`; sibling to `josei_adult_memoir` but broader in topic and less confessional-intensity by default.
28. **[graphic_medicine](graphic_medicine.md)** — Illness/disability/patient-care register (*Marbles*, *Cancer Vixen*, *Epileptic*, *Stitches*, *El Deafo*). `parent_family: essay` per `canonical_genre_list.yaml`; gated on `patient_care_or_family_pressure` — narrower than `essay`, always specifically medical/embodied, requires a living clinical or family pressure axis rather than solo artifact-review.

### Phase 2X.4 proxy-only genre bibles (absorbed 2026-07-24 from PR #295 branch, reworked per Q-MPU-02)

29. **[procedural](procedural.md)** — Case Closed / Golden Kamuy / Silver Spoon / Dr. Stone register. Investigative/systems-driven manga where a professional process (forensics, agriculture, chemistry, medicine, craft-trade) is the narrative engine. `pacing_proxy: workplace` per `canonical_genre_list.yaml` (no direct pacing entry); reaction-shot frequency and diagram-inset convention adapted up from the workplace baseline for investigative reveals.
30. **[family](family.md)** — Yotsuba&! / Usagi Drop / Sweetness & Lightning register. Multi-generational household drama carried through caregiving labor and domestic-specific texture. `pacing_proxy: social_issue` per `canonical_genre_list.yaml` (no direct pacing entry); silent-panel ratio and black-fill baseline adapted toward a warmer, quieter register than social_issue's issue-driven tension.
31. **[slice_of_life](slice_of_life.md)** — Yotsuba&! / K-On! / Nichijou / Barakamon / Non Non Biyori register. Ensemble everyday-life warmth and social texture at low stakes; the reaction-row and the group-tableau spread are the lane's signature devices. `pacing_proxy: healing` per `canonical_genre_list.yaml` (no direct pacing entry, explicitly adapted up in dialogue density and reaction-shot frequency, down in silent-panel ratio, from the iyashikei/healing baseline since slice_of_life is warmer and more socially populated than iyashikei's atmospheric solo-lead register).
32. **[food](food.md)** — Food Wars! / Oishinbo / What Did You Eat Yesterday? / Sweetness & Lightning / Restaurant to Another World register. Craft/kitchen manga where cooking and eating are the narrative engine; the dish-reveal spread and the tasting-reaction sequence are the lane's signature devices, paired with a dedicated food-specific SFX vocabulary. `pacing_proxy: healing` per `canonical_genre_list.yaml` (no direct pacing entry; keeps healing's sensory-close-up quietness but adds craft/technique-demonstration beats and a much higher reaction-shot frequency around tasting moments).

> **Absorb/reconciliation note (2026-07-24, Lane 05):** rows 24–32 were authored on the PR #295
> branch (`claude/manga-12ep-arc-authoring-egnwqf` @ `4c6e2c3d59`) and land via this lane's PR per
> operator ruling Q-MPU-02 (#295 itself is never merged). #295's tenth bible, `cultivation.md`, was
> **not** absorbed: it duplicates row 20's `cultivation_martial.md` (same taxonomy id `cultivation`),
> which merged first via PR #94, is pinned to the canonical `cultivation_martial` pacing/cookbook/
> drawing-tradition configs, and closes the `VALID_GENRES` gap — canonical singleton wins.

## How to use

- **For 48-volume pre-planning:** read Section 7 of the relevant lane first; each lane gives a concrete 48-volume arc shape.
- **For deterministic panel scripting:** Section 8 lists the 6–9 required panel fields per lane. Scripts should emit these fields per panel; downstream artist/image-gen handoff uses this as the contract.
- **For stylistic tuning:** Section 9's three canonical openings are voice reference. Section 6 lists failure modes to lint against.
- **For quantitative targets** (panels/page, silent-panel ratio, ink density, etc.): Section 2.

## Cross-lane notes

- **Iyashikei vs josei memoir:** both are quiet lanes but have opposite dialogue/narration ratios. Don't confuse them.
- **Shojo romance vs webtoon vertical romance:** core beats overlap but format grammar is entirely different (panel grid vs vertical scroll; B&W+tone vs full color; flower-tone vs color-register).
- **Seinen psychological vs literary graphic novel:** both permit heavy interior work; seinen uses visual symbolic substitution where literary GN uses essayistic caption.
- **Kodomomuke vs iyashikei:** both are low-threat, but kodomomuke resolves per-chapter warmly with named feelings; iyashikei leaves feelings un-named and returns to atmospheric baseline.
- **Psychological horror vs supernatural mystery vs seinen psychological:** psychological horror's entity is *wrong* and dread-bearing; supernatural mystery's spirits are *sad*, not dangerous; seinen psychological needs no entity at all. Psychological horror also keeps its own `top_8_deep` drawing-tradition block — it never collapses into the deferred `horror` genre id.
- **School coming-of-age vs comedy:** ensemble gag beats are seasoning in school stories; when gag rhythm takes over chapter structure, the lane has drifted to `comedy` (gag pacing key).
- **Isekai vs cultivation_martial:** both are transported/ascent fantasies, but isekai's ladder is *belonging* (settlement eras) where cultivation's ladder is *rank* (power tiers); isekai at this catalog's pole is a recovery shell, not a progression engine.

## Canonical 48-volume shapes summary

| Lane | 48-vol shape | Volume unit |
|---|---|---|
| iyashikei | 12 × 4-vol seasonal cycles | seasonal bouquet |
| josei memoir | diaristic serial, 12yr window, retrospectives at vols 8/16/24/32/40/48 | life-quarter |
| seinen psych | 4 × 12-vol psychological eras | one life-stage |
| shojo romance | 6–8 multi-vol relationship arcs | one ladder-rung |
| shonen encouragement | 4 × 12-vol career eras (apprentice → master-as-doubt) | one practice cycle |
| webtoon romance | 48 seasons × ~25 episodes (~1,200 eps) | season |
| webtoon drama | 48 arcs, each 20–30 eps, 4-stage cosmology | arc/floor |
| BL slice-of-life | 4 × 12-vol couple arcs + aging coda | relationship stage |
| literary GN | 48 thematic-artifact single volumes | one artifact/theme |
| kodomomuke | age-progressive 4 × 12-vol bands (5–7, 7–9, 9–11, 10–12) | age-register |
| cultivation_martial | 5-band realm ascent: Foundation (1–8) → Core Formation (9–18) → Nascent Soul (19–30) → Ascension approach (31–42) → the Long Reckoning (43–48) | one realm transition |
| isekai | 4 × 12-vol settlement eras (Arrival → Roots → the Crossing → Homecoming in Place) | one settlement era |
| psychological_horror | 4 × 12-vol dread cycles (the Signal → the House That Remembers → the Naming Without Names → Met, Not Defeated) | one dread cycle |
| school_coming_of_age | 12 terms across 4 school-year bands (Year One → Naming Wants → the Countdown → the Echo Cohort) | one term |
| comedy | episodic-cumulative: formula (1–12) → running-gag accumulation (13–24) → format play (25–36) → legacy payoff (37–48) | one gag/callback cycle |
| battle_internal | 4 × 12-vol convictions (vow formed → tested → near-relapse → held) | one vow lifecycle |
| social_issue | 4 × 12-vol community eras, each keyed to a related social pressure aging with the same household | one pressure-cycle |
| essay | single spine artifact reviewed serially across all 48 vols (discovery → accumulation → intervention → practice) | one artifact/theme |
| graphic_medicine | 4 × 12-vol care bands (onset/admission → relearning/living-with → setback → practice, not finish line) | one recovery/care band |
| procedural | 4 × 12-vol discipline-mastery macro-arcs (apprentice method → independent casework → system pressure → standard-setter) | one method/case-mastery band |
| family | 4 × 12-vol household-configuration macro-arcs (formation → growth friction → wider household → legacy) | one household-configuration band |
| slice_of_life | 12 × 4-vol ensemble terms/seasons (or 8 × 6-vol "chapters of the group's life", or 48 standalone-ish place-and-cast-linked vols) | one ensemble term/season |
| food | 12 × 4-vol "menus" by technique/ingredient theme (or 4 × 12-vol career stages apprentice→head-of-table, or 48 standalone-ish vols linked by one restaurant/tavern vessel) | one menu/technique block |
