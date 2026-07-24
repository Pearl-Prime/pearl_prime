# 37-Brand → 25-Genre Assignment (full canonical taxonomy coverage)

Source of the 25 canonical genres: `config/manga/canonical_genre_list.yaml`.
Source of the "12 most popular" ranking: `artifacts/research/popular_genre_ranking_2026-05-02.md`
("Empirical global ranking (2024-2026)" table, decomposed from its bundled
rows into 12 individual canonical ids: battle+dark_fantasy at rank 1,
fantasy_adventure at 2, romance at 3, healing at 4, mystery at 5,
horror+supernatural_everyday at 6, sports at 7, slice_of_life at 8, mecha at 9,
comedy at 10).

37 canonical brands (`config/manga/canonical_brand_list.yaml`) - 25 canonical
genres = 12 brands left over after a 1:1 pass, so the 12 most popular genres
each get a second brand. 13 genres get exactly 1 brand; 12 genres get exactly
2 brands. 13x1 + 12x2 = 37.

**Continuity constraint respected:** `stillness_press` (healing), `cognitive_clarity`
(mystery), `digital_ground` (sci_fi_cyberpunk), and `focus_sprint_workplace`
(sports) already have established/partially-authored identities in these
exact genres (stillness_press has 12 real authored episodes in this genre) -
kept as-is rather than reassigned, so this exercise extends rather than
contradicts existing shipped content.

## Popular genres (2 brands each, 24 brands)

| Genre | Brand 1 (primary_topic) | Brand 2 (primary_topic) |
|---|---|---|
| battle | stoic_edge_battle (courage) | warrior_calm_cultivation (burnout) |
| dark_fantasy | trauma_path_healing (grief) | healing_ground_healing (grief) |
| fantasy_adventure | solar_return_isekai (self_worth) | gentle_growth_healing (self_worth) |
| romance | confidence_core_romance (imposter_syndrome) | creative_unfold_social (social_anxiety) |
| healing | stillness_press (anxiety) [continuity] | somatic_wisdom_shojo (somatic_healing) |
| mystery | cognitive_clarity (overthinking) [continuity] | adhd_forge_mystery (adhd_focus) |
| horror | bright_presence_tw_seinen (social_anxiety) | bio_flow_healing (somatic_healing -> body horror) |
| supernatural_everyday | spiritual_ground_supernatural (grief) | devotion_path_shonen (grief) |
| sports | focus_sprint_workplace (adhd_focus) [continuity] | morning_momentum_workplace (burnout) |
| slice_of_life | relational_calm_iyashikei (social_anxiety) | night_reset_healing (sleep) |
| mecha | longevity_lab_healing (somatic_healing) | hormone_reset_healing (somatic_healing) |
| comedy | career_lift_workplace (imposter_syndrome) | optimizer_workplace (overthinking) |

## Remaining genres (1 brand each, 13 brands)

| Genre | Brand (primary_topic) |
|---|---|
| sci_fi_cyberpunk | digital_ground (burnout) [continuity] |
| cultivation | qi_foundation_cultivation (somatic_healing) |
| school | calm_student_school (anxiety) |
| memoir | legacy_builder_memoir (self_worth) |
| workplace | high_performer_workplace (burnout) |
| essay | executive_calm_workplace (burnout) |
| battle_internal | stabilizer_healing (burnout) |
| procedural | minimal_mind_healing (overthinking) |
| graphic_medicine | body_memory_shojo (somatic_healing) |
| family | sleep_restoration_iyashikei (sleep) |
| food | heart_balance_shojo (social_anxiety) |
| social_issue | resilient_parent_social (burnout) |
| historical | relationship_clarity_romance (social_anxiety) |

## Craft-resource availability per genre (check before writing; some are thin)

Direct or alias-mapped craft bible exists in `docs/research/manga_craft/`:
battle(action_battle.md), dark_fantasy(dark_fantasy.md), fantasy_adventure(isekai.md),
romance(shojo_romance.md), healing(iyashikei_minimalism.md), mystery(psychological_thriller.md),
horror(psychological_horror.md), supernatural_everyday(supernatural_mystery.md),
sports(sports_competition.md), mecha(mecha.md), sci_fi_cyberpunk(sci_fi_cyberpunk.md),
school(school_coming_of_age.md), memoir(josei_adult_memoir.md, loose reference),
workplace(workplace_drama.md).

**No dedicated craft bible exists** for: slice_of_life, comedy, cultivation,
essay, battle_internal, procedural, graphic_medicine, family, food,
social_issue, historical (historical_period.md exists but is a different
canonical id - "historical" here maps via the `historical_period: historical`
alias, so historical_period.md DOES apply - moving this to the "has a bible"
list). Truly bible-less: slice_of_life, comedy, cultivation, essay,
battle_internal, procedural, graphic_medicine, family, food, social_issue.
For these, work from `config/manga/canonical_genre_list.yaml`'s row
description + `config/manga/main_character_interaction_grammar.yaml`'s
`quality_gate_checks` hint for that genre + general manga/webtoon genre
craft knowledge - flag the missing-bible gap explicitly in your output.
