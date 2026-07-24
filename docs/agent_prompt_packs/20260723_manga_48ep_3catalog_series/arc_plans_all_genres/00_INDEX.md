# Full-Genre-Taxonomy Coverage Exercise — Index

**Status: PLANNING DELIVERABLE, exploratory, NOT a production reassignment.**
This is a structural 4-arc/48-episode planning exercise spreading all 37
canonical brands (`config/manga/canonical_brand_list.yaml`) across all 25
canonical manga genres (`config/manga/canonical_genre_list.yaml`), per
operator instruction: "use all genres... assign 12 most popular to the rest...
so 12 genres will be covered by 2 brands."

**This is separate from and additional to** `arc_plans/` (the earlier,
narrower deliverable: 36 en_US brands under their *currently-established*
6 genre_ids from `ASSIGNMENT_MATRIX.tsv`, PR #295). That directory reflects
the live production genre assignments. **This directory does not.**

## The assignment logic

37 canonical brands − 25 canonical genres = 12 brands left over after a
1:1 pass, so the 12 most popular genres each get a second brand. Full
reasoning and the complete assignment table (including craft-resource
availability per genre): [GENRE_ASSIGNMENT_TABLE.md](GENRE_ASSIGNMENT_TABLE.md).

**"12 most popular" is grounded in this repo's own market research**,
`artifacts/research/popular_genre_ranking_2026-05-02.md` (Oricon/ICv2/Ken
Research aggregation), "Empirical global ranking (2024-2026)" table,
decomposed from its bundled rows into 12 individual canonical genre ids:
battle, dark_fantasy, fantasy_adventure, romance, healing, mystery, horror,
supernatural_everyday, sports, slice_of_life, mecha, comedy.

**IMPORTANT — this reassigns many brands away from their live production
genre.** These reassignments are exploratory/planning only. They do NOT
change `ASSIGNMENT_MATRIX.tsv`, `config/manga/canonical_brand_list.yaml`,
or any brand's real production genre — that would require a separate,
explicit operator action on those source-of-truth files. Four brands were
deliberately kept at their real established genre because they already have
authored/shipped content or a real existing identity in that genre:
`stillness_press` (healing — 12 real episodes authored, PR merged),
`cognitive_clarity` (mystery — existing partial series), `digital_ground`
(sci_fi_cyberpunk — flagship, existing identity), `focus_sprint_workplace`
(sports — real ja_JP arc-1 authored, PR #196 merged).

## Full 37-brand → genre table

### Popular genres (2 brands each, 24 brands)

| Genre | Brand 1 | Brand 2 | File |
|---|---|---|---|
| battle | stoic_edge_battle | warrior_calm_cultivation | [battle_and_dark_fantasy.md](battle_and_dark_fantasy.md) |
| dark_fantasy | trauma_path_healing | healing_ground_healing | [battle_and_dark_fantasy.md](battle_and_dark_fantasy.md) |
| fantasy_adventure | solar_return_isekai | gentle_growth_healing | [fantasy_adventure_and_supernatural_everyday.md](fantasy_adventure_and_supernatural_everyday.md) |
| supernatural_everyday | spiritual_ground_supernatural | devotion_path_shonen | [fantasy_adventure_and_supernatural_everyday.md](fantasy_adventure_and_supernatural_everyday.md) |
| romance | confidence_core_romance | creative_unfold_social | [romance_and_slice_of_life.md](romance_and_slice_of_life.md) |
| slice_of_life | relational_calm_iyashikei | night_reset_healing | [romance_and_slice_of_life.md](romance_and_slice_of_life.md) |
| healing | stillness_press* | somatic_wisdom_shojo | [healing_and_mystery.md](healing_and_mystery.md) |
| mystery | cognitive_clarity* | adhd_forge_mystery | [healing_and_mystery.md](healing_and_mystery.md) |
| horror | bright_presence_tw_seinen | bio_flow_healing | [horror_and_mecha.md](horror_and_mecha.md) |
| mecha | longevity_lab_healing | hormone_reset_healing | [horror_and_mecha.md](horror_and_mecha.md) |
| sports | focus_sprint_workplace* | morning_momentum_workplace | [sports_and_comedy.md](sports_and_comedy.md) |
| comedy | career_lift_workplace | optimizer_workplace | [sports_and_comedy.md](sports_and_comedy.md) |

\* = kept at real established genre (not a reassignment) — see note above.

### Remaining genres (1 brand each, 13 brands)

| Genre | Brand | File |
|---|---|---|
| sci_fi_cyberpunk | digital_ground* | [scifi_and_cultivation.md](scifi_and_cultivation.md) |
| cultivation | qi_foundation_cultivation | [scifi_and_cultivation.md](scifi_and_cultivation.md) |
| school | calm_student_school | [school_and_memoir.md](school_and_memoir.md) |
| memoir | legacy_builder_memoir | [school_and_memoir.md](school_and_memoir.md) |
| workplace | high_performer_workplace | [workplace_essay_battle_internal.md](workplace_essay_battle_internal.md) |
| essay | executive_calm_workplace | [workplace_essay_battle_internal.md](workplace_essay_battle_internal.md) |
| battle_internal | stabilizer_healing | [workplace_essay_battle_internal.md](workplace_essay_battle_internal.md) |
| procedural | minimal_mind_healing | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |
| graphic_medicine | body_memory_shojo | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |
| family | sleep_restoration_iyashikei | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |
| food | heart_balance_shojo | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |
| social_issue | resilient_parent_social | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |
| historical | relationship_clarity_romance | [procedural_medicine_family_food_social_historical.md](procedural_medicine_family_food_social_historical.md) |

\* = kept at real established genre (not a reassignment).

**Coverage verified programmatically**: all 37 expected brand_ids present
across the 10 files, zero missing, zero extra. Arc-count check: every brand
has exactly 4 arc/block sections except `stillness_press`, which has 3
(arcs 2-4 only — its arc 1, ep_001-012, is already authored and merged; see
`healing_and_mystery.md`).

## Known gap: craft-bible coverage

**10 of the 25 canonical genres have no dedicated craft bible** in
`docs/research/manga_craft/`: slice_of_life, comedy, cultivation, essay,
battle_internal, procedural, graphic_medicine, family, food, social_issue.
Every batch touching one of these flagged it explicitly and built from
`config/manga/canonical_genre_list.yaml` row descriptions +
`config/manga/main_character_interaction_grammar.yaml` quality-gate hints +
general genre craft knowledge instead. **This is a real gap worth closing
(a `docs/research/manga_craft/*.md` bible per missing genre) before any of
these 10 genres' plans move toward actual episode authoring** — the existing
gated production pipeline (`check_manga_story_authored.py`,
`validate_story_excellence.py`) has been battle-tested against genres with
real craft bibles; genres without one are a materially weaker starting
point for a writing agent.

One additional correction surfaced during authoring: the battle+dark_fantasy
batch found that `dark_fantasy_strategies.yaml` DOES exist in
`config/source_of_truth/manga_story_strategies/` (the dispatch pack's
assumption of a gap there was outdated) — used directly.

## What this is not

- Not authored episodes — no chapter scripts, no storyboards, no CI-gated
  content, matching the same planning-only scope as `arc_plans/`.
- Not a live production reassignment — `ASSIGNMENT_MATRIX.tsv` and
  `config/manga/canonical_brand_list.yaml` are unchanged.
- Not a claim that every pairing is equally strong — several (e.g.
  somatic_healing brands under `mecha` or `horror`) are intentional creative
  stretches to exercise full-taxonomy coverage, flagged as such inline by
  each writing agent, and would benefit from an operator read before any
  are taken further.
