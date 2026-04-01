# Pearl_Int — Exploding Topics Daily Scrape Plan

Last updated: 2026-03-22
Authority: docs/TREND_FEED_INTEGRATION_STRATEGY.md
Implementation status: **ACTIVE** — First scrape completed 2026-03-22 (7 entries in daily_trend_digest)

## Why Scrape Instead of API

Exploding Topics has no free API (Pro plan required, Semrush company).
But their **topic pages are public** and contain exactly what we need:
- Search volume (monthly)
- Growth percentage
- Trend chart (2-year)
- Related topics

**URL pattern:** `https://explodingtopics.com/topic/{slug}`
**Blog roundups:** `https://explodingtopics.com/blog/{category}-trends`

## Daily Scrape Targets

### Tier 1: CONFIRMED WORKING — Check Daily

Verified 2026-03-22. These URLs return full topic pages with volume + growth:

| Slug | Volume | Growth | Maps to topic_id | Status |
|------|--------|--------|-------------------|--------|
| emdr | 450K | +21% | anxiety / trauma | ✅ CONFIRMED |
| somatic-therapy | 110K | +102% | somatic | ✅ CONFIRMED |
| breathwork | 60.5K | +42% | wellness | ✅ CONFIRMED |
| rosebud-ai | 49.5K | +1086% | ai_wellness_tool | ✅ CONFIRMED |
| ketamine-therapy | 201K | +40% | alternative_therapy | ✅ CONFIRMED |

### Tier 1: 404 — NOT IN DATABASE (use SerpApi Google Trends instead)

Tested 2026-03-22. These slugs do NOT exist on Exploding Topics:

| Slug | Fallback |
|------|----------|
| nervous-system-regulation | SerpApi: "nervous system regulation" |
| dopamine-detox | SerpApi: "dopamine detox" |
| inner-child-healing | SerpApi: "inner child healing" |
| attachment-style | SerpApi: "attachment style" |
| trauma-response | SerpApi: "trauma response" |
| vagus-nerve | SerpApi: "vagus nerve" |
| polyvagal-theory | SerpApi: "polyvagal theory" |
| internal-family-systems | SerpApi: "internal family systems" |
| mindfulness | SerpApi: "mindfulness" |
| emotional-intelligence | SerpApi: "emotional intelligence" |
| shadow-work | SerpApi: "shadow work" |
| journaling | SerpApi: "journaling" |
| meditation | SerpApi: "meditation" |
| self-care | SerpApi: "self care" |
| somatic-yoga | SerpApi: "somatic yoga" |
| somatic-experiencing | SerpApi: "somatic experiencing" |
| mental-health | SerpApi: "mental health" |

### Tier 2: Category Pages — Browse for New Discoveries

| Page | URL | Status |
|------|-----|--------|
| Health & Wellness | `explodingtopics.com/health-topics` | ✅ CONFIRMED |
| Lifestyle & Culture | `explodingtopics.com/lifestyle-topics` | ✅ CONFIRMED |

Notable topics found in categories (2026-03-22):
- AI Slop (74K, +9100%) — quality differentiation signal
- Serene Herbs (22.2K, +2767%) — herbal anxiety solutions
- Snapcalorie (2.4K, +6500%) — AI nutrition
- Pet Anxiety Supplement (77, +5200%) — anxiety adjacent

### Tier 3: Blog Roundups (check weekly)

| Page | URL |
|------|-----|
| Health & Wellness Trends | `explodingtopics.com/blog/health-trends` |
| Self-Care Trends | `explodingtopics.com/blog/self-care-trends` |
| Mental Health Trends | `explodingtopics.com/blog/mental-health-trends` |
| Fitness Trends | `explodingtopics.com/blog/fitness-trends` |
| Consumer Trends | `explodingtopics.com/blog/consumer-trends` |

## Data to Extract Per Topic Page

From each `explodingtopics.com/topic/{slug}` page, extract:

```json
{
  "slug": "emdr",
  "volume": 450000,
  "growth_pct": 21,
  "status": "exploding|regular|peaked",
  "scraped_at": "2026-03-22T10:00:00Z",
  "related_topics": ["trauma therapy", "bilateral stimulation", "..."],
  "maps_to_topic_id": "anxiety"
}
```

## Scrape Method

**Browser-based (via Cowork/Claude in Chrome):**
1. Navigate to topic URL
2. Read page content for volume + growth
3. Extract related topics if visible
4. Write to `artifacts/feeds/exploding_topics_daily.jsonl`

**Scheduled task approach:**
- Daily at 9am: open each Tier 1 URL, extract data
- Rotate through 3-4 Tier 2 URLs each day (full rotation every 3-4 days)
- Weekly: check Tier 3 blog roundups for new topics to add to Tier 1/2

## Rate Limiting / Politeness

- Max 15 page loads per session
- 3-second wait between requests
- Respect robots.txt
- No login required (all pages are public)
- If blocked, back off 24 hours

## Output Integration

Daily scrape results feed into:
1. **trend_signals.jsonl** — scored by `score_trends.py` against topic registry
2. **Pearl News Qwen** — injected as `{{rss_context}}` for deep research
3. **ML Editorial MarketRouter** — `trend_heat_score` on BookSpec
4. **Pearl_Editor** — weekly review of new topic candidates

## New Topic Discovery

When the blog roundups or related topics surface a slug NOT in Tier 1/2:
1. Add it to Tier 2 rotation
2. Run it through `score_trends.py`
3. If trend_heat > 0.6, flag for Pearl_Editor as `new_evergreen_candidate`
4. If trend_heat > 0.8, flag as `fast_publish` candidate
