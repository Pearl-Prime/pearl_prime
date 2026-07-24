# Empirical Arc-Cadence Study — Per-Genre Family (2026-07-24)

**Lane:** manga process uplift Lane 03 (Pearl_Research) ·
**Grounds:** `config/manga/manga_pacing_by_genre.yaml` `arc_cadence` blocks (the machine-readable
output of this study) and the §7 "48-volume shape" assertions in `docs/research/manga_craft/*.md`.
**Consumed by:** Lane 06 (100-episode master-plan contract) via `episodes_per_arc_range`,
`arc_pattern`, `first_major_shift_by`.

## Method & verification (read before citing numbers)

- Unit of analysis: the **major arc** as delimited by fan-wiki arc indexes / publisher volume
  breakdowns / platform episode listings, counted in serialized episodes (weekly/monthly chapters
  or webtoon episodes). Min/median/max are corpus observations, not prescriptions.
- Each family draws on ≥3 named series from its existing `reference_corpus[]` (topped up where
  thin). Two evidence tiers, marked per family:
  - **live-verified** — arc boundaries checked against the named source on 2026-07-24
    (battle corpus, Vinland Saga arc boundaries, webtoon platform season sizes, JJK/MHA arc spans).
  - **corpus-derived** — chapter/volume counts from well-documented reference works, cited to the
    named wiki/Wikipedia index; not re-fetched this session. Confidence is capped at `medium` for
    these; families whose English-language arc indexing is genuinely thin are marked `low`.
- Honest-gap rule: where evidence is thin (single-book Western forms, manhua arc boundaries), the
  YAML block still lands with `arc_cadence_confidence: low` and a named follow-up in the Lane 03
  handoff. No number below is invented; imprecise bands are stated as bands.
- `first_major_shift_by` = episode/chapter number by which the corpus's first irreversible
  status-quo shift has landed (upper bound of observed band). `null` = the family has **no
  status-quo-shift convention** (healing, horror anthology, case-grammar supernatural, gag,
  essay) — Lane 06 must branch on null rather than default it.

## Roll-up table (matches YAML `arc_cadence` blocks)

| Family | Arc range (eps) | Median | Pattern | Season unit | 1st shift by | Confidence |
|---|---|---|---|---|---|---|
| battle | 6–60 | 26 | escalating | 9/vol | 100 | high (live-verified) |
| romance | 4–20 | 9 | fixed | 4/vol | 50 | medium |
| workplace | 1–15 | 8 | fixed | 5/vol | 30 | medium |
| healing | 1–5 | 2 | seasonal_cycle | 8/vol | null | high |
| mystery | 8–40 | 18 | escalating | 9/vol | 55 | medium |
| horror | 1–3 | 1 | fixed | 10/vol | null | high |
| sports | 5–45 | 18 | escalating | 9/vol | 40 | high |
| essay | 1–12 | 1 | fixed | 8/vol | null | low |
| memoir | 6–15 | 10 | fixed | 8/vol | 5 | low |
| social_issue | 6–25 | 14 | escalating | mixed | 10 | medium |
| supernatural_everyday | 1–5 | 2 | fixed | 5/vol | null | high |
| school | 3–10 | 5 | seasonal_cycle | 4/vol | 50 | medium |
| fantasy | 5–25 | 12 | escalating | mixed | 16 | medium |
| battle_internal | 25–80 | 45 | escalating | 9/vol | 30 | medium |
| graphic_medicine | 8–21 | 12 | fixed | single-book | 3 | low |
| gag | 1–25 | 1 | fixed | 9/vol | null | medium |
| dark_fantasy | 10–90 | 45 | escalating | 9/vol | 55 | high (live-verified) |
| mecha | 2–15 | 8 | escalating | 6/vol | 30 | medium |
| sci_fi_cyberpunk | 3–25 | 9 | escalating | mixed | 30 | medium |
| historical_period | 5–80 | 30 | escalating | 8/vol | 55 | medium |
| cultivation_martial | 15–50 | 30 | escalating | none stable | 30 | low |
| *(webtoon lanes — no YAML family row; see §Webtoon and handoff follow-up)* | 15–30 | ~22 | seasonal_cycle | 78–115/season | 40 | high (live-verified) |

---

## battle — Battle shonen (confidence: high, live-verified)

**Corpus:** One Piece, Demon Slayer, Jujutsu Kaisen, My Hero Academia (family `reference_corpus`).

**1. Arc length distribution.** Verified arc spans: Demon Slayer — Mugen Train ch 54–66 (13),
Entertainment District 67–97 (31), Swordsmith Village 98–127 (30), Hashira Training 128–139 (12),
Infinity Castle 140–183 (44), series total 205 ch. JJK — Shibuya Incident ch 79–136 (58). MHA —
23 arcs over 430 ch (mean ~19); Paranormal Liberation War ch 253–306 (54). One Piece — early East
Blue arcs 5–19 ch; Alabasta saga ch 102–218; Dressrosa ch 700–801 (102); Wano ~148.
**Planning range [6, 60], median ~26**; late-run mega-arcs (100+) are outliers a 100-episode plan
never reaches. Volume alignment: arc ends align only *partially* with tankobon edges (~9 ch/vol,
WSJ); saga ends align better than arc ends.

**2. Cadence pattern: escalating.** Arc lengths grow monotonically with run maturity in all four
series (KnY 9→44; MHA ~10→54; OP <20→100+). Mid-arc mini-climaxes every 5–10 ch (named-fight
resolution); cliffhangers sit at arc position ~85–95% (the reveal before the finish) and at
nearly every chapter end in tournament/war stretches.

**3. Serialization unit.** Print volume, ~9 chapters (WSJ). Arc ≈ 1.5–5 volumes mid-run.

**4. First-100-episodes shape.** 5–8 complete arcs. First major status-quo shift lands ch 66–101
across the corpus: KnY ch 66 (Rengoku's death closes Mugen Train), JJK ch 79 (Shibuya opens),
MHA ch 92–94 (Kamino / All Might's retirement), OP ch 100–101 (Grand Line entry).
**`first_major_shift_by: 100`.** A 100-ep battle plan should spend arcs 1–2 establishing
(6–15 ch each), arcs 3–5 escalating (15–30 ch), and land the irreversible shift in the final
quarter — not at ep 100 itself (3 of 4 corpus series land it by ep ~80).

**Bible cross-check:** `action_battle.md` §7 (4 × 12-vol arc *families*) is a grouping above the
individual-arc grain measured here; not contradicted. `manga_craft/index.md` summary row consistent.

## romance — Shojo romance (confidence: medium, corpus-derived)

**Corpus:** Fruits Basket (136 ch / 23 vols), Kimi ni Todoke (123 ch / 30 vols), Ao Haru Ride
(49 ch / 13 vols), Strobe Edge (41 ch / 10 vols).

**1. Arc length distribution.** Ladder-rung arcs (a school event, a rival's push, a confession
attempt and its fallout) run 4–20 monthly chapters, median ~9. Volume alignment is **strong and
designed**: monthly shojo tankobon carry ~4 chapters and arcs are written to close at volume
boundaries (the tankobon is the retail unit of emotional resolution).

**2. Cadence pattern: fixed.** Arc *size* stays roughly constant while *stakes* escalate up the
relationship ladder — the inverse of battle's escalating-length pattern. Mini-climaxes are
chapter-end near-miss beats (almost-confession, misread signal) roughly every chapter; the true
climax of a rung sits in its final chapter, followed by a 1-chapter breather.

**3. Serialization unit.** Print volume, ~4 monthly chapters. Arc ≈ 1–4 volumes.

**4. First-100-episodes shape.** 8–12 rungs. Relationship-status shift (couple established):
Kimi ni Todoke ch 48–49 (vol 11); mid-length titles resolve by ch ~25 (Ao Haru Ride, Strobe Edge
place it past midpoint of shorter runs). **`first_major_shift_by: 50`** — a 100-ep romance that
has not converted its central relationship by ep 50 is off-corpus; post-couple chapters pivot to
new-rung stakes (family, rival return, future paths), consistent with `shojo_romance.md` §7's
phase model.

## workplace — Josei workplace (confidence: medium, corpus-derived)

**Corpus:** What Did You Eat Yesterday? (episodic, 170+ ch / 20+ vols), Princess Jellyfish
(~80 ch / 17 vols), Honey and Clover (64 ch / 10 vols).

**1. Arc length distribution.** Bimodal: episodic baseline units of 1 chapter (a meal, a client,
a deadline) and serial threads of 8–15 chapters (Princess Jellyfish's redevelopment fight, Honey
and Clover's life-stage turns). Range [1, 15], median ~8 for titles that arc at all. Volume
alignment weak — episodic units don't need it.

**2. Cadence pattern: fixed** (episodic-with-serial-thread). Serial threads surface roughly every
volume-and-a-half and resolve without resetting the ensemble. Cliffs are rare; chapter ends land
on a restrained-recognition beat instead.

**3. Serialization unit.** Print volume, ~5 monthly chapters (Kiss / Feel Young convention).

**4. First-100-episodes shape.** Purely episodic titles (WDYEY) defer any status-quo shift far
past ep 100 — the loop is the product. Serial-forward titles land a first professional/domestic
shift (job change, workshop threat, cohabitation) by ch ~20–30. **`first_major_shift_by: 30`**
with the episodic-mode caveat carried in the YAML notes.

## healing — Iyashikei (confidence: high, corpus-consistent)

**Corpus:** Yotsuba&! (100+ ch), Laid-Back Camp, Barakamon (18 vols), Non Non Biyori,
Flying Witch (family `reference_corpus`, all five).

**1. Arc length distribution.** Units are vignettes (1–2 ch) and trips/festivals (2–5 ch,
Laid-Back Camp's multi-chapter camping trips are the long end). Range [1, 5], median 2. Volume
alignment: volumes are curated *bouquets* (~8 chapters) — the volume is an anthology boundary,
not an arc boundary.

**2. Cadence pattern: seasonal_cycle.** The year is the macro-structure: chapters ride the
season calendar (first snow, summer festival, harvest) and reset annually. Mini-climaxes are
small recognitions; there are no cliffs — chapter ends return to atmospheric baseline
(`iyashikei_minimalism.md` §7's seasonal-cycle claim is **confirmed** by the corpus).

**3. Serialization unit.** Print volume, ~8 short monthly chapters.

**4. First-100-episodes shape.** ~3–4 season wheels, 30–60 vignette units, **no status-quo
shift** (`first_major_shift_by: null`). Change is demographic drift (a character ages, a skill
slowly improves — Barakamon's calligraphy competitions are the ceiling of "plot"). Lane 06 must
branch on null here: a 100-ep healing plan is a calendar, not an arc sequence.

## Webtoon lanes — vertical romance / vertical drama (confidence: high, live-verified; NO YAML family row)

**Corpus:** Lore Olympus (romance), True Beauty (romance), Tower of God (drama), Solo Leveling
(drama/action).

**1–2. Season sizes (live-verified 2026-07-24).** Platform seasons are **78–115+ episodes**, not
~25: Tower of God S1 = 78 eps (S2 opens at platform episode_no 81 after two ep-0s); Lore Olympus
S1 finale = ep 115; Solo Leveling S1 break ≈ ch 110 of 179 total (+20-ch epilogue). Seasons are
hiatus/production boundaries, not story-arc boundaries.

**3. Arc grain inside seasons.** Story arcs (a floor/test in ToG, a dungeon/raid tier in Solo
Leveling, a relationship crisis cycle in Lore Olympus) run **~15–30 episodes** — the
`webtoon_vertical_drama.md` §7 claim of 20–30-ep arcs holds at arc grain. Weekly episodes ≈
50–70 vertical panels; cliff-per-episode is near-mandatory (platform ranking pressure), with a
season-scale cliff at the finale.

**4. First-100-episodes shape.** First 100 eps ≈ 4–6 arcs ≈ one platform season + opening of the
second. First major status-quo shift by ep ~40 (Solo Leveling's double-dungeon/reawakening lands
by ep ~10; ToG's first-floor commitments by ep ~25; Lore Olympus' inciting scandal inside S1's
first third).

**Consequences (recorded as corrections + follow-up):** `webtoon_vertical_romance.md` §7's
"season of ~25 episodes" mapping is **contradicted** (dated correction line added);
`webtoon_vertical_drama.md` §7's "season/arc of ~20–30 episodes" conflates arc (confirmed
20–30) with season (contradicted: 78+) — dated correction line added. There is **no webtoon
family row in `manga_pacing_by_genre.yaml`** to carry an `arc_cadence` block; named follow-up in
the Lane 03 handoff so Lane 06 doesn't silently inherit print cadence for webtoon-format series.

## mystery — Seinen psychological / mystery (confidence: medium, corpus-derived)

**Corpus:** Monster (162 ch / 18 vols), 20th Century Boys (249 ch / 22 vols), Pluto (65 ch / 8 vols).

Investigation-block arcs (a location, an era-jump, a suspect) of 8–25 ch early, widening to 30–40
as conspiracies compound; Pluto's act-per-robot grid (~8 ch/act) is the compact model. Pattern:
**escalating**. ~9 ch/vol biweekly seinen; arc↔volume alignment moderate (acts often close on
volume ends). First irreversible reframe by ch ~15–55 (Tenma becomes fugitive early; 20thCB's
Bloody New Year's Eve climax ~vol 5). First 100 eps ≈ 4–6 investigation blocks with one mid-run
reframe. `first_major_shift_by: 55`.

## horror — Horror / dread (confidence: high, corpus-consistent)

**Corpus:** Uzumaki (19 ch), Tomie (~20 stories), Junji Ito short-form collections.

Anthology grammar: 1-ch standalones sharing a town/motif; range [1, 3], median 1. Pattern:
**fixed**, with the genre's signature **terminal convergence** (Uzumaki's final 3 chapters fuse
the standalone dread into apocalypse). No first-shift convention (`null`) — dread accumulates
without status-quo change until the convergence. A 100-ep horror plan ≈ 85–92 standalones with
motif escalation clusters every ~10 eps + a 8–15-ep convergence finale. ~10 stories/volume.

## sports — Sports ascent (confidence: high, corpus-derived)

**Corpus:** Slam Dunk (276 ch), Haikyu!! (402 ch), Blue Lock, Kuroko's Basketball (275 ch).

Unit = match, container = tournament. Match length scales with stakes — practice matches 5–10 ch,
mid-tournament 10–25, climax matches 30–45 (Slam Dunk's Sannoh match spans ~6 volumes; Haikyu!!'s
Shiratorizawa ~30 ch). Range [5, 45], median 18, pattern **escalating**. WSJ ~9 ch/vol; big
matches deliberately straddle volume ends (buy-the-next-volume engineering). First tournament
entry = first status-quo shift, by ch ~30–45 → `first_major_shift_by: 40`. First 100 eps ≈ 1
full tournament cycle + entry of the second, 5–7 matches.

## essay — Essay / diary (confidence: LOW — no long-serial evidence)

**Corpus:** My Lesbian Experience with Loneliness, My Solo Exchange Diary (+ sequel volumes).

Unit = one essay/diary entry (1 ch); a volume is a curated thematic arc of 8–12 entries. Pattern:
**fixed**; shifts are retrospective (narrated as already-having-happened), so `first_major_shift_by:
null`. The corpus is 1–2-volume works — **there is no 100-episode essay-manga long-runner to
observe**; Lane 06 must treat 100-ep essay plans as inference (stacked thematic volumes with
recurrence motifs), flagged in the handoff. Confidence: low.

## memoir — Memoir / life reflection (confidence: LOW — thin long-serial evidence)

**Corpus:** Nagata Kabi's memoir sequence, The Summit of the Gods (5 vols).

Life-phase / expedition arcs of 6–15 ch, median 10, pattern **fixed**. The premise-defining
rupture sits in the opening chapters (`first_major_shift_by: 5`) and the remainder excavates it —
memoir front-loads what battle back-loads. Craft-bible retrospective rhythm (vols 8/16/24…) is
consistent with the corpus shape but unproven at 100-ep scale. Confidence: low.

## social_issue — Josei realism (confidence: medium, corpus-derived)

**Corpus:** A Silent Voice (62 ch / 7 vols), Blue Period, Princess Jellyfish (overlap).

Inciting rupture is **front-loaded**: A Silent Voice's elementary prologue ends at ch 6
(time-skip = status-quo shift); Blue Period commits to the art path by ch ~5. Then life-stage
arcs of 6–25 ch (median 14) escalate toward institutional tests (exam, film screening, hospital).
Pattern: **escalating**. `first_major_shift_by: 10` — the inverse of battle; Lane 06 should open
social-issue plans with the rupture, not build to it. Season unit mixed (weekly ~9/vol vs monthly
~4/vol) → `season_unit: null` + note.

## supernatural_everyday — (confidence: high, corpus-consistent)

**Corpus:** Mushishi (~50 cases), Natsume's Book of Friends (29+ vols), xxxHolic (213 ch).

Case-of-the-chapter grammar: 1–4 ch per case (Mushishi strictly 1; Natsume 1–4; xxxHolic 1–5),
median 2, pattern **fixed**. Serial threads (Reiko's past, exorcist clans) resurface every ~8–12
cases and deepen relationships **without status-quo change** → `first_major_shift_by: null`.
First 100 eps ≈ 50–70 cases with 3–4 thread-surfacing clusters. ~5 case-chapters/vol monthly.

## school — School / youth (confidence: medium, corpus-derived)

**Corpus:** Kimi ni Todoke, Ao Haru Ride, My Love Story!! (26 monthly ch).

Arcs are school-calendar events (entrance, culture festival, exams, summer trip, graduation) of
3–8 ch riding the annual cycle — the calendar sets cadence, hence **seasonal_cycle** despite
romance-adjacent stakes. Median 5. Monthly shojo ~4 ch/vol with designed volume alignment.
Relationship-status shift by ch ~50 (KnT ch 48–49) unless the couple forms in act one (My Love
Story!! ch 3 — the post-couple variant). `first_major_shift_by: 50`.

## fantasy — Fantasy / isekai adventure (confidence: medium, corpus-derived)

**Corpus:** Fullmetal Alchemist (108 monthly ch / 27 vols), Made in Abyss, Witch Hat Atelier.

Journey-segment arcs (a layer, a city, a trial) of 5–25 **monthly** chapters, median 12, pattern
**escalating**. Monthly mega-chapters (40–60 pages) mean episode counts run lower than weekly
genres at equal story mass — Lane 06 must not compare fantasy arc counts to weekly-genre arc
counts 1:1. First irreversible loss/reveal early-to-mid: FMA Hughes' death ch 15–16; Made in
Abyss's descent commitment ch ~9. `first_major_shift_by: 16`. Season unit mixed (4–8 ch/vol) →
null + note.

## battle_internal — Internal battle / philosophical (confidence: medium, corpus-derived)

**Corpus:** Vagabond (327 ch / 37 vols), Berserk (contemplative arcs).

Long-breath opponent/era arcs of 25–80 ch (Vagabond's Yoshioka block ~60–80 ch; Kojiro flashback
~55 ch; Berserk's Golden Age ~85 eps), median 45, pattern **escalating**. Extended non-combat
stretches (Vagabond's farming arc ~30 ch) are canonical to the family, not filler — a 100-ep plan
holds only ~2 major arcs plus an establishing arc. First reframe of the vow (renaming, first true
defeat) by ch ~30. Weekly seinen ~9 ch/vol.

## graphic_medicine — (confidence: LOW — single-book form)

**Corpus:** Stitches, El Deafo (~21 ch units), Mom's Cancer.

Complete-in-one-book memoirs of 8–21 chapter units; diagnosis/premise rupture by ch ~3; the book
IS the arc. Pattern: **fixed**; `season_unit: null` (no serialized volume convention exists).
**No 100-episode graphic-medicine long-runner exists** — for serial planning, treat as stacked
10–15-ch case/treatment arcs (explicit inference, flagged in handoff). Confidence: low.

## gag — Gag / comedy (confidence: medium, corpus-derived)

**Corpus:** Gintama (704 ch), Azumanga Daioh, Daily Lives of High School Boys.

Status quo is sacred. Baseline = 1-ch (or 1-page 4-koma) episodic units, median 1; long-runners
spike a 5–25-ch "serious arc" every ~50–100 ch (Gintama's Benizakura ch 89–97; Shogun Assassination
~23 ch) then **reset to baseline**. Pattern: **fixed** with periodic spikes — the spike is not a
status-quo shift (`first_major_shift_by: null`). School-cycle gag (Azumanga) rides the 3-year
calendar with graduation as the only shift, at the very end. First 100 eps ≈ 90+ episodic units +
one serious-arc spike around ep ~85–100.

## dark_fantasy — (confidence: high, live-verified anchor)

**Corpus:** Berserk, Vinland Saga (live-verified arcs: 1–54 / 55–99 / 100–166 / 167+), Frieren.

Short establishing arc (9–15 eps: Berserk's Black Swordsman ~9) then saga-blocks of 45–90 eps
(Vinland War arc 54, Slave arc 45, Eastern Expedition 67; Berserk Golden Age ~85). Median 45,
pattern **escalating**. The genre's signature is the **first status-quo destruction** — Vinland
ch 54 (Askeladd's death + timeskip), Berserk's Eclipse closing the Golden Age —
`first_major_shift_by: 55`. Frieren runs the quiet variant (10–25-ep arcs, First-Class Exam
ch ~36–60). A 100-ep plan = establishing arc + one full saga-block + the destruction beat +
opening of the second block. ~9 eps/vol.

## mecha — (confidence: medium, corpus-derived)

**Corpus:** Neon Genesis Evangelion manga (96 ch / 14 vols), Knights of Sidonia (78 ch / 15 vols),
Gundam: The Origin.

Sortie-of-the-arc units: 2–6 ch per enemy encounter early, fusing into continuous operations as
the command-layer conspiracy surfaces; act-structured titles (Origin) run ~8 ch/act. Range [2, 15],
median 8, pattern **escalating**. Pilot-roster changes / conspiracy reveals land ch ~20–35 (Eva:
Asuka's arrival ~ch 20; Sidonia timeskip ~ch 30) → `first_major_shift_by: 30`. ~5–7 ch/vol monthly.

## sci_fi_cyberpunk — (confidence: medium, corpus-derived)

**Corpus:** Battle Angel Alita (56 ch / 9 vols), BLAME! (65 ch / 10 vols), Akira (120 ch / 6 vols),
Ghost in the Shell (12 ch).

Role/zone arcs (a job, a stratum, a case): Alita's Motorball ~10 ch; BLAME!'s zone-per-arc ~6;
case-grammar GitS = 12 episodic ch with 3-ch convergence. Range [3, 25], median 9, pattern
**escalating**. First systemic rupture ranges ch 9–60 (Alita enters Motorball ch ~13; Akira's
awakening mid-series) → plan `first_major_shift_by: 30`. Volume sizes vary wildly (6–20 ch/vol)
→ `season_unit: null` + note.

## historical_period — (confidence: medium, live-verified anchor)

**Corpus:** Vinland Saga (verified), Vagabond, A Bride's Story, Cesare.

Two sub-modes share the family: **saga-blocks** of 45–80 ch driven by war/politics (Vinland,
Vagabond) and **portrait-cycles** of 5–15 ch rotating POV households (A Bride's Story's
bride-per-arc). Range [5, 80], median 30, pattern **escalating** (saga mode). Era-defining shift
(a death, an exile, a POV handoff) by ch ~20–55 → `first_major_shift_by: 55`. Flagship planning
should use saga-block mode; portrait-cycle is the low-arousal variant. ~8 ch/vol.

## cultivation_martial — (confidence: LOW — arc boundaries poorly indexed)

**Corpus:** Battle Through the Heavens, Soul Land, Tales of Demons and Gods (manhua).

Power-ladder loop (train → breakthrough → rival → new tier) every 15–50 ch, median ~30; leaving
the home sect/village by ch ~20–30 → `first_major_shift_by: 30`. Pattern: **escalating** (each
realm tier raises scale). Release is continuous webtoon-style (often multiple ch/week) with **no
stable volume/season convention** → `season_unit: null`. English-language arc indexing for manhua
is genuinely thin: ranges derive from realm/sect-stage groupings in aggregate listings, not
per-arc verified counts. Confidence: low; named follow-up in handoff (verify against zh-language
chapter indexes when the zh lanes are active).

---

## Cross-family findings (for Lane 06's segmentation logic)

1. **Three cadence regimes, not one:** escalating-arc genres (battle, sports, mystery, fantasy,
   dark_fantasy, mecha, sci-fi, historical, cultivation, battle_internal, social_issue),
   fixed-unit genres (romance ladder, workplace/supernatural/horror/gag/essay episodic), and
   calendar genres (healing, school — the year is the structure). A 100-episode contract needs a
   different segmentation function per regime.
2. **`first_major_shift_by` is trimodal:** front-loaded (social_issue 10, memoir 5,
   graphic_medicine 3), mid-run (fantasy 16, workplace/mecha/sci-fi/cultivation ~30, sports 40,
   romance/school 50, mystery/dark_fantasy/historical 55), and late (battle 100) — plus **null**
   families where forcing a shift breaks the genre contract (healing, horror, supernatural,
   gag, essay). Lane 06 must branch on null.
3. **Volume alignment is strongest where volumes are the retail emotion-unit** (monthly shojo —
   designed alignment; anthology volumes as bouquets) and weakest in weekly action (arcs straddle
   volume ends deliberately at climax matches/fights).
4. **Webtoon seasons are production units, not story units** (78–115+ eps verified); story arcs
   inside them run 15–30 eps. Any webtoon-format series planned off print-family cadence rows
   needs the season grain corrected first (no YAML family row exists yet — see handoff).

## Sources footer

Access date for all URLs: 2026-07-24. Live-verified this session:

- Story Arcs — One Piece Wiki — https://onepiece.fandom.com/wiki/Story_Arcs
- Demon Slayer: All Manga Arcs in Order & Chapters — ComingSoon — https://www.comingsoon.net/guides/news/1786665-demon-slayer-all-manga-arcs-in-order-chapters-list
- Shibuya Incident Arc — Jujutsu Kaisen Wiki — https://jujutsu-kaisen.fandom.com/wiki/Category:Shibuya_Incident_Arc_Chapters
- Paranormal Liberation War Arc — My Hero Academia Wiki — https://myheroacademia.fandom.com/wiki/Paranormal_Liberation_War_Arc
- List of My Hero Academia chapters — Wikipedia — https://en.wikipedia.org/wiki/List_of_My_Hero_Academia_chapters
- Story Arcs — Vinland Saga Wiki — https://vinlandsaga.fandom.com/wiki/Story_Arcs
- Tower of God — WEBTOON episode list (S2 Ep.1 = episode_no 81) — https://www.webtoons.com/en/fantasy/tower-of-god/list?title_no=95
- Lore Olympus S1 finale = episode 115 — Lore Olympus Wiki — https://lore-olympus.fandom.com/wiki/The_Bringer_of_Death_(Season_1_Finale)
- Solo Leveling webtoon 179 ch + S1 break ~ch 110 — Solo Leveling Wiki / CBR — https://www.cbr.com/solo-leveling-complete-guide-manga-vs-anime/

Corpus-derived citations are inlined per family section and mirrored in each family's
`arc_cadence_sources[]` in the YAML.
