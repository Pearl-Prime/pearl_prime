# SerpApi Google Trends — Search Budget Allocation Plan

**Budget:** 250 searches/month (free tier)
**Authority:** Pearl_Int · docs/TREND_FEED_INTEGRATION_STRATEGY.md
**Last updated:** 2026-03-22

---

## The Universe We're Covering

| Dimension | Count | Source |
|-----------|-------|--------|
| Personas | 10 | canonical_personas.yaml |
| Topics | 15 | canonical_topics.yaml |
| Persona × Topic cells | 150 | invisible_scripts_by_persona_topic.yaml |
| Consumer search clusters | ~75 | consumer_language_by_topic.yaml (5 per topic) |
| Watchlist keywords | 23 | feed_sources.md |
| Active locales | 13 | locale_registry.yaml |
| Exploding Topics slugs | 5 confirmed | exploding_topics_scrape_plan.md |

**Key insight:** Google Trends searches by keyword, not persona. We search consumer-language keywords, then map results back to personas via the existing YAML configs. This means 250 searches covers ALL 150 persona-topic cells — we don't need 150 separate searches.

---

## Weekly Budget: 57 searches/week (250 ÷ 4.35)

> **Month guard:** Months average 4.35 weeks, not 4. Budget is calculated conservatively
> at 57/week to avoid overrun. The remaining ~2 searches/month roll into Tier 5 reserve.
> The budget guard script hard-stops at 245 to leave a 5-search safety margin.

### Tier 1 — TOPIC PRIMARIES (15/week · 60/month)

One primary consumer keyword per topic, checked every week. These are the "headline" search terms from `consumer_language_by_topic.yaml` search_clusters.

| topic_id | Primary keyword | Personas served |
|----------|----------------|-----------------|
| anxiety | "anxiety relief" | All 10 |
| boundaries | "setting boundaries" | All 10 |
| burnout | "burnout recovery" | 8 (excl gen_alpha, first_responders use compassion_fatigue) |
| compassion_fatigue | "compassion fatigue" | healthcare_rns, first_responders, working_parents |
| courage | "finding courage" | entrepreneurs, gen_z_professionals |
| depression | "feeling depressed" | All 10 |
| financial_anxiety | "money anxiety" | millennial_women, tech_finance, entrepreneurs, working_parents |
| financial_stress | "financial stress" | gen_x_sandwich, corporate_managers, working_parents |
| grief | "dealing with grief" | All 10 |
| imposter_syndrome | "imposter syndrome" | millennial_women, tech_finance, entrepreneurs, gen_z |
| overthinking | "how to stop overthinking" | All 10 |
| self_worth | "building self worth" | All 10 |
| sleep_anxiety | "can't sleep anxiety" | All 10 |
| social_anxiety | "social anxiety" | gen_z, gen_alpha, millennial_women |
| somatic_healing | "somatic therapy" | All 10 |

**Schedule:** Every Monday, batch of 15 searches.
**Maps to personas:** Each result feeds ALL personas that share that topic (via invisible_scripts_by_persona_topic.yaml).

---

### Tier 2 — DEEP CLUSTER ROTATION (15/week · 60/month)

Each week, deep-dive 3 topics with all 5 search cluster keywords. Full rotation = 5 weeks to cover all 15 topics.

| Week | Topics deep-dived | Searches |
|------|-------------------|----------|
| Week 1 | anxiety, burnout, boundaries | 15 |
| Week 2 | depression, grief, self_worth | 15 |
| Week 3 | imposter_syndrome, overthinking, sleep_anxiety | 15 |
| Week 4 | social_anxiety, somatic_healing, compassion_fatigue | 15 |
| Week 5 | courage, financial_anxiety, financial_stress | 15 |

**Schedule:** Every Tuesday, batch of 15 searches.
**Purpose:** Catches long-tail keyword movement that Tier 1 primaries miss. Example: "anxiety" might be flat but "chest tightness anxiety how to calm down" could be spiking.

---

### Tier 3 — PERSONA-SPECIFIC VARIANTS (12/week · 48/month)

Some personas have distinct search language for the same topic. These keywords only make sense for specific persona segments.

| Persona cluster | Keywords (rotate 3/week) | Why distinct |
|----------------|--------------------------|--------------|
| tech_finance_burnout | "tech burnout", "startup founder mental health", "finance industry stress" | Industry-specific framing |
| healthcare_rns | "nurse burnout", "compassion fatigue nursing", "healthcare worker stress" | Occupation-specific |
| first_responders | "first responder PTSD", "first responder mental health", "critical incident stress" | Occupation-specific |
| gen_z_professionals | "quarter life crisis", "career anxiety gen z", "adulting stress" | Generational framing |
| gen_alpha_students | "school anxiety", "test anxiety teen", "social media anxiety" | Age-specific |
| working_parents | "mom burnout", "parent guilt anxiety", "work life balance stress" | Life-stage specific |
| gen_x_sandwich | "sandwich generation stress", "caring for aging parents burnout", "midlife anxiety" | Life-stage specific |
| entrepreneurs | "founder anxiety", "startup stress", "entrepreneurial loneliness" | Role-specific |
| millennial_women_professionals | "high-functioning anxiety", "perfectionism burnout women", "people pleasing recovery" | Demographic-specific |
| corporate_managers | "leadership burnout", "manager stress", "meeting fatigue" | Role-specific |

**Pool:** 30 unique persona-specific keywords, rotated 12/week.
**Schedule:** Every Wednesday, batch of 12 searches.
**Full rotation:** 2.5 weeks covers all 30 keywords.

---

### Tier 4 — EMERGING & WATCHLIST (12/week · 48/month)

Keywords from feed_sources.md watchlist + new discoveries from Exploding Topics and RSS feeds.

#### Fixed watchlist (8 keywords, checked every 2 weeks = 16/month):
- EMDR
- nervous system regulation
- dopamine detox
- inner child work
- attachment style
- trauma response
- vagus nerve
- polyvagal theory

#### Rotating emerging (cycle through, 8/week from this pool):
- cortisol reset
- body-based healing
- people pleasing recovery
- boundaries healing
- emotional granularity
- window of tolerance
- parts work / IFS
- reparenting
- breathwork
- somatic experiencing
- journaling therapy
- meditation for anxiety

#### Zeitgeist (1-2/month):
- mental health trend
- therapy speak
- healing journey
- self-help burnout
- wellness culture

**Schedule:** Every Thursday, batch of 12 searches.

---

### Tier 5 — RESERVE (8/week · 34/month)

Held for:
- **Hot signal follow-up** (4/week): When daily trend summary flags a spike, immediately check related keywords
- **New topic discovery** (2/week): When Exploding Topics or RSS surfaces a new slug, validate with Google Trends
- **Locale pilot** (2/week): When Phase 1 locales launch (zh-TW, ja-JP), test non-English keyword equivalents

**Schedule:** Friday or ad-hoc, triggered by Pearl_Editor or daily trend summary flags.

---

## Monthly Allocation Summary

| Tier | Purpose | /week | /month (×4.35) | Day |
|------|---------|-------|----------------|-----|
| 1 | Topic primaries (all 15) | 15 | ~65 | Monday |
| 2 | Deep cluster rotation (3 topics × 5 kw) | 15 | ~65 | Tuesday |
| 3 | Persona-specific variants | 12 | ~52 | Wednesday |
| 4 | Emerging & watchlist | 10 | ~44 | Thursday |
| 5 | Reserve (hot signals, discovery, locale) | 5 | ~24 | Friday/ad-hoc |
| **TOTAL** | | **57** | **~250** | |

> Budget guard enforces hard ceiling at 245/month. Any unused Tier 5 reserve rolls
> forward as extra capacity for the following week (never across months).

---

## How Results Map to Personas

The scoring pipeline uses this chain:

```
SerpApi result (keyword + interest score)
  → consumer_language_by_topic.yaml (maps keyword → topic_id)
  → invisible_scripts_by_persona_topic.yaml (maps topic_id → all relevant personas)
  → score_trends.py (generates trend_heat_score per topic)
  → MarketRouter (routes to BookSpec with persona_id + topic_id + trend_heat_score)
```

**Example flow:**
1. Tier 1 search: "anxiety relief" → Google Trends interest = 82/100
2. Maps to topic_id: `anxiety`
3. Invisible scripts exist for ALL 10 personas on `anxiety`
4. trend_heat_score for anxiety = 0.82
5. BookSpec candidates for anxiety × all 10 personas get heat score injected
6. MarketRouter prioritizes high-heat combos for fast-publish track

---

## Persona Coverage Guarantee

Every persona is covered by multiple tiers:

| Persona | Tier 1 topics | Tier 3 dedicated | Total keywords/month |
|---------|--------------|------------------|---------------------|
| millennial_women_professionals | 15 | 3 | 18+ |
| tech_finance_burnout | 15 | 3 | 18+ |
| entrepreneurs | 15 | 3 | 18+ |
| working_parents | 15 | 3 | 18+ |
| gen_x_sandwich | 15 | 3 | 18+ |
| corporate_managers | 15 | 3 | 18+ |
| gen_z_professionals | 15 | 3 | 18+ |
| healthcare_rns | 15 | 3 | 18+ |
| gen_alpha_students | 15 | 3 | 18+ |
| first_responders | 15 | 3 | 18+ |

Each persona gets: 15 universal topic checks + 3 persona-specific checks + shared emerging/watchlist coverage = full market visibility.

---

## Locale Expansion Plan (Future)

When non-English locales launch, reallocate from Tier 5 reserve:

| Phase | Locales | Keywords | Monthly searches needed |
|-------|---------|----------|------------------------|
| Current | en-US only | English | 0 extra |
| Phase 1 | zh-TW, ja-JP | 5 key topics × 2 locales | 10 from reserve |
| Phase 2 | zh-CN, ko-KR | 5 key topics × 2 locales | 10 from reserve |
| Phase 3+ | es-US, de-DE, fr-FR | 5 key topics × 3 locales | 15 → need paid tier |

**Trigger to upgrade:** When Tier 5 reserve is consistently exhausted (3+ weeks), request SerpApi paid plan upgrade.

---

## Daily Scheduled Task Integration

The existing `daily-trend-scrape` task (9:04 AM daily) should be updated to use this rotation:

```
Monday:    Tier 1 (15 topic primaries) + Exploding Topics scrape
Tuesday:   Tier 2 (15 deep cluster keywords)
Wednesday: Tier 3 (12 persona-specific)
Thursday:  Tier 4 (12 emerging/watchlist)
Friday:    Tier 5 reserve (8 hot signals / discovery)
Saturday:  Exploding Topics category browse only (0 SerpApi)
Sunday:    RSS digest + summary generation only (0 SerpApi)
```

Weekend days use zero SerpApi budget — only free sources (Exploding Topics public pages, RSS feeds).

---

## Pearl_Dev Implementation Tasks

These are the build items for Pearl_Dev. Each task is scoped small enough for a single branch + PR.

---

### TASK 1 — Keyword config files (new directory)

**Branch:** `agent/trend-keyword-configs`
**Creates:** `config/trend_keywords/` (new directory)

Files to create:

1. **`config/trend_keywords/tier1_topic_primaries.yaml`**
   - 15 entries, one per canonical topic
   - Schema: `{ topic_id: str, primary_keyword: str, source: "consumer_language_by_topic" }`
   - Pull primary keywords from `consumer_language_by_topic.yaml` → first entry in each topic's `search_clusters`
   - Must validate all 15 `canonical_topics.yaml` IDs are present

2. **`config/trend_keywords/tier2_cluster_rotation.yaml`**
   - 5 week-groups, 3 topics each, 5 keywords per topic
   - Schema: `{ week: int, topics: [{ topic_id: str, keywords: [str, str, str, str, str] }] }`
   - Pull keywords from `consumer_language_by_topic.yaml` → `search_clusters` field for each topic
   - Every topic must appear exactly once across the 5 weeks

3. **`config/trend_keywords/tier3_persona_specific.yaml`**
   - 10 persona entries, 3 keywords each = 30 total
   - Schema: `{ persona_id: str, keywords: [str, str, str] }`
   - Keywords must be persona-specific variants NOT already in Tier 1/2
   - Use the Tier 3 table in this document as starting point

4. **`config/trend_keywords/tier4_emerging_watchlist.yaml`**
   - Three sections: `fixed_watchlist` (8 kw, checked every 2 weeks), `rotating_emerging` (12 kw pool), `zeitgeist` (5 kw pool)
   - Schema: `{ section: str, keywords: [str], rotation: "biweekly" | "weekly" | "monthly" }`
   - Seed from `feed_sources.md` Keyword Watchlist

5. **`config/trend_keywords/budget_config.yaml`**
   - `monthly_limit: 250`, `safety_margin: 5`, `hard_stop: 245`
   - `tier_weekly_budgets: { tier1: 15, tier2: 15, tier3: 12, tier4: 10, tier5: 5 }`
   - `weekend_serpapi: false`
   - `counter_file: artifacts/feeds/.serpapi_usage_counter.json`

**Validation:** Write `scripts/feeds/validate_keyword_configs.py` that:
- Checks all 15 canonical topics covered in Tier 1
- Checks no duplicate keywords across tiers 1-3
- Checks Tier 2 rotation covers all 15 topics in 5 weeks
- Checks all 10 canonical personas covered in Tier 3
- Exits 0 on success, 1 on failure

---

### TASK 2 — Budget guard + usage counter

**Branch:** `agent/serpapi-budget-guard`
**Creates:** `scripts/feeds/budget_guard.py`

Responsibilities:
- Read `config/trend_keywords/budget_config.yaml` for limits
- Read/write `artifacts/feeds/.serpapi_usage_counter.json`:
  ```json
  { "month": "2026-03", "searches_used": 0, "last_reset": "2026-03-01T00:00:00Z" }
  ```
- Auto-reset counter on new month
- Expose functions:
  - `can_search(n: int) -> bool` — returns True if n searches fit in remaining budget
  - `record_searches(n: int)` — increments counter
  - `remaining() -> int` — returns remaining searches this month
  - `usage_report() -> dict` — month, used, remaining, pct
- Hard-stop at 245 (not 250) per `budget_config.yaml`
- Print warning at 200 (80% used)

**Reads:** `config/trend_keywords/budget_config.yaml`
**Writes:** `artifacts/feeds/.serpapi_usage_counter.json`
**Depends on:** Task 1 (budget_config.yaml)

---

### TASK 3 — Daily trend scrape scripts

**Branch:** `agent/trend-scrape-scripts`
**Creates:**

1. **`scripts/feeds/pull_feeds.py`**
   - Pull RSS feeds from the 6 active sources in `feed_sources.md`
   - Use `feedparser` library
   - Filter entries by keyword watchlist (core + emerging)
   - Write JSONL to `artifacts/feeds/feed_digest_{date}.jsonl`
   - Schema per line: `{ source, title, link, published, matched_keywords: [], topic_ids: [] }`
   - Map keywords → topic_ids via `consumer_language_by_topic.yaml` search_clusters

2. **`scripts/feeds/check_trends.py`**
   - Accept `--tier {1,2,3,4,5}` and `--week {1,2,3,4,5}` (for Tier 2 rotation)
   - Read keyword list for the given tier from `config/trend_keywords/`
   - Call SerpApi Google Trends engine (batch up to 5 keywords per request)
   - Check `budget_guard.can_search(n)` before every batch — abort if over budget
   - Call `budget_guard.record_searches(n)` after each batch
   - Write JSONL to `artifacts/feeds/google_trends_{date}.jsonl`
   - Schema: `{ keyword, topic_id, persona_ids: [], interest_score: int, trend_direction: str, tier: int, period: "90d", scraped_at: str }`
   - Map keyword → topic_id via Tier 1/2 yamls; keyword → persona_ids via Tier 3 yaml
   - Env var: `SERPAPI_KEY` from `.env`

3. **`scripts/feeds/score_trends.py`**
   - Read `google_trends_{date}.jsonl` + `feed_digest_{date}.jsonl`
   - For each topic_id, compute `trend_heat_score` (0.0–1.0):
     - Google Trends interest (0-100) → normalize to 0-1, weight 0.6
     - RSS mention count → normalize by max, weight 0.2
     - Exploding Topics growth_pct (if available) → normalize, weight 0.2
   - Read `invisible_scripts_by_persona_topic.yaml` to expand topic → persona_ids
   - Write `artifacts/feeds/trend_scores_{date}.jsonl`:
     ```json
     { "topic_id": "anxiety", "trend_heat_score": 0.82, "persona_ids": ["all"],
       "signals": { "google_interest": 82, "rss_mentions": 3, "et_growth": null },
       "fast_publish_eligible": true, "scored_at": "..." }
     ```
   - Flag `fast_publish_eligible: true` when score >= `TREND_FAST_PUBLISH_THRESHOLD` from .env (0.8)
   - Write human-readable `artifacts/feeds/daily_trend_summary_{date}.md` with:
     - Hot signals table (score >= 0.8)
     - Steady signals table (0.6-0.8)
     - Low-but-interesting table (< 0.6 with high growth)
     - Recommendations for Pearl_Editor (fast-publish candidates, boost existing, new evergreen)
     - Budget usage footer from `budget_guard.usage_report()`

4. **`scripts/feeds/daily_scrape_runner.py`**
   - Orchestrator: called by `daily-trend-scrape` scheduled task
   - Determine day of week → select tier
   - Determine current week number in month → select Tier 2 rotation week
   - Call scripts in order: `pull_feeds.py` → `check_trends.py --tier X` → `score_trends.py`
   - Log to `artifacts/feeds/scrape_run_log.jsonl`
   - Exit codes: 0 success, 1 partial (some feeds failed), 2 budget exhausted, 3 fatal

**Depends on:** Task 1 (keyword configs), Task 2 (budget guard)

---

### TASK 4 — BookSpec `trend_heat_score` field

**Branch:** `agent/bookspec-trend-heat`
**Modifies:** `phoenix_v4/planning/catalog_planner.py`

Changes:
- Add field to `BookSpec` dataclass:
  ```python
  trend_heat_score: Optional[float] = None  # 0.0-1.0, from score_trends.py
  ```
- Add to `to_dict()` method
- Add to any `from_dict()` or factory methods
- Update docstring to reference `artifacts/feeds/trend_scores_{date}.jsonl`

Also modify: `scripts/ml_editorial/run_market_router.py`
- In `load_config()` or scoring logic, read latest `trend_scores_{date}.jsonl`
- When routing, boost books whose `topic_id` has `trend_heat_score >= TREND_FAST_PUBLISH_THRESHOLD`
- Add `trend_boost` field to `market_actions.jsonl` output

**Depends on:** Task 3 (score_trends.py output format)

---

### TASK 5 — Update scheduled task + .gitignore

**Branch:** `agent/trend-schedule-update`

1. Update `daily-trend-scrape` scheduled task prompt to call `scripts/feeds/daily_scrape_runner.py` with day-of-week routing instead of the current inline scrape logic

2. Add to `.gitignore`:
   ```
   # Trend feed artifacts (machine-generated, not committed)
   artifacts/feeds/*.jsonl
   artifacts/feeds/.serpapi_usage_counter.json
   ```
   Keep `.md` summaries tracked (they're human-reviewed).

3. Add to `.env`:
   ```
   SERPAPI_SEARCHES_USED=0
   SERPAPI_BUDGET_MONTH=2026-03
   ```

**Depends on:** Tasks 1-4 all complete

---

### TASK 6 — consumer_language_by_topic.yaml updates

**Branch:** `agent/consumer-language-trend-update`
**Modifies:** `config/marketing/consumer_language_by_topic.yaml`

Add new trending consumer phrases discovered from the 2026-03-22 scrape:
- `somatic_healing` → add "vagal tone", "body-based healing", "somatic experiencing"
- `anxiety` → add "cortisol face", "cortisol reset", "nervous system dysregulation"
- `burnout` → add "dopamine detox", "dopamine fasting"
- `boundaries` → add "people pleasing recovery", "fawn response"
- Add new search_clusters entries for any topic that has fewer than 5

Also add `trend_keywords` field to each topic entry (new field):
```yaml
trend_keywords:
  - keyword: "cortisol reset"
    tier: 4
    first_seen: "2026-03-22"
```

**Depends on:** Task 1 (to know which keywords landed in which tier)

---

## Task Dependency Graph

```
Task 1 (keyword configs)
  ├── Task 2 (budget guard)     ← reads budget_config.yaml
  │     └── Task 3 (scrape scripts) ← uses budget_guard.py
  │           └── Task 4 (BookSpec + MarketRouter) ← reads score output
  │                 └── Task 5 (scheduled task + gitignore) ← wires it all up
  └── Task 6 (consumer language update) ← needs tier assignments
```

Tasks 1 and 6 can start in parallel.
Tasks 2 and 3 are sequential (3 depends on 2).
Task 4 can start once Task 3's output schema is defined (can stub).
Task 5 is last — integration glue.

---

## Verification

After all tasks complete, run this sequence to validate end-to-end:

```bash
# 1. Validate keyword configs
python scripts/feeds/validate_keyword_configs.py

# 2. Dry-run budget guard
python -c "from scripts.feeds.budget_guard import remaining; print(f'Budget: {remaining()} left')"

# 3. Run Monday scrape (Tier 1)
python scripts/feeds/daily_scrape_runner.py --dry-run

# 4. Check output artifacts exist
ls -la artifacts/feeds/trend_scores_$(date +%Y-%m-%d).jsonl
ls -la artifacts/feeds/daily_trend_summary_$(date +%Y-%m-%d).md

# 5. Verify BookSpec field
python -c "from phoenix_v4.planning.catalog_planner import BookSpec; print(BookSpec.__dataclass_fields__['trend_heat_score'])"

# 6. Run market router with trend data
python scripts/ml_editorial/run_market_router.py --dry-run
```

---

*Generated by Pearl_Int | Budget: 250/month SerpApi free tier | Pearl_Dev tasks: 6*
