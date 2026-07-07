# Manga Story Wave 2 — shell-proof flagship scripts (3 strategic shells, first true written output)

Tier-1 authored `ep_001` chapter scripts (`chapter_script_writer_handoff` format) for the three
strategic shells that had research + series plans but **zero genre-native written output**:
`romance_josei_drama` (flagship scale), `historical_period`, `cultivation_martial`. Wave 2's brief
(operator, 2026-07-07): **genre story first, wellness vehicle second** — each script must still
read as strong commercial genre manga if the wellness topic label is removed. No iyashikei
fallback; no therapeutic monologue; shell-native tension engines only.

These are **stories** (Tier-1 prose authoring). Per the six-layer acceptance taxonomy the stories
are *authored artifacts on disk*; rendering remains gated exactly like wave 1; nothing here is
EXECUTED-REAL as panels or PROVEN-AT-BAR.

Honest scope note: `romance_josei_drama` had one wave-1 artifact — `the_weight_she_set_down`
(6-page teacher-mode **wrapper proof**, iyashikei-cadence). Wave 2's romance script is the shell's
first **genre-engine** script (delay / gaze / proximity / confession pressure), and a **new
genre×mode combo** (romance×music vs wave 1's romance×teacher). Historical and cultivation had
nothing written at all.

## The 3 (2 teacher · 1 music — all new genre×mode combos)

| # | Genre | Series (SSOT) | Title / ep_001 | Mode · Vessel | Interior (never on page) |
|---|---|---|---|---|---|
| 1 | romance_josei_drama | `heart_balance_shojo__en_US__romance_josei_drama__series01` | **Worthy of the Window Seat** — "Eight Bars, Unfinished" | MUSIC · the shared song | self_worth |
| 2 | historical_period | `legacy_builder_memoir__en_US__historical_period__series01` | **The Last Letter Home** — "The Character for Return" | TEACHER · the workshop hands that refuse hurry | grief |
| 3 | cultivation_martial | `devotion_path_shonen__en_US__cultivation_martial__series01` | **The Mountain Does Not Move** — "Struck From the Roll" | TEACHER · the master of the lower gate | courage |

## Why these series

- **heart_balance_shojo series01** — heart_balance is the romance shell's TENTPOLE brand
  (`config/manga/brand_genre_allocation.yaml` brand_tentpole: romance; 30–40% romance across
  locale matrices). Its #1 planned romance series is the shell's flagship by definition. Plan
  topic (self_worth) is the shell's native story engine per `docs/GENRE_PORTFOLIO_PLAN.md`
  ("'why would you love me?' as story engine").
- **legacy_builder_memoir series01** — legacy_builder is the only brand whose PRIMARY genre is
  historical (40% per GENRE_PORTFOLIO_PLAN; Phase-5 historical lane brand). Plan topic (grief) is
  the craft bible's stated distinguishing load ("grief across time is the emotional load that
  distinguishes historical from adventure").
- **devotion_path_shonen series01** — the ONLY `cultivation_martial` series in the series-plan
  SSOT (verified across all 5 locales). Not the Sai Ma healing-locked `devotion_path` brand —
  `devotion_path_shonen` is the separate shonen brand (teacher_id `ra` per plan), so the healing
  lock does not apply. Plan topic (courage) maps to the vessel's force-vs-settling doctrine.

## Shell-engine summaries

### 1. Worthy of the Window Seat (romance_josei_drama · music-mode)
- **Reader fantasy:** being seen and chosen by the person whose world outranks yours.
- **Escalation engine:** the shared song passing hand to hand — his ink bars vs her pencil bars in
  a manuscript's margins — under a premiere clock (3 weeks, a co-credit, a kept front-row seat).
- **Protagonist hook:** the shop clerk who can finish the famous pianist's stuck phrase — and does
  it anonymously, in erasable pencil.
- **Signature scene pleasures:** margin-note courtship, the drawer-handle almost-touch, the
  doorway eye-lock in the dark shop, piano-bench proximity, the claimed window seat.
- **Generic failure mode avoided:** no beloved-as-teacher, no rest/soften cadence, no therapeutic
  caption; self_worth carried only by *who plays in the dark vs who hums in the open* and *pencil
  (deniable) vs ink (named)*. Ends on the genre's ALMOST, not a resolution.

### 2. The Last Letter Home (historical_period · teacher-mode)
- **Reader fantasy:** standing inside a real, weighted past — Hōsen, winter of Meiji 38 (1905),
  Russo-Japanese War home front — where the stakes were real and mattered.
- **Escalation engine:** the war's paper machinery closing in on named people — casualty telegraph
  lists under victory lanterns, censor bars, the drawer of returned letters — on the (dramatic-
  irony) Mukden clock.
- **Protagonist hook:** the apprentice scribe who took the job to read the casualty lists first —
  her brother is with the Eighth — and who writes fast so nothing can be true while she writes it.
- **Signature scene pleasures:** ink-grinding craft sequence, the blotted-then-whole character 帰
  (RETURN), dictation-as-duel with a held brush, the field-post clerk's one-beat hesitation, the
  posthumous letter as final-page hook.
- **Generic failure mode avoided:** no modern/therapeutic vocabulary in any era voice; no
  history-as-costume (the widow's knowledge is never resolved into a modern grief conversation);
  era-force established before the personal arc; grief is carried, never cured.

### 3. The Mountain Does Not Move (cultivation_martial · teacher-mode)
- **Reader fantasy:** visible, earned progression on a ladder the world acknowledges — nine gates
  in the body, nine on the mountain, iron rings as rank at a glance.
- **Escalation engine:** breakthrough logic + sect rank politics on a tournament clock — public
  qi-deviation rupture → demotion to the mountain's lowest gate → foundation-reforging → struck
  from the roll → vow ("I'll climb your whole ladder without leaving the first gate").
- **Protagonist hook:** the strongest raw talent in a generation whose own method (forcing) is the
  obstacle — he attacks first so no one sees him flinch.
- **Signature scene pleasures:** channel-map inner-vision insets, qi-glow color grammar (jade vs
  furnace-red), the rival's strolling taunt, the ford demonstration (rooting frees what flooding
  couldn't), the ring-hum progression tick, the vow.
- **Generic failure mode avoided:** stillness is a POWER MECHANIC with ladder consequences, never
  a mood; no serene wellness cadence; the dossier's courtyard-sweeping example is deliberately NOT
  copied (threshold-stance practice instead); rival + verdicts keep shonen-grade tension per page.

## Files

1. `worthy_of_the_window_seat__ep_001.chapter_script.yaml` — MUSIC · romance_josei_drama
2. `the_last_letter_home__ep_001.chapter_script.yaml` — TEACHER · historical_period
3. `the_mountain_does_not_move__ep_001.chapter_script.yaml` — TEACHER · cultivation_martial

## QA

- Valid YAML; `artifact_type: chapter_script_writer_handoff`; 8 pages / 23 panels each
  (deliberately larger than wave 1's 6 pages — these shells need room for genre escalation;
  panel budgets sit inside each shell's `config/manga/manga_pacing_by_genre.yaml` contract).
- Single-mode XOR verified: teacher files carry no song/musician vessel on the page; the music
  file carries no teacher/doctrine line on the page (`teacher_id`/`musician_id` fields consistent).
- No clinical/self-help word in any title, caption, or balloon; interior topics live only in
  metadata (`topic`/`felt_topic`) and wrapper notes.
- No Phoenix-template lines ("the body already knows" family, body/shape/alarm phrasing) on any
  page; each script has a distinct voice (interior-fragment josei captions / distanced
  retrospective seinen narrator / terse ladder-grammar shonen narration).
- Series IDs resolve to real series-plan SSOT files under
  `config/source_of_truth/manga_series_plans/` in all 5 locales; brand/teacher/author fields match
  the plans (`manga_author` from plan; `teacher_id: ra` per devotion_path_shonen plan;
  `teacher_id: brand_teacher_unresolved` M3 convention where the brand has no assignment).
- Each script carries `mode_beats`, `craft_notes` (vessel citation + genre bible/dossier + pacing
  contract + shell traceability + failure-mode note) and `wrapper_note`, per wave-1 + M3 conventions.

## Relationship to wave 1 (not duplicated)

Wave 1 proved the mode wrappers generalize (8 genre×mode combos, ~6pp each). Wave 2 proves the
three unwritten strategic shells can carry **genre-native story engines** at flagship scale. No
wave-1 genre×mode combo is repeated; the romance shell flips mode (teacher→music) and engine
(modeled-ease → delay/gaze/confession-pressure).
