# Pearl_Int — RSS / Web Feed Sources

Last updated: 2026-03-22
Authority: docs/TREND_FEED_INTEGRATION_STRATEGY.md

## Active Feeds

| Name | URL | Format | Interval | Status | Category |
|------|-----|--------|----------|--------|----------|
| Trend Hunter | `https://trendhunter.com/rss` | RSS 2.0 | 30 min | active | Trends/innovation |
| mindbodygreen Features | `https://mindbodygreen.com/rss/features` | RSS 2.0 | 30 min | active | Wellness/health |
| Tiny Buddha | `https://feeds.feedburner.com/tinybuddha` | RSS 2.0 | 60 min | active | Mindfulness/growth |
| Positivity Blog | `https://feeds.feedburner.com/ThePositivityBlog` | RSS 2.0 | 120 min | active | Self-improvement |
| Marc & Angel Hack Life | `https://feeds.feedburner.com/MarcAndAngelHackLife` | RSS 2.0 | 120 min | active | Life advice |
| Be More with Less | `https://feeds.feedburner.com/BeMoreWithLess` | RSS 2.0 | 120 min | active | Minimalism |

## API-Based Sources (require .env keys)

| Name | Endpoint | Free Tier | .env Key | Status | Use |
|------|----------|-----------|----------|--------|-----|
| Google Trends (SerpApi) | `https://serpapi.com/search?engine=google_trends` | 250/month | `SERPAPI_KEY` | **active** | Daily keyword heat — tiered batching (5/call), budget-guarded |
| Exploding Topics | Public pages: `https://explodingtopics.com/topic/{slug}` | No API (Semrush paywall) | N/A — browser scrape | **active** | Emerging micro-topics via public `/topic/{slug}` pages + category browse |

## Scraper Sources (no key, use Python package)

| Name | Package | Install | Status | Use |
|------|---------|---------|--------|-----|
| Trend Hunter Scraper | `trendhunter` | `pip install trendhunter` | active | Structured trend JSON |
| FeedSpot CSV | Manual download | N/A | active | Bulk feed import |

## Keyword Watchlist

58 unique keywords across 4 tiers. Budget: ~130 API calls/month (batching 5 keywords/call).
Full config: `config/trend_keywords/` (tier1–4 YAML + budget_config.yaml).
Validated by: `scripts/feeds/validate_keyword_config.py`.

### Tier 1 — Daily primaries (8 keywords)
EMDR, somatic therapy, breathwork, nervous system regulation, inner child healing, dopamine detox, attachment style, trauma response

### Tier 2 — Rotation, 5/day round-robin (20 keywords)
vagus nerve, polyvagal theory, IFS therapy, people pleasing recovery, cortisol reset, emotional regulation techniques, shadow work, reparenting, window of tolerance, body-based healing, boundaries healing, codependency recovery, complex PTSD, dissociation, emotional neglect, grief processing, hypervigilance, nervous system dysregulation, self-compassion, stress response cycle

### Tier 3 — Persona-specific, 2/day cycling 5 persona groups (20 keywords)
nyc_exec (4), new_mom (4), gen_z_student (4), midlife_transition (4), caregiver (4)

### Tier 4 — Weekly cultural discovery, Sunday batch (10 + 5 reserve)
AI journaling app, therapy speak toxic, healing journey burnout, self-help books that actually work, AI self help, nervous system reset exercises, cortisol face, doom spending anxiety, microdosing for depression, emotional fitness routine

## Output Artifacts

| Artifact | Path | Format | Writer |
|----------|------|--------|--------|
| Feed digest | `artifacts/feeds/feed_digest_{date}.jsonl` | JSONL | pull_feeds.py |
| Google Trends raw | `artifacts/feeds/google_trends_{date}.jsonl` | JSONL | check_trends.py |
| Exploding Topics raw | `artifacts/feeds/exploding_topics_{date}.jsonl` | JSONL | browser scrape |
| Trend signals (scored) | `artifacts/feeds/trend_signals_{date}.jsonl` | JSONL | score_trends.py |
| Daily digest (combined) | `artifacts/feeds/daily_trend_digest_{date}.jsonl` | JSONL | daily_scrape_runner.py |
| Daily summary (human) | `artifacts/feeds/daily_trend_summary_{date}.md` | Markdown | daily_scrape_runner.py |
| Budget state | `artifacts/feeds/.serpapi_budget_state.json` | JSON | budget_guard.py |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/feeds/pull_feeds.py` | Pulls 6 RSS feeds, keyword extraction, domain relevance scoring |
| `scripts/feeds/check_trends.py` | SerpApi Google Trends — tiered batching, budget-guarded, spike detection |
| `scripts/feeds/score_trends.py` | Heat scoring (domain×0.4 + velocity×0.35 + novelty×0.25), action classification |
| `scripts/feeds/daily_scrape_runner.py` | Orchestrator: pull→check→score→summary; --dry-run, --skip-* flags |
| `scripts/feeds/budget_guard.py` | Monthly hard-stop (245), auto-reset, persistent state |
| `scripts/feeds/validate_keyword_config.py` | Validates all tier YAMLs, dedup, budget math |

## Feed Health

Last health check: 2026-03-22 (first run)

| Feed | Last Pull | Entries | HTTP Status | Notes |
|------|-----------|---------|-------------|-------|
| Trend Hunter | 2026-03-22 | — | blocked from VM | Works from user machine / GitHub Actions |
| mindbodygreen | 2026-03-22 | — | blocked from VM | Works from user machine / GitHub Actions |
| SerpApi | 2026-03-22 | 5 | 200 | Working — budget 0/245 used |
| Exploding Topics | 2026-03-22 | 7 | 200 | Browser scrape — 5 confirmed slugs + 2 category pages |
