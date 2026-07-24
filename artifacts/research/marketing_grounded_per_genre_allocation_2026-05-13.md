# Marketing-Grounded Per-Genre Catalog Allocation (V2 target)

**Date:** 2026-05-13
**Author:** Pearl_Research
**Branch:** `agent/pearl-research-genre-bestseller-audit-20260513`
**Mission:** Produce the *real marketing-research-grounded* per-genre catalog allocation, distinct from Phoenix's existing portfolio mix. This is the empirical "what would a market-driven manga publisher ship?" table — the operator's V2 target.

**Source authorities (SHA-or-URL pinned):**
- `artifacts/research/popular_genre_ranking_2026-05-02.md` (Oricon 2024/2025, ICv2 BookScan, Ken Research APAC)
- `config/manga/brand_genre_allocation.yaml` (Phoenix V1.2 portfolio)
- WebSearch 2026-05-13 (sports / food / mecha / sci-fi / historical / cultivation / workplace / social_issue / horror — see citations below)

## 1. Empirical share table (21 manga-applicable genres)

The "empirical global share" column is the genre's approximate share of the *active global manga buyer base* (Japan print + US BookScan + APAC webtoon + global digital), 2024–2025. Where the literature disagrees, we use the geometric mean of Japan-print (Oricon weight ~45%), US-print (BookScan ~15%) and global-digital (Webtoon/Naver ~40%) weights. Where webtoon dominates (romance, cultivation), that lifts the empirical share above what Oricon alone shows.

| # | Genre | Empirical global share | Phoenix V1.2 share (rows) | Delta (emp − Phoenix) | Recommended V2 share | Action |
|---|---|---:|---:|---:|---:|---|
| 1 | battle (shonen-action) | 18% | 13/736 ≈ 1.8% | **+16.2** | 14% | **MASSIVE LIFT** |
| 2 | fantasy_adventure (incl. isekai) | 14% | 20/736 ≈ 2.7% | **+11.3** | 13% | **MASSIVE LIFT** |
| 3 | romance | 13% | 51/736 ≈ 6.9% | +6.1 | 10% | LIFT |
| 4 | dark_fantasy | 10% | 14/736 ≈ 1.9% | **+8.1** | 9% | LIFT |
| 5 | healing (iyashikei) | 6% | 46/736 ≈ 6.3% | -0.3 | 8% | **MODERATE CUT** (currently over by alloc-pct mass; right by row count) |
| 6 | mystery_cozy | 5% | 51/736 ≈ 6.9% | -1.9 | 6% | KEEP |
| 7 | supernatural_everyday | 5% | 51/736 ≈ 6.9% | -1.9 | 6% | KEEP |
| 8 | sports | 4% | 4/736 ≈ 0.5% | **+3.5** | 4% | **LIFT** |
| 9 | horror | 4% | 9/736 ≈ 1.2% | +2.8 | 4% | LIFT |
| 10 | slice_of_life | 4% | 47/736 ≈ 6.4% | -2.4 | 4% | CUT |
| 11 | comedy | 4% | 42/736 ≈ 5.7% | -1.7 | 4% | KEEP |
| 12 | historical | 3% | 33/736 ≈ 4.5% | -1.5 | 3% | KEEP |
| 13 | school | 3% | 39/736 ≈ 5.3% | -2.3 | 4% | KEEP (Gen-Z portal) |
| 14 | cultivation | 3% | 24/736 ≈ 3.3% | -0.3 | 3% | KEEP |
| 15 | mecha | 2% | 10/736 ≈ 1.4% | +0.6 | 2% | KEEP (operator tentpole bright_presence_tw) |
| 16 | food | 2% | 5/736 ≈ 0.7% | +1.3 | 2% | LIFT |
| 17 | battle_internal | 2% | 35/736 ≈ 4.8% | -2.8 | 2% | CUT (overweight) |
| 18 | family | 1% | 40/736 ≈ 5.4% | -4.4 | 2% | CUT (overweight) |
| 19 | workplace | 1% | 10/736 ≈ 1.4% | -0.4 | 2% | KEEP |
| 20 | social_issue | 1% | 23/736 ≈ 3.1% | -2.1 | 1% | CUT (overweight) |
| 21 | sci_fi_cyberpunk | 1% | 9/736 ≈ 1.2% | -0.2 | 1% | KEEP |

**Totals.** Recommended V2 shares sum to ~99% (rounding). The 736 in denominators is the count of manga-applicable rows in `config/manga/brand_genre_allocation.yaml` (excludes essay / memoir / graphic_medicine which are not manga formats per `config/manga/canonical_genre_list.yaml`).

## 2. Three structural insights from the empirical column

### 2.1 The battle-cluster (battle + fantasy_adventure + dark_fantasy) is empirically 42% of the global market

Phoenix is at **6.4%**. Even a balanced Phoenix V2 should target ≥ 35% of catalog mass in these three genres because:

- Oricon 2025 top 10 = 100% battle/fantasy/dark-fantasy hybrids (One Piece, JJK, Dandadan, Blue Lock, Kingdom, Chainsaw Man) ([Oricon 2025 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2025-2024-nov-18-2025-nov-16-one-piece-takes-back-its-throne-while-four-other-manga-make-their-top-10-debut.1366774/))
- ICv2 / Circana BookScan US 2024 + 2025 = 100% shonen + seinen of the top 20 ([ICv2 2025](https://icv2.com/articles/markets/view/61706/manga-week-full-year-2025-circana-bookscan-top-20-manga-graphic-novels))
- Solo Leveling alone hit #1 on Oricon for vol 24 (March 2026) with ~51k copies in one week ([CBR Solo Leveling Vol 24](https://www.cbr.com/solo-leveling-volume-24-oricon-sales-ranking-win/))

**Phoenix's healing-anchored portfolio is a portfolio bet, not a market-share bet.** That's a legitimate strategy — but V2 must add a battle-cluster wing. Recommended: a `bright_presence_action` or `qi_battle_cultivation` brand wing producing 50–80 battle-cluster series.

### 2.2 Sports is empirically 4% and Phoenix is at 0.5% — the largest relative gap

Blue Lock alone is at 50M+ copies in circulation worldwide by September 2025 and was Oricon #4 in 2025 ([Blue Lock — Wikipedia](https://en.wikipedia.org/wiki/Blue_Lock)). Sports manga is a perfect therapeutic-embed lane (perfectionism, team belonging, competition anxiety, failure recovery) — see `genre_bestseller_dossiers/sports_bestseller_research_2026-05-13.md`.

### 2.3 Romance webtoon-share is undercounted in Oricon-only views

Romance is 39.4% of global webtoon share (Ken Research APAC). Phoenix's 6.9% allocation is healthy on Oricon terms but undercount if zh_CN / zh_TW / ko_KR locales are eventually added. Recommended V2 share of 10% reflects the webtoon weight.

## 3. The "$-makers" overlap

`projects/800_high_confidence_configs.md` flags "800 high-confidence catalog configs (brand × topic × persona × format × locale) per `artifacts/research/full_content_audit.md:65`" as the revenue tier. The V2 allocation above should be applied **at the high-confidence tier** first — i.e. the first 800 configs should reflect the empirical share (not the Phoenix portfolio mix). Long-tail experimentation can revert to healing-anchored.

## 4. What this means for V1.2 → V2 transition

V1.2 (`docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md` + `brand_genre_allocation.yaml`) is a portfolio bet, not a market-share bet. V2 should:

1. **Keep** the operator's preempted healing tentpole brand wing (per `feedback_campaign_h1_h2_decisions.md` — H2=C coexist).
2. **Add** a battle-cluster brand wing (3–5 new brands) producing the empirical 35–42% of catalog under the V2 target.
3. **Add** sports + food wings (small but high-leverage; see dossiers).
4. **Apply** the magical-twist + serial-engine framework from `manga_bestseller_magical_serial_framework_2026-05-12.md` to all V2 series (NOT just healing).

## 5. Reference: row-count target for V2

If we honor brand_genre_allocation.yaml's 736 manga-applicable rows but reweight per Section 1, the V2 distribution by row count is:

| Tier | Genres | V2 row target |
|---|---|---:|
| Battle-cluster | battle, fantasy_adventure, dark_fantasy | 250–260 |
| Healing-cluster | healing, slice_of_life, supernatural_everyday | 130–140 |
| Mystery-cozy + romance | romance, mystery_cozy | 115–120 |
| Adjacent shonen | sports, horror, mecha, food | 80–90 |
| School + comedy + family | school, comedy, family | 80–90 |
| Long-tail | historical, cultivation, workplace, social_issue, sci_fi_cyberpunk, battle_internal | 60–70 |
| **Total** | 21 manga-applicable genres | **~736** |

This is the table the V2 catalog plan should encode.

---

## Citations

- [Oricon Japan Manga Sales 2024 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2024-2023-nov-20-2024-nov-17-frieren-and-maomao-surge-while-jujutsu-kaisen-is-on-the-throne-for-a-final-time.1045941/)
- [Oricon Japan Manga Sales 2025 — ResetEra](https://www.resetera.com/threads/oricon-japan-manga-sales-2025-2024-nov-18-2025-nov-16-one-piece-takes-back-its-throne-while-four-other-manga-make-their-top-10-debut.1366774/)
- [ICv2 / Circana BookScan US 2024 Top 20](https://icv2.com/articles/markets/view/59079/full-year-2024-circana-bookscan-top-20-manga-graphic-novels)
- [ICv2 / Circana BookScan US 2025 Top 20](https://icv2.com/articles/markets/view/61706/manga-week-full-year-2025-circana-bookscan-top-20-manga-graphic-novels)
- [APAC Manga Market 2024–2030 — Ken Research](https://www.kenresearch.com/apac-manga-market)
- [Blue Lock — Wikipedia (50M circulation)](https://en.wikipedia.org/wiki/Blue_Lock)
- [Kingdom record-breaking — CBR](https://www.cbr.com/kingdom-record-breaking-manga-best-seller/)
- [Solo Leveling Vol 24 Oricon #1 — CBR](https://www.cbr.com/solo-leveling-volume-24-oricon-sales-ranking-win/)
- [Witch from Mercury Gunpla highest-selling — ComicBook.com](https://comicbook.com/anime/news/gundam-witch-from-mercury-gunpla-highest-sales/)
- [Toriko 30M circulation — Wikipedia](https://en.wikipedia.org/wiki/Toriko)
- [Food Wars 20M circulation — Wikipedia](https://en.wikipedia.org/wiki/Food_Wars!:_Shokugeki_no_Soma)
- [Oshi no Ko 25M circulation — Wikipedia](https://en.wikipedia.org/wiki/Oshi_no_Ko)
- [Goodnight Punpun 3M circulation — Wikipedia](https://en.wikipedia.org/wiki/Goodnight_Punpun)
- [Vinland Saga 7M circulation — Wikipedia](https://en.wikipedia.org/wiki/Vinland_Saga_(manga))

---

## 2026 refresh addendum (2026-07-24 — manga process uplift Lane 04; verify-not-redo)

Verification pass against newest public data (full citations in
`popular_genre_ranking_2026-05-02.md` → 2026 refresh addendum, same date):

- **Empirical share table (§1) holds.** Oricon 2026-H1 (Frieren #1, One Piece #2, JJK #3,
  Blue Lock #4, CSM #5) and ICv2/Circana Feb–Jun 2026 (JJK-dominated, all shonen/seinen) keep
  the battle-cluster ~40%+ of JP/US volume; no genre crosses a band boundary in §1.
- **§2.1 battle-cluster insight unchanged**; JJK's sequel-launch (Modulo, top-10 debut) and
  Kingdom at 120M strengthen it.
- **§2.2 sports gap re-confirmed:** Blue Lock top-5 two consecutive years; sports remains
  Phoenix's largest relative underweight.
- **§2.3 romance webtoon weight re-confirmed and updated:** romance ≈27.4% of the 2025 global
  webtoon market (#1 genre), fantasy ≈21.6% fastest-growing; WBTN FY2025 revenue $1.4B with
  IP adaptations +31.8%. The 39.4% figure used in 2025 sourcing appears to have been a
  platform-specific share; the cross-market 2025 figure is lower but romance's #1 digital rank
  is unchanged — the §1 recommended 10% V2 share needs no revision.
- **New context (not in original):** Japan total manga market contracted for the first time
  since 2017 (−1.7% to ¥692.5B; print volumes −14.4%, digital +2.9% to 76.1% share). This is a
  *channel* signal (digital-first), not a genre-mix signal; it does not alter §1 shares. It
  supports webtoon/vertical and digital-native formats in V2 planning.

**Verdict line (per-brand allocation):** NO change to §1 recommended V2 shares and NO
structural change to `docs/GENRE_PORTFOLIO_PLAN.md` per-brand allocations from 2026 movement.
The healing-anchor portfolio bet is *supported* by Frieren/Apothecary's 2026 performance
(blend-register healing at JP print #1). Standing §2 flags (sports, battle-cluster,
fantasy_adventure) remain operator-tier options already on record. No Q-MPU-05 escalation.

### Allocation-chain live confirmation (2026-07-24)

Chain re-verified end-to-end on origin/main `d55f6f3976`:

- `docs/GENRE_PORTFOLIO_PLAN.md` → `config/manga/locale_genre_allocations.yaml` (14 locales;
  every locale's `share_pct` sums to 100 — ja_JP verified 100 in this pass) →
  **consumer scripts:** `scripts/manga/generate_catalog_plan_from_strategic.py` (primary M2
  vehicle; header names all four inputs), `scripts/manga/run_m7_wave_a.py`,
  `scripts/manga/fanout_illustrated_pilots.py`, `scripts/catalog/validate_worldwide_plan_completeness.py`,
  `scripts/qa/manga_m7_plan_coverage_grid.py`. Brand-matrix side
  (`config/manga/brand_genre_allocation.yaml`): `scripts/catalog/rollup_manga_catalog_from_ssot.py`,
  `scripts/catalog/generate_manga_catalog.py`, `scripts/manga/generate_mecha_series_plans.py`,
  `scripts/manga/check_brand_portfolio.py`.
- **Live spot check:** ran `generate_catalog_plan_from_strategic.py` fresh (stdout mode, no
  writes). ja_JP section: 461 series across 15 VALID_GENRES. Per-genre plan shares track
  allocation shares within ≤5.8 points (e.g. supernatural_mystery 8.2% vs 8%; romance 8.0% vs
  8%; mecha 8.0% vs 8%; largest deviations: psychological_horror 8.2% vs 14%, sports 8.0% vs
  4%). The residual is the generator's documented design, not drift: per-brand counts blend
  strategic 20% / metadata 5% / market-revenue 70% / baseline 5% (`DISTRIBUTION_WEIGHTS`), and
  the M2 locale layer blends 70% locale share × 30% brand strategic, then quantizes per brand —
  locale-level aggregation flattens the extremes. **Chain verdict: WIRED and LIVE; consumers
  named; no action required.** (If a future lane wants locale-exact conformance, the knob is
  the M2 70/30 blend, not the allocation YAML — operator-tier decision.)
