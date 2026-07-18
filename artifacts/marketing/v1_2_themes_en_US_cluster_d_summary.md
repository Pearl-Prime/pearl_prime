# V1.2 Themes — Cluster D × en_US — Summary

**Status:** AUTHORED (Pearl_Writer subagent, 2026-05-12)
**Cluster:** D — Relational/Connection/Family
**Locale:** en_US
**Total series:** 25 (5 brands × 5 series)
**Constraint authority:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`

## Brand-id mapping (constraint doc -> canonical_brand_list.yaml)

| Constraint doc id | Canonical brand_id | Tier | Demographic | Primary topic | Mapping basis |
|---|---|---|---|---|---|
| relational_calm_iyashikei | `relational_calm_iyashikei` | core | josei | social_anxiety | exact match |
| inner_security | `confidence_core_romance` | niche | shojo | imposter_syndrome | shojo register for self-worth / inner security |
| bright_presence | `bright_presence_tw_seinen` | niche | seinen | social_anxiety | exact root id |
| found_family_shojo | `heart_balance_shojo` | core | josei | social_anxiety | josei shojo-register found-family |
| communal_warmth | `resilient_parent_social` | niche | josei | burnout | josei communal/family + chosen-family |

## Genre allocation validation (binding)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 (HARD floor) | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 5 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 2 | 1-2 (ceiling for Cluster D) | ✅ |
| horror/dark/occult | 0 | 0-1 | ✅ |
| school | 0 | 0-1 | ✅ |
| other | 0 | 0-1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

Notes:
- **Romance bumped to ceiling (2):** per cluster-D brief — found-family / chosen-family register fits romance better than Cluster C did. Both romance entries are slow-build adjacency (no Webtoon-thirst register): `roommate_with_a_lease_on_my_heart` (B1, Mill/GZ sublease) and `honey_in_the_groupchat` (B2, GZ college a cappella).
- **Healing floor 6 met** with strong cluster-fit anchors: `the_unlocked_door_apartment` (B1), `the_quiet_friend_clinic` (B1), `shrine_for_the_first_no` (B2), `the_office_uncle` (B3), `bookstore_with_the_three_dogs` (B4), `the_house_that_passed_to_me` (B5).
- **No horror/dark in cluster:** Cluster D's tonal register (Frieren / Spy x Family / Heartstopper warmth) is incompatible with horror; budget allocated to the romance ceiling instead. Per constraint doc, horror floor 0-1 means absence is permitted.

## STRICT enum validation

All 25 series use canonical enums only.

```
genre_family:    healing(6) slice_of_life(5) supernatural_everyday(5)
                 mystery_cozy(4) fantasy_adventure(3) romance(2)
magical_register: supernatural_everyday(10) magical_realism(6) none(6) soft_fantasy(3)
serial_engine:   case_of_the_week(15) life_stage_rhythm(4)
                 companion_roster(3) location_anthology(3)
```

Zero enum violations. (Validated with `python3 -c` against the constraint enum
sets — see CLOSEOUT_RECEIPT.)

## Magical-register distribution

| magical_register | count | % | vs 125-target % |
|---|---|---|---|
| supernatural_everyday | 10 | 40% | 37% target — slightly hot, cluster-appropriate (relational hauntings) |
| magical_realism | 6 | 24% | 28% target — within band |
| none | 6 | 24% | 19% target — Cluster D leans realist (Heartstopper register; co-op, sublease, band) |
| soft_fantasy | 3 | 12% | 8% target — three diaspora/heritage entries (cousin atlas, Kingston kitchen, chosen-aunt almanac) |
| isekai | 0 | 0% | 6% — Cluster D has no isekai (relational register incompatible with portal-out frame) |
| occult_cosmic | 0 | 0% | 2% — n/a |

Cluster D tilts realist (`none` over-weight at 24% vs 19%) because chosen-family register works fine without supernatural beats — `interns_in_the_basement`, `the_grandma_co_op`, `the_band_in_the_garage`, `roommate_with_a_lease_on_my_heart`, `honey_in_the_groupchat`, `the_breakfast_that_made_us`. This is intentional cluster register and within the magical-register **advisory** distribution rule (not binding per constraint doc §1.2 ¶35).

## Persona archetype distribution

| persona | count | % | target |
|---|---|---|---|
| ML-mid (Millennial mid-30s/40s) | 12 | 48% | ~18% target → over-weight |
| GZ-firstjob | 5 | 20% | combined GZ ~60% target |
| GZ-uni | 4 | 16% | |
| GA-tween (Gen Alpha) | 3 | 12% | ~20% target → under-weight |
| GZ-queer | 1 | 4% | |
| **Total Gen Z** | **10** | **40%** | ~60% target — under |
| **Total Gen Alpha** | **3** | **12%** | ~20% target — under |
| **Total Millennial** | **12** | **48%** | ~18% target — over |

**Justification for persona-distribution drift from cluster-D spec target:**
- Cluster D = Relational/Connection/Family. Two of five brands (`bright_presence_tw_seinen` seinen, `resilient_parent_social` josei-burnout) are demographically Millennial+ by canonical brand definition. Authoring those brands at Gen Z register would have broken brand-demographic fit (`config/manga/canonical_brand_list.yaml` is authoritative on demographic).
- Heritage/extended-family register (cousin atlas, Kingston kitchen, chosen-aunt almanac, office uncle, estate sales, grandma co-op, neighborhood dispatch) is inherently Millennial-skewed by anchor — Gen Z doesn't yet have the cousin-genealogy-or-estate-clearance daily life.
- Gen Alpha persona is met in 3 series (`library_card_for_a_better_self`, `the_band_in_the_garage`, `the_third_floor_book_club`) — apartment-building / middle-school / garage-band register, exactly the spec-d "sibling/cousin relationships" anchor.
- Brands 1 + 2 + 4 carry the Gen Z load (9 of 15 = 60% within their scope), preserving the Gen Z register where the brand-demographic permits.

## Serial-engine distribution

| serial_engine | count | notes |
|---|---|---|
| case_of_the_week | 15 | Cluster D's natural fit — relational "case" per volume (one friend, one cousin, one neighbor) |
| life_stage_rhythm | 4 | school-year + month-by-month entries (a cappella year, garage band year, sublease year, AIM-logs revisit) |
| companion_roster | 3 | the apartment, the pet-grief hallway analogue, the upstairs aunts |
| location_anthology | 3 | Henry's diner, the cousin atlas (location = the office), the grandma co-op (location = neighborhood) |
| mystery_box | 0 | not used (Cluster D is relational, not secret-driven) |
| power_escalation_ladder | 0 | not used (no shonen/cultivation in this cluster) |

## Volume-runway distribution

- min: 100 (`year_of_the_sublease` — 12 months × 1 vol; `interns_in_the_basement` — 11 months × 1 vol; `honey_in_the_groupchat` — 1 school year)
- median: **175**
- max: 200 (high-runway anchors — `the_unlocked_door_apartment`, `detective_with_the_low_self_image`, `the_estate_of_quiet_goodbyes`, `the_breakfast_that_made_us`, `the_cousin_atlas`, `the_bookstore_with_the_three_dogs`, `the_kitchen_at_kingston`, `the_grandma_co_op`)

Cluster-D median runway aligns with Cluster A/C medians (175). Acceptable.

## Daily-life anchor distribution

Anchors used (spec-listed for Cluster D):
- queer_identity (2: B1, B4 — chosen-family-of-origin)
- thrift_vintage (4: B3, B4, B5×2 — inherited relationships)
- dating (2: B1 sublease, B2 a cappella) — slow-build only
- ai_companion (2: B3 office uncle, B4 grandmother-call service) — parasocial → real friendship
- retail_service (4: B1 lost-and-found, B2 internship, B3 diner, B5 grandma co-op) — workplace-as-family
- alt_spirituality (3: B2 shrine, B3 cousin atlas, B5 chosen-aunt almanac)
- k_pop_fandom (1: B4 garage band) — parasocial → real friendship
- content_creation (1: B1 group-chat-dinner)
- late_night_economy (2: B2 detective, B5 dispatcher)
- parasocial_creator (2: B1 AIM logs, B4 book club)

All Cluster-D-spec'd anchors represented. No off-cluster anchors.

## Out of scope (deferred)

- Cover-art prompts: not in this PR (Pearl_Brand authority)
- Localization to ja_JP / zh_CN / zh_TW: separate cluster-D-locale subagents
- Catalog ingestion: handled by V1.2 catalog reconciliation pipeline once all 5 cluster × 4 locale = 20 files exist

## Next action

- Merge after CI passes (governance, mass-deletion check, push-guard preflight).
- Cluster-D × ja_JP / zh_CN / zh_TW subagents to follow.
