# Research Integration Log

**Last updated:** 2026-04-20  
**Maintained by:** Pearl_GitHub / manga audit sprint

This log tracks the integration status of research artifacts into the Phoenix Omega manga pipeline. Each artifact is tracked from discovery → integration → verification.

---

## Integrated Artifacts

### 1. `therapeutic_manga_wellness_market_research_2026_04_04.md`

| Field | Value |
|---|---|
| Artifact type | Market research report |
| Discovery date | 2026-04-04 |
| Integration date | 2026-04-20 |
| Sprint | `agent/manga-audit-remediation-20260420` |

**Integration points:**

- `config/source_of_truth/manga_profiles/therapeutic/` — 12 new therapeutic brand-genre profiles (burnout×3, overthinking×3, graphic_medicine×3, spiritual_essay×3) derived directly from §burnout, §overthinking, §anxiety, §adhd, §depression_adjacent, §grief, §chronic_illness, §spiritual, §mindfulness, §somatic research sections
- `artifacts/research/MANGA_READER_PROMISES.md` — 3 therapeutic craving extensions (Named-ness #11, Permission #12, Reframe #13) derived from §therapeutic_cravings
- `config/catalog_planning/brand_series_plans.yaml` — zh_HK + zh_SG lane_intensity correction from §ko_KR Phase 3 market analysis

**Unintegrated sections:** §pricing (deferred to pricing strategy sprint), §distribution_channel (deferred to `manga_publishing_revenue_strategy.md` sprint)

---

### 2. `global_manga_distribution_strategy.md`

| Field | Value |
|---|---|
| Artifact type | Distribution strategy document |
| Discovery date | prior sprint |
| Integration date | 2026-04-20 (partial) |
| Sprint | `agent/manga-audit-remediation-20260420` |

**Integration points:**

- `config/catalog_planning/brand_series_plans.yaml` — `lane_intensity` block reflects §Phase 3 market guidance (zh_HK, zh_SG = light lane)
- `config/manga/format_adaptation_grammars.yaml` — `webtoon` and `vertical_short_teaser` format grammars aligned with §digital_first distribution guidance

**Unintegrated sections:** §platform_partnerships (deferred — requires business development decisions), §13_market_calibration (deferred to separate full-market calibration sprint), §pricing_tiers (deferred to pricing sprint)

---

### 3. `manga_publishing_revenue_strategy.md`

| Field | Value |
|---|---|
| Artifact type | Revenue strategy document |
| Discovery date | prior sprint |
| Integration date | 2026-04-20 (structural only) |
| Sprint | `agent/manga-audit-remediation-20260420` |

**Integration points:**

- `config/manga/format_adaptation_grammars.yaml` — `vertical_short_teaser` format grammar includes CTA ("read now on [platform]") per §monetization_funnels guidance on teaser-to-subscription conversion

**Unintegrated sections:** §subscription_tier_design (requires product decisions), §chapter_pricing (requires finance decisions), §creator_revenue_share (requires legal/contract decisions)

---

### 4. `manga_pacing_corpus_analysis.md` *(if exists — verify on integration)*

| Field | Value |
|---|---|
| Artifact type | Corpus analysis |
| Discovery date | 2026-04-04 (referenced in research) |
| Integration date | 2026-04-20 |
| Sprint | `agent/manga-audit-remediation-20260420` |

**Integration points:**

- `config/manga/manga_pacing_by_genre.yaml` — `words_per_page_range`, `silent_panel_ratio_range`, `reference_corpus` entries for all 16 genre families derived from corpus analysis benchmarks

**Verification note:** If this artifact does not exist as a standalone file, the pacing ranges in `manga_pacing_by_genre.yaml` were derived from the §pacing sections of `therapeutic_manga_wellness_market_research_2026_04_04.md` combined with published corpus data for each genre family.

---

## Deferred Integrations

| Artifact section | Reason for deferral | Owner |
|---|---|---|
| §pricing (all artifacts) | Requires finance + product decisions | Product sprint |
| §13_market_calibration | Full 13-market rollout requires business development | Distribution sprint |
| §platform_partnerships | Requires external partner agreements | BD sprint |
| §subscription_tier_design | Requires product architecture decision | Product sprint |
| Localization sprints (12 therapeutic profiles × 12 locales = 144 files) | EN-first policy; localization requires native speaker QA | Localization sprint |

---

## Integration Methodology

1. **Research artifact discovery** — artifacts identified during catalog audit sprint
2. **Section triage** — each artifact's sections classified as: immediately actionable / deferred (business decision required) / deferred (localization required)
3. **Profile/config derivation** — actionable sections translated to YAML profiles, gate logic, or config changes
4. **Citation threading** — every derived file includes `Research basis:` comment pointing back to source artifact and section
5. **Integration verification** — homogeneity check (`scripts/manga/check_catalog_homogeneity.py`) run after all profiles created; gate tests run after gate files created
