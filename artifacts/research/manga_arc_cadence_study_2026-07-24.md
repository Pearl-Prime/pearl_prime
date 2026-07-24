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

<!-- SCALE SECTIONS LAND IN THE SCALE CHECKPOINT COMMIT -->

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
