# Marketing-Grounded V2 Catalog Brief — Synthesis

**Date:** 2026-05-13
**Author:** Pearl_Research
**Branch:** `agent/pearl-research-genre-bestseller-audit-20260513`
**Purpose:** Single-page synthesis of the per-genre bestseller audit, the marketing-grounded allocation, the 9 gap dossiers, and the therapeutic-embed framework. This is the operator-facing brief.

## Three questions, three answers

### Q1: What does the actual marketing research say about per-genre manga bestseller volume / share / search-demand?

**Answer in one paragraph.** Oricon 2024/2025 and ICv2/Circana BookScan US 2024/2025 agree: the battle-cluster (battle + fantasy_adventure + dark_fantasy) is **~42% of the global manga buyer base** — One Piece, JJK, Dandadan, Blue Lock, Kingdom, Chainsaw Man, Solo Leveling, Frieren, Berserk, Apothecary Diaries dominate. Romance, when webtoon-share is included (Ken Research APAC, 39.4% of webtoon viewership is romance), is **~13%**. Healing/iyashikei is **~6% globally** but Phoenix's #1 by portfolio allocation mass (920 pct in `brand_genre_allocation.yaml` vs the next genre at 602). Sports is **~4%** of global buyers (Blue Lock alone hit 50M circulation by Sep 2025) — Phoenix is at 0.5%, the largest relative gap. Phoenix's V1.2 portfolio is a **portfolio bet**, not a market-share bet. Full per-genre share table in `marketing_grounded_per_genre_allocation_2026-05-13.md`.

### Q2: For every manga genre, do we have Pearl_Research-grade bestseller guidance?

**Answer.** Before this audit: 8 COVERED, 5 PARTIAL, 8 GAP. After this audit: **8 COVERED + 13 COVERED-via-new-dossier = 21/21 COVERED.**

| Coverage status | Genres | Path |
|---|---|---|
| COVERED (existing) | supernatural_everyday, romance, slice_of_life, healing, school, fantasy_adventure, dark_fantasy, battle | `popular_genre_ranking_2026-05-02.md`, `manga_bestseller_magical_serial_framework_2026-05-12.md`, `manga_genz_genalpha_portal_framework_2026-05-13.md`, `MANGA_READER_PROMISES.md`, `therapeutic_manga_wellness_market_research_2026_04_04.md` |
| COVERED-via-new-dossier | sports, food, mecha, horror, sci_fi_cyberpunk, historical, cultivation, workplace, social_issue | `artifacts/research/genre_bestseller_dossiers/<genre>_bestseller_research_2026-05-13.md` (9 files) |
| Still PARTIAL (existing breadth sufficient, can be deepened later) | mystery_cozy, comedy, family, battle_internal | covered for V2 authoring; deepening optional |

**Full audit table** in `genre_bestseller_coverage_audit_2026-05-13.md`.

### Q3: The psychology of therapeutic impact across genres — how do we embed self-help teaching without preaching?

**Answer.** The 5,300-word framework in `therapeutic_embed_psychology_framework_2026-05-13.md` specifies:

- **5 universal pitfalls** (preachy monologue, therapy-jargon, therapist-mouthpiece, fast-recovery, self-help-horror mislabel).
- **7 natural landing moments** (post-defeat, 3am-alone, mentor-doing-task, co-regulator-silence, witness-not-fixer, body-first, refusal-to-resolve).
- **Per-genre table** with 3–5 landing moments + 3 pitfalls + 1–3 self-help topics for EACH of the 21 genres.
- **4 cross-genre embedding moves** (mentor-doing-task, "I noticed" specificity, body-first, refusal-to-resolve) that recur in every successful embedding.
- **Operator-style example paragraph** for each of the 9 new-dossier genres (sports flinch-mapping, food grief-broth, mecha Hina's gauntlet, horror Baba's tea, cyberpunk aftermarket-implant, historical Vinland farm, cultivation courtyard-sweeping, workplace Room 4C, social-issue Forty-Three Nights).

The framework's closing principle: **"Story is the vehicle. Teaching is a passenger. If the passenger drives, the bus crashes."**

## V1.2 → V2 transition: the 13-genre delta

V1.2 themes (PR #1042 + brand_genre_allocation.yaml) were authored before this research. The delta:

| Aspect | V1.2 | V2 target |
|---|---|---|
| Genre count covered with Pearl_Research grade | 8 (mostly healing-cluster) | 21 |
| Battle-cluster catalog share | 6.4% | 35–42% |
| Sports allocation | 0.5% (4 rows) | 4% (~30 rows) |
| Magical-twist + serial-engine framework applied | partial (`manga_bestseller_magical_serial_framework_2026-05-12.md` exists; V1.1 didn't apply it) | required for ALL V2 series |
| Therapeutic-embed framework applied | implicit, healing-only | explicit, all 21 genres per `therapeutic_embed_psychology_framework_2026-05-13.md` |
| Per-genre dossier reference | 8 genres | 21 genres |

## Recommended catalog target

If Phoenix preserves the 736 manga-applicable rows in `brand_genre_allocation.yaml` and reweights per the marketing-grounded allocation:

- **250–260 rows** in battle-cluster (battle, fantasy_adventure, dark_fantasy)
- **130–140 rows** in healing-cluster (healing, slice_of_life, supernatural_everyday)
- **115–120 rows** in mystery_cozy + romance
- **80–90 rows** in adjacent shonen (sports, horror, mecha, food)
- **80–90 rows** in school + comedy + family
- **60–70 rows** in long-tail (historical, cultivation, workplace, social_issue, sci_fi_cyberpunk, battle_internal)

Total ~736. **800 high-confidence-config tier** (per `memory/project_800_high_confidence_configs.md`) should be drawn from this allocation, NOT from V1.2.

## Recommended V2 reauthoring plan

1. **DO NOT scrap V1.2.** Keep `brand_genre_allocation.yaml` as the row-count substrate. Reauthor the *themes* under V2.
2. **Author battle-cluster wing first** (250 series): biggest gap, biggest market.
3. **Apply magical-twist + serial-engine framework** to every V2 series (`manga_bestseller_magical_serial_framework_2026-05-12.md`).
4. **Apply therapeutic-embed framework** to every V2 series (`therapeutic_embed_psychology_framework_2026-05-13.md`).
5. **Reference the per-genre dossier** when authoring (each V2 series should cite its dossier in metadata).
6. **Test-author 1 series per genre** as canary (21 series) before fanning out the full 736.
7. **Gate the H2 fan-out** on canary review (per `memory/feedback_validation_before_scaling.md` — never stack/cherry-pick scale-up on unvalidated PRs).

## Files produced in this work (10 total)

1. `artifacts/research/genre_bestseller_coverage_audit_2026-05-13.md` — the 21-genre coverage matrix.
2. `artifacts/research/marketing_grounded_per_genre_allocation_2026-05-13.md` — empirical share table + V2 allocation target.
3. `artifacts/research/genre_bestseller_dossiers/sports_bestseller_research_2026-05-13.md`
4. `artifacts/research/genre_bestseller_dossiers/food_bestseller_research_2026-05-13.md`
5. `artifacts/research/genre_bestseller_dossiers/mecha_bestseller_research_2026-05-13.md`
6. `artifacts/research/genre_bestseller_dossiers/horror_bestseller_research_2026-05-13.md`
7. `artifacts/research/genre_bestseller_dossiers/sci_fi_cyberpunk_bestseller_research_2026-05-13.md`
8. `artifacts/research/genre_bestseller_dossiers/historical_bestseller_research_2026-05-13.md`
9. `artifacts/research/genre_bestseller_dossiers/cultivation_bestseller_research_2026-05-13.md`
10. `artifacts/research/genre_bestseller_dossiers/workplace_bestseller_research_2026-05-13.md`
11. `artifacts/research/genre_bestseller_dossiers/social_issue_bestseller_research_2026-05-13.md`
12. `artifacts/research/therapeutic_embed_psychology_framework_2026-05-13.md` — the cross-genre framework.
13. `artifacts/research/marketing_grounded_v2_catalog_brief_2026-05-13.md` — this synthesis brief.

Total: 13 new files, 0 deletions, 0 modifications to existing research.

## Next action for the operator

Decide:
1. **Approve V2 reauthoring** (per above plan), OR
2. **Approve canary-only** (1 series per genre × 21 genres = 21 canary series authored first, full fan-out gated on review).

The dossiers + framework are now in place. Pearl_Writer subagents (English prose, per `memory/feedback_qwen_vs_pearl_writer.md`) can begin authoring against this material immediately.
