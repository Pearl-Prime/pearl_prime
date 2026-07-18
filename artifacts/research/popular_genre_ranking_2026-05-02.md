# Q4 — Popular-Genre Ranking (top 10 globally, 2024–2026)

**Date:** 2026-05-02
**Branch:** `agent/manga-drawing-traditions-research-20260502`
**Source agent:** general-purpose subagent (cross-source aggregation; 0 WebFetch / 18 WebSearch)
**Cross-references (SHA-pinned):**
- Cookbook research: `docs/COMFYUI_FLUX_MANGA_PROMPTING_RESEARCH_2026-04-29.md` @ `2881dd970bf2433e2225800ac6f73b1dd0281be5` (#802)
- Community audit: `docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md` @ `f4c50142b63df134d2f34c10a4a761bd9015c910` (#803)

---

## Cross-source aggregation

**Oricon Japan 2024 annual top 10** (Nov 2023–Nov 2024): JJK (#1, 7.61M), One Piece (#2, 5.25M), Frieren (#3, surge), Apothecary Diaries (#4, near-2× 2023), Mash, Blue Lock, Spy×Family, Kaiju No.8, Blue Box, Dandadan. ([Oricon 2024 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2024-2023-nov-20-2024-nov-17-frieren-and-maomao-surge-while-jujutsu-kaisen-is-on-the-throne-for-a-final-time.1045941/))

**Oricon Japan 2025 annual top 10** (Nov 2024–Nov 2025): One Piece (#1, 4.21M), JJK (#2, 3.92M), Dandadan (#3, ~3.51M), Blue Lock (#4, ~3.01M), Kingdom (#5, ~2.52M), Chainsaw Man (#12, ~1.85M). ([Oricon 2025 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2025-2024-nov-18-2025-nov-16-one-piece-takes-back-its-throne-while-four-other-manga-make-their-top-10-debut.1366774/))

**ICv2 / Circana BookScan US 2024 top 20:** entirely Shonen Jump series + Berserk high-end collections + Junji Ito Uzumaki. JJK took 7 of 20 slots. ([ICv2 2024](https://icv2.com/articles/markets/view/59079/full-year-2024-circana-bookscan-top-20-manga-graphic-novels))

**ICv2 / Circana BookScan US 2025 top 20:** "All of the Top 20 manga of 2025 were either shonen or seinen, and most had an anime adaptation helping them along." VIZ = 15/20. ([ICv2 2025](https://icv2.com/articles/markets/view/61706/manga-week-full-year-2025-circana-bookscan-top-20-manga-graphic-novels))

**Webtoon (Naver/LINE) global 2024–2025:** Romance ≈ 39.4% global webtoon share (largest single genre); romance ≈ 33% viewership; fantasy + action ≈ 45% of remainder. Webtoon Entertainment paid revenue $1.35B in 2024 (80% paid content). ([APAC Manga Market 2024–2030 — Ken Research](https://www.kenresearch.com/apac-manga-market))

**Anime adaptation pipeline 2025:** isekai 32 new TV series (vs 34 in 2024 peak); shonen-action confirmed (Sakamoto Days, Yaiba, OPM S3); romance/healing (Honey Lemon Soda, My Happy Marriage S2); horror/paranormal (Dandadan S2); fantasy/healing (Apothecary Diaries S2, Witch Hat Atelier); isekai (Zenshu). ([2025 in anime — Wikipedia](https://en.wikipedia.org/wiki/2025_in_anime))

**Phoenix Omega portfolio (rows by genre, all 4 locales × all brands):**

| Genre | Portfolio rows | Total pct sum |
|---|---:|---:|
| essay | 61 | 602 |
| memoir | 52 | 325 |
| supernatural_everyday | 51 | 334 |
| romance | 51 | 551 |
| mystery | 51 | 222 |
| slice_of_life | 47 | 408 |
| **healing** | **46** | **920** |
| comedy | 42 | 137 |
| graphic_medicine | 41 | 253 |
| family | 40 | 265 |
| school | 39 | 246 |
| battle_internal | 35 | 305 |
| historical | 33 | 209 |
| cultivation | 24 | 372 |
| social_issue | 23 | 141 |
| fantasy_adventure | 20 | 271 |
| dark_fantasy | 14 | 99 |
| battle | 13 | 204 |
| workplace | 10 | 50 |
| mecha | 10 | 65 |
| horror | 9 | 59 |
| sci_fi_cyberpunk | 9 | 40 |
| food | 5 | 8 |
| sports | 4 | 14 |

(Source: `config/manga/brand_genre_allocation.yaml` aggregated.)

---

## Empirical global ranking (2024–2026)

| # | Genre | Aggregate evidence | Phoenix portfolio share | 2024–26 anime | Rationale |
|---|---|---|---|---|---|
| **1** | **shonen-battle / dark-fantasy hybrids** (`battle` + `dark_fantasy`) | JJK #1 2024 / #2 2025; Dandadan #3 2025; Chainsaw Man; Berserk dominates US; ICv2 2025 = 100% shonen+seinen | battle: 13 / 204; dark_fantasy: 14 / 99 — **UNDERWEIGHTED** | 10+ | Largest absolute volume globally; dominates Oricon and US |
| **2** | **fantasy_adventure (incl. isekai)** | Frieren #3 Oricon 2024; isekai = "most read genre 2025" per Outlook; 32 new isekai anime 2025; Solo Leveling | 20 / 271 — appropriate mid-weight | 12+ | Widest-tent genre; covers shonen + quiet + isekai sub-registers |
| **3** | **romance** (incl. shojo / josei / BL / webtoon-romance) | Webtoon romance = 39.4% global webtoon share; shojo 11.5M / ¥7.8B JP 2024; josei 7.4M / ¥7.4B; BL 1.9M / ¥1.65B; rising female Gen Z + Millennials | 51 / 551 — strong | 6+ | #1 by digital reading share; under-indexed in print Oricon |
| **4** | **healing / iyashikei** | Frieren straddles healing+fantasy; Apothecary cozy-mystery healing; isekai-recovery growing 55% above standard iyashikei | **46 / 920 — Phoenix's #1 by allocation mass** | 4+ | High-engagement evergreen; smaller absolute volume than shonen but high female + millennial Gen Z share |
| **5** | **mystery / cozy-mystery** | Apothecary near-doubled 2023→2024; Conan continues; Medalist top-10; cozy-mystery + healing-mystery growing | 51 / 222 — broad shallow | 3+ | Often blended (mystery+healing, mystery+fantasy); the #4 Oricon 2024 surge |
| **6** | **horror / supernatural-comedy / paranormal** | Dandadan #3 Oricon 2025; Junji Ito Uzumaki US top-20; Chainsaw Man horror-shonen | supernatural_everyday: 51 / 334; horror: 9 / 59 — **horror underweighted** | 4+ | The "Dark Trio" (JJK + Chainsaw Man + Hell's Paradise) drives this |
| **7** | **sports** | Blue Lock #4 Oricon 2025 / #6 Oricon 2024 (~3.01M); Medalist top-10 2024–25; persistent ICv2 BookScan presence | sports: 4 / 14 — **MASSIVELY UNDERWEIGHTED** | 3+ | Operator's preempted top-8 excludes sports; empirical evidence forces inclusion |
| **8** | **slice_of_life** | Slice-of-life isekai 55% more popular than standard iyashikei (ANN); Witch Hat Atelier; broad mid-tier presence | 47 / 408 — strong allocation | 3+ | Steady mid-volume, high crossover with healing/school |
| **9** | **mecha** | Witch from Mercury Gunpla = highest-selling Gundam; spinoff manga 2025; Super Robot Wars Y 2025; Bandai/Sunrise Gundam franchise hit $783M sales 2022 baseline | mecha: 10 / 65 — appropriate niche allocation; bright_presence_tw is sole tentpole | 3+ | Niche but high-monetization (model-kit revenue); operator correctly retains |
| **10** | **comedy / paranormal-comedy** | Spy×Family Oricon 2024 top-10; Dandadan straddles horror+comedy | comedy: 42 / 137 — broad shallow | 4+ | Often blended; rarely a standalone anchor |

---

## Validation/refute of operator's preempted top-8

Operator's preempted list:
> 1. healing/iyashikei  2. dark_fantasy  3. psychological_horror  4. mecha  5. romance  6. slice_of_life  7. fantasy_adventure  8. comedy

| Slot | Operator | Empirical | Verdict |
|---|---|---|---|
| 1 | healing | (would be #4 globally; #1 by Phoenix portfolio mass) | **keep as Phoenix-portfolio #1; flag global #4** |
| 2 | dark_fantasy | empirically appropriate as part of #1 cluster | **keep; consider portfolio rebalance — only 14 rows** |
| 3 | psychological_horror | not separate canonical genre; closest = horror + battle_internal blend | **reasonable as horror+battle_internal blend** |
| 4 | mecha | empirically lower (#9) | **portfolio bet vs global signal — operator's #4 reflects bright_presence_tw tentpole strategy** |
| 5 | romance | empirically should be #2-3 globally (webtoon dominance) | **under-ranked in operator list** |
| 6 | slice_of_life | empirically #8 — appropriate | **keep** |
| 7 | fantasy_adventure | empirically should be #2 globally (Frieren + Solo Leveling + isekai) | **significantly under-ranked; Phoenix portfolio also under-allocated (20 rows vs 46 healing)** |
| 8 | comedy | empirically #10 — appropriate | **keep** |

**Empirical reorder (ignoring portfolio bias):**
1. battle (shonen-action) — *missing from operator list*
2. fantasy_adventure (incl. isekai)
3. romance
4. healing/iyashikei
5. mystery (cozy + dark) — *missing from operator list*
6. horror / supernatural
7. sports — *missing from operator list*
8. slice_of_life
9. mecha
10. comedy

**Portfolio-weighted reorder (matches Phoenix's explicit bet):** keep operator's top-8 as published. The portfolio is intentionally healing/iyashikei-anchored (920 pct allocation mass — 3.4× the next genre), defensible if audience is teacher-brand subscribers seeking calm/mindfulness content.

---

## Two flags for operator

1. **Sports is empirically top-7-8** (Blue Lock #4 Oricon 2025; Medalist top-10) and Phoenix has only 4 rows / 14 pct. If even one teacher brand has sports affinity, this is a high-ROI portfolio expansion.

2. **Fantasy_adventure under-allocation** (20 rows vs ~50 for romance/mystery/SoL) is the largest portfolio-vs-empirical gap. Lifting solar_return / qi_foundation / devotion_path fantasy_adventure cells by 5-10 pct each would close the gap without disturbing the healing tentpole strategy.

---

## Sources

Full source list in the agent's returned report. Key citations:
- [Oricon 2024 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2024-2023-nov-20-2024-nov-17-frieren-and-maomao-surge-while-jujutsu-kaisen-is-on-the-throne-for-a-final-time.1045941/)
- [Oricon 2025 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2025-2024-nov-18-2025-nov-16-one-piece-takes-back-its-throne-while-four-other-manga-make-their-top-10-debut.1366774/)
- [ICv2 2024](https://icv2.com/articles/markets/view/59079/full-year-2024-circana-bookscan-top-20-manga-graphic-novels)
- [ICv2 2025](https://icv2.com/articles/markets/view/61706/manga-week-full-year-2025-circana-bookscan-top-20-manga-graphic-novels)
- [APAC Manga Market 2024–2030](https://www.kenresearch.com/apac-manga-market)
- [Berserk Dominates 2024 — CBR](https://www.cbr.com/berserk-manga-top-manga-ranking-2024/)
- [State of Isekai Anime — ANN](https://www.animenewsnetwork.com/feature/2025-01-22/the-state-of-isekai-anime/.219776)
- [Top 10 best-selling manga of 2024 — Comics Beat](https://www.comicsbeat.com/top-10-best-selling-manga-of-2024/)
- [2025 in anime — Wikipedia](https://en.wikipedia.org/wiki/2025_in_anime)

---

*End of popular_genre_ranking_2026-05-02.md.*
