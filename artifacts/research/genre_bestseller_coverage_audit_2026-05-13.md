# Per-Genre Manga Bestseller Research Coverage Audit

**Date:** 2026-05-13
**Author:** Pearl_Research
**Branch:** `agent/pearl-research-genre-bestseller-audit-20260513`
**Mission:** Audit Phoenix's existing manga research corpus against the 21 manga-applicable genres to identify which have Pearl_Research-grade bestseller guidance and which are gaps.

## Genre list (21 manga-applicable)

`supernatural_everyday | romance | mystery_cozy | slice_of_life | healing | comedy | family | school | battle_internal | historical | cultivation | social_issue | fantasy_adventure | dark_fantasy | battle | workplace | mecha | horror | sci_fi_cyberpunk | food | sports`

Source: `config/manga/brand_genre_allocation.yaml` (Phoenix portfolio allocation), filtered to genres that map to manga as a publishable format.

## Coverage axes (per genre)

For each genre we ask four questions:

| Axis | Question |
|---|---|
| A. **Market-share data** | Do we cite an empirical % share of global manga buyer base for this genre? (Oricon / ICv2 / BookScan / Naver / Webtoon Korea) |
| B. **Bestseller corpus** | Do we name top-5 living bestsellers in this genre, with circulation/revenue numbers? |
| C. **Craft research** | Do we have archetype / arc / pacing / visual register research specific to this genre? |
| D. **Therapeutic-embed** | Do we have research on how self-help teachings can land inside this genre without breaking story? |

Legend: COVERED = repo has Pearl_Research-grade artifact; PARTIAL = mentioned but thin (named but no quantitative depth or only one of the four sub-axes); GAP = no artifact, must be filled.

## Coverage matrix

Below is the audit. Each row links to the strongest existing artifact and tags gaps for filling by dossier authoring.

| # | Genre | A. Market share | B. Bestseller corpus | C. Craft research | D. Therapeutic-embed | Strongest existing artifact | Status |
|---|---|---|---|---|---|---|---|
| 1 | supernatural_everyday | PARTIAL | COVERED | COVERED | PARTIAL | `manga_bestseller_magical_serial_framework_2026-05-12.md`, `popular_genre_ranking_2026-05-02.md` (Mushishi / Mob Psycho / Jujutsu Kaisen examples), `manga_genre_writing_styles_2026_04_04.md` | COVERED |
| 2 | romance | PARTIAL | COVERED | COVERED | PARTIAL | `popular_genre_ranking_2026-05-02.md` (Kimi ni Todoke, Horimiya, Lovely Complex), `manga_genre_writing_styles_2026_04_04.md`, `webtoon_master_reference_2026-04-25.md` | COVERED |
| 3 | mystery_cozy | PARTIAL | PARTIAL | PARTIAL | GAP | `popular_genre_ranking_2026-05-02.md` (Detective Conan, Death Note), `MANGA_READER_PROMISES.md` | PARTIAL |
| 4 | slice_of_life | COVERED | COVERED | COVERED | PARTIAL | `popular_genre_ranking_2026-05-02.md`, `manga_bestseller_magical_serial_framework_2026-05-12.md` (Yotsuba!, Yokohama Kaidashi, Aria) | COVERED |
| 5 | healing (iyashi-kei) | COVERED | COVERED | COVERED | COVERED | `manga_bestseller_magical_serial_framework_2026-05-12.md`, `therapeutic_manga_wellness_market_research_2026_04_04.md` | COVERED |
| 6 | comedy | PARTIAL | COVERED | PARTIAL | GAP | `popular_genre_ranking_2026-05-02.md` (Gintama, Saiki K, Spy x Family), `manga_genre_writing_styles_2026_04_04.md` | PARTIAL |
| 7 | family | PARTIAL | PARTIAL | PARTIAL | PARTIAL | `popular_genre_ranking_2026-05-02.md` (Spy x Family, Yotsuba, Sweetness & Lightning), `MANGA_READER_PROMISES.md` | PARTIAL |
| 8 | school | COVERED | COVERED | COVERED | PARTIAL | `manga_genz_genalpha_portal_framework_2026-05-13.md`, `gen_z_student_persona_research.md`, `popular_genre_ranking_2026-05-02.md` | COVERED |
| 9 | battle_internal | PARTIAL | PARTIAL | PARTIAL | PARTIAL | `manga_bestseller_magical_serial_framework_2026-05-12.md` (Vagabond, Berserk inner monologue), `popular_genre_ranking_2026-05-02.md` | PARTIAL |
| 10 | historical | GAP | PARTIAL | PARTIAL | GAP | `popular_genre_ranking_2026-05-02.md` (Vinland Saga, Vagabond, Kingdom mentions) | GAP |
| 11 | cultivation (xianxia/wuxia) | PARTIAL | PARTIAL | GAP | GAP | `popular_genre_ranking_2026-05-02.md` (Solo Leveling cultivation arc note), `webtoon_japan_market_rakuten_ai_2026-04-25.md` | GAP |
| 12 | social_issue | GAP | PARTIAL | GAP | PARTIAL | `popular_genre_ranking_2026-05-02.md` (A Silent Voice, Goodnight Punpun mentions) | GAP |
| 13 | fantasy_adventure | COVERED | COVERED | COVERED | PARTIAL | `popular_genre_ranking_2026-05-02.md` (Hunter x Hunter, Frieren, One Piece, Made in Abyss), `manga_bestseller_magical_serial_framework_2026-05-12.md` | COVERED |
| 14 | dark_fantasy | COVERED | COVERED | COVERED | PARTIAL | `popular_genre_ranking_2026-05-02.md` (Berserk, Chainsaw Man, Attack on Titan), `manga_bestseller_magical_serial_framework_2026-05-12.md` | COVERED |
| 15 | battle (shounen action) | COVERED | COVERED | COVERED | PARTIAL | `popular_genre_ranking_2026-05-02.md` (Naruto, Bleach, Demon Slayer, JJK, MHA), `manga_bestseller_magical_serial_framework_2026-05-12.md` | COVERED |
| 16 | workplace (salaryman/OL) | GAP | PARTIAL | GAP | GAP | brief mention only in `popular_genre_ranking_2026-05-02.md` (Wotakoi, Aggretsuko) | GAP |
| 17 | mecha | GAP | PARTIAL | GAP | GAP | brief mention only — Gundam, NGE listed in `popular_genre_ranking_2026-05-02.md` w/o craft research | GAP |
| 18 | horror | PARTIAL | PARTIAL | PARTIAL | GAP | `popular_genre_ranking_2026-05-02.md` (Junji Ito, Tomie, Uzumaki), `manga_genre_writing_styles_2026_04_04.md` | GAP |
| 19 | sci_fi_cyberpunk | GAP | PARTIAL | GAP | GAP | brief mention only — Akira, GitS, BLAME!, Battle Angel in `popular_genre_ranking_2026-05-02.md` | GAP |
| 20 | food (gourmet) | GAP | PARTIAL | GAP | GAP | brief mention only — Toriko, Food Wars, Oishinbo, Yakitate Japan | GAP |
| 21 | sports | GAP | PARTIAL | GAP | GAP | brief mention only — Slam Dunk, Haikyuu, Blue Lock, Ping Pong | GAP |

## Summary

- **COVERED (full Pearl_Research-grade):** 8 — supernatural_everyday, romance, slice_of_life, healing, school, fantasy_adventure, dark_fantasy, battle
- **PARTIAL:** 5 — mystery_cozy, comedy, family, battle_internal, horror (some named bestsellers but no quantitative share/craft/therapeutic depth)
- **GAP (must author dossier):** 8 — historical, cultivation, social_issue, workplace, mecha, sci_fi_cyberpunk, food, sports

Plus horror moved from PARTIAL into GAP-fill because therapeutic-embed framework is missing and horror is high-leverage for self-help embedding (somatic resourcing, panic, survival).

**Total dossiers to author: 9** (the 8 GAPs + horror).

These dossiers are written under `artifacts/research/genre_bestseller_dossiers/`.
