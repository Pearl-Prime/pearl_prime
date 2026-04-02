# Trend Feed Integration Strategy — Pearl_Int × Pearl_Editor × Ei

**Purpose:** Wire free RSS feeds, trend APIs, and web scrapers into Phoenix Omega's existing ML Editorial + Market Intelligence loop to automate topic discovery, validate evergreen angles, and surface weekly trending topics for rapid book/series production.

**Owner:** Pearl_Int (feed acquisition + .env) → Pearl_Editor (editorial scoring) → Ei (quality gates + market routing)
**Authority:** This doc + `skills/pearl-int/references/feed_sources.md` + `docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md`
**Last updated:** 2026-03-22

---

## 1. The Problem We're Solving

Phoenix Omega already has a sophisticated pipeline for choosing book topics:

- `catalog_planner.py` produces `BookSpec` from domain/topic/persona/angle configs
- `angle_resolver.py` selects narrative drivers from `config/angles/angle_registry.yaml`
- `consumer_language_by_topic.yaml` maps clinical topics to real consumer language
- The ML Editorial loop scores, ranks, and routes content through market positioning
- Pearl News / Qwen deep research engine provides generational intelligence

**What's missing:** A live, automated signal layer that tells us *what's trending right now* in self-help, wellness, and mental health — so we can:

1. Validate that planned topics still have market heat
2. Surface emerging micro-topics before competitors
3. Feed weekly "fast-publish" topics into the pipeline alongside evergreen catalog
4. Calibrate `consumer_language_by_topic.yaml` with real-time language shifts

---

## 2. Architecture: Where Feeds Plug In

```
                    ┌──────────────────────────┐
                    │   FREE RSS/API FEEDS      │
                    │   (Pearl_Int manages)      │
                    │                            │
                    │  Trend Hunter RSS          │
                    │  mindbodygreen RSS         │
                    │  Tiny Buddha RSS           │
                    │  Positivity Blog RSS       │
                    │  Marc & Angel RSS          │
                    │  Be More with Less RSS     │
                    │  Google Trends (SerpApi)   │
                    │  Exploding Topics API      │
                    │  trendhunter Python pkg    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  TREND INGESTION SCRIPT   │
                    │  scripts/feeds/           │
                    │  pull_feeds.py            │
                    │  score_trends.py          │
                    │                           │
                    │  Outputs:                 │
                    │  artifacts/feeds/          │
                    │    trend_signals.jsonl     │
                    │    feed_digest.jsonl       │
                    └──────────┬───────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
    ┌─────────────┐  ┌────────────────┐  ┌──────────────┐
    │ CATALOG      │  │ ML EDITORIAL   │  │ PEARL NEWS   │
    │ PLANNER      │  │ MARKET LOOP    │  │ DEEP RESEARCH│
    │              │  │                │  │              │
    │ BookSpec     │  │ VariantRanker  │  │ Qwen chain   │
    │ gets trend   │  │ gets trend     │  │ gets RSS     │
    │ heat score   │  │ signal boost   │  │ context      │
    └─────────────┘  └────────────────┘  └──────────────┘
              │                │                 │
              └────────────────┼─────────────────┘
                               ▼
                    ┌──────────────────────────┐
                    │  PEARL_EDITOR             │
                    │  Topic Decision Gate      │
                    │                           │
                    │  Two tracks:              │
                    │  EVERGREEN = planned       │
                    │  TRENDING  = fast-publish  │
                    └──────────────────────────┘
```

---

## 3. Free Feed Sources — Complete Registry

### 3A. RSS Feeds (Free, No Auth)

| Feed | URL | Category | Update Freq |
|------|-----|----------|-------------|
| Trend Hunter | `https://trendhunter.com/rss` | Trends/innovation | Daily |
| mindbodygreen | `https://mindbodygreen.com/rss/features` | Wellness/health | Daily |
| Tiny Buddha | `https://feeds.feedburner.com/tinybuddha` | Mindfulness/growth | 2-3x/week |
| Positivity Blog | `https://feeds.feedburner.com/ThePositivityBlog` | Self-improvement | Weekly |
| Marc & Angel | `https://feeds.feedburner.com/MarcAndAngelHackLife` | Life advice | 2x/week |
| Be More with Less | `https://feeds.feedburner.com/BeMoreWithLess` | Minimalism/simplicity | Weekly |
| Insideout Mastery | via FeedSpot CSV | Personal mastery | Weekly |
| Possibility Change | via FeedSpot CSV | Change/growth | Weekly |

### 3B. Free-Tier APIs (Auth Required — Pearl_Int manages .env)

| Service | Free Tier | .env Variable | Use Case |
|---------|-----------|---------------|----------|
| SerpApi (Google Trends) | 250 searches/month | `SERPAPI_KEY` | Daily keyword heat check (tiered batching) |
| Exploding Topics | Public pages (no API) | N/A — browser scrape | Emerging micro-topic discovery via `/topic/{slug}` |

### 3C. Free Open-Source Tools (No Key Needed)

| Tool | Install | Use Case |
|------|---------|----------|
| `trendhunter` Python pkg | `pip install trendhunter` | Scrape Trend Hunter ideas as JSON |
| FeedSpot CSV export | Download once | Bulk import 100+ self-improvement feeds |
| `feedparser` Python pkg | `pip install feedparser` | Parse any RSS/Atom feed |

---

## 4. Two-Track Strategy: Evergreen + Trending

### The Core Insight

Phoenix Omega's catalog planner already handles **evergreen** topics (anxiety, inner-child, EMDR, dopamine, etc.) through `config/catalog_planning/`. These are planned months ahead, go through full Ei quality gates, and produce polished series.

The feed integration adds a **trending** track that runs in parallel:

| Dimension | Evergreen Track | Trending Track |
|-----------|----------------|----------------|
| **Cadence** | Monthly/quarterly planning | Weekly topic selection |
| **Source** | Domain definitions, persona research | RSS feeds, Google Trends, Exploding Topics |
| **Depth** | Full book/series (8-12 chapters) | Short book or standalone (3-5 chapters) |
| **Quality gate** | Full Ei V2 pipeline | Abbreviated: section scoring + reader-fit only |
| **Time to publish** | 2-4 weeks | 3-5 days |
| **Risk** | Low (validated topics) | Medium (trend may cool before publish) |
| **Example** | "Anxiety series, 6 installments" | "The Cortisol Reset: trending this week" |

### How They Complement Each Other

1. **Trending validates evergreen:** If "dopamine detox" is trending on Google Trends and we have a planned book on dopamine regulation, that book gets priority in the ML Editorial market router (priority boost from `trend_heat_score`)
2. **Trending discovers new evergreen:** If "emotional fitness" appears on Exploding Topics growing 200%+ over 3 months, Pearl_Editor flags it as a candidate for a full evergreen series
3. **Evergreen absorbs trending:** When a trending micro-topic (e.g., "cortisol face") maps to an existing domain (stress/HPA axis), the catalog planner can add it as an angle variant rather than a new book

---

## 5. Data Flow: Feed → Topic Decision

### Step 1: Pearl_Int pulls feeds (daily)

```python
# scripts/feeds/pull_feeds.py
# Scheduled via GitHub Actions cron or Pearl_Dev scheduled task
# Writes: artifacts/feeds/feed_digest.jsonl

for feed_url in registered_feeds:
    entries = feedparser.parse(feed_url)
    for entry in entries[:RSS_MAX_ENTRIES]:
        emit({
            "source": feed_name,
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary[:500],
            "pulled_at": now_utc(),
            "keywords": extract_keywords(entry.title + entry.summary)
        })
```

### Step 2: Pearl_Int checks Google Trends (weekly, 100/month budget)

```python
# scripts/feeds/check_trends.py
# Uses SerpApi free tier
# Checks Phoenix Omega's keyword list against Google Trends

KEYWORDS = [
    "EMDR", "emotional fitness", "body-based healing",
    "dopamine detox", "cortisol reset", "nervous system regulation",
    "inner child work", "somatic therapy", "attachment style",
    "trauma response", "people pleasing", "boundaries"
]

for keyword in KEYWORDS:
    response = serpapi_search(engine="google_trends", q=keyword)
    if seven_day_avg_jump(response) > 20:
        emit_trend_signal(keyword, response)
```

### Step 3: Score against existing topic registry

```python
# scripts/feeds/score_trends.py
# Maps feed items + trend signals against consumer_language_by_topic.yaml
# Writes: artifacts/feeds/trend_signals.jsonl

for signal in feed_digest + trend_data:
    # Match against known topic_ids
    topic_match = match_to_topics(signal.keywords, consumer_language)
    # Score: relevance to our domains × trend velocity × novelty
    trend_heat = calculate_heat(
        domain_relevance=topic_match.score,
        trend_velocity=signal.growth_rate,
        novelty=1.0 - existing_coverage(signal.keywords)
    )
    emit({
        "signal_id": hash(signal),
        "topic_match": topic_match.topic_id or "NEW",
        "trend_heat": trend_heat,  # 0-1
        "source": signal.source,
        "keywords": signal.keywords,
        "action": classify_action(trend_heat, topic_match)
        # "boost_existing" | "fast_publish" | "new_evergreen_candidate" | "ignore"
    })
```

### Step 4: Pearl_Editor receives scored signals

Pearl_Editor reviews `trend_signals.jsonl` and makes topic decisions:

| Action | What Happens | Who Executes |
|--------|-------------|-------------|
| `boost_existing` | Existing BookSpec gets `trend_heat_score` field; ML Editorial MarketRouter bumps priority | Automated (ML loop) |
| `fast_publish` | New short-form BookSpec created with trending angle; abbreviated Ei gate | Pearl_Editor approves → catalog_planner |
| `new_evergreen_candidate` | Topic added to planning backlog for next quarterly review | Pearl_Editor logs → PLANNING_STATUS.md |
| `ignore` | Signal below threshold; logged for pattern analysis | Automated |

### Step 5: Ei validates (both tracks)

Regardless of track, every BookSpec passes through Ei:

- **Evergreen:** Full pipeline (section scoring → variant ranking → reader-fit → rewrite recs → market router)
- **Trending:** Abbreviated (section scoring → reader-fit → market router; skip variant ranking and rewrite for speed)

---

## 6. Weekly Cadence

| Day | Action | Agent |
|-----|--------|-------|
| Mon | Pull all RSS feeds + Exploding Topics | Pearl_Int |
| Mon | Run Google Trends check (budget: ~25 keywords) | Pearl_Int |
| Mon | Score trends against topic registry | Pearl_Int |
| Tue | Pearl_Editor reviews trend_signals.jsonl | Pearl_Editor |
| Tue | Approve/reject fast-publish candidates | Pearl_Editor (PM approval) |
| Wed | Fast-publish BookSpecs enter abbreviated Ei pipeline | Ei |
| Thu | Fast-publish content drafted | Pearl_Writer |
| Fri | Ei quality gate + market router for fast-publish | Ei |
| Fri | Weekly ML Editorial run includes trend-boosted evergreen | ML loop |

---

## 7. .env Additions for Pearl_Int

Add to `.env` (Pearl_Int manages):

```env
# ── TREND FEEDS (Pearl_Int) ────────────────────────────
SERPAPI_KEY=<your-key>
# Exploding Topics: no API key (public page scrape via browser)
RSS_POLL_INTERVAL_MINUTES=30
RSS_MAX_ENTRIES_PER_FEED=50
TREND_HEAT_THRESHOLD=0.6
TREND_FAST_PUBLISH_THRESHOLD=0.8
```

---

## 8. Integration with Existing Pipeline Components

### 8A. consumer_language_by_topic.yaml

Trend feeds provide a feedback loop: when feed items consistently use language not yet captured in `consumer_language_by_topic.yaml`, Pearl_Editor can propose updates. Example: if "cortisol face" appears 15 times across feeds in a month but isn't in the `stress` topic's `consumer_phrases`, it gets flagged for addition.

### 8B. Pearl News Qwen Deep Research Engine

The `{{rss_context}}` injection point in the Qwen system prompt (see `PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`) is designed exactly for this. Pearl_Int's `feed_digest.jsonl` becomes the RSS context fed into Qwen research chains, giving the deep research engine current-week data to reason about.

### 8C. ML Editorial VariantRanker

`run_variant_ranking.py` already accepts marketing lexicons. Trend signals can inject trending language into the variant ranking step so that title/subtitle options reflect current search patterns.

### 8D. ML Editorial MarketRouter

`run_market_router.py` routes books to priority segments and channels. A `trend_heat_score` field on BookSpec gives the router a signal to bump distribution priority for trend-aligned content.

---

## 9. What This Gets You

**Without this integration:** You plan topics based on domain expertise and quarterly research cycles. Good for evergreen, slow to react to market shifts.

**With this integration:**
- Every Monday, you see a scored list of what's trending in your domains
- Topics you already planned get a heat score confirming (or questioning) their timing
- New micro-topics get surfaced before competitors publish on them
- You can put out a trend-responsive book every week while your evergreen catalog builds in parallel
- The same Ei quality system governs both tracks — no drop in quality for speed
- Consumer language stays current because feeds tell you how real people are talking about your topics right now
- Pearl News research chains get live context instead of stale training data

**Evergreen strategy remains untouched.** The trending track is additive. If a week has no actionable trends, nothing changes. If a trend aligns with a planned book, it gets a boost. If a trend is completely new and hot, you have a 5-day path to publish.

---

## 10. Implementation Checklist

- [x] Pearl_Int: Register all RSS feeds in `skills/pearl-int/references/feed_sources.md`
- [x] Pearl_Int: Add `SERPAPI_KEY` to .env (250 searches/month free tier)
- [x] Pearl_Int: Exploding Topics scrape plan via public `/topic/{slug}` pages (no API key — Semrush paywall)
- [x] Pearl_Dev: Create `scripts/feeds/pull_feeds.py` — pulls 6 RSS feeds, keyword extraction, JSONL output
- [x] Pearl_Dev: Create `scripts/feeds/check_trends.py` — SerpApi Google Trends, tiered keyword batching (5/call), budget-guarded
- [x] Pearl_Dev: Create `scripts/feeds/score_trends.py` — heat scoring (domain_relevance×0.4 + velocity×0.35 + novelty×0.25), action classification
- [x] Pearl_Dev: Create `scripts/feeds/daily_scrape_runner.py` — orchestrator with --dry-run, --skip-rss, --skip-trends, --skip-score flags
- [x] Pearl_Dev: Create `scripts/feeds/budget_guard.py` — monthly hard-stop at 245, auto-reset, persistent state
- [x] Pearl_Dev: Create `scripts/feeds/validate_keyword_config.py` — validates all tier YAMLs, dedup, budget math
- [x] Pearl_Dev: Create `config/trend_keywords/` — tier1 (8 daily), tier2 (20 rotation), tier3 (20 persona), tier4 (10 weekly), budget_config
- [x] Pearl_Dev: Add `trend_heat_score` field to BookSpec dataclass in `catalog_planner.py`
- [x] Pearl_Dev: Wire trend signals into MarketRouter (`run_market_router.py`) — priority boost at heat ≥0.6/≥0.8
- [x] Pearl_Dev: Update `consumer_language_by_topic.yaml` with trend-sourced phrases (anxiety, somatic_healing, burnout)
- [x] Pearl_Dev: Widen `validate_marketing_config.py` search_clusters limit from (3,5) to (3,10) for trend additions
- [x] Pearl_GitHub: Add `artifacts/feeds/` patterns to `.gitignore`
- [x] Pearl_Dev: Scheduled task `daily-trend-scrape` (9 AM daily)
- [ ] Pearl_Editor: Define fast-publish quality gate (abbreviated Ei) — **pending**
- [ ] Pearl_Editor: Create weekly trend review workflow — **pending**
- [ ] Pearl_Dev: GitHub Actions cron for daily feed pulls — **pending** (currently Cowork scheduled task only)
- [ ] Pearl_Dev: Feed health monitoring in integration health check — **pending**

### Implementation Date: 2026-03-22

**58 unique keywords** across 4 tiers. Budget: ~130 API calls/month (batching saves ~48%). First daily digest produced `daily_trend_digest_2026-03-22.jsonl` with 12 entries (7 Exploding Topics + 5 Google Trends). 422/422 repo tests passing.
