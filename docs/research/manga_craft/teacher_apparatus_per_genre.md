# Teacher Apparatus Per Genre (R3)

**Milestone:** M4 · **Owner:** Pearl_Research · **Date:** 2026-07-04  
**Authority chain:** `artifacts/manga/pilots/MANGA_MODE_WRAPPER_DESIGN.md` ·
`config/manga/manga_mode_vessels.yaml` · genre craft bibles under `docs/research/manga_craft/` ·
12 genre bestseller dossiers in `artifacts/research/` (2026-05-13).

## Purpose

R3 requires a researched per-genre **teacher apparatus**: how doctrine enters a genre story
*diegetically* without naming the brand teacher. This doc validates the 15×2 vessel set and
records the M4 upgrades to the three C-grade vessels the vision audit flagged.

**Hard rule:** the teacher is NEVER named in-story. The vessel is a genre-native presence
(character, force, object, ritual). Metadata may carry `teacher_id`; panels must not.

## Apparatus map (teacher-mode)

| Genre | Apparatus (vessel) | How doctrine is earned | Craft bible |
|---|---|---|---|
| iyashikei | tea-house hands / daily ritual | watch hands; body settles before mind agrees | `iyashikei_minimalism.md` |
| dark_fantasy | Keeper / living land | observation, never advice; palm on warm ground | `dark_fantasy.md` |
| mecha | mechanic who co-regulates the pilot | care as doctrine; settle, don't override | `mecha.md` |
| supernatural_mystery | medium who reads the cold | body signal before the ghost | `supernatural_mystery.md` |
| psychological_thriller | detective who reads bodies | body confesses before the mouth | `psychological_thriller.md` |
| romance_josei_drama | beloved who rests | unhurried partner models ease | `shojo_romance.md` / josei |
| workplace_drama | custodian who's seen the cycles | small acts; when to put the pen down | `workplace_drama.md` |
| sci_fi_cyberpunk | wetware elder / old hacker | trust the meat's alarm over the feed | `sci_fi_cyberpunk.md` |
| psychological_horror | survivor who turns toward it | meet the dread; only way out is through | `psychological_horror.md` |
| action_battle | sensei of the settled strike | hardest blow from a quiet body | `action_battle.md` |
| historical_period | **workshop hands that refuse hurry** (M4 upgrade) | material demands the pause; hands stop when forced | `historical_period.md` |
| isekai | guide who trusts old instincts | body's old-world map is truest | `isekai.md` |
| sports_competition | coach of the unclenched | choke is bracing; flow is release | `sports_competition.md` |
| school_coming_of_age | senpai who pays quiet attention | being seen accurately, no speeches | `school_coming_of_age.md` |
| cultivation_martial | master of the lower gate | dantian knows first; force ruptures | (cultivation / mecha-adjacent) |

## Music-mode apparatus (cross-ref R4)

Music vessels are the *feel* contract (opening→mid→closing), not doctrine. Full treatment:
`docs/specs/MUSIC_MODE_MANGA_V1_SPEC.md`. Teacher-mode and music-mode are XOR per series.

## C-grade upgrades (M4)

Vision audit R3: "3 C-grade (apparatus clarity issues)". Upgraded in
`config/manga/manga_mode_vessels.yaml`:

| # | Genre / mode | Problem | Upgrade |
|---|---|---|---|
| 1 | action_battle / music | "war-drum heart" was abstract score, not diegetic | **armor that keeps the pulse** — suit hums with the fighter's heart |
| 2 | historical_period / teacher | "master of the craft" too generic | **workshop hands that refuse hurry** — material-demanded pause |
| 3 | isekai / music | "tune that crosses worlds" read as BGM | **hummed bar that still works here** — only translating magic |

## Validation notes

- A-grade retained: mecha teacher (mechanic co-regulation), dark_fantasy teacher (Keeper/land),
  iyashikei teacher (tea-house hands) — gold exemplars from prior pilots.
- Every teacher vessel uses wound→turn→renewal; music uses opening→mid→closing.
- Operator vision: mecha → enlightened mentor *as mechanic*; romance → love coach *as beloved
  who rests* — never a named brand teacher.

## Consumption

- `phoenix_v4/manga/series/story_architect.py` (`apply_mode_vessel` / `load_vessel`)
- `phoenix_v4/manga/chapter/writer.py` (`_mode_vessel_prompt_block`)
- M3 chapter_scripts cite vessels in `craft_notes`
