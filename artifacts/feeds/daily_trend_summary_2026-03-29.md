# Pearl_Int Daily Trend Summary — 2026-03-29 (Sunday)

## Pipeline Status

| Step | Status | Notes |
|------|--------|-------|
| SerpApi Google Trends | BLOCKED | Sandbox 403 tunnel error. 0/245 budget used. All 4 tiers (25 keywords) failed. |
| RSS Feed Pulls | SKIPPED | daily_scrape_runner.py not yet built |
| Exploding Topics (5 confirmed) | DONE | All 5 topics scraped via browser |
| Exploding Topics discovery scan | DONE | Health + Lifestyle pages scanned |
| Trend scoring | DONE | Manual scoring against consumer_language_by_topic.yaml |

## Confirmed Topic Snapshot (vs 2026-03-28)

| Topic | Volume | Growth | Signal | Delta | Fast Publish? |
|-------|--------|--------|--------|-------|---------------|
| somatic-therapy | 110K | +102% | strong | No change; late-Mar rebound on chart | YES |
| breathwork | 60.5K | +75% | strong | No change; uptick from mid-Mar dip | YES |
| emdr | 450K | +37% | mature_steady | No change; approaching prior highs | No |
| rosebud-ai | 49.5K | +1243% | explosive_spike | Sustained plateau | No (competitor) |
| ketamine-therapy | 201K | +74% | high_volume_risky | Stable plateau | No (compliance) |

## Fast-Publish Candidates

1. **Somatic Therapy** — 4 topic_id matches (anxiety, burnout, grief, somatic_healing). +102% growth still doubling. Bridge language ready. Best content opportunity right now.
2. **Breathwork** — 4 topic_id matches. +75% growth. Natural pairing with somatic-therapy content. Trending upward again after mid-Mar dip.

## Watch List

- **Rosebud AI** remains explosive at 49.5K sustained plateau. AI journaling competitor signal. Content angle: "AI journaling for overthinkers" using Phoenix bridge language. Don't chase the brand name.
- **EMDR** showing late-Mar chart uptick. Revisit if volume breaks above ~484K.

## Discovery Scan: No New Topics

Health and Lifestyle pages scanned. No new self-help/wellness/therapy/mental health topics with >1000% growth found outside existing watchlist. Pages dominated by:
- Health: PDRN skincare, Retatrutide (pharma), AI Agentic, OpenEvidence, Snapcalorie, body sculpting devices
- Lifestyle: Boneless Couch, Barrel Leg Sweatpants, pet anxiety supplements, Serene Herbs (re-confirmed, product signal only)

## Action Items

1. **Publish somatic-therapy + breathwork content** — both remain strong fast-publish candidates with 4 topic_id matches each
2. **Fix SerpApi execution** — needs to run outside sandbox (403 tunnel block). March budget untouched at 245 remaining. Sunday tier 4 emerging keywords missed.
3. **Build daily_scrape_runner.py and score_trends.py** — pipeline automation still missing
4. **Monitor rosebud-ai** — sustained explosive growth signals consumer appetite for AI self-reflection tools
